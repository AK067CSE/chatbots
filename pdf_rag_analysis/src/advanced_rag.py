from typing import List, Dict, Tuple, Any, Optional
from pathlib import Path
import json
from datetime import datetime
import re

try:
    from sentence_transformers import SentenceTransformer
    HAS_EMBEDDINGS = True
except ImportError:
    HAS_EMBEDDINGS = False

try:
    import numpy as np
    HAS_NUMPY = True
except ImportError:
    HAS_NUMPY = False

from rank_bm25 import BM25Okapi
from src.config import settings
from src.pdf_extractor import ExtractedDocument


class AdvancedChunker:
    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
    
    def chunk_text(self, text: str, metadata: Dict, doc_id: str) -> List[Dict[str, Any]]:
        chunks = []
        words = text.split()
        
        for i in range(0, len(words), self.chunk_size - self.chunk_overlap):
            chunk_words = words[i:i + self.chunk_size]
            chunk_text = " ".join(chunk_words)
            
            if len(chunk_text.strip()) > 50:
                chunk_metadata = {
                    **metadata,
                    'chunk_index': len(chunks),
                    'chunk_size': len(chunk_text),
                    'chunk_type': self._identify_chunk_type(chunk_text),
                    'doc_id': doc_id
                }
                chunks.append({
                    'text': chunk_text,
                    'metadata': chunk_metadata,
                    'id': f"{doc_id}_chunk_{len(chunks)}"
                })
        
        return chunks
    
    def _identify_chunk_type(self, chunk: str) -> str:
        lower = chunk.lower()
        if any(w in lower for w in ['sku', 'qty', 'quantity', 'price', 'unit']):
            return 'LINE_ITEMS'
        elif any(w in lower for w in ['subtotal', 'total', 'tax', 'grand']):
            return 'TOTALS'
        elif any(w in lower for w in ['note', 'term', 'condition', 'remark']):
            return 'NOTES'
        elif any(w in lower for w in ['date', 'po', 'invoice', 'order']):
            return 'METADATA'
        return 'GENERAL'


class BM25Retriever:
    def __init__(self):
        self.corpus = []
        self.bm25 = None
        self.chunk_map = {}
    
    def add_documents(self, chunks: List[Dict[str, Any]]):
        for chunk in chunks:
            doc_id = chunk['id']
            tokens = self._tokenize(chunk['text'])
            self.corpus.append(tokens)
            self.chunk_map[len(self.corpus) - 1] = chunk
        
        self.bm25 = BM25Okapi(self.corpus)
    
    def retrieve(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        if not self.bm25:
            return []
        
        tokens = self._tokenize(query)
        scores = self.bm25.get_scores(tokens)
        
        top_indices = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[:top_k]
        results = []
        for idx in top_indices:
            if idx in self.chunk_map:
                chunk = self.chunk_map[idx]
                results.append({
                    'text': chunk['text'],
                    'metadata': chunk['metadata'],
                    'score': float(scores[idx]),
                    'retrieval_method': 'BM25'
                })
        
        return results
    
    def _tokenize(self, text: str) -> List[str]:
        text = text.lower()
        text = re.sub(r'[^\w\s]', ' ', text)
        return text.split()


class DenseRetriever:
    def __init__(self, model_name: str = "BAAI/bge-base-en-v1.5"):
        self.model_name = model_name
        self.model = None
        self.embeddings = {}
        
        if HAS_EMBEDDINGS:
            try:
                self.model = SentenceTransformer(model_name)
            except Exception as e:
                print(f"Warning: Could not load embedding model: {e}")
    
    def add_documents(self, chunks: List[Dict[str, Any]]):
        if not self.model:
            return
        
        try:
            for chunk in chunks:
                text = chunk['text']
                embedding = self.model.encode(text)
                self.embeddings[chunk['id']] = {
                    'embedding': embedding,
                    'chunk': chunk
                }
        except Exception as e:
            print(f"Error encoding documents: {e}")
    
    def retrieve(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        if not self.model or not self.embeddings:
            return []
        
        try:
            query_embedding = self.model.encode(query)
            
            scores = {}
            for doc_id, data in self.embeddings.items():
                similarity = self._cosine_similarity(query_embedding, data['embedding'])
                scores[doc_id] = similarity
            
            top_docs = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:top_k]
            
            results = []
            for doc_id, score in top_docs:
                chunk = self.embeddings[doc_id]['chunk']
                results.append({
                    'text': chunk['text'],
                    'metadata': chunk['metadata'],
                    'score': float(score),
                    'retrieval_method': 'DENSE'
                })
            
            return results
        except Exception as e:
            print(f"Error retrieving: {e}")
            return []
    
    def _cosine_similarity(self, a, b):
        if HAS_NUMPY:
            import numpy as np
            return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))
        else:
            dot_product = sum(x * y for x, y in zip(a, b))
            norm_a = sum(x * x for x in a) ** 0.5
            norm_b = sum(x * x for x in b) ** 0.5
            return dot_product / (norm_a * norm_b) if norm_a > 0 and norm_b > 0 else 0.0


class HybridRetriever:
    def __init__(self, alpha: float = 0.5):
        self.bm25_retriever = BM25Retriever()
        self.dense_retriever = DenseRetriever()
        self.alpha = alpha
    
    def add_documents(self, chunks: List[Dict[str, Any]]):
        self.bm25_retriever.add_documents(chunks)
        self.dense_retriever.add_documents(chunks)
    
    def retrieve(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        bm25_results = self.bm25_retriever.retrieve(query, top_k * 2)
        dense_results = self.dense_retriever.retrieve(query, top_k * 2)
        
        combined = {}
        
        max_bm25_score = max([r['score'] for r in bm25_results], default=1.0)
        for result in bm25_results:
            doc_id = result['metadata']['doc_id']
            normalized_score = result['score'] / max_bm25_score if max_bm25_score > 0 else 0
            combined[doc_id] = {
                'result': result,
                'bm25_score': normalized_score,
                'dense_score': 0
            }
        
        max_dense_score = max([r['score'] for r in dense_results], default=1.0)
        for result in dense_results:
            doc_id = result['metadata']['doc_id']
            normalized_score = result['score'] / max_dense_score if max_dense_score > 0 else 0
            if doc_id in combined:
                combined[doc_id]['dense_score'] = normalized_score
            else:
                combined[doc_id] = {
                    'result': result,
                    'bm25_score': 0,
                    'dense_score': normalized_score
                }
        
        for doc_id in combined:
            combined[doc_id]['hybrid_score'] = (
                self.alpha * combined[doc_id]['bm25_score'] +
                (1 - self.alpha) * combined[doc_id]['dense_score']
            )
        
        sorted_results = sorted(combined.items(), key=lambda x: x[1]['hybrid_score'], reverse=True)
        
        final_results = []
        for doc_id, data in sorted_results[:top_k]:
            result = data['result']
            result['score'] = data['hybrid_score']
            result['retrieval_method'] = 'HYBRID'
            final_results.append(result)
        
        return final_results


class RAGFusionRetriever:
    def __init__(self, hybrid_retriever: HybridRetriever):
        self.retriever = hybrid_retriever
    
    def retrieve_with_fusion(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        query_variations = self._generate_query_variations(query)
        all_results = {}
        
        for var_query in query_variations:
            results = self.retriever.retrieve(var_query, top_k)
            for rank, result in enumerate(results):
                doc_text = result['text']
                if doc_text not in all_results:
                    all_results[doc_text] = {
                        'result': result,
                        'rrf_score': 0
                    }
                all_results[doc_text]['rrf_score'] += 1 / (rank + 60)
        
        sorted_results = sorted(
            all_results.values(),
            key=lambda x: x['rrf_score'],
            reverse=True
        )
        
        final_results = []
        for item in sorted_results[:top_k]:
            result = item['result']
            result['score'] = item['rrf_score']
            result['retrieval_method'] = 'RAG_FUSION'
            final_results.append(result)
        
        return final_results
    
    def _generate_query_variations(self, query: str) -> List[str]:
        variations = [query]
        
        if '?' in query:
            variations.append(query.replace('?', ''))
        
        if 'what' in query.lower():
            variations.append(query.lower().replace('what ', '').title())
        
        if 'how' in query.lower():
            variations.append(query.lower().replace('how ', '').title())
        
        words = query.split()
        if len(words) > 3:
            variations.append(' '.join(words[:3]))
            variations.append(' '.join(words[-3:]))
        
        return variations[:5]


class AdvancedRAGSystem:
    def __init__(self, db_path: Path = None):
        self.db_path = db_path or settings.CHROMA_DB_PATH
        self.db_path.mkdir(parents=True, exist_ok=True)
        
        self.chunker = AdvancedChunker(
            chunk_size=settings.CHUNK_SIZE,
            chunk_overlap=settings.CHUNK_OVERLAP
        )
        
        self.hybrid_retriever = HybridRetriever(alpha=0.5)
        self.fusion_retriever = RAGFusionRetriever(self.hybrid_retriever)
        
        self.documents_store = {}
        self.chunks_store = []
    
    def add_document(self, document: ExtractedDocument, doc_id: str):
        doc_metadata = {
            'doc_type': document.metadata.doc_type,
            'document_id': document.metadata.document_id,
            'date': document.metadata.date,
            'vendor': document.metadata.vendor_name,
            'customer': document.metadata.customer_name,
            'total': document.total,
            'items_count': len(document.items)
        }
        
        chunks = self.chunker.chunk_text(document.raw_text, doc_metadata, doc_id)
        self.chunks_store.extend(chunks)
        self.documents_store[doc_id] = document
        
        self.hybrid_retriever.add_documents(chunks)
        
        return len(chunks)
    
    def retrieve(self, query: str, top_k: int = 5, use_fusion: bool = True) -> List[Dict[str, Any]]:
        if use_fusion:
            return self.fusion_retriever.retrieve_with_fusion(query, top_k)
        else:
            return self.hybrid_retriever.retrieve(query, top_k)
    
    def get_summary(self) -> Dict[str, Any]:
        return {
            'documents': len(self.documents_store),
            'chunks': len(self.chunks_store),
            'retrieval_methods': ['BM25', 'Dense', 'Hybrid', 'RAG_Fusion']
        }
