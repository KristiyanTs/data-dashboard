# Backend Testing Guide

This document explains how to run and understand the backend tests for the Procurement Data Dashboard API.

## Test Structure

The backend tests are organized into three main categories:

- **Unit Tests (Repository)**: `tests/test_repository.py` - Tests the data access layer
- **Unit Tests (Service)**: `tests/test_service.py` - Tests the business logic layer
- **Integration Tests (API)**: `tests/test_api.py` - Tests the complete API endpoints

## Prerequisites

Install the test dependencies:

```bash
cd backend
pip install -r requirements.txt
```

## Running Tests

### Run all tests
```bash
pytest
```

### Run with coverage report
```bash
pytest --cov=app --cov-report=term-missing
```

### Run specific test file
```bash
pytest tests/test_repository.py
pytest tests/test_service.py
pytest tests/test_api.py
```

### Run specific test class or function
```bash
pytest tests/test_repository.py::TestContractRepository::test_create_contract
pytest tests/test_api.py::TestContractsAPI::test_get_contracts_with_data
```

### Run tests in verbose mode
```bash
pytest -v
```

### Run tests with output (print statements)
```bash
pytest -s
```

## Test Coverage

The tests cover:

### Repository Layer (`test_repository.py`)
- ✅ Creating contracts
- ✅ Retrieving contracts by ID
- ✅ Listing all contracts with pagination
- ✅ Filtering by category, value range, and date range
- ✅ Combined filters
- ✅ Statistics calculation
- ✅ Edge cases (empty database, not found)

### Service Layer (`test_service.py`)
- ✅ Business logic validation (date ranges, value ranges)
- ✅ Page size limiting
- ✅ Contract creation with business rules
- ✅ High-value contract handling (>$10M)
- ✅ Future-dated contracts
- ✅ Statistics aggregation
- ✅ Error handling

### API Layer (`test_api.py`)
- ✅ All endpoint responses (GET, POST)
- ✅ Request validation
- ✅ Error responses (400, 404, 422)
- ✅ Pagination
- ✅ Filtering
- ✅ CORS headers
- ✅ Edge cases

## Test Database

Tests use an in-memory SQLite database that is:
- Created fresh for each test
- Isolated between tests
- Automatically cleaned up after each test

This ensures tests are fast, reliable, and don't affect your development database.

## Continuous Integration

To run tests in CI/CD:

```bash
# Install dependencies
pip install -r requirements.txt

# Run tests with coverage
pytest --cov=app --cov-report=xml

# Check coverage threshold (optional)
pytest --cov=app --cov-fail-under=80
```

## Writing New Tests

When adding new features, follow this pattern:

1. **Repository tests**: Test database operations
2. **Service tests**: Test business logic with mocked repository
3. **API tests**: Test the complete endpoint with real database

Example:

```python
# test_repository.py
def test_new_feature(self, db_session):
    repository = ContractRepository(db_session)
    # Test database operation
    
# test_service.py
def test_new_feature(self, service, mock_repository):
    # Test business logic
    
# test_api.py
def test_new_feature(self, client):
    # Test API endpoint
```

## Common Issues

### Import Errors
Make sure you're running pytest from the `backend` directory:
```bash
cd backend
pytest
```

### Database Errors
The test database is in-memory and recreated for each test. If you see database errors, check that your fixtures are properly set up in `conftest.py`.

### Async Warnings
If you see async warnings, make sure `pytest-asyncio` is installed and `asyncio_mode = auto` is set in `pytest.ini`.
