"""RAG service for vector similarity search."""
from typing import List, Tuple, Optional
from sqlalchemy.orm import Session
from sqlalchemy import text
from pgvector.sqlalchemy import Vector
import numpy as np
from app.models import Complaint
from app.config import settings
import logging

logger = logging.getLogger(__name__)


def retrieve_similar_complaints(
    db: Session,
    query_embedding: List[float],
    limit: int = None,
    similarity_threshold: float = None,
    exclude_complaint_id: Optional[str] = None
) -> List[Tuple[Complaint, float]]:
    """
    Retrieve similar complaints using vector similarity search.
    
    Args:
        db: Database session
        query_embedding: Query embedding vector
        limit: Maximum number of results (defaults to SIMILARITY_TOP_K)
        similarity_threshold: Minimum similarity score (defaults to SIMILARITY_THRESHOLD)
        exclude_complaint_id: Complaint ID to exclude from results
        
    Returns:
        List of tuples (Complaint, similarity_score) sorted by similarity (descending)
    """
    if limit is None:
        limit = settings.SIMILARITY_TOP_K
    if similarity_threshold is None:
        similarity_threshold = settings.SIMILARITY_THRESHOLD
    
    # Convert list to numpy array and ensure it's the right shape
    query_vector = np.array(query_embedding, dtype=np.float32)
    
    # Build query
    query = db.query(
        Complaint,
        (1 - Complaint.embedding.cosine_distance(query_vector)).label('similarity')
    ).filter(
        Complaint.embedding.isnot(None)  # Only complaints with embeddings
    )
    
    # Exclude specific complaint if provided
    if exclude_complaint_id:
        query = query.filter(Complaint.complaint_id != exclude_complaint_id)
    
    # Apply similarity threshold and order by similarity
    query = query.having(
        (1 - Complaint.embedding.cosine_distance(query_vector)) >= similarity_threshold
    ).order_by(
        Complaint.embedding.cosine_distance(query_vector)
    ).limit(limit)
    
    try:
        results = query.all()
        # Extract complaints and similarity scores
        similar_complaints = [
            (complaint, float(similarity))
            for complaint, similarity in results
        ]
        return similar_complaints
    except Exception as e:
        logger.error(f"Error retrieving similar complaints: {e}")
        # Fallback to simple query if vector operations fail
        return _fallback_similarity_search(db, query_embedding, limit, exclude_complaint_id)


def retrieve_similar_by_complaint_id(
    db: Session,
    complaint_id: str,
    limit: int = None,
    similarity_threshold: float = None
) -> List[Tuple[Complaint, float]]:
    """
    Retrieve similar complaints by complaint ID.
    
    Args:
        db: Database session
        complaint_id: ID of the complaint to find similar ones for
        limit: Maximum number of results
        similarity_threshold: Minimum similarity score
        
    Returns:
        List of tuples (Complaint, similarity_score)
    """
    # Get the complaint
    complaint = db.query(Complaint).filter(Complaint.complaint_id == complaint_id).first()
    
    if not complaint:
        raise ValueError(f"Complaint with ID {complaint_id} not found")
    
    if not complaint.embedding:
        logger.warning(f"Complaint {complaint_id} has no embedding")
        return []
    
    # Convert embedding to list
    query_embedding = complaint.embedding.tolist() if hasattr(complaint.embedding, 'tolist') else list(complaint.embedding)
    
    # Retrieve similar complaints (excluding the query complaint itself)
    return retrieve_similar_complaints(
        db=db,
        query_embedding=query_embedding,
        limit=limit,
        similarity_threshold=similarity_threshold,
        exclude_complaint_id=complaint_id
    )


def _fallback_similarity_search(
    db: Session,
    query_embedding: List[float],
    limit: int,
    exclude_complaint_id: Optional[str]
) -> List[Tuple[Complaint, float]]:
    """Fallback similarity search using raw SQL if ORM fails."""
    try:
        # Convert embedding to PostgreSQL array format
        embedding_str = "[" + ",".join(map(str, query_embedding)) + "]"
        
        sql = f"""
        SELECT 
            id, complaint_id, complaint_text, product, sub_product, 
            issue, sub_issue, company, state, zip_code, date_received,
            date_sent_to_company, company_response, consumer_disputed,
            summary, created_at, updated_at,
            1 - (embedding <=> '{embedding_str}'::vector) as similarity
        FROM complaints
        WHERE embedding IS NOT NULL
        """
        
        if exclude_complaint_id:
            sql += f" AND complaint_id != '{exclude_complaint_id}'"
        
        sql += f"""
        AND (1 - (embedding <=> '{embedding_str}'::vector)) >= {settings.SIMILARITY_THRESHOLD}
        ORDER BY embedding <=> '{embedding_str}'::vector
        LIMIT {limit}
        """
        
        result = db.execute(text(sql))
        similar_complaints = []
        
        for row in result:
            complaint = Complaint(
                id=row.id,
                complaint_id=row.complaint_id,
                complaint_text=row.complaint_text,
                product=row.product,
                sub_product=row.sub_product,
                issue=row.issue,
                sub_issue=row.sub_issue,
                company=row.company,
                state=row.state,
                zip_code=row.zip_code,
                date_received=row.date_received,
                date_sent_to_company=row.date_sent_to_company,
                company_response=row.company_response,
                consumer_disputed=row.consumer_disputed,
                summary=row.summary,
                created_at=row.created_at,
                updated_at=row.updated_at
            )
            similar_complaints.append((complaint, float(row.similarity)))
        
        return similar_complaints
        
    except Exception as e:
        logger.error(f"Fallback similarity search failed: {e}")
        return []
