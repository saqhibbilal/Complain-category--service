"""Pydantic schemas for API request/response validation."""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from uuid import UUID


# Request Schemas
class ComplaintCreate(BaseModel):
    """Schema for creating a new complaint."""
    complaint_text: str = Field(..., min_length=10, description="The complaint text")
    product: Optional[str] = None
    sub_product: Optional[str] = None
    company: Optional[str] = None
    state: Optional[str] = None
    zip_code: Optional[str] = None


class ComplaintBatchRequest(BaseModel):
    """Schema for batch complaint ingestion."""
    complaints: List[dict] = Field(..., description="List of complaint objects from JSON")


class SimilarComplaintsRequest(BaseModel):
    """Schema for finding similar complaints."""
    complaint_text: Optional[str] = None
    complaint_id: Optional[str] = None
    top_k: int = Field(default=5, ge=1, le=20, description="Number of similar complaints to retrieve")
    similarity_threshold: Optional[float] = Field(default=0.7, ge=0.0, le=1.0)


# Response Schemas
class ComplaintResponse(BaseModel):
    """Schema for complaint response."""
    id: UUID
    complaint_id: str
    complaint_text: str
    product: Optional[str]
    sub_product: Optional[str]
    issue: Optional[str]
    sub_issue: Optional[str]
    company: Optional[str]
    state: Optional[str]
    zip_code: Optional[str]
    date_received: Optional[datetime]
    date_sent_to_company: Optional[datetime]
    company_response: Optional[str]
    consumer_disputed: Optional[str]
    summary: Optional[str]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class SimilarComplaint(BaseModel):
    """Schema for similar complaint with similarity score."""
    complaint: ComplaintResponse
    similarity_score: float = Field(..., ge=0.0, le=1.0, description="Cosine similarity score")


class SimilarComplaintsResponse(BaseModel):
    """Schema for similar complaints response."""
    query_complaint_id: Optional[str]
    similar_complaints: List[SimilarComplaint]
    total_found: int


class BatchProcessingStatus(BaseModel):
    """Schema for batch processing status."""
    job_id: str
    total_complaints: int
    processed: int
    successful: int
    failed: int
    status: str  # "pending", "processing", "completed", "failed"
    current_batch: Optional[int] = None
    error_message: Optional[str] = None


class StatsResponse(BaseModel):
    """Schema for system statistics."""
    total_complaints: int
    total_products: int
    total_companies: int
    complaints_by_product: dict[str, int]
    complaints_by_state: dict[str, int]


# Internal schemas
class ComplaintData(BaseModel):
    """Schema for parsed complaint data from JSON."""
    complaint_id: str
    complaint_text: str
    product: Optional[str] = None
    sub_product: Optional[str] = None
    issue: Optional[str] = None
    sub_issue: Optional[str] = None
    company: Optional[str] = None
    state: Optional[str] = None
    zip_code: Optional[str] = None
    date_received: Optional[datetime] = None
    date_sent_to_company: Optional[datetime] = None
    company_response: Optional[str] = None
    consumer_disputed: Optional[str] = None
    timely: Optional[str] = None
    consumer_consent_provided: Optional[str] = None
    submitted_via: Optional[str] = None
    company_public_response: Optional[str] = None
    tags: Optional[str] = None
