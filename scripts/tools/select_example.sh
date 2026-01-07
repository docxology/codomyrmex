#!/bin/bash
# 🐜 Codomyrmex Example Selector
#
# Interactive script to help users select and run examples based on their interests
# and experience level. Provides guided exploration of Codomyrmex capabilities.

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

# Helper functions
log_info() { echo -e "${CYAN}ℹ️  $1${NC}"; }
log_success() { echo -e "${GREEN}✅ $1${NC}"; }
log_warning() { echo -e "${YELLOW}⚠️  $1${NC}"; }
log_error() { echo -e "${RED}❌ $1${NC}"; }

show_header() {
    echo -e "${CYAN}"
    cat << "EOF"
╔════════════════════════════════════════════════════════════════╗
║                                                                ║
║   🐜 CODOMYRMEX EXAMPLE SELECTOR 🐜                           ║
║   Choose Your Perfect Learning Path                            ║
║                                                                ║
╚════════════════════════════════════════════════════════════════╝
EOF
    echo -e "${NC}"
}

check_environment() {
    # Check if we're in the right directory
    if [[ ! -f "$PROJECT_ROOT/pyproject.toml" ]] || [[ ! -d "$PROJECT_ROOT/src/codomyrmex" ]]; then
        log_error "Not in Codomyrmex project root. Please run from examples/ directory."
        exit 1
    fi
    
    # Check if Codomyrmex is installed
    if ! command -v codomyrmex &> /dev/null; then
        log_warning "Codomyrmex CLI not available. Some checks may not work optimally."
    fi
}

show_user_path_selection() {
    echo -e "${WHITE}🎯 What describes you best?${NC}\n"
    echo -e "${GREEN}1)${NC} 🔰 ${CYAN}New to Codomyrmex${NC} - I want to see what it can do"
    echo -e "${GREEN}2)${NC} 🧪 ${CYAN}Developer/Contributor${NC} - I want to understand the architecture"
    echo -e "${GREEN}3)${NC} 🚀 ${CYAN}Integration-focused${NC} - I want to see modules working together"  
    echo -e "${GREEN}4)${NC} 🎓 ${CYAN}Learning-oriented${NC} - I want comprehensive tutorials"
    echo -e "${GREEN}5)${NC} 🔧 ${CYAN}Specific Use Case${NC} - I know what I want to explore"
    echo -e "${GREEN}6)${NC} 📋 ${CYAN}Show All Examples${NC} - Let me see everything available"
    echo ""
    read -p "Choose your path (1-6): " user_path
}

show_basic_examples() {
    echo -e "\n${WHITE}🔰 Basic Examples - Perfect for Getting Started${NC}"
    echo -e "${CYAN}════════════════════════════════════════════════${NC}\n"
    
    local examples=(
        "data-visualization-demo.sh|📊|Data Visualization|3 min|Create charts and plots|None"
        "static-analysis-demo.sh|🔍|Static Analysis|2 min|Code quality analysis|Sample code"
        # Add more basic examples here
    )
    
    echo -e "${GREEN}Available Basic Examples:${NC}"
    for i in "${!examples[@]}"; do
        IFS='|' read -r script icon title duration description prereqs <<< "${examples[$i]}"
        echo -e "${GREEN}$((i+1)))${NC} ${icon} ${CYAN}$title${NC}"
        echo -e "     Duration: ${duration} | Prerequisites: ${prereqs}"
        echo -e "     ${description}"
        echo ""
    done
    
    read -p "Select example to run (number), or 'b' to go back: " choice
    
    if [[ "$choice" == "b" ]]; then
        return
    elif [[ "$choice" -ge 1 ]] && [[ "$choice" -le ${#examples[@]} ]]; then
        local selected_index=$((choice - 1))
        IFS='|' read -r script icon title duration description prereqs <<< "${examples[$selected_index]}"
        
        echo -e "\n${CYAN}Running: ${title}${NC}"
        echo -e "Duration: ${duration}"
        echo -e "Prerequisites: ${prereqs}"
        echo ""
        read -p "Continue? (Y/n): " confirm
        
        if [[ "$confirm" =~ ^[Nn]$ ]]; then
            return
        fi
        
        # Check if script exists and run it
        local script_path="$SCRIPT_DIR/basic/$script"
        if [[ -f "$script_path" ]]; then
            cd "$SCRIPT_DIR/basic"
            bash "./$script"
        else
            log_error "Example script not found: $script"
        fi
    else
        log_error "Invalid selection"
    fi
}

show_integration_examples() {
    echo -e "\n${WHITE}🔗 Integration Examples - See Modules Working Together${NC}"
    echo -e "${CYAN}══════════════════════════════════════════════════════${NC}\n"
    
    local examples=(
        "ai-enhanced-analysis.sh|🤖|AI + Analysis + Visualization|5 min|Complete AI workflow|API keys"
        # Add more integration examples here
    )
    
    echo -e "${GREEN}Available Integration Examples:${NC}"
    for i in "${!examples[@]}"; do
        IFS='|' read -r script icon title duration description prereqs <<< "${examples[$i]}"
        echo -e "${GREEN}$((i+1)))${NC} ${icon} ${CYAN}$title${NC}"
        echo -e "     Duration: ${duration} | Prerequisites: ${prereqs}"
        echo -e "     ${description}"
        echo ""
    done
    
    read -p "Select example to run (number), or 'b' to go back: " choice
    
    if [[ "$choice" == "b" ]]; then
        return
    elif [[ "$choice" -ge 1 ]] && [[ "$choice" -le ${#examples[@]} ]]; then
        local selected_index=$((choice - 1))
        IFS='|' read -r script icon title duration description prereqs <<< "${examples[$selected_index]}"
        
        echo -e "\n${CYAN}Running: ${title}${NC}"
        echo -e "Duration: ${duration}"
        echo -e "Prerequisites: ${prereqs}"
        echo ""
        read -p "Continue? (Y/n): " confirm
        
        if [[ "$confirm" =~ ^[Nn]$ ]]; then
            return
        fi
        
        # Check if script exists and run it
        local script_path="$SCRIPT_DIR/integration/$script"
        if [[ -f "$script_path" ]]; then
            cd "$SCRIPT_DIR/integration"
            bash "./$script"
        else
            log_error "Example script not found: $script"
        fi
    else
        log_error "Invalid selection"
    fi
}

show_learning_examples() {
    echo -e "\n${WHITE}🎓 Learning Examples - Comprehensive Tutorials${NC}"
    echo -e "${CYAN}═══════════════════════════════════════════════════${NC}\n"
    
    echo -e "${YELLOW}📚 Educational Examples (Coming Soon):${NC}"
    echo -e "   🐜 ${CYAN}Module System Tour${NC} - Interactive exploration of all modules"
    echo -e "   🏗️  ${CYAN}Building Your First Module${NC} - Complete module development tutorial"
    echo -e "   🔗 ${CYAN}Integration Patterns${NC} - Learn how modules work together"
    echo ""
    echo -e "${INFO}These comprehensive tutorials are being developed.${NC}"
    echo -e "${INFO}For now, check out the documentation: docs/getting-started/tutorials/${NC}"
    
    read -p "Press Enter to continue..."
}

show_specific_use_cases() {
    echo -e "\n${WHITE}🔧 Specific Use Cases - Target Your Interest${NC}"
    echo -e "${CYAN}════════════════════════════════════════════════════${NC}\n"
    
    echo -e "${GREEN}What would you like to explore?${NC}\n"
    echo -e "${GREEN}1)${NC} 📊 ${CYAN}Data Analysis & Visualization${NC} - Charts, plots, data processing"
    echo -e "${GREEN}2)${NC} 🔍 ${CYAN}Code Quality & Analysis${NC} - Linting, security, complexity analysis"
    echo -e "${GREEN}3)${NC} 🤖 ${CYAN}AI-Powered Development${NC} - Code generation, improvement suggestions"
    echo -e "${GREEN}4)${NC} 🏃 ${CYAN}Code Execution & Testing${NC} - Safe sandboxed code execution"
    echo -e "${GREEN}5)${NC} 📚 ${CYAN}Documentation Generation${NC} - Automated doc creation"
    echo -e "${GREEN}6)${NC} 🔄 ${CYAN}Complete Workflows${NC} - End-to-end development processes"
    echo ""
    read -p "Choose your interest (1-6), or 'b' to go back: " use_case
    
    case $use_case in
        1)
            echo -e "\n${CYAN}Recommended for Data Analysis & Visualization:${NC}"
            echo -e "   🔰 Start with: ${GREEN}basic/data-visualization-demo.sh${NC}"
            echo -e "   🔗 Then try: ${GREEN}integration/data-analysis-workflow.sh${NC} (coming soon)"
            ;;
        2)
            echo -e "\n${CYAN}Recommended for Code Quality & Analysis:${NC}"
            echo -e "   🔰 Start with: ${GREEN}basic/static-analysis-demo.sh${NC}"
            echo -e "   🔗 Then try: ${GREEN}integration/code-quality-pipeline.sh${NC} (coming soon)"
            ;;
        3)
            echo -e "\n${CYAN}Recommended for AI-Powered Development:${NC}"
            echo -e "   🔰 Start with: ${GREEN}basic/ai-code-editing-demo.sh${NC} (coming soon)"
            echo -e "   🔗 Then try: ${GREEN}integration/ai-enhanced-analysis.sh${NC}"
            ;;
        4)
            echo -e "\n${CYAN}Recommended for Code Execution & Testing:${NC}"
            echo -e "   🔰 Start with: ${GREEN}basic/code-execution-demo.sh${NC} (coming soon)"
            echo -e "   🔗 Then try: ${GREEN}workflows/performance-analysis.sh${NC} (coming soon)"
            ;;
        5)
            echo -e "\n${CYAN}Recommended for Documentation Generation:${NC}"
            echo -e "   🔰 Start with: ${GREEN}integration/documentation-generator.sh${NC} (coming soon)"
            echo -e "   🔗 Then try: ${GREEN}workflows/new-project-setup.sh${NC} (coming soon)"
            ;;
        6)
            echo -e "\n${CYAN}Recommended for Complete Workflows:${NC}"
            echo -e "   🔗 Try: ${GREEN}integration/ai-enhanced-analysis.sh${NC}"
            echo -e "   🚀 Then: ${GREEN}workflows/ai-development-cycle.sh${NC} (coming soon)"
            ;;
        "b")
            return
            ;;
        *)
            log_error "Invalid selection"
            ;;
    esac
    
    echo ""
    read -p "Would you like to run one of these recommendations? (y/N): " run_rec
    if [[ "$run_rec" =~ ^[Yy]$ ]]; then
        echo "Feature coming soon - for now, navigate to the recommended scripts manually"
    fi
}

show_all_examples() {
    echo -e "\n${WHITE}📋 All Available Examples${NC}"
    echo -e "${CYAN}═══════════════════════════${NC}\n"
    
    echo -e "${GREEN}🔰 Basic Examples:${NC}"
    if [[ -d "$SCRIPT_DIR/basic" ]]; then
        for script in "$SCRIPT_DIR/basic"/*.sh; do
            if [[ -f "$script" ]]; then
                filename=$(basename "$script")
                echo -e "   📄 ${filename}"
            fi
        done
    else
        echo -e "   ${YELLOW}No basic examples directory found${NC}"
    fi
    
    echo -e "\n${GREEN}🔗 Integration Examples:${NC}"
    if [[ -d "$SCRIPT_DIR/integration" ]]; then
        for script in "$SCRIPT_DIR/integration"/*.sh; do
            if [[ -f "$script" ]]; then
                filename=$(basename "$script")
                echo -e "   📄 ${filename}"
            fi
        done
    else
        echo -e "   ${YELLOW}No integration examples directory found${NC}"
    fi
    
    echo -e "\n${GREEN}🚀 Workflow Examples:${NC}"
    if [[ -d "$SCRIPT_DIR/workflows" ]]; then
        for script in "$SCRIPT_DIR/workflows"/*.sh; do
            if [[ -f "$script" ]]; then
                filename=$(basename "$script")
                echo -e "   📄 ${filename}"
            fi
        done
    else
        echo -e "   ${YELLOW}Workflow examples coming soon${NC}"
    fi
    
    echo -e "\n${GREEN}🎓 Learning Examples:${NC}"
    if [[ -d "$SCRIPT_DIR/learning" ]]; then
        for script in "$SCRIPT_DIR/learning"/*.sh; do
            if [[ -f "$script" ]]; then
                filename=$(basename "$script")
                echo -e "   📄 ${filename}"
            fi
        done
    else
        echo -e "   ${YELLOW}Learning examples coming soon${NC}"
    fi
    
    echo ""
    read -p "Press Enter to continue..."
}

show_tips() {
    echo -e "\n${YELLOW}💡 Pro Tips for Using Examples:${NC}"
    echo ""
    echo -e "${CYAN}Getting Started:${NC}"
    echo -e "   • Start with basic examples to understand individual modules"
    echo -e "   • Read the script headers to understand prerequisites"
    echo -e "   • Check scripts/output/ for generated files after running"
    echo ""
    echo -e "${CYAN}For API-based Examples:${NC}"
    echo -e "   • Create .env file in project root with API keys"
    echo -e "   • Examples work in simulation mode without API keys"
    echo -e "   • Real AI features require: OPENAI_API_KEY, ANTHROPIC_API_KEY, or GOOGLE_API_KEY"
    echo ""
    echo -e "${CYAN}Exploring Results:${NC}"
    echo -e "   • All examples create output in scripts/output/[example-name]/"
    echo -e "   • View generated visualizations, reports, and code"
    echo -e "   • Scripts include cleanup options to remove generated files"
    echo ""
    echo -e "${CYAN}Going Further:${NC}"
    echo -e "   • Modify example scripts for your own use cases"
    echo -e "   • Combine examples to create custom workflows"
    echo -e "   • Check docs/getting-started/tutorials/ for in-depth guides"
    echo ""
}

main_menu() {
    while true; do
        show_user_path_selection
        
        case $user_path in
            1)
                show_basic_examples
                ;;
            2)
                echo -e "\n${CYAN}For developers and contributors:${NC}"
                echo -e "   🔰 Start with basic examples to understand modules"
                echo -e "   🔗 Try integration examples to see architecture"
                echo -e "   📚 Check docs/development/environment-setup.md"
                echo -e "   🎓 Review docs/getting-started/tutorials/creating-a-module.md"
                read -p "Press Enter to continue..."
                ;;
            3)
                show_integration_examples
                ;;
            4)
                show_learning_examples
                ;;
            5)
                show_specific_use_cases
                ;;
            6)
                show_all_examples
                ;;
            *)
                log_error "Invalid selection. Please choose 1-6."
                continue
                ;;
        esac
        
        echo ""
        read -p "Return to main menu? (Y/n): " return_menu
        if [[ "$return_menu" =~ ^[Nn]$ ]]; then
            break
        fi
    done
}

# Main execution
main() {
    show_header
    check_environment
    
    log_info "Welcome to the Codomyrmex Example Selector!"
    log_info "This interactive guide helps you find the perfect examples for your needs."
    echo ""
    
    show_tips
    
    echo ""
    read -p "Ready to explore? Press Enter to continue..."
    
    main_menu
    
    echo -e "\n${GREEN}🎉 Thanks for exploring Codomyrmex examples!${NC}"
    echo -e "${CYAN}Happy coding! 🐜✨${NC}"
}

# Run the selector
main "$@"
