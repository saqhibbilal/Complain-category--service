"""Error tracking and reporting for complaint processing."""
from typing import Dict, List, Optional
from datetime import datetime
import json
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class ErrorTracker:
    """Track errors during complaint processing."""
    
    def __init__(self):
        self.errors: List[Dict] = []
        self.warnings: List[Dict] = []
    
    def log_error(
        self,
        complaint_id: str,
        error_message: str,
        error_type: str = "processing_error",
        complaint_data: Optional[Dict] = None
    ):
        """Log an error for a complaint."""
        error_entry = {
            "complaint_id": complaint_id,
            "error_type": error_type,
            "error_message": str(error_message),
            "timestamp": datetime.now().isoformat(),
            "complaint_data": complaint_data
        }
        self.errors.append(error_entry)
        logger.error(f"Error processing complaint {complaint_id}: {error_message}")
    
    def log_warning(
        self,
        complaint_id: str,
        warning_message: str,
        warning_type: str = "validation_warning"
    ):
        """Log a warning for a complaint."""
        warning_entry = {
            "complaint_id": complaint_id,
            "warning_type": warning_type,
            "warning_message": str(warning_message),
            "timestamp": datetime.now().isoformat()
        }
        self.warnings.append(warning_entry)
        logger.warning(f"Warning for complaint {complaint_id}: {warning_message}")
    
    def get_error_summary(self) -> Dict:
        """Get summary of errors."""
        error_types = {}
        for error in self.errors:
            error_type = error["error_type"]
            error_types[error_type] = error_types.get(error_type, 0) + 1
        
        return {
            "total_errors": len(self.errors),
            "total_warnings": len(self.warnings),
            "errors_by_type": error_types
        }
    
    def save_error_report(self, file_path: Optional[str] = None):
        """Save error report to JSON file."""
        if file_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            file_path = f"error_report_{timestamp}.json"
        
        report = {
            "summary": self.get_error_summary(),
            "errors": self.errors,
            "warnings": self.warnings,
            "generated_at": datetime.now().isoformat()
        }
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Error report saved to: {file_path}")
        return file_path
    
    def clear(self):
        """Clear all errors and warnings."""
        self.errors.clear()
        self.warnings.clear()


# Global error tracker instance
_global_tracker: Optional[ErrorTracker] = None


def get_error_tracker() -> ErrorTracker:
    """Get global error tracker instance."""
    global _global_tracker
    if _global_tracker is None:
        _global_tracker = ErrorTracker()
    return _global_tracker


def reset_error_tracker():
    """Reset global error tracker."""
    global _global_tracker
    _global_tracker = ErrorTracker()
