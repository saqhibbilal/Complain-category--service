"""Search API routes."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func, distinct
from typing import List
from app.database import get_db
from app.schemas import (
    SimilarComplaintsRequest,
    SimilarComplaintsResponse,
    SimilarComplaint,
    ComplaintResponse,
    StatsResponse
)
from app.models import Complaint
from app.services.rag import retrieve_similar_complaints, retrieve_similar_by_complaint_id
from app.services.embedding import generate_embedding
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/search", tags=["search"])


@router.post("/similar", response_model=SimilarComplaintsResponse)
async def find_similar_complaints(
    request: SimilarComplaintsRequest,
    db: Session = Depends(get_db)
):
    """
    Find similar complaints using vector similarity search.
    
    Accepts either:
    - complaint_text: Generate embedding and find similar
    - complaint_id: Find similar to existing complaint
    """
    try:
        if request.complaint_id:
            # Find similar by complaint ID
            similar_complaints = retrieve_similar_by_complaint_id(
                db=db,
                complaint_id=request.complaint_id,
                limit=request.top_k,
                similarity_threshold=request.similarity_threshold
            )
            query_complaint_id = request.complaint_id
            
        elif request.complaint_text:
            # Generate embedding and find similar
            query_embedding = generate_embedding(request.complaint_text)
            similar_complaints = retrieve_similar_complaints(
                db=db,
                query_embedding=query_embedding,
                limit=request.top_k,
                similarity_threshold=request.similarity_threshold
            )
            query_complaint_id = None
            
        else:
            raise HTTPException(
                status_code=400,
                detail="Either complaint_text or complaint_id must be provided"
            )
        
        # Format response
        similar_complaints_list = [
            SimilarComplaint(
                complaint=ComplaintResponse.model_validate(complaint),
                similarity_score=score
            )
            for complaint, score in similar_complaints
        ]
        
        return SimilarComplaintsResponse(
            query_complaint_id=query_complaint_id,
            similar_complaints=similar_complaints_list,
            total_found=len(similar_complaints_list)
        )
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error finding similar complaints: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats", response_model=StatsResponse)
async def get_stats(db: Session = Depends(get_db)):
    """
    Get system statistics.
    
    Returns:
    - Total complaints
    - Total unique products
    - Total unique companies
    - Complaints by product
    - Complaints by state
    """
    try:
        # Total complaints
        total_complaints = db.query(func.count(Complaint.id)).scalar()
        
        # Total unique products
        total_products = db.query(func.count(distinct(Complaint.product))).scalar()
        
        # Total unique companies
        total_companies = db.query(func.count(distinct(Complaint.company))).scalar()
        
        # Complaints by product
        product_counts = db.query(
            Complaint.product,
            func.count(Complaint.id).label('count')
        ).group_by(Complaint.product).all()
        
        complaints_by_product = {
            product: count for product, count in product_counts if product
        }
        
        # Complaints by state
        state_counts = db.query(
            Complaint.state,
            func.count(Complaint.id).label('count')
        ).group_by(Complaint.state).all()
        
        complaints_by_state = {
            state: count for state, count in state_counts if state
        }
        
        return StatsResponse(
            total_complaints=total_complaints or 0,
            total_products=total_products or 0,
            total_companies=total_companies or 0,
            complaints_by_product=complaints_by_product,
            complaints_by_state=complaints_by_state
        )
        
    except Exception as e:
        logger.error(f"Error getting stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))
