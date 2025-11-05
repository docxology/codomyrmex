#!/bin/bash
# 🚀 Codomyrmex Installation Script - UV Optimized
# This script provides the fastest and most reliable installation using uv

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
WHITE='\033[1;37m'
NC='\033[0m' # No Color

# ASCII Art Banner
show_banner() {
    echo -e "${CYAN}"
    cat << "EOF"
    ╔═══════════════════════════════════════════════════════════════╗
    ║                                                               ║
    ║   🐜 CODOMYRMEX - UV OPTIMIZED INSTALLATION 🐜              ║
    ║   Fast, Reliable, and Modern Python Package Management       ║
    ║                                                               ║
    ╚═══════════════════════════════════════════════════════════════╝
EOF
    echo -e "${NC}"
}

# Check if uv is installed
check_uv() {
    echo -e "${BLUE}🔍 Checking for uv package manager...${NC}"
    
    if command -v uv &> /dev/null; then
        UV_VERSION=$(uv --version | cut -d' ' -f2)
        echo -e "${GREEN}✅ uv is installed (version: $UV_VERSION)${NC}"
        return 0
    else
        echo -e "${YELLOW}⚠️  uv is not installed. Installing uv...${NC}"
        install_uv
    fi
}

# Install uv
install_uv() {
    echo -e "${BLUE}📦 Installing uv package manager...${NC}"
    
    # Install uv using the official installer
    curl -LsSf https://astral.sh/uv/install.sh | sh
    
    # Add to PATH for current session
    export PATH="$HOME/.cargo/bin:$PATH"
    
    # Verify installation
    if command -v uv &> /dev/null; then
        UV_VERSION=$(uv --version | cut -d' ' -f2)
        echo -e "${GREEN}✅ uv installed successfully (version: $UV_VERSION)${NC}"
    else
        echo -e "${RED}❌ Failed to install uv. Please install manually from https://github.com/astral-sh/uv${NC}"
        exit 1
    fi
}

# Check Python version
check_python() {
    echo -e "${BLUE}🐍 Checking Python version...${NC}"
    
    # Check if Python 3.10+ is available
    if command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
        PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d'.' -f1)
        PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d'.' -f2)
        
        if [ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -ge 10 ]; then
            echo -e "${GREEN}✅ Python $PYTHON_VERSION is compatible${NC}"
        else
            echo -e "${YELLOW}⚠️  Python $PYTHON_VERSION detected. Codomyrmex requires Python 3.10+${NC}"
            echo -e "${BLUE}🔧 uv will automatically install a compatible Python version${NC}"
        fi
    else
        echo -e "${YELLOW}⚠️  Python not found. uv will install a compatible version${NC}"
    fi
}

# Install Codomyrmex with uv
install_codomyrmex() {
    echo -e "${BLUE}🚀 Installing Codomyrmex with uv...${NC}"
    
    # Create virtual environment and install
    echo -e "${CYAN}Creating virtual environment...${NC}"
    uv venv .venv
    
    echo -e "${CYAN}Activating virtual environment...${NC}"
    source .venv/bin/activate
    
    echo -e "${CYAN}Installing Codomyrmex and dependencies...${NC}"
    uv sync
    
    echo -e "${GREEN}✅ Codomyrmex installed successfully!${NC}"
}

# Verify installation
verify_installation() {
    echo -e "${BLUE}🔍 Verifying installation...${NC}"
    
    # Activate virtual environment
    source .venv/bin/activate
    
    # Test basic import
    echo -e "${CYAN}Testing basic imports...${NC}"
    python3 -c "
import sys
sys.path.insert(0, 'src')
try:
    import codomyrmex
    print('✅ Codomyrmex package imported successfully')
    print(f'   Version: {codomyrmex.__version__}')
except ImportError as e:
    print(f'❌ Import failed: {e}')
    sys.exit(1)
"
    
    # Test CLI
    echo -e "${CYAN}Testing CLI...${NC}"
    if command -v codomyrmex &> /dev/null; then
        echo -e "${GREEN}✅ CLI command available${NC}"
        codomyrmex info
    else
        echo -e "${YELLOW}⚠️  CLI command not found in PATH${NC}"
        echo -e "${BLUE}💡 You can run: source .venv/bin/activate && codomyrmex info${NC}"
    fi
    
    # Test modules
    echo -e "${CYAN}Testing core modules...${NC}"
    python3 -c "
import sys
sys.path.insert(0, 'src')
from codomyrmex.data_visualization import create_line_plot
from codomyrmex.logging_monitoring import get_logger
print('✅ Core modules imported successfully')
"
    
    echo -e "${GREEN}✅ Installation verification complete!${NC}"
}

# Setup environment variables
setup_env() {
    echo -e "${BLUE}⚙️  Setting up environment...${NC}"
    
    if [ ! -f ".env" ]; then
        echo -e "${CYAN}Creating .env file template...${NC}"
        cat > .env << EOF
# Codomyrmex Environment Configuration
# Copy this file and add your API keys for AI features

# LLM API Keys (optional - only needed for AI features)
# OPENAI_API_KEY="sk-your-openai-key-here"
# ANTHROPIC_API_KEY="sk-ant-your-anthropic-key-here"
# GOOGLE_API_KEY="AIzaSy-your-google-key-here"

# Logging Configuration (optional)
CODOMYRMEX_LOG_LEVEL="INFO"
CODOMYRMEX_LOG_FILE="codomyrmex.log"

# Debug Mode (optional)
CODOMYRMEX_DEBUG="false"
EOF
        echo -e "${GREEN}✅ .env file created${NC}"
        echo -e "${YELLOW}💡 Edit .env file to add your API keys for AI features${NC}"
    else
        echo -e "${GREEN}✅ .env file already exists${NC}"
    fi
}

# Show next steps
show_next_steps() {
    echo -e "\n${WHITE}🎉 Installation Complete!${NC}\n"
    
    echo -e "${CYAN}Next Steps:${NC}"
    echo -e "1. ${GREEN}Activate the virtual environment:${NC}"
    echo -e "   ${YELLOW}source .venv/bin/activate${NC}"
    echo ""
    echo -e "2. ${GREEN}Try Codomyrmex:${NC}"
    echo -e "   ${YELLOW}codomyrmex info${NC}"
    echo -e "   ${YELLOW}codomyrmex check${NC}"
    echo ""
    echo -e "3. ${GREEN}Run examples:${NC}"
    echo -e "   ${YELLOW}python scripts/development/example_usage.py${NC}"
    echo ""
    echo -e "4. ${GREEN}Explore interactively:${NC}"
    echo -e "   ${YELLOW}./start_here.sh${NC}"
    echo ""
    echo -e "5. ${GREEN}For AI features, edit .env file with your API keys${NC}"
    echo ""
    echo -e "${PURPLE}Happy coding with Codomyrmex! 🐜✨${NC}"
}

# Main installation flow
main() {
    show_banner
    check_uv
    check_python
    install_codomyrmex
    setup_env
    verify_installation
    show_next_steps
}

# Run main function
main "$@"
