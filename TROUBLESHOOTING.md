# 🔍 Codomyrmex Troubleshooting Guide

Comprehensive solutions for common Codomyrmex issues and problems.

## 📋 Quick Navigation

- [🚀 Installation Issues](#installation-issues)
- [🐳 Docker Problems](#docker-problems)
- [🤖 AI/LLM Configuration](#ai-and-llm-issues)
- [📊 Data Visualization Errors](#data-visualization-errors)
- [🔧 Module Import Errors](#module-import-errors)
- [🧪 Testing Problems](#testing-issues)
- [📚 Documentation Issues](#documentation-problems)
- [🚦 Performance Issues](#performance-problems)

## 🚀 Installation Issues

### **❌ `ModuleNotFoundError` After Installation**

**Symptoms:**
```bash
ModuleNotFoundError: No module named 'codomyrmex'
```

**Solutions:**

1. **Reinstall in Editable Mode:**
   ```bash
   pip uninstall codomyrmex
   pip install -e .
   ```

2. **Check Python Path:**
   ```bash
   python -c "import sys; print(sys.path)"
   # Ensure project root is in path
   ```

3. **Virtual Environment Issues:**
   ```bash
   # Deactivate and reactivate
   deactivate
   source .venv/bin/activate
   pip install -e .
   ```

### **❌ `externally-managed-environment` Error**

**Symptoms:**
```bash
error: externally-managed-environment
```

**Solutions:**

1. **Use uv (Recommended):**
   ```bash
   # Install uv
   curl -LsSf https://astral.sh/uv/install.sh | sh
   source ~/.cargo/env

   # Use uv for installation
   uv venv .venv
   source .venv/bin/activate
   uv pip install -e .
   ```

2. **Use `--user` Flag:**
   ```bash
   pip install --user -e .
   ```

3. **Use `--break-system-packages**:**
   ```bash
   pip install --break-system-packages -e .
   # ⚠️  Only use as last resort
   ```

### **❌ `uv` Command Not Found**

**Solutions:**
```bash
# Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# Add to PATH
export PATH="$HOME/.cargo/bin:$PATH"

# Or reinstall
pip install uv
```

## 🐳 Docker Problems

### **❌ Docker Not Available**

**Symptoms:**
```python
{"error": "Docker is required but not available or not running"}
```

**Solutions:**

1. **Install Docker:**
   ```bash
   # Ubuntu/Debian
   sudo apt-get update
   sudo apt-get install docker.io
   sudo systemctl start docker
   sudo usermod -aG docker $USER

   # macOS
   brew install --cask docker
   # Or download from docker.com

   # Windows
   # Download from docker.com/windows
   ```

2. **Start Docker Service:**
   ```bash
   # Linux
   sudo systemctl start docker

   # macOS/Windows
   # Start Docker Desktop application
   ```

3. **Add User to Docker Group (Linux):**
   ```bash
   sudo usermod -aG docker $USER
   # Logout and login again, or run: newgrp docker
   ```

### **❌ Docker Permission Denied**

**Solutions:**
```bash
# Check Docker group membership
groups | grep docker

# If not in docker group:
sudo usermod -aG docker $USER
# Logout and login again

# Or run with sudo (not recommended for development)
sudo docker run ...
```

### **❌ Code Execution Timeout**

**Symptoms:**
```python
{"error": "Execution timed out"}
```

**Solutions:**

1. **Increase Timeout:**
   ```python
   from codomyrmex.code_execution_sandbox import execute_code

   result = execute_code(
       language="python",
       code="long_running_code()",
       timeout=120  # Increase timeout to 2 minutes
   )
   ```

2. **Check Code Efficiency:**
   - Optimize loops and algorithms
   - Remove infinite loops
   - Check for blocking operations

3. **Check Docker Resources:**
   ```bash
   docker system info  # Check Docker resource limits
   docker stats        # Monitor container resource usage
   ```

## 🤖 AI and LLM Issues

### **❌ API Key Not Found**

**Symptoms:**
```python
{"error": "OPENAI_API_KEY environment variable not set"}
```

**Solutions:**

1. **Create .env File:**
   ```bash
   # In project root
   cat > .env << EOF
   OPENAI_API_KEY="sk-your-openai-key-here"
   ANTHROPIC_API_KEY="sk-ant-your-anthropic-key-here"
   GOOGLE_API_KEY="your-google-api-key-here"
   EOF
   ```

2. **Load .env File:**
   ```python
   from dotenv import load_dotenv
   load_dotenv()  # Load .env file

   # Or use environment_setup module
   from environment_setup.env_checker import check_and_setup_env_vars
   check_and_setup_env_vars("/path/to/project")
   ```

3. **Set Environment Variables Directly:**
   ```bash
   export OPENAI_API_KEY="sk-your-key-here"
   # Or add to ~/.bashrc or ~/.zshrc
   ```

### **❌ LLM API Rate Limit Exceeded**

**Solutions:**

1. **Implement Retry Logic:**
   ```python
   import time
   from codomyrmex.ai_code_editing import generate_code_snippet

   def generate_with_retry(prompt, max_retries=3):
       for attempt in range(max_retries):
           try:
               result = generate_code_snippet(prompt, "python")
               return result
           except Exception as e:
               if "rate limit" in str(e).lower():
                   wait_time = 2 ** attempt  # Exponential backoff
                   print(f"Rate limited. Waiting {wait_time}s...")
                   time.sleep(wait_time)
               else:
                   raise
   ```

2. **Reduce Request Frequency:**
   - Cache responses for similar prompts
   - Batch requests when possible
   - Use smaller models for simple tasks

### **❌ LLM Response Quality Issues**

**Solutions:**

1. **Improve Prompts:**
   ```python
   # Better prompt structure
   detailed_prompt = f"""
   Create a Python function to {task}.

   Requirements:
   - Use type hints
   - Include comprehensive docstring
   - Handle edge cases
   - Follow PEP 8 style guidelines

   Context: {additional_context}
   """
   ```

2. **Provide Context:**
   ```python
   result = generate_code_snippet(
       prompt="Add error handling to this function",
       language="python",
       context_code="def existing_function():\n    return risky_operation()"
   )
   ```

3. **Try Different Models:**
   ```python
   # Try different models for different tasks
   result = generate_code_snippet(
       prompt="Complex algorithm implementation",
       language="python",
       model_name="gpt-4-turbo-preview"  # More capable model
   )
   ```

## 📊 Data Visualization Errors

### **❌ Matplotlib Display Issues**

**Symptoms:**
```python
UserWarning: Matplotlib is currently using a non-GUI backend
```

**Solutions:**

1. **Set Display Backend:**
   ```python
   import matplotlib
   matplotlib.use('Agg')  # Use non-interactive backend
   # Or
   matplotlib.use('TkAgg')  # Use Tkinter backend
   ```

2. **Save Instead of Show:**
   ```python
   from codomyrmex.data_visualization import create_line_plot

   create_line_plot(
       x_data=[1, 2, 3],
       y_data=[1, 4, 9],
       output_path="plot.png",
       show_plot=False  # Don't try to display
   )
   ```

### **❌ Plot Not Saving**

**Symptoms:**
```python
FileNotFoundError: [Errno 2] No such file or directory: 'plot.png'
```

**Solutions:**

1. **Create Output Directory:**
   ```python
   import os
   from pathlib import Path

   output_dir = Path("output/plots")
   output_dir.mkdir(parents=True, exist_ok=True)

   create_line_plot(
       x_data=x,
       y_data=y,
       output_path=str(output_dir / "plot.png")
   )
   ```

2. **Check Permissions:**
   ```bash
   ls -la output/plots/  # Check directory permissions
   chmod 755 output/plots/  # Fix permissions if needed
   ```

### **❌ Missing Dependencies**

**Solutions:**
```bash
# Install visualization dependencies
pip install matplotlib seaborn numpy pandas

# Or install all optional dependencies
pip install -e .[all]
pip install -e .[visualization]
```

## 🔧 Module Import Errors

### **❌ Circular Import Issues**

**Solutions:**

1. **Use Delayed Imports:**
   ```python
   # Instead of top-level import
   # from other_module import function

   # Use inside functions
   def my_function():
       from other_module import function
       return function()
   ```

2. **Use TYPE_CHECKING:**
   ```python
   from typing import TYPE_CHECKING

   if TYPE_CHECKING:
       from other_module import SomeClass
   ```

### **❌ Version Compatibility Issues**

**Solutions:**

1. **Check Package Versions:**
   ```bash
   pip list | grep codomyrmex
   python -c "import codomyrmex; print(codomyrmex.__version__)"
   ```

2. **Update Dependencies:**
   ```bash
   pip install --upgrade codomyrmex
   pip install -e . --upgrade
   ```

3. **Check Python Version:**
   ```bash
   python --version  # Should be 3.10+
   ```

## 🧪 Testing Issues

### **❌ Tests Failing Due to Missing Dependencies**

**Solutions:**

1. **Install Test Dependencies:**
   ```bash
   pip install pytest pytest-cov pytest-mock
   # Or
   pip install -e .[dev]
   ```

2. **Run Specific Test Categories:**
   ```bash
   # Run only unit tests
   pytest testing/unit/ -v

   # Skip integration tests
   pytest -m "not integration"
   ```

### **❌ Mock Objects Not Working**

**Solutions:**

1. **Use Correct Mock Import:**
   ```python
   from unittest.mock import patch, MagicMock
   # Instead of
   from mock import patch, MagicMock
   ```

2. **Patch at Correct Level:**
   ```python
   # Patch where the module is imported
   with patch('module.submodule.function') as mock_func:
       # Test code
   ```

## 📚 Documentation Problems

### **❌ Documentation Not Building**

**Solutions:**

1. **Install Documentation Dependencies:**
   ```bash
   cd code/documentation
   npm install
   ```

2. **Build Documentation:**
   ```bash
   cd code/documentation
   npm run build
   npm run serve  # To preview locally
   ```

3. **Check Node.js Version:**
   ```bash
   node --version  # Should be 18+
   npm --version
   ```

### **❌ Docusaurus Errors**

**Solutions:**
```bash
# Clear cache and rebuild
cd code/documentation
rm -rf .docusaurus/
npm run clear
npm run build
```

## 🚦 Performance Issues

### **❌ Slow AI Responses**

**Solutions:**

1. **Use Smaller Models:**
   ```python
   result = generate_code_snippet(
       prompt="Simple task",
       language="python",
       model_name="gpt-3.5-turbo"  # Faster than GPT-4
   )
   ```

2. **Implement Caching:**
   ```python
   from functools import lru_cache

   @lru_cache(maxsize=100)
   def cached_generate_code(prompt, language):
       return generate_code_snippet(prompt, language)
   ```

3. **Optimize Prompts:**
   - Use shorter, more focused prompts
   - Provide clear, specific instructions
   - Include examples when possible

### **❌ Memory Issues with Large Codebases**

**Solutions:**

1. **Process in Chunks:**
   ```python
   from codomyrmex.pattern_matching import analyze_repository_path

   # Analyze specific directories instead of entire codebase
   result = analyze_repository_path(
       path="src/specific_module",
       config={"analysis_depth": "shallow"}
   )
   ```

2. **Use Streaming for Large Outputs:**
   ```python
   # For large visualizations, save to file instead of memory
   create_histogram(
       data=large_dataset,
       output_path="large_histogram.png",
       show_plot=False
   )
   ```

### **❌ Docker Container Resource Limits**

**Solutions:**

1. **Increase Docker Resources:**
   ```bash
   # Edit Docker Desktop settings to increase memory/CPU limits
   # Or configure via docker daemon.json
   ```

2. **Optimize Code Execution:**
   ```python
   result = execute_code(
       language="python",
       code="memory_efficient_code()",
       timeout=60  # Reasonable timeout
   )
   ```

## 🔍 Debug Mode and Logging

### **Enable Debug Logging**
```python
import logging
from codomyrmex.logging_monitoring import setup_logging

# Enable debug logging
setup_logging(level=logging.DEBUG)

# Or set environment variable
import os
os.environ['LOG_LEVEL'] = 'DEBUG'
```

### **Common Debug Commands**
```bash
# Check environment
codomyrmex check

# View logs
tail -f ~/.codomyrmex/logs/codomyrmex.log

# Check Docker status
docker ps -a
docker logs <container_id>

# Check Python environment
python -c "import codomyrmex; print(codomyrmex.__file__)"
pip list | grep codomyrmex
```

## 📞 Getting Help

### **Community Resources**
- **[📖 Documentation](code/documentation/README.md)** - Comprehensive guides
- **[💬 GitHub Discussions](https://github.com/codomyrmex/codomyrmex/discussions)** - Ask questions
- **[🐛 GitHub Issues](https://github.com/codomyrmex/codomyrmex/issues)** - Report bugs
- **[📧 Mailing List](mailto:codomyrmex-users@googlegroups.com)** - Community discussions

### **Quick Diagnostic Script**
```python
# Run this to diagnose common issues
python -c "
import sys
print('Python version:', sys.version)
print('Platform:', sys.platform)

try:
    import codomyrmex
    print('✅ Codomyrmex imported successfully')
except ImportError as e:
    print('❌ Codomyrmex import failed:', e)

try:
    import docker
    print('✅ Docker SDK available')
except ImportError:
    print('⚠️  Docker SDK not available')

import os
api_keys = ['OPENAI_API_KEY', 'ANTHROPIC_API_KEY', 'GOOGLE_API_KEY']
for key in api_keys:
    if os.getenv(key):
        print(f'✅ {key} is set')
    else:
        print(f'⚠️  {key} is not set')
"
```

---

**💡 Still having issues?** Check the [full documentation](code/documentation/README.md) or create an issue on GitHub with your error messages and environment details.
