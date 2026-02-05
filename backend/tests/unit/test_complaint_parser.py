"""Unit tests for complaint parsing."""
import pytest
from datetime import datetime
from app.services.complaint import parse_complaint_from_json
from app.schemas import ComplaintData


def test_parse_complaint_elasticsearch_format():
    """Test parsing complaint from Elasticsearch format."""
    complaint_json = {
        "_source": {
            "complaint_id": "12345",
            "complaint_what_happened": "Test complaint text",
            "product": "Credit card",
            "sub_product": "General-purpose credit card",
            "company": "Test Bank",
            "state": "NY",
            "date_received": "2024-01-15T12:00:00-05:00"
        }
    }
    
    result = parse_complaint_from_json(complaint_json)
    
    assert isinstance(result, ComplaintData)
    assert result.complaint_id == "12345"
    assert result.complaint_text == "Test complaint text"
    assert result.product == "Credit card"
    assert result.company == "Test Bank"
    assert result.state == "NY"


def test_parse_complaint_direct_format():
    """Test parsing complaint from direct format (no _source)."""
    complaint_json = {
        "complaint_id": "67890",
        "complaint_what_happened": "Direct format complaint",
        "product": "Mortgage"
    }
    
    result = parse_complaint_from_json(complaint_json)
    
    assert result.complaint_id == "67890"
    assert result.complaint_text == "Direct format complaint"
    assert result.product == "Mortgage"


def test_parse_complaint_with_missing_fields():
    """Test parsing complaint with missing optional fields."""
    complaint_json = {
        "_source": {
            "complaint_id": "99999",
            "complaint_what_happened": "Minimal complaint"
        }
    }
    
    result = parse_complaint_from_json(complaint_json)
    
    assert result.complaint_id == "99999"
    assert result.product is None
    assert result.company is None
