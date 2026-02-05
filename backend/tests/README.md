# Testing Guide

## Running Tests

**Important:** Make sure you have installed all dependencies first:
```bash
cd backend
pip install -r requirements.txt
```

**Note:** Some tests require database dependencies (like `psycopg2`). If you don't have these installed, tests that require them will be automatically skipped. Unit tests that don't need the database will still run.

### Run all tests
```bash
cd backend
pytest
```

### Run tests without database (unit tests only)
```bash
# These tests will skip if database dependencies are missing
pytest tests/unit/ -v
```

### Troubleshooting

If you see `ModuleNotFoundError: No module named 'psycopg2'`:
- Install dependencies: `pip install -r requirements.txt`
- Or run only unit tests that don't require the database: `pytest tests/unit/ -v`
- Tests will automatically skip if dependencies are missing

### Run specific test categories
```bash
# Unit tests only
pytest tests/unit/

# API tests only
pytest tests/api/

# Integration tests only
pytest tests/integration/ -m integration

# Exclude integration tests
pytest -m "not integration"
```

### Run with coverage
```bash
pytest --cov=app --cov-report=html
```

### Run with verbose output
```bash
pytest -v
```

## Test Structure

- `tests/unit/` - Unit tests for individual services
- `tests/api/` - API endpoint tests
- `tests/integration/` - Integration tests (require database)

## Test Database

Integration tests use a separate test database. Set `TEST_DATABASE_URL` environment variable:

```bash
export TEST_DATABASE_URL=postgresql://postgres:postgres@localhost:5432/complaints_test_db
```

Or create a `.env.test` file with:
```
TEST_DATABASE_URL=postgresql://postgres:postgres@localhost:5432/complaints_test_db
```

## Writing Tests

### Unit Test Example
```python
def test_my_function():
    result = my_function(input)
    assert result == expected_output
```

### API Test Example
```python
def test_endpoint(client):
    response = client.get("/api/v1/endpoint")
    assert response.status_code == 200
```

### Integration Test Example
```python
@pytest.mark.integration
def test_database_operation(db_session):
    # Test database operations
    pass
```

## Notes

- Unit tests don't require database
- API tests use TestClient (no real server)
- Integration tests require test database setup
- Mock Mistral client is provided for LLM tests
