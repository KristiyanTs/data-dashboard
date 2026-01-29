# Interview Prep: How to Read & Explain This Project

Use this guide to prepare for talking about the Procurement Data Dashboard in your interview.

---

## 1. How to Begin Reading This Project

**Suggested reading order** (top-down: entry point → data flow):

| Order | File | Why read it first |
|-------|------|-------------------|
| 1 | `README.md` | High-level: what the app is, architecture diagram, project structure. |
| 2 | `backend/app/main.py` | **Entry point.** App creation, CORS, which routers are mounted. |
| 3 | `backend/app/database.py` | **Data layer.** How DB connects, what the `Contract` table looks like, `get_db()` dependency. |
| 4 | `backend/app/models.py` | **API contracts.** Pydantic models for requests/responses (ContractCreate, Contract, ContractList, Statistics). |
| 5 | `backend/app/routes/contracts.py` | **API surface.** Which endpoints exist and how they get the service. |
| 6 | `backend/app/services/contract_service.py` | **Business logic.** Validation, rules, orchestration. |
| 7 | `backend/app/repositories/contract_repository.py` | **Data access.** SQL queries, filters, pagination. |

**One sentence per layer (memorize this):**

- **Routes** → HTTP in/out, query params, call service, map errors to HTTP.
- **Service** → Business rules, validation, calls repository, returns domain/API models.
- **Repository** → Talks to DB only: query, filter, paginate, aggregate.

---

## 2. What Does It Do?

**Elevator pitch (30 seconds):**

> "It's a **Procurement Data Dashboard**: a small full-stack app to manage and visualize procurement contracts. The backend is a REST API built with FastAPI. It lets you list contracts with filtering and pagination, create new contracts, get one by ID, and fetch aggregated statistics (totals, averages, by category). The frontend would show lists, forms, and charts—the backend we have here is the API that supports that."

**Concrete features:**

- **List contracts** – Paginated, filterable by category, value range, date range.
- **Get one contract** – By ID.
- **Create contract** – POST with validation (company name, value, date, category, optional description).
- **Statistics** – Total count, total value, average value, breakdown by category (goods / services / works).

**Domain:** Procurement contracts = company name, monetary value, date, category (goods/services/works), optional description.

---

## 3. How Does It Work?

### Request flow (e.g. “GET /contracts”)

```
HTTP Request
    → FastAPI (main.py)
    → Router (routes/contracts.py)
    → get_contract_service(db)  ← dependency injection: creates Repository(db), then Service(repository)
    → ContractService.get_contracts(...)
        → validates (e.g. date range, value range, max page size)
        → ContractRepository.get_all(skip, limit, filters...)
            → SQLAlchemy: query, filter, count, offset/limit
            → returns (list of DB Contract, total count)
        → maps DB models to Pydantic Contract
        → returns ContractList(contracts, total, page, page_size, has_more)
    → FastAPI serializes to JSON (response_model=ContractList)
    → HTTP Response
```

**Same pattern for other endpoints:** route → service (with optional validation) → repository → DB; service maps DB → Pydantic; route returns or raises HTTPException.

### Key concepts to mention in the interview

1. **Layered architecture (Service–Repository)**
   - **Repository:** Only data access. No business rules. Returns DB entities.
   - **Service:** Business logic and validation. Uses repository. Returns DTOs/Pydantic models.
   - **Routes:** Thin. Parse request, call service, return response or 4xx/5xx.

2. **Dependency injection**
   - `get_db()` yields a DB session per request.
   - `get_contract_service(db)` builds Repository(db) and Service(repository). FastAPI injects `db` and `service` into route handlers. Clean and testable.

3. **Large dataset handling**
   - **Pagination:** `page`, `page_size`, `skip`/`limit`; response includes `total`, `has_more`.
   - **Filtering:** category, min/max value, start/end date to reduce result set.
   - **Aggregation:** `/contracts/statistics` uses DB aggregation (count, sum, avg, group by) instead of loading all rows.

4. **Validation**
   - **Pydantic:** Request/response models (ContractCreate, Contract, etc.) validate types and constraints.
   - **Service:** Business rules (e.g. start_date &lt; end_date, min_value &lt; max_value, max page size 1000).

5. **API design**
   - REST: GET /contracts, GET /contracts/{id}, POST /contracts, GET /contracts/statistics.
   - Query params for filtering and pagination; JSON body for create; clear status codes (200, 201, 400, 404).

---

## 4. Quick Cheat Sheet for “Walk Me Through the Code”

- **“Where does a request enter?”** → `main.py` → `routes/contracts.py` (e.g. `get_contracts`).
- **“Where is the database?”** → `database.py`: engine, `Contract` table, `SessionLocal`, `get_db()`.
- **“Where are API shapes defined?”** → `models.py`: Pydantic models.
- **“Where is business logic?”** → `services/contract_service.py`: validation, page size cap, date/value checks.
- **“Where do we touch the DB?”** → `repositories/contract_repository.py`: `get_all`, `get_by_id`, `create`, `get_statistics`.
- **“How do routes get the service?”** → `get_contract_service(db)` in routes; FastAPI’s `Depends(get_db)` and `Depends(get_contract_service)`.

---

## 5. If They Ask: “Why this structure?”

- **Testability:** Service can be tested with a mock repository; API tests with a test DB or mocks.
- **Maintainability:** Change DB or queries in repository without touching business rules; change business rules without touching HTTP or SQL.
- **Clarity:** Each file has one role; new developers know where to add filtering (repository), rules (service), or new endpoints (routes).

You can say: *“I structured it so the API layer stays thin, all business rules live in the service, and all database access is in the repository. That’s what I’d aim for in a real codebase too.”*

---

Good luck in your interview.
