"""Database connection and session management."""
from sqlalchemy import create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.config import settings

# Create database engine
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()


def get_db():
    """Dependency for getting database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Initialize database: enable pgvector extension and create tables."""
    with engine.connect() as conn:
        # Enable pgvector extension
        conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
        conn.commit()
    
    # Create all tables
    Base.metadata.create_all(bind=engine)


def check_pgvector_extension():
    """Check if pgvector extension is available."""
    try:
        with engine.connect() as conn:
            result = conn.execute(
                text("SELECT * FROM pg_extension WHERE extname = 'vector'")
            )
            return result.fetchone() is not None
    except Exception as e:
        print(f"Error checking pgvector extension: {e}")
        return False
