# Technical Test Plan: FastAPI Ticket Management API

## Executive Summary
This plan outlines optimal technical choices for a FastAPI-based ticket management REST API, with each decision backed by decisive factors.

---

## 1. Technical Stack Decisions

### 1.1 FastAPI Version
| Choice | **`fastapi>=0.115.0,<1.0.0`** |
|--------|-------------------------------|
| **Decisive Factor** | Stable release with full Python 3.10+ syntax support (`X | Y` union types), TYPE_CHECKING blocks, and Pydantic v2 integration |
| **Why not latest 0.124.x?** | Too recent (Dec 2025), less battle-tested. 0.115.x is production-proven |

### 1.2 Python Version
| Choice | **Python 3.10+** (as specified) |
|--------|--------------------------------|
| **Decisive Factor** | Modern type syntax (`int | None`), required by spec |

### 1.3 Database: Sync vs Async SQLAlchemy

| Choice | **Synchronous SQLAlchemy** |
|--------|---------------------------|
| **Decisive Factor** | SQLite + async (aiosqlite) is **7x slower** than sync due to asyncio overhead ([GitHub Discussion](https://github.com/sqlalchemy/sqlalchemy/discussions/12353)). For in-memory SQLite with simple CRUD, sync is optimal |
| **Trade-off** | Async routes will use `run_in_threadpool` internally (FastAPI handles this automatically for sync functions) |
| **Alternative rejected** | `aiosqlite` - adds complexity with no performance benefit for SQLite |

### 1.4 Primary Key: UUID vs Auto-Increment Integer

| Choice | **Auto-increment Integer** |
|--------|---------------------------|
| **Decisive Factor** | |
| 1. Spec allows both - simpler is better for a technical test |
| 2. More readable in API responses (`/tickets/1` vs `/tickets/b1e92c3b-a44a...`) |
| 3. SQLite handles auto-increment natively with excellent performance |
| 4. 4 bytes vs 16 bytes storage - more efficient |
| 5. Human-readable during code review/demo |
| **When UUID would be better** | Distributed systems, security concerns, microservices |

### 1.5 Linting Tool

| Choice | **Ruff** |
|--------|----------|
| **Decisive Factor** | |
| 1. **150-200x faster** than flake8 |
| 2. Used by FastAPI, Pydantic, pandas themselves |
| 3. Replaces flake8 + isort + black + pyupgrade in one tool |
| 4. Auto-fix capability (`ruff check --fix`) |
| 5. Demonstrates modern Python tooling knowledge |

### 1.6 Configuration Management

| Choice | **Pydantic Settings v2** (`pydantic-settings`) |
|--------|-----------------------------------------------|
| **Decisive Factor** | |
| 1. Native FastAPI integration |
| 2. Type-validated environment variables |
| 3. `@lru_cache` for singleton pattern |
| 4. Demonstrates proper configuration separation |

---

## 2. Project Structure

```
ticket_api/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI app instance, lifespan
│   ├── config.py            # Pydantic Settings
│   ├── database.py          # SQLAlchemy engine, session, Base
│   ├── models.py            # SQLAlchemy ORM models
│   ├── schemas.py           # Pydantic request/response schemas
│   ├── routers/
│   │   ├── __init__.py
│   │   └── tickets.py       # Ticket endpoints
│   └── crud.py              # Database operations (optional separation)
├── tests/
│   ├── __init__.py
│   ├── conftest.py          # Fixtures
│   └── test_tickets.py      # Endpoint tests
├── pyproject.toml           # All config: deps, pytest, ruff, coverage
├── README.md
├── Makefile                 # Bonus: convenience commands
└── Dockerfile               # Bonus: containerization
```

**Decisive Factor for Structure:**
- Single `app/` module - appropriate for project size
- `routers/` subfolder - demonstrates knowledge of FastAPI router organization
- `crud.py` - separates business logic from routes (clean architecture)
- All config in `pyproject.toml` - modern Python standard (PEP 517/518)

---

## 3. Data Models

### 3.1 SQLAlchemy Model (models.py)
```python
from enum import Enum
from datetime import datetime
from sqlalchemy import Integer, String, DateTime, Enum as SQLEnum
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

class TicketStatus(str, Enum):
    OPEN = "open"
    STALLED = "stalled"
    CLOSED = "closed"

class Base(DeclarativeBase):
    pass

class Ticket(Base):
    __tablename__ = "tickets"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(String, nullable=False)
    status: Mapped[TicketStatus] = mapped_column(
        SQLEnum(TicketStatus), default=TicketStatus.OPEN
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow
    )
```

**Decisive Factors:**
- `Mapped[]` + `mapped_column()` = SQLAlchemy 2.0 style (modern, type-safe)
- `str, Enum` inheritance = JSON serializable enum
- `String(255)` for title = reasonable limit, good practice
- `index=True` on id = explicit even though primary keys are indexed

### 3.2 Pydantic Schemas (schemas.py)
```python
from datetime import datetime
from pydantic import BaseModel, ConfigDict
from app.models import TicketStatus

class TicketCreate(BaseModel):
    title: str
    description: str
    status: TicketStatus = TicketStatus.OPEN

class TicketUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    status: TicketStatus | None = None

class TicketResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    description: str
    status: TicketStatus
    created_at: datetime
```

**Decisive Factors:**
- Python 3.10+ union syntax (`str | None`)
- `ConfigDict(from_attributes=True)` = Pydantic v2 way (replaces `orm_mode`)
- Separate Create/Update/Response schemas = proper API design
- `TicketUpdate` with all optional = partial updates for PUT

---

## 4. API Endpoints Implementation

| Method | Endpoint | Response | Status Codes |
|--------|----------|----------|--------------|
| POST | `/tickets/` | `TicketResponse` | 201 (created), 422 (validation) |
| GET | `/tickets/` | `list[TicketResponse]` | 200 |
| GET | `/tickets/{ticket_id}` | `TicketResponse` | 200, 404 |
| PUT | `/tickets/{ticket_id}` | `TicketResponse` | 200, 404, 422, 400 (if trying to set status=closed) |
| PATCH | `/tickets/{ticket_id}/close` | `TicketResponse` | 200, 404, 400 (already closed) |

**Business Rules (User Confirmed):**
1. **PATCH /close on already-closed ticket → 400 error** (not idempotent - demonstrates edge case handling)
2. **PUT cannot set status to "closed"** → 400 error (closing must happen via dedicated PATCH endpoint)

**Decisive Factors:**
- 201 for POST = REST best practice (resource created)
- 404 with proper HTTPException = clear error handling
- PATCH `/close` returns 400 if already closed = demonstrates edge case handling
- PUT blocks status→closed = enforces business workflow through API design

---

## 5. Testing Strategy

### 5.1 Test Configuration
```toml
# pyproject.toml
[tool.pytest.ini_options]
testpaths = ["tests"]
asyncio_mode = "auto"

[tool.coverage.run]
source = ["app"]
branch = true
omit = ["app/__init__.py"]

[tool.coverage.report]
fail_under = 80
show_missing = true
```

### 5.2 Test Cases for 80%+ Coverage

| Test Category | Tests |
|--------------|-------|
| **Create Ticket** | Valid creation, missing fields (422), invalid status |
| **List Tickets** | Empty list, multiple tickets |
| **Get Ticket** | Existing ticket, non-existent (404) |
| **Update Ticket** | Full update, partial update, non-existent (404), **attempt to close via PUT (400)** |
| **Close Ticket** | Open→Closed, **already closed (400)**, non-existent (404) |
| **Edge Cases** | Empty strings, very long strings |

### 5.3 Test Setup (conftest.py)
```python
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.database import get_db, Base

# In-memory SQLite for tests
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture
def client():
    Base.metadata.create_all(bind=engine)
    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()
    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    Base.metadata.drop_all(bind=engine)
    app.dependency_overrides.clear()
```

**Decisive Factors:**
- `TestClient` (sync) not `AsyncClient` - simpler, works perfectly with sync SQLAlchemy
- `StaticPool` - required for in-memory SQLite with multiple connections
- Fixture recreates tables per test = isolation
- `dependency_overrides` = FastAPI's built-in DI override mechanism

---

## 6. Dependencies (pyproject.toml)

```toml
[project]
name = "ticket-api"
version = "0.1.0"
requires-python = ">=3.10"
dependencies = [
    "fastapi>=0.115.0,<1.0.0",
    "uvicorn[standard]>=0.30.0",
    "sqlalchemy>=2.0.0,<3.0.0",
    "pydantic>=2.0.0,<3.0.0",
    "pydantic-settings>=2.0.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=8.0.0",
    "pytest-cov>=4.0.0",
    "httpx>=0.27.0",  # Required for TestClient
    "ruff>=0.4.0",
]
```

---

## 7. Bonus Features

### 7.1 Makefile
```makefile
.PHONY: install run test lint format

install:
	pip install -e ".[dev]"

run:
	uvicorn app.main:app --reload

test:
	pytest --cov=app --cov-report=term-missing --cov-fail-under=80

lint:
	ruff check app tests

format:
	ruff format app tests
```

### 7.2 Dockerfile
```dockerfile
FROM python:3.10-slim
WORKDIR /app
COPY pyproject.toml .
RUN pip install .
COPY app/ app/
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

---

## 8. Implementation Order

1. **Project setup**: Create structure, `pyproject.toml`
2. **Database layer**: `config.py`, `database.py`, `models.py`
3. **Schemas**: `schemas.py`
4. **CRUD operations**: `crud.py`
5. **Routes**: `routers/tickets.py`
6. **Main app**: `main.py` with lifespan for table creation
7. **Tests**: `conftest.py`, `test_tickets.py`
8. **Documentation**: `README.md`
9. **Bonus**: `Makefile`, `Dockerfile`, ruff configuration

---

## 9. Key Evaluation Points Addressed

| Criteria | How Addressed |
|----------|---------------|
| **Code Quality** | Clean structure, PEP8 (ruff), type hints, separation of concerns |
| **Functionality** | All 5 endpoints, proper error handling, edge cases |
| **Documentation** | Auto Swagger, comprehensive README |
| **Tests** | 80%+ coverage, pytest, isolated fixtures |
| **Modern Practices** | SQLAlchemy 2.0, Pydantic v2, Python 3.10+ syntax, ruff |

---

## Sources Referenced
- [FastAPI Release Notes](https://fastapi.tiangolo.com/release-notes/)
- [SQLAlchemy Async Performance Discussion](https://github.com/sqlalchemy/sqlalchemy/discussions/12353)
- [FastAPI Best Practices](https://github.com/zhanymkanov/fastapi-best-practices)
- [Pydantic Settings Documentation](https://docs.pydantic.dev/latest/concepts/pydantic_settings/)
- [Ruff Documentation](https://docs.astral.sh/ruff/)
- [UUID vs Auto-Increment Analysis](https://www.bytebase.com/blog/choose-primary-key-uuid-or-auto-increment/)
