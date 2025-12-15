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


class SimpleRAGSystem:
    def __init__(self, db_path: Path = None):
        self.db_path = db_path or settings.CHROMA_DB_PATH
        self.db_path.mkdir(parents=True, exist_ok=True)
        
        self.client = chromadb.PersistentClient(
            path=str(self.db_path),
            settings=Settings(
                anonymized_telemetry=False,
                allow_reset=True
            )
        )
        
        self.chunker = AdvancedChunker(
            chunk_size=settings.CHUNK_SIZE,
            chunk_overlap=settings.CHUNK_OVERLAP
        )
        
        self.collection = None
        self.documents_index = {}
    
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
        
        try:
            self.collection.add(
                ids=chunk_ids,
                documents=chunk_documents,
                metadatas=chunk_metadatas
            )
        except Exception as e:
            print(f"[INFO] Adding documents without embeddings: {e}")
            for chunk_id, doc_text, metadata in zip(chunk_ids, chunk_documents, chunk_metadatas):
                self.documents_index[chunk_id] = {
                    'document': doc_text,
                    'metadata': metadata
                }
        
        self.documents_index[doc_id] = {
            'doc_id': doc_id,
            'type': document.metadata.doc_type,
            'total': document.total,
            'chunks': len(chunks)
        }
        
        print(f"Added {len(chunks)} chunks for document {doc_id}")
        return len(chunks)
    
    def search(self, query: str, n_results: int = 5) -> List[Dict]:
        if not self.collection:
            raise ValueError("Collection not initialized")
        
        try:
            results = self.collection.query(
                query_texts=[query],
                n_results=n_results
            )
        except Exception as e:
            print(f"Search error: {e}. Using keyword-based fallback...")
            return self._keyword_search(query, n_results)
        
        processed_results = []
        if results and results['documents'] and results['documents'][0]:
            for i, doc in enumerate(results['documents'][0]):
                processed_results.append({
                    'document': doc,
                    'metadata': results['metadatas'][0][i] if results['metadatas'] else {},
                    'distance': results['distances'][0][i] if results['distances'] else 0
                })
        
        return processed_results
    
    def _keyword_search(self, query: str, n_results: int = 5) -> List[Dict]:
        if not self.collection:
            return []
        
        query_words = query.lower().split()
        all_documents = self.collection.get()
        
        scored_docs = []
        for i, doc_text in enumerate(all_documents['documents']):
            score = sum(1 for word in query_words if word in doc_text.lower())
            if score > 0:
                scored_docs.append({
                    'document': doc_text,
                    'metadata': all_documents['metadatas'][i] if all_documents['metadatas'] else {},
                    'distance': -score
                })
        
        return sorted(scored_docs, key=lambda x: x['distance'], reverse=True)[:n_results]
    
    def get_document_summary(self, doc_id: str) -> Dict:
        if doc_id in self.documents_index:
            return self.documents_index[doc_id]
        return {}


class SimpleRAGFusionRetriever:
    def __init__(self, rag_system: SimpleRAGSystem):
        self.rag = rag_system
    
    def retrieve_with_fusion(
        self,
        original_query: str,
        n_results: int = 5
    ) -> List[Dict]:
        query_variations = self._generate_query_variations(original_query)
        all_queries = [original_query] + query_variations[:2]
        
        all_results = []
        result_map = {}
        
        for query in all_queries:
            results = self.rag.search(query, n_results=n_results)
            
            for i, result in enumerate(results):
                doc_text = result['document']
                if doc_text not in result_map:
                    result_map[doc_text] = {
                        'score': 0,
                        'result': result,
                        'count': 0
                    }
                
                result_map[doc_text]['score'] += (1.0 / (i + 1))
                result_map[doc_text]['count'] += 1
        
        sorted_results = sorted(
            result_map.values(),
            key=lambda x: x['score'],
            reverse=True
        )[:n_results]
        
        return [item['result'] for item in sorted_results]
    
    def _generate_query_variations(self, query: str) -> List[str]:
        variations = []
        
        words = query.split()
        if len(words) > 2:
            variations.append(" ".join(words[:-1]))
            variations.append(" ".join(words[1:]))
        
        synonyms_map = {
            'price': 'cost amount value',
            'quantity': 'amount count number',
            'item': 'product line entry',
            'invoice': 'bill proforma',
            'order': 'purchase PO',
            'discrepancy': 'difference mismatch variance',
            'total': 'sum grand',
        }
        
        for word in words:
            if word.lower() in synonyms_map:
                for synonym in synonyms_map[word.lower()].split():
                    variations.append(query.replace(word, synonym, 1))
        
        return variations[:3]


def initialize_rag_system(db_path: Path = None) -> SimpleRAGSystem:
    rag = SimpleRAGSystem(db_path=db_path)
    rag.create_collection()
    return rag
