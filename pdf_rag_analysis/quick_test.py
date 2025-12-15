#!/usr/bin/env python
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from src.pdf_extractor import PDFExtractor
from src.config import settings

def main():
    print("[TEST] Quick PDF Extraction")
    
    pdf_dir = settings.DATA_DIR
    pdf_files = list(pdf_dir.glob("*.pdf"))
    
    if not pdf_files:
        print("[ERR] No PDFs found")
        return
    
    extractor = PDFExtractor()
    
    for pdf_file in pdf_files[:1]:
        print(f"\n[EXTRACT] {pdf_file.name}")
        doc = extractor.extract_pdf(pdf_file)
        print(f"  - Type: {doc.metadata.doc_type}")
        print(f"  - Doc ID: {doc.metadata.document_id}")
        print(f"  - Items: {len(doc.items)}")
        print(f"  - Total: ${doc.total:,.2f}")
        print(f"  - Text length: {len(doc.raw_text)}")

if __name__ == "__main__":
    main()
