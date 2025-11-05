#!/bin/bash
# 🐜 Codomyrmex Examples Test Runner
# 
# This script systematically tests all Codomyrmex orchestrator examples to ensure
# they work properly as thin orchestrators without hanging or errors.
#
# Features:
# - Tests all examples in non-interactive mode
# - Captures output and errors
# - Provides comprehensive summary
# - Generates test reports

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
WHITE='\033[1;37m'
NC='\033[0m'

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
TEST_OUTPUT_DIR="$PROJECT_ROOT/scripts/output/test-runner"
TEST_START_TIME=$(date +%s)

# Test results tracking
TOTAL_TESTS=0
PASSED_TESTS=0
FAILED_TESTS=0
SKIPPED_TESTS=0
TEST_RESULTS=()

# Parse arguments
VERBOSE=false
CLEANUP=false
TIMEOUT=300  # 5 minutes default timeout per test

for arg in "$@"; do
    case $arg in
        -v|--verbose)
            VERBOSE=true
            ;;
        --cleanup)
            CLEANUP=true
            ;;
        --timeout=*)
            TIMEOUT="${arg#*=}"
            ;;
        --help)
            echo "Usage: $0 [--verbose] [--cleanup] [--timeout=SECONDS] [--help]"
            echo "  --verbose       Show detailed output from each test"
            echo "  --cleanup       Clean up test outputs after completion"
            echo "  --timeout=N     Set timeout per test in seconds (default: 300)"
            echo "  --help          Show this help message"
            exit 0
            ;;
    esac
done

# Helper functions
log_header() {
    echo -e "${CYAN}╔══════════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${CYAN}║          🐜 Codomyrmex Examples Test Runner 🐜                  ║${NC}"
    echo -e "${CYAN}║     Testing all orchestrator examples for functionality         ║${NC}"
    echo -e "${CYAN}╚══════════════════════════════════════════════════════════════════╝${NC}"
    echo ""
}

log_info() { echo -e "${CYAN}ℹ️  $1${NC}"; }
log_success() { echo -e "${GREEN}✅ $1${NC}"; }
log_warning() { echo -e "${YELLOW}⚠️  $1${NC}"; }
log_error() { echo -e "${RED}❌ $1${NC}"; }

# Create test output directory
mkdir -p "$TEST_OUTPUT_DIR"
echo "" > "$TEST_OUTPUT_DIR/test-summary.log"

# Test execution function
run_test() {
    local test_name="$1"
    local script_path="$2"
    local category="$3"
    local requires_api_keys="$4"
    local requires_docker="$5"
    
    TOTAL_TESTS=$((TOTAL_TESTS + 1))
    local test_log="$TEST_OUTPUT_DIR/${test_name}.log"
    local test_status="UNKNOWN"
    local test_duration=0
    local test_start_time=$(date +%s)
    
    echo -e "${BLUE}[$(printf '%02d' $TOTAL_TESTS)] Testing: $test_name${NC}"
    echo "Test: $test_name" >> "$TEST_OUTPUT_DIR/test-summary.log"
    echo "Script: $script_path" >> "$TEST_OUTPUT_DIR/test-summary.log"
    echo "Category: $category" >> "$TEST_OUTPUT_DIR/test-summary.log"
    
    # Check prerequisites
    local skip_reason=""
    if [ "$requires_api_keys" = "true" ] && [ ! -f "$PROJECT_ROOT/.env" ]; then
        skip_reason="Missing .env file with API keys"
    elif [ "$requires_docker" = "true" ] && ! docker info >/dev/null 2>&1; then
        skip_reason="Docker not running"
    fi
    
    if [ -n "$skip_reason" ]; then
        log_warning "SKIPPED: $skip_reason"
        SKIPPED_TESTS=$((SKIPPED_TESTS + 1))
        test_status="SKIPPED"
        echo "Status: SKIPPED ($skip_reason)" >> "$TEST_OUTPUT_DIR/test-summary.log"
        TEST_RESULTS+=("$test_name|SKIPPED|$skip_reason|0")
        echo "---" >> "$TEST_OUTPUT_DIR/test-summary.log"
        return
    fi
    
    # Check if script exists and is executable
    if [ ! -f "$script_path" ]; then
        log_error "FAILED: Script not found"
        FAILED_TESTS=$((FAILED_TESTS + 1))
        test_status="FAILED"
        echo "Status: FAILED (Script not found)" >> "$TEST_OUTPUT_DIR/test-summary.log"
        TEST_RESULTS+=("$test_name|FAILED|Script not found|0")
        echo "---" >> "$TEST_OUTPUT_DIR/test-summary.log"
        return
    fi
    
    if [ ! -x "$script_path" ]; then
        log_error "FAILED: Script not executable"
        FAILED_TESTS=$((FAILED_TESTS + 1))
        test_status="FAILED"
        echo "Status: FAILED (Script not executable)" >> "$TEST_OUTPUT_DIR/test-summary.log"
        TEST_RESULTS+=("$test_name|FAILED|Script not executable|0")
        echo "---" >> "$TEST_OUTPUT_DIR/test-summary.log"
        return
    fi
    
    # Run the test with a background process and kill after timeout (macOS compatible)
    echo "Starting test at $(date)" > "$test_log"
    
    # Start the script in background with appropriate flags
    if [[ "$script_path" == *"setup-fabric-demo.sh"* ]]; then
        # Use test mode for setup-fabric-demo to avoid network operations
        "$script_path" --test-mode >> "$test_log" 2>&1 &
    else
        "$script_path" --non-interactive >> "$test_log" 2>&1 &
    fi
    local script_pid=$!
    
    # Wait for completion or timeout
    local count=0
    while [ $count -lt $TIMEOUT ] && kill -0 $script_pid 2>/dev/null; do
        sleep 1
        count=$((count + 1))
    done
    
    if kill -0 $script_pid 2>/dev/null; then
        # Process still running, kill it
        kill -TERM $script_pid 2>/dev/null
        sleep 2
        kill -KILL $script_pid 2>/dev/null
        test_status="TIMEOUT"
        log_error "TIMEOUT (${TIMEOUT}s)"
        FAILED_TESTS=$((FAILED_TESTS + 1))
        local exit_code=124
    else
        # Process completed, get exit code
        wait $script_pid
        local exit_code=$?
        if [ $exit_code -eq 0 ]; then
            test_status="PASSED"
            log_success "PASSED"
            PASSED_TESTS=$((PASSED_TESTS + 1))
        else
            test_status="FAILED"
            log_error "FAILED (exit code: $exit_code)"
            FAILED_TESTS=$((FAILED_TESTS + 1))
        fi
    fi
    
    local test_end_time=$(date +%s)
    test_duration=$((test_end_time - test_start_time))
    
    echo "Status: $test_status" >> "$TEST_OUTPUT_DIR/test-summary.log"
    echo "Duration: ${test_duration}s" >> "$TEST_OUTPUT_DIR/test-summary.log"
    echo "Exit Code: $exit_code" >> "$TEST_OUTPUT_DIR/test-summary.log"
    
    if [ "$VERBOSE" = true ] && [ "$test_status" != "PASSED" ]; then
        echo -e "${YELLOW}Last 10 lines of output:${NC}"
        tail -10 "$test_log" | sed 's/^/  /'
    fi
    
    TEST_RESULTS+=("$test_name|$test_status|Exit code: $exit_code|$test_duration")
    echo "---" >> "$TEST_OUTPUT_DIR/test-summary.log"
}

# Main test execution
log_header

log_info "Starting comprehensive orchestrator tests..."
log_info "Test results will be saved to: $TEST_OUTPUT_DIR"
echo ""

# Test basic examples
echo -e "${WHITE}📦 Basic Examples${NC}"
run_test "data-visualization-demo" "$PROJECT_ROOT/scripts/examples/basic/data-visualization-demo.sh" "basic" "false" "false"
run_test "advanced-data-visualization-demo" "$PROJECT_ROOT/scripts/examples/basic/advanced_data_visualization_demo.sh" "basic" "false" "false"
run_test "static-analysis-demo" "$PROJECT_ROOT/scripts/examples/basic/static-analysis-demo.sh" "basic" "false" "false"

echo ""

# Test integration examples  
echo -e "${WHITE}🔗 Integration Examples${NC}"
run_test "environment-health-monitor" "$PROJECT_ROOT/scripts/examples/integration/environment-health-monitor.sh" "integration" "false" "false"
run_test "code-quality-pipeline" "$PROJECT_ROOT/scripts/examples/integration/code-quality-pipeline.sh" "integration" "false" "false"
run_test "ai-enhanced-analysis" "$PROJECT_ROOT/scripts/examples/integration/ai-enhanced-analysis.sh" "integration" "true" "false"
run_test "ai-development-assistant" "$PROJECT_ROOT/scripts/examples/integration/ai-development-assistant.sh" "integration" "true" "true"
run_test "development-workflow-orchestrator" "$PROJECT_ROOT/scripts/examples/integration/development-workflow-orchestrator.sh" "integration" "true" "true"

# Test advanced integration examples
echo -e "${WHITE}🚀 Advanced Integration Examples${NC}"
run_test "ai-driven-development-workflow" "$PROJECT_ROOT/scripts/examples/integration/ai_driven_development_workflow.sh" "integration" "true" "false"
run_test "comprehensive-analysis-pipeline" "$PROJECT_ROOT/scripts/examples/integration/comprehensive_analysis_pipeline.sh" "integration" "false" "false"
run_test "interactive-learning-orchestrator" "$PROJECT_ROOT/scripts/examples/integration/interactive_learning_orchestrator.sh" "integration" "false" "false"
run_test "performance-benchmarking-orchestrator" "$PROJECT_ROOT/scripts/examples/integration/performance_benchmarking_orchestrator.sh" "integration" "false" "false"
run_test "complete-ecosystem-orchestrator" "$PROJECT_ROOT/scripts/examples/integration/complete_ecosystem_orchestrator.sh" "integration" "true" "true"

echo ""

# Test core examples
echo -e "${WHITE}📋 Core Examples${NC}"
run_test "setup-fabric-demo" "$PROJECT_ROOT/scripts/fabric_integration/setup_demo.sh" "core" "false" "false"

# Generate comprehensive summary
TEST_END_TIME=$(date +%s)
TOTAL_DURATION=$((TEST_END_TIME - TEST_START_TIME))

echo ""
echo -e "${CYAN}╔══════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║                           TEST SUMMARY                          ║${NC}"  
echo -e "${CYAN}╚══════════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${WHITE}📊 Results Overview:${NC}"
echo -e "   Total Tests: $TOTAL_TESTS"
echo -e "   ${GREEN}✅ Passed: $PASSED_TESTS${NC}"
echo -e "   ${RED}❌ Failed: $FAILED_TESTS${NC}" 
echo -e "   ${YELLOW}⏭️  Skipped: $SKIPPED_TESTS${NC}"
echo -e "   ⏱️  Duration: ${TOTAL_DURATION}s"
echo ""

if [ $PASSED_TESTS -gt 0 ]; then
    echo -e "${GREEN}✅ PASSED TESTS:${NC}"
    for result in "${TEST_RESULTS[@]}"; do
        IFS='|' read -r name status reason duration <<< "$result"
        if [ "$status" = "PASSED" ]; then
            echo -e "   • $name (${duration}s)"
        fi
    done
    echo ""
fi

if [ $FAILED_TESTS -gt 0 ]; then
    echo -e "${RED}❌ FAILED TESTS:${NC}"
    for result in "${TEST_RESULTS[@]}"; do
        IFS='|' read -r name status reason duration <<< "$result"
        if [ "$status" = "FAILED" ] || [ "$status" = "TIMEOUT" ]; then
            echo -e "   • $name - $status ($reason)"
        fi
    done
    echo ""
fi

if [ $SKIPPED_TESTS -gt 0 ]; then
    echo -e "${YELLOW}⏭️  SKIPPED TESTS:${NC}"
    for result in "${TEST_RESULTS[@]}"; do
        IFS='|' read -r name status reason duration <<< "$result"
        if [ "$status" = "SKIPPED" ]; then
            echo -e "   • $name - $reason"
        fi
    done
    echo ""
fi

# Generate detailed JSON report
cat > "$TEST_OUTPUT_DIR/test-results.json" << EOF
{
    "summary": {
        "total_tests": $TOTAL_TESTS,
        "passed": $PASSED_TESTS,
        "failed": $FAILED_TESTS,
        "skipped": $SKIPPED_TESTS,
        "duration": $TOTAL_DURATION,
        "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
    },
    "results": [
EOF

for i in "${!TEST_RESULTS[@]}"; do
    result="${TEST_RESULTS[$i]}"
    IFS='|' read -r name status reason duration <<< "$result"
    cat >> "$TEST_OUTPUT_DIR/test-results.json" << EOF
        {
            "name": "$name",
            "status": "$status",
            "reason": "$reason", 
            "duration": $duration
        }$([ $i -lt $((${#TEST_RESULTS[@]} - 1)) ] && echo ",")
EOF
done

cat >> "$TEST_OUTPUT_DIR/test-results.json" << EOF
    ]
}
EOF

echo -e "${BLUE}📄 Detailed reports generated:${NC}"
echo -e "   • $TEST_OUTPUT_DIR/test-summary.log - Full test log"
echo -e "   • $TEST_OUTPUT_DIR/test-results.json - Structured results"
echo -e "   • $TEST_OUTPUT_DIR/*.log - Individual test outputs"

# Cleanup if requested
if [ "$CLEANUP" = true ]; then
    echo ""
    log_info "Cleaning up test outputs as requested..."
    find "$PROJECT_ROOT/scripts/output" -name "*.png" -o -name "*.json" -o -name "*.py" -o -name "*.md" | grep -v test-runner | xargs rm -f
    log_success "Cleanup completed"
fi

echo ""
if [ $FAILED_TESTS -eq 0 ]; then
    echo -e "${GREEN}🎉 All tests completed successfully!${NC}"
    exit 0
else
    echo -e "${RED}⚠️  Some tests failed. Check the logs above for details.${NC}"
    exit 1
fi
