# Codomyrmex Development Makefile
# Common development tasks and workflows

.PHONY: help install setup test lint format type-check security clean docs serve build deploy

# Default target
help:
	@echo "Codomyrmex Development Makefile"
	@echo "=============================="
	@echo ""
	@echo "Available targets:"
	@echo "  install      - Install dependencies using uv"
	@echo "  setup        - Set up complete development environment"
	@echo "  test         - Run all tests"
	@echo "  test-unit    - Run unit tests only"
	@echo "  test-integration - Run integration tests only"
	@echo "  test-coverage - Run tests with coverage report"
	@echo "  test-coverage-html - Open HTML coverage report in browser"
	@echo "  lint         - Run code linting"
	@echo "  format       - Format code with black and isort"
	@echo "  type-check   - Run type checking with mypy"
	@echo "  security     - Run security scanning"
	@echo "  docs         - Generate and check documentation"
	@echo "  serve-docs   - Serve documentation locally"
	@echo "  clean        - Clean build artifacts and caches"
	@echo "  analyze      - Run project analysis"
	@echo "  check-deps   - Check and validate dependencies"
	@echo "  check-dependencies - Check module dependency hierarchy"
	@echo "  pre-commit   - Run pre-commit hooks"
	@echo "  ci           - Run full CI pipeline"
	@echo "  dev          - Start development server"
	@echo ""

# Installation and setup
install:
	@echo "Installing Codomyrmex with uv..."
	uv sync

setup: install
	@echo "Setting up development environment..."
	@echo "Creating virtual environment..."
	uv venv
	@echo "Installing pre-commit hooks..."
	pre-commit install
	@echo "Setting up git hooks..."
	@echo "Development environment ready!"

# Testing
test:
	@echo "Running all tests..."
	uv run pytest testing/ -v --tb=short --cov=src/codomyrmex --cov-report=term-missing --cov-report=html:htmlcov --cov-report=json:coverage.json

test-unit:
	@echo "Running unit tests..."
	uv run pytest testing/unit/ -v --tb=short -m unit --cov=src/codomyrmex --cov-report=term-missing --cov-report=json:coverage.json

test-integration:
	@echo "Running integration tests..."
	uv run pytest testing/integration/ -v --tb=short -m integration

test-coverage:
	@echo "Running tests with coverage report..."
	uv run pytest testing/ -v --tb=short --cov=src/codomyrmex --cov-report=term-missing --cov-report=html:htmlcov --cov-report=json:coverage.json
	@echo "Coverage report generated: coverage.json and htmlcov/"

test-coverage-html:
	@echo "Opening HTML coverage report..."
	@if [ -d "htmlcov" ]; then \
		python3 -m http.server 8000 --directory htmlcov & \
		echo "Coverage report available at http://localhost:8000"; \
	else \
		echo "No coverage report found. Run 'make test-coverage' first."; \
	fi

# Code quality
lint:
	@echo "Running linting..."
	uv run python -m flake8 src/codomyrmex/ testing/

format:
	@echo "Formatting code..."
	uv run python -m black src/codomyrmex/ testing/
	uv run python -m isort --profile=black src/codomyrmex/ testing/

type-check:
	@echo "Running type checking..."
	uv run python -m mypy src/codomyrmex/

security:
	@echo "Running security scanning..."
	uv run python -m bandit -r src/codomyrmex/
	@echo "Checking for vulnerabilities..."
	uv run python -m pip-audit

# Documentation
docs: docs-check docs-generate

docs-check:
	@echo "Checking documentation status..."
	uv run python scripts/documentation/check_docs_status.py

docs-generate:
	@echo "Generating missing documentation..."
	uv run python scripts/documentation/generate_missing_readmes.py

serve-docs:
	@echo "Serving documentation locally..."
	@echo "Note: This requires documentation website setup"
	@echo "See docs/development/documentation.md for setup instructions"

# Analysis and maintenance
analyze:
	@echo "Running project analysis..."
	uv run python -m codomyrmex.tools.analyze_project

check-deps:
	@echo "Checking dependencies..."
	uv run python -m codomyrmex.tools.dependency_checker

check-dependencies:
	@echo "Checking module dependency hierarchy..."
	uv run python -m codomyrmex.tools.dependency_analyzer

# Pre-commit and CI
pre-commit:
	@echo "Running pre-commit hooks..."
	pre-commit run --all-files

ci: lint type-check security test docs-check
	@echo "CI pipeline completed successfully!"

# Development server
dev:
	@echo "Starting development server..."
	@echo "Note: This requires additional setup for web server"
	@echo "See docs/development/environment-setup.md"

# Cleanup
clean:
	@echo "Cleaning build artifacts and caches..."
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf htmlcov/
	rm -rf .coverage
	rm -rf .pytest_cache/
	rm -rf .mypy_cache/
	rm -rf .ruff_cache/
	find . -type d -name __pycache__ -delete
	find . -type f -name "*.pyc" -delete
	@echo "Cleanup complete!"

# Advanced targets
build: clean
	@echo "Building package..."
	uv build

deploy: build
	@echo "Deploying package..."
	@echo "Note: Configure deployment target in pyproject.toml"
	uv publish

# Environment management
env-info:
	@echo "Environment information:"
	@echo "Python version: $$(python --version)"
	@echo "Python path: $$(which python)"
	@echo "Virtual environment: $$(python -c 'import sys; print(\"Yes\" if hasattr(sys, \"real_prefix\") or (hasattr(sys, \"base_prefix\") and sys.base_prefix != sys.prefix) else \"No\")')"
	@echo "UV available: $$(which uv || echo 'No')"
	@echo "Git available: $$(which git || echo 'No')"
	@echo "Docker available: $$(which docker || echo 'No')"

# Quick commands
quick-test: test-unit
quick-lint: lint
quick-format: format
quick-check: lint format type-check

# Development workflow
dev-workflow: format lint type-check test-unit
	@echo "Development workflow completed!"

# Production workflow
prod-workflow: ci security analyze
	@echo "Production workflow completed!"

# Update all
update: install clean
	@echo "Updating all dependencies and cleaning cache..."
	uv sync --upgrade

# Help for specific tools
help-flake8:
	@echo "Flake8 help:"
	uv run python -m flake8 --help

help-black:
	@echo "Black help:"
	uv run python -m black --help

help-mypy:
	@echo "MyPy help:"
	uv run python -m mypy --help

help-bandit:
	@echo "Bandit help:"
	uv run python -m bandit --help

# Docker targets (if needed)
docker-build:
	@echo "Building Docker image..."
	docker build -t codomyrmex:latest .

docker-run:
	@echo "Running Codomyrmex in Docker..."
	docker run -p 8000:8000 codomyrmex:latest

# Git workflow helpers
git-status:
	git status

git-clean:
	git clean -fd

git-reset:
	git reset --hard HEAD

# Release helpers
release-patch:
	@echo "Creating patch release..."
	@echo "Run: uv run python -m bump2version patch"

release-minor:
	@echo "Creating minor release..."
	@echo "Run: uv run python -m bump2version minor"

release-major:
	@echo "Creating major release..."
	@echo "Run: uv run python -m bump2version major"
