"""Unit tests for embedding service."""
import pytest
from app.services.embedding import generate_embedding, generate_embeddings_batch


def test_generate_embedding():
    """Test single embedding generation."""
    text = "This is a test complaint about credit card issues."
    embedding = generate_embedding(text)
    
    assert embedding is not None
    assert isinstance(embedding, list)
    assert len(embedding) == 384  # all-MiniLM-L6-v2 dimension
    assert all(isinstance(x, float) for x in embedding)


def test_generate_embedding_empty_text():
    """Test embedding generation with empty text raises error."""
    with pytest.raises(ValueError):
        generate_embedding("")


def test_generate_embeddings_batch():
    """Test batch embedding generation."""
    texts = [
        "First complaint about credit card",
        "Second complaint about mortgage",
        "Third complaint about bank account"
    ]
    embeddings = generate_embeddings_batch(texts, batch_size=2)
    
    assert len(embeddings) == 3
    assert all(len(emb) == 384 for emb in embeddings)
    assert all(isinstance(emb, list) for emb in embeddings)


def test_generate_embeddings_batch_empty():
    """Test batch embedding with empty list."""
    embeddings = generate_embeddings_batch([])
    assert embeddings == []
