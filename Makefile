.PHONY: help install install-dev lint format test clean ci run-wav2lip run-musetalk run-ultralight

# Default target
help:
	@echo "Digital Human - Development Commands"
	@echo ""
	@echo "Setup Commands:"
	@echo "  make install        - Install production dependencies"
	@echo "  make install-dev    - Install development dependencies"
	@echo "  make setup-hooks    - Setup pre-commit hooks"
	@echo ""
	@echo "Code Quality Commands:"
	@echo "  make lint           - Run pylint on all Python files"
	@echo "  make lint-file FILE=<path> - Run pylint on specific file"
	@echo "  make mypy           - Run mypy type checking"
	@echo "  make bandit         - Run security checks with bandit"
	@echo "  make format         - Format code (requires black/isort)"
	@echo "  make check          - Run all quality checks"
	@echo ""
	@echo "Testing Commands:"
	@echo "  make test           - Run all tests"
	@echo "  make test-cov       - Run tests with coverage report"
	@echo "  make test-file FILE=<path> - Run specific test file"
	@echo ""
	@echo "Running Application:"
	@echo "  make run-wav2lip    - Run with Wav2Lip model"
	@echo "  make run-musetalk   - Run with MuseTalk model"
	@echo "  make run-ultralight - Run with Ultralight model"
	@echo "  make run            - Run with validation"
	@echo ""
	@echo "Maintenance Commands:"
	@echo "  make clean          - Clean temporary files and caches"
	@echo "  make clean-all      - Clean everything including venv"
	@echo "  make ci             - Run full CI pipeline locally"
	@echo ""

# Installation
install:
	pip install --upgrade pip setuptools wheel
	pip install -r requirements.txt

install-dev:
	pip install --upgrade pip setuptools wheel
	pip install -r requirements.txt
	pip install -r requirements-dev.txt

setup-hooks:
	pip install pre-commit
	pre-commit install
	@echo "Pre-commit hooks installed successfully!"

# Code Quality
lint:
	@echo "Running pylint..."
	pylint $$(git ls-files '*.py') --fail-under=7.0 --score=yes

lint-file:
	@echo "Running pylint on $(FILE)..."
	pylint $(FILE) --score=yes

mypy:
	@echo "Running mypy type checking..."
	mypy src/ --ignore-missing-imports --python-version=3.10

bandit:
	@echo "Running bandit security checks..."
	bandit -r src/ -c .bandit.yml

format:
	@echo "Formatting code..."
	@command -v black >/dev/null 2>&1 && black src/ tests/ --line-length=100 || echo "black not installed, skipping"
	@command -v isort >/dev/null 2>&1 && isort src/ tests/ --profile=black || echo "isort not installed, skipping"

check: lint mypy bandit
	@echo "All quality checks passed!"

# Testing
test:
	@echo "Running tests..."
	pytest tests/ -v

test-cov:
	@echo "Running tests with coverage..."
	pytest tests/ --cov=src --cov-report=html --cov-report=term
	@echo "Coverage report generated in htmlcov/index.html"

test-file:
	@echo "Running tests in $(FILE)..."
	pytest $(FILE) -v

# Running Application
run-wav2lip:
	python app.py --model wav2lip --avatar_id avator_1

run-musetalk:
	python app.py --model musetalk --avatar_id avator_1

run-ultralight:
	python app.py --model ultralight --avatar_id avator_1

run:
	python run.py

# Maintenance
clean:
	@echo "Cleaning temporary files..."
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "htmlcov" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name ".coverage" -delete
	find . -type f -name "pylint_report.txt" -delete
	@echo "Cleanup complete!"

clean-all: clean
	@echo "Removing virtual environment..."
	rm -rf venv/ .venv/
	@echo "Full cleanup complete!"

# CI Pipeline
ci: clean
	@echo "=== Running Full CI Pipeline ==="
	@echo ""
	@echo "Step 1: Installing dependencies..."
	make install-dev
	@echo ""
	@echo "Step 2: Running pre-commit hooks..."
	pre-commit run --all-files || true
	@echo ""
	@echo "Step 3: Running pylint..."
	make lint
	@echo ""
	@echo "Step 4: Running mypy..."
	make mypy
	@echo ""
	@echo "Step 5: Running security checks..."
	make bandit
	@echo ""
	@echo "Step 6: Running tests..."
	make test-cov
	@echo ""
	@echo "=== CI Pipeline Complete ==="

# Docker commands
docker-build:
	docker build -t digital-human:latest .

docker-run:
	docker run -p 8010:8010 digital-human:latest

docker-compose-up:
	docker-compose up --build

docker-compose-down:
	docker-compose down

# Update dependencies
update-deps:
	pip list --outdated
	@echo "Run 'pip install --upgrade <package>' to update specific packages"

freeze-deps:
	pip freeze > requirements-freeze.txt
	@echo "Dependencies frozen to requirements-freeze.txt"

