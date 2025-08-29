#!/bin/bash
# 🐜 Codomyrmex Orchestrator - Your Gateway to the Epistemic Forager Nest
# A comprehensive system discovery and interaction script for the entire Codomyrmex ecosystem

set -e  # Exit on any error

# Colors for terminal output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
WHITE='\033[1;37m'
NC='\033[0m' # No Color

# Helper function to get Python command
get_python_cmd() {
    if [[ -f ".venv/bin/python" ]]; then
        echo ".venv/bin/python"
    elif [[ -f "venv/bin/python" ]]; then
        echo "venv/bin/python"
    else
        echo "python3"
    fi
}

# ASCII Art Banner
show_banner() {
    echo -e "${CYAN}"
    cat << "EOF"
    ╔═══════════════════════════════════════════════════════════════╗
    ║                                                               ║
    ║   🐜 CODOMYRMEX - Epistemic Forager Orchestrator 🐜         ║
    ║   A Modular, Extensible Coding Workspace Discovery System    ║
    ║                                                               ║
    ╚═══════════════════════════════════════════════════════════════╝
EOF
    echo -e "${NC}"
}

# Check if we're in the right directory
check_environment() {
    if [[ ! -f "pyproject.toml" ]] || [[ ! -d "src/codomyrmex" ]]; then
        echo -e "${RED}❌ Error: Not in the Codomyrmex project root directory!${NC}"
        echo -e "${YELLOW}Please run this script from the main codomyrmex directory.${NC}"
        exit 1
    fi
}

# Activate virtual environment if it exists
activate_venv() {
    if [[ -d ".venv" ]]; then
        echo -e "${GREEN}🔄 Activating virtual environment...${NC}"
        source .venv/bin/activate
    elif [[ -d "venv" ]]; then
        echo -e "${GREEN}🔄 Activating virtual environment...${NC}"
        source venv/bin/activate
    else
        echo -e "${YELLOW}⚠️  No virtual environment found. Consider creating one:${NC}"
        PYTHON_CMD=$(get_python_cmd)
        echo -e "${CYAN}   $PYTHON_CMD -m venv venv && source venv/bin/activate${NC}"
    fi
}

# Install dependencies if needed
ensure_dependencies() {
    echo -e "${BLUE}🔍 Checking dependencies...${NC}"
    PYTHON_CMD=$(get_python_cmd)

    if ! $PYTHON_CMD -c "import sys; sys.path.insert(0, 'src'); from codomyrmex.system_discovery import SystemDiscovery" 2>/dev/null; then
        echo -e "${YELLOW}📦 Installing dependencies...${NC}"
        if [[ -f ".venv/bin/pip" ]]; then
            .venv/bin/pip install -e . || {
                echo -e "${RED}❌ Failed to install dependencies. Please run: pip install -e .${NC}"
                exit 1
            }
        elif [[ -f "venv/bin/pip" ]]; then
            venv/bin/pip install -e . || {
                echo -e "${RED}❌ Failed to install dependencies. Please run: pip install -e .${NC}"
                exit 1
            }
        else
            pip install -e . || {
                echo -e "${RED}❌ Failed to install dependencies. Please run: pip install -e .${NC}"
                exit 1
            }
        fi
    else
        echo -e "${GREEN}✅ All dependencies are properly installed${NC}"
    fi
}

# Main interactive menu
show_menu() {
    echo -e "\n${WHITE}🚀 What would you like to explore in the Codomyrmex nest?${NC}\n"
    echo -e "${GREEN}1)${NC} 🔍 ${CYAN}System Discovery${NC} - Scan all modules, methods, and capabilities"
    echo -e "${GREEN}2)${NC} 📊 ${CYAN}Status Dashboard${NC} - Comprehensive system status and health check"
    echo -e "${GREEN}3)${NC} 🏃 ${CYAN}Quick Demo${NC} - Run example workflows from working modules"
    echo -e "${GREEN}4)${NC} 🧪 ${CYAN}Test Suite${NC} - Run comprehensive tests across all modules"
    echo -e "${GREEN}5)${NC} 📚 ${CYAN}Documentation${NC} - Browse and generate documentation"
    echo -e "${GREEN}6)${NC} 🔧 ${CYAN}Development Tools${NC} - Linting, formatting, and analysis"
    echo -e "${GREEN}7)${NC} 🎮 ${CYAN}Interactive Shell${NC} - Enter interactive exploration mode"
    echo -e "${GREEN}8)${NC} 📋 ${CYAN}Export Inventory${NC} - Generate complete system inventory report"
    echo -e "${GREEN}9)${NC} 🌐 ${CYAN}Git Repository Status${NC} - Check all Git repos and dependencies"
    echo -e "${GREEN}0)${NC} 🚪 ${CYAN}Exit${NC} - Return to the outside world"
    echo ""
    echo -e "${PURPLE}Choose your path (0-9):${NC} "
}

# Run system discovery
run_system_discovery() {
    echo -e "\n${CYAN}🔍 Scanning the Codomyrmex ecosystem...${NC}"
    PYTHON_CMD=$(get_python_cmd)

    $PYTHON_CMD -c "
import sys
sys.path.insert(0, 'src')
from codomyrmex.system_discovery import SystemDiscovery

discovery = SystemDiscovery()
discovery.run_full_discovery()
"
}

# Run status dashboard
run_status_dashboard() {
    echo -e "\n${CYAN}📊 Codomyrmex System Status Dashboard${NC}"
    PYTHON_CMD=$(get_python_cmd)

    $PYTHON_CMD -c "
import sys
sys.path.insert(0, 'src')
from codomyrmex.system_discovery import SystemDiscovery

discovery = SystemDiscovery()
discovery.show_status_dashboard()
"
}

# Run quick demo
run_quick_demo() {
    echo -e "\n${CYAN}🏃 Running Codomyrmex Quick Demo...${NC}"
    PYTHON_CMD=$(get_python_cmd)

    if [[ -f "example_usage.py" ]]; then
        $PYTHON_CMD example_usage.py
    else
        echo -e "${YELLOW}⚠️  example_usage.py not found. Running basic demo...${NC}"
        $PYTHON_CMD -c "
import sys
sys.path.insert(0, 'src')
from codomyrmex.system_discovery import SystemDiscovery

discovery = SystemDiscovery()
discovery.run_demo_workflows()
"
    fi
}

# Run test suite
run_test_suite() {
    echo -e "\n${CYAN}🧪 Running Codomyrmex Test Suite...${NC}"
    if command -v pytest &> /dev/null; then
        pytest testing/ -v --tb=short
    else
        echo -e "${YELLOW}⚠️  pytest not found. Installing...${NC}"
        pip install pytest
        pytest testing/ -v --tb=short
    fi
}

# Browse documentation
browse_documentation() {
    echo -e "\n${CYAN}📚 Codomyrmex Documentation${NC}"
    echo -e "${YELLOW}Available documentation:${NC}"
    find . -name "README.md" -o -name "*.md" | grep -E "(README|API_SPECIFICATION|USAGE|TUTORIAL)" | head -10
    echo -e "\n${GREEN}To build the full documentation website:${NC}"
    echo -e "${CYAN}cd src/codomyrmex/documentation && npm install && npm run build${NC}"
}

# Development tools
run_dev_tools() {
    echo -e "\n${CYAN}🔧 Development Tools${NC}"
    echo -e "${GREEN}1) Run linting (pylint, flake8)${NC}"
    echo -e "${GREEN}2) Format code (black)${NC}"
    echo -e "${GREEN}3) Type checking (mypy)${NC}"
    echo -e "${GREEN}4) Security scan (bandit)${NC}"
    echo -e "${GREEN}5) All of the above${NC}"
    echo ""
    read -p "Choose option (1-5): " dev_choice

    PYTHON_CMD=$(get_python_cmd)

    case $dev_choice in
        1) $PYTHON_CMD -m pylint src/codomyrmex/ --disable=C0114,C0116 ;;
        2) $PYTHON_CMD -m black src/ testing/ ;;
        3) $PYTHON_CMD -m mypy src/codomyrmex/ ;;
        4) $PYTHON_CMD -m bandit -r src/codomyrmex/ ;;
        5)
            echo -e "${CYAN}Running all development tools...${NC}"
            $PYTHON_CMD -m black src/ testing/
            $PYTHON_CMD -m pylint src/codomyrmex/ --disable=C0114,C0116
            $PYTHON_CMD -m mypy src/codomyrmex/
            $PYTHON_CMD -m bandit -r src/codomyrmex/
            ;;
        *) echo -e "${YELLOW}Invalid choice${NC}" ;;
    esac
}

# Interactive shell
run_interactive_shell() {
    echo -e "\n${CYAN}🎮 Entering Interactive Codomyrmex Shell...${NC}"
    PYTHON_CMD=$(get_python_cmd)

    $PYTHON_CMD -c "
import sys
sys.path.insert(0, 'src')
from codomyrmex.terminal_interface import InteractiveShell

shell = InteractiveShell()
shell.run()
"
}

# Export inventory
export_inventory() {
    echo -e "\n${CYAN}📋 Generating System Inventory...${NC}"
    PYTHON_CMD=$(get_python_cmd)

    $PYTHON_CMD -c "
import sys
sys.path.insert(0, 'src')
from codomyrmex.system_discovery import SystemDiscovery

discovery = SystemDiscovery()
discovery.export_full_inventory()
"
}

# Git repository status
check_git_status() {
    echo -e "\n${CYAN}🌐 Git Repository Status${NC}"
    PYTHON_CMD=$(get_python_cmd)

    $PYTHON_CMD -c "
import sys
sys.path.insert(0, 'src')
from codomyrmex.system_discovery import SystemDiscovery

discovery = SystemDiscovery()
discovery.check_git_repositories()
"
}

# Main execution loop
main() {
    show_banner
    check_environment
    activate_venv
    ensure_dependencies
    
    while true; do
        show_menu
        read choice
        
        case $choice in
            1) run_system_discovery ;;
            2) run_status_dashboard ;;
            3) run_quick_demo ;;
            4) run_test_suite ;;
            5) browse_documentation ;;
            6) run_dev_tools ;;
            7) run_interactive_shell ;;
            8) export_inventory ;;
            9) check_git_status ;;
            0) 
                echo -e "\n${CYAN}🐜 Thank you for exploring the Codomyrmex nest!${NC}"
                echo -e "${YELLOW}Until next time, happy foraging! 🌟${NC}\n"
                exit 0
                ;;
            *) 
                echo -e "${RED}Invalid choice. Please select 0-9.${NC}"
                sleep 1
                ;;
        esac
        
        echo -e "\n${PURPLE}Press Enter to continue...${NC}"
        read
    done
}

# Run the main function
main "$@"
