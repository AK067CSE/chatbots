# helper to test calling retriever methods
from src.rag.enhanced_rag_builder import EnhancedRAGBuilder
r = EnhancedRAGBuilder()
try:
    r.load_vector_store()
    retr = r.retriever
    print('retriever:', type(retr))
    try:
        docs = retr.get_relevant_documents('test')
        print('got docs via get_relevant_documents', len(docs))
    except Exception as e:
        print('get_relevant_documents failed:', e)
        try:
            docs = retr._get_relevant_documents('test', run_manager=None)
            print('got docs via _get_relevant_documents with run_manager', len(docs))
        except Exception as e2:
            print('fallback failed:', e2)
except Exception as e:
    import traceback; traceback.print_exc()
