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

# Helper function to check if uv is available
check_uv() {
    if ! command -v uv &> /dev/null; then
        echo -e "${RED}❌ Error: uv is required but not found!${NC}"
        echo -e "${YELLOW}Please install uv: curl -LsSf https://astral.sh/uv/install.sh | sh${NC}"
        exit 1
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
    check_uv
    if [[ -d ".venv" ]]; then
        echo -e "${GREEN}🔄 Virtual environment detected${NC}"
    else
        echo -e "${YELLOW}📦 Creating virtual environment...${NC}"
        uv venv .venv || {
            echo -e "${RED}❌ Failed to create virtual environment${NC}"
            exit 1
        }
    fi
}

# Install dependencies if needed
ensure_dependencies() {
    echo -e "${BLUE}🔍 Checking dependencies...${NC}"
    check_uv

    if ! uv run python -c "import sys; sys.path.insert(0, 'src'); from codomyrmex.system_discovery import SystemDiscovery" 2>/dev/null; then
        echo -e "${YELLOW}📦 Installing dependencies...${NC}"
            uv sync || {
                echo -e "${RED}❌ Failed to install dependencies. Please run: uv sync${NC}"
                exit 1
            }
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
    check_uv

    uv run python -c "
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
    check_uv

    uv run python -c "
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
    check_uv

    if [[ -f "scripts/documentation/examples/basic_usage.py" ]]; then
        uv run python scripts/documentation/examples/basic_usage.py
    else
        echo -e "${YELLOW}⚠️  scripts/documentation/examples/basic_usage.py not found. Running basic demo...${NC}"
        uv run python -c "
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
    check_uv
    
    uv run pytest src/codomyrmex/tests/ -v --tb=short
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
    check_uv
    
    echo -e "${GREEN}1) Run linting (ruff)${NC}"
    echo -e "${GREEN}2) Format code (ruff format)${NC}"
    echo -e "${GREEN}3) Type checking (mypy)${NC}"
    echo -e "${GREEN}4) Security scan (bandit)${NC}"
    echo -e "${GREEN}5) All of the above${NC}"
    echo ""
    read -p "Choose option (1-5): " dev_choice

    case $dev_choice in
        1) uv run ruff check src/codomyrmex/ ;;
        2) uv run ruff format src/codomyrmex/ ;;
        3) uv run mypy src/codomyrmex/ ;;
        4) uv run bandit -r src/codomyrmex/ ;;
        5)
            echo -e "${CYAN}Running all development tools...${NC}"
            uv run ruff format src/codomyrmex/
            uv run ruff check src/codomyrmex/
            uv run mypy src/codomyrmex/
            uv run bandit -r src/codomyrmex/
            ;;
        *) echo -e "${YELLOW}Invalid choice${NC}" ;;
    esac
}

# Interactive shell
run_interactive_shell() {
    echo -e "\n${CYAN}🎮 Entering Interactive Codomyrmex Shell...${NC}"
    check_uv

    uv run python -c "
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
    check_uv

    uv run python -c "
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
    check_uv

    uv run python -c "
import sys
sys.path.insert(0, 'src')
from codomyrmex.system_discovery import SystemDiscovery

discovery = SystemDiscovery()
discovery.check_git_repositories()
"
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
    check_uv
    
    # Check current API key status
    echo -e "${YELLOW}Checking current API key status...${NC}"
    uv run python -c "
import sys
sys.path.insert(0, 'src')
try:
    from codomyrmex.agents.ai_code_editing import validate_api_keys, get_supported_providers
    
    print('\\nCurrent API Key Status:')
    providers = get_supported_providers()
    api_status = validate_api_keys()
    
    for provider in providers:
        status = '✅ Available' if api_status[provider] else '❌ Missing'
        print(f'  {provider.upper()}: {status}')
    
    print('\\nSupported Providers:', ', '.join(providers))
except ImportError as e:
    print(f'⚠️  AI code editing module not available: {e}')
    print('\\nYou can still set API keys manually in your .env file:')
    print('  OPENAI_API_KEY=sk-...')
    print('  ANTHROPIC_API_KEY=sk-ant-...')
    print('  GOOGLE_API_KEY=...')
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
            uv run python -c "
import sys
sys.path.insert(0, 'src')
try:
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
except ImportError as e:
    print(f'⚠️  AI code editing module not available: {e}')
"
            ;;
        6)
            echo -e "\n${YELLOW}API Usage Examples:${NC}"
            uv run python -c "
import sys
sys.path.insert(0, 'src')
try:
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
except ImportError as e:
    print(f'⚠️  AI code editing module not available: {e}')
    print('\\nSee docs/getting-started/quickstart.md for setup instructions')
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

# Workflow management
run_workflow_management() {
    echo -e "\n${CYAN}⚙️  Workflow Management${NC}"
    check_uv
    
    echo -e "${GREEN}1)${NC} List available workflows"
    echo -e "${GREEN}2)${NC} Create a new workflow"
    echo -e "${GREEN}3)${NC} Run a workflow"
    echo -e "${GREEN}4)${NC} Show orchestration status"
    echo -e "${GREEN}0)${NC} Return to main menu"
    echo ""
    read -p "Choose option (0-4): " wf_choice
    
    case $wf_choice in
        1)
            uv run codomyrmex workflow list
            ;;
        2)
            read -p "Enter workflow name: " wf_name
            read -p "Enter template (optional, press Enter to skip): " wf_template
            if [[ -n "$wf_template" ]]; then
                uv run codomyrmex workflow create "$wf_name" --template "$wf_template"
            else
                uv run codomyrmex workflow create "$wf_name"
            fi
            ;;
        3)
            read -p "Enter workflow name to run: " wf_name
            uv run codomyrmex workflow run "$wf_name"
            ;;
        4)
            uv run codomyrmex orchestration status
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

# Project management
run_project_management() {
    echo -e "\n${CYAN}📁 Project Management${NC}"
    check_uv
    
    echo -e "${GREEN}1)${NC} List available projects"
    echo -e "${GREEN}2)${NC} Create a new project"
    echo -e "${GREEN}0)${NC} Return to main menu"
    echo ""
    read -p "Choose option (0-2): " proj_choice
    
    case $proj_choice in
        1)
            uv run codomyrmex project list
            ;;
        2)
            read -p "Enter project name: " proj_name
            read -p "Enter template (ai_analysis, web_application, data_pipeline) [default: ai_analysis]: " proj_template
            proj_template=${proj_template:-ai_analysis}
            
            uv run codomyrmex project create "$proj_name" --template "$proj_template"
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

# CLI access
run_cli_access() {
    echo -e "\n${CYAN}💻 Codomyrmex CLI Access${NC}"
    check_uv
    
    echo -e "${GREEN}Available CLI commands:${NC}"
    echo -e "  ${CYAN}codomyrmex check${NC} - Check environment setup"
    echo -e "  ${CYAN}codomyrmex info${NC} - Show project information"
    echo -e "  ${CYAN}codomyrmex modules${NC} - List all available modules"
    echo -e "  ${CYAN}codomyrmex status${NC} - Show system status dashboard"
    echo -e "  ${CYAN}codomyrmex shell${NC} - Launch interactive shell"
    echo -e "  ${CYAN}codomyrmex workflow list${NC} - List workflows"
    echo -e "  ${CYAN}codomyrmex project list${NC} - List projects"
    echo -e "  ${CYAN}codomyrmex ai generate \"prompt\"${NC} - Generate code with AI"
    echo ""
    echo -e "${YELLOW}Enter a CLI command (or 'help' for full help, 'exit' to return):${NC}"
    
    while true; do
        read -p "${CYAN}codomyrmex>${NC} " cli_cmd
        
        if [[ "$cli_cmd" == "exit" || "$cli_cmd" == "quit" || "$cli_cmd" == "q" ]]; then
            break
        elif [[ "$cli_cmd" == "help" || "$cli_cmd" == "h" ]]; then
            uv run codomyrmex --help
        elif [[ -n "$cli_cmd" ]]; then
            uv run codomyrmex $cli_cmd
        fi
    done
}

# Examples and tutorials
run_examples_tutorials() {
    echo -e "\n${CYAN}📝 Examples & Tutorials${NC}"
    check_uv
    
    echo -e "${GREEN}1)${NC} Run example usage script"
    echo -e "${GREEN}2)${NC} Browse example scripts directory"
    echo -e "${GREEN}3)${NC} Run example selector"
    echo -e "${GREEN}4)${NC} View tutorials documentation"
    echo -e "${GREEN}0)${NC} Return to main menu"
    echo ""
    read -p "Choose option (0-4): " ex_choice
    
    case $ex_choice in
        1)
            if [[ -f "scripts/documentation/examples/basic_usage.py" ]]; then
                uv run python scripts/documentation/examples/basic_usage.py
            else
                echo -e "${YELLOW}⚠️  Example script not found at scripts/documentation/examples/basic_usage.py${NC}"
            fi
            ;;
        2)
            if [[ -d "scripts/documentation/examples" ]]; then
                echo -e "${CYAN}Available example scripts:${NC}"
                find scripts/documentation/examples -name "*.sh" -o -name "*.py" | head -20
                echo ""
                echo -e "${YELLOW}To run an example, navigate to scripts/documentation/examples/ and execute the script${NC}"
            else
                echo -e "${YELLOW}⚠️  Examples directory not found at scripts/documentation/examples${NC}"
            fi
            ;;
        3)
            echo -e "${GREEN}Select an example to run:${NC}"
            echo -e "1) Basic Usage"
            echo -e "2) Advanced Workflow"
            read -p "Choice (1-2): " ex_sel
            
            if [[ "$ex_sel" == "1" ]]; then
                uv run python scripts/documentation/examples/basic_usage.py
            elif [[ "$ex_sel" == "2" ]]; then
                uv run python scripts/documentation/examples/advanced_workflow.py
            else
                echo -e "${RED}Invalid selection${NC}"
            fi
            ;;
        4)
            TUTORIAL_DOC="docs/getting-started/tutorials/README.md"
            if [[ -f "$TUTORIAL_DOC" ]]; then
                if command -v less &> /dev/null; then
                    less "$TUTORIAL_DOC"
                else
                    cat "$TUTORIAL_DOC"
                fi
                echo -e "\n${CYAN}Check 'docs/getting-started/tutorials/' for more guides!${NC}"
            else
                echo -e "${YELLOW}⚠️  Tutorials documentation not found at $TUTORIAL_DOC${NC}"
            fi
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
    check_uv
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
            W|w) run_workflow_management ;;
            P|p) run_project_management ;;
            C|c) run_cli_access ;;
            E|e) run_examples_tutorials ;;
            A|a) run_installation ;;
            B|b) configure_llm_apis ;;
            0) 
                echo -e "\n${CYAN}🐜 Thank you for exploring the Codomyrmex nest!${NC}"
                echo -e "${YELLOW}Until next time, happy foraging! 🌟${NC}\n"
                exit 0
                ;;
            *) 
                echo -e "${RED}Invalid choice. Please select 0-9, W, P, C, E, A, or B.${NC}"
                sleep 1
                ;;
        esac
        
        echo -e "\n${PURPLE}Press Enter to continue...${NC}"
        read
    done
}

# Run the main function
main "$@"
