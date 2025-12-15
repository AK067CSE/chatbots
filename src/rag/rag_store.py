# # # # from dotenv import load_dotenv
# # # # from langchain_community.vectorstores import Chroma
# # # # from langchain_chroma import Chroma


# # # # from langchain_openai import OpenAIEmbeddings
# # # # import os

# # # # # Ensure environment variables are loaded
# # # # load_dotenv()


# # # # class RagStore:
# # # #     def __init__(self, persist_dir="rag_db"):
# # # #         self.persist_dir = persist_dir
# # # #         self.embeddings = OpenAIEmbeddings()
# # # #         self.db = Chroma(
# # # #             persist_directory=persist_dir,
# # # #             embedding_function=self.embeddings
# # # #         )


# # # #     def add_documents(self, documents):
# # # #         self.db.add_documents(documents)
# # # #         self.db.persist()

# # # #     def similarity_search(self, query, k=5):
# # # #         return self.db.similarity_search(query, k=k)
# # # # src/rag/rag_store.py
# # # from __future__ import annotations

# # # import os
# # # from typing import Optional, List
# # # from dotenv import load_dotenv
# # # import pandas as pd
# # # from langchain_openai import OpenAIEmbeddings
# # # from langchain_core.documents import Document
# # # from langchain_chroma import Chroma   # ✅ new import

# # # from dotenv import load_dotenv
# # # class RagStore:
# # #     def __init__(self, persist_dir: str = "rag_db", collection_name: str = "salesbot"):
# # #         self.persist_dir = persist_dir
# # #         self.collection_name = collection_name

# # #         os.makedirs(self.persist_dir, exist_ok=True)

# # #         self.embeddings = OpenAIEmbeddings()
# # #         self.db = Chroma(
# # #             collection_name=self.collection_name,
# # #             persist_directory=self.persist_dir,
# # #             embedding_function=self.embeddings,
# # #         )

# # #     def add_documents(self, docs: List[Document]) -> None:
# # #         self.db.add_documents(docs)

# # #     def add_dataframe(
# # #         self,
# # #         df: pd.DataFrame,
# # #         *,
# # #         source: str,
# # #         text_cols: Optional[list[str]] = None,
# # #         limit: Optional[int] = None,
# # #     ) -> None:
# # #         """
# # #         Convert rows into Documents and add into vector store.

# # #         - source: label like "sales" / "active_store" / "headers"
# # #         - text_cols: which columns to include in the document text
# # #         - limit: optionally limit rows for quick dev
# # #         """
# # #         if limit:
# # #             df = df.head(limit)

# # #         if text_cols is None:
# # #             text_cols = list(df.columns)

# # #         docs: List[Document] = []
# # #         for i, row in df.iterrows():
# # #             parts = []
# # #             for c in text_cols:
# # #                 val = row.get(c, "")
# # #                 if pd.isna(val):
# # #                     continue
# # #                 parts.append(f"{c}: {val}")
# # #             text = "\n".join(parts).strip()
# # #             if not text:
# # #                 continue

# # #             docs.append(
# # #                 Document(
# # #                     page_content=text,
# # #                     metadata={"source": source, "row": int(i)},
# # #                 )
# # #             )

# # #         if docs:
# # #             self.add_documents(docs)

# # #     def search(self, query: str, k: int = 5):
# # #         return self.db.similarity_search(query, k=k)
# # from dotenv import load_dotenv
# # load_dotenv()
# # from langchain_chroma import Chroma
# # from langchain_openai import OpenAIEmbeddings


# # class RagStore:
# #     def __init__(self, persist_dir="rag_db"):
# #         self.db = Chroma(
# #             persist_directory=persist_dir,
# #             embedding_function=OpenAIEmbeddings()
# #         )

# #     def add_texts(self, texts, metadatas=None):
# #         self.db.add_texts(texts=texts, metadatas=metadatas)

# #     def search(self, query: str, k: int = 5):
# #         return self.db.similarity_search(query, k=k)
# from langchain_chroma import Chroma
# from langchain_openai import OpenAIEmbeddings


# class RagStore:
#     def __init__(self, persist_dir="rag_db"):
#         self.db = Chroma(
#             persist_directory=persist_dir,
#             embedding_function=OpenAIEmbeddings()
#         )

#     def add_texts(self, texts, metadatas=None):
#         self.db.add_texts(texts=texts, metadatas=metadatas)

#     def search(self, query: str, k: int = 5):
#         return self.db.similarity_search(query, k=k)
from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma

from langchain_core.documents import Document

# Load environment variables (including OPENAI_API_KEY)
load_dotenv()


class RagStore:
    def __init__(self, persist_dir="rag_db"):
        self.embeddings = OpenAIEmbeddings()
        self.db = Chroma(
            persist_directory=persist_dir,
            embedding_function=self.embeddings
        )

    # def add_documents(self, docs):
    #     self.db.add_documents(docs)
    #     self.db.persist()
    def add_documents(self, docs):
        self.db.add_documents(docs)


    def search(self, query: str, k: int = 5):
        return self.db.similarity_search(query, k=k)
