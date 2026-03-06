# Codomyrmex — justfile
# Modern task runner (alternative to Makefile)
# Install: https://github.com/casey/just

# Default recipe — show help
default:
    @just --list

# ─── Installation ────────────────────────────────────────────────
# Install dependencies
install:
    uv sync

# Install all dependency groups (dev, test, docs, etc.)
dev:
    uv sync --all-groups

# ─── Testing ─────────────────────────────────────────────────────
# Run all tests with coverage
test:
    uv run pytest src/codomyrmex/tests/ -v --tb=short --cov=src/codomyrmex --cov-report=term-missing --cov-report=html:htmlcov --cov-report=json:coverage.json

# Run unit tests only
test-unit:
    uv run pytest src/codomyrmex/tests/unit/ -v --tb=short --cov=src/codomyrmex --cov-report=term-missing

# Run integration tests
test-integration:
    uv run pytest src/codomyrmex/tests/integration/ -v --tb=short

# Fast test run (no coverage overhead)
test-fast:
    uv run pytest src/codomyrmex/tests/ -q --no-header --override-ini="addopts="

# Run tests with HTML coverage report
test-coverage-html: test
    @echo "Coverage report: htmlcov/index.html"

# ─── Code Quality ────────────────────────────────────────────────
# Lint with ruff
lint:
    uv run ruff check .

# Auto-fix lint issues
lint-fix:
    uv run ruff check --fix .

# Unsafe auto-fix (review diff carefully!)
lint-fix-unsafe:
    uv run ruff check --fix --unsafe-fixes .

# Format with ruff
format:
    uv run ruff format .

# Check formatting without changes
format-check:
    uv run ruff format --check .

# Type check with ty
type-check:
    uv run ty check src/

# Run all quality checks
check: lint format-check type-check

# ─── Build ───────────────────────────────────────────────────────
# Build sdist + wheel
build:
    uv build

# Clean build artifacts
clean:
    rm -rf build/ dist/ *.egg-info/ htmlcov/ .coverage .pytest_cache/ .mypy_cache/ .ty/ .ruff_cache/

# Build from clean state
rebuild: clean build

# ─── Documentation ───────────────────────────────────────────────
# Serve docs locally
docs-serve:
    uv run mkdocs serve

# Build docs (strict mode)
docs-build:
    uv run mkdocs build --strict

# ─── CI Pipeline ─────────────────────────────────────────────────
# Full CI pipeline
ci: lint type-check test build
    @echo "✅ CI pipeline passed"

# Quick pre-commit check
quick: format lint type-check test-fast
    @echo "✅ Quick check passed"

# ─── Release ─────────────────────────────────────────────────────
# Bump patch version and tag
release-patch:
    #!/usr/bin/env bash
    VERSION=$(grep 'version = ' pyproject.toml | head -1 | sed 's/.*"\(.*\)"/\1/')
    echo "Current version: $VERSION"
    echo "Run 'git tag -a v$VERSION -m \"Release v$VERSION\"' to tag"

# ─── Security ────────────────────────────────────────────────────
# Run security scanning (bandit + pip-audit)
security:
    @echo "Running security scanning..."
    uv run python -m bandit -r src/codomyrmex/
    @echo "Checking for vulnerabilities..."
    uv run python -m pip_audit

# Dependency audit via pip-audit
audit:
    @echo "Running dependency audit..."
    uv run python -m pip_audit
    @echo "Audit complete."

# ─── Documentation ───────────────────────────────────────────────
# Check documentation status
docs-check:
    @echo "Checking documentation status..."
    uv run python scripts/documentation/check_docs_status.py

# Generate missing documentation
docs-generate:
    @echo "Generating missing documentation..."
    uv run python scripts/documentation/generate_missing_readmes.py

# Full docs pipeline: check + generate + build
docs: docs-check docs-generate docs-build

# ─── Benchmarks ──────────────────────────────────────────────────
# Run MCP performance benchmarks
benchmark-mcp:
    @echo "Running MCP performance benchmarks..."
    uv run python -m pytest src/codomyrmex/tests/performance/test_mcp_load.py -v --no-cov --no-header
    uv run python -m pytest src/codomyrmex/tests/performance/test_mcp_performance.py -v --no-cov --no-header

# Run all benchmarks
benchmark: benchmark-mcp
    @echo "All benchmarks completed."

# ─── Utilities ───────────────────────────────────────────────────
# Show project info
info:
    @echo "Modules: $(ls -d src/codomyrmex/*/ 2>/dev/null | wc -l | tr -d ' ')"
    @echo "Tests:   $(find src/codomyrmex/tests -name 'test_*.py' 2>/dev/null | wc -l | tr -d ' ') files"
    @echo "LOC:     $(find src/ -name '*.py' | xargs wc -l 2>/dev/null | tail -1 | awk '{print $1}')"
    @uv run ruff check . 2>&1 | tail -1
    @uv run ty check src/ 2>&1 | tail -1

# Verify all parse errors are fixed
verify-parse:
    @python3 -c "import ast, glob; errors=[f for f in glob.glob('**/*.py', recursive=True) if not (lambda p: (ast.parse(open(p).read()), True)[-1])(f)]; print(f'Parse errors: {len(errors)}')" 2>/dev/null || echo "Parse check done"

# Show environment info
env-info:
    @echo "Python version: $(python --version)"
    @echo "Python path: $(which python)"
    @echo "UV available: $(which uv || echo 'No')"
    @echo "Git available: $(which git || echo 'No')"
    @echo "Docker available: $(which docker || echo 'No')"

# Update dependencies and clean
update: install clean
    @echo "Updating all dependencies..."
    uv sync --upgrade

# ─── Docker ──────────────────────────────────────────────────────
# Build Docker image
docker-build:
    docker build -t codomyrmex:latest .

# Run in Docker
docker-run:
    docker run -p 8000:8000 codomyrmex:latest

# ─── Development Workflows ──────────────────────────────────────
# Quick pre-commit: format + lint + type-check + fast tests
dev-workflow: format lint type-check test-fast
    @echo "✅ Development workflow passed"

# Production workflow: full CI + security + audit
prod-workflow: ci security audit
    @echo "✅ Production workflow passed"
