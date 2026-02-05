"""Standalone script for ingesting complaints from JSON file."""
import json
import sys
import os
from pathlib import Path
from typing import List, Dict
import logging
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.database import SessionLocal, init_db, check_pgvector_extension
from app.services.complaint import process_batch, parse_complaint_from_json
from app.services.error_tracking import get_error_tracker, reset_error_tracker
from app.config import settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f'ingestion_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


def load_json_file(file_path: str) -> List[Dict]:
    """
    Load and parse JSON file.
    
    Supports:
    - Array of complaint objects
    - Elasticsearch format (array with _source)
    """
    logger.info(f"Loading JSON file: {file_path}")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    if not isinstance(data, list):
        raise ValueError("JSON file must contain an array of complaints")
    
    logger.info(f"Loaded {len(data)} complaints from file")
    return data


def validate_complaint_data(complaint_json: Dict) -> bool:
    """Validate that complaint has required fields."""
    source = complaint_json.get("_source", complaint_json)
    
    # Check for complaint_id or complaint_what_happened
    has_id = bool(source.get("complaint_id"))
    has_text = bool(source.get("complaint_what_happened"))
    
    if not has_id:
        logger.warning(f"Complaint missing complaint_id: {source.get('complaint_id', 'unknown')}")
    
    if not has_text:
        logger.warning(f"Complaint {source.get('complaint_id', 'unknown')} missing complaint_what_happened")
    
    return has_id and has_text


def preprocess_complaints(complaints_json: List[Dict]) -> List[Dict]:
    """
    Preprocess complaints: validate, filter invalid ones.
    
    Returns:
        Tuple of (valid_complaints, invalid_count)
    """
    valid_complaints = []
    invalid_count = 0
    
    for complaint_json in complaints_json:
        if validate_complaint_data(complaint_json):
            valid_complaints.append(complaint_json)
        else:
            invalid_count += 1
    
    logger.info(f"Preprocessing complete: {len(valid_complaints)} valid, {invalid_count} invalid")
    return valid_complaints, invalid_count


def ingest_file(
    file_path: str,
    batch_size: int = None,
    use_rag: bool = True,
    skip_existing: bool = True
):
    """
    Ingest complaints from JSON file.
    
    Args:
        file_path: Path to JSON file
        batch_size: Number of complaints per batch
        use_rag: Whether to use RAG for categorization
        skip_existing: Skip complaints that already exist in database
    """
    if batch_size is None:
        batch_size = settings.BATCH_SIZE
    
    # Load JSON file
    try:
        complaints_json = load_json_file(file_path)
    except FileNotFoundError:
        logger.error(f"File not found: {file_path}")
        return
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON file: {e}")
        return
    except Exception as e:
        logger.error(f"Error loading file: {e}")
        return
    
    if not complaints_json:
        logger.warning("No complaints found in file")
        return
    
    # Preprocess complaints
    valid_complaints, invalid_count = preprocess_complaints(complaints_json)
    
    if not valid_complaints:
        logger.error("No valid complaints to process")
        return
    
    # Reset error tracker
    reset_error_tracker()
    error_tracker = get_error_tracker()
    
    # Initialize database
    logger.info("Initializing database...")
    if not check_pgvector_extension():
        logger.warning("pgvector extension not found. Some features may not work.")
    
    init_db()
    
    # Create database session
    db = SessionLocal()
    
    try:
        logger.info(f"Starting ingestion: {len(valid_complaints)} complaints")
        logger.info(f"Batch size: {batch_size}, Use RAG: {use_rag}")
        
        # Process batch
        stats = process_batch(
            db=db,
            complaints_json=valid_complaints,
            batch_size=batch_size,
            use_rag=use_rag
        )
        
        # Get error summary
        error_summary = error_tracker.get_error_summary()
        
        # Print summary
        logger.info("=" * 60)
        logger.info("INGESTION SUMMARY")
        logger.info("=" * 60)
        logger.info(f"Total complaints in file: {len(complaints_json)}")
        logger.info(f"Valid complaints: {len(valid_complaints)}")
        logger.info(f"Invalid complaints: {invalid_count}")
        logger.info(f"Processed: {stats['processed']}")
        logger.info(f"Successful: {stats['successful']}")
        logger.info(f"Failed: {stats['failed']}")
        logger.info("")
        logger.info("Error Summary:")
        logger.info(f"  Total errors: {error_summary['total_errors']}")
        logger.info(f"  Total warnings: {error_summary['total_warnings']}")
        if error_summary['errors_by_type']:
            logger.info("  Errors by type:")
            for error_type, count in error_summary['errors_by_type'].items():
                logger.info(f"    - {error_type}: {count}")
        logger.info("=" * 60)
        
        # Save error report if there are errors
        if error_summary['total_errors'] > 0 or error_summary['total_warnings'] > 0:
            report_path = error_tracker.save_error_report()
            logger.info(f"Error report saved to: {report_path}")
        
        if stats['failed'] > 0:
            logger.warning(f"{stats['failed']} complaints failed to process. Check error report for details.")
        
    except Exception as e:
        logger.error(f"Error during ingestion: {e}", exc_info=True)
        db.rollback()
        error_tracker.log_error("system", str(e), "system_error")
        error_tracker.save_error_report()
    finally:
        db.close()


def main():
    """Main entry point for the ingestion script."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Ingest complaints from JSON file")
    parser.add_argument(
        "file_path",
        type=str,
        help="Path to JSON file containing complaints"
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=None,
        help=f"Number of complaints per batch (default: {settings.BATCH_SIZE})"
    )
    parser.add_argument(
        "--no-rag",
        action="store_true",
        help="Disable RAG for categorization"
    )
    parser.add_argument(
        "--skip-existing",
        action="store_true",
        default=True,
        help="Skip complaints that already exist in database"
    )
    
    args = parser.parse_args()
    
    # Resolve file path
    file_path = Path(args.file_path)
    if not file_path.is_absolute():
        # Try relative to project root
        project_root = Path(__file__).parent.parent.parent
        file_path = project_root / file_path
    
    if not file_path.exists():
        logger.error(f"File not found: {file_path}")
        sys.exit(1)
    
    # Run ingestion
    ingest_file(
        file_path=str(file_path),
        batch_size=args.batch_size,
        use_rag=not args.no_rag,
        skip_existing=args.skip_existing
    )


if __name__ == "__main__":
    main()
