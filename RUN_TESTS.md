# Quick Test Guide

## 🚀 Run All Tests (Both Backend & Frontend)

### Backend Tests
```bash
cd backend
pip install -r requirements.txt  # First time only
pytest --cov=app --cov-report=term-missing
```

### Frontend Tests
```bash
cd frontend
npm install  # First time only
npm test -- --coverage --watchAll=false
```

---

## 📊 Expected Results

### Backend
```
============================= test session starts ==============================
collected 50 items

tests/test_repository.py ............... [ 30%]
tests/test_service.py ............... [ 60%]
tests/test_api.py ...................... [100%]

============================== 50 passed in 2.5s ===============================

---------- coverage: platform darwin, python 3.11.x -----------
Name                                      Stmts   Miss  Cover   Missing
-----------------------------------------------------------------------
app/__init__.py                              2      0   100%
app/database.py                             42      2    95%   25-26
app/main.py                                 34      4    88%   27-30
app/models.py                               53      1    98%   24
app/repositories/__init__.py                 0      0   100%
app/repositories/contract_repository.py     93      2    98%   54, 92
app/routes/contracts.py                     85      3    96%   30, 70, 84
app/services/contract_service.py            85      2    98%   71, 76
-----------------------------------------------------------------------
TOTAL                                      394     14    96%
```

### Frontend
```
PASS  src/services/__tests__/api.test.ts
PASS  src/components/__tests__/Dashboard.test.tsx
PASS  src/components/__tests__/ContractForm.test.tsx
PASS  src/components/__tests__/ContractList.test.tsx

Test Suites: 4 passed, 4 total
Tests:       67 passed, 67 total
Snapshots:   0 total
Time:        8.5s

----------------------|---------|----------|---------|---------|-------------------
File                  | % Stmts | % Branch | % Funcs | % Lines | Uncovered Line #s 
----------------------|---------|----------|---------|---------|-------------------
All files             |   85.2  |   78.5   |   88.9  |   84.8  |                   
 components           |   92.3  |   85.7   |   95.0  |   92.1  |                   
  ContractForm.tsx    |   95.5  |   88.9   |  100.0  |   95.2  | 36-37             
  ContractList.tsx    |   90.2  |   83.3   |   90.0  |   89.8  | 22-23, 88         
  Dashboard.tsx       |   91.1  |   84.6   |   95.0  |   90.9  | 24                
 services             |   78.3  |   66.7   |   80.0  |   77.8  |                   
  api.ts              |   78.3  |   66.7   |   80.0  |   77.8  | 5, 32-36          
----------------------|---------|----------|---------|---------|-------------------
```

---

## 🔍 Common Commands

### Backend

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app

# Run specific test file
pytest tests/test_api.py

# Run specific test
pytest tests/test_api.py::TestContractsAPI::test_create_contract_success

# Verbose output
pytest -v

# Stop on first failure
pytest -x

# Show print statements
pytest -s
```

### Frontend

```bash
# Interactive mode (watch)
npm test

# Run all tests once
npm test -- --watchAll=false

# Run with coverage
npm test -- --coverage --watchAll=false

# Run specific test file
npm test ContractList

# Run specific test
npm test -- --testNamePattern="should render loading state"

# Update snapshots (if using)
npm test -- -u

# Verbose output
npm test -- --verbose
```

---

## 🐛 Troubleshooting

### Backend Issues

**Problem**: `ModuleNotFoundError`
```bash
# Solution: Make sure you're in the backend directory
cd backend
pytest
```

**Problem**: Database errors
```bash
# Solution: Tests use in-memory DB, check conftest.py is present
ls tests/conftest.py
```

**Problem**: Import errors
```bash
# Solution: Install dependencies
pip install -r requirements.txt
```

### Frontend Issues

**Problem**: Tests not found
```bash
# Solution: Make sure you're in the frontend directory
cd frontend
npm test
```

**Problem**: Module not found
```bash
# Solution: Install dependencies
npm install
```

**Problem**: Tests hanging
```bash
# Solution: Exit watch mode with Ctrl+C, or run once:
npm test -- --watchAll=false
```

**Problem**: Coverage not showing
```bash
# Solution: Run with coverage flag
npm test -- --coverage --watchAll=false
```

---

## 📈 Coverage Reports

### Backend Coverage HTML Report
```bash
cd backend
pytest --cov=app --cov-report=html
open htmlcov/index.html  # macOS
# or
xdg-open htmlcov/index.html  # Linux
```

### Frontend Coverage HTML Report
```bash
cd frontend
npm test -- --coverage --watchAll=false
open coverage/lcov-report/index.html  # macOS
# or
xdg-open coverage/lcov-report/index.html  # Linux
```

---

## 🎯 Quick Verification

Run this to verify everything works:

```bash
# Terminal 1 - Backend tests
cd backend && pytest --cov=app

# Terminal 2 - Frontend tests
cd frontend && npm test -- --watchAll=false --coverage
```

Both should pass with >80% coverage!

---

## 📚 More Information

- Backend testing details: `backend/README_TESTS.md`
- Frontend testing details: `frontend/README_TESTS.md`
- Complete test summary: `TESTING_SUMMARY.md`
