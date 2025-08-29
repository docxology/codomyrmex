# Development Environment Setup

This guide helps you set up a complete development environment for contributing to Codomyrmex.

## 🎯 Overview

Setting up a development environment for Codomyrmex involves:
1. **Local Development Setup** - Core tools and dependencies
2. **Development Tools** - Linting, formatting, and testing tools
3. **Module Development** - Tools for creating and testing new modules
4. **Documentation Development** - Tools for documentation generation and testing
5. **Quality Assurance** - Testing, security, and CI/CD integration

## 🛠️ Core Development Setup

### **Prerequisites**
- Python 3.10+ (3.11 or 3.12 recommended)
- Git 2.30+
- Node.js 18+ (for documentation)
- Docker (for code execution sandbox)
- `uv` (recommended) or `pip`

### **Quick Development Setup**
```bash
# 1. Fork and clone your fork
git clone https://github.com/YOUR_USERNAME/codomyrmex.git
cd codomyrmex

# 2. Automated development setup
bash src/codomyrmex/environment_setup/scripts/setup_dev_env.sh

# 3. Verify setup
codomyrmex check
pytest testing/unit/ -x  # Run tests (stop at first failure)
```

### **Manual Development Setup**
```bash
# 1. Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# 2. Install development dependencies
pip install -e ".[dev]"

# 3. Install pre-commit hooks (recommended)
pre-commit install

# 4. Setup Node.js dependencies (for documentation)
cd src/codomyrmex/documentation
npm install
cd ../../..

# 5. Verify installation
codomyrmex check
```

## 📦 Development Dependencies

The development environment includes additional tools beyond the base installation:

### **Code Quality Tools**
```bash
# Linting and formatting
black              # Code formatting
ruff               # Fast linting
pylint             # Comprehensive code analysis
mypy               # Type checking
bandit             # Security scanning

# Usage
black src/ testing/              # Format code
ruff src/ testing/               # Quick linting  
pylint src/codomyrmex/          # Detailed analysis
mypy src/codomyrmex/            # Type checking
bandit -r src/codomyrmex/       # Security scan
```

### **Testing Tools**
```bash
# Testing framework and coverage
pytest             # Testing framework
pytest-cov         # Coverage reporting
pytest-mock        # Mocking utilities

# Usage
pytest testing/                           # Run all tests
pytest testing/unit/test_specific.py -v  # Run specific tests
pytest --cov=src/codomyrmex --cov-report=html  # Coverage report
```

### **Development Utilities**
```bash
# Git and development workflow
pre-commit         # Git hooks for quality checks
commitizen         # Conventional commits (optional)

# Dependency management
pip-tools          # Dependency management
uv                 # Fast package manager (recommended)
```

## 🔧 IDE Setup

### **VS Code (Recommended)**
Create `.vscode/settings.json`:
```json
{
    "python.defaultInterpreterPath": "./.venv/bin/python",
    "python.terminal.activateEnvironment": true,
    "python.formatting.provider": "black",
    "python.linting.enabled": true,
    "python.linting.pylintEnabled": true,
    "python.linting.flake8Enabled": false,
    "python.testing.pytestEnabled": true,
    "python.testing.pytestArgs": ["testing"],
    "files.exclude": {
        "**/__pycache__": true,
        "**/*.pyc": true,
        ".pytest_cache": true,
        ".mypy_cache": true
    },
    "editor.formatOnSave": true,
    "editor.codeActionsOnSave": {
        "source.organizeImports": true
    }
}
```

### **PyCharm/IntelliJ**
1. Set Python interpreter to `.venv/bin/python`
2. Configure pytest as default test runner
3. Enable Black as code formatter
4. Configure pylint and mypy as external tools

## 📝 Pre-commit Hooks

Pre-commit hooks ensure code quality before commits:

### **Setup Pre-commit**
```bash
# Install hooks
pre-commit install

# Update to latest versions
pre-commit autoupdate

# Run on all files manually
pre-commit run --all-files
```

### **Pre-commit Configuration (`.pre-commit-config.yaml`)**
```yaml
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.4.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-added-large-files
      - id: check-merge-conflict

  - repo: https://github.com/psf/black
    rev: 23.1.0
    hooks:
      - id: black

  - repo: https://github.com/charliermarsh/ruff-pre-commit
    rev: v0.0.254
    hooks:
      - id: ruff

  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.0.1
    hooks:
      - id: mypy
        additional_dependencies: [types-requests]
```

## 🧪 Testing Environment

### **Running Tests**
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src/codomyrmex --cov-report=html --cov-report=term

# Run specific test categories
pytest -m unit          # Unit tests only
pytest -m integration   # Integration tests only
pytest -k "test_ai"     # Tests matching pattern

# Run tests for specific module
pytest testing/unit/test_data_visualization.py -v

# Run tests in parallel (faster)
pytest -n auto  # Requires pytest-xdist
```

### **Test Coverage Requirements**
- **Minimum coverage**: 80% (enforced by CI)
- **Target coverage**: 90%+ for new modules
- **Coverage reporting**: HTML reports generated in `testing/htmlcov/`

### **Writing Tests**
Follow the existing patterns:
```python
# testing/unit/test_my_module.py
import pytest
from unittest.mock import patch, MagicMock

from codomyrmex.my_module import my_function


class TestMyModule:
    """Test suite for my_module"""
    
    def test_my_function_success(self):
        """Test successful execution of my_function"""
        result = my_function("input")
        assert result == "expected_output"
    
    def test_my_function_error_handling(self):
        """Test error handling in my_function"""
        with pytest.raises(ValueError):
            my_function("invalid_input")
    
    @patch('codomyrmex.my_module.external_dependency')
    def test_my_function_with_mock(self, mock_dep):
        """Test my_function with mocked dependencies"""
        mock_dep.return_value = "mocked_result"
        result = my_function("input")
        assert result == "mocked_result"
        mock_dep.assert_called_once_with("input")
```

## 📚 Documentation Development

### **Local Documentation Development**
```bash
# Start documentation development server
cd src/codomyrmex/documentation
npm run start  # Opens browser with live-reload

# Build documentation site
npm run build

# Serve built documentation
npm run serve
```

### **Documentation Structure**
The documentation system has two parts:
- **`/docs/`**: Documentation about Codomyrmex itself (this guide!)
- **`src/codomyrmex/documentation/`**: Tool for generating documentation websites

### **Writing Documentation**
- Use Markdown with clear headers and structure
- Include code examples that actually work
- Add screenshots for UI-related features
- Keep documentation synchronized with code changes

## 🔧 Module Development

### **Creating a New Module**
```bash
# Use the module template
cp -r src/codomyrmex/module_template src/codomyrmex/my_new_module

# Follow the development checklist
# 1. Update __init__.py and main module file
# 2. Write comprehensive tests
# 3. Update documentation
# 4. Add to requirements if needed
# 5. Test integration with other modules
```

### **Module Development Workflow**
1. **Design Phase**
   - Define module purpose and API
   - Identify dependencies on other modules
   - Plan testing strategy

2. **Implementation Phase**
   - Write core functionality
   - Add comprehensive error handling
   - Implement logging with codomyrmex.logging_monitoring
   - Add type hints throughout

3. **Testing Phase**
   - Write unit tests (>90% coverage)
   - Add integration tests with other modules
   - Test error conditions and edge cases
   - Validate security considerations

4. **Documentation Phase**
   - Update module README.md
   - Write API specification
   - Create usage examples
   - Add tutorials for common use cases

5. **Integration Phase**
   - Test with other modules
   - Add to system discovery
   - Update module relationships documentation
   - Add CI/CD pipeline tests

## 🚀 Development Workflow

### **Daily Development Workflow**
```bash
# 1. Start development session
source .venv/bin/activate
git pull origin main

# 2. Create feature branch
git checkout -b feature/my-new-feature

# 3. Make changes and test frequently
# Edit code...
pytest testing/unit/test_my_module.py -v  # Test your changes
black src/ testing/                       # Format code

# 4. Run quality checks
pre-commit run --all-files  # Check all quality standards
pytest --cov=src/codomyrmex  # Full test suite with coverage

# 5. Commit and push
git add .
git commit -m "feat: add new feature for module X"
git push origin feature/my-new-feature

# 6. Create pull request
# Use GitHub web interface or gh CLI
```

### **Code Review Process**
1. **Self-Review**
   - Run all tests locally
   - Check code coverage
   - Review your own changes for clarity
   - Ensure documentation is updated

2. **Automated Checks**
   - CI/CD pipeline runs tests
   - Code quality checks (linting, formatting)
   - Security scans
   - Documentation build tests

3. **Peer Review**
   - Code functionality and design
   - Test adequacy and coverage
   - Documentation clarity
   - Security considerations

## 🔐 Security Considerations

### **Security Development Practices**
- Never commit secrets or API keys
- Use environment variables for configuration
- Validate and sanitize all inputs
- Follow principle of least privilege
- Regular security scanning with bandit

### **Secure Development Workflow**
```bash
# Security scanning
bandit -r src/codomyrmex/          # Python security issues
safety check                      # Vulnerability scanning
pip-audit                         # Dependency vulnerabilities

# Secret scanning (before commit)
pre-commit run --all-files        # Includes secret detection
```

## 🎯 Performance Development

### **Performance Testing**
```bash
# Profile module performance
python -m cProfile -o profile.stats my_script.py
python -c "import pstats; pstats.Stats('profile.stats').sort_stats('cumulative').print_stats()"

# Memory profiling
pip install memory-profiler
@profile
def my_function():
    # Your code here
python -m memory_profiler my_script.py
```

### **Performance Guidelines**
- Profile before optimizing
- Focus on algorithmic improvements
- Use lazy loading for expensive operations
- Cache computation results when appropriate
- Monitor memory usage for large data processing

## 📞 Getting Help

### **Development Support**
- **Documentation**: This guide and [Architecture Overview](../project/architecture.md)
- **Code Examples**: Look at existing modules for patterns
- **Community**: [GitHub Discussions](https://github.com/codomyrmex/codomyrmex/discussions)
- **Issues**: [GitHub Issues](https://github.com/codomyrmex/codomyrmex/issues)

### **Debugging Tips**
```python
# Use the logging system for debugging
from codomyrmex.logging_monitoring import get_logger
logger = get_logger(__name__)

# Add debug logging
logger.debug(f"Function called with args: {args}")
logger.info(f"Processing {len(items)} items")

# Use breakpoint() for interactive debugging
def my_function(data):
    breakpoint()  # Python 3.7+ built-in debugger
    return process(data)
```

---

This development environment setup ensures you have all the tools needed to contribute effectively to Codomyrmex while maintaining high code quality and testing standards.
