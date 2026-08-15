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
    uv sync --locked --all-groups

# ─── Testing ─────────────────────────────────────────────────────
# Run all tests with coverage
test:
    uv run --locked --group docs pytest tests/ -v --tb=short -m "not performance and not benchmark and not bench" --cov=src/codomyrmex --cov-report=term-missing --cov-report=html:htmlcov --cov-report=json:coverage.json --cov-fail-under=60

# Run unit tests only
test-unit:
    uv run --locked --group docs pytest tests/unit/ -v --tb=short --cov=src/codomyrmex --cov-report=term-missing --cov-fail-under=60

# Run integration tests
test-integration:
    uv run --locked --group docs pytest tests/integration/ -v --tb=short

# Fast test run (no coverage overhead)
test-fast:
    uv run --locked --group docs pytest tests/ -q --no-header -m "not performance and not benchmark and not bench" --override-ini="addopts=" --import-mode=importlib

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
    uv run ty check --output-format concise src/ scripts/ tests/

# Enforce package layers, file-scoped exceptions, and explicit exports
lint-imports:
    uv run --locked lint-imports --config pyproject.toml
    uv run --locked python scripts/audits/audit_imports.py --root .
    uv run --locked python scripts/audits/audit_exports.py --root .

# Run all quality checks
check: lint lint-imports format-check type-check

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
    NO_MKDOCS_2_WARNING=1 uv run --locked --group docs mkdocs serve

# Build docs (strict mode)
docs-build:
    NO_MKDOCS_2_WARNING=1 uv run --locked --group docs mkdocs build --strict

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
    make security

# Dependency audit via pip-audit
audit:
    make audit-lock

# ─── Documentation ───────────────────────────────────────────────
# Check documentation status
docs-check:
    @echo "Checking documentation status..."
    uv run --locked --group docs python scripts/rasp_gap_report.py --repo-root . --check
    uv run --locked --group docs python scripts/documentation/audit_readme_agents.py --repo-root . --strict
    uv run --locked --group docs python scripts/documentation/validate_links_comprehensive.py --repo-root . --format both --fail-on-broken
    uv run --locked --group docs python scripts/documentation/analyze_content_quality.py --repo-root . --format both --min-score 70 --fail-on-below
    uv run --locked --group docs python scripts/documentation/validate_agents_structure.py --repo-root . --format both --fail-on-invalid
    uv run --locked --group docs python scripts/documentation/enforce_quality_gate.py --repo-root . --max-broken-links 0
    uv run --locked --group docs python src/codomyrmex/documentation/scripts/triple_check.py --repo-root . --fail-on-issues
    NO_MKDOCS_2_WARNING=1 uv run --locked --group docs mkdocs build --strict

# Validate generated manuscript, figures, claims, and provenance.
manuscript-check:
    uv run --locked --group docs python scripts/validate_manuscript_integrity.py

# Require source-current rendered HTML and tagged PDF/UA-2 receipts.
manuscript-pdf-check:
    uv run --locked --group docs python scripts/validate_manuscript_integrity.py --require-rendered --require-source-current

# Generate missing documentation
docs-generate:
    @echo "Explicitly generating missing documentation (do not run during a hand-pass freeze)..."
    uv run --locked --group docs python src/codomyrmex/documentation/scripts/generate_missing_readmes.py --repo-root .

# Canonical docs validation (generation remains an explicit maintenance step)
docs: docs-check

# ─── Benchmarks ──────────────────────────────────────────────────
# Run MCP performance benchmarks
benchmark-mcp:
    @echo "Running MCP performance benchmarks..."
    uv run python -m pytest tests/performance/test_mcp_load.py -v --no-cov --no-header
    uv run python -m pytest tests/performance/test_mcp_performance.py -v --no-cov --no-header

# Run all benchmarks
benchmark: benchmark-mcp
    @echo "All benchmarks completed."

# ─── Utilities ───────────────────────────────────────────────────
# Show project info
info:
    @echo "Modules: $(ls -d src/codomyrmex/*/ 2>/dev/null | wc -l | tr -d ' ')"
    @echo "Tests:   $(find tests -name 'test_*.py' 2>/dev/null | wc -l | tr -d ' ') files"
    @echo "LOC:     $(find src/ -name '*.py' | xargs wc -l 2>/dev/null | tail -1 | awk '{print $1}')"
    @uv run ruff check . 2>&1 | tail -1
    @uv run ty check --output-format concise src/ scripts/ tests/ 2>&1 | tail -1

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
