#!/usr/bin/env python3
"""
Example usage patterns for the PDF Analysis System
"""

from pathlib import Path
from src.pdf_extractor import extract_all_pdfs
from src.comparator import compare_po_with_invoice
from src.report_generator import generate_all_reports
from src.rag_system import initialize_rag_system, RAGFusionRetriever
from src.agent_rag import create_analysis_agent, create_comparison_analyzer
from src.chatbot import initialize_chatbot
from src.orchestrator import PDFAnalysisOrchestrator


def example_basic_extraction():
    """Example 1: Basic PDF extraction"""
    print("\n" + "="*60)
    print("EXAMPLE 1: Basic PDF Extraction")
    print("="*60)
    
    documents = extract_all_pdfs(Path("data"))
    
    for name, doc in documents.items():
        print(f"\nDocument: {name}")
        print(f"  Type: {doc.metadata.doc_type}")
        print(f"  ID: {doc.metadata.document_id}")
        print(f"  Date: {doc.metadata.date}")
        print(f"  Items: {len(doc.items)}")
        print(f"  Total: ${doc.total:.2f}")
        
        print("\n  Line Items:")
        for item in doc.items[:3]:
            print(f"    - {item.description}: {item.quantity} x ${item.unit_price:.2f}")


def example_comparison():
    """Example 2: Document comparison"""
    print("\n" + "="*60)
    print("EXAMPLE 2: Document Comparison")
    print("="*60)
    
    documents = extract_all_pdfs(Path("data"))
    
    po_doc = None
    invoice_doc = None
    
    for name, doc in documents.items():
        if 'PURCHASE_ORDER' in doc.metadata.doc_type:
            po_doc = doc
        elif 'PROFORMA_INVOICE' in doc.metadata.doc_type:
            invoice_doc = doc
    
    if po_doc and invoice_doc:
        comparison = compare_po_with_invoice(po_doc, invoice_doc)
        
        print(f"\nComparison Results:")
        print(f"  PO ID: {comparison.po_doc_id}")
        print(f"  Invoice ID: {comparison.invoice_doc_id}")
        print(f"  Items in PO: {comparison.total_items_po}")
        print(f"  Items in Invoice: {comparison.total_items_invoice}")
        print(f"  Matching Items: {comparison.matching_items}")
        print(f"  Discrepancies: {comparison.discrepant_items}")
        print(f"\nFinancial Summary:")
        print(f"  PO Total: ${comparison.po_total:.2f}")
        print(f"  Invoice Total: ${comparison.invoice_total:.2f}")
        print(f"  Difference: ${comparison.grand_total_diff:.2f}")
        print(f"  Variance: {comparison.grand_total_variance_pct:.2f}%")
        
        print(f"\nTop Discrepancies:")
        for disc in comparison.discrepancies[:3]:
            print(f"  - {disc.description}")
            print(f"    Status: {disc.status}")
            print(f"    Qty Variance: {disc.quantity_variance_pct:.1f}%")
            print(f"    Price Variance: {disc.price_variance_pct:.1f}%")


def example_report_generation():
    """Example 3: Multi-format report generation"""
    print("\n" + "="*60)
    print("EXAMPLE 3: Multi-Format Report Generation")
    print("="*60)
    
    documents = extract_all_pdfs(Path("data"))
    
    po_doc = next((d for d in documents.values() if 'PURCHASE_ORDER' in d.metadata.doc_type), None)
    invoice_doc = next((d for d in documents.values() if 'PROFORMA_INVOICE' in d.metadata.doc_type), None)
    
    if po_doc and invoice_doc:
        comparison = compare_po_with_invoice(po_doc, invoice_doc)
        reports = generate_all_reports(comparison, Path("reports"))
        
        print("\nGenerated Reports:")
        for format_type, path in reports.items():
            print(f"  ✓ {format_type.upper()}: {Path(path).name}")


def example_rag_search():
    """Example 4: RAG system and semantic search"""
    print("\n" + "="*60)
    print("EXAMPLE 4: RAG Search with RAG Fusion")
    print("="*60)
    
    documents = extract_all_pdfs(Path("data"))
    
    rag = initialize_rag_system()
    
    for name, doc in documents.items():
        rag.add_document(doc, name)
    
    retriever = RAGFusionRetriever(rag)
    
    queries = [
        "What items have quantity mismatches?",
        "What are the price differences?",
        "Which items are missing from the invoice?"
    ]
    
    for query in queries:
        print(f"\nQuery: {query}")
        results = retriever.retrieve_with_fusion(query, n_results=3)
        
        for i, result in enumerate(results, 1):
            print(f"  [{i}] {result['document'][:150]}...")
            print(f"      Type: {result['metadata'].get('chunk_type')}")


def example_agent_analysis():
    """Example 5: Agentic RAG analysis"""
    print("\n" + "="*60)
    print("EXAMPLE 5: Agentic Analysis")
    print("="*60)
    
    documents = extract_all_pdfs(Path("data"))
    rag = initialize_rag_system()
    
    for name, doc in documents.items():
        rag.add_document(doc, name)
    
    agent = create_analysis_agent(rag)
    
    queries = [
        "What are the main discrepancies between PO and Invoice?",
        "Which items have the largest price differences?",
        "What is the total value difference?"
    ]
    
    for query in queries:
        print(f"\nQuery: {query}")
        result = agent.analyze_query(query)
        
        if result['success']:
            print(f"Response: {result['response'][:300]}...")
        else:
            print(f"Error: {result['error']}")


def example_chatbot_interaction():
    """Example 6: Chatbot interaction"""
    print("\n" + "="*60)
    print("EXAMPLE 6: Chatbot Interaction")
    print("="*60)
    
    documents = extract_all_pdfs(Path("data"))
    rag = initialize_rag_system()
    
    for name, doc in documents.items():
        rag.add_document(doc, name)
    
    chatbot = initialize_chatbot(rag)
    
    conversations = [
        ("What items are in the purchase order?", "Understand document contents"),
        ("What are the discrepancies?", "Identify mismatches"),
        ("Which items have price differences?", "Specific analysis"),
        ("What would you recommend?", "Get recommendations"),
    ]
    
    for user_input, context in conversations:
        print(f"\nUser: {user_input}")
        print(f"(Context: {context})")
        
        response = chatbot.chat(user_input)
        print(f"Assistant: {response['response'][:400]}...")


def example_complete_pipeline():
    """Example 7: Complete end-to-end pipeline"""
    print("\n" + "="*60)
    print("EXAMPLE 7: Complete Pipeline")
    print("="*60)
    
    orchestrator = PDFAnalysisOrchestrator()
    
    summary = orchestrator.run_complete_pipeline()
    
    print("\nPipeline Execution Summary:")
    for key, value in summary.items():
        print(f"  {key}: {value}")
    
    if orchestrator.chatbot:
        print("\n\nInteractive Chat Session:")
        test_queries = [
            "What is the total difference between PO and Invoice?",
            "Which items have mismatches?",
        ]
        
        for query in test_queries:
            response = orchestrator.chat(query)
            print(f"\nUser: {query}")
            print(f"Assistant: {response['response'][:300]}...\n")


def run_all_examples():
    """Run all examples in sequence"""
    print("\n" + "="*70)
    print("PDF ANALYSIS SYSTEM - COMPREHENSIVE EXAMPLES")
    print("="*70)
    
    try:
        example_basic_extraction()
        example_comparison()
        example_report_generation()
        example_rag_search()
        example_agent_analysis()
        example_chatbot_interaction()
        example_complete_pipeline()
        
        print("\n" + "="*70)
        print("ALL EXAMPLES COMPLETED SUCCESSFULLY")
        print("="*70 + "\n")
        
    except Exception as e:
        print(f"\n❌ Error running examples: {e}")
        print("Ensure PDFs are in the 'data' directory and all dependencies are installed")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        example_name = sys.argv[1]
        
        examples = {
            'extraction': example_basic_extraction,
            'comparison': example_comparison,
            'reports': example_report_generation,
            'rag': example_rag_search,
            'agent': example_agent_analysis,
            'chatbot': example_chatbot_interaction,
            'pipeline': example_complete_pipeline,
        }
        
        if example_name in examples:
            examples[example_name]()
        else:
            print(f"Unknown example: {example_name}")
            print(f"Available examples: {', '.join(examples.keys())}")
    else:
        run_all_examples()
