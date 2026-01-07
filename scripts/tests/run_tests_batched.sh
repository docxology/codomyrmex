#!/bin/bash
# Codomyrmex Test Suite Batch Runner
#
# This script runs the Codomyrmex test suite in manageable batches to avoid
# memory issues and provide better control over test execution.
#
# Usage:
#   ./run_tests_batched.sh [batch_name] [options]
#
# Batches:
#   unit         - Unit tests (fastest, most isolated)
#   integration  - Integration tests (moderate speed)
#   examples     - Example validation tests
#   performance  - Performance tests (slowest)
#   all          - Run all batches in sequence
#   quick        - Run unit and examples only (fastest)
#
# Options:
#   --coverage   - Generate coverage report
#   --verbose    - Verbose output
#   --fail-fast  - Stop on first failure
#   --timeout=N  - Set test timeout in seconds (default: 300)

set -e

# Configuration
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Default settings
COVERAGE=""
VERBOSE=""
FAIL_FAST=""
TIMEOUT="300"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Parse arguments
BATCH="${1:-all}"
shift

while [[ $# -gt 0 ]]; do
    case $1 in
        --coverage)
            COVERAGE="--cov=src/codomyrmex --cov-report=html:testing/htmlcov --cov-report=term-missing --cov-fail-under=80"
            shift
            ;;
        --verbose)
            VERBOSE="-v"
            shift
            ;;
        --fail-fast)
            FAIL_FAST="-x"
            shift
            ;;
        --timeout=*)
            TIMEOUT="${1#*=}"
            shift
            ;;
        *)
            echo "Unknown option: $1"
            echo "Usage: $0 [batch_name] [--coverage] [--verbose] [--fail-fast] [--timeout=N]"
            exit 1
            ;;
    esac
done

# Common pytest options
PYTEST_BASE="uv run pytest --tb=short $VERBOSE $FAIL_FAST $COVERAGE --timeout=$TIMEOUT"

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Run test batch
run_batch() {
    local batch_name="$1"
    local test_paths="$2"
    local description="$3"

    log_info "Running $batch_name tests: $description"

    if $PYTEST_BASE $test_paths; then
        log_success "$batch_name tests completed successfully"
        return 0
    else
        log_error "$batch_name tests failed"
        return 1
    fi
}

# Main execution
cd "$PROJECT_ROOT"

log_info "Codomyrmex Test Suite Batch Runner"
log_info "Project root: $PROJECT_ROOT"
log_info "Batch: $BATCH"
log_info "Timeout: ${TIMEOUT}s"

case "$BATCH" in
    unit)
        log_info "Running unit tests only..."
        run_batch "unit" "testing/unit/ -m \"not slow\" --maxfail=5" "Unit tests (excluding slow tests)"
        ;;

    integration)
        log_info "Running integration tests..."
        run_batch "integration" "testing/integration/ --maxfail=3" "Integration tests"
        ;;

    examples)
        log_info "Running example validation tests..."
        run_batch "examples" "testing/examples/ --maxfail=3" "Example validation tests"
        ;;

    performance)
        log_warning "Running performance tests (these may take a long time)..."
        run_batch "performance" "testing/performance/ --maxfail=1" "Performance tests"
        ;;

    quick)
        log_info "Running quick test suite (unit + examples)..."
        run_batch "unit" "testing/unit/ -m 'not slow' --maxfail=5" "Unit tests (excluding slow tests)" || exit 1
        run_batch "examples" "testing/examples/ --maxfail=3" "Example validation tests" || exit 1
        ;;

    all)
        log_info "Running complete test suite..."

        # Unit tests (fastest)
        run_batch "unit" "testing/unit/ -m 'not slow' --maxfail=10" "Unit tests (excluding slow tests)" || exit 1

        # Integration tests
        run_batch "integration" "testing/integration/ --maxfail=5" "Integration tests" || exit 1

        # Example validation
        run_batch "examples" "testing/examples/ --maxfail=5" "Example validation tests" || exit 1

        # Performance tests (slowest)
        log_warning "Running performance tests last (may take several minutes)..."
        run_batch "performance" "testing/performance/ --maxfail=2" "Performance tests" || exit 1

        log_success "All test batches completed successfully!"
        ;;

    *)
        log_error "Unknown batch: $BATCH"
        echo "Available batches:"
        echo "  unit        - Unit tests (fast, isolated)"
        echo "  integration - Integration tests (moderate speed)"
        echo "  examples    - Example validation tests"
        echo "  performance - Performance tests (slow)"
        echo "  quick       - Unit + examples only (fastest)"
        echo "  all         - Complete test suite"
        exit 1
        ;;
esac

log_success "Test batch execution completed"
