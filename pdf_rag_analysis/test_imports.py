#!/usr/bin/env python
import sys

try:
    import pdfplumber
    print("[OK] pdfplumber")
except ImportError as e:
    print(f"[ERR] pdfplumber: {e}")

try:
    import rank_bm25
    print("[OK] rank_bm25")
except ImportError as e:
    print(f"[ERR] rank_bm25: {e}")

try:
    import streamlit
    print("[OK] streamlit")
except ImportError as e:
    print(f"[ERR] streamlit: {e}")

try:
    import chromadb
    print("[OK] chromadb")
except ImportError as e:
    print(f"[ERR] chromadb: {e}")

try:
    import langchain
    print("[OK] langchain")
except ImportError as e:
    print(f"[ERR] langchain: {e}")

print("\nAll imports successful!")
