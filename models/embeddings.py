import logging
import numpy as np
from typing import List, Any
from sentence_transformers import SentenceTransformer
import torch

logger = logging.getLogger(__name__)

class EmbeddingManager:
    """Manages text embeddings for RAG pipeline"""
    
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        self.model_name = model_name
        self.model = None
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.embedding_dim = 384  # Dimension for all-MiniLM-L6-v2
        
        self._load_model()
    
    def _load_model(self):
        """Load the sentence transformer model"""
        try:
            logger.info(f"Loading embedding model: {self.model_name}")
            
            self.model = SentenceTransformer(self.model_name, device=self.device)
            
            # Get actual embedding dimension
            test_embedding = self.model.encode(["test"])
            self.embedding_dim = len(test_embedding[0])
            
            logger.info(f"Embedding model loaded successfully on {self.device}")
            logger.info(f"Embedding dimension: {self.embedding_dim}")
            
        except Exception as e:
            logger.error(f"Failed to load embedding model: {str(e)}")
            raise
    
    def embed_texts(self, texts: List[str], batch_size: int = 32) -> List[List[float]]:
        """Generate embeddings for a list of texts"""
        if not texts:
            return []
        
        try:
            # Clean texts
            cleaned_texts = [str(text).strip() for text in texts if text and str(text).strip()]
            
            if not cleaned_texts:
                return []
            
            # Generate embeddings in batches
            all_embeddings = []
            
            for i in range(0, len(cleaned_texts), batch_size):
                batch_texts = cleaned_texts[i:i + batch_size]
                
                # Generate embeddings
                batch_embeddings = self.model.encode(
                    batch_texts,
                    convert_to_tensor=False,
                    show_progress_bar=False,
                    normalize_embeddings=True
                )
                
                # Convert to list of lists
                if isinstance(batch_embeddings, np.ndarray):
                    batch_embeddings = batch_embeddings.tolist()
                
                all_embeddings.extend(batch_embeddings)
            
            logger.debug(f"Generated embeddings for {len(texts)} texts")
            return all_embeddings
            
        except Exception as e:
            logger.error(f"Failed to generate embeddings: {str(e)}")
            raise
    
    def embed_text(self, text: str) -> List[float]:
        """Generate embedding for a single text"""
        embeddings = self.embed_texts([text])
        return embeddings[0] if embeddings else []
    
    def calculate_similarity(self, text1: str, text2: str) -> float:
        """Calculate cosine similarity between two texts"""
        try:
            embeddings = self.embed_texts([text1, text2])
            if len(embeddings) != 2:
                return 0.0
            
            # Calculate cosine similarity
            emb1 = np.array(embeddings[0])
            emb2 = np.array(embeddings[1])
            
            similarity = np.dot(emb1, emb2) / (np.linalg.norm(emb1) * np.linalg.norm(emb2))
            return float(similarity)
            
        except Exception as e:
            logger.error(f"Failed to calculate similarity: {str(e)}")
            return 0.0
    
    def get_embedding_info(self) -> dict:
        """Get information about the embedding model"""
        return {
            "model_name": self.model_name,
            "embedding_dim": self.embedding_dim,
            "device": str(self.device),
            "max_seq_length": getattr(self.model, 'max_seq_length', 'unknown')
        }