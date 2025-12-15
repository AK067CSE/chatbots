"""
Enhanced RAG Pipeline for Text-to-SQL
Uses vector embeddings to retrieve relevant SQL patterns and database schema info
"""

import json
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass

import numpy as np
from langchain_community.vectorstores import Chroma
try:
    from langchain_huggingface import HuggingFaceEmbeddings
except Exception:
    try:
        from sentence_transformers import SentenceTransformer

        class HuggingFaceEmbeddings:
            def __init__(self, model_name: str = "sentence-transformers/all-MiniLM-L6-v2", model_kwargs: dict = None):
                self.model = SentenceTransformer(model_name)

            def embed_documents(self, texts: List[str]):
                embs = self.model.encode(texts, show_progress_bar=False)
                # Ensure native Python floats for downstream compatibility
                return [[float(x) for x in e] for e in embs]

            def embed_query(self, text: str):
                e = self.model.encode([text], show_progress_bar=False)[0]
                return [float(x) for x in e]
    except Exception:
        raise

from langchain_core.documents import Document
from langchain_text_splitters import CharacterTextSplitter

from src.db.duckdb_client import DuckDBClient
from src.sql.templates import SQL_TEMPLATES


@dataclass
class RetrievalResult:
    """Result from RAG retrieval"""
    query: str
    relevant_patterns: List[str]
    schema_info: str
    examples: List[Dict]
    context: str


class EnhancedRAGBuilder:
    """
    Build and manage RAG knowledge base for Text-to-SQL
    
    Features:
    - Database schema extraction and embedding
    - SQL pattern extraction from templates
    - Query example retrieval
    - Semantic search over knowledge base
    """
    
    def __init__(self, persist_dir: str = "../rag_db/chroma_text2sql"):
        """
        Initialize RAG builder
        
        Args:
            persist_dir: Directory to persist Chroma vector store
        """
        self.persist_dir = Path(persist_dir)
        self.db = DuckDBClient()
        
        # Initialize embeddings
        self.embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2",
            model_kwargs={"device": "cpu"}
        )
        
        self.vector_store = None
        self.retriever = None
    
    def extract_database_schema(self) -> str:
        """Extract schema information from DuckDB database"""
        schema_parts = []
        
        # Get all tables
        tables = self.db.get_tables()
        
        for table_name in tables:
            schema_parts.append(f"\n## Table: {table_name}")
            
            # Get columns
            columns = self.db.get_columns(table_name)
            schema_parts.append("Columns:")
            for col_name, col_type in columns:
                schema_parts.append(f"  - {col_name}: {col_type}")
        
        return "\n".join(schema_parts)
    
    def extract_sql_patterns(self) -> List[Dict]:
        """Extract SQL generation patterns from templates"""
        patterns = []
        
        for intent_type, template in SQL_TEMPLATES.items():
            patterns.append({
                "intent": intent_type,
                "template": template,
                "description": f"SQL template for {intent_type} queries"
            })
        
        return patterns
    
    def create_knowledge_base(self) -> None:
        """Create vector store with comprehensive knowledge base"""
        documents = []
        
        print("Building RAG Knowledge Base...")
        
        # 1. Add schema document
        schema = self.extract_database_schema()
        schema_doc = Document(
            page_content=f"Database Schema:\n{schema}",
            metadata={"type": "schema", "importance": "high"}
        )
        documents.append(schema_doc)
        print(f"  + Added schema document")
        
        # 2. Add SQL patterns
        patterns = self.extract_sql_patterns()
        for pattern in patterns:
            tpl = pattern.get('template')
            tpl_repr = getattr(tpl, '__name__', str(tpl))
            pattern_doc = Document(
                page_content=f"""Query Type: {pattern['intent']}
Description: {pattern['description']}
Template: {tpl_repr}""",
                metadata={"type": "pattern", "intent": pattern["intent"]}
            )
            documents.append(pattern_doc)
        print(f"  + Added {len(patterns)} SQL pattern documents")
        
        # 3. Add training examples
        training_examples = self._load_training_examples()
        for example in training_examples[:100]:  # Limit to first 100 for efficiency
            example_doc = Document(
                page_content=f"""User Query: {example.get('input', '')}
SQL Query: {example.get('output', '')}""",
                metadata={"type": "example"}
            )
            documents.append(example_doc)
        print(f"  + Added {len(training_examples[:100])} training examples")
        
        # 4. Add common metrics documentation
        metrics_doc = Document(
            page_content="""Common Sales Metrics:
            
- Total Sales: SUM(amount) - Sum of all transaction amounts
- Sales by Brand: Group by brand, sum amounts
- Sales by Region: Group by region, sum amounts
- Year-over-Year Growth: Compare sales between years
- Top Brands: Sort by sales volume descending
- Active Stores Count: Count stores with status='active'
- Regional Distribution: Count stores grouped by region
- Sales Comparison: Compare metrics between time periods
- Market Share: Calculate percentage of total sales
- Growth Trends: Calculate change over time periods""",
            metadata={"type": "metrics"}
        )
        documents.append(metrics_doc)
        print(f"  + Added metrics documentation")
        
        # Create vector store
        print(f"\n  Creating Chroma vector store with {len(documents)} documents...")
        self.persist_dir.parent.mkdir(parents=True, exist_ok=True)
        
        self.vector_store = Chroma.from_documents(
            documents=documents,
            embedding=self.embeddings,
            persist_directory=str(self.persist_dir)
        )
        
        # Create retriever
        self.retriever = self.vector_store.as_retriever(
            search_kwargs={"k": 5}
        )
        
        print(f"Vector store created at {self.persist_dir}")
    
    def load_vector_store(self) -> None:
        """Load existing vector store from disk"""
        if not self.persist_dir.exists():
            print(f"Vector store not found at {self.persist_dir}")
            self.create_knowledge_base()
            return
        
        print(f"Loading vector store from {self.persist_dir}...")
        self.vector_store = Chroma(
            embedding_function=self.embeddings,
            persist_directory=str(self.persist_dir)
        )
        self.retriever = self.vector_store.as_retriever(
            search_kwargs={"k": 5}
        )
        print("Vector store loaded")
    
    def retrieve(self, query: str) -> RetrievalResult:
        """
        Retrieve relevant information for a query
        
        Args:
            query: User natural language query
            
        Returns:
            RetrievalResult with relevant patterns, schema, and examples
        """
        if self.retriever is None:
            self.load_vector_store()
        
        # Retrieve documents (support different LangChain retriever APIs)
        try:
            docs = self.retriever.get_relevant_documents(query)
        except Exception:
            # fallback to older/underscored method (some versions require run_manager kwarg)
            try:
                docs = getattr(self.retriever, "_get_relevant_documents")(query, run_manager=None)
            except TypeError:
                docs = getattr(self.retriever, "_get_relevant_documents")(query)
        
        # Organize by type
        schema_docs = [d for d in docs if d.metadata.get("type") == "schema"]
        pattern_docs = [d for d in docs if d.metadata.get("type") == "pattern"]
        example_docs = [d for d in docs if d.metadata.get("type") == "example"]
        
        # Build result
        relevant_patterns = [d.page_content for d in pattern_docs]
        schema_info = schema_docs[0].page_content if schema_docs else ""
        examples = [
            {"pattern": d.page_content, "type": d.metadata.get("type")}
            for d in example_docs
        ]
        
        # Combine all context
        context = "\n\n".join([
            f"### Schema Information\n{schema_info}",
            f"### Relevant SQL Patterns\n" + "\n".join(relevant_patterns[:3]),
            f"### Similar Examples\n" + "\n".join([e["pattern"] for e in examples[:3]])
        ])
        
        return RetrievalResult(
            query=query,
            relevant_patterns=relevant_patterns,
            schema_info=schema_info,
            examples=examples,
            context=context
        )
    
    def _load_training_examples(self) -> List[Dict]:
        """Load training examples from JSONL file"""
        training_file = Path("../data/training_data_formatted.jsonl")
        
        examples = []
        if training_file.exists():
            with open(training_file, "r") as f:
                for line in f:
                    try:
                        data = json.loads(line)
                        # Parse the formatted text
                        if "text" in data:
                            text = data["text"]
                            # Extract input and output
                            if "<start_of_turn>user" in text:
                                input_part = text.split("<end_of_turn>")[0].split("user\n")[1]
                                if "<start_of_turn>model" in text:
                                    output_part = text.split("<start_of_turn>model")[1].split("<end_of_turn>")[0].strip()
                                    examples.append({
                                        "input": input_part.strip(),
                                        "output": output_part
                                    })
                    except:
                        continue
        
        return examples
    
    def save_knowledge_base(self) -> None:
        """Save knowledge base metadata"""
        if self.vector_store is not None:
            metadata = {
                "persist_dir": str(self.persist_dir),
                "embedding_model": "sentence-transformers/all-MiniLM-L6-v2",
                "created_at": str(Path.cwd()),
            }
            
            metadata_file = self.persist_dir / "metadata.json"
            with open(metadata_file, "w") as f:
                json.dump(metadata, f, indent=2)
            
            print(f"Knowledge base metadata saved to {metadata_file}")


class RAGQueryEnhancer:
    """Use RAG to enhance SQL generation prompts"""
    
    def __init__(self, rag_builder: Optional[EnhancedRAGBuilder] = None):
        self.rag = rag_builder or EnhancedRAGBuilder()
        self.rag.load_vector_store()
    
    def enhance_prompt(self, query: str) -> str:
        """
        Enhance a user query with RAG context for better SQL generation
        
        Args:
            query: User natural language query
            
        Returns:
            Enhanced prompt with schema and example context
        """
        retrieval_result = self.rag.retrieve(query)
        
        enhanced_prompt = f"""Generate SQL for the following query using the database schema and examples.

Database Schema:
{retrieval_result.schema_info}

Similar Query Examples:
{chr(10).join(retrieval_result.examples[:2])}

User Query: {query}

Generate the SQL query:"""
        
        return enhanced_prompt
    
    def get_context(self, query: str) -> Dict:
        """Get full RAG context for a query"""
        result = self.rag.retrieve(query)
        return {
            "query": query,
            "schema": result.schema_info,
            "patterns": result.relevant_patterns,
            "examples": result.examples,
            "full_context": result.context
        }


# Example usage and initialization
if __name__ == "__main__":
    # Build RAG knowledge base
    rag_builder = EnhancedRAGBuilder()
    rag_builder.create_knowledge_base()
    
    # Test retrieval
    test_queries = [
        "What were total sales in 2023?",
        "Show top 5 brands by revenue",
        "How many active stores by region?",
    ]
    
    print("\n" + "="*60)
    print("Testing RAG Retrieval")
    print("="*60)
    
    for query in test_queries:
        print(f"\nQuery: {query}")
        result = rag_builder.retrieve(query)
        print(f"Schema relevant: {bool(result.schema_info)}")
        print(f"Patterns found: {len(result.relevant_patterns)}")
        print(f"Examples found: {len(result.examples)}")
    
    # Test prompt enhancement
    enhancer = RAGQueryEnhancer(rag_builder)
    
    print("\n" + "="*60)
    print("Testing Prompt Enhancement")
    print("="*60)
    
    enhanced = enhancer.enhance_prompt("Total sales by region?")
    print(f"Enhanced prompt:\n{enhanced[:200]}...")
