#!/bin/bash
# 🐜 Run All Basic Codomyrmex Examples
#
# This script runs all basic examples in sequence, providing a comprehensive
# overview of Codomyrmex's core capabilities. Perfect for initial exploration
# or demonstrating the system to others.
#
# Duration: ~8-10 minutes (all basic examples)
# Output: Results in examples/output/ subdirectories

set -e

# Colors for terminal output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
WHITE='\033[1;37m'
NC='\033[0m' # No Color

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
BASIC_DIR="$SCRIPT_DIR/basic"
DEMO_START_TIME=$(date +%s)

# Helper functions
log_info() { echo -e "${CYAN}ℹ️  $1${NC}"; }
log_success() { echo -e "${GREEN}✅ $1${NC}"; }
log_warning() { echo -e "${YELLOW}⚠️  $1${NC}"; }
log_error() { echo -e "${RED}❌ $1${NC}"; }
log_step() { echo -e "\n${BLUE}🔹 $1${NC}"; }

show_header() {
    echo -e "${CYAN}"
    cat << "EOF"
╔════════════════════════════════════════════════════════════════╗
║                                                                ║
║   🐜 CODOMYRMEX BASIC EXAMPLES RUNNER 🐜                      ║
║   Comprehensive Overview of Core Capabilities                 ║
║                                                                ║
╚════════════════════════════════════════════════════════════════╝
EOF
    echo -e "${NC}"
}

check_environment() {
    log_step "Environment Setup & Validation"
    
    # Check project structure
    if [[ ! -f "$PROJECT_ROOT/pyproject.toml" ]] || [[ ! -d "$PROJECT_ROOT/src/codomyrmex" ]]; then
        log_error "Not in Codomyrmex project root. Please run from examples/ directory."
        exit 1
    fi
    
    # Check basic examples directory
    if [[ ! -d "$BASIC_DIR" ]]; then
        log_error "Basic examples directory not found: $BASIC_DIR"
        exit 1
    fi
    
    # Activate virtual environment if available
    if [[ -f "$PROJECT_ROOT/.venv/bin/activate" ]]; then
        log_info "Activating virtual environment..."
        source "$PROJECT_ROOT/.venv/bin/activate"
    fi
    
    # Check Codomyrmex installation
    if ! python3 -c "import sys; sys.path.insert(0, '$PROJECT_ROOT/src'); import codomyrmex" 2>/dev/null; then
        log_error "Codomyrmex not properly installed. Please run: pip install -e ."
        exit 1
    fi
    
    log_success "Environment ready!"
}

discover_basic_examples() {
    log_step "Discovering Basic Examples"
    
    # Find all executable shell scripts in basic directory
    local examples=()
    while IFS= read -r -d '' script; do
        if [[ -x "$script" ]] && [[ "$script" == *.sh ]]; then
            examples+=("$(basename "$script")")
        fi
    done < <(find "$BASIC_DIR" -name "*.sh" -type f -print0)
    
    if [[ ${#examples[@]} -eq 0 ]]; then
        log_error "No executable examples found in $BASIC_DIR"
        exit 1
    fi
    
    log_info "Found ${#examples[@]} basic examples:"
    for example in "${examples[@]}"; do
        echo -e "   📄 $example"
    done
    
    echo "${examples[@]}"
}

run_example() {
    local example="$1"
    local example_number="$2"
    local total_examples="$3"
    
    log_step "Running Example $example_number/$total_examples: $example"
    
    local script_path="$BASIC_DIR/$example"
    local example_name="${example%.sh}"
    
    echo -e "${WHITE}📋 Example: $example_name${NC}"
    echo -e "${CYAN}═══════════════════════════════════════${NC}"
    
    # Extract description from script if available
    if [[ -f "$script_path" ]]; then
        local description=$(grep -m 1 "^# .*demonstrates\|^# This script" "$script_path" | sed 's/^# //' || echo "No description available")
        echo -e "${INFO}Description: $description${NC}"
        echo ""
    fi
    
    # Ask user if they want to run this example
    read -p "Run this example? (Y/n/s to skip all remaining): " choice
    case "$choice" in
        [Nn]*)
            log_info "Skipping $example"
            return 1
            ;;
        [Ss]*)
            log_info "Skipping all remaining examples"
            return 2
            ;;
        *)
            # Run the example
            log_info "Starting $example..."
            
            local start_time=$(date +%s)
            
            if cd "$BASIC_DIR" && timeout 300 bash "./$example"; then
                local end_time=$(date +%s)
                local duration=$((end_time - start_time))
                log_success "$example completed in ${duration}s"
                return 0
            else
                local end_time=$(date +%s)
                local duration=$((end_time - start_time))
                log_error "$example failed after ${duration}s"
                return 1
            fi
            ;;
    esac
}

show_summary() {
    log_step "Demo Session Summary"
    
    local demo_end_time=$(date +%s)
    local total_duration=$((demo_end_time - demo_start_time))
    
    echo -e "${GREEN}🎉 Basic Examples Session Complete!${NC}"
    echo ""
    echo -e "${WHITE}📊 Session Statistics:${NC}"
    echo "   🕒 Total Duration: ${total_duration} seconds"
    echo "   ✅ Examples Completed: $successful_examples"
    echo "   ❌ Examples Failed: $failed_examples"
    echo "   ⏭️  Examples Skipped: $skipped_examples"
    
    if [[ $successful_examples -gt 0 ]]; then
        echo ""
        echo -e "${WHITE}📁 Generated Outputs:${NC}"
        local output_base="$PROJECT_ROOT/examples/output"
        if [[ -d "$output_base" ]]; then
            for output_dir in "$output_base"/*/; do
                if [[ -d "$output_dir" ]]; then
                    local dir_name=$(basename "$output_dir")
                    local file_count=$(find "$output_dir" -type f | wc -l | tr -d ' ')
                    echo "   📂 $dir_name ($file_count files)"
                fi
            done
        fi
    fi
    
    echo ""
    echo -e "${YELLOW}🚀 Next Steps:${NC}"
    echo "   1. Review generated outputs in examples/output/"
    echo "   2. Try integration examples: cd integration"
    echo "   3. Explore workflow examples: cd workflows"
    echo "   4. Read documentation: docs/getting-started/"
    echo "   5. Create your own examples and workflows"
    
    if [[ $failed_examples -gt 0 ]]; then
        echo ""
        echo -e "${YELLOW}⚠️  Note: Some examples failed.${NC}"
        echo "   • Check error messages above"
        echo "   • Verify all dependencies are installed"
        echo "   • Run individual examples to debug issues"
    fi
    
    echo ""
    echo -e "${GREEN}✨ Happy exploring with Codomyrmex! ✨${NC}"
}

cleanup_session() {
    echo ""
    read -p "🧹 Clean up all generated files from this session? (y/N): " cleanup_choice
    
    if [[ "$cleanup_choice" =~ ^[Yy]$ ]]; then
        log_info "Cleaning up session outputs..."
        
        local output_base="$PROJECT_ROOT/examples/output"
        if [[ -d "$output_base" ]]; then
            # Remove all output directories created during this session
            find "$output_base" -type d -name "*" -mindepth 1 -exec rm -rf {} + 2>/dev/null || true
            log_success "Cleanup completed!"
        else
            log_info "No output directory found - nothing to clean up"
        fi
    else
        log_info "Files preserved for your exploration"
        echo -e "${CYAN}💡 Tip: You can always clean up individual example outputs by running the examples again and choosing cleanup.${NC}"
    fi
}

# Error handling
handle_error() {
    log_error "Runner encountered an error on line $1"
    log_info "You may have partial results in examples/output/"
    exit 1
}

trap 'handle_error $LINENO' ERR

# Global counters
successful_examples=0
failed_examples=0
skipped_examples=0

# Main execution
main() {
    show_header
    
    log_info "This runner executes all basic Codomyrmex examples in sequence"
    log_info "Each example demonstrates a core module's capabilities"
    log_info "Estimated duration: 8-10 minutes total"
    echo ""
    
    echo -e "${YELLOW}📋 What to Expect:${NC}"
    echo "   • Interactive prompts for each example"
    echo "   • Generated files in examples/output/ directories"
    echo "   • Comprehensive overview of Codomyrmex capabilities"
    echo "   • Option to skip examples that don't interest you"
    echo ""
    
    read -p "Ready to start the basic examples tour? (Y/n): " start_choice
    if [[ "$start_choice" =~ ^[Nn]$ ]]; then
        log_info "Example session cancelled"
        exit 0
    fi
    
    check_environment
    
    # Get list of examples
    examples_output=$(discover_basic_examples)
    read -ra examples <<< "$examples_output"
    
    log_info "Starting basic examples tour with ${#examples[@]} examples"
    echo ""
    
    # Run each example
    for i in "${!examples[@]}"; do
        local example="${examples[$i]}"
        local example_number=$((i + 1))
        local total_examples=${#examples[@]}
        
        case $(run_example "$example" "$example_number" "$total_examples") in
            0)
                ((successful_examples++))
                ;;
            1)
                ((failed_examples++))
                ;;
            2)
                # Skip all remaining
                local remaining=$((total_examples - i - 1))
                skipped_examples=$((skipped_examples + remaining + 1))
                log_info "Skipping remaining $remaining examples"
                break
                ;;
        esac
        
        # Add separator between examples
        if [[ $((example_number)) -lt $total_examples ]]; then
            echo ""
            echo -e "${CYAN}${'━' * 60}${NC}"
            echo ""
        fi
    done
    
    show_summary
    cleanup_session
}

# Run the examples runner
main "$@"
