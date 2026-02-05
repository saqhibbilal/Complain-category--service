"""Configuration settings for the application."""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Database settings
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/complaints_db"
    
    # Mistral API settings
    MISTRAL_API_KEY: str = ""
    MISTRAL_MODEL: str = "mistral-small"  # or "open-mistral-7b" for free tier
    MISTRAL_BASE_URL: Optional[str] = None
    
    # Embedding model settings
    EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"
    EMBEDDING_DIMENSION: int = 384
    
    # Batch processing settings
    BATCH_SIZE: int = 100
    MAX_RETRIES: int = 3
    
    # API settings
    API_V1_PREFIX: str = "/api/v1"
    CORS_ORIGINS: list[str] = ["http://localhost:3000", "http://localhost:5173"]
    
    # Vector search settings
    SIMILARITY_TOP_K: int = 5
    SIMILARITY_THRESHOLD: float = 0.7
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
