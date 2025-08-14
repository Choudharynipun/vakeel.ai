import os
import time
import logging
from typing import Dict, List, Optional, Any
import chromadb
from chromadb.config import Settings
import numpy as np
from sentence_transformers import SentenceTransformer
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch

from .llm_handler import LLMHandler
from .embeddings import EmbeddingManager

logger = logging.getLogger(__name__)

class RAGPipeline:
    """Complete RAG pipeline with ChromaDB and local LLM"""
    
    def __init__(self, db_path: str = "./vector_db"):
        self.db_path = db_path
        self.client = None
        self.collection = None
        self.llm_handler = None
        self.embedding_manager = None
        self.reranker_model = None
        self.reranker_tokenizer = None
        
        # Configuration
        self.top_k_retrieval = 10
        self.top_k_rerank = 5
        self.chunk_size = 1000
        self.chunk_overlap = 200
        
    def initialize(self):
        """Initialize all components"""
        try:
            logger.info("Initializing RAG pipeline...")
            
            # Initialize ChromaDB
            self._init_chromadb()
            
            # Initialize embedding manager
            self.embedding_manager = EmbeddingManager()
            
            # Initialize LLM handler
            self.llm_handler = LLMHandler()
            self.llm_handler.initialize()
            
            # Initialize reranker
            self._init_reranker()
            
            logger.info("RAG pipeline initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize RAG pipeline: {str(e)}")
            raise
    
    def _init_chromadb(self):
        """Initialize ChromaDB client and collection"""
        try:
            os.makedirs(self.db_path, exist_ok=True)
            
            self.client = chromadb.PersistentClient(
                path=self.db_path,
                settings=Settings(anonymized_telemetry=False)
            )
            
            # Get or create collection
            self.collection = self.client.get_or_create_collection(
                name="legal_documents",
                metadata={"hnsw:space": "cosine"}
            )
            
            logger.info(f"ChromaDB initialized with {self.collection.count()} documents")
            
        except Exception as e:
            logger.error(f"Failed to initialize ChromaDB: {str(e)}")
            raise
    
    def _init_reranker(self):
        """Initialize BGE reranker model"""
        try:
            model_name = "BAAI/bge-reranker-v2-m3"
            
            logger.info(f"Loading reranker model: {model_name}")
            
            self.reranker_tokenizer = AutoTokenizer.from_pretrained(model_name)
            self.reranker_model = AutoModelForSequenceClassification.from_pretrained(model_name)
            
            # Move to GPU if available
            device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
            self.reranker_model.to(device)
            self.reranker_model.eval()
            
            logger.info(f"Reranker initialized on device: {device}")
            
        except Exception as e:
            logger.error(f"Failed to initialize reranker: {str(e)}")
            # Continue without reranker if it fails
            self.reranker_model = None
            self.reranker_tokenizer = None
    
    def _chunk_text(self, text: str, metadata: Dict = None) -> List[Dict]:
        """Split text into chunks with metadata"""
        chunks = []
        words = text.split()
        
        for i in range(0, len(words), self.chunk_size - self.chunk_overlap):
            chunk_words = words[i:i + self.chunk_size]
            chunk_text = " ".join(chunk_words)
            
            chunk_metadata = {
                "chunk_id": len(chunks),
                "start_word": i,
                "end_word": min(i + self.chunk_size, len(words)),
                "word_count": len(chunk_words)
            }
            
            if metadata:
                chunk_metadata.update(metadata)
            
            chunks.append({
                "text": chunk_text,
                "metadata": chunk_metadata
            })
        
        return chunks
    
    def index_document(self, text: str, filename: str = None) -> str:
        """Index a document in the vector database"""
        try:
            doc_id = f"doc_{int(time.time() * 1000)}"
            
            if filename:
                doc_id = f"{doc_id}_{filename.replace('.', '_')}"
            
            # Create chunks
            chunks = self._chunk_text(text, {
                "document_id": doc_id,
                "filename": filename or "unknown",
                "document_type": "user_uploaded",
                "indexed_at": time.time()
            })
            
            # Generate embeddings for chunks
            texts = [chunk["text"] for chunk in chunks]
            embeddings = self.embedding_manager.embed_texts(texts)
            
            # Prepare data for ChromaDB
            ids = [f"{doc_id}_chunk_{i}" for i in range(len(chunks))]
            metadatas = [chunk["metadata"] for chunk in chunks]
            
            # Add to collection
            self.collection.add(
                ids=ids,
                embeddings=embeddings,
                documents=texts,
                metadatas=metadatas
            )
            
            logger.info(f"Indexed document {doc_id} with {len(chunks)} chunks")
            return doc_id
            
        except Exception as e:
            logger.error(f"Failed to index document: {str(e)}")
            raise
    
    def index_legal_documents(self, documents: List[Dict]):
        """Index legal knowledge base documents"""
        try:
            logger.info(f"Indexing {len(documents)} legal documents...")
            
            for doc in documents:
                chunks = self._chunk_text(doc["content"], {
                    "document_id": doc["id"],
                    "title": doc["title"],
                    "document_type": "legal_knowledge",
                    "category": doc.get("category", "general"),
                    "source": doc.get("source", "unknown"),
                    "indexed_at": time.time()
                })
                
                if chunks:
                    texts = [chunk["text"] for chunk in chunks]
                    embeddings = self.embedding_manager.embed_texts(texts)
                    
                    ids = [f"{doc['id']}_chunk_{i}" for i in range(len(chunks))]
                    metadatas = [chunk["metadata"] for chunk in chunks]
                    
                    self.collection.add(
                        ids=ids,
                        embeddings=embeddings,
                        documents=texts,
                        metadatas=metadatas
                    )
            
            logger.info("Legal documents indexed successfully")
            
        except Exception as e:
            logger.error(f"Failed to index legal documents: {str(e)}")
            raise
    
    def _rerank_results(self, query: str, documents: List[str], scores: List[float]) -> List[int]:
        """Rerank retrieved documents using BGE reranker"""
        if not self.reranker_model or not documents:
            return list(range(len(documents)))
        
        try:
            pairs = [[query, doc] for doc in documents]
            
            with torch.no_grad():
                inputs = self.reranker_tokenizer(
                    pairs,
                    padding=True,
                    truncation=True,
                    return_tensors='pt',
                    max_length=512
                )
                
                # Move to same device as model
                device = next(self.reranker_model.parameters()).device
                inputs = {k: v.to(device) for k, v in inputs.items()}
                
                scores = self.reranker_model(**inputs, return_dict=True).logits.view(-1).float()
                scores = torch.sigmoid(scores).cpu().numpy()
            
            # Sort by reranker scores
            ranked_indices = np.argsort(scores)[::-1]
            return ranked_indices.tolist()
            
        except Exception as e:
            logger.error(f"Reranking failed: {str(e)}")
            return list(range(len(documents)))
    
    def retrieve_documents(self, query: str, document_id: str = None) -> List[Dict]:
        """Retrieve relevant documents from vector database"""
        try:
            # Generate query embedding
            query_embedding = self.embedding_manager.embed_texts([query])[0]
            
            # Build where clause
            where_clause = None
            if document_id:
                where_clause = {"document_id": document_id}
            
            # Query collection
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=self.top_k_retrieval,
                where=where_clause,
                include=["documents", "metadatas", "distances"]
            )
            
            if not results["documents"][0]:
                return []
            
            # Prepare documents for reranking
            documents = results["documents"][0]
            metadatas = results["metadatas"][0]
            distances = results["distances"][0]
            
            # Rerank results
            reranked_indices = self._rerank_results(query, documents, distances)
            
            # Return top-k reranked results
            retrieved_docs = []
            for idx in reranked_indices[:self.top_k_rerank]:
                retrieved_docs.append({
                    "text": documents[idx],
                    "metadata": metadatas[idx],
                    "score": 1.0 - distances[idx],  # Convert distance to similarity
                    "rank": len(retrieved_docs) + 1
                })
            
            return retrieved_docs
            
        except Exception as e:
            logger.error(f"Document retrieval failed: {str(e)}")
            return []
    
    def query(self, question: str, document_id: str = None, max_tokens: int = 1000) -> Dict[str, Any]:
        """Process a query through the RAG pipeline"""
        start_time = time.time()
        
        try:
            # Retrieve relevant documents
            retrieved_docs = self.retrieve_documents(question, document_id)
            
            # Prepare context
            context_parts = []
            sources = []
            
            for doc in retrieved_docs:
                context_parts.append(f"[Source: {doc['metadata'].get('title', 'Unknown')}]\n{doc['text']}")
                sources.append({
                    "title": doc['metadata'].get('title', 'Unknown'),
                    "filename": doc['metadata'].get('filename', 'Unknown'),
                    "document_type": doc['metadata'].get('document_type', 'unknown'),
                    "score": doc['score'],
                    "rank": doc['rank']
                })
            
            context = "\n\n".join(context_parts) if context_parts else ""
            
            # Generate response using LLM
            response = self.llm_handler.generate_response(
                question=question,
                context=context,
                max_tokens=max_tokens
            )
            
            processing_time = time.time() - start_time
            
            return {
                "answer": response,
                "sources": sources,
                "context_length": len(context),
                "retrieved_docs": len(retrieved_docs),
                "processing_time": processing_time,
                "confidence": self._calculate_confidence(retrieved_docs)
            }
            
        except Exception as e:
            logger.error(f"Query processing failed: {str(e)}")
            return {
                "answer": "I apologize, but I encountered an error while processing your question. Please try again.",
                "sources": [],
                "context_length": 0,
                "retrieved_docs": 0,
                "processing_time": time.time() - start_time,
                "confidence": 0.0
            }
    
    def _calculate_confidence(self, retrieved_docs: List[Dict]) -> float:
        """Calculate confidence score based on retrieval results"""
        if not retrieved_docs:
            return 0.0
        
        # Simple confidence calculation based on top document score
        top_score = retrieved_docs[0]["score"] if retrieved_docs else 0.0
        
        # Normalize score to 0-1 range
        confidence = min(top_score, 1.0)
        return round(confidence, 2)
    
    def clear_user_documents(self):
        """Clear user-uploaded documents from the database"""
        try:
            # Get all user documents
            results = self.collection.get(
                where={"document_type": "user_uploaded"},
                include=["documents"]
            )
            
            if results["ids"]:
                self.collection.delete(
                    where={"document_type": "user_uploaded"}
                )
                logger.info(f"Cleared {len(results['ids'])} user documents")
            
        except Exception as e:
            logger.error(f"Failed to clear user documents: {str(e)}")
    
    def get_document_count(self) -> Dict[str, int]:
        """Get count of indexed documents by type"""
        try:
            total_count = self.collection.count()
            
            legal_results = self.collection.get(
                where={"document_type": "legal_knowledge"},
                include=["documents"]
            )
            legal_count = len(legal_results["ids"]) if legal_results["ids"] else 0
            
            user_results = self.collection.get(
                where={"document_type": "user_uploaded"},
                include=["documents"]
            )
            user_count = len(user_results["ids"]) if user_results["ids"] else 0
            
            return {
                "total": total_count,
                "legal_knowledge": legal_count,
                "user_uploaded": user_count
            }
            
        except Exception as e:
            logger.error(f"Failed to get document count: {str(e)}")
            return {"total": 0, "legal_knowledge": 0, "user_uploaded": 0}
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about loaded models"""
        return {
            "llm_model": self.llm_handler.model_name if self.llm_handler else "Not loaded",
            "embedding_model": self.embedding_manager.model_name if self.embedding_manager else "Not loaded",
            "reranker_available": self.reranker_model is not None,
            "vector_db": "ChromaDB",
            "device": torch.device("cuda" if torch.cuda.is_available() else "cpu").type
        }