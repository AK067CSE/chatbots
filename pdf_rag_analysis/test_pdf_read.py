#!/usr/bin/env python
import sys
from pathlib import Path

data_dir = Path("c:\\Users\\abhik\\Downloads\\sales\\salesbot\\pdf_rag_analysis\\data")
pdf_files = list(data_dir.glob("*.pdf"))

print(f"Found {len(pdf_files)} PDF files:")
for pdf in pdf_files:
    print(f"  - {pdf.name} ({pdf.stat().st_size} bytes)")

if pdf_files:
    print("\nTrying to read first PDF...")
    import pypdf
    
    pdf_path = pdf_files[0]
    print(f"Reading {pdf_path.name}...")
    
    reader = pypdf.PdfReader(str(pdf_path))
    print(f"  - Pages: {len(reader.pages)}")
    
    print(f"Extracting text from first page...")
    text = reader.pages[0].extract_text()
    print(f"  - Text length: {len(text)}")
    print(f"  - Preview: {text[:200]}")
