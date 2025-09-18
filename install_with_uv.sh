#!/bin/bash
# 🚀 Codomyrmex Installation Script - Root Level Wrapper
# This script calls the main installation script in the environment_setup module

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Check if we're in the right directory
if [[ ! -f "pyproject.toml" ]] || [[ ! -d "src/codomyrmex" ]]; then
    echo -e "${RED}❌ Error: Not in the Codomyrmex project root directory!${NC}"
    echo -e "${BLUE}Please run this script from the main codomyrmex directory.${NC}"
    exit 1
fi

# Call the main installation script
INSTALL_SCRIPT="src/codomyrmex/environment_setup/scripts/install_with_uv.sh"

if [[ -f "$INSTALL_SCRIPT" ]]; then
    echo -e "${GREEN}🚀 Starting Codomyrmex installation...${NC}"
    bash "$INSTALL_SCRIPT"
else
    echo -e "${RED}❌ Installation script not found at: $INSTALL_SCRIPT${NC}"
    echo -e "${BLUE}Please ensure the repository is complete and try again.${NC}"
    exit 1
fi
