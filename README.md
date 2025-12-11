# Ticket Management API

[![CI](https://github.com/khalidgt18/tech_test/actions/workflows/ci.yml/badge.svg)](https://github.com/khalidgt18/tech_test/actions/workflows/ci.yml)
[![CodeQL](https://github.com/khalidgt18/tech_test/actions/workflows/codeql.yml/badge.svg)](https://github.com/khalidgt18/tech_test/actions/workflows/codeql.yml)
[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A mini REST API for ticket management built with FastAPI, SQLAlchemy, and Pydantic.

## Features

- Create, read, update, and close tickets
- In-memory SQLite database (no persistence after restart)
- Automatic API documentation via Swagger UI
- 80%+ test coverage

## Requirements

- Python 3.10+

## Installation

### Option 1: Using pip (recommended)

```bash
# Clone the repository
git clone https://github.com/khalidgt18/tech_test.git
cd tech_test

# Create a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -e ".[dev]"
```

### Option 2: Using Make

```bash
make install
```

## Running the API

### Development server

```bash
uvicorn app.main:app --reload
```

Or using Make:

```bash
make run
```

The API will be available at `http://127.0.0.1:8000`

### API Documentation

- Swagger UI: http://127.0.0.1:8000/docs
- ReDoc: http://127.0.0.1:8000/redoc

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/tickets/` | Create a new ticket |
| GET | `/tickets/` | List all tickets |
| GET | `/tickets/{ticket_id}` | Get a specific ticket |
| PUT | `/tickets/{ticket_id}` | Update a ticket |
| PATCH | `/tickets/{ticket_id}/close` | Close a ticket |

### Ticket Model

```json
{
  "id": 1,
  "title": "string",
  "description": "string",
  "status": "open | stalled | closed",
  "created_at": "2025-12-11T12:00:00"
}
```

### Example Usage

**Create a ticket:**
```bash
curl -X POST "http://127.0.0.1:8000/tickets/" \
  -H "Content-Type: application/json" \
  -d '{"title": "Bug fix", "description": "Fix login issue"}'
```

**List all tickets:**
```bash
curl "http://127.0.0.1:8000/tickets/"
```

**Get a specific ticket:**
```bash
curl "http://127.0.0.1:8000/tickets/1"
```

**Update a ticket:**
```bash
curl -X PUT "http://127.0.0.1:8000/tickets/1" \
  -H "Content-Type: application/json" \
  -d '{"title": "Updated title", "status": "stalled"}'
```

**Close a ticket:**
```bash
curl -X PATCH "http://127.0.0.1:8000/tickets/1/close"
```

## Running Tests

```bash
# Run tests with coverage
pytest --cov=app --cov-report=term-missing --cov-fail-under=80

# Or using Make
make test
```

## Linting

```bash
# Check for issues
ruff check app tests

# Auto-fix issues
ruff check --fix app tests

# Format code
ruff format app tests

# Or using Make
make lint
make format
```

## Project Structure

```
ticket-api/
├── app/
│   ├── __init__.py
│   ├── main.py           # FastAPI application
│   ├── config.py         # Configuration settings
│   ├── database.py       # Database connection
│   ├── models.py         # SQLAlchemy models
│   ├── schemas.py        # Pydantic schemas
│   ├── crud.py           # Database operations
│   └── routers/
│       ├── __init__.py
│       └── tickets.py    # Ticket endpoints
├── tests/
│   ├── __init__.py
│   ├── conftest.py       # Test fixtures
│   └── test_tickets.py   # API tests
├── docs/
│   └── plananddecisions.md
├── pyproject.toml        # Project configuration
├── Makefile              # Convenience commands
├── Dockerfile            # Container configuration
└── README.md
```

## CI/CD & Code Quality

Ce projet utilise GitHub Actions pour l'intégration continue et le contrôle qualité.

### Pipeline CI

| Vérification | Description |
|--------------|-------------|
| **Tests multi-versions** | Exécution sur Python 3.10, 3.11, 3.12 |
| **Linting Ruff** | Vérification du style de code (PEP8, imports, bugs) |
| **Formatage Ruff** | Vérification du formatage du code |
| **Coverage** | Minimum 80% de couverture requis |
| **CodeQL** | Analyse de sécurité du code Python |

### Outils de qualité

- **Ruff** : Linter ultra-rapide (150x plus rapide que flake8), remplace flake8 + isort + black
- **pytest-cov** : Mesure de couverture de tests avec seuil minimum
- **CodeQL** : Détection de vulnérabilités de sécurité

### Dependabot

Mise à jour automatique des dépendances chaque lundi :
- Dépendances Python (pip)
- Actions GitHub

### Protection de branche

La branche `main` est protégée :
- Les status checks CI doivent passer avant merge
- Historique linéaire requis (pas de merge commits)
- Force push bloqué
- Analyse CodeQL requise

## Technical Decisions

See `docs/plananddecisions.md` for detailed technical decisions and their rationale.

## License

MIT
