"""Integration tests for complaint processing pipeline."""
import pytest
from app.services.complaint import process_complaint, parse_complaint_from_json
from app.schemas import ComplaintData


@pytest.mark.integration
def test_complaint_processing_pipeline(db_session, mock_mistral_client):
    """Test full complaint processing pipeline."""
    complaint_data = ComplaintData(
        complaint_id="test-123",
        complaint_text="I was charged an unauthorized fee on my credit card. The company refused to refund it.",
        product=None,
        sub_product=None
    )
    
    # Process complaint (will use mocked Mistral client)
    result = process_complaint(
        db=db_session,
        complaint_data=complaint_data,
        use_rag=False,  # Disable RAG for faster testing
        validate_existing_categories=False
    )
    
    assert result is not None
    assert result.complaint_id == "test-123"
    assert result.embedding is not None  # Embedding should be generated


@pytest.mark.integration
def test_complaint_already_exists(db_session):
    """Test that duplicate complaints are skipped."""
    complaint_data = ComplaintData(
        complaint_id="duplicate-test",
        complaint_text="Duplicate complaint test"
    )
    
    # Process first time
    result1 = process_complaint(db_session, complaint_data, use_rag=False)
    
    # Process second time (should return existing)
    result2 = process_complaint(db_session, complaint_data, use_rag=False)
    
    assert result1.id == result2.id  # Same complaint returned
