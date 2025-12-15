# """
# PDF RAG Assistant App - Entry point for Streamlit Cloud deployment
# This app wraps the PDF RAG functionality from pdf_rag_analysis/
# """

# import os
# import sys
# import streamlit as st
# from pathlib import Path
# import tempfile
# import json

# # ✅ FIX PYTHON PATH FOR STREAMLIT
# ROOT_DIR = os.path.abspath(os.path.dirname(__file__))
# if ROOT_DIR not in sys.path:
#     sys.path.insert(0, ROOT_DIR)

# from dotenv import load_dotenv

# try:
#     from pdf_rag_analysis.src.advanced_rag import AdvancedRAGSystem
#     from pdf_rag_analysis.src.pdf_extractor import PDFExtractor
#     from pdf_rag_analysis.src.config import settings
# except ImportError:
#     from src.advanced_rag import AdvancedRAGSystem
#     from src.pdf_extractor import PDFExtractor
#     from src.config import settings

# # Load environment variables
# load_dotenv()

# # ============================================================
# # PAGE CONFIGURATION
# # ============================================================
# st.set_page_config(
#     page_title="PDF RAG Assistant",
#     page_icon="📄",
#     layout="wide",
#     initial_sidebar_state="expanded"
# )

# st.title("📄 PDF RAG Assistant")
# st.caption("Advanced PDF Analysis using RAG (Retrieval Augmented Generation)")

# # ============================================================
# # SESSION STATE INITIALIZATION
# # ============================================================
# def initialize_session():
#     """Initialize session state variables"""
#     if 'rag_system' not in st.session_state:
#         st.session_state.rag_system = AdvancedRAGSystem()
#     if 'uploaded_documents' not in st.session_state:
#         st.session_state.uploaded_documents = {}
#     if 'messages' not in st.session_state:
#         st.session_state.messages = []
#     if 'pdf_content' not in st.session_state:
#         st.session_state.pdf_content = {}

# initialize_session()

# # ============================================================
# # SIDEBAR CONFIGURATION
# # ============================================================
# with st.sidebar:
#     st.header("⚙️ Configuration")
    
#     # Upload PDF files
#     st.subheader("📁 Upload PDFs")
#     uploaded_files = st.file_uploader(
#         "Upload PDF files",
#         type=["pdf"],
#         accept_multiple_files=True,
#         help="Upload one or more PDF files for analysis"
#     )
    
#     # Process uploaded files
#     if uploaded_files:
#         st.write(f"✅ {len(uploaded_files)} file(s) uploaded")
        
#         if st.button("🔄 Process PDFs", key="process_pdfs"):
#             with st.spinner("Processing PDFs..."):
#                 try:
#                     for uploaded_file in uploaded_files:
#                         # Read file content
#                         with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
#                             tmp_file.write(uploaded_file.read())
#                             tmp_path = tmp_file.name
                        
#                         # Extract content
#                         extractor = PDFExtractor()
#                         pdf_data = extractor.extract_from_file(tmp_path)
                        
#                         # Store in session
#                         st.session_state.pdf_content[uploaded_file.name] = pdf_data
                        
#                         # Clean up
#                         os.unlink(tmp_path)
                    
#                     st.success(f"✅ Processed {len(uploaded_files)} PDF(s)")
#                 except Exception as e:
#                     st.error(f"❌ Error processing PDFs: {str(e)}")
    
#     # Display processed files
#     if st.session_state.pdf_content:
#         st.subheader("📚 Processed Documents")
#         for doc_name in st.session_state.pdf_content.keys():
#             st.write(f"✅ {doc_name}")
    
#     # Clear session button
#     if st.button("🗑️ Clear All", key="clear_all"):
#         st.session_state.pdf_content = {}
#         st.session_state.messages = []
#         st.rerun()

# # ============================================================
# # MAIN CONTENT AREA
# # ============================================================
# if not st.session_state.pdf_content:
#     st.info("📌 Please upload PDF files using the sidebar to get started.")
#     st.write("""
#     ### Features:
#     - 📄 Extract text from PDF documents
#     - 🔍 Search and query document content
#     - 💬 Chat with your documents
#     - 📊 Generate analysis reports
#     - 🔗 Compare multiple documents
#     """)
# else:
#     # Chat interface
#     st.subheader("💬 Chat with Your Documents")
    
#     # Display chat history
#     for message in st.session_state.messages:
#         with st.chat_message(message["role"]):
#             st.write(message["content"])
    
#     # Chat input
#     user_query = st.chat_input("Ask a question about your documents...")
    
#     if user_query:
#         # Add user message to history
#         st.session_state.messages.append({
#             "role": "user",
#             "content": user_query
#         })
        
#         # Display user message
#         with st.chat_message("user"):
#             st.write(user_query)
        
#         # Generate response
#         with st.chat_message("assistant"):
#             with st.spinner("Thinking..."):
#                 try:
#                     # Query RAG system
#                     rag_system = st.session_state.rag_system
                    
#                     # Add documents to RAG if not already added
#                     for doc_name, content in st.session_state.pdf_content.items():
#                         rag_system.add_document(
#                             doc_id=doc_name.replace(".pdf", ""),
#                             content=content.get("text", ""),
#                             metadata={"source": doc_name}
#                         )
                    
#                     # Get response
#                     response = rag_system.query(user_query)
                    
#                     st.write(response)
                    
#                     # Add assistant message to history
#                     st.session_state.messages.append({
#                         "role": "assistant",
#                         "content": response
#                     })
                
#                 except Exception as e:
#                     st.error(f"❌ Error: {str(e)}")

# # ============================================================
"""
PDF RAG Assistant App - Entry point for Streamlit Cloud deployment
This app wraps the PDF RAG functionality from pdf_rag_analysis/
"""

import os
import sys
import streamlit as st
from pathlib import Path
import tempfile
import json

# ✅ FIX PYTHON PATH FOR STREAMLIT
ROOT_DIR = os.path.abspath(os.path.dirname(__file__))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)
    # ensure repo src folders are also available for imports
    extra_paths = [
        os.path.join(ROOT_DIR, "src"),
        os.path.join(ROOT_DIR, "pdf_rag_analysis", "src"),
    ]
    for p in extra_paths:
        if os.path.isdir(p) and p not in sys.path:
            sys.path.insert(0, p)

# Ensure extra src paths are present even if ROOT_DIR was already in sys.path
extra_paths = [
    os.path.join(ROOT_DIR, "src"),
    os.path.join(ROOT_DIR, "pdf_rag_analysis", "src"),
]
for p in extra_paths:
    if os.path.isdir(p) and p not in sys.path:
        sys.path.insert(0, p)

from dotenv import load_dotenv
import importlib.util


def _load_by_paths(name, paths):
    for fp in paths:
        if os.path.isfile(fp):
            spec = importlib.util.spec_from_file_location(name, fp)
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            return mod
    raise ModuleNotFoundError(name)


# Try package-style imports first, then fallback to loading from known file locations
try:
    from pdf_rag_analysis.src.advanced_rag import AdvancedRAGSystem
    from pdf_rag_analysis.src.pdf_extractor import PDFExtractor
    from pdf_rag_analysis.src.config import settings
except Exception:
    try:
        from src.advanced_rag import AdvancedRAGSystem
        from src.pdf_extractor import PDFExtractor
        from src.config import settings
    except Exception:
        adv = _load_by_paths("advanced_rag", [
            os.path.join(ROOT_DIR, "pdf_rag_analysis", "src", "advanced_rag.py"),
            os.path.join(ROOT_DIR, "src", "advanced_rag.py"),
        ])
        AdvancedRAGSystem = getattr(adv, "AdvancedRAGSystem")

        pdfmod = _load_by_paths("pdf_extractor", [
            os.path.join(ROOT_DIR, "pdf_rag_analysis", "src", "pdf_extractor.py"),
            os.path.join(ROOT_DIR, "src", "pdf_extractor.py"),
        ])
        PDFExtractor = getattr(pdfmod, "PDFExtractor")

        cfg = _load_by_paths("config", [
            os.path.join(ROOT_DIR, "pdf_rag_analysis", "src", "config.py"),
            os.path.join(ROOT_DIR, "src", "config.py"),
        ])
        settings = getattr(cfg, "settings")

# Load environment variables
load_dotenv()

# ============================================================
# PAGE CONFIGURATION
# ============================================================
st.set_page_config(
    page_title="PDF RAG Assistant",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("📄 PDF RAG Assistant")
st.caption("Advanced PDF Analysis using RAG (Retrieval Augmented Generation)")

# ============================================================
# SESSION STATE INITIALIZATION
# ============================================================
def initialize_session():
    """Initialize session state variables"""
    if 'rag_system' not in st.session_state:
        st.session_state.rag_system = AdvancedRAGSystem()
    if 'uploaded_documents' not in st.session_state:
        st.session_state.uploaded_documents = {}
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    if 'pdf_content' not in st.session_state:
        st.session_state.pdf_content = {}

initialize_session()

# ============================================================
# SIDEBAR CONFIGURATION
# ============================================================
with st.sidebar:
    st.header("⚙️ Configuration")
    
    # Upload PDF files
    st.subheader("📁 Upload PDFs")
    uploaded_files = st.file_uploader(
        "Upload PDF files",
        type=["pdf"],
        accept_multiple_files=True,
        help="Upload one or more PDF files for analysis"
    )
    
    # Process uploaded files
    if uploaded_files:
        st.write(f"✅ {len(uploaded_files)} file(s) uploaded")
        
        if st.button("🔄 Process PDFs", key="process_pdfs"):
            with st.spinner("Processing PDFs..."):
                try:
                    for uploaded_file in uploaded_files:
                        # Read file content
                        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
                            tmp_file.write(uploaded_file.read())
                            tmp_path = tmp_file.name
                        
                        # Extract content
                        extractor = PDFExtractor()
                        pdf_data = extractor.extract_from_file(tmp_path)
                        
                        # Store in session
                        st.session_state.pdf_content[uploaded_file.name] = pdf_data
                        
                        # Clean up
                        os.unlink(tmp_path)
                    
                    st.success(f"✅ Processed {len(uploaded_files)} PDF(s)")
                except Exception as e:
                    st.error(f"❌ Error processing PDFs: {str(e)}")
    
    # Display processed files
    if st.session_state.pdf_content:
        st.subheader("📚 Processed Documents")
        for doc_name in st.session_state.pdf_content.keys():
            st.write(f"✅ {doc_name}")
    
    # Clear session button
    if st.button("🗑️ Clear All", key="clear_all"):
        st.session_state.pdf_content = {}
        st.session_state.messages = []
        st.rerun()

# ============================================================
# MAIN CONTENT AREA
# ============================================================
if not st.session_state.pdf_content:
    st.info("📌 Please upload PDF files using the sidebar to get started.")
    st.write("""
    ### Features:
    - 📄 Extract text from PDF documents
    - 🔍 Search and query document content
    - 💬 Chat with your documents
    - 📊 Generate analysis reports
    - 🔗 Compare multiple documents
    """)
else:
    # Chat interface
    st.subheader("💬 Chat with Your Documents")
    
    # Display chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])
    
    # Chat input
    user_query = st.chat_input("Ask a question about your documents...")
    
    if user_query:
        # Add user message to history
        st.session_state.messages.append({
            "role": "user",
            "content": user_query
        })
        
        # Display user message
        with st.chat_message("user"):
            st.write(user_query)
        
        # Generate response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                try:
                    # Query RAG system
                    rag_system = st.session_state.rag_system
                    
                    # Add documents to RAG if not already added
                    for doc_name, content in st.session_state.pdf_content.items():
                        rag_system.add_document(
                            doc_id=doc_name.replace(".pdf", ""),
                            content=content.get("text", ""),
                            metadata={"source": doc_name}
                        )
                    
                    # Get response
                    response = rag_system.query(user_query)
                    
                    st.write(response)
                    
                    # Add assistant message to history
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": response
                    })
                
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")

# ============================================================
# FOOTER
# ============================================================
st.divider()
st.caption("🤖 Powered by RAG (Retrieval Augmented Generation) • Built with Streamlit")

# # FOOTER
# # ============================================================
# st.divider()
# st.caption("🤖 Powered by RAG (Retrieval Augmented Generation) • Built with Streamlit")
