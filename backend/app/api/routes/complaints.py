"""Complaint API routes."""
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, BackgroundTasks
from sqlalchemy.orm import Session
from sqlalchemy import desc, func
from typing import List, Optional
from uuid import UUID
import json
import uuid
from app.database import get_db, SessionLocal
from app.schemas import (
    ComplaintCreate,
    ComplaintResponse,
    ComplaintBatchRequest,
    BatchProcessingStatus
)
from app.models import Complaint
from app.services.complaint import process_complaint, process_batch, parse_complaint_from_json
from app.services.embedding import generate_embedding
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/complaints", tags=["complaints"])

# In-memory batch job tracking (in production, use Redis or database)
_batch_jobs: dict[str, dict] = {}


@router.post("/", response_model=ComplaintResponse, status_code=201)
async def create_complaint(
    complaint: ComplaintCreate,
    db: Session = Depends(get_db),
    use_rag: bool = True
):
    """
    Submit a new complaint for processing.
    
    The complaint will be:
    - Embedded using sentence-transformers
    - Categorized using Mistral API with RAG context
    - Summarized
    - Stored in the database
    """
    try:
        # Convert to ComplaintData format
        from app.schemas import ComplaintData
        complaint_data = ComplaintData(
            complaint_id=str(uuid.uuid4()),  # Generate new ID
            complaint_text=complaint.complaint_text,
            product=complaint.product,
            sub_product=complaint.sub_product,
            company=complaint.company,
            state=complaint.state,
            zip_code=complaint.zip_code
        )
        
        # Process complaint
        processed_complaint = process_complaint(db, complaint_data, use_rag=use_rag)
        
        return ComplaintResponse.model_validate(processed_complaint)
        
    except Exception as e:
        logger.error(f"Error creating complaint: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{complaint_id}", response_model=ComplaintResponse)
async def get_complaint(
    complaint_id: str,
    db: Session = Depends(get_db)
):
    """Get a complaint by ID."""
    complaint = db.query(Complaint).filter(
        Complaint.complaint_id == complaint_id
    ).first()
    
    if not complaint:
        raise HTTPException(status_code=404, detail=f"Complaint {complaint_id} not found")
    
    return ComplaintResponse.model_validate(complaint)


@router.get("/", response_model=List[ComplaintResponse])
async def list_complaints(
    skip: int = 0,
    limit: int = 100,
    product: Optional[str] = None,
    sub_product: Optional[str] = None,
    company: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    List complaints with optional filtering.
    
    Supports pagination and filtering by product, sub_product, and company.
    """
    query = db.query(Complaint)
    
    # Apply filters
    if product:
        query = query.filter(Complaint.product == product)
    if sub_product:
        query = query.filter(Complaint.sub_product == sub_product)
    if company:
        query = query.filter(Complaint.company.ilike(f"%{company}%"))
    
    # Order by date received (newest first)
    query = query.order_by(desc(Complaint.date_received))
    
    # Apply pagination
    complaints = query.offset(skip).limit(limit).all()
    
    return [ComplaintResponse.model_validate(c) for c in complaints]


@router.post("/batch", status_code=202)
async def ingest_batch(
    background_tasks: BackgroundTasks,
    file: Optional[UploadFile] = File(None),
    json_data: Optional[str] = None,
    db: Session = Depends(get_db),
    use_rag: bool = True
):
    """
    Ingest complaints from JSON file or JSON data.
    
    Accepts either:
    - File upload (JSON file)
    - JSON string in request body
    
    Returns a job ID for tracking batch processing status.
    """
    # Generate job ID
    job_id = str(uuid.uuid4())
    
    # Initialize job status
    _batch_jobs[job_id] = {
        "job_id": job_id,
        "total_complaints": 0,
        "processed": 0,
        "successful": 0,
        "failed": 0,
        "status": "pending",
        "current_batch": None,
        "error_message": None
    }
    
    try:
        # Parse input
        complaints_json = []
        
        if file:
            # Read from uploaded file
            content = await file.read()
            complaints_json = json.loads(content.decode('utf-8'))
        elif json_data:
            # Parse JSON string
            complaints_json = json.loads(json_data)
        else:
            raise HTTPException(status_code=400, detail="Either file or json_data must be provided")
        
        # Handle Elasticsearch format (array of objects with _source)
        if isinstance(complaints_json, list) and len(complaints_json) > 0:
            # Check if it's Elasticsearch format
            if "_source" in complaints_json[0]:
                # Already in correct format
                pass
            else:
                # Assume it's a list of complaint objects
                pass
        
        total = len(complaints_json)
        _batch_jobs[job_id]["total_complaints"] = total
        _batch_jobs[job_id]["status"] = "processing"
        
        # Process in background (don't pass db session, create new one)
        background_tasks.add_task(
            process_batch_background,
            job_id=job_id,
            complaints_json=complaints_json,
            use_rag=use_rag
        )
        
        return {
            "job_id": job_id,
            "status": "processing",
            "total_complaints": total,
            "message": "Batch processing started"
        }
        
    except json.JSONDecodeError as e:
        _batch_jobs[job_id]["status"] = "failed"
        _batch_jobs[job_id]["error_message"] = f"Invalid JSON: {str(e)}"
        raise HTTPException(status_code=400, detail=f"Invalid JSON format: {str(e)}")
    except Exception as e:
        _batch_jobs[job_id]["status"] = "failed"
        _batch_jobs[job_id]["error_message"] = str(e)
        logger.error(f"Error starting batch processing: {e}")
        raise HTTPException(status_code=500, detail=str(e))


def process_batch_background(
    job_id: str,
    complaints_json: List[dict],
    use_rag: bool
):
    """Background task for batch processing."""
    # Create new database session for background task
    db = SessionLocal()
    try:
        stats = process_batch(db, complaints_json, use_rag=use_rag)
        
        _batch_jobs[job_id].update({
            "processed": stats["processed"],
            "successful": stats["successful"],
            "failed": stats["failed"],
            "status": "completed"
        })
        
    except Exception as e:
        logger.error(f"Error in batch processing job {job_id}: {e}")
        _batch_jobs[job_id].update({
            "status": "failed",
            "error_message": str(e)
        })
    finally:
        db.close()


@router.get("/batch/{job_id}/status", response_model=BatchProcessingStatus)
async def get_batch_status(job_id: str):
    """Get the status of a batch processing job."""
    if job_id not in _batch_jobs:
        raise HTTPException(status_code=404, detail=f"Job {job_id} not found")
    
    job_status = _batch_jobs[job_id]
    return BatchProcessingStatus(**job_status)
