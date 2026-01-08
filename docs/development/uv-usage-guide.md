# UV Usage Guide for Codomyrmex

This guide covers the use of `uv` (the fast Python package manager) with Codomyrmex for optimal development experience.

## 🚀 Why UV?

UV is a fast, reliable Python package manager that offers significant advantages over traditional pip:

- **10-100x faster** than pip for package installation
- **Deterministic builds** with lock files
- **Automatic virtual environment management**
- **Better dependency resolution**
- **Compatible with existing pip workflows**

## 📦 Installation

### Install UV
```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows (PowerShell)
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# Or via pip (if you have Python)
pip install uv
```

### Verify Installation
```bash
uv --version
```

## 🏗️ Project Setup with UV

### 1. Clone and Setup
```bash
# Clone the repository
git clone https://github.com/codomyrmex/codomyrmex.git
cd codomyrmex

# Use the automated UV setup script (recommended)
./install_with_uv.sh

# OR manual setup
uv venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
uv pip install -e .
```

### 2. Development Setup
```bash
# Install with development dependencies
uv pip install -e ".[dev]"

# Or install specific development tools
uv pip install pytest black mypy ruff pre-commit
```

## 🔧 Daily Development Workflow

### Virtual Environment Management
```bash
# Activate virtual environment
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Deactivate
deactivate

# Check if environment is active
uv pip list
```

### Package Management
```bash
# Install a new package
uv pip install package-name

# Install with version constraints
uv pip install "package-name>=1.0,<2.0"

# Install from requirements file
uv pip install -r requirements.txt

# Install in development mode
uv pip install -e .

# Update packages
uv pip install --upgrade package-name

# Update all packages
uv pip install --upgrade -r requirements.txt
```

### Dependency Management
```bash
# Generate lock file (already done in project)
uv lock

# Install from lock file
uv pip install -r uv.lock

# Sync dependencies (install exactly what's in lock file)
uv pip sync uv.lock
```

## 🧪 Testing with UV

### Run Tests
```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=src/codomyrmex

# Run specific test file
uv run pytest src/codomyrmex/tests/unit/test_data_visualization.py

# Run with verbose output
uv run pytest -v
```

### Code Quality
```bash
# Format code
uv run black src/ src/codomyrmex/tests/

# Lint code
uv run ruff check src/ src/codomyrmex/tests/

# Type checking
uv run mypy src/codomyrmex/

# Security scanning
uv run bandit -r src/codomyrmex/
```

## 🚀 Performance Benefits

### Speed Comparison
```bash
# Traditional pip workflow
time pip install -e .  # ~30-60 seconds

# UV workflow
time uv pip install -e .  # ~2-5 seconds
```

### Lock File Benefits
- **Reproducible builds**: Same dependencies across all environments
- **Faster CI/CD**: Pre-resolved dependencies
- **Security**: Pinned versions prevent supply chain attacks

## 🔄 Migration from pip

### If you're already using pip
```bash
# Your existing virtual environment will work
source .venv/bin/activate

# Gradually migrate to uv commands
uv pip install -e .  # Instead of pip install -e .
uv pip install package-name  # Instead of pip install package-name
```

### Clean Migration
```bash
# Remove old virtual environment
rm -rf .venv

# Create new with uv
uv venv .venv
source .venv/bin/activate
uv pip install -e .
```

## 🛠️ Advanced UV Features

### Workspace Management
```bash
# UV supports workspaces (already configured in pyproject.toml)
uv sync  # Install all workspace dependencies
```

### Python Version Management
```bash
# Install specific Python version
uv python install 3.11

# Use specific Python version
uv venv --python 3.11 .venv
```

### Script Execution
```bash
# Run scripts without activating environment
uv run python script.py
uv run pytest
uv run black src/
```

## 📊 Monitoring and Debugging

### Dependency Analysis
```bash
# Show dependency tree
uv pip show --tree package-name

# Show all installed packages
uv pip list

# Show outdated packages
uv pip list --outdated
```

### Cache Management
```bash
# Clear UV cache
uv cache clean

# Show cache info
uv cache info
```

## 🔧 Configuration

### UV Configuration File
Create `uv.toml` in project root for custom settings:

```toml
[tool.uv]
# Custom cache directory
cache-dir = "/path/to/cache"

# Custom index URL
index-url = "https://pypi.org/simple"

# Extra index URLs
extra-index-url = ["https://pypi.org/simple"]

# Development dependencies
dev-dependencies = [
    "pytest>=7.0.0",
    "black>=23.0.0",
    "mypy>=1.0.0",
]
```

### Environment Variables
```bash
# Set custom cache directory
export UV_CACHE_DIR="/path/to/cache"

# Set custom index URL
export UV_INDEX_URL="https://pypi.org/simple"

# Enable verbose output
export UV_VERBOSE=1
```

## 🚨 Troubleshooting

### Common Issues

#### 1. Permission Errors
```bash
# Fix: Don't use sudo with uv
# Instead, fix Python installation permissions
sudo chown -R $USER:$USER /usr/local/lib/python3.*/site-packages
```

#### 2. Lock File Conflicts
```bash
# Regenerate lock file
rm uv.lock
uv lock
```

#### 3. Virtual Environment Issues
```bash
# Remove and recreate
rm -rf .venv
uv venv .venv
source .venv/bin/activate
uv pip install -e .
```

#### 4. Package Resolution Issues
```bash
# Clear cache and retry
uv cache clean
uv pip install --no-cache package-name
```

### Debug Mode
```bash
# Enable verbose output
uv --verbose pip install package-name

# Show dependency resolution
uv pip install --dry-run package-name
```

## 📚 Best Practices

### 1. Always Use Lock Files
```bash
# Commit uv.lock to version control
git add uv.lock
git commit -m "Update dependencies"
```

### 2. Use Virtual Environments
```bash
# Always work in virtual environments
uv venv .venv
source .venv/bin/activate
```

### 3. Pin Dependencies
```bash
# Use specific versions in requirements.txt
package-name==1.2.3
```

### 4. Regular Updates
```bash
# Update dependencies regularly
uv pip install --upgrade -r requirements.txt
uv lock  # Update lock file
```

### 5. CI/CD Integration
```yaml
# GitHub Actions example
- name: Install dependencies
  run: |
    uv venv .venv
    source .venv/bin/activate
    uv pip install -r uv.lock
```

## 🔗 Integration with Codomyrmex

### Module Development
```bash
# When developing new modules
uv pip install -e .  # Install in development mode
uv run pytest src/codomyrmex/tests/unit/test_new_module.py
```

### AI Integration
```bash
# Install AI dependencies
uv pip install openai anthropic google-generativeai

# Test AI features
uv run python -c "from codomyrmex.agents.ai_code_editing import generate_code_snippet"
```

### Performance Monitoring
```bash
# Install performance tools
uv pip install psutil

# Run performance tests
uv run python -c "from codomyrmex.performance import PerformanceMonitor"
```

## 📖 Additional Resources

- [UV Documentation](https://docs.astral.sh/uv/)
- [UV GitHub Repository](https://github.com/astral-sh/uv)
- [Python Packaging User Guide](https://packaging.python.org/)
- [Codomyrmex Development Guide](environment-setup.md)

---

**Happy coding with UV and Codomyrmex! 🐜✨**

## Navigation Links

- **Parent**: [Project Overview](../README.md)
- **Module Index**: [All Agents](../../AGENTS.md)
- **Documentation**: [Reference Guides](../../docs/README.md)
- **Home**: [Repository Root](../../../README.md)
