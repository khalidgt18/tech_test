.PHONY: install run test lint format clean help

help:
	@echo "Available commands:"
	@echo "  make install  - Install dependencies (including dev)"
	@echo "  make run      - Run the development server"
	@echo "  make test     - Run tests with coverage"
	@echo "  make lint     - Check code with ruff"
	@echo "  make format   - Format code with ruff"
	@echo "  make clean    - Remove cache files"

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
	ruff check --fix app tests

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".ruff_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	find . -type f -name ".coverage" -delete 2>/dev/null || true
	rm -rf htmlcov/ 2>/dev/null || true
	rm -rf *.egg-info/ 2>/dev/null || true
