#!/bin/bash
# 🐜 Codomyrmex Example Prerequisites Checker
# 
# This script helps verify that your environment is ready to run Codomyrmex examples
# by checking for required dependencies, API keys, and system components.

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

echo -e "${CYAN}╔══════════════════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║        🔍 Codomyrmex Example Prerequisites Check 🔍     ║${NC}"
echo -e "${CYAN}╚══════════════════════════════════════════════════════════╝${NC}\n"

show_check() {
    echo -e "${BLUE}Checking: $1${NC}"
}

show_success() {
    echo -e "${GREEN}  ✅ $1${NC}"
}

show_warning() {
    echo -e "${YELLOW}  ⚠️  $1${NC}"
}

show_error() {
    echo -e "${RED}  ❌ $1${NC}"
}

# Check basic requirements
show_check "Basic System Requirements"

# Python check
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
    show_success "Python 3 available ($PYTHON_VERSION)"
    
    # Check Python version
    PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d'.' -f1)
    PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d'.' -f2)
    
    if [ "$PYTHON_MAJOR" -ge 3 ] && [ "$PYTHON_MINOR" -ge 9 ]; then
        show_success "Python version is compatible (3.9+)"
    else
        show_warning "Python 3.9+ recommended (you have $PYTHON_VERSION)"
    fi
else
    show_error "Python 3 not found - required for all examples"
fi

# Git check
if command -v git &> /dev/null; then
    GIT_VERSION=$(git --version | cut -d' ' -f3)
    show_success "Git available ($GIT_VERSION)"
else
    show_warning "Git not available - needed for git-related examples"
fi

# Node.js check (for documentation)
if command -v node &> /dev/null; then
    NODE_VERSION=$(node --version)
    show_success "Node.js available ($NODE_VERSION)"
else
    show_warning "Node.js not available - needed for documentation examples"
fi

# Docker check (for sandbox execution)
if command -v docker &> /dev/null; then
    if docker info &> /dev/null; then
        show_success "Docker available and running"
    else
        show_warning "Docker installed but not running - needed for code execution examples"
    fi
else
    show_warning "Docker not available - needed for code execution sandbox examples"
fi

# Check Codomyrmex installation
show_check "Codomyrmex Installation"

cd "$PROJECT_ROOT"

python3 -c "
import sys
sys.path.insert(0, 'src')

try:
    import codomyrmex
    print('✅ Codomyrmex package installed')
except ImportError:
    print('⚠️  Codomyrmex package not found, checking development installation...')
    
    # Check individual modules
    modules_checked = 0
    modules_available = 0
    
    core_modules = [
        'logging_monitoring',
        'environment_setup', 
        'data_visualization',
        'ai_code_editing',
        'static_analysis',
        'code_execution_sandbox',
        'git_operations'
    ]
    
    for module in core_modules:
        modules_checked += 1
        try:
            __import__(f'codomyrmex.{module}')
            modules_available += 1
        except ImportError:
            pass
    
    if modules_available >= 4:
        print(f'✅ Codomyrmex modules available ({modules_available}/{modules_checked})')
        print('ℹ️  Development installation detected')
    else:
        print(f'❌ Insufficient Codomyrmex modules ({modules_available}/{modules_checked})')
        print('   Please run: pip install -e . (from project root)')
"

# Check API keys
show_check "API Keys (for AI-enhanced examples)"

if [ -f .env ]; then
    show_success ".env file found"
    
    # Check for common API keys
    api_keys=("OPENAI_API_KEY" "ANTHROPIC_API_KEY" "GOOGLE_API_KEY")
    keys_found=0
    
    for key in "${api_keys[@]}"; do
        if grep -q "^$key=" .env 2>/dev/null; then
            show_success "$key configured"
            keys_found=$((keys_found + 1))
        fi
    done
    
    if [ $keys_found -eq 0 ]; then
        show_warning "No API keys found in .env file"
        echo -e "${YELLOW}    Add API keys to enable AI-enhanced examples:${NC}"
        echo -e "${YELLOW}    OPENAI_API_KEY=\"sk-...\"${NC}"
        echo -e "${YELLOW}    ANTHROPIC_API_KEY=\"sk-ant-...\"${NC}"
    else
        show_success "$keys_found API key(s) configured"
    fi
else
    show_warning ".env file not found"
    echo -e "${YELLOW}    Create .env file for API keys (optional):${NC}"
    echo -e "${YELLOW}    OPENAI_API_KEY=\"sk-...\"${NC}"
    echo -e "${YELLOW}    ANTHROPIC_API_KEY=\"sk-ant-...\"${NC}"
fi

# Check example files
show_check "Example Scripts Availability"

cd "$SCRIPT_DIR"

example_scripts=(
    "basic/data-visualization-demo.sh"
    "basic/static-analysis-demo.sh"
    "integration/ai-enhanced-analysis.sh"
    "integration/code-quality-pipeline.sh"
    "integration/ai-development-assistant.sh"
    "integration/environment-health-monitor.sh"
    "integration/development-workflow-orchestrator.sh"
    "setup-fabric-demo.sh"
)

scripts_found=0
for script in "${example_scripts[@]}"; do
    if [ -f "$script" ]; then
        scripts_found=$((scripts_found + 1))
        if [ -x "$script" ]; then
            show_success "$script (executable)"
        else
            show_warning "$script (not executable - run: chmod +x examples/$script)"
        fi
    else
        show_error "$script not found"
    fi
done

show_success "$scripts_found/${#example_scripts[@]} example scripts available"

# Final recommendations
echo ""
echo -e "${CYAN}╔══════════════════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║                    📋 RECOMMENDATIONS                    ║${NC}"
echo -e "${CYAN}╚══════════════════════════════════════════════════════════╝${NC}"

echo -e "${WHITE}For the best example experience:${NC}"

echo -e "${GREEN}✅ You can run:${NC}"
echo "  • Basic examples (data visualization, static analysis)"
echo "  • Environment health monitor"
echo "  • Core integration examples"

if command -v docker &> /dev/null && docker info &> /dev/null; then
    echo -e "${GREEN}✅ Docker available:${NC}"
    echo "  • Code execution sandbox examples"
fi

if [ -f .env ] && grep -q "API_KEY=" .env 2>/dev/null; then
    echo -e "${GREEN}✅ API keys configured:${NC}"
    echo "  • AI-enhanced development examples"
    echo "  • AI development assistant"
    echo "  • Complete workflow orchestrator"
fi

echo ""
echo -e "${BLUE}🚀 Ready to start? Try these examples:${NC}"
echo "  1. ./basic/data-visualization-demo.sh"
echo "  2. ./integration/environment-health-monitor.sh"
echo "  3. ./integration/code-quality-pipeline.sh"

if [ -f .env ] && grep -q "API_KEY=" .env 2>/dev/null; then
    echo "  4. ./integration/ai-development-assistant.sh"
    echo "  5. ./integration/development-workflow-orchestrator.sh"
fi

echo ""
echo -e "${CYAN}📖 For more information: cat examples/README.md${NC}"
