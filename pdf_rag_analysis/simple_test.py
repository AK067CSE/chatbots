#!/usr/bin/env python
print("[1] Starting test...")

from pathlib import Path
print("[2] Imported Path")

import pypdf
print("[3] Imported pypdf")

pdf_path = Path("c:\\Users\\abhik\\Downloads\\sales\\salesbot\\pdf_rag_analysis\\data\\Purchase_Order_2025-12-12.pdf")
print(f"[4] PDF path: {pdf_path}")

reader = pypdf.PdfReader(str(pdf_path))
print(f"[5] Pages: {len(reader.pages)}")

text = ""
for page in reader.pages:
    text += page.extract_text()
print(f"[6] Text length: {len(text)}")

print("[DONE]")
