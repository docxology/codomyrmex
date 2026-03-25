# Codomyrmex Development Makefile
# Common development tasks and workflows

.PHONY: help dev install setup submodules test lint format type-check security clean docs serve build deploy benchmark benchmark-mcp test-obsidian test-fast verify-release

# Default target
help:
	@echo "Codomyrmex Development Makefile"
	@echo "=============================="
	@echo ""
	@echo "Available targets:"
	@echo "  dev          - Install all dependency groups"
	@echo "  install      - Install dependencies using uv"
	@echo "  submodules   - Initialize git submodules and install their deps"
	@echo "  setup        - Set up complete development environment (install + submodules)"
	@echo "  test         - Run all tests with coverage + 40% gate"
	@echo "  test-unit    - Run unit tests only"
	@echo "  test-integration - Run integration tests only"
	@echo "  test-coverage - Run tests with coverage report"
	@echo "  test-coverage-html - Open HTML coverage report in browser"
	@echo "  test-obsidian - Run Obsidian module tests only"
	@echo "  test-fast    - Run tests with minimal addopts (no verbose/timeout from ini)"
	@echo "  lint         - Run code linting with ruff"
	@echo "  format       - Format code with ruff"
	@echo "  type-check   - Run type checking with ty"
	@echo "  security     - Run security scanning"
	@echo "  docs         - Generate and check documentation"
	@echo "  serve-docs   - Serve documentation locally"
	@echo "  clean        - Clean build artifacts and caches"
	@echo "  analyze      - Run project analysis"
	@echo "  check-deps   - Check and validate dependencies"
	@echo "  check-dependencies - Check module dependency hierarchy"
	@echo "  ci           - Run full CI pipeline"
	@echo "  verify-release - lint + type-check + full tests with 40% coverage gate"
	@echo ""

# Installation and setup
install:
	@echo "Installing Codomyrmex with uv..."
	uv sync

dev:
	@echo "Installing all dependency groups..."
	uv sync --all-groups

submodules:
	@echo "Initializing and setting up git submodules..."
	@bash scripts/setup_submodules.sh

setup: install submodules
	@echo "Development environment (including submodules) ready!"

# Testing
test:
	@echo "Running all tests..."
	uv run pytest src/codomyrmex/tests/ -v --tb=short --cov=src/codomyrmex --cov-report=term-missing --cov-report=html:htmlcov --cov-report=json:coverage.json --cov-fail-under=40

test-unit:
	@echo "Running unit tests..."
	uv run pytest src/codomyrmex/tests/unit/ -v --tb=short -m unit --cov=src/codomyrmex --cov-report=term-missing --cov-report=json:coverage.json --cov-fail-under=40

test-integration:
	@echo "Running integration tests..."
	uv run pytest src/codomyrmex/tests/integration/ -v --tb=short -m integration

test-obsidian:
	@echo "Running Obsidian module tests..."
	uv run pytest src/codomyrmex/tests/unit/agentic_memory/obsidian/ -v --tb=short --override-ini="addopts="

test-fast:
	@echo "Running tests without coverage..."
	uv run pytest src/codomyrmex/tests/ -q --no-header --override-ini="addopts="

test-coverage:
	@echo "Running tests with coverage report..."
	uv run pytest src/codomyrmex/tests/ -v --tb=short --cov=src/codomyrmex --cov-report=term-missing --cov-report=html:htmlcov --cov-report=json:coverage.json --cov-fail-under=40
	@echo "Coverage report generated: coverage.json and htmlcov/"

test-coverage-html:
	@echo "Opening HTML coverage report..."
	@if [ -d "htmlcov" ]; then \
		python3 -m http.server 8000 --directory htmlcov & \
		echo "Coverage report available at http://localhost:8000"; \
	else \
		echo "No coverage report found. Run 'make test-coverage' first."; \
	fi

verify-release: lint type-check test
	@echo "verify-release: all checks passed."

# Code quality
lint:
	@echo "Running linting with ruff..."
	uv run ruff check .

format:
	@echo "Formatting code with ruff..."
	uv run ruff format .

type-check:
	@echo "Running type checking with ty..."
	uv run ty check src/

security:
	@echo "Running security scanning..."
	uv run python -m bandit -r src/codomyrmex/
	@echo "Checking for vulnerabilities..."
	uv run python -m pip-audit

# Performance Benchmarks
benchmark-mcp:
	@echo "Running MCP performance benchmarks..."
	uv run python -m pytest src/codomyrmex/tests/performance/test_mcp_load.py -v --no-cov --no-header
	@echo "Running MCP benchmark suite..."
	uv run python -m pytest src/codomyrmex/tests/performance/test_mcp_performance.py -v --no-cov --no-header --benchmark-only 2>/dev/null || \
		uv run python -m pytest src/codomyrmex/tests/performance/test_mcp_performance.py -v --no-cov --no-header

benchmark: benchmark-mcp
	@echo "All benchmarks completed."

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
	rm -rf .ty/
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



# Docker targets (if needed)
docker-build:
	@echo "Building Docker image..."
	docker build -t codomyrmex:latest .

docker-run:
	@echo "Running Codomyrmex in Docker..."
	docker run -p 8000:8000 codomyrmex:latest

# Git workflow helpers
git-status:
	@echo "Running ruff on all files..."
	uv run ruff check .

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
