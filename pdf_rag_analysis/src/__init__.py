from src.config import settings
from src.pdf_extractor import PDFExtractor, extract_all_pdfs
from src.comparator import EnhancedDocumentComparator, compare_po_with_invoice
from src.report_generator import EnhancedReportGenerator, generate_all_reports

try:
    from src.rag_system import RAGSystem, initialize_rag_system, RAGFusionRetriever
except Exception:
    from src.rag_system_simple import SimpleRAGSystem as RAGSystem
    from src.rag_system_simple import initialize_rag_system, SimpleRAGFusionRetriever as RAGFusionRetriever

try:
    from src.agent_rag import DocumentAnalysisAgent, create_analysis_agent
except Exception:
    DocumentAnalysisAgent = None
    create_analysis_agent = None

try:
    from src.chatbot import PDFAnalysisChatbot, initialize_chatbot
except Exception:
    from src.chatbot_simple import SimplePDFChatbot as PDFAnalysisChatbot
    from src.chatbot_simple import initialize_simple_chatbot as initialize_chatbot

from src.orchestrator import PDFAnalysisOrchestrator

__all__ = [
    'settings',
    'PDFExtractor',
    'extract_all_pdfs',
    'DocumentComparator',
    'compare_po_with_invoice',
    'ReportGenerator',
    'generate_all_reports',
    'RAGSystem',
    'initialize_rag_system',
    'RAGFusionRetriever',
    'DocumentAnalysisAgent',
    'create_analysis_agent',
    'PDFAnalysisChatbot',
    'initialize_chatbot',
    'PDFAnalysisOrchestrator',
]
