.PHONY: help install up down test lint clean

help:
	@echo "OptiFIRE Makefile Commands:"
	@echo "  make install    - Install dependencies"
	@echo "  make up         - Start OptiFIRE server"
	@echo "  make down       - Stop OptiFIRE server (if running in background)"
	@echo "  make test       - Run tests"
	@echo "  make lint       - Run linters"
	@echo "  make clean      - Clean temporary files"

install:
	pip install -r requirements.txt

up:
	@echo "Starting OptiFIRE..."
	@mkdir -p data logs
	python -m optifire.services.runner

down:
	@echo "Stopping OptiFIRE..."
	@pkill -f "optifire.services.runner" || true

test:
	pytest -v optifire/tests/ optifire/plugins/*/tests/

lint:
	@echo "Running linters..."
	@command -v ruff >/dev/null 2>&1 && ruff check optifire/ || echo "ruff not installed"
	@command -v mypy >/dev/null 2>&1 && mypy optifire/ || echo "mypy not installed"

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name ".DS_Store" -delete
	@echo "Cleaned!"
