try:
    from langchain_openai import ChatOpenAI
except ImportError:
    from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate, PromptTemplate
try:
    from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
except ImportError:
    from langchain.schema import HumanMessage, AIMessage, SystemMessage
from langchain.chains import LLMChain
from langchain_core.tools import tool
from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain import hub
from typing import Dict, List, Any
import json
from src.rag_system import RAGSystem, RAGFusionRetriever
from src.comparator import DocumentComparison
from src.config import settings


class DocumentAnalysisAgent:
    def __init__(self, rag_system: RAGSystem):
        self.rag = rag_system
        self.retriever = RAGFusionRetriever(rag_system)
        
        self.llm = ChatOpenAI(
            api_key=settings.OPENAI_API_KEY,
            model=settings.LLM_MODEL,
            temperature=settings.LLM_TEMPERATURE
        )
        
        self._setup_tools()
        self._setup_agent()
    
    def _setup_tools(self):
        @tool
        def search_documents(query: str) -> str:
            """Search through stored PDF documents using RAG Fusion retrieval"""
            results = self.retriever.retrieve_with_fusion(query, n_results=5)
            
            formatted_results = []
            for result in results:
                formatted_results.append({
                    'content': result['document'][:500],
                    'metadata': result['metadata']
                })
            
            return json.dumps(formatted_results, indent=2)
        
        @tool
        def get_document_details(doc_type: str) -> str:
            """Get detailed information about documents (PO or INVOICE)"""
            doc_type = doc_type.upper()
            results = self.rag.collection.get(
                where={"doc_type": doc_type}
            )
            
            if not results['documents']:
                return f"No documents found of type {doc_type}"
            
            unique_metadata = {}
            for metadata in results['metadatas']:
                doc_id = metadata.get('document_id')
                if doc_id not in unique_metadata:
                    unique_metadata[doc_id] = metadata
            
            return json.dumps(unique_metadata, indent=2)
        
        @tool
        def analyze_discrepancies(query: str) -> str:
            """Analyze specific discrepancies or mismatches in documents"""
            search_results = self.retriever.retrieve_with_fusion(query, n_results=10)
            
            analysis = {
                'query': query,
                'relevant_chunks': [r['document'][:300] for r in search_results],
                'metadata': [r['metadata'] for r in search_results]
            }
            
            return json.dumps(analysis, indent=2)
        
        @tool
        def get_comparison_summary(doc_id: str) -> str:
            """Get summary of document comparison and discrepancies"""
            summary = self.rag.get_document_summary(doc_id)
            return json.dumps(summary, indent=2)
        
        self.tools = [
            search_documents,
            get_document_details,
            analyze_discrepancies,
            get_comparison_summary
        ]
    
    def _setup_agent(self):
        prompt = hub.pull("hwchase17/openai-tools-agent-prompt")
        
        self.agent = create_openai_tools_agent(
            llm=self.llm,
            tools=self.tools,
            prompt=prompt
        )
        
        self.executor = AgentExecutor(
            agent=self.agent,
            tools=self.tools,
            verbose=True,
            handle_parsing_errors=True
        )
    
    def analyze_query(self, query: str) -> Dict[str, Any]:
        try:
            result = self.executor.invoke({"input": query})
            return {
                'query': query,
                'response': result.get('output', ''),
                'success': True
            }
        except Exception as e:
            return {
                'query': query,
                'error': str(e),
                'success': False
            }
    
    def analyze_comparison(self, query: str) -> str:
        return self.analyze_query(query)


class ComparisonAnalysisChain:
    def __init__(self, rag_system: RAGSystem):
        self.rag = rag_system
        
        self.llm = ChatOpenAI(
            api_key=settings.OPENAI_API_KEY,
            model=settings.LLM_MODEL,
            temperature=settings.LLM_TEMPERATURE
        )
    
    def analyze_comparison(self, comparison: DocumentComparison) -> Dict[str, Any]:
        discrepancies_text = self._format_discrepancies(comparison)
        
        prompt = ChatPromptTemplate.from_messages([
            SystemMessage(content="""You are an expert procurement analyst specializing in PO and Invoice reconciliation.
            Analyze the following discrepancies between a Purchase Order and Proforma Invoice.
            Provide:
            1. Key findings and insights
            2. Root cause analysis for major discrepancies
            3. Risk assessment (Critical, High, Medium, Low)
            4. Recommended actions
            5. Questions for vendor or internal team"""),
            
            HumanMessage(content=f"""Please analyze these discrepancies:
            
{discrepancies_text}

Provide a detailed analysis with actionable recommendations.""")
        ])
        
        chain = LLMChain(llm=self.llm, prompt=prompt)
        response = chain.run()
        
        return {
            'analysis': response,
            'comparison_summary': comparison.summary,
            'discrepancies_count': len(comparison.discrepancies)
        }
    
    def _format_discrepancies(self, comparison: DocumentComparison) -> str:
        lines = [
            f"PO ID: {comparison.po_doc_id}",
            f"Invoice ID: {comparison.invoice_doc_id}",
            f"Total Discrepancies: {len(comparison.discrepancies)}\n"
        ]
        
        for disc in comparison.discrepancies[:10]:
            lines.append(f"- Item: {disc.description}")
            lines.append(f"  PO Qty: {disc.po_quantity}, Invoice Qty: {disc.invoice_quantity} (Diff: {disc.quantity_variance_pct:.1f}%)")
            lines.append(f"  PO Price: ${disc.po_unit_price:.2f}, Invoice Price: ${disc.invoice_unit_price:.2f} (Diff: {disc.price_variance_pct:.1f}%)")
            lines.append(f"  Status: {disc.status}\n")
        
        return "\n".join(lines)


class PromptTemplateManager:
    @staticmethod
    def get_extraction_prompt() -> ChatPromptTemplate:
        return ChatPromptTemplate.from_messages([
            SystemMessage(content="You are an expert at extracting structured data from unstructured documents."),
            HumanMessage(content="Extract all line items from this document:\n{document_text}")
        ])
    
    @staticmethod
    def get_comparison_prompt() -> ChatPromptTemplate:
        return ChatPromptTemplate.from_messages([
            SystemMessage(content="You are a procurement expert analyzing PO vs Invoice discrepancies."),
            HumanMessage(content="Analyze these discrepancies:\n{discrepancies}")
        ])
    
    @staticmethod
    def get_recommendation_prompt() -> ChatPromptTemplate:
        return ChatPromptTemplate.from_messages([
            SystemMessage(content="You are a procurement specialist providing recommendations."),
            HumanMessage(content="Based on this analysis, what actions should be taken?\n{analysis}")
        ])


def create_analysis_agent(rag_system: RAGSystem) -> DocumentAnalysisAgent:
    return DocumentAnalysisAgent(rag_system)


def create_comparison_analyzer(rag_system: RAGSystem) -> ComparisonAnalysisChain:
    return ComparisonAnalysisChain(rag_system)
