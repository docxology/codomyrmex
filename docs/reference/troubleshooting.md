# Troubleshooting Guide

This guide helps you resolve common issues when using or developing Codomyrmex.

## 🔧 Installation Issues

### **Python Version Problems**

#### Issue: "Python version too old" error
```bash
ERROR: Python 3.9 is required, but you have Python 3.8
```

**Solution:**
```bash
# Check current Python version
python3 --version

# Install newer Python (macOS with Homebrew)
brew install python@3.11

# Ubuntu/Debian
sudo apt-get update
sudo apt-get install python3.11

# Update your PATH or use specific version
python3.11 -m venv .venv
```

#### Issue: Multiple Python versions causing confusion
```bash
# Check all Python versions
which -a python3
ls -la /usr/bin/python*

# Use specific version for virtual environment
/usr/bin/python3.11 -m venv .venv
```

### **Virtual Environment Issues**

#### Issue: Virtual environment not activating
```bash
# Remove corrupted virtual environment
rm -rf .venv

# Create new environment
python3 -m venv .venv

# Activate (Linux/macOS)
source .venv/bin/activate

# Activate (Windows)
.venv\Scripts\activate

# Verify activation
which python  # Should show .venv/bin/python
```

#### Issue: "Permission denied" when creating virtual environment
```bash
# Don't use sudo with virtual environments
# Instead, fix Python installation permissions or use user directory

# Use uv for package management
uv sync

# Or fix permissions (macOS/Linux)
sudo chown -R $USER:$USER /usr/local/lib/python3.*/site-packages
```

### **Dependency Installation Problems**

#### Issue: Package installation fails with "ERROR: Could not build wheels"
```bash
# Update uv and build tools
uv self update

# Install development dependencies
sudo apt-get install python3-dev build-essential  # Ubuntu/Debian
xcode-select --install  # macOS

# For specific packages
uv pip install --no-cache package_name
```

#### Issue: Conflicting package versions
```bash
# Clear pip cache
pip cache purge

# Use fresh virtual environment
rm -rf .venv
uv venv .venv
source .venv/bin/activate
uv sync
```

## 🐛 Runtime Issues

### **Import Errors**

#### Issue: "ModuleNotFoundError: No module named 'codomyrmex'"
```bash
# Ensure you're in project root
pwd  # Should end with /codomyrmex

# Install in editable mode
uv sync

# Check installation
python -c "import codomyrmex; print(codomyrmex.__file__)"
```

#### Issue: "ModuleNotFoundError" for specific Codomyrmex modules
```bash
# Check module is properly installed
python -c "
import sys
sys.path.insert(0, 'src')
from codomyrmex.system_discovery import SystemDiscovery
discovery = SystemDiscovery()
modules = discovery.discover_modules()
for name, info in modules.items():
    print(f'{name}: {\"✅\" if info.is_importable else \"❌\"}')"

# Reinstall if needed
uv sync
```

### **Configuration Issues** {#environment-variable-issues}

#### Issue: API keys not being recognized
```bash
# Check .env file exists and is in project root
ls -la .env

# Verify environment variable loading
python -c "
import os
from dotenv import load_dotenv
load_dotenv()
print('OPENAI_API_KEY:', 'SET' if os.getenv('OPENAI_API_KEY') else 'NOT SET')
"

# Create .env file if missing
cat > .env << EOF
OPENAI_API_KEY="your-api-key-here"
ANTHROPIC_API_KEY="your-anthropic-key-here"
EOF
```

#### Issue: Docker not working for code execution
```bash
# Check Docker is running
docker --version
docker run hello-world

# Fix Docker permissions (Linux)
sudo usermod -aG docker $USER
newgrp docker  # Or logout/login

# Test Docker with Python
docker run --rm python:3.11-slim python -c "print('Docker works!')"
```

### **Performance Issues** {#performance-issues}

#### Issue: Slow module discovery or analysis
```bash
# Run with debug logging to identify bottlenecks
export CODOMYRMEX_LOG_LEVEL="DEBUG"
python -c "
import sys; sys.path.insert(0, 'src')
from codomyrmex.system_discovery import SystemDiscovery
SystemDiscovery().run_full_discovery()
"

# Check for large files in analysis
find . -name "*.py" -size +1M  # Find large Python files
```

#### Issue: High memory usage
```bash
# Monitor memory usage
python -c "
import psutil
import sys; sys.path.insert(0, 'src')
from codomyrmex.system_discovery import SystemDiscovery

process = psutil.Process()
print(f'Memory before: {process.memory_info().rss / 1024 / 1024:.1f} MB')

discovery = SystemDiscovery()
discovery.run_full_discovery()

print(f'Memory after: {process.memory_info().rss / 1024 / 1024:.1f} MB')
"
```

## 🧪 Testing Issues

### **Test Failures**

#### Issue: Tests failing with import errors
```bash
# Run tests from project root
cd /path/to/codomyrmex
pytest src/codomyrmex/tests/ -v

# Check test environment
python -m pytest --version
python -c "import sys; print(sys.path)"

# Reinstall in editable mode
uv sync
```

#### Issue: Tests pass locally but fail in CI
```bash
# Check Python version consistency
python --version
pytest --version

# Check for missing test dependencies
uv sync --dev

# Run tests with same options as CI
pytest src/codomyrmex/tests/ -v --tb=short --cov=src/codomyrmex
```

#### Issue: Coverage reports not generating
```bash
# Install coverage dependencies
uv sync

# Generate HTML coverage report
pytest --cov=src/codomyrmex --cov-report=html --cov-report=term

# View coverage report
open src/codomyrmex/tests/htmlcov/index.html  # macOS
xdg-open src/codomyrmex/tests/htmlcov/index.html  # Linux
```

### **Linting and Code Quality Issues**

#### Issue: Pre-commit hooks failing
```bash
# Update pre-commit hooks
pre-commit autoupdate

# Install hooks
pre-commit install

# Run hooks manually
pre-commit run --all-files

# Skip hooks temporarily (for testing)
git commit --no-verify -m "temporary commit"
```

#### Issue: Code formatting inconsistencies
```bash
# Run Black formatter
black src/ src/codomyrmex/tests/

# Check what would be formatted
black --check --diff src/ src/codomyrmex/tests/

# Configure Black in pyproject.toml if needed
```

## 📊 Data Visualization Issues

### **Matplotlib Issues**

#### Issue: Plots not displaying or saving
```bash
# Check matplotlib backend
python -c "import matplotlib; print(matplotlib.get_backend())"

# Set non-interactive backend for server environments
export MPLBACKEND=Agg
python your_script.py

# Or in Python code:
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
```

#### Issue: Font or rendering problems
```bash
# Clear matplotlib cache
rm -rf ~/.matplotlib/

# Install system fonts (Ubuntu/Debian)
sudo apt-get install fonts-dejavu-core fonts-liberation

# List available fonts
python -c "
from matplotlib import font_manager
fonts = font_manager.findSystemFonts()
print(f'Found {len(fonts)} fonts')
"
```

## 🤖 AI Integration Issues

### **OpenAI API Issues**

#### Issue: "Authentication failed" errors
```bash
# Check API key format
python -c "
import os
key = os.getenv('OPENAI_API_KEY', '')
print(f'Key length: {len(key)}')
print(f'Starts with sk-: {key.startswith(\"sk-\")}')
"

# Test API key directly
python -c "
import openai
import os
openai.api_key = os.getenv('OPENAI_API_KEY')
try:
    response = openai.Model.list()
    print('API key works!')
except Exception as e:
    print(f'API error: {e}')
"
```

#### Issue: Rate limiting or quota exceeded
```bash
# Check rate limits in your OpenAI dashboard
# Implement exponential backoff in your code

# Or use different model with higher limits
python -c "
from codomyrmex.agents.ai_code_editing import generate_code_snippet
result = generate_code_snippet(
    'print hello world',
    'python',
    model_name='gpt-3.5-turbo'  # Use cheaper model
)
"
```

### **Anthropic Claude Issues**

#### Issue: Claude API authentication problems
```bash
# Check Anthropic API key
python -c "
import os
key = os.getenv('ANTHROPIC_API_KEY', '')
print(f'Key length: {len(key)}')
print(f'Starts with sk-ant-: {key.startswith(\"sk-ant-\")}')
"
```

## 🔧 Development Issues

### **Git and Version Control**

#### Issue: Large files causing Git problems
```bash
# Check for large files
find . -size +100M -not -path "./.git/*"

# Use Git LFS for large files
git lfs install
git lfs track "*.pkl" "*.model" "*.bin"
git add .gitattributes
```

#### Issue: Merge conflicts in generated files
```bash
# Add to .gitignore
echo "codomyrmex_inventory.json" >> .gitignore
echo "*.log" >> .gitignore
echo "__pycache__/" >> .gitignore

# Clean up tracked generated files
git rm --cached codomyrmex_inventory.json
git commit -m "Remove generated files from tracking"
```

### **IDE and Editor Issues**

#### Issue: VS Code not recognizing Python environment
```json
// Add to .vscode/settings.json
{
    "python.defaultInterpreterPath": "./.venv/bin/python",
    "python.terminal.activateEnvironment": true,
    "python.analysis.extraPaths": ["src"]
}
```

#### Issue: Type checking errors with mypy
```bash
# Install type stubs
uv pip install types-requests types-PyYAML

# Configure mypy in pyproject.toml
[tool.mypy]
ignore_missing_imports = true
python_version = "3.10"
```

## 🔍 Debugging Techniques

### **Debug Mode**
```bash
# Enable debug logging
export CODOMYRMEX_LOG_LEVEL="DEBUG"
export CODOMYRMEX_DEBUG="true"

# Run with Python debugger
python -m pdb your_script.py

# Use breakpoint() in Python 3.7+
def problematic_function():
    breakpoint()  # Interactive debugger
    return result
```

### **System Information**
```bash
# Get comprehensive system information
python -c "
import sys, platform, os
print(f'OS: {platform.system()} {platform.release()}')
print(f'Python: {sys.version}')
print(f'Python path: {sys.executable}')
print(f'Working directory: {os.getcwd()}')
print(f'Environment variables:')
for key in sorted(os.environ.keys()):
    if 'CODOMYRMEX' in key or key in ['PATH', 'PYTHONPATH']:
        print(f'  {key}={os.environ[key][:100]}...')
"
```

### **Module Diagnostics**
```bash
# Run comprehensive system check
python -c "
import sys; sys.path.insert(0, 'src')
from codomyrmex.system_discovery import SystemDiscovery
discovery = SystemDiscovery()
discovery.show_status_dashboard()
"

# Check specific module
python -c "
import sys; sys.path.insert(0, 'src')
try:
    from codomyrmex.your_module import your_function
    print('✅ Module imports successfully')
    result = your_function('test')
    print('✅ Module functions work')
except Exception as e:
    print(f'❌ Module error: {e}')
    import traceback
    traceback.print_exc()
"
```

## 🔗 Integration Issues {#integration-issues}

### **External System Integration Problems**

#### Issue: API authentication failures with external systems
```bash
# Check API credentials
python -c "
import os
print('API Keys configured:')
for key in ['EXTERNAL_API_KEY', 'DATABASE_URL', 'CLOUD_CREDENTIALS']:
    value = os.getenv(key, 'Not set')
    print(f'  {key}: {\"Set\" if value != \"Not set\" else \"Not set\"}')
"

# Test API connectivity
python -c "
import requests
try:
    response = requests.get('https://api.example.com/health', timeout=5)
    print(f'API Status: {response.status_code}')
except Exception as e:
    print(f'API Error: {e}')
"
```

#### Issue: Database connection problems
```bash
# Test database connection
python -c "
from sqlalchemy import create_engine
import os
db_url = os.getenv('DATABASE_URL', 'postgresql://user:pass@localhost/db')
try:
    engine = create_engine(db_url)
    with engine.connect() as conn:
        print('✅ Database connection successful')
except Exception as e:
    print(f'❌ Database error: {e}')
"
```

#### Issue: Webhook delivery failures
```bash
# Check webhook configuration
python -c "
import os
webhook_url = os.getenv('WEBHOOK_URL', '')
print(f'Webhook URL configured: {webhook_url != \"\"}')
print(f'Webhook URL: {webhook_url[:50]}...' if webhook_url else 'Not set')
"

# Test webhook delivery
python -c "
import requests
import json
webhook_url = os.getenv('WEBHOOK_URL')
if webhook_url:
    try:
        response = requests.post(webhook_url, json={'test': True}, timeout=10)
        print(f'Webhook Status: {response.status_code}')
    except Exception as e:
        print(f'Webhook Error: {e}')
else:
    print('Webhook URL not configured')
"
```

## 🚀 Production Issues {#production-issues}

### **Deployment Problems**

#### Issue: Application fails to start in production
```bash
# Check environment variables
python -c "
import os
required_vars = ['DATABASE_URL', 'API_KEY', 'ENVIRONMENT']
for var in required_vars:
    value = os.getenv(var, 'Not set')
    print(f'{var}: {\"✅ Set\" if value != \"Not set\" else \"❌ Not set\"}')
"

# Check application health
python -c "
import sys; sys.path.insert(0, 'src')
from codomyrmex.environment_setup import validate_environment
status = validate_environment()
print(f'Environment Status: {status}')
"
```

#### Issue: High resource usage in production
```bash
# Monitor resource usage
python -c "
import psutil
import os
process = psutil.Process(os.getpid())
print(f'CPU: {process.cpu_percent()}%')
print(f'Memory: {process.memory_info().rss / 1024 / 1024:.2f} MB')
print(f'Open Files: {len(process.open_files())}')
"
```

#### Issue: Production database migrations failing
```bash
# Check database connection
python -c "
from sqlalchemy import create_engine, text
import os
db_url = os.getenv('DATABASE_URL')
if db_url:
    engine = create_engine(db_url)
    with engine.connect() as conn:
        result = conn.execute(text('SELECT version()'))
        print(f'Database Version: {result.fetchone()[0]}')
"
```

## 🔒 Security Issues {#security-issues}

### **Security Configuration Problems**

#### Issue: API keys exposed in logs
```bash
# Check logging configuration
python -c "
import logging
logger = logging.getLogger()
print(f'Log Level: {logging.getLevelName(logger.level)}')
print('Check log formatters for sensitive data exposure')
"

# Review environment variable handling
python -c "
import os
sensitive_keys = [key for key in os.environ.keys() if any(x in key.upper() for x in ['KEY', 'SECRET', 'PASSWORD', 'TOKEN'])]
print(f'Sensitive environment variables found: {len(sensitive_keys)}')
print('Review these variables for proper handling:')
for key in sensitive_keys[:5]:
    print(f'  {key}')
"
```

#### Issue: SSL/TLS certificate validation failures
```bash
# Test SSL connectivity
python -c "
import ssl
import socket
try:
    context = ssl.create_default_context()
    with socket.create_connection(('github.com', 443)) as sock:
        with context.wrap_socket(sock, server_hostname='github.com') as ssock:
            print(f'SSL Connection: ✅ Success')
            print(f'Certificate: {ssock.getpeercert()[\"subject\"]}')
except Exception as e:
    print(f'SSL Error: {e}')
"
```

#### Issue: Unauthorized access attempts
```bash
# Check authentication configuration
python -c "
import os
auth_method = os.getenv('AUTH_METHOD', 'none')
print(f'Auth Method: {auth_method}')
if auth_method == 'none':
    print('⚠️  Warning: No authentication configured')
"
```

## 📞 Getting Additional Help

### **Community Support**
- **GitHub Issues**: [Report bugs and problems](https://github.com/codomyrmex/codomyrmex/issues)
- **GitHub Discussions**: [Get help from community](https://github.com/codomyrmex/codomyrmex/discussions)
- **Documentation**: [Full documentation](../README.md)

### **When Reporting Issues**
Include the following information:

1. **System Information**:
   ```bash
   python --version
   uname -a  # Linux/macOS
   systeminfo  # Windows
   ```

2. **Codomyrmex Information**:
   ```bash
   codomyrmex check
   pip list | grep -i codomyrmex
   ```

3. **Error Details**:
   - Complete error messages
   - Steps to reproduce
   - Expected vs actual behavior
   - Relevant configuration files

4. **Environment**:
   - Virtual environment status
   - API keys configured (don't include actual keys!)
   - Docker version if using code execution
   - Node.js version if using documentation

### **Emergency Debugging**
If nothing works, try a clean reinstall:

```bash
# Complete clean reinstall
rm -rf .venv
rm -rf src/codomyrmex.egg-info
rm -rf __pycache__
find . -name "*.pyc" -delete
find . -name "__pycache__" -type d -exec rm -rf {} +

# Fresh installation
uv venv .venv
source .venv/bin/activate
uv sync

# Verify installation
codomyrmex check
pytest src/codomyrmex/tests/unit/ -x
```

---

This troubleshooting guide covers the most common issues. If you encounter something not covered here, please [open an issue](https://github.com/codomyrmex/codomyrmex/issues) so we can help you and improve this guide for others.

## Navigation Links

- **Parent**: [Project Overview](../README.md)
- **Module Index**: [All Agents](../../AGENTS.md)
- **Documentation**: [Reference Guides](../../docs/README.md)
- **Home**: [Repository Root](../../../README.md)
