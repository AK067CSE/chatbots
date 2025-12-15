from typing import Any, Dict, List, Optional
import json
from datetime import datetime

try:
    from langchain.chat_models import ChatOpenAI
except ImportError:
    from langchain_openai import ChatOpenAI

try:
    from langchain.prompts import ChatPromptTemplate, PromptTemplate
    from langchain.chains import LLMChain
    from langchain.schema import HumanMessage, SystemMessage
except ImportError:
    from langchain_core.prompts import ChatPromptTemplate, PromptTemplate
    from langchain_core.output_parsers import StrOutputParser

from src.config import settings


class DocumentAnalysisChain:
    def __init__(self, llm_model: str = "gpt-4-turbo-preview", temperature: float = 0.7):
        self.llm = ChatOpenAI(
            model=llm_model,
            temperature=temperature,
            openai_api_key=settings.OPENAI_API_KEY
        )
    
    def analyze_discrepancies(self, po_items: List[Dict], invoice_items: List[Dict]) -> str:
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an expert financial auditor analyzing discrepancies between Purchase Orders and Proforma Invoices.
Provide a clear, concise analysis of the differences found."""),
            ("user", """Analyze the following discrepancies:

PO Items: {po_items}

Invoice Items: {invoice_items}

Provide:
1. Summary of key discrepancies
2. Financial impact
3. Recommended actions""")
        ])
        
        chain = prompt | self.llm
        
        response = chain.invoke({
            "po_items": json.dumps(po_items, indent=2),
            "invoice_items": json.dumps(invoice_items, indent=2)
        })
        
        return response.content if hasattr(response, 'content') else str(response)
    
    def extract_financial_summary(self, document_text: str, doc_type: str) -> Dict[str, Any]:
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a financial data extraction expert. Extract key financial information from documents.
Return a JSON object with the extracted data."""),
            ("user", """Extract financial summary from this {doc_type}:

{document_text}

Return JSON with: subtotal, discounts, taxable_amount, tax, grand_total""")
        ])
        
        chain = prompt | self.llm
        
        response = chain.invoke({
            "document_text": document_text[:2000],
            "doc_type": doc_type
        })
        
        try:
            return json.loads(response.content if hasattr(response, 'content') else str(response))
        except:
            return {"raw_response": str(response)}


class MultiTurnChatChain:
    def __init__(self, llm_model: str = "gpt-4-turbo-preview", temperature: float = 0.7):
        self.llm = ChatOpenAI(
            model=llm_model,
            temperature=temperature,
            openai_api_key=settings.OPENAI_API_KEY
        )
        self.conversation_history = []
    
    def chat(self, user_query: str, context: str = "", system_prompt: str = None) -> str:
        if system_prompt is None:
            system_prompt = """You are an intelligent PDF document assistant. 
You help users understand and analyze Purchase Orders and Proforma Invoices.
Be concise, accurate, and helpful. Use the provided context to answer questions."""
        
        self.conversation_history.append({
            "role": "user",
            "content": user_query,
            "timestamp": datetime.now().isoformat()
        })
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("user", """Context from documents:
{context}

User query: {query}

Provide a helpful, accurate response based on the context and your knowledge.""")
        ])
        
        chain = prompt | self.llm
        
        response = chain.invoke({
            "context": context,
            "query": user_query
        })
        
        assistant_response = response.content if hasattr(response, 'content') else str(response)
        
        self.conversation_history.append({
            "role": "assistant",
            "content": assistant_response,
            "timestamp": datetime.now().isoformat()
        })
        
        return assistant_response
    
    def get_history(self) -> List[Dict]:
        return self.conversation_history
    
    def clear_history(self):
        self.conversation_history = []


class ComparisonAnalysisChain:
    def __init__(self, llm_model: str = "gpt-4-turbo-preview"):
        self.llm = ChatOpenAI(
            model=llm_model,
            temperature=0.5,
            openai_api_key=settings.OPENAI_API_KEY
        )
    
    def generate_comparison_report(self, comparison_data: Dict[str, Any]) -> str:
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a financial comparison expert. 
Generate a professional analysis report of PO vs Invoice comparison.
Be thorough but concise."""),
            ("user", """Generate a comparison report based on:

{comparison_data}

Include:
1. Executive Summary
2. Line Item Analysis
3. Financial Summary
4. Risk Assessment
5. Recommendations""")
        ])
        
        chain = prompt | self.llm
        
        response = chain.invoke({
            "comparison_data": json.dumps(comparison_data, indent=2)
        })
        
        return response.content if hasattr(response, 'content') else str(response)


class IntelligentQueryProcessor:
    def __init__(self, llm_model: str = "gpt-4-turbo-preview"):
        self.llm = ChatOpenAI(
            model=llm_model,
            temperature=0.3,
            openai_api_key=settings.OPENAI_API_KEY
        )
    
    def classify_query(self, query: str) -> Dict[str, Any]:
        prompt = ChatPromptTemplate.from_messages([
            ("system", """Classify user queries about PDF documents.
Return JSON with: query_type, intent, keywords, confidence"""),
            ("user", """Classify this query: {query}

Return JSON.""")
        ])
        
        chain = prompt | self.llm
        
        response = chain.invoke({"query": query})
        
        try:
            return json.loads(response.content if hasattr(response, 'content') else str(response))
        except:
            return {"query_type": "general", "intent": "unknown"}
    
    def generate_followup_questions(self, context: str, user_query: str) -> List[str]:
        prompt = ChatPromptTemplate.from_messages([
            ("system", """Generate relevant follow-up questions based on context and user query.
Return a JSON list of 3-5 follow-up questions."""),
            ("user", """Context: {context}

User query: {query}

Generate follow-up questions as JSON list.""")
        ])
        
        chain = prompt | self.llm
        
        response = chain.invoke({
            "context": context[:1000],
            "query": user_query
        })
        
        try:
            return json.loads(response.content if hasattr(response, 'content') else str(response))
        except:
            return []
    
    def summarize_documents(self, documents: List[str]) -> str:
        prompt = ChatPromptTemplate.from_messages([
            ("system", "You are a document summarization expert. Create concise summaries."),
            ("user", "Summarize these documents:\n\n{documents}")
        ])
        
        chain = prompt | self.llm
        
        combined_docs = "\n\n".join(documents[:3])
        
        response = chain.invoke({"documents": combined_docs[:2000]})
        
        return response.content if hasattr(response, 'content') else str(response)


class LLMChainOrchestrator:
    def __init__(self):
        self.doc_analysis = DocumentAnalysisChain()
        self.chat = MultiTurnChatChain()
        self.comparison = ComparisonAnalysisChain()
        self.query_processor = IntelligentQueryProcessor()
    
    def process_query(self, query: str, context: str, use_advanced: bool = True) -> Dict[str, Any]:
        classification = self.query_processor.classify_query(query) if use_advanced else {}
        
        response = self.chat.chat(query, context)
        
        followups = self.query_processor.generate_followup_questions(context, query) if use_advanced else []
        
        return {
            "query": query,
            "response": response,
            "classification": classification,
            "followup_questions": followups,
            "timestamp": datetime.now().isoformat()
        }
    
    def analyze_full_comparison(self, comparison_data: Dict, retrieved_context: List[str]) -> Dict[str, Any]:
        report = self.comparison.generate_comparison_report(comparison_data)
        summary = self.query_processor.summarize_documents(retrieved_context)
        
        return {
            "report": report,
            "summary": summary,
            "timestamp": datetime.now().isoformat()
        }
