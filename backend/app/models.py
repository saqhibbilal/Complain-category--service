"""SQLAlchemy database models."""
from sqlalchemy import Column, String, Text, DateTime, Index, Float
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from pgvector.sqlalchemy import Vector
import uuid
from app.database import Base


class Complaint(Base):
    """Complaint model with vector embedding support."""
    __tablename__ = "complaints"
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Original complaint ID from JSON
    complaint_id = Column(String(50), unique=True, nullable=False, index=True)
    
    # Complaint text (main content)
    complaint_text = Column(Text, nullable=False)
    
    # Category fields (from JSON, validated/enhanced by AI)
    product = Column(String(100), nullable=True, index=True)
    sub_product = Column(String(200), nullable=True, index=True)
    issue = Column(String(200), nullable=True)
    sub_issue = Column(String(200), nullable=True)
    
    # Company and location
    company = Column(String(200), nullable=True)
    state = Column(String(2), nullable=True)
    zip_code = Column(String(10), nullable=True)
    
    # Dates
    date_received = Column(DateTime(timezone=True), nullable=True)
    date_sent_to_company = Column(DateTime(timezone=True), nullable=True)
    
    # Response and dispute info
    company_response = Column(String(200), nullable=True)
    consumer_disputed = Column(String(50), nullable=True)
    timely = Column(String(10), nullable=True)
    consumer_consent_provided = Column(String(50), nullable=True)
    submitted_via = Column(String(50), nullable=True)
    company_public_response = Column(Text, nullable=True)
    tags = Column(String(200), nullable=True)
    
    # AI-generated content
    summary = Column(Text, nullable=True)
    
    # Vector embedding (384 dimensions for all-MiniLM-L6-v2)
    embedding = Column(Vector(384), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Indexes
    __table_args__ = (
        # Vector similarity index (IVFFlat for faster queries)
        Index(
            'idx_complaint_embedding',
            embedding,
            postgresql_using='ivfflat',
            postgresql_with={'lists': 100}
        ),
        # Composite index for filtering
        Index('idx_product_subproduct', product, sub_product),
    )
    
    def __repr__(self):
        return f"<Complaint(id={self.complaint_id}, product={self.product})>"
