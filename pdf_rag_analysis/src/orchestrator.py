# from pathlib import Path
# from typing import Dict
# import json
# from src.config import settings
# from src.pdf_extractor import extract_all_pdfs, ExtractedDocument
# from src.comparator import compare_po_with_invoice
# from src.report_generator import generate_all_reports
# try:
#     from src.rag_system import initialize_rag_system
# except Exception as e:
#     from src.rag_system_simple import initialize_rag_system

# try:
#     from src.chatbot import initialize_chatbot
# except Exception:
#     from src.chatbot_simple import initialize_simple_chatbot as initialize_chatbot


# class PDFAnalysisOrchestrator:
#     def __init__(self):
#         self.data_dir = settings.DATA_DIR
#         self.reports_dir = settings.REPORTS_DIR
#         self.reports_dir.mkdir(parents=True, exist_ok=True)
        
#         self.extracted_documents = {}
#         self.po_doc = None
#         self.invoice_doc = None
#         self.comparison_result = None
#         self.rag_system = None
#         self.analysis_agent = None
#         self.chatbot = None
    
#     def run_complete_pipeline(self) -> Dict:
#         print("\n" + "="*60)
#         print("PDF ANALYSIS PIPELINE - COMPLETE WORKFLOW")
#         print("="*60 + "\n")
        
#         print("[STEP 1/6] Extracting PDF documents...")
#         self.extract_documents()
        
#         print("[STEP 2/6] Comparing PO with Invoice...")
#         self.compare_documents()
        
#         print("[STEP 3/6] Generating reports...")
#         self.generate_reports()
        
#         print("[STEP 4/6] Initializing RAG system...")
#         self.initialize_rag()
        
#         print("[STEP 5/6] Setting up analysis agent...")
#         self.setup_agent()
        
#         print("[STEP 6/6] Initializing chatbot...")
#         self.setup_chatbot()
        
#         return self.get_pipeline_summary()
    
#     def extract_documents(self) -> Dict[str, ExtractedDocument]:
#         self.extracted_documents = extract_all_pdfs(self.data_dir)
        
#         for name, doc in self.extracted_documents.items():
#             print(f"  [OK] Extracted {name}")
#             print(f"    - Type: {doc.metadata.doc_type}")
#             print(f"    - Items: {len(doc.items)}")
#             print(f"    - Total: ${doc.total:.2f}")
        
#         return self.extracted_documents
    
#     def compare_documents(self):
#         self.po_doc = None
#         self.invoice_doc = None
        
#         for name, doc in self.extracted_documents.items():
#             if 'PURCHASE_ORDER' in doc.metadata.doc_type:
#                 self.po_doc = doc
#             elif 'PROFORMA_INVOICE' in doc.metadata.doc_type:
#                 self.invoice_doc = doc
        
#         if self.po_doc and self.invoice_doc:
#             self.comparison_result = compare_po_with_invoice(self.po_doc, self.invoice_doc)
#             print(f"  [OK] Comparison completed")
#             print(f"    - Discrepancies found: {len(self.comparison_result.discrepancies)}")
#             print(f"    - Total difference: ${self.comparison_result.grand_total_diff:.2f}")
#         else:
#             print("  [ERR] Could not find both PO and Invoice documents")
    
#     def generate_reports(self) -> Dict[str, str]:
#         if not self.comparison_result:
#             print("  [ERR] No comparison result to report")
#             return {}
        
#         report_paths = generate_all_reports(self.comparison_result, self.reports_dir, self.po_doc, self.invoice_doc)
        
#         for format_type, path in report_paths.items():
#             print(f"  [OK] Generated {format_type.upper()} report: {Path(path).name}")
        
#         return report_paths
    
#     def initialize_rag(self):
#         self.rag_system = initialize_rag_system(settings.CHROMA_DB_PATH)
#         print(f"  [OK] RAG system initialized at {settings.CHROMA_DB_PATH}")
        
#         for name, doc in self.extracted_documents.items():
#             self.rag_system.add_document(doc, name)
        
#         print(f"  [OK] Added {len(self.extracted_documents)} documents to RAG system")
    
#     def setup_agent(self):
#         if not self.rag_system:
#             print("  [ERR] RAG system not initialized")
#             return
        
#         try:
#             from src.agent_rag import create_analysis_agent as create_agent
#             self.analysis_agent = create_agent(self.rag_system)
#             print("  [OK] Analysis agent ready")
#         except Exception as e:
#             print(f"  [WARN] Analysis agent setup skipped: {e}")
    
#     def setup_chatbot(self):
#         if not self.rag_system:
#             print("  [ERR] RAG system not initialized")
#             return
        
#         try:
#             self.chatbot = initialize_chatbot(self.rag_system)
#             print("  [OK] Chatbot initialized and ready")
#         except Exception as e:
#             print(f"  [WARN] Using simplified chatbot: {e}")
#             try:
#                 from src.chatbot_simple import initialize_simple_chatbot
#                 self.chatbot = initialize_simple_chatbot(self.rag_system)
#                 print("  [OK] Simplified chatbot initialized")
#             except Exception as e2:
#                 print(f"  [ERR] Chatbot initialization failed: {e2}")
    
#     def analyze_with_agent(self, query: str) -> Dict:
#         if not self.analysis_agent:
#             return {'error': 'Agent not initialized'}
        
#         return self.analysis_agent.analyze_query(query)
    
#     def chat(self, user_query: str) -> Dict:
#         if not self.chatbot:
#             return {'error': 'Chatbot not initialized'}
        
#         return self.chatbot.chat(user_query)
    
#     def get_pipeline_summary(self) -> Dict:
#         return {
#             'status': 'complete',
#             'documents_extracted': len(self.extracted_documents),
#             'discrepancies_found': len(self.comparison_result.discrepancies) if self.comparison_result else 0,
#             'reports_generated': 4,
#             'rag_ready': self.rag_system is not None,
#             'agent_ready': self.analysis_agent is not None,
#             'chatbot_ready': self.chatbot is not None,
#             'reports_directory': str(self.reports_dir),
#             'rag_db_path': str(settings.CHROMA_DB_PATH)
#         }
    
#     def print_pipeline_summary(self):
#         summary = self.get_pipeline_summary()
#         print("\n" + "="*60)
#         print("PIPELINE SUMMARY")
#         print("="*60)
#         for key, value in summary.items():
#             print(f"{key}: {value}")
#         print("="*60 + "\n")
    
#     def interactive_analysis(self):
#         print("\n" + "="*60)
#         print("INTERACTIVE ANALYSIS MODE")
#         print("="*60)
#         print("Type 'help' for commands, 'exit' to quit\n")
        
#         while True:
#             try:
#                 user_input = input("Query> ").strip()
                
#                 if not user_input:
#                     continue
                
#                 if user_input.lower() == 'exit':
#                     print("Exiting...")
#                     break
                
#                 if user_input.lower() == 'help':
#                     print("""
# COMMANDS:
# - Any natural language question about the documents
# - 'compare' - Show comparison details
# - 'discrepancies' - List all discrepancies
# - 'summary' - Show full summary
# - 'help' - Show this help
# - 'exit' - Exit the program
# """)
#                     continue
                
#                 if user_input.lower() == 'compare':
#                     if self.comparison_result:
#                         print(self.comparison_result.summary)
#                     continue
                
#                 if user_input.lower() == 'discrepancies':
#                     if self.comparison_result:
#                         for d in self.comparison_result.discrepancies[:5]:
#                             print(f"- {d.description}: {d.status}")
#                     continue
                
#                 if user_input.lower() == 'summary':
#                     self.print_pipeline_summary()
#                     continue
                
#                 response = self.chat(user_input)
#                 print(f"\nAssistant: {response['response']}\n")
                
#             except KeyboardInterrupt:
#                 print("\n\nInterrupted.")
#                 break
#             except Exception as e:
#                 print(f"Error: {str(e)}")


# def main():
#     orchestrator = PDFAnalysisOrchestrator()
    
#     summary = orchestrator.run_complete_pipeline()
#     orchestrator.print_pipeline_summary()
    
#     return orchestrator


# if __name__ == "__main__":
#     main()
from pathlib import Path
from typing import Dict
import json

from src.config import settings
from src.pdf_extractor import extract_all_pdfs, ExtractedDocument
from src.comparator import compare_po_with_invoice
from src.report_generator import generate_all_reports

try:
    from src.rag_system import initialize_rag_system
except Exception as e:
    from src.rag_system_simple import initialize_rag_system

try:
    from src.chatbot import initialize_chatbot
except Exception:
    from src.chatbot_simple import initialize_simple_chatbot as initialize_chatbot

class PDFAnalysisOrchestrator:
    def __init__(self):
        self.data_dir = settings.DATA_DIR
        self.reports_dir = settings.REPORTS_DIR
        self.reports_dir.mkdir(parents=True, exist_ok=True)

        self.extracted_documents = {}
        self.po_doc = None
        self.invoice_doc = None
        self.comparison_result = None

        self.rag_system = None
        self.analysis_agent = None
        self.chatbot = None

    def run_complete_pipeline(self) -> Dict:
        print("\n" + "="*60)
        print("PDF ANALYSIS PIPELINE - COMPLETE WORKFLOW")
        print("="*60 + "\n")

        print("[STEP 1/6] Extracting PDF documents...")
        self.extract_documents()

        print("[STEP 2/6] Comparing PO with Invoice...")
        self.compare_documents()

        print("[STEP 3/6] Generating reports...")
        self.generate_reports()

        print("[STEP 4/6] Initializing RAG system...")
        self.initialize_rag()

        print("[STEP 5/6] Setting up analysis agent...")
        self.setup_agent()

        print("[STEP 6/6] Initializing chatbot...")
        self.setup_chatbot()

        return self.get_pipeline_summary()

    def extract_documents(self) -> Dict[str, ExtractedDocument]:
        self.extracted_documents = extract_all_pdfs(self.data_dir)

        for name, doc in self.extracted_documents.items():
            print(f"  [OK] Extracted {name}")
            print(f"    - Type: {doc.metadata.doc_type}")
            print(f"    - Items: {len(doc.items)}")
            print(f"    - Total: ${doc.total:.2f}")

            # Diagnostic warning
            if len(doc.items) == 0:
                print(f"    ⚠️  WARNING: No line items extracted from {name}!")

        return self.extracted_documents

    def compare_documents(self):
        self.po_doc = None
        self.invoice_doc = None

        for name, doc in self.extracted_documents.items():
            if 'PURCHASE_ORDER' in doc.metadata.doc_type:
                self.po_doc = doc
            elif 'PROFORMA_INVOICE' in doc.metadata.doc_type:
                self.invoice_doc = doc

        if self.po_doc and self.invoice_doc:
            self.comparison_result = compare_po_with_invoice(self.po_doc, self.invoice_doc)

            # ✅ FIXED: Use correct field names from DocumentComparison dataclass
            print(f"  [OK] Comparison completed")
            print(f"    - Items compared: {len(self.comparison_result.item_level_comparison)}")
            print(f"    - Matching items: {self.comparison_result.matching_items}")
            print(f"    - Discrepant items: {self.comparison_result.discrepant_items}")
            print(f"    - Total difference: ${self.comparison_result.summary_metrics.grand_total_difference:.2f}")

            # Show some key discrepancies
            if self.comparison_result.discrepant_items > 0:
                print(f"\n  ⚠️  Found {self.comparison_result.discrepant_items} discrepancies:")
                count = 0
                for item in self.comparison_result.item_level_comparison:
                    if item.severity in ['CRITICAL', 'HIGH'] and count < 3:
                        print(f"    - {item.item_no}: {item.reason}")
                        count += 1
        else:
            print("  [ERR] Could not find both PO and Invoice documents")

    def generate_reports(self) -> Dict[str, str]:
        if not self.comparison_result:
            print("  [ERR] No comparison result to report")
            return {}

        report_paths = generate_all_reports(
            self.comparison_result, 
            self.reports_dir, 
            self.po_doc, 
            self.invoice_doc
        )

        for format_type, path in report_paths.items():
            print(f"  [OK] Generated {format_type.upper()} report: {Path(path).name}")

        return report_paths

    def initialize_rag(self):
        self.rag_system = initialize_rag_system(settings.CHROMA_DB_PATH)
        print(f"  [OK] RAG system initialized at {settings.CHROMA_DB_PATH}")

        for name, doc in self.extracted_documents.items():
            self.rag_system.add_document(doc, name)

        print(f"  [OK] Added {len(self.extracted_documents)} documents to RAG system")

    def setup_agent(self):
        if not self.rag_system:
            print("  [ERR] RAG system not initialized")
            return

        try:
            from src.agent_rag import create_analysis_agent as create_agent
            self.analysis_agent = create_agent(self.rag_system)
            print("  [OK] Analysis agent ready")
        except Exception as e:
            print(f"  [WARN] Analysis agent setup skipped: {e}")

    def setup_chatbot(self):
        if not self.rag_system:
            print("  [ERR] RAG system not initialized")
            return

        try:
            self.chatbot = initialize_chatbot(self.rag_system)
            print("  [OK] Chatbot initialized and ready")
        except Exception as e:
            print(f"  [WARN] Using simplified chatbot: {e}")
            try:
                from src.chatbot_simple import initialize_simple_chatbot
                self.chatbot = initialize_simple_chatbot(self.rag_system)
                print("  [OK] Simplified chatbot initialized")
            except Exception as e2:
                print(f"  [ERR] Chatbot initialization failed: {e2}")

    def analyze_with_agent(self, query: str) -> Dict:
        if not self.analysis_agent:
            return {'error': 'Agent not initialized'}
        return self.analysis_agent.analyze_query(query)

    def chat(self, user_query: str) -> Dict:
        if not self.chatbot:
            return {'error': 'Chatbot not initialized'}
        return self.chatbot.chat(user_query)

    def get_pipeline_summary(self) -> Dict:
        # ✅ FIXED: Use correct field name
        discrepancies = self.comparison_result.discrepant_items if self.comparison_result else 0

        return {
            'status': 'complete',
            'documents_extracted': len(self.extracted_documents),
            'items_compared': len(self.comparison_result.item_level_comparison) if self.comparison_result else 0,
            'matching_items': self.comparison_result.matching_items if self.comparison_result else 0,
            'discrepant_items': discrepancies,
            'total_variance': self.comparison_result.summary_metrics.grand_total_difference if self.comparison_result else 0,
            'reports_generated': 3,  # JSON, CSV, Excel
            'rag_ready': self.rag_system is not None,
            'agent_ready': self.analysis_agent is not None,
            'chatbot_ready': self.chatbot is not None,
            'reports_directory': str(self.reports_dir),
            'rag_db_path': str(settings.CHROMA_DB_PATH)
        }

    def print_pipeline_summary(self):
        summary = self.get_pipeline_summary()
        print("\n" + "="*60)
        print("PIPELINE SUMMARY")
        print("="*60)
        print(f"Status: {summary['status']}")
        print(f"Documents Extracted: {summary['documents_extracted']}")
        print(f"Items Compared: {summary['items_compared']}")
        print(f"  - Matching: {summary['matching_items']}")
        print(f"  - Discrepant: {summary['discrepant_items']}")
        print(f"Total Variance: ${summary['total_variance']:.2f}")
        print(f"Reports Generated: {summary['reports_generated']}")
        print(f"RAG System: {'✓' if summary['rag_ready'] else '✗'}")
        print(f"Analysis Agent: {'✓' if summary['agent_ready'] else '✗'}")
        print(f"Chatbot: {'✓' if summary['chatbot_ready'] else '✗'}")
        print(f"Reports Directory: {summary['reports_directory']}")
        print("="*60 + "\n")

    def interactive_analysis(self):
        print("\n" + "="*60)
        print("INTERACTIVE ANALYSIS MODE")
        print("="*60)
        print("Type 'help' for commands, 'exit' to quit\n")

        while True:
            try:
                user_input = input("Query> ").strip()

                if not user_input:
                    continue

                if user_input.lower() == 'exit':
                    print("Exiting...")
                    break

                if user_input.lower() == 'help':
                    print("""
COMMANDS:
  - Any natural language question about the documents
  - 'compare' - Show comparison details
  - 'discrepancies' - List all discrepancies
  - 'summary' - Show full summary
  - 'help' - Show this help
  - 'exit' - Exit the program
""")
                    continue

                if user_input.lower() == 'compare':
                    if self.comparison_result:
                        print(f"\nComparison Results:")
                        print(f"  Items compared: {len(self.comparison_result.item_level_comparison)}")
                        print(f"  Matching: {self.comparison_result.matching_items}")
                        print(f"  Discrepant: {self.comparison_result.discrepant_items}")
                    continue

                if user_input.lower() == 'discrepancies':
                    if self.comparison_result:
                        print(f"\nDiscrepancies ({self.comparison_result.discrepant_items}):")
                        for item in self.comparison_result.item_level_comparison[:10]:
                            if item.severity != 'NONE':
                                print(f"  [{item.severity}] {item.item_no} - {item.description}")
                                print(f"    {item.reason}")
                    continue

                if user_input.lower() == 'summary':
                    self.print_pipeline_summary()
                    continue

                response = self.chat(user_input)
                print(f"\nAssistant: {response.get('response', 'Error processing query')}\n")

            except KeyboardInterrupt:
                print("\n\nInterrupted.")
                break
            except Exception as e:
                print(f"Error: {str(e)}")

def main():
    orchestrator = PDFAnalysisOrchestrator()
    summary = orchestrator.run_complete_pipeline()
    orchestrator.print_pipeline_summary()

    # Optional: Start interactive mode
    # orchestrator.interactive_analysis()

    return orchestrator

if __name__ == "__main__":
    main()
