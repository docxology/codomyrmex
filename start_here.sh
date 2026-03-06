#!/bin/bash
# 🐜 Codomyrmex Orchestrator - Your Gateway to the Epistemic Forager Nest
# Ultimate Thin Orchestrator encompassing dynamic script discovery, PAI, Agents, and Frameworks.

set -e  # Exit on any error

# Colors for terminal output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
WHITE='\033[1;37m'
NC='\033[0m'

# Helper function to check if uv is available
check_uv() {
    if ! command -v uv &> /dev/null; then
        echo -e "${RED}❌ Error: uv is required but not found!${NC}"
        echo -e "${YELLOW}Please install uv: curl -LsSf https://astral.sh/uv/install.sh | sh${NC}"
        exit 1
    fi
}

show_banner() {
    clear
    echo -e "${CYAN}"
    cat << "EOF"
    ╔═══════════════════════════════════════════════════════════════╗
    ║                                                               ║
    ║   🐜 CODOMYRMEX - Epistemic Forager Orchestrator 🐜         ║
    ║   The Ultimate Thin Gateway to all Agents and Modules        ║
    ║                                                               ║
    ╚═══════════════════════════════════════════════════════════════╝
EOF
    echo -e "${NC}"
}

check_environment() {
    if [[ ! -f "pyproject.toml" ]] || [[ ! -d "src/codomyrmex" ]]; then
        echo -e "${RED}❌ Error: Not in the Codomyrmex project root directory!${NC}"
        echo -e "${YELLOW}Please run this script from the main codomyrmex directory.${NC}"
        exit 1
    fi
}

activate_venv() {
    check_uv
    if [[ ! -d ".venv" ]]; then
        echo -e "${YELLOW}📦 Creating virtual environment...${NC}"
        uv venv .venv || {
            echo -e "${RED}❌ Failed to create virtual environment${NC}"
            exit 1
        }
    fi
}

ensure_dependencies() {
    check_uv
    if ! uv run python -c "import sys; sys.path.insert(0, 'src'); from codomyrmex.system_discovery import SystemDiscovery" 2>/dev/null; then
        echo -e "${YELLOW}📦 Installing dependencies...${NC}"
        uv sync || {
            echo -e "${RED}❌ Failed to install dependencies. Please run: uv sync${NC}"
            exit 1
        }
    fi
}

pause() {
    echo -e "\n${PURPLE}Press Enter to continue...${NC}"
    read -r
}

# ==========================================
# 🔍 1. System Discovery Submenu
# ==========================================
menu_discovery() {
    while true; do
        clear
        echo -e "${CYAN}🔍 System Discovery & Status${NC}\n"
        echo -e "${GREEN}1)${NC} Run Full System Discovery"
        echo -e "${GREEN}2)${NC} View System Status Dashboard"
        echo -e "${GREEN}3)${NC} Export Full System Inventory"
        echo -e "${GREEN}4)${NC} Check Git Repositories Status"
        echo -e "${GREEN}0)${NC} Back to Main Menu"
        echo ""
        read -p "Choose option (0-4): " choice
        
        case $choice in
            1)
                echo -e "\n${CYAN}Scanning the Codomyrmex ecosystem...${NC}"
                uv run python -c "import sys; sys.path.insert(0, 'src'); from codomyrmex.system_discovery import SystemDiscovery; SystemDiscovery().run_full_discovery()"
                pause
                ;;
            2)
                uv run python -c "import sys; sys.path.insert(0, 'src'); from codomyrmex.system_discovery import SystemDiscovery; SystemDiscovery().show_status_dashboard()"
                pause
                ;;
            3)
                uv run python -c "import sys; sys.path.insert(0, 'src'); from codomyrmex.system_discovery import SystemDiscovery; SystemDiscovery().export_full_inventory()"
                pause
                ;;
            4)
                uv run python -c "import sys; sys.path.insert(0, 'src'); from codomyrmex.system_discovery import SystemDiscovery; SystemDiscovery().check_git_repositories()"
                pause
                ;;
            0) return ;;
            *) echo -e "${RED}Invalid choice${NC}"; sleep 1 ;;
        esac
    done
}

# ==========================================
# 🖥️ 2. PAI Submenu
# ==========================================
menu_pai() {
    while true; do
        clear
        echo -e "${CYAN}🖥️ Personal AI Infrastructure (PAI)${NC}\n"
        echo -e "${GREEN}1)${NC} Launch PAI Dashboard (Browser)"
        echo -e "${GREEN}2)${NC} Generate/Update Module Skills"
        echo -e "${GREEN}3)${NC} Validate PAI Integration"
        echo -e "${GREEN}4)${NC} Update PAI Knowledge Documentation"
        echo -e "${GREEN}0)${NC} Back to Main Menu"
        echo ""
        read -p "Choose option (0-4): " choice
        
        case $choice in
            1) uv run python scripts/pai/dashboard.py; pause ;;
            2) uv run python scripts/pai/generate_skills.py; pause ;;
            3) uv run python scripts/pai/validate_pai_integration.py; pause ;;
            4) uv run python scripts/pai/update_pai_docs.py; pause ;;
            0) return ;;
            *) echo -e "${RED}Invalid choice${NC}"; sleep 1 ;;
        esac
    done
}

# ==========================================
# 🧠 3. AI Agents & Swarms Submenu
# ==========================================
menu_agents() {
    while true; do
        clear
        echo -e "${CYAN}🧠 AI Agents & Swarms${NC}\n"
        echo -e "${GREEN}1)${NC} Multi-Agent Collaborative Workflow"
        echo -e "${GREEN}2)${NC} Discursive Debate Simulation"
        echo -e "${GREEN}3)${NC} Run All Agents (Full Sweep)"
        echo -e "${GREEN}4)${NC} Agent Status & Diagnostics"
        echo -e "${GREEN}5)${NC} Agent Model Comparison"
        echo -e "${GREEN}6)${NC} Recursive Task Strategy Engine"
        echo -e "${GREEN}0)${NC} Back to Main Menu"
        echo ""
        read -p "Choose option (0-6): " choice
        
        case $choice in
            1) uv run python scripts/agents/multi_agent_workflow.py; pause ;;
            2) uv run python scripts/agents/discursive_debate.py; pause ;;
            3) uv run python scripts/agents/run_all_agents.py; pause ;;
            4) uv run python scripts/agents/agent_diagnostics.py; pause ;;
            5) uv run python scripts/agents/agent_comparison.py; pause ;;
            6) uv run python scripts/agents/recursive_task.py; pause ;;
            0) return ;;
            *) echo -e "${RED}Invalid choice${NC}"; sleep 1 ;;
        esac
    done
}

# ==========================================
# 🧬 4. Specialized Frameworks
# ==========================================
menu_frameworks() {
    while true; do
        clear
        echo -e "${CYAN}🧬 Specialized Frameworks & Verticals${NC}\n"
        echo -e "${GREEN}1)${NC} MetaInformAnt Bio-Simulation / Colony"
        echo -e "${GREEN}2)${NC} Data Visualization Demos"
        echo -e "${GREEN}3)${NC} Advanced Orchestrator Workflows"
        echo -e "${GREEN}0)${NC} Back to Main Menu"
        echo ""
        read -p "Choose option (0-3): " choice
        
        case $choice in
            1) 
                if [ -f "scripts/bio_simulation/run_colony.py" ]; then
                    uv run python scripts/bio_simulation/run_colony.py
                else
                    echo "Script not found."
                fi
                pause 
                ;;
            2) 
                if [ -d "scripts/data_visualization" ]; then
                    files=(scripts/data_visualization/*.py)
                    if [ ${#files[@]} -gt 0 ] && [ -f "${files[0]}" ]; then
                        echo -e "${YELLOW}Running: ${files[0]}${NC}"
                        uv run python "${files[0]}"
                    else
                        echo "No data visualization scripts found."
                    fi
                else
                    echo "Module not found."
                fi
                pause 
                ;;
            3) 
                uv run python scripts/agents/advanced_workflow.py; pause 
                ;;
            0) return ;;
            *) echo -e "${RED}Invalid choice${NC}"; sleep 1 ;;
        esac
    done
}

# ==========================================
# 🗄️ 5. Dynamic Script Explorer
# ==========================================
dynamic_script_explorer() {
    while true; do
        clear
        echo -e "${CYAN}🗄️ Dynamic Script Explorer${NC}"
        echo -e "Dynamically discover and execute ANY script across $PWD/scripts\n"
        
        # Discover all subdirectories in scripts/
        mapfile -t domains < <(find scripts -mindepth 1 -maxdepth 1 -type d -exec basename {} \; | sort)
        
        if [ ${#domains[@]} -eq 0 ]; then
            echo -e "${YELLOW}No script domains found in scripts/.${NC}"
            pause
            return
        fi

        for i in "${!domains[@]}"; do
            printf "${GREEN}%2d)${NC} %s\n" $((i+1)) "${domains[$i]}"
        done
        echo -e "${GREEN} 0)${NC} Back to Main Menu"
        echo ""
        read -p "Select a domain to explore (0-${#domains[@]}): " domain_idx
        
        if [[ "$domain_idx" == "0" ]]; then
            return
        elif [[ "$domain_idx" =~ ^[0-9]+$ ]] && [ "$domain_idx" -ge 1 ] && [ "$domain_idx" -le "${#domains[@]}" ]; then
            selected_domain="${domains[$((domain_idx-1))]}"
            
            while true; do
                clear
                echo -e "${CYAN}🗄️ Domain :: ${selected_domain}${NC}\n"
                # Find python/sh scripts
                mapfile -t scr_files < <(find "scripts/${selected_domain}" -maxdepth 1 \( -name "*.py" -o -name "*.sh" \) -exec basename {} \; | sort)
                
                if [ ${#scr_files[@]} -eq 0 ]; then
                    echo -e "${YELLOW}No executable .py or .sh scripts found in this domain.${NC}"
                    pause
                    break
                fi

                for j in "${!scr_files[@]}"; do
                    printf "${GREEN}%2d)${NC} %s\n" $((j+1)) "${scr_files[$j]}"
                done
                echo -e "${GREEN} 0)${NC} Back to Domains"
                echo ""
                read -p "Select a script to run (0-${#scr_files[@]}): " script_idx
                
                if [[ "$script_idx" == "0" ]]; then
                    break
                elif [[ "$script_idx" =~ ^[0-9]+$ ]] && [ "$script_idx" -ge 1 ] && [ "$script_idx" -le "${#scr_files[@]}" ]; then
                    target_script="scripts/${selected_domain}/${scr_files[$((script_idx-1))]}"
                    echo -e "\n${YELLOW}Executing: $target_script...${NC}\n"
                    if [[ "$target_script" == *.py ]]; then
                        uv run python "$target_script"
                    elif [[ "$target_script" == *.sh ]]; then
                        bash "$target_script"
                    fi
                    pause
                else
                    echo -e "${RED}Invalid choice${NC}"; sleep 1
                fi
            done
        else
            echo -e "${RED}Invalid choice${NC}"; sleep 1
        fi
    done
}

# ==========================================
# 🧪 6. Testing & Development
# ==========================================
menu_testing_dev() {
    while true; do
        clear
        echo -e "${CYAN}🧪 Testing & Development${NC}\n"
        echo -e "${GREEN}1)${NC} Run Full Test Suite (pytest)"
        echo -e "${GREEN}2)${NC} Run Fast Tests (No Coverage)"
        echo -e "${GREEN}3)${NC} Code Formatting (ruff format)"
        echo -e "${GREEN}4)${NC} Code Linting (ruff check)"
        echo -e "${GREEN}5)${NC} Type Checking (ty check)"
        echo -e "${GREEN}6)${NC} Security Scan (bandit)"
        echo -e "${GREEN}7)${NC} Run All Dev Tools (Format, Lint, Type, Security)"
        echo -e "${GREEN}0)${NC} Back to Main Menu"
        echo ""
        read -p "Choose option (0-7): " choice
        
        case $choice in
            1) make test; pause ;;
            2) make test-fast; pause ;;
            3) uv run ruff format src/codomyrmex/; pause ;;
            4) uv run ruff check src/codomyrmex/; pause ;;
            5) uv run ty check src/; pause ;;
            6) uv run bandit -r src/codomyrmex/; pause ;;
            7) 
                uv run ruff format src/codomyrmex/
                uv run ruff check src/codomyrmex/
                uv run ty check src/
                uv run bandit -r src/codomyrmex/
                pause
                ;;
            0) return ;;
            *) echo -e "${RED}Invalid choice${NC}"; sleep 1 ;;
        esac
    done
}

# ==========================================
# ⚙️ 8. Configuration & Setup
# ==========================================
menu_config() {
    clear
    echo -e "${CYAN}⚙️ Configuration & Setup${NC}\n"
    INSTALL_SCRIPT="src/codomyrmex/environment_setup/scripts/install_with_uv.sh"
    
    echo -e "${GREEN}1)${NC} Run UV Installation Script"
    echo -e "${GREEN}2)${NC} Configure LLM API Keys"
    echo -e "${GREEN}0)${NC} Back to Main Menu"
    echo ""
    read -p "Choose option (0-2): " choice
    
    case $choice in
        1)
            if [[ -f "$INSTALL_SCRIPT" ]]; then
                bash "$INSTALL_SCRIPT"
            else
                echo -e "${RED}Install script not found.${NC}"
            fi
            pause ;;
        2)
            uv run python -c "
import sys
sys.path.insert(0, 'src')
try:
    from codomyrmex.agents.ai_code_editing import validate_api_keys
    print('Testing API Keys...')
    status = validate_api_keys()
    for provider, avail in status.items():
        print(f'{provider}: {\"✅ Available\" if avail else \"❌ Missing\"}')
    print('\\nTo configure, please set OPENAI_API_KEY, ANTHROPIC_API_KEY, or GOOGLE_API_KEY in your environment or .env file.')
except ImportError as e:
    print(f'Cannot load API key validator: {e}')"
            pause ;;
        0) return ;;
        *) echo -e "${RED}Invalid choice${NC}"; sleep 1 ;;
    esac
}

# ==========================================
# 💻 9. Interactive Tools
# ==========================================
menu_interactive() {
    while true; do
        clear
        echo -e "${CYAN}💻 Interactive Tools${NC}\n"
        echo -e "${GREEN}1)${NC} Enter Interactive Python Shell"
        echo -e "${GREEN}2)${NC} Codomyrmex CLI Engine"
        echo -e "${GREEN}3)${NC} Run Demo Workflows"
        echo -e "${GREEN}0)${NC} Back to Main Menu"
        echo ""
        read -p "Choose option (0-3): " choice
        case $choice in
            1)
                uv run python -c "
import sys
sys.path.insert(0, 'src')
from codomyrmex.terminal_interface import InteractiveShell
shell = InteractiveShell()
shell.run()
"
                ;;
            2)
                echo -e "Enter CLI command (e.g. status, info, help) or type exit to return:"
                while true; do
                    read -p "codomyrmex> " cli_cmd
                    if [[ "$cli_cmd" == "exit" ]]; then break; fi
                    if [[ -n "$cli_cmd" ]]; then uv run codomyrmex $cli_cmd; fi
                done
                ;;
            3)
                uv run python -c "
import sys
sys.path.insert(0, 'src')
from codomyrmex.system_discovery import SystemDiscovery
SystemDiscovery().run_demo_workflows()
"
                pause ;;
            0) return ;;
            *) echo -e "${RED}Invalid choice${NC}"; sleep 1 ;;
        esac
    done
}

# ==========================================
# MAIN MENU LOOP
# ==========================================
main() {
    check_environment
    activate_venv
    ensure_dependencies
    
    while true; do
        show_banner
        echo -e "${WHITE}🚀 Welcome to the Epistemic Forager Nest${NC}\n"
        
        echo -e "${GREEN}1)${NC} 🔍 ${CYAN}System Discovery & Status${NC}"
        echo -e "${GREEN}2)${NC} 🖥️  ${CYAN}Personal AI Infrastructure (PAI)${NC}"
        echo -e "${GREEN}3)${NC} 🧠 ${CYAN}AI Agents & Swarms${NC}"
        echo -e "${GREEN}4)${NC} 🧬 ${CYAN}Specialized Frameworks${NC}"
        echo -e "${GREEN}5)${NC} 🗄️  ${CYAN}Dynamic Script Explorer (All Scripts)${NC}"
        echo -e "${GREEN}6)${NC} 🧪 ${CYAN}Testing & Development${NC}"
        echo -e "${GREEN}7)${NC} 📚 ${CYAN}Documentation & Examples${NC}"
        echo -e "${GREEN}8)${NC} ⚙️  ${CYAN}Configuration & Setup${NC}"
        echo -e "${GREEN}9)${NC} 💻 ${CYAN}Interactive Tools & CLI${NC}"
        echo -e "${GREEN}0)${NC} 🚪 ${CYAN}Exit${NC}"
        echo ""
        read -p "$(echo -e ${PURPLE}Choose your path \(0-9\):${NC} )" main_choice
        
        case $main_choice in
            1) menu_discovery ;;
            2) menu_pai ;;
            3) menu_agents ;;
            4) menu_frameworks ;;
            5) dynamic_script_explorer ;;
            6) menu_testing_dev ;;
            7) 
                echo -e "${YELLOW}Key documentation files:${NC}"
                find docs/ -name "README.md" -o -name "*.md" | head -10
                pause
                ;;
            8) menu_config ;;
            9) menu_interactive ;;
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
    done
}

main "$@"
