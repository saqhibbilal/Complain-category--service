"""Complaint processing service."""
from typing import Dict, List, Optional
from sqlalchemy.orm import Session
from datetime import datetime
from app.models import Complaint
from app.schemas import ComplaintData
from app.services.embedding import generate_embedding, generate_embeddings_batch
from app.services.llm import validate_category, generate_summary, categorize_complaint
from app.services.rag import retrieve_similar_complaints
from app.config import settings
import logging

logger = logging.getLogger(__name__)


def parse_complaint_from_json(complaint_json: Dict) -> ComplaintData:
    """
    Parse complaint data from JSON structure (Elasticsearch format).
    
    Args:
        complaint_json: Raw complaint JSON from file
        
    Returns:
        ComplaintData object
    """
    # Extract from _source if present (Elasticsearch format)
    source = complaint_json.get("_source", complaint_json)
    
    # Parse dates
    date_received = None
    date_sent = None
    
    if source.get("date_received"):
        try:
            date_received = datetime.fromisoformat(source["date_received"].replace("Z", "+00:00"))
        except Exception as e:
            logger.warning(f"Error parsing date_received: {e}")
    
    if source.get("date_sent_to_company"):
        try:
            date_sent = datetime.fromisoformat(source["date_sent_to_company"].replace("Z", "+00:00"))
        except Exception as e:
            logger.warning(f"Error parsing date_sent_to_company: {e}")
    
    return ComplaintData(
        complaint_id=str(source.get("complaint_id", "")),
        complaint_text=source.get("complaint_what_happened", ""),
        product=source.get("product"),
        sub_product=source.get("sub_product"),
        issue=source.get("issue"),
        sub_issue=source.get("sub_issue"),
        company=source.get("company"),
        state=source.get("state"),
        zip_code=source.get("zip_code"),
        date_received=date_received,
        date_sent_to_company=date_sent,
        company_response=source.get("company_response"),
        consumer_disputed=source.get("consumer_disputed"),
        timely=source.get("timely"),
        consumer_consent_provided=source.get("consumer_consent_provided"),
        submitted_via=source.get("submitted_via"),
        company_public_response=source.get("company_public_response"),
        tags=source.get("tags")
    )


def process_complaint(
    db: Session,
    complaint_data: ComplaintData,
    use_rag: bool = True,
    validate_existing_categories: bool = True
) -> Complaint:
    """
    Process a single complaint: generate embedding, retrieve similar complaints,
    validate/enhance categories, generate summary, and save to database.
    
    Args:
        db: Database session
        complaint_data: Parsed complaint data
        use_rag: Whether to use RAG for categorization
        validate_existing_categories: Whether to validate existing categories
        
    Returns:
        Saved Complaint object
    """
    # Check if complaint already exists
    existing = db.query(Complaint).filter(
        Complaint.complaint_id == complaint_data.complaint_id
    ).first()
    
    if existing:
        logger.info(f"Complaint {complaint_data.complaint_id} already exists, skipping")
        return existing
    
    # Generate embedding
    logger.info(f"Generating embedding for complaint {complaint_data.complaint_id}")
    try:
        embedding = generate_embedding(complaint_data.complaint_text)
    except Exception as e:
        logger.error(f"Error generating embedding: {e}")
        embedding = None
    
    # Retrieve similar complaints for RAG context
    similar_complaints_texts = []
    if use_rag and embedding:
        try:
            similar_complaints = retrieve_similar_complaints(
                db=db,
                query_embedding=embedding,
                limit=3,  # Use top 3 for context
                exclude_complaint_id=complaint_data.complaint_id
            )
            similar_complaints_texts = [
                comp.complaint_text for comp, _ in similar_complaints
            ]
            logger.info(f"Retrieved {len(similar_complaints_texts)} similar complaints for RAG")
        except Exception as e:
            logger.warning(f"Error retrieving similar complaints: {e}")
    
    # Validate or enhance categories
    product = complaint_data.product
    sub_product = complaint_data.sub_product
    issue = complaint_data.issue
    sub_issue = complaint_data.sub_issue
    
    # If categories exist and validation is enabled, validate them
    if validate_existing_categories and product and sub_product:
        try:
            is_valid = validate_category(
                complaint_data.complaint_text,
                product,
                sub_product
            )
            if not is_valid:
                logger.info(f"Category validation failed for {complaint_data.complaint_id}, recategorizing")
                # Recategorize using RAG
                categories = categorize_complaint(
                    complaint_data.complaint_text,
                    similar_complaints_texts if use_rag else None
                )
                product = categories.get("product") or product
                sub_product = categories.get("sub_product") or sub_product
                issue = categories.get("issue") or issue
                sub_issue = categories.get("sub_issue") or sub_issue
        except Exception as e:
            logger.warning(f"Error validating category: {e}")
    
    # If no categories exist, categorize using LLM with RAG
    elif not product or not sub_product:
        try:
            categories = categorize_complaint(
                complaint_data.complaint_text,
                similar_complaints_texts if use_rag else None
            )
            product = categories.get("product") or product
            sub_product = categories.get("sub_product") or sub_product
            issue = categories.get("issue") or issue
            sub_issue = categories.get("sub_issue") or sub_issue
        except Exception as e:
            logger.error(f"Error categorizing complaint: {e}")
    
    # Generate summary
    summary = None
    try:
        summary = generate_summary(complaint_data.complaint_text)
    except Exception as e:
        logger.warning(f"Error generating summary: {e}")
    
    # Create complaint object
    complaint = Complaint(
        complaint_id=complaint_data.complaint_id,
        complaint_text=complaint_data.complaint_text,
        product=product,
        sub_product=sub_product,
        issue=issue,
        sub_issue=sub_issue,
        company=complaint_data.company,
        state=complaint_data.state,
        zip_code=complaint_data.zip_code,
        date_received=complaint_data.date_received,
        date_sent_to_company=complaint_data.date_sent_to_company,
        company_response=complaint_data.company_response,
        consumer_disputed=complaint_data.consumer_disputed,
        timely=complaint_data.timely,
        consumer_consent_provided=complaint_data.consumer_consent_provided,
        submitted_via=complaint_data.submitted_via,
        company_public_response=complaint_data.company_public_response,
        tags=complaint_data.tags,
        summary=summary,
        embedding=embedding
    )
    
    # Save to database
    db.add(complaint)
    try:
        db.commit()
        db.refresh(complaint)
        logger.info(f"Successfully processed complaint {complaint_data.complaint_id}")
        return complaint
    except Exception as e:
        db.rollback()
        logger.error(f"Error saving complaint {complaint_data.complaint_id}: {e}")
        raise


def process_batch(
    db: Session,
    complaints_json: List[Dict],
    batch_size: int = None,
    use_rag: bool = True
) -> Dict[str, int]:
    """
    Process complaints in batches.
    
    Args:
        db: Database session
        complaints_json: List of complaint JSON objects
        batch_size: Number of complaints to process in each batch
        use_rag: Whether to use RAG for categorization
        
    Returns:
        Dictionary with processing statistics
    """
    if batch_size is None:
        batch_size = settings.BATCH_SIZE
    
    total = len(complaints_json)
    processed = 0
    successful = 0
    failed = 0
    
    logger.info(f"Starting batch processing: {total} complaints, batch size: {batch_size}")
    
    for i in range(0, total, batch_size):
        batch = complaints_json[i:i + batch_size]
        batch_num = (i // batch_size) + 1
        logger.info(f"Processing batch {batch_num}: complaints {i+1}-{min(i+batch_size, total)}")
        
        for complaint_json in batch:
            try:
                # Parse complaint
                complaint_data = parse_complaint_from_json(complaint_json)
                
                # Skip if no complaint text
                if not complaint_data.complaint_text or not complaint_data.complaint_text.strip():
                    logger.warning(f"Skipping complaint {complaint_data.complaint_id}: no text")
                    failed += 1
                    continue
                
                # Process complaint
                process_complaint(db, complaint_data, use_rag=use_rag)
                successful += 1
                
            except Exception as e:
                logger.error(f"Error processing complaint: {e}")
                failed += 1
            
            processed += 1
            
            # Log progress every 10 complaints
            if processed % 10 == 0:
                logger.info(f"Progress: {processed}/{total} ({successful} successful, {failed} failed)")
        
        # Commit after each batch
        try:
            db.commit()
        except Exception as e:
            logger.error(f"Error committing batch {batch_num}: {e}")
            db.rollback()
    
    logger.info(f"Batch processing complete: {processed} processed, {successful} successful, {failed} failed")
    
    return {
        "total": total,
        "processed": processed,
        "successful": successful,
        "failed": failed
    }
