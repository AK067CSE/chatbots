#!/usr/bin/env python
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from src.pdf_extractor import extract_all_pdfs
from src.comparator import compare_po_with_invoice
from src.advanced_rag import AdvancedRAGSystem
from src.config import settings

def main():
    print("\n" + "="*60)
    print("ADVANCED RAG SYSTEM TEST")
    print("="*60 + "\n")
    
    data_dir = settings.DATA_DIR
    print(f"[1/5] Extracting PDFs from {data_dir}...")
    
    documents = extract_all_pdfs(data_dir)
    
    for name, doc in documents.items():
        print(f"  [OK] {name}")
        print(f"    - Type: {doc.metadata.doc_type}")
        print(f"    - Items: {len(doc.items)}")
        print(f"    - Total: ${doc.total:.2f}")
    
    print("\n[2/5] Comparing documents...")
    po_doc = None
    invoice_doc = None
    
    for name, doc in documents.items():
        if 'PURCHASE_ORDER' in doc.metadata.doc_type:
            po_doc = doc
        elif 'INVOICE' in doc.metadata.doc_type:
            invoice_doc = doc
    
    if po_doc and invoice_doc:
        comparator = compare_po_with_invoice(po_doc, invoice_doc)
        print(f"  [OK] Comparison complete")
        print(f"    - Variance: ${comparator.grand_total_diff:.2f}")
    else:
        print("  [WARN] Could not find both PO and Invoice")
    
    print("\n[3/5] Initializing Advanced RAG System...")
    rag = AdvancedRAGSystem()
    print("  [OK] RAG System created")
    
    print("\n[4/5] Adding documents to RAG...")
    for idx, (name, doc) in enumerate(documents.items()):
        chunk_count = rag.add_document(doc, f"doc_{idx}")
        print(f"  [OK] Added {name} - {chunk_count} chunks")
    
    summary = rag.get_summary()
    print(f"\n  System Summary:")
    print(f"    - Documents: {summary['documents']}")
    print(f"    - Chunks: {summary['chunks']}")
    print(f"    - Methods: {', '.join(summary['retrieval_methods'])}")
    
    print("\n[5/5] Testing Hybrid Retrieval...")
    test_queries = [
        "What are the line items?",
        "What is the total price?",
        "Are there any discrepancies?",
        "What products are listed?"
    ]
    
    for query in test_queries:
        print(f"\n  Query: '{query}'")
        results = rag.retrieve(query, top_k=3, use_fusion=False)
        print(f"    - Found {len(results)} results (Hybrid)")
        for i, result in enumerate(results, 1):
            print(f"    [{i}] Score: {result['score']:.3f} | Type: {result['retrieval_method']}")
        
        fusion_results = rag.retrieve(query, top_k=3, use_fusion=True)
        print(f"    - Found {len(fusion_results)} results (RAG Fusion)")
        for i, result in enumerate(fusion_results, 1):
            print(f"    [{i}] Score: {result['score']:.3f} | Method: {result['retrieval_method']}")
    
    print("\n" + "="*60)
    print("TEST COMPLETED SUCCESSFULLY")
    print("="*60 + "\n")

if __name__ == "__main__":
    main()
