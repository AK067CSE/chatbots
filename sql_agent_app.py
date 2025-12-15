"""
SQL Agent App - Entry point for Streamlit Cloud deployment
This app wraps the existing SQL agent functionality from src/ui/streamlit_app.py
"""

import os
import sys
import streamlit as st

# ✅ FIX PYTHON PATH FOR STREAMLIT
ROOT_DIR = os.path.abspath(os.path.dirname(__file__))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

# Import the main streamlit app
# The existing streamlit_app.py contains all the SQL agent logic
import importlib.util

spec = importlib.util.spec_from_file_location(
    "streamlit_app",
    os.path.join(ROOT_DIR, "src/ui/streamlit_app.py")
)
streamlit_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(streamlit_module)
