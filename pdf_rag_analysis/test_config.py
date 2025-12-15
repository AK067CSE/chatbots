#!/usr/bin/env python
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

print("[1] Starting...")

try:
    print("[2] Importing config...")
    from src.config import settings
    print("[3] Config imported")
    print(f"[4] DATA_DIR: {settings.DATA_DIR}")
except Exception as e:
    print(f"[ERR] Error: {e}")
    import traceback
    traceback.print_exc()
