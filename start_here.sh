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
        echo -e "${CYAN}   uv venv .venv && source .venv/bin/activate${NC}"
    fi
}

# Install dependencies if needed
ensure_dependencies() {
    echo -e "${BLUE}🔍 Checking dependencies...${NC}"
    PYTHON_CMD=$(get_python_cmd)

    if ! $PYTHON_CMD -c "import sys; sys.path.insert(0, 'src'); from codomyrmex.system_discovery import SystemDiscovery" 2>/dev/null; then
        echo -e "${YELLOW}📦 Installing dependencies...${NC}"
        if command -v uv &> /dev/null; then
            uv sync || {
                echo -e "${RED}❌ Failed to install dependencies. Please run: uv sync${NC}"
                exit 1
            }
        elif [[ -f ".venv/bin/pip" ]]; then
            .venv/bin/pip install -e . || {
                echo -e "${RED}❌ Failed to install dependencies. Please run: uv sync${NC}"
                exit 1
            }
        elif [[ -f "venv/bin/pip" ]]; then
            venv/bin/pip install -e . || {
                echo -e "${RED}❌ Failed to install dependencies. Please run: uv sync${NC}"
                exit 1
            }
        else
            pip install -e . || {
                echo -e "${RED}❌ Failed to install dependencies. Please run: uv sync${NC}"
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
    echo -e "${GREEN}W)${NC} ⚙️  ${CYAN}Workflow Management${NC} - Create, list, and run workflows"
    echo -e "${GREEN}P)${NC} 📁 ${CYAN}Project Management${NC} - Create and manage projects"
    echo -e "${GREEN}C)${NC} 💻 ${CYAN}CLI Access${NC} - Access Codomyrmex command-line interface"
    echo -e "${GREEN}E)${NC} 📝 ${CYAN}Examples & Tutorials${NC} - Browse and run example scripts"
    echo -e "${GREEN}A)${NC} 🚀 ${CYAN}Install/Update Codomyrmex${NC} - Run UV-optimized installation script"
    echo -e "${GREEN}B)${NC} 🤖 ${CYAN}LLM API Configuration${NC} - Configure AI/LLM API keys and settings"
    echo -e "${GREEN}0)${NC} 🚪 ${CYAN}Exit${NC} - Return to the outside world"
    echo ""
    echo -e "${PURPLE}Choose your path (0-9, W, P, C, E, A, B):${NC} "
}

# Run system discovery
run_system_discovery() {
    echo -e "\n${CYAN}🔍 Scanning the Codomyrmex ecosystem...${NC}"
    PYTHON_CMD=$(get_python_cmd)

    if command -v uv &> /dev/null; then
        uv run python -c "
import sys
sys.path.insert(0, 'src')
from codomyrmex.system_discovery import SystemDiscovery

discovery = SystemDiscovery()
discovery.run_full_discovery()
"
    else
        $PYTHON_CMD -c "
import sys
sys.path.insert(0, 'src')
from codomyrmex.system_discovery import SystemDiscovery

discovery = SystemDiscovery()
discovery.run_full_discovery()
"
    fi
}

# Run status dashboard
run_status_dashboard() {
    echo -e "\n${CYAN}📊 Codomyrmex System Status Dashboard${NC}"
    PYTHON_CMD=$(get_python_cmd)

    if command -v uv &> /dev/null; then
        uv run python -c "
import sys
sys.path.insert(0, 'src')
from codomyrmex.system_discovery import SystemDiscovery

discovery = SystemDiscovery()
discovery.show_status_dashboard()
"
    else
        $PYTHON_CMD -c "
import sys
sys.path.insert(0, 'src')
from codomyrmex.system_discovery import SystemDiscovery

discovery = SystemDiscovery()
discovery.show_status_dashboard()
"
    fi
}

# Run quick demo
run_quick_demo() {
    echo -e "\n${CYAN}🏃 Running Codomyrmex Quick Demo...${NC}"
    PYTHON_CMD=$(get_python_cmd)

    if [[ -f "scripts/development/example_usage.py" ]]; then
        if command -v uv &> /dev/null; then
            uv run python scripts/development/example_usage.py
        else
            $PYTHON_CMD scripts/development/example_usage.py
        fi
    else
        echo -e "${YELLOW}⚠️  scripts/development/example_usage.py not found. Running basic demo...${NC}"
        if command -v uv &> /dev/null; then
            uv run python -c "
import sys
sys.path.insert(0, 'src')
from codomyrmex.system_discovery import SystemDiscovery

discovery = SystemDiscovery()
discovery.run_demo_workflows()
"
        else
            $PYTHON_CMD -c "
import sys
sys.path.insert(0, 'src')
from codomyrmex.system_discovery import SystemDiscovery

discovery = SystemDiscovery()
discovery.run_demo_workflows()
"
        fi
    fi
}

# Run test suite
run_test_suite() {
    echo -e "\n${CYAN}🧪 Running Codomyrmex Test Suite...${NC}"
    if command -v uv &> /dev/null; then
        uv run pytest testing/ -v --tb=short
    elif command -v pytest &> /dev/null; then
        pytest testing/ -v --tb=short
    else
        echo -e "${YELLOW}⚠️  pytest not found. Installing...${NC}"
        uv pip install pytest
        uv run pytest testing/ -v --tb=short
    fi
}

# Browse documentation
browse_documentation() {
    echo -e "\n${CYAN}📚 Codomyrmex Documentation${NC}"
    echo -e "${YELLOW}Available documentation sections:${NC}"
    echo -e "${GREEN}📖 docs/README.md${NC} - Documentation overview"
    echo -e "${GREEN}🚀 docs/getting-started/${NC} - Installation and setup guides"
    echo -e "${GREEN}🏗️  docs/project/${NC} - Architecture and contributing guides"
    echo -e "${GREEN}🔧 docs/development/${NC} - Development environment and testing"
    echo -e "${GREEN}📚 docs/modules/${NC} - Module system documentation"
    echo -e "${GREEN}📋 docs/reference/${NC} - API reference and troubleshooting"
    echo -e ""
    echo -e "${YELLOW}Key documentation files:${NC}"
    find docs/ -name "README.md" -o -name "*.md" | head -10
    echo -e "\n${GREEN}To view documentation:${NC}"
    echo -e "${CYAN}Open docs/ directory in your editor or use: make docs${NC}"
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
        1) uv run pylint src/codomyrmex/ --disable=C0114,C0116 ;;
        2) uv run black src/ testing/ ;;
        3) uv run mypy src/codomyrmex/ ;;
        4) uv run bandit -r src/codomyrmex/ ;;
        5)
            echo -e "${CYAN}Running all development tools...${NC}"
            uv run black src/ testing/
            uv run pylint src/codomyrmex/ --disable=C0114,C0116
            uv run mypy src/codomyrmex/
            uv run bandit -r src/codomyrmex/
            ;;
        *) echo -e "${YELLOW}Invalid choice${NC}" ;;
    esac
}

# Interactive shell
run_interactive_shell() {
    echo -e "\n${CYAN}🎮 Entering Interactive Codomyrmex Shell...${NC}"
    PYTHON_CMD=$(get_python_cmd)

    if command -v uv &> /dev/null; then
        uv run python -c "
import sys
sys.path.insert(0, 'src')
from codomyrmex.terminal_interface import InteractiveShell

shell = InteractiveShell()
shell.run()
"
    else
        $PYTHON_CMD -c "
import sys
sys.path.insert(0, 'src')
from codomyrmex.terminal_interface import InteractiveShell

shell = InteractiveShell()
shell.run()
"
    fi
}

# Export inventory
export_inventory() {
    echo -e "\n${CYAN}📋 Generating System Inventory...${NC}"
    PYTHON_CMD=$(get_python_cmd)

    if command -v uv &> /dev/null; then
        uv run python -c "
import sys
sys.path.insert(0, 'src')
from codomyrmex.system_discovery import SystemDiscovery

discovery = SystemDiscovery()
discovery.export_full_inventory()
"
    else
        $PYTHON_CMD -c "
import sys
sys.path.insert(0, 'src')
from codomyrmex.system_discovery import SystemDiscovery

discovery = SystemDiscovery()
discovery.export_full_inventory()
"
    fi
}

# Git repository status
check_git_status() {
    echo -e "\n${CYAN}🌐 Git Repository Status${NC}"
    PYTHON_CMD=$(get_python_cmd)

    if command -v uv &> /dev/null; then
        uv run python -c "
import sys
sys.path.insert(0, 'src')
from codomyrmex.system_discovery import SystemDiscovery

discovery = SystemDiscovery()
discovery.check_git_repositories()
"
    else
        $PYTHON_CMD -c "
import sys
sys.path.insert(0, 'src')
from codomyrmex.system_discovery import SystemDiscovery

discovery = SystemDiscovery()
discovery.check_git_repositories()
"
    fi
}

# Run installation script
run_installation() {
    echo -e "\n${CYAN}🚀 Running Codomyrmex Installation...${NC}"
    
    INSTALL_SCRIPT="src/codomyrmex/environment_setup/scripts/install_with_uv.sh"
    
    if [[ -f "$INSTALL_SCRIPT" ]]; then
        echo -e "${GREEN}Running UV-optimized installation script...${NC}"
        bash "$INSTALL_SCRIPT"
    else
        echo -e "${RED}❌ Installation script not found at: $INSTALL_SCRIPT${NC}"
        echo -e "${YELLOW}Please ensure the script exists and try again.${NC}"
    fi
}

# LLM API Configuration
configure_llm_apis() {
    echo -e "\n${CYAN}🤖 LLM API Configuration${NC}"
    PYTHON_CMD=$(get_python_cmd)
    
    # Check current API key status
    echo -e "${YELLOW}Checking current API key status...${NC}"
    $PYTHON_CMD -c "
import sys
sys.path.insert(0, 'src')
from codomyrmex.agents.ai_code_editing import validate_api_keys, get_supported_providers

print('\\nCurrent API Key Status:')
providers = get_supported_providers()
api_status = validate_api_keys()

for provider in providers:
    status = '✅ Available' if api_status[provider] else '❌ Missing'
    print(f'  {provider.upper()}: {status}')

print('\\nSupported Providers:', ', '.join(providers))
"
    
    echo -e "\n${GREEN}API Key Configuration Options:${NC}"
    echo -e "${GREEN}1)${NC} Set OpenAI API Key"
    echo -e "${GREEN}2)${NC} Set Anthropic API Key"
    echo -e "${GREEN}3)${NC} Set Google API Key"
    echo -e "${GREEN}4)${NC} Set all API keys interactively"
    echo -e "${GREEN}5)${NC} Test API connections"
    echo -e "${GREEN}6)${NC} Show API usage examples"
    echo -e "${GREEN}0)${NC} Return to main menu"
    echo ""
    read -p "Choose option (0-6): " api_choice
    
    case $api_choice in
        1)
            echo -e "\n${YELLOW}Setting OpenAI API Key...${NC}"
            read -p "Enter your OpenAI API key: " openai_key
            if [[ -n "$openai_key" ]]; then
                export OPENAI_API_KEY="$openai_key"
                echo "export OPENAI_API_KEY=\"$openai_key\"" >> ~/.bashrc
                echo "export OPENAI_API_KEY=\"$openai_key\"" >> ~/.zshrc
                echo -e "${GREEN}✅ OpenAI API key set successfully${NC}"
            else
                echo -e "${RED}❌ No API key provided${NC}"
            fi
            ;;
        2)
            echo -e "\n${YELLOW}Setting Anthropic API Key...${NC}"
            read -p "Enter your Anthropic API key: " anthropic_key
            if [[ -n "$anthropic_key" ]]; then
                export ANTHROPIC_API_KEY="$anthropic_key"
                echo "export ANTHROPIC_API_KEY=\"$anthropic_key\"" >> ~/.bashrc
                echo "export ANTHROPIC_API_KEY=\"$anthropic_key\"" >> ~/.zshrc
                echo -e "${GREEN}✅ Anthropic API key set successfully${NC}"
            else
                echo -e "${RED}❌ No API key provided${NC}"
            fi
            ;;
        3)
            echo -e "\n${YELLOW}Setting Google API Key...${NC}"
            read -p "Enter your Google API key: " google_key
            if [[ -n "$google_key" ]]; then
                export GOOGLE_API_KEY="$google_key"
                echo "export GOOGLE_API_KEY=\"$google_key\"" >> ~/.bashrc
                echo "export GOOGLE_API_KEY=\"$google_key\"" >> ~/.zshrc
                echo -e "${GREEN}✅ Google API key set successfully${NC}"
            else
                echo -e "${RED}❌ No API key provided${NC}"
            fi
            ;;
        4)
            echo -e "\n${YELLOW}Setting all API keys...${NC}"
            read -p "Enter your OpenAI API key (or press Enter to skip): " openai_key
            read -p "Enter your Anthropic API key (or press Enter to skip): " anthropic_key
            read -p "Enter your Google API key (or press Enter to skip): " google_key
            
            if [[ -n "$openai_key" ]]; then
                export OPENAI_API_KEY="$openai_key"
                echo "export OPENAI_API_KEY=\"$openai_key\"" >> ~/.bashrc
                echo "export OPENAI_API_KEY=\"$openai_key\"" >> ~/.zshrc
                echo -e "${GREEN}✅ OpenAI API key set${NC}"
            fi
            
            if [[ -n "$anthropic_key" ]]; then
                export ANTHROPIC_API_KEY="$anthropic_key"
                echo "export ANTHROPIC_API_KEY=\"$anthropic_key\"" >> ~/.bashrc
                echo "export ANTHROPIC_API_KEY=\"$anthropic_key\"" >> ~/.zshrc
                echo -e "${GREEN}✅ Anthropic API key set${NC}"
            fi
            
            if [[ -n "$google_key" ]]; then
                export GOOGLE_API_KEY="$google_key"
                echo "export GOOGLE_API_KEY=\"$google_key\"" >> ~/.bashrc
                echo "export GOOGLE_API_KEY=\"$google_key\"" >> ~/.zshrc
                echo -e "${GREEN}✅ Google API key set${NC}"
            fi
            ;;
        5)
            echo -e "\n${YELLOW}Testing API connections...${NC}"
            $PYTHON_CMD -c "
import sys
sys.path.insert(0, 'src')
from codomyrmex.agents.ai_code_editing import validate_api_keys, get_llm_client

api_status = validate_api_keys()
print('\\nTesting API connections...')

for provider, available in api_status.items():
    if available:
        try:
            client, model = get_llm_client(provider)
            print(f'✅ {provider.upper()}: Connection successful (model: {model})')
        except Exception as e:
            print(f'❌ {provider.upper()}: Connection failed - {e}')
    else:
        print(f'⚠️  {provider.upper()}: No API key configured')
"
            ;;
        6)
            echo -e "\n${YELLOW}API Usage Examples:${NC}"
            $PYTHON_CMD -c "
import sys
sys.path.insert(0, 'src')
from codomyrmex.agents.ai_code_editing import generate_code_snippet, get_supported_languages, get_available_models

print('\\nExample: Generate Python code')
print('=' * 50)
try:
    result = generate_code_snippet(
        prompt='Create a function that calculates fibonacci numbers',
        language='python',
        provider='openai'
    )
    print('Generated code:')
    print(result['generated_code'])
    print(f'\\nExecution time: {result[\"execution_time\"]:.2f}s')
    print(f'Tokens used: {result.get(\"tokens_used\", \"N/A\")}')
except Exception as e:
    print(f'Error: {e}')
    print('\\nMake sure you have set up your API keys first!')

print('\\n\\nSupported Languages:')
languages = get_supported_languages()
for i, lang in enumerate(languages[:10]):  # Show first 10
    print(f'  {lang.value}')
if len(languages) > 10:
    print(f'  ... and {len(languages) - 10} more')

print('\\n\\nAvailable Models:')
for provider in ['openai', 'anthropic', 'google']:
    models = get_available_models(provider)
    print(f'{provider.upper()}: {', '.join(models)}')
"
            ;;
        0)
            return
            ;;
        *)
            echo -e "${RED}Invalid choice${NC}"
            ;;
    esac
    
    echo -e "\n${PURPLE}Press Enter to continue...${NC}"
    read
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
            A|a) run_installation ;;
            B|b) configure_llm_apis ;;
            0) 
                echo -e "\n${CYAN}🐜 Thank you for exploring the Codomyrmex nest!${NC}"
                echo -e "${YELLOW}Until next time, happy foraging! 🌟${NC}\n"
                exit 0
                ;;
            *) 
                echo -e "${RED}Invalid choice. Please select 0-9, A, or B.${NC}"
                sleep 1
                ;;
        esac
        
        echo -e "\n${PURPLE}Press Enter to continue...${NC}"
        read
    done
}

# Run the main function
main "$@"
