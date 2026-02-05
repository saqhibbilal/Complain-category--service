"""Validate JSON file structure before ingestion."""
import json
import sys
from pathlib import Path
from typing import List, Dict
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def validate_json_structure(file_path: str) -> Dict:
    """
    Validate JSON file structure and return statistics.
    
    Returns:
        Dictionary with validation results
    """
    logger.info(f"Validating JSON file: {file_path}")
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except FileNotFoundError:
        return {"valid": False, "error": "File not found"}
    except json.JSONDecodeError as e:
        return {"valid": False, "error": f"Invalid JSON: {e}"}
    
    if not isinstance(data, list):
        return {"valid": False, "error": "JSON must be an array"}
    
    stats = {
        "valid": True,
        "total_complaints": len(data),
        "valid_complaints": 0,
        "invalid_complaints": 0,
        "missing_fields": {},
        "sample_complaint": None
    }
    
    required_fields = ["complaint_id", "complaint_what_happened"]
    optional_fields = ["product", "sub_product", "company", "state"]
    
    for i, complaint_json in enumerate(data[:100]):  # Check first 100
        source = complaint_json.get("_source", complaint_json)
        
        # Check required fields
        missing = []
        for field in required_fields:
            if not source.get(field):
                missing.append(field)
        
        if not missing:
            stats["valid_complaints"] += 1
            if stats["sample_complaint"] is None:
                stats["sample_complaint"] = {
                    "complaint_id": source.get("complaint_id"),
                    "has_text": bool(source.get("complaint_what_happened")),
                    "product": source.get("product"),
                    "sub_product": source.get("sub_product")
                }
        else:
            stats["invalid_complaints"] += 1
            for field in missing:
                stats["missing_fields"][field] = stats["missing_fields"].get(field, 0) + 1
    
    # Estimate total valid/invalid
    if stats["total_complaints"] > 100:
        ratio = stats["valid_complaints"] / 100
        stats["estimated_valid"] = int(stats["total_complaints"] * ratio)
        stats["estimated_invalid"] = stats["total_complaints"] - stats["estimated_valid"]
    
    logger.info(f"Validation complete: {stats['valid_complaints']} valid out of 100 checked")
    return stats


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Usage: python validate_json.py <json_file_path>")
        sys.exit(1)
    
    file_path = sys.argv[1]
    result = validate_json_structure(file_path)
    
    if not result["valid"]:
        print(f"❌ Validation failed: {result['error']}")
        sys.exit(1)
    
    print("\n" + "=" * 60)
    print("JSON VALIDATION REPORT")
    print("=" * 60)
    print(f"Total complaints: {result['total_complaints']}")
    print(f"Valid (sample): {result['valid_complaints']}/100")
    if 'estimated_valid' in result:
        print(f"Estimated valid: ~{result['estimated_valid']}")
        print(f"Estimated invalid: ~{result['estimated_invalid']}")
    print(f"\nMissing fields:")
    for field, count in result['missing_fields'].items():
        print(f"  - {field}: {count} occurrences")
    
    if result['sample_complaint']:
        print(f"\nSample complaint:")
        print(f"  ID: {result['sample_complaint']['complaint_id']}")
        print(f"  Has text: {result['sample_complaint']['has_text']}")
        print(f"  Product: {result['sample_complaint']['product']}")
        print(f"  Sub-product: {result['sample_complaint']['sub_product']}")
    
    print("=" * 60)
    
    if result['valid_complaints'] == 0:
        print("❌ No valid complaints found in sample!")
        sys.exit(1)
    else:
        print("✅ JSON file structure is valid")
        sys.exit(0)


if __name__ == "__main__":
    main()
