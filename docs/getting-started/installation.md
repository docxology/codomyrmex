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

## 📋 Prerequisites

Before installing Codomyrmex, ensure you have:

### **Required**
- **Python 3.10+** (latest versions recommended for best package compatibility)
  ```bash
  python3 --version  # Should be 3.10 or higher
  ```
- **uv** (package manager used across Codomyrmex)
  ```bash
  uv --version || curl -LsSf https://astral.sh/uv/install.sh | sh
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
uv venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# 3. Install
uv pip install -e .

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
uv pip install -e ".[dev]"

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

## ✅ Verification & Testing

### **Step 1: Basic System Check**
```bash
# Verify Codomyrmex is working correctly
codomyrmex check

# Expected output shows all systems operational
# ✅ Python 3.13.7
# ✅ Logging & Monitoring module
# ✅ Environment Setup module
# ✅ Data visualization
# ✅ Testing framework
```

### **Step 2: Interactive Exploration**
```bash
# Launch the interactive shell for hands-on exploration
./start_here.sh
# Choose option 7: Interactive Shell

# Or launch directly
python -c "
from codomyrmex.terminal_interface import InteractiveShell
InteractiveShell().run()
"
```

**Try these commands in the interactive shell:**
```bash
🐜 codomyrmex> explore                    # Overview of all modules
🐜 codomyrmex> forage visualization       # Find visualization capabilities
🐜 codomyrmex> demo data_visualization    # Run live demo
🐜 codomyrmex> dive ai_code_editing       # Deep dive into AI module
🐜 codomyrmex> status                     # System health check
🐜 codomyrmex> export                     # Generate system inventory
```

### **Step 3: Test Core Functionality**

Test the main features to ensure everything works:

```python
# Test data visualization (should create PNG files)
from codomyrmex.data_visualization import create_line_plot
import numpy as np

x = np.linspace(0, 10, 100)
y = np.sin(x)
result = create_line_plot(x, y, title="Test Plot", output_path="test_plot.png")
print(f"✅ Visualization test: {result is not None}")

# Test AI code generation (requires API key)
from codomyrmex.ai_code_editing import generate_code_snippet

try:
    ai_result = generate_code_snippet("Create a hello world function", "python")
    print(f"✅ AI test: {ai_result['status'] == 'success'}")
except Exception as e:
    print(f"⚠️ AI test skipped (no API key): {e}")

# Test code execution sandbox
from codomyrmex.code_execution_sandbox import execute_code

sandbox_result = execute_code("python", "print('Hello from sandbox!')")
print(f"✅ Sandbox test: {sandbox_result['success']}")
```

### **Step 4: Run Comprehensive Tests**
```bash
# Run all tests with coverage reporting
pytest testing/ --cov=src/codomyrmex --cov-report=html

# Run specific module tests
pytest testing/unit/test_data_visualization.py -v

# Run integration tests
pytest testing/integration/ -v

# Check test coverage
open testing/htmlcov/index.html  # View coverage report
```

### **Step 5: Code Quality Check**
```bash
# Run linting on the main codebase
python -m ruff check src/codomyrmex/

# Format code (if needed)
python -m black src/codomyrmex/

# Type checking (if configured)
python -m mypy src/codomyrmex/
```

## 🐛 Troubleshooting Guide

This section provides solutions for the most common installation and setup issues. If you encounter problems, work through these solutions systematically.

### **🔍 Quick Diagnostic Commands**

First, run these commands to identify the issue:

```bash
# 1. Check your environment
python3 --version
which python3
pwd

# 2. Verify virtual environment
source .venv/bin/activate  # or .venv\Scripts\activate on Windows
which python

# 3. Check Codomyrmex installation
python -c "import codomyrmex; print('✅ Import successful')"

# 4. Run system check
codomyrmex check

# 5. Check dependencies
pip list | grep -E "(matplotlib|numpy|pytest|docker)"
```

### **🚨 Common Issues & Solutions**

#### **❌ "Module not found" Errors**
```bash
# Problem: ImportError when trying to use Codomyrmex
# Solution: Ensure virtual environment is activated and installation is correct

# 1. Check you're in the right directory
cd /path/to/codomyrmex

# 2. Activate virtual environment
source .venv/bin/activate

# 3. Verify Python path
which python  # Should show .venv/bin/python

# 4. Reinstall if needed
pip install -e .

# 5. Test import
python -c "import codomyrmex; print('Success!')"
```

#### **❌ Python Version Too Old**
```bash
# Problem: Python 3.9 or older detected
# Solution: Upgrade to Python 3.10+

# macOS with Homebrew
brew install python@3.11
brew link python@3.11

# Ubuntu/Debian
sudo apt-get update
sudo apt-get install python3.11 python3.11-venv

# Windows: Download from python.org
# Install Python 3.11+ and add to PATH
```

#### **❌ Virtual Environment Problems**
```bash
# Problem: Virtual environment not working properly
# Solution: Recreate the environment

# Remove old environment
rm -rf .venv

# Create fresh environment
python3 -m venv .venv

# Activate and install
source .venv/bin/activate
pip install --upgrade pip
pip install -e .

# Verify
codomyrmex check
```

#### **❌ Permission Errors**
```bash
# Problem: Permission denied when installing packages
# Solution: Don't use sudo in virtual environments

# Correct approach:
source .venv/bin/activate
pip install package_name

# If you accidentally used sudo:
sudo rm -rf .venv
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
```

#### **❌ "No module named 'codomyrmex'" After Installation**
```bash
# Problem: Module not found despite installation
# Solution: Check installation and Python path

# 1. Check installation location
pip show codomyrmex

# 2. Verify PYTHONPATH includes the right directories
echo $PYTHONPATH

# 3. Try reinstalling
pip uninstall codomyrmex
pip install -e .

# 4. Test in fresh shell
source .venv/bin/activate
python -c "import codomyrmex; print('Fixed!')"
```

### **🔧 Module-Specific Issues**

#### **🤖 AI Features Not Working**
```bash
# Problem: AI code generation fails
# Solution: Check API keys and connectivity

# 1. Check API keys are set
echo "OpenAI: ${OPENAI_API_KEY:+SET}"
echo "Anthropic: ${ANTHROPIC_API_KEY:+SET}"

# 2. Create .env file if missing
cat > .env << EOF
OPENAI_API_KEY="your-openai-key-here"
ANTHROPIC_API_KEY="your-anthropic-key-here"
GOOGLE_API_KEY="your-google-key-here"
EOF

# 3. Test API connectivity
python -c "
import os
from codomyrmex.ai_code_editing import validate_api_keys
print('API Keys:', validate_api_keys())
"
```

#### **🐳 Docker/Code Execution Issues**
```bash
# Problem: Code execution sandbox fails
# Solution: Check Docker installation and permissions

# 1. Verify Docker is installed and running
docker --version
docker run hello-world

# 2. On Linux, add user to docker group
sudo usermod -aG docker $USER
# Logout and login again

# 3. Test sandbox functionality
python -c "
from codomyrmex.code_execution_sandbox import execute_code
result = execute_code('python', 'print(\"Hello\")')
print('Sandbox test:', result['success'])
"
```

#### **📊 Visualization Issues**
```bash
# Problem: Can't create plots or display images
# Solution: Check matplotlib backend and dependencies

# 1. Check matplotlib installation
python -c "import matplotlib; print('Matplotlib version:', matplotlib.__version__)"

# 2. Set non-interactive backend for saving files
export MPLBACKEND=Agg

# 3. Test plot creation
python -c "
from codomyrmex.data_visualization import create_line_plot
import numpy as np
x = np.linspace(0, 10, 50)
y = np.sin(x)
result = create_line_plot(x, y, output_path='test.png')
print('Plot test:', result is not None)
"
```

#### **📚 Documentation Build Issues**
```bash
# Problem: Documentation website build fails
# Solution: Check Node.js and dependencies

# 1. Verify Node.js version
node --version  # Should be 18.0+

# 2. Install dependencies
cd src/codomyrmex/documentation
npm install

# 3. Test build
npm run build

# 4. If issues persist, clear cache
rm -rf node_modules package-lock.json
npm install
```

### **🔍 Advanced Debugging**

#### **Check System Dependencies**
```bash
# Verify all required system packages
python -c "
import sys
required_modules = ['matplotlib', 'numpy', 'pytest', 'docker']
for module in required_modules:
    try:
        __import__(module)
        print(f'✅ {module}')
    except ImportError as e:
        print(f'❌ {module}: {e}')
"

# Check optional dependencies
optional_modules = ['openai', 'anthropic', 'google.generativeai']
for module in optional_modules:
    try:
        __import__(module)
        print(f'✅ {module} (optional)')
    except ImportError:
        print(f'⚠️  {module} (optional - not installed)')
"
```

#### **Environment Variable Issues**
```bash
# Check if .env file is being loaded
python -c "
import os
from pathlib import Path

# Check if .env exists and is readable
env_file = Path('.env')
if env_file.exists():
    print('✅ .env file exists')
    print('📄 Contents preview:')
    with open(env_file) as f:
        lines = f.readlines()[:3]  # Show first 3 lines
        for line in lines:
            if '=' in line and not line.startswith('#'):
                key = line.split('=')[0]
                print(f'  {key}: {os.getenv(key, \"NOT SET\")}')
else:
    print('⚠️  .env file not found')
"
```

### **🚀 Getting Additional Help**

If these solutions don't resolve your issue:

1. **Check the logs**: Look for detailed error messages
   ```bash
   codomyrmex check --verbose
   ```

2. **Review the documentation**: Check module-specific guides
   ```bash
   # See available documentation
   find docs/ -name "*.md" | head -10
   ```

3. **Search existing issues**: [GitHub Issues](https://github.com/codomyrmex/codomyrmex/issues)

4. **Ask the community**: [GitHub Discussions](https://github.com/codomyrmex/codomyrmex/discussions)

5. **Create a bug report**: Include your system info and exact error messages

## 🚀 Next Steps

Once installed successfully:

1. **Try the Quick Start**: Follow the [Quick Start Guide](quickstart.md)
2. **Explore modules**: Use the [Interactive Shell](../modules/overview.md#interactive-module-exploration)
3. **Read tutorials**: Check out [Tutorials](tutorials/) for specific use cases
4. **Join development**: See [Contributing Guide](../project/contributing.md)

---

**Installation complete!** You're ready to start using Codomyrmex's powerful modular toolkit for code analysis, generation, and workflow automation.

---

**📝 Documentation Status**: ✅ **Verified & Signed** | *Last reviewed: January 2025* | *Maintained by: Codomyrmex Documentation Team* | *Version: v0.1.0*
