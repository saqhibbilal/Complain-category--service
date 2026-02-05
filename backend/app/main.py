"""FastAPI application entry point."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.database import init_db, check_pgvector_extension
from app.api.routes import complaints, search
import logging
import os
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Create FastAPI app
app = FastAPI(
    title="Complaint Categorization and RAG System",
    description="AI-powered complaint categorization system with RAG pipeline",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(complaints.router, prefix=settings.API_V1_PREFIX)
app.include_router(search.router, prefix=settings.API_V1_PREFIX)


@app.on_event("startup")
async def startup_event():
    """Initialize database on startup."""
    print("Starting up application...")
    
    # Load .env file explicitly BEFORE importing settings
    env_path = Path(__file__).parent.parent.parent / ".env"
    if env_path.exists():
        from dotenv import load_dotenv
        load_dotenv(env_path, override=True)
        print(f"Loaded .env from {env_path}")
    
    # Re-import settings after loading .env
    import importlib
    import app.config
    importlib.reload(app.config)
    from app import config as config_module
    current_settings = config_module.settings
    
    # Check Mistral API key
    api_key = current_settings.MISTRAL_API_KEY
    if not api_key:
        print("Warning: MISTRAL_API_KEY not set. LLM features will not work.")
        print(f"  Checked .env at: {env_path}")
    else:
        print(f"Mistral API key loaded (length: {len(api_key)} chars)")
    
    # Check pgvector extension
    if not check_pgvector_extension():
        print("Warning: pgvector extension not found. Please install it in PostgreSQL.")
    else:
        print("pgvector extension is available.")
    
    # Initialize database (create tables if they don't exist)
    try:
        init_db()
        print("Database initialized successfully.")
    except Exception as e:
        print(f"Error initializing database: {e}")


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Complaint Categorization and RAG System API",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}
