"""Embedding service using sentence-transformers."""
from typing import List
from sentence_transformers import SentenceTransformer
from app.config import settings
import logging

logger = logging.getLogger(__name__)

# Global model instance (singleton pattern)
_model: SentenceTransformer = None


def get_embedding_model() -> SentenceTransformer:
    """Get or initialize the embedding model (singleton pattern)."""
    global _model
    if _model is None:
        logger.info(f"Loading embedding model: {settings.EMBEDDING_MODEL}")
        _model = SentenceTransformer(settings.EMBEDDING_MODEL)
        logger.info("Embedding model loaded successfully")
    return _model


def generate_embedding(text: str) -> List[float]:
    """
    Generate embedding for a single text.
    
    Args:
        text: Input text to embed
        
    Returns:
        List of floats representing the embedding vector
    """
    if not text or not text.strip():
        raise ValueError("Text cannot be empty")
    
    model = get_embedding_model()
    embedding = model.encode(text, normalize_embeddings=True)
    return embedding.tolist()


def generate_embeddings_batch(texts: List[str], batch_size: int = 32) -> List[List[float]]:
    """
    Generate embeddings for multiple texts in batch.
    
    Args:
        texts: List of texts to embed
        batch_size: Number of texts to process at once
        
    Returns:
        List of embedding vectors
    """
    if not texts:
        return []
    
    # Filter out empty texts
    valid_texts = [text.strip() if text else "" for text in texts]
    if not any(valid_texts):
        raise ValueError("No valid texts provided")
    
    model = get_embedding_model()
    embeddings = model.encode(
        valid_texts,
        batch_size=batch_size,
        normalize_embeddings=True,
        show_progress_bar=False
    )
    return embeddings.tolist()
