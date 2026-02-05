# Ingestion Scripts

Scripts for ingesting and validating complaint data.

## Scripts

### `ingest_complaints.py`

Main script for ingesting complaints from JSON file into the database.

**Usage:**
```bash
# Basic usage
python scripts/ingest_complaints.py data/complaints-2024-08-15_20_15.json

# With options
python scripts/ingest_complaints.py data/complaints.json \
    --batch-size 50 \
    --no-rag \
    --skip-existing
```

**Options:**
- `--batch-size`: Number of complaints per batch (default: from config)
- `--no-rag`: Disable RAG for categorization (faster but less accurate)
- `--skip-existing`: Skip complaints that already exist (default: True)

**Features:**
- Validates complaint data before processing
- Processes in batches with progress tracking
- Generates error reports for failed complaints
- Creates detailed logs with timestamps

**Output:**
- Console logs with progress updates
- Log file: `ingestion_YYYYMMDD_HHMMSS.log`
- Error report: `error_report_YYYYMMDD_HHMMSS.json` (if errors occur)

### `validate_json.py`

Validates JSON file structure before ingestion.

**Usage:**
```bash
python scripts/validate_json.py data/complaints.json
```

**Output:**
- Validation report with statistics
- Sample complaint structure
- Missing fields analysis

**Exit codes:**
- `0`: File is valid
- `1`: File is invalid or has errors

## Example Workflow

1. **Validate JSON file:**
   ```bash
   python scripts/validate_json.py data/complaints-2024-08-15_20_15.json
   ```

2. **Ingest complaints:**
   ```bash
   python scripts/ingest_complaints.py data/complaints-2024-08-15_20_15.json
   ```

3. **Check error report** (if generated):
   ```bash
   cat error_report_*.json
   ```

## Notes

- Make sure PostgreSQL is running (via Docker or local installation)
- Ensure `.env` file is configured with database URL and Mistral API key
- Large files may take significant time to process
- Error reports include detailed information about failed complaints
