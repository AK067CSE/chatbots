#!/usr/bin/env python
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from src.pdf_extractor import extract_all_pdfs
from src.comparator import DocumentComparator
from src.config import settings

def main():
    print("\n" + "="*60)
    print("BASIC RAG SYSTEM TEST")
    print("="*60 + "\n")
    
    data_dir = settings.DATA_DIR
    print("[1/3] Extracting PDFs...")
    
    documents = extract_all_pdfs(data_dir)
    
    if not documents:
        print("[ERR] No documents found!")
        return
    
    for name, doc in documents.items():
        print(f"  [OK] {name}")
        print(f"    - Type: {doc.metadata.doc_type}")
        print(f"    - Items: {len(doc.items)}")
        print(f"    - Total: ${doc.total:,.2f}")
        print(f"    - Raw text length: {len(doc.raw_text)} chars")
    
    print("\n[2/3] Testing PDF Extraction...")
    po_doc = None
    invoice_doc = None
    
    for name, doc in documents.items():
        if 'PURCHASE_ORDER' in doc.metadata.doc_type:
            po_doc = doc
            print(f"  [OK] Found PO: {doc.metadata.document_id}")
        elif 'INVOICE' in doc.metadata.doc_type:
            invoice_doc = doc
            print(f"  [OK] Found Invoice: {doc.metadata.document_id}")
    
    if po_doc and invoice_doc:
        print("\n[3/3] Comparing documents...")
        comparator = DocumentComparator()
        comparison = comparator.compare(po_doc, invoice_doc)
        print(f"  [OK] Comparison complete")
        print(f"    - PO Total: ${comparison.po_total:,.2f}")
        print(f"    - Invoice Total: ${comparison.invoice_total:,.2f}")
        print(f"    - Variance: ${comparison.grand_total_diff:,.2f} ({comparison.grand_total_variance_pct:.2f}%)")
        print(f"    - Discrepancies: {len(comparison.discrepancies)}")
    else:
        print("[WARN] Could not find both PO and Invoice")
    
    print("\n" + "="*60)
    print("BASIC TEST COMPLETED")
    print("="*60 + "\n")

if __name__ == "__main__":
    main()
