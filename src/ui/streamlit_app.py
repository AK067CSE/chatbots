import os
import streamlit as st
import pandas as pd
import sys
import os

# ✅ FIX PYTHON PATH FOR STREAMLIT
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)


from dotenv import load_dotenv

from src.data.excel_loader import ExcelDataLoader
from src.db.duckdb_client import DuckDBClient
from src.agents.sql_rag_router import SQLRAGRouter


# ------------------------------------------------------------
# APP CONFIG
# ------------------------------------------------------------
load_dotenv()

st.set_page_config(
    page_title="AI Sales & Active Store Assistant",
    layout="wide"
)

st.title("📊 AI Sales & Active Store Dashboard")
st.caption("Agentic BI Assistant: DuckDB SQL + RAG + Hybrid Reasoning + Charts")


# ------------------------------------------------------------
# HELPERS
# ------------------------------------------------------------
def _safe_str(x) -> str:
    try:
        return "" if x is None else str(x)
    except Exception:
        return ""


@st.cache_data(show_spinner=False)
def load_excel_to_duckdb(uploaded_file) -> dict:
    """
    1) Parse Excel (.xlsb/.xlsx) using ExcelDataLoader
    2) Load sales + active_store into DuckDB
    3) Return dataframes for optional UI use
    """
    # Streamlit UploadedFile is file-like; ExcelDataLoader expects a file path.
    # So we save it to a temp location.
    tmp_dir = "tmp_uploads"
    os.makedirs(tmp_dir, exist_ok=True)
    tmp_path = os.path.join(tmp_dir, uploaded_file.name)

    with open(tmp_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    loader = ExcelDataLoader(tmp_path)
    data = loader.load_all()

    sales_df = data["sales"]
    active_df = data["active_store"]
    headers_df = data.get("headers")

    # Load into DuckDB
    db = DuckDBClient()
    db.load_dataframe("sales", sales_df)
    db.load_dataframe("active_store", active_df)

    return {
        "tmp_path": tmp_path,
        "sales_df": sales_df,
        "active_df": active_df,
        "headers_df": headers_df
    }


def render_output(output: dict):
    """
    Renders router output for engines:
      - SQL
      - RAG
      - HYBRID
    """
    engine = output.get("engine", "UNKNOWN")
    st.subheader(f"🧭 Engine Used: {engine}")

    # SQL / HYBRID typically return sql + df
    if engine in ["SQL", "HYBRID"]:
        sql = output.get("sql", "")
        df = output.get("data", None)

        # Top panels
        top_left, top_right = st.columns([2, 1])

        with top_left:
            st.markdown("### 🧾 Generated SQL")
            st.code(_safe_str(sql), language="sql")

        with top_right:
            # Chart (optional)
            chart = output.get("chart", None)
            if chart is not None:
                st.markdown("### 📈 Chart")
                st.plotly_chart(chart, use_container_width=True)
            else:
                st.markdown("### 📈 Chart")
                st.info("No chart returned (yet). Ask for a chart like: 'show chart of sales by month'.")

        # Data table
        st.markdown("### 📋 Data")
        if df is None:
            st.warning("No dataframe returned.")
        else:
            st.dataframe(df, use_container_width=True)

        # Explanation / analysis
        if engine == "SQL":
            st.markdown("### 🧠 Explanation")
            st.write(_safe_str(output.get("explanation", "")))

        if engine == "HYBRID":
            st.markdown("### 🧩 Business Analysis")
            st.write(_safe_str(output.get("analysis", "")))

        return

    # RAG
    if engine == "RAG":
        st.markdown("### 📘 Knowledge Answer")
        st.write(_safe_str(output.get("answer", "")))
        return

    # Unknown
    st.warning("Unsupported engine output format.")
    st.json(output)


# ------------------------------------------------------------
# SIDEBAR: UPLOAD + INFO
# ------------------------------------------------------------
with st.sidebar:
    st.header("⚙️ Controls")

    uploaded_file = st.file_uploader(
        "Upload Excel (.xlsb / .xlsx)",
        type=["xlsb", "xlsx"]
    )

    st.markdown("---")
    st.markdown("### ✅ Example Questions")
    st.markdown("""
- Total sales for Delmond in JAN 2024  
- Compare Delmond sales between 2024 and 2025  
- Top 5 brands by sales in 2025  
- Active stores count in 2024 vs 2025  
- What is 'Line of Business'?  
- How can I improve sales for Neo brand?  
- Show chart of monthly sales for 2024  
""")

    show_debug = st.toggle("Show Debug (data preview)", value=False)


if not uploaded_file:
    st.info("Upload your Excel file from the sidebar to start.")
    st.stop()


# ------------------------------------------------------------
# LOAD DATA + INIT ROUTER
# ------------------------------------------------------------
with st.spinner("Loading Excel → cleaning → indexing → DuckDB..."):
    data = load_excel_to_duckdb(uploaded_file)

router = SQLRAGRouter()


# ------------------------------------------------------------
# OPTIONAL: DEBUG PREVIEW
# ------------------------------------------------------------
if show_debug:
    st.markdown("## 🧪 Debug Preview")

    c1, c2 = st.columns(2)

    with c1:
        st.markdown("### Sales (head)")
        st.dataframe(data["sales_df"].head(10), use_container_width=True)

    with c2:
        st.markdown("### Active Store (head)")
        st.dataframe(data["active_df"].head(10), use_container_width=True)

    if data.get("headers_df") is not None:
        st.markdown("### Headers Dictionary (head)")
        st.dataframe(data["headers_df"].head(10), use_container_width=True)


# ------------------------------------------------------------
# CHAT SECTION
# ------------------------------------------------------------
st.markdown("## 💬 Chat with your Excel")

# Maintain chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Show chat history
for m in st.session_state.messages:
    role = m.get("role", "assistant")
    content = m.get("content", "")
    with st.chat_message(role):
        st.markdown(content)

# New user input
user_question = st.chat_input("Ask a business question… (sales, YoY, top products, active stores, explain columns, strategy)")

if user_question:
    # Append user message
    st.session_state.messages.append({"role": "user", "content": user_question})
    with st.chat_message("user"):
        st.markdown(user_question)

    # Process
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                output = router.route(user_question)

                # Build a compact chat response (and also render full output below)
                engine = output.get("engine", "")
                if engine == "RAG":
                    chat_text = output.get("answer", "")
                elif engine == "SQL":
                    chat_text = output.get("explanation", "")
                elif engine == "HYBRID":
                    chat_text = output.get("analysis", "")
                else:
                    chat_text = f"Output: {output}"

                st.markdown(chat_text if chat_text else "Done. See details below ⬇️")

                st.session_state.messages.append({"role": "assistant", "content": chat_text if chat_text else "Done. See details below ⬇️"})

            except Exception as e:
                err = f"❌ Error: {e}"
                st.error(err)
                st.session_state.messages.append({"role": "assistant", "content": err})


# ------------------------------------------------------------
# FULL RESULT PANEL (LATEST)
# ------------------------------------------------------------
st.markdown("---")
st.markdown("## 🧾 Detailed Result Panel")

if st.session_state.messages and st.session_state.messages[-1]["role"] == "assistant":
    # Re-run latest query only if user asked something in this run
    # We'll store last output in session for stable rendering
    if "last_output" not in st.session_state:
        st.session_state.last_output = None

# If user_question exists, update last_output
if user_question:
    try:
        st.session_state.last_output = router.route(user_question)
    except Exception:
        st.session_state.last_output = None

if st.session_state.get("last_output") is None:
    st.info("Ask a question above to see full SQL + table + chart here.")
else:
    render_output(st.session_state.last_output)
