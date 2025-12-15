from pathlib import Path
from typing import List, Dict, Tuple
import chromadb
from chromadb.config import Settings
try:
    from langchain_text_splitters import RecursiveCharacterTextSplitter
except ImportError:
    from langchain.text_splitter import RecursiveCharacterTextSplitter
import json
from src.config import settings
from src.pdf_extractor import ExtractedDocument

try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except Exception as e:
    print(f"Warning: sentence_transformers not available ({e}), using fallback")
    SENTENCE_TRANSFORMERS_AVAILABLE = False


class AdvancedChunker:
    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separators=["\n\n", "\n", ". ", " ", ""]
        )
    
    def chunk_text(self, text: str, metadata: Dict) -> List[Tuple[str, Dict]]:
        chunks = self.splitter.split_text(text)
        
        enriched_chunks = []
        for i, chunk in enumerate(chunks):
            chunk_metadata = {
                **metadata,
                'chunk_index': i,
                'chunk_size': len(chunk),
                'chunk_type': self._identify_chunk_type(chunk)
            }
            enriched_chunks.append((chunk, chunk_metadata))
        
        return enriched_chunks
    
    def _identify_chunk_type(self, chunk: str) -> str:
        lower_chunk = chunk.lower()
        
        if any(word in lower_chunk for word in ['item', 'description', 'quantity', 'price', 'unit']):
            return 'LINE_ITEMS'
        elif any(word in lower_chunk for word in ['total', 'subtotal', 'tax', 'grand']):
            return 'TOTALS'
        elif any(word in lower_chunk for word in ['note', 'term', 'condition', 'remark']):
            return 'NOTES_TERMS'
        elif any(word in lower_chunk for word in ['date', 'po', 'order', 'invoice']):
            return 'METADATA'
        else:
            return 'GENERAL'


class RAGSystem:
    def __init__(self, db_path: Path = None, model_name: str = "BAAI/bge-base-en-v1.5"):
        if not SENTENCE_TRANSFORMERS_AVAILABLE:
            raise ImportError("Sentence transformers not available. Use SimpleRAGSystem instead.")
        
        self.db_path = db_path or settings.CHROMA_DB_PATH
        self.db_path.mkdir(parents=True, exist_ok=True)
        
        self.client = chromadb.PersistentClient(
            path=str(self.db_path),
            settings=Settings(
                anonymized_telemetry=False,
                allow_reset=True
            )
        )
        
        self.embedding_model = SentenceTransformer(model_name)
        self.chunker = AdvancedChunker(
            chunk_size=settings.CHUNK_SIZE,
            chunk_overlap=settings.CHUNK_OVERLAP
        )
        
        self.collection = None
    
    def create_collection(self, collection_name: str = "pdf_documents"):
        try:
            self.client.delete_collection(name=collection_name)
        except:
            pass
        
        self.collection = self.client.create_collection(
            name=collection_name,
            metadata={"hnsw:space": "cosine"}
        )
        
        return self.collection
    
    def add_document(self, document: ExtractedDocument, doc_id: str):
        if not self.collection:
            self.create_collection()
        
        document_metadata = {
            'doc_type': document.metadata.doc_type,
            'document_id': document.metadata.document_id,
            'date': document.metadata.date,
            'vendor': document.metadata.vendor_name,
            'customer': document.metadata.customer_name,
            'total': document.total,
            'items_count': len(document.items)
        }
        
        chunks = self.chunker.chunk_text(document.raw_text, document_metadata)
        
        chunk_ids = []
        chunk_documents = []
        chunk_metadatas = []
        
        for i, (chunk_text, chunk_meta) in enumerate(chunks):
            chunk_id = f"{doc_id}_chunk_{i}"
            chunk_ids.append(chunk_id)
            chunk_documents.append(chunk_text)
            chunk_metadatas.append(chunk_meta)
        
        embeddings = self.embedding_model.encode(chunk_documents, convert_to_tensor=False).tolist()
        
        self.collection.add(
            ids=chunk_ids,
            documents=chunk_documents,
            embeddings=embeddings,
            metadatas=chunk_metadatas
        )
        
        print(f"Added {len(chunks)} chunks for document {doc_id}")
        return len(chunks)
    
    def search(self, query: str, n_results: int = 5) -> List[Dict]:
        if not self.collection:
            raise ValueError("Collection not initialized")
        
        results = self.collection.query(
            query_texts=[query],
            n_results=n_results
        )
        
        processed_results = []
        if results and results['documents'] and results['documents'][0]:
            for i, doc in enumerate(results['documents'][0]):
                processed_results.append({
                    'document': doc,
                    'metadata': results['metadatas'][0][i] if results['metadatas'] else {},
                    'distance': results['distances'][0][i] if results['distances'] else 0
                })
        
        return processed_results
    
    def rag_fusion_search(self, queries: List[str], n_results: int = 5) -> List[Dict]:
        if not self.collection:
            raise ValueError("Collection not initialized")
        
        all_results = []
        result_scores = {}
        
        for query in queries:
            results = self.search(query, n_results=n_results)
            
            for i, result in enumerate(results):
                doc_id = result['document']
                score = 1.0 / (i + 1)
                
                if doc_id not in result_scores:
                    result_scores[doc_id] = {
                        'score': 0,
                        'data': result,
                        'count': 0
                    }
                
                result_scores[doc_id]['score'] += score
                result_scores[doc_id]['count'] += 1
        
        sorted_results = sorted(
            result_scores.values(),
            key=lambda x: x['score'],
            reverse=True
        )[:n_results]
        
        return [item['data'] for item in sorted_results]
    
    def get_document_summary(self, doc_id: str) -> Dict:
        if not self.collection:
            raise ValueError("Collection not initialized")
        
        results = self.collection.get(
            where={"document_id": doc_id}
        )
        
        if not results['documents']:
            return {}
        
        metadata_sample = results['metadatas'][0] if results['metadatas'] else {}
        
        return {
            'document_id': metadata_sample.get('document_id'),
            'doc_type': metadata_sample.get('doc_type'),
            'vendor': metadata_sample.get('vendor'),
            'customer': metadata_sample.get('customer'),
            'total': metadata_sample.get('total'),
            'items_count': metadata_sample.get('items_count'),
            'chunks_stored': len(results['documents'])
        }


class RAGFusionRetriever:
    def __init__(self, rag_system: RAGSystem):
        self.rag = rag_system
    
    def retrieve_with_fusion(
        self,
        original_query: str,
        n_results: int = 5
    ) -> List[Dict]:
        query_variations = self._generate_query_variations(original_query)
        all_queries = [original_query] + query_variations
        
        return self.rag.rag_fusion_search(all_queries, n_results=n_results)
    
    def _generate_query_variations(self, query: str) -> List[str]:
        variations = []
        
        words = query.split()
        if len(words) > 2:
            variations.append(" ".join(words[:-1]))
            variations.append(" ".join(words[1:]))
        
        synonyms_map = {
            'price': 'cost, amount, value',
            'quantity': 'amount, count, number',
            'item': 'product, line, entry',
            'invoice': 'bill, proforma',
            'order': 'purchase, PO',
            'discrepancy': 'difference, mismatch, variance',
            'total': 'sum, grand total',
        }
        
        for word in words:
            if word.lower() in synonyms_map:
                for synonym in synonyms_map[word.lower()].split(', '):
                    variations.append(query.replace(word, synonym, 1))
        
        return variations[:3]


def initialize_rag_system(db_path: Path = None):
    try:
        if SENTENCE_TRANSFORMERS_AVAILABLE:
            rag = RAGSystem(db_path=db_path)
            rag.create_collection()
            return rag
        else:
            raise ImportError("Sentence transformers not available")
    except Exception as e:
        print(f"[WARN] RAG system initialization failed: {e}")
        print("[INFO] Using SimpleRAGSystem as fallback")
        from src.rag_system_simple import initialize_rag_system as init_simple
        return init_simple(db_path=db_path)
