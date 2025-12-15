#!/usr/bin/env python3
import shutil
from pathlib import Path

source_dir = Path("c:/Users/abhik/Downloads/sales/salesbot/data")
target_dir = Path("c:/Users/abhik/Downloads/sales/salesbot/pdf_rag_analysis/data")

pdf_files = [
    "Purchase_Order_2025-12-12.pdf",
    "Proforma_Invoice_2025-12-12.pdf"
]

target_dir.mkdir(parents=True, exist_ok=True)

for pdf_file in pdf_files:
    source = source_dir / pdf_file
    target = target_dir / pdf_file
    
    if source.exists():
        shutil.copy2(source, target)
        print(f"[OK] Copied {pdf_file}")
    else:
        print(f"[ERR] Not found: {pdf_file}")

print("\nDone! PDFs are ready in the data directory.")
