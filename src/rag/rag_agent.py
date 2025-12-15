# # from src.rag.rag_store import RAGStore
# from src.rag.rag_store import RagStore


# class RagAgent:
#     def __init__(self, persist_dir="rag_db"):
#         self.store = RagStore(persist_dir=persist_dir)

#     def search(self, query: str, k: int = 5):
#         return self.store.search(query, k=k)


# # class RAGAgent:
# #     def __init__(self):
# #         self.store = RAGStore()

# #     def get_context(self, question: str) -> str:
# #         docs = self.store.search(question)
# #         return "\n".join([d.page_content for d in docs])
from src.rag.rag_store import RagStore


class RagAgent:
    def __init__(self, persist_dir="rag_db"):
        self.store = RagStore(persist_dir=persist_dir)

    def search(self, query: str, k: int = 5):
        return self.store.search(query, k=k)
    
    def retrieve(self, query: str) -> str:
        """Retrieve context for query"""
        try:
            results = self.search(query, k=5)
            if isinstance(results, list):
                return "\n".join([str(r) for r in results])
            return str(results)
        except Exception as e:
            return f"RAG retrieval error: {str(e)}"


class RAGAgent(RagAgent):
    """Alias for RagAgent with uppercase naming"""
    pass
