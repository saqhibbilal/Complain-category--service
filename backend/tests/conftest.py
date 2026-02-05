"""Pytest configuration and fixtures."""
import pytest
import os


# Use test database
TEST_DATABASE_URL = os.getenv("TEST_DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/complaints_test_db")


@pytest.fixture(scope="session")
def test_engine():
    """Create test database engine."""
    try:
        from sqlalchemy import create_engine
        from sqlalchemy.ext.declarative import declarative_base
    except ImportError as e:
        pytest.skip(f"Database dependencies not available: {e}")
    
    # Try to import Base from app.database, but if that fails (due to psycopg2 missing),
    # create our own Base. This allows tests to run even if database isn't fully configured.
    try:
        from app.database import Base
        # Import models to ensure they're registered with Base
        try:
            from app.models import Complaint  # noqa: F401
        except ImportError:
            pass
    except ImportError:
        # If app.database can't be imported, create a minimal Base
        # Note: This means models won't be available, but some tests can still run
        Base = declarative_base()
    
    try:
        engine = create_engine(TEST_DATABASE_URL)
        Base.metadata.create_all(bind=engine)
        yield engine
        Base.metadata.drop_all(bind=engine)
    except Exception as e:
        pytest.skip(f"Database not available: {e}")


@pytest.fixture(scope="function")
def db_session(test_engine):
    """Create a database session for testing."""
    try:
        from sqlalchemy.orm import sessionmaker
    except ImportError as e:
        pytest.skip(f"Database dependencies not available: {e}")
    
    SessionLocal = sessionmaker(bind=test_engine)
    session = SessionLocal()
    try:
        yield session
    finally:
        session.rollback()
        session.close()


@pytest.fixture
def mock_mistral_client(monkeypatch):
    """Mock Mistral client for testing."""
    class MockMistralClient:
        def __init__(self, *args, **kwargs):
            pass
        
        class chat:
            class complete:
                @staticmethod
                def __call__(*args, **kwargs):
                    class MockResponse:
                        class Choice:
                            class Message:
                                content = '{"product": "Credit card", "sub_product": "General-purpose credit card", "issue": "Problem with a purchase", "sub_issue": "Unauthorized charge"}'
                            message = Message()
                        choices = [Choice()]
                    return MockResponse()
                complete = __call__
    
    monkeypatch.setattr("app.services.llm.Mistral", MockMistralClient)
    return MockMistralClient
