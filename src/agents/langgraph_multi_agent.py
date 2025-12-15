"""
Multi-Agent LangGraph System for Text-to-SQL with RAG Enhancement
Combines intent classification, entity extraction, RAG retrieval, and SQL generation
"""

import json
from typing import Any, Dict, List, Optional
from dataclasses import dataclass
from enum import Enum

try:
    from langchain_core.language_model import BaseLanguageModel
except Exception:
    class BaseLanguageModel:  # fallback shim for test environments
        pass

try:
    from langchain_core.prompts import PromptTemplate
except Exception:
    class PromptTemplate:
        @staticmethod
        def from_template(tpl):
            return tpl

try:
    from langchain.agents import AgentExecutor, create_react_agent
except Exception:
    # Fallbacks for environments with different langchain versions
    def create_react_agent(*args, **kwargs):
        raise RuntimeError("create_react_agent not available in this langchain version")

    class AgentExecutor:
        @classmethod
        def from_agent_and_tools(cls, *args, **kwargs):
            raise RuntimeError("AgentExecutor not available in this langchain version")

try:
    from langchain_core.tools import BaseTool, tool
except Exception:
    class BaseTool:
        pass

    def tool(f):
        return f

try:
    from langchain.tools.retriever import create_retriever_tool
except Exception:
    def create_retriever_tool(*args, **kwargs):
        raise RuntimeError("create_retriever_tool not available in this environment")
from pydantic import BaseModel

try:
    from src.agents.intent_classifier import IntentClassifier
except Exception:
    # Compatibility shim: older intent_classifier exposes detect_intent function
    try:
        from src.agents.intent_classifier import detect_intent

        class IntentClassifier:
            def classify(self, q: str):
                return {"type": detect_intent(q), "confidence": 1.0}
    except Exception:
        class IntentClassifier:
            def classify(self, q: str):
                return {"type": "unknown", "confidence": 0.0}

try:
    from src.agents.entity_extractor import EntityExtractor
except Exception:
    # Compatibility shim: older entity_extractor exposes extract_entities function
    try:
        from src.agents.entity_extractor import extract_entities

        class EntityExtractor:
            def extract(self, q: str, intent: Dict = None):
                return {"metrics": [], "filters": {}, "group_by": None, "order_by": None, "limit": None, **extract_entities(q).__dict__}
    except Exception:
        class EntityExtractor:
            def extract(self, q: str, intent: Dict = None):
                return {"metrics": [], "filters": {}, "group_by": None, "order_by": None, "limit": None}
from src.db.duckdb_client import DuckDBClient
try:
    from src.sql.templates import SQL_TEMPLATES
except Exception:
    SQL_TEMPLATES = {}

from src.charts.chart_agent import ChartAgent
try:
    from src.rag.rag_agent import RAGAgent
except Exception:
    # Fallback to older/alternate class name
    try:
        from src.rag.rag_agent import RagAgent as RAGAgent
    except Exception:
        class RAGAgent:
            def __init__(self, *args, **kwargs):
                raise RuntimeError("RAGAgent not available in this environment")

try:
    from src.agents.gemma_sql_agent import GemmaSQLAgent
except Exception:
    class GemmaSQLAgent:
        def __init__(self, *args, **kwargs):
            pass
        def is_loaded(self):
            return False
        def generate(self, intent, entities):
            return {"sql": None, "error": "GemmaSQLAgent not available"}


class QueryType(str, Enum):
    """Query type enumeration"""
    SALES = "sales"
    ACTIVE_STORE = "active_store"
    HYBRID = "hybrid"
    RAG_ONLY = "rag_only"


@dataclass
class AgentState:
    """State object for multi-agent system"""
    user_query: str
    intent: Dict[str, Any] = None
    entities: Dict[str, Any] = None
    query_type: QueryType = None
    sql: str = None
    results_df: Any = None
    explanation: str = None
    chart_data: Optional[Dict] = None
    rag_context: Optional[str] = None
    error: Optional[str] = None
    
    def to_dict(self) -> Dict:
        """Convert state to dictionary"""
        return {
            "user_query": self.user_query,
            "intent": self.intent,
            "entities": self.entities,
            "query_type": self.query_type.value if self.query_type else None,
            "sql": self.sql,
            "results": self.results_df.to_dict(orient="records") if self.results_df is not None else None,
            "explanation": self.explanation,
            "chart_data": self.chart_data,
            "rag_context": self.rag_context,
            "error": self.error,
        }


class IntentClassifierAgent:
    """Agent for classifying user intent"""
    
    def __init__(self, llm: Optional[BaseLanguageModel] = None):
        self.classifier = IntentClassifier()
        self.llm = llm
    
    def classify(self, query: str) -> Dict[str, Any]:
        """Classify query intent"""
        result = self.classifier.classify(query)
        return {
            "type": result["type"],
            "confidence": result.get("confidence", 0.0),
            "metrics": result.get("metrics", []),
            "time_period": result.get("time_period"),
        }


class EntityExtractionAgent:
    """Agent for extracting entities from query"""
    
    def __init__(self, llm: Optional[BaseLanguageModel] = None):
        self.extractor = EntityExtractor()
        self.llm = llm
    
    def extract(self, query: str, intent: Dict) -> Dict[str, Any]:
        """Extract entities from query"""
        entities = self.extractor.extract(query, intent)
        
        # Handle both dict and Entities object formats
        if hasattr(entities, '__dict__'):
            entities_dict = entities.__dict__
        else:
            entities_dict = entities if isinstance(entities, dict) else {}
        
        return {
            "brand": entities_dict.get("brand"),
            "month": entities_dict.get("month"),
            "year": entities_dict.get("year"),
            "year_2": entities_dict.get("year_2"),
            "group_by": entities_dict.get("group_by"),
            "top_n": entities_dict.get("top_n"),
            "metrics": entities_dict.get("metrics", []),
            "filters": entities_dict.get("filters", {}),
            "order_by": entities_dict.get("order_by"),
            "limit": entities_dict.get("limit"),
        }


class SQLGenerationAgent:
    """Agent for generating SQL from intent and entities"""
    
    def __init__(self, llm: Optional[BaseLanguageModel] = None, use_gemma: bool = True):
        self.llm = llm
        self.templates = SQL_TEMPLATES
        self.db = DuckDBClient()
        
        self.gemma_agent = None
        if use_gemma:
            try:
                self.gemma_agent = GemmaSQLAgent()
            except Exception as e:
                print(f"[WARNING] Could not initialize Gemma agent: {e}")
    
    def generate(self, intent: Dict, entities: Dict, rag_context: Optional[str] = None) -> Dict[str, Any]:
        """Generate SQL query"""
        intent_type = intent.get("type", "")
        
        # Try Gemma model first if available
        if self.gemma_agent and self.gemma_agent.is_loaded():
            try:
                gemma_result = self.gemma_agent.generate(intent, entities)
                if gemma_result.get("sql"):
                    return {
                        "sql": gemma_result["sql"],
                        "query_type": QueryType.SALES if intent_type in ["total_sales", "sales_comparison", "sales_yoy", "sales_summary"] else QueryType.ACTIVE_STORE,
                        "error": None,
                        "model": "gemma",
                    }
            except Exception as e:
                print(f"[WARNING] Gemma generation failed, falling back to templates: {e}")
        
        # Map intent type to template key
        intent_to_template_key = {
            "sales_total": "total_sales",
            "sales_yoy": "sales_yoy",
            "sales_summary": "sales_summary",
            "sales_comparison": "sales_yoy",
            "active_store_total": "active_store_total",
            "active_store_yoy": "active_store_yoy",
            "active_store_summary": "active_store_summary",
        }
        
        template_key = intent_to_template_key.get(intent_type, intent_type.lower())
        
        if template_key not in self.templates:
            return {
                "sql": None,
                "error": f"No template found for intent type: {intent_type}",
                "query_type": QueryType.RAG_ONLY,
            }
        
        template_func = self.templates[template_key]
        
        # Extract entities for template function
        entities_obj = entities
        if hasattr(entities, '__dict__'):
            entities_obj = entities.__dict__
        elif isinstance(entities, dict):
            entities_obj = entities
        
        # Build query parameters based on template type
        template_params = {}
        
        # Common parameters for all templates
        if "brand" in entities_obj:
            template_params["brand"] = entities_obj.get("brand")
        if "month" in entities_obj:
            template_params["month"] = entities_obj.get("month")
        
        # YoY-specific parameters (for comparison queries)
        if "yoy" in template_key or "comparison" in intent_type.lower():
            # YoY queries need year_1 and year_2
            if "year_2" in entities_obj:
                template_params["year_2"] = entities_obj.get("year_2")
            else:
                template_params["year_2"] = entities_obj.get("year")
            
            # For year_1, if no year_2, use year for year_1
            if "year" in entities_obj and "year_2" not in entities_obj:
                template_params["year_1"] = entities_obj.get("year")
            elif entities_obj.get("year"):
                template_params["year_1"] = entities_obj.get("year")
        else:
            # Non-YoY queries use single year parameter
            if "year" in entities_obj:
                template_params["year"] = entities_obj.get("year")
        
        # Summary-specific parameters
        if "summary" in template_key:
            if "group_by" in entities_obj:
                template_params["group_by"] = entities_obj.get("group_by")
            if "top_n" in entities_obj:
                template_params["top_n"] = entities_obj.get("top_n")
        
        # Remove None values
        template_params = {k: v for k, v in template_params.items() if v is not None}
        
        try:
            sql = template_func(**template_params)
            return {
                "sql": sql,
                "query_type": QueryType.SALES if "sales" in template_key else QueryType.ACTIVE_STORE,
                "error": None,
                "model": "template",
            }
        except Exception as e:
            return {
                "sql": None,
                "error": f"Error generating SQL: {str(e)}",
                "query_type": QueryType.RAG_ONLY,
            }
    
    def execute(self, sql: str) -> Dict[str, Any]:
        """Execute SQL and return results"""
        try:
            df = self.db.query(sql)
            return {
                "results": df,
                "row_count": len(df),
                "error": None,
            }
        except Exception as e:
            return {
                "results": None,
                "row_count": 0,
                "error": f"SQL execution error: {str(e)}",
            }


class RAGEnhancementAgent:
    """Agent for RAG-based context retrieval and enhancement"""
    
    def __init__(self, llm: Optional[BaseLanguageModel] = None):
        self.llm = llm
        self.rag_agent = None
        try:
            self.rag_agent = RAGAgent()
        except Exception as e:
            print(f"[WARNING] RAGAgent initialization failed: {e}")
            self.rag_agent = None
    
    def retrieve_context(self, query: str, intent: Dict) -> Dict[str, Any]:
        """Retrieve relevant context from RAG"""
        if not self.rag_agent:
            return {
                "context": None,
                "retrieved": False,
                "error": "RAG agent not available",
            }
        
        try:
            context = self.rag_agent.retrieve(query)
            return {
                "context": context,
                "retrieved": True,
                "error": None,
            }
        except Exception as e:
            return {
                "context": None,
                "retrieved": False,
                "error": f"RAG retrieval error: {str(e)}",
            }


class ChartGenerationAgent:
    """Agent for generating charts from results"""
    
    def __init__(self):
        self.chart_agent = ChartAgent()
    
    def generate_chart(self, results_df, intent: Dict) -> Dict[str, Any]:
        """Generate chart from results"""
        try:
            chart_data = self.chart_agent.generate_chart(results_df, intent)
            return {
                "chart": chart_data,
                "error": None,
            }
        except Exception as e:
            return {
                "chart": None,
                "error": f"Chart generation error: {str(e)}",
            }


class MultiAgentOrchestrator:
    """
    Main orchestrator for multi-agent system.
    Coordinates flow between intent classification, entity extraction, 
    SQL generation, RAG enhancement, and chart generation.
    """
    
    def __init__(self, llm: Optional[BaseLanguageModel] = None):
        self.llm = llm
        
        # Initialize agents
        self.intent_agent = IntentClassifierAgent(llm)
        self.entity_agent = EntityExtractionAgent(llm)
        self.sql_agent = SQLGenerationAgent(llm)
        self.rag_agent = RAGEnhancementAgent(llm)
        self.chart_agent = ChartGenerationAgent()
        self.db = DuckDBClient()
    
    def process(self, query: str, use_rag: bool = True) -> AgentState:
        """
        Process user query through multi-agent system
        
        Flow:
        1. Intent Classification - Determine what user wants
        2. Entity Extraction - Extract metrics, filters, grouping
        3. RAG Enhancement - Retrieve relevant context (optional)
        4. SQL Generation - Generate SQL based on intent/entities
        5. SQL Execution - Run query against database
        6. Chart Generation - Create visualization if applicable
        
        Args:
            query: User natural language query
            use_rag: Whether to use RAG enhancement
            
        Returns:
            AgentState with complete processing results
        """
        
        state = AgentState(user_query=query)
        
        # Step 1: Classify Intent
        try:
            intent = self.intent_agent.classify(query)
            state.intent = intent
        except Exception as e:
            state.error = f"Intent classification failed: {str(e)}"
            return state
        
        # Step 2: Extract Entities
        try:
            entities = self.entity_agent.extract(query, intent)
            state.entities = entities
        except Exception as e:
            state.error = f"Entity extraction failed: {str(e)}"
            return state
        
        # Step 3: RAG Enhancement (optional)
        rag_context = None
        if use_rag:
            try:
                rag_result = self.rag_agent.retrieve_context(query, intent)
                if rag_result["retrieved"]:
                    rag_context = rag_result["context"]
                    state.rag_context = rag_context
            except Exception as e:
                # RAG failure is not fatal, continue with template-based approach
                print(f"Warning: RAG enhancement failed: {str(e)}")
        
        # Step 4: Generate SQL
        try:
            sql_result = self.sql_agent.generate(intent, entities, rag_context)
            state.sql = sql_result.get("sql")
            state.query_type = sql_result.get("query_type")
            
            if sql_result.get("error"):
                state.error = sql_result["error"]
                return state
        except Exception as e:
            state.error = f"SQL generation failed: {str(e)}"
            return state
        
        # Step 5: Execute SQL
        if state.sql:
            try:
                exec_result = self.sql_agent.execute(state.sql)
                state.results_df = exec_result["results"]
                
                if exec_result.get("error"):
                    state.error = exec_result["error"]
                    return state
                
            except Exception as e:
                state.error = f"SQL execution failed: {str(e)}"
                return state
        
        # Step 6: Generate Chart (if results available)
        if state.results_df is not None and len(state.results_df) > 0:
            try:
                chart_result = self.chart_agent.generate_chart(state.results_df, intent)
                state.chart_data = chart_result.get("chart")
            except Exception as e:
                print(f"Warning: Chart generation failed: {str(e)}")
        
        return state


# Standalone tools for LangChain integration
@tool
def classify_intent(query: str) -> str:
    """Classify the intent of a user query (sales, active stores, comparison, etc.)"""
    agent = IntentClassifierAgent()
    result = agent.classify(query)
    return json.dumps(result)


@tool
def extract_entities_tool(query: str, intent_json: str) -> str:
    """Extract entities (metrics, filters, grouping) from query"""
    agent = EntityExtractionAgent()
    intent = json.loads(intent_json)
    result = agent.extract(query, intent)
    return json.dumps(result)


@tool
def generate_sql(intent_json: str, entities_json: str) -> str:
    """Generate SQL query from intent and entities"""
    agent = SQLGenerationAgent()
    intent = json.loads(intent_json)
    entities = json.loads(entities_json)
    result = agent.generate(intent, entities)
    return json.dumps(result)


@tool
def execute_sql(sql: str) -> str:
    """Execute SQL query and return results"""
    agent = SQLGenerationAgent()
    result = agent.execute(sql)
    return json.dumps({
        "row_count": result["row_count"],
        "error": result["error"],
        "preview": result["results"].head(5).to_dict(orient="records") if result["results"] is not None else None,
    })


@tool  
def retrieve_rag_context(query: str) -> str:
    """Retrieve relevant context from RAG system"""
    agent = RAGEnhancementAgent()
    result = agent.retrieve_context(query, {})
    return json.dumps(result)


# Build LangChain agent with tools
def create_react_agent_executor(llm: BaseLanguageModel) -> AgentExecutor:
    """Create a ReAct agent executor with all tools"""
    
    tools = [
        classify_intent,
        extract_entities_tool,
        generate_sql,
        execute_sql,
        retrieve_rag_context,
    ]
    
    prompt = PromptTemplate.from_template("""
You are an AI assistant that helps users analyze sales data using SQL queries.

You have access to the following tools:
{tools}

Use the following format:

Question: the input question you must answer
Thought: you should always think about what to do
Action: the action to take, should be one of [{tool_names}]
Action Input: the input to the action
Observation: the result of the action
... (this Thought/Action/Observation can repeat N times)
Thought: I now know the final answer
Final Answer: the final answer to the original input question

Begin!

Question: {input}
Thought:{agent_scratchpad}
""")
    
    agent = create_react_agent(llm, tools, prompt)
    executor = AgentExecutor.from_agent_and_tools(
        agent=agent,
        tools=tools,
        verbose=True,
        handle_parsing_errors=True,
        max_iterations=10,
    )
    
    return executor


if __name__ == "__main__":
    # Example usage
    orchestrator = MultiAgentOrchestrator()
    
    # Test queries
    test_queries = [
        "What were total sales in 2023?",
        "Compare sales between 2023 and 2024",
        "How many active stores do we have by region?",
        "Top 5 brands by sales",
    ]
    
    for query in test_queries:
        print(f"\n{'='*60}")
        print(f"Query: {query}")
        print(f"{'='*60}")
        
        state = orchestrator.process(query)
        
        print(f"Intent: {state.intent}")
        print(f"Entities: {state.entities}")
        print(f"Query Type: {state.query_type}")
        print(f"SQL: {state.sql}")
        
        if state.results_df is not None:
            print(f"Results ({len(state.results_df)} rows):")
            print(state.results_df.head())
        
        if state.error:
            print(f"Error: {state.error}")
