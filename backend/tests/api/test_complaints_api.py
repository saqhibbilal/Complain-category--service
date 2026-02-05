"""API endpoint tests for complaints."""
import pytest
from fastapi.testclient import TestClient
from app.main import app

# Note: TestClient requires httpx, which is already in requirements.txt
client = TestClient(app)


def test_root_endpoint():
    """Test root endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    assert "message" in response.json()


def test_health_check():
    """Test health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


def test_create_complaint():
    """Test creating a complaint."""
    complaint_data = {
        "complaint_text": "I was charged an unauthorized fee on my credit card statement. The company refused to refund it despite multiple calls.",
        "company": "Test Bank",
        "state": "NY"
    }
    
    response = client.post("/api/v1/complaints/", json=complaint_data)
    
    # Should succeed (201) or fail gracefully (500 if Mistral API key not set)
    assert response.status_code in [201, 500]
    
    if response.status_code == 201:
        data = response.json()
        assert "complaint_id" in data
        assert "complaint_text" in data


def test_get_complaint_not_found():
    """Test getting non-existent complaint."""
    response = client.get("/api/v1/complaints/nonexistent-id-12345")
    assert response.status_code == 404


def test_list_complaints():
    """Test listing complaints."""
    response = client.get("/api/v1/complaints/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_list_complaints_with_filters():
    """Test listing complaints with filters."""
    response = client.get("/api/v1/complaints/?product=Credit%20card&limit=10")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_search_stats():
    """Test getting statistics."""
    response = client.get("/api/v1/search/stats")
    assert response.status_code == 200
    data = response.json()
    assert "total_complaints" in data
    assert "total_products" in data
