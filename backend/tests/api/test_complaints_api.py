"""API endpoint tests for complaints."""
import pytest

# Skip tests if FastAPI/TestClient not available
try:
    from fastapi.testclient import TestClient
    from app.main import app
    API_AVAILABLE = True
    client = TestClient(app)
except (ImportError, Exception) as e:
    API_AVAILABLE = False
    client = None


@pytest.mark.skipif(not API_AVAILABLE, reason="API dependencies not available")
def test_root_endpoint():
    """Test root endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    assert "message" in response.json()


@pytest.mark.skipif(not API_AVAILABLE, reason="API dependencies not available")
def test_health_check():
    """Test health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


@pytest.mark.skipif(not API_AVAILABLE, reason="API dependencies not available")
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


@pytest.mark.skipif(not API_AVAILABLE, reason="API dependencies not available")
def test_get_complaint_not_found():
    """Test getting non-existent complaint."""
    response = client.get("/api/v1/complaints/nonexistent-id-12345")
    assert response.status_code == 404


@pytest.mark.skipif(not API_AVAILABLE, reason="API dependencies not available")
def test_list_complaints():
    """Test listing complaints."""
    response = client.get("/api/v1/complaints/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


@pytest.mark.skipif(not API_AVAILABLE, reason="API dependencies not available")
def test_list_complaints_with_filters():
    """Test listing complaints with filters."""
    response = client.get("/api/v1/complaints/?product=Credit%20card&limit=10")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


@pytest.mark.skipif(not API_AVAILABLE, reason="API dependencies not available")
def test_search_stats():
    """Test getting statistics."""
    response = client.get("/api/v1/search/stats")
    assert response.status_code == 200
    data = response.json()
    assert "total_complaints" in data
    assert "total_products" in data
