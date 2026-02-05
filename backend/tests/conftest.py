"""Pytest configuration and fixtures."""
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Base
from app.config import settings
import os

# Use test database
TEST_DATABASE_URL = os.getenv("TEST_DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/complaints_test_db")


@pytest.fixture(scope="session")
def test_engine():
    """Create test database engine."""
    engine = create_engine(TEST_DATABASE_URL)
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def db_session(test_engine):
    """Create a database session for testing."""
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
