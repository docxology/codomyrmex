# Troubleshooting Guide for Codomyrmex Examples

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: December 2025

## Overview

This guide provides solutions to common issues encountered when running Codomyrmex examples. It covers import errors, configuration problems, execution failures, and platform-specific issues.

## Quick Diagnosis

### Check System Requirements

Before running examples, ensure your system meets the minimum requirements:

```bash
# Check Python version (3.8+ required)
python --version

# Check pip version
pip --version

# Check available disk space
df -h

# Check memory
free -h  # Linux/macOS
```

### Environment Setup

```bash
# Ensure you're in the project root
pwd
# Should show: /path/to/codomyrmex

# Check if src is in Python path
python -c "import sys; print('src' in str(sys.path))"
```

## Common Issues and Solutions

### 1. Import Errors

#### `ModuleNotFoundError: No module named 'codomyrmex'`

**Symptoms**: Examples fail immediately with import errors.

**Causes**:
- Python path not configured correctly
- Running from wrong directory
- Virtual environment issues

**Solutions**:

1. **Check working directory**:
   ```bash
   cd /path/to/codomyrmex
   pwd  # Should show the codomyrmex directory
   ```

2. **Verify src directory exists**:
   ```bash
   ls -la src/
   # Should show codomyrmex/ directory
   ```

3. **Check Python path**:
   ```bash
   python -c "import sys; sys.path.insert(0, 'src'); import codomyrmex"
   ```

4. **Run from correct directory**:
   ```bash
   cd examples/{module_name}
   PYTHONPATH=../../src python example_basic.py
   ```

#### `ImportError: cannot import name 'SomeClass'`

**Symptoms**: Specific class or function import fails.

**Causes**:
- Module has import issues (known for some modules)
- Dependencies not installed
- Circular import issues

**Affected Modules**:
- `api_standardization` - Uses mock implementation
- `events` - Uses mock implementation
- `model_context_protocol` - Has import issues

**Solutions**:

1. **Check if module uses mocks**:
   ```python
   # Look for mock usage in the example
   grep -n "mock" examples/{module}/example_basic.py
   ```

2. **Install missing dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Check module status**:
   ```bash
   python -c "import codomyrmex.{module}; print('Module OK')"
   ```

### 2. Configuration Issues

#### `FileNotFoundError: config.yaml`

**Symptoms**: Example fails to load configuration file.

**Solutions**:

1. **Check file exists**:
   ```bash
   cd examples/{module_name}
   ls -la config.yaml config.json
   ```

2. **Verify file permissions**:
   ```bash
   ls -l config.yaml
   # Should show readable permissions (e.g., -rw-r--r--)
   ```

3. **Check file syntax**:
   ```bash
   python -c "import yaml; yaml.safe_load(open('config.yaml'))"
   ```

#### Environment Variable Substitution Issues

**Symptoms**: Configuration values not substituted correctly.

**Solutions**:

1. **Check environment variables**:
   ```bash
   echo $API_KEY
   echo $DATABASE_URL
   ```

2. **Set missing variables**:
   ```bash
   export API_KEY="your_key_here"
   export DATABASE_URL="sqlite:///test.db"
   ```

3. **Use default values**:
   ```yaml
   # In config.yaml
   api_key: ${API_KEY:default_key}
   ```

4. **Test substitution**:
   ```bash
   python -c "
   import os
   value = os.environ.get('TEST_VAR', 'default')
   print(f'TEST_VAR: {value}')
   "
   ```

### 3. Execution Failures

#### `PermissionError: [Errno 13] Permission denied`

**Symptoms**: Cannot write to output or log directories.

**Solutions**:

1. **Check directory permissions**:
   ```bash
   ls -ld examples/{module}/output/
   ls -ld examples/{module}/logs/
   ```

2. **Create directories if missing**:
   ```bash
   mkdir -p examples/{module}/output
   mkdir -p examples/{module}/logs
   ```

3. **Fix permissions**:
   ```bash
   chmod 755 examples/{module}/output
   chmod 755 examples/{module}/logs
   ```

4. **Run with sudo if necessary** (not recommended):
   ```bash
   sudo python example_basic.py
   ```

#### `TimeoutError` or Hanging Execution

**Symptoms**: Example takes too long or hangs indefinitely.

**Solutions**:

1. **Check system resources**:
   ```bash
   top  # Linux
   htop  # Linux (if installed)
   Activity Monitor  # macOS
   ```

2. **Kill long-running processes**:
   ```bash
   ps aux | grep python
   kill -9 <pid>
   ```

3. **Run with timeout**:
   ```bash
   timeout 60 python example_basic.py
   ```

4. **Check for infinite loops** in the example code.

#### Database Connection Errors

**Symptoms**: Database examples fail with connection errors.

**Solutions**:

1. **Check database server**:
   ```bash
   # SQLite (file-based, usually works)
   ls -la examples/database_management/databases/

   # PostgreSQL
   pg_isready -h localhost

   # MySQL
   mysqladmin ping
   ```

2. **Verify connection string**:
   ```python
   # In config
   database:
     type: sqlite
     database: examples/database_management/databases/api.db
   ```

3. **Check database permissions**:
   ```bash
   chmod 644 examples/database_management/databases/*.db
   ```

### 4. Output Generation Issues

#### Missing Output Files

**Symptoms**: Example runs but no output files generated.

**Solutions**:

1. **Check output directories exist**:
   ```bash
   ls -la examples/{module}/output/
   ```

2. **Verify example completed successfully**:
   ```bash
   echo $?  # Should be 0
   ```

3. **Check for early exits** in example code.

4. **Review log files**:
   ```bash
   cat examples/{module}/logs/*.log
   ```

#### Invalid JSON Output

**Symptoms**: Output file exists but contains invalid JSON.

**Solutions**:

1. **Validate JSON syntax**:
   ```bash
   python -m json.tool examples/{module}/output/results.json
   ```

2. **Check for special characters**:
   ```bash
   cat examples/{module}/output/results.json | grep -P '[^\x00-\x7F]'
   ```

3. **Fix encoding issues**:
   ```python
   # In example code
   with open(output_file, 'w', encoding='utf-8') as f:
       json.dump(data, f, ensure_ascii=False, indent=2)
   ```

### 5. Platform-Specific Issues

#### macOS Issues

**Symptoms**: Examples fail on macOS but work on Linux.

**Solutions**:

1. **Check Homebrew installations**:
   ```bash
   brew list | grep -E "(python|sqlite|postgresql)"
   ```

2. **Update Python**:
   ```bash
   brew upgrade python
   ```

3. **Check PATH**:
   ```bash
   echo $PATH
   which python
   ```

#### Linux Issues

**Symptoms**: Examples fail on Linux distributions.

**Solutions**:

1. **Check package manager**:
   ```bash
   # Ubuntu/Debian
   apt list --installed | grep python

   # CentOS/RHEL
   yum list installed | grep python
   ```

2. **Install system dependencies**:
   ```bash
   # Ubuntu/Debian
   sudo apt-get install python3-dev build-essential

   # CentOS/RHEL
   sudo yum install python3-devel gcc
   ```

#### Windows Issues

**Symptoms**: Examples fail on Windows.

**Solutions**:

1. **Check Python installation**:
   ```cmd
   python --version
   where python
   ```

2. **Set environment variables**:
   ```cmd
   set PYTHONPATH=%CD%\src
   set PATH=%PATH%;%CD%\scripts
   ```

3. **Use Windows-compatible paths**:
   ```python
   # Use forward slashes or Path objects
   from pathlib import Path
   output_dir = Path("output")
   ```

### 6. Module-Specific Issues

#### AI Code Editing Examples

**Symptoms**: OpenAI/Claude API calls fail.

**Solutions**:

1. **Check API keys**:
   ```bash
   echo $OPENAI_API_KEY
   echo $ANTHROPIC_API_KEY
   ```

2. **Verify API key format**:
   ```bash
   # Should start with sk- for OpenAI
   echo $OPENAI_API_KEY | cut -c1-3
   ```

3. **Check API quota**:
   ```bash
   curl -H "Authorization: Bearer $OPENAI_API_KEY" \
        https://api.openai.com/v1/models
   ```

#### Database Examples

**Symptoms**: Database operations fail.

**Solutions**:

1. **Check database file permissions**:
   ```bash
   ls -la examples/database_management/databases/
   chmod 644 examples/database_management/databases/*.db
   ```

2. **Verify SQLite installation**:
   ```bash
   python -c "import sqlite3; print('SQLite OK')"
   ```

#### Containerization Examples

**Symptoms**: Docker commands fail.

**Solutions**:

1. **Check Docker installation**:
   ```bash
   docker --version
   docker info
   ```

2. **Verify Docker daemon**:
   ```bash
   docker ps
   ```

3. **Check user permissions**:
   ```bash
   groups | grep docker
   ```

### 7. Performance Issues

#### Slow Execution

**Symptoms**: Examples take longer than expected.

**Solutions**:

1. **Check system resources**:
   ```bash
   # CPU
   top -n 1 | head -5

   # Memory
   free -h

   # Disk I/O
   iostat -x 1 5
   ```

2. **Profile the example**:
   ```python
   import cProfile
   cProfile.run('main()', 'profile_output.prof')
   ```

3. **Optimize resource usage** in config files.

#### Memory Issues

**Symptoms**: Examples run out of memory.

**Solutions**:

1. **Increase memory limits**:
   ```yaml
   # In config.yaml
   performance:
     memory_limit: 1024MB
   ```

2. **Process data in chunks**:
   ```python
   # Instead of loading all data
   for chunk in process_in_chunks(data, chunk_size=1000):
       process_chunk(chunk)
   ```

3. **Use streaming processing** for large files.

### 8. Testing Issues

#### Test Discovery Problems

**Symptoms**: Pytest doesn't find tests.

**Solutions**:

1. **Check test file naming**:
   ```bash
   find . -name "test_*.py" | head -10
   ```

2. **Verify test structure**:
   ```bash
   python -m pytest --collect-only testing/examples/
   ```

3. **Check imports** in test files.

#### Test Execution Failures

**Symptoms**: Tests pass locally but fail in CI.

**Solutions**:

1. **Check environment differences**:
   ```bash
   # Compare environments
   env | sort > local_env.txt
   # Compare with CI environment
   ```

2. **Use absolute paths**:
   ```python
   # Instead of relative paths
   project_root = Path(__file__).parent.parent.parent
   config_path = project_root / "examples" / module / "config.yaml"
   ```

3. **Mock external dependencies**:
   ```python
   @pytest.fixture
   def mock_api_response():
       return {"status": "success", "data": []}
   ```

## Diagnostic Tools

### System Information

```bash
# Basic system info
uname -a
python --version
pip --version

# Python environment
python -c "import sys; print(sys.path)"
python -c "import sys; print(sys.version_info)"

# Installed packages
pip list | grep -E "(codomyrmex|pytest|pyyaml)"
```

### Example Debugging

```python
# Add debug prints to example
import logging
logging.basicConfig(level=logging.DEBUG)

# Check current working directory
import os
print(f"CWD: {os.getcwd()}")

# Check file paths
from pathlib import Path
config_path = Path("config.yaml")
print(f"Config exists: {config_path.exists()}")
print(f"Absolute path: {config_path.absolute()}")
```

### Network Diagnostics

```bash
# Test network connectivity
curl -I https://api.openai.com
curl -I https://api.anthropic.com

# DNS resolution
nslookup api.openai.com

# Check proxy settings
echo $http_proxy $https_proxy
```

## Getting Help

### Community Support

1. **Check existing issues**:
   - GitHub Issues
   - Documentation
   - Stack Overflow

2. **Provide diagnostic information**:
   ```bash
   # System info
   uname -a > system_info.txt
   python --version >> system_info.txt
   pip list >> system_info.txt
   ```

3. **Include error logs**:
   ```bash
   # Run with verbose logging
   PYTHONPATH=src python examples/{module}/example_basic.py 2>&1 | tee error.log
   ```

### Reporting Issues

When reporting issues, include:

1. **Full error traceback**
2. **System information**
3. **Configuration files** (with sensitive data removed)
4. **Steps to reproduce**
5. **Expected vs actual behavior**

## Prevention Strategies

### Development Best Practices

1. **Use virtual environments**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/macOS
   venv\Scripts\activate     # Windows
   ```

2. **Keep dependencies updated**:
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

3. **Test examples regularly**:
   ```bash
   python -m pytest testing/examples/
   ```

4. **Use version control** for configuration changes.

### Configuration Management

1. **Validate configurations** before running:
   ```bash
   python -c "import yaml; yaml.safe_load(open('config.yaml'))"
   ```

2. **Use environment variables** for secrets:
   ```bash
   export API_KEY="your_secure_key"
   ```

3. **Document configuration changes**.

### Monitoring and Logging

1. **Enable detailed logging**:
   ```yaml
   logging:
     level: DEBUG
     file: debug.log
   ```

2. **Monitor resource usage**:
   ```bash
   top -p $(pgrep -f example_basic.py)
   ```

3. **Set up alerts** for failures.

## Advanced Troubleshooting

### Debugging Import Issues

```python
# Detailed import debugging
import sys
import importlib

try:
    import codomyrmex.example_module
    print("Import successful")
except ImportError as e:
    print(f"Import failed: {e}")
    print(f"Python path: {sys.path}")
    print(f"Current directory: {os.getcwd()}")

    # Try to find the module
    import pkgutil
    for importer, modname, ispkg in pkgutil.iter_modules(['src']):
        print(f"Found module: {modname}")
```

### Profiling Performance Issues

```python
import cProfile
import pstats
from io import StringIO

def profile_example():
    # Run your example function here
    main()

# Profile the execution
profiler = cProfile.Profile()
profiler.enable()
profile_example()
profiler.disable()

# Print statistics
stats = pstats.Stats(profiler)
stats.sort_stats('cumulative')
stats.print_stats(20)  # Top 20 functions
```

### Memory Leak Detection

```python
import tracemalloc
import gc

# Start tracing
tracemalloc.start()

# Run example
main()

# Check memory usage
current, peak = tracemalloc.get_traced_memory()
print(f"Current memory usage: {current / 1024 / 1024:.1f} MB")
print(f"Peak memory usage: {peak / 1024 / 1024:.1f} MB")

# Get traceback of allocations
snapshot = tracemalloc.take_snapshot()
for stat in snapshot.statistics('lineno')[:10]:
    print(stat)
```

## Quick Reference

### Most Common Fixes

| Issue | Quick Fix |
|-------|-----------|
| Import error | `PYTHONPATH=src python example.py` |
| Config missing | Check file exists in correct directory |
| Permission denied | `chmod 755 output/ logs/` |
| Database error | Check SQLite file permissions |
| API key error | `export API_KEY=your_key` |
| Timeout | `timeout 60 python example.py` |

### Emergency Commands

```bash
# Kill hanging processes
pkill -f python

# Clean up generated files
find examples/ -name "*.log" -delete
find examples/ -name "*_results.json" -delete

# Reset example state
rm -rf examples/*/output/*
rm -rf examples/*/logs/*

# Full system reset (use with caution)
git clean -fdx examples/
```

---

**Need more help?** Check the [README.md](README.md) or create an issue on GitHub.
