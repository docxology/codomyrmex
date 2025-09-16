# Codomyrmex Installation Guide

This guide will get you up and running with Codomyrmex quickly and reliably.

## 🎯 Quick Start (Recommended)

### **Option 1: UV-Optimized Setup (Fastest & Most Reliable)**
```bash
# Clone and setup everything automatically with uv
git clone https://github.com/codomyrmex/codomyrmex.git
cd codomyrmex
./install_with_uv.sh
```

### **Option 2: Manual UV Setup**
```bash
# 1. Install uv (if not already installed)
curl -LsSf https://astral.sh/uv/install.sh | sh

# 2. Clone the repository
git clone https://github.com/codomyrmex/codomyrmex.git
cd codomyrmex

# 3. Create virtual environment and install
uv venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
uv pip install -e .

# 4. Verify installation
codomyrmex check
```

### **Option 3: Traditional pip Setup (Alternative)**
```bash
# 1. Clone the repository
git clone https://github.com/codomyrmex/codomyrmex.git
cd codomyrmex

# 2. Create virtual environment
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# 3. Install Codomyrmex
pip install -e .

# 4. Verify installation
codomyrmex check
```

## 📋 Prerequisites

Before installing Codomyrmex, ensure you have:

### **Required**
- **Python 3.10+** (latest versions recommended for best package compatibility)
  ```bash
  python3 --version  # Should be 3.10 or higher
  ```
- **pip** or **uv** (package manager)
  ```bash
  pip --version
  # OR install uv for faster, more reliable package management
  curl -LsSf https://astral.sh/uv/install.sh | sh
  ```
- **git** (version control)
  ```bash
  git --version
  ```

### **Optional (for specific modules)**
- **Node.js 18+** (for documentation generation)
  ```bash
  node --version  # Should be 18.0 or higher
  npm --version
  ```
- **Docker** (for code execution sandbox)
  ```bash
  docker --version
  docker run hello-world  # Test Docker installation
  ```
- **Graphviz** (for dependency visualization)
  ```bash
  # macOS
  brew install graphviz
  # Ubuntu/Debian
  sudo apt-get install graphviz
  # Windows
  # Download from https://graphviz.org/download/
  ```

## 🛠️ Detailed Installation Options

### **Using uv (Recommended)**

[uv](https://github.com/astral-sh/uv) is a fast Python package manager that's more reliable than pip:

```bash
# 1. Install uv (if not already installed)
curl -LsSf https://astral.sh/uv/install.sh | sh

# 2. Clone repository
git clone https://github.com/codomyrmex/codomyrmex.git
cd codomyrmex

# 3. Create virtual environment and install
uv venv .venv
source .venv/bin/activate
uv pip install -e .

# 4. Verify installation
codomyrmex check
```

### **Using pip (Traditional)**

```bash
# 1. Clone repository
git clone https://github.com/codomyrmex/codomyrmex.git
cd codomyrmex

# 2. Create virtual environment
python3 -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# 3. Upgrade pip and install
pip install --upgrade pip
pip install -e .

# 4. Verify installation
codomyrmex check
```

### **Development Installation**

For contributors or developers who want to modify Codomyrmex:

```bash
# 1. Clone your fork
git clone https://github.com/YOUR_USERNAME/codomyrmex.git
cd codomyrmex

# 2. Setup development environment
bash src/codomyrmex/environment_setup/scripts/setup_dev_env.sh

# 3. Install development dependencies
pip install -e ".[dev]"  # If using pip
# OR
uv pip install -e ".[dev]"  # If using uv

# 4. Setup pre-commit hooks (optional but recommended)
pre-commit install

# 5. Run tests to verify everything works
pytest testing/ -v
```

## ⚙️ Configuration

### **Environment Variables (Optional)**

For AI-powered features, create a `.env` file in the project root:

```bash
# Create .env file
cat > .env << EOF
# LLM API Keys (optional - only needed for AI features)
OPENAI_API_KEY="sk-..."
ANTHROPIC_API_KEY="sk-ant-..."
GOOGLE_API_KEY="AIzaSy..."

# Logging Configuration (optional)
CODOMYRMEX_LOG_LEVEL="INFO"
CODOMYRMEX_LOG_FILE="codomyrmex.log"

# Other Configuration (optional)
CODOMYRMEX_DEBUG="false"
EOF
```

**Security Note**: Never commit the `.env` file to version control. It's already included in `.gitignore`.

### **Module-Specific Setup**

Some modules may require additional setup:

#### **Documentation Module**
```bash
# Install Node.js dependencies for documentation generation
cd src/codomyrmex/documentation
npm install
cd ../../..
```

#### **Docker for Code Execution**
```bash
# Test Docker setup
docker run --rm python:3.11-slim python -c "print('Docker works!')"
```

## ✅ Verification

### **Basic Verification**
```bash
# Check overall system health
codomyrmex check

# Get project information
codomyrmex info

# Run example workflows
python example_usage.py
```

### **Comprehensive Testing**
```bash
# Run the full test suite
pytest testing/ -v

# Run specific module tests
pytest testing/unit/test_data_visualization.py -v

# Check code quality
python -m pylint src/codomyrmex/ --disable=C0114,C0116
python -m flake8 src/codomyrmex/
```

### **Interactive Verification**
```bash
# Launch the interactive shell for exploration
./start_here.sh
# Choose option 7: Interactive Shell

# Or launch directly
python -c "
from codomyrmex.terminal_interface import InteractiveShell
InteractiveShell().run()
"
```

## 🐛 Troubleshooting

### **Common Issues**

#### **Python Version Issues**
```bash
# Check Python version
python3 --version

# If too old, install newer Python
# macOS with Homebrew
brew install python@3.11

# Ubuntu/Debian
sudo apt-get update
sudo apt-get install python3.11

# Windows: Download from python.org
```

#### **Virtual Environment Issues**
```bash
# Remove and recreate virtual environment
rm -rf .venv
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
```

#### **Import Errors**
```bash
# Ensure you're in the project root and venv is activated
pwd  # Should show path ending in /codomyrmex
which python  # Should show path in .venv/bin/python

# Reinstall in editable mode
pip install -e .
```

#### **Permission Errors**
```bash
# Don't use sudo with pip in virtual environments
# If you get permission errors, ensure virtual environment is activated
source .venv/bin/activate
```

### **Module-Specific Issues**

#### **AI Features Not Working**
- Ensure API keys are set in `.env` file
- Check API key validity and quotas
- Verify network connectivity

#### **Docker Issues**
- Ensure Docker daemon is running
- Check Docker permissions (add user to docker group on Linux)
- Test with simple container: `docker run hello-world`

#### **Documentation Build Failures**
- Ensure Node.js 18+ is installed
- Clear node_modules: `rm -rf src/codomyrmex/documentation/node_modules`
- Reinstall: `cd src/codomyrmex/documentation && npm install`

### **Getting Help**

If you encounter issues not covered here:

1. **Check existing issues**: [GitHub Issues](https://github.com/codomyrmex/codomyrmex/issues)
2. **Run diagnostics**: `codomyrmex check` for detailed system information
3. **Consult documentation**: [Full Documentation](../README.md)
4. **Ask for help**: Create a new issue with:
   - Your operating system and version
   - Python version (`python3 --version`)
   - Complete error messages
   - Steps to reproduce the issue

## 🚀 Next Steps

Once installed successfully:

1. **Try the Quick Start**: Follow the [Quick Start Guide](quickstart.md)
2. **Explore modules**: Use the [Interactive Shell](../modules/overview.md#interactive-module-exploration)
3. **Read tutorials**: Check out [Tutorials](tutorials/) for specific use cases
4. **Join development**: See [Contributing Guide](../project/contributing.md)

---

**Installation complete!** You're ready to start using Codomyrmex's powerful modular toolkit for code analysis, generation, and workflow automation.
