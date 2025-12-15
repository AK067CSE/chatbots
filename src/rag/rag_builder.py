# from dotenv import load_dotenv

# # Load environment variables early for OpenAI API key
# load_dotenv()

# # # from src.data.data_loader import ExcelDataLoader
# # # from src.rag.rag_store import RagStore
# # from src.data.excel_loader import ExcelDataLoader
# # from src.rag.rag_store import RagStore



# # def build_rag(file_path: str):
# #     loader = ExcelDataLoader(file_path)
# #     data = loader.load_all()

# #     store = RagStore()

# #     store.add_dataframe(
# #         data["sales"],
# #         namespace="sales",
# #         metadata_cols=["Brand", "Category", "Year", "Month"]
# #     )

# #     store.add_dataframe(
# #         data["active_store"],
# #         namespace="active_store"
# #     )

# #     store.persist()
# #     print("✅ RAG index built successfully")


# # if __name__ == "__main__":
# #     build_rag("data/Sales & Active Stores Data.xlsb")
# # src/rag/rag_builder.py
# from src.data.excel_loader import ExcelDataLoader
# from src.rag.rag_store import RagStore


# def build_rag(file_path: str, persist_dir: str = "rag_db"):
#     loader = ExcelDataLoader(file_path)
#     data = loader.load_all()

#     sales_df = data["sales"]
#     active_df = data["active_store"]
#     headers_df = data["headers"]

#     store = RagStore(persist_dir=persist_dir)

#     # Store headers dictionary (very useful for definitions)
#     store.add_dataframe(headers_df, source="headers", text_cols=["column", "description"])

#     # Store sales rows (limit optional during dev)
#     store.add_dataframe(sales_df, source="sales", limit=5000)

#     # Store active store pivot rows (limit optional)
#     store.add_dataframe(active_df, source="active_store", limit=2000)

#     print("✅ RAG built successfully!")
#     print(f"Persisted at: {persist_dir}")


# if __name__ == "__main__":
#     build_rag("data/Sales & Active Stores Data.xlsb")
# from langchain.schema import Document
from dotenv import load_dotenv
from langchain_core.documents import Document

# Load environment variables early
load_dotenv()

from src.insights.insight_builder import InsightBuilder
from src.rag.rag_store import RagStore


def build_rag():
    """
    Build RAG memory from BUSINESS INSIGHTS (not raw data).
    """
    builder = InsightBuilder()
    store = RagStore()

    insights = builder.build_all()

    docs = []
    for ins in insights:
        docs.append(
            Document(
                page_content=ins.text,
                metadata=ins.meta
            )
        )

    store.add_documents(docs)

    print(f"✅ RAG built with {len(docs)} business insights")


if __name__ == "__main__":
    build_rag()
