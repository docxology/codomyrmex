# Best Practices Guide for Codomyrmex Examples

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: December 2025

## Overview

This guide outlines best practices for creating, maintaining, and using Codomyrmex examples. It covers code quality, configuration management, error handling, testing, documentation, and maintenance guidelines.

## Example Structure Best Practices

### 1. Consistent File Organization

**✅ Do:**
```bash
examples/{module_name}/
├── example_basic.py      # Main example script
├── config.yaml          # Primary configuration
├── config.json          # Alternative JSON config
└── README.md            # Documentation
```

**❌ Don't:**
```bash
examples/{module_name}/
├── main.py              # Non-standard naming
├── settings.txt         # Non-standard config format
├── docs.md              # Non-standard documentation
└── extra_files/         # Unnecessary subdirectories
```

### 2. Standard Example Template

**✅ Use the standard template:**
```python
#!/usr/bin/env python3
"""
Example: {Module Name} - {Brief Description}

Demonstrates:
- Key feature 1
- Key feature 2
- Integration point

Tested Methods:
- method_name() - Verified in test_{module}.py::TestClass::test_method
"""

import sys
from pathlib import Path

# Add src to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root / "src"))

from codomyrmex.{module} import {TestedMethod}
from examples._common.config_loader import load_config
from examples._common.example_runner import ExampleRunner

def main():
    config = load_config(Path(__file__).parent / "config.yaml")
    runner = ExampleRunner(__file__, config)
    runner.start()

    try:
        # Implementation
        results = {...}
        runner.validate_results(results)
        runner.save_results(results)
        runner.complete()
    except Exception as e:
        runner.error("Example failed", e)
        sys.exit(1)

if __name__ == "__main__":
    main()
```

### 3. Module Import Patterns

**✅ Import from specific modules:**
```python
from codomyrmex.database_management import (
    DatabaseManager,      # Core classes
    DatabaseConnection,   # Data structures
    Migration,           # Key functions
    generate_schema       # Utility functions
)
```

**❌ Don't use wildcard imports:**
```python
from codomyrmex.database_management import *  # Unclear what is imported
```

## Configuration Management Patterns

### 1. Environment Variable Substitution

**✅ Use environment variables for sensitive data:**
```yaml
# config.yaml
api:
  key: ${API_KEY}
  database_url: ${DATABASE_URL:sqlite:///default.db}
  debug: ${DEBUG:false}

database:
  password: ${DB_PASSWORD}
```

**✅ Provide sensible defaults:**
```yaml
performance:
  timeout: ${TIMEOUT:30}
  max_retries: ${MAX_RETRIES:3}
```

### 2. Configuration Validation

**✅ Validate configuration early:**
```python
def validate_config(config: dict) -> bool:
    """Validate configuration structure."""
    required_fields = ['api', 'database']
    for field in required_fields:
        if field not in config:
            raise ValueError(f"Missing required config field: {field}")

    if 'port' in config.get('api', {}):
        port = config['api']['port']
        if not isinstance(port, int) or not (1000 <= port <= 9999):
            raise ValueError("API port must be integer between 1000-9999")

    return True
```

**✅ Handle configuration errors gracefully:**
```python
def main():
    try:
        config = load_config("config.yaml")
        validate_config(config)
    except FileNotFoundError:
        print("Configuration file not found. Using defaults.")
        config = get_default_config()
    except ValueError as e:
        print(f"Configuration error: {e}")
        sys.exit(1)
```

### 3. Configuration Inheritance

**✅ Use configuration inheritance for environments:**
```yaml
# config_base.yaml
logging:
  level: INFO
  format: "%(asctime)s - %(levelname)s - %(message)s"

# config_development.yaml
extends: config_base.yaml
logging:
  level: DEBUG
api:
  debug: true
  port: 8000

# config_production.yaml
extends: config_base.yaml
logging:
  level: WARNING
api:
  debug: false
  port: 443
```

## Error Handling Strategies

### 1. Comprehensive Exception Handling

**✅ Handle specific exceptions:**
```python
def main():
    try:
        # Database operations
        db.connect()
        db.execute_query("SELECT * FROM users")

    except ConnectionError as e:
        logger.error(f"Database connection failed: {e}")
        # Attempt reconnection or graceful degradation

    except QueryError as e:
        logger.error(f"Query execution failed: {e}")
        # Log query details and rollback if needed

    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        # Last resort error handling
    finally:
        # Always cleanup resources
        if 'db' in locals():
            db.close()
```

### 2. Resource Management

**✅ Use context managers for resources:**
```python
def process_with_database(config):
    with DatabaseConnection(config['database']) as db:
        with db.transaction():
            # Database operations
            users = db.execute_query("SELECT * FROM users")
            # Process users
            return process_users(users)
```

**✅ Implement proper cleanup:**
```python
class ExampleRunner:
    def __init__(self, config):
        self.config = config
        self.resources = []

    def add_resource(self, resource):
        self.resources.append(resource)

    def cleanup(self):
        for resource in reversed(self.resources):
            try:
                if hasattr(resource, 'close'):
                    resource.close()
                elif hasattr(resource, 'cleanup'):
                    resource.cleanup()
            except Exception as e:
                logger.warning(f"Cleanup failed for {resource}: {e}")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.cleanup()
```

### 3. Graceful Degradation

**✅ Provide fallbacks for optional features:**
```python
def load_ai_provider(config):
    """Load AI provider with fallback."""
    providers = [
        ('openai', config.get('openai_key')),
        ('anthropic', config.get('anthropic_key')),
        ('mock', None)  # Always available fallback
    ]

    for provider_name, api_key in providers:
        try:
            provider = load_provider(provider_name, api_key)
            logger.info(f"Using {provider_name} provider")
            return provider
        except ProviderError:
            continue

    raise RuntimeError("No AI provider available")
```

## Testing Integration Approaches

### 1. Reference Tested Methods

**✅ Document tested methods in docstrings:**
```python
"""
Example: Database Management - Connection and Schema Operations

Tested Methods:
- DatabaseManager.add_connection() - Verified in test_database_management.py::TestDatabaseManager::test_add_connection
- DatabaseConnection.execute_query() - Verified in test_database_management.py::TestDatabaseConnection::test_execute_query
- SchemaGenerator.generate_schema() - Verified in test_database_management.py::TestSchemaGenerator::test_generate_schema
"""
```

**✅ Use the same method signatures as tests:**
```python
# ✅ Matches test signature
def test_execute_query(self):
    conn = DatabaseConnection(...)
    result = conn.execute_query("SELECT 1")
    assert result == [1]

# In example
conn = DatabaseConnection(config['database'])
result = conn.execute_query("SELECT * FROM users")  # Same signature
```

### 2. Example Testing

**✅ Include example validation:**
```python
def validate_example_results(results, expected_keys):
    """Validate example output."""
    missing_keys = []
    for key in expected_keys:
        if key not in results:
            missing_keys.append(key)

    if missing_keys:
        raise AssertionError(f"Missing expected results: {missing_keys}")

    return True

# In example
results = {
    'connections_created': len(manager.connections),
    'queries_executed': query_count,
    'cleanup_completed': True
}

validate_example_results(results, ['connections_created', 'queries_executed'])
```

### 3. Performance Testing Integration

**✅ Include performance measurements:**
```python
import time

def measure_performance(func, *args, **kwargs):
    """Measure function execution time."""
    start_time = time.perf_counter()
    result = func(*args, **kwargs)
    end_time = time.perf_counter()

    execution_time = end_time - start_time
    logger.info(f"{func.__name__} executed in {execution_time:.2f}s")

    return result, execution_time

# In example
(query_result, query_time) = measure_performance(
    db.execute_query,
    "SELECT * FROM large_table"
)

results['query_performance'] = {
    'execution_time': query_time,
    'rows_returned': len(query_result)
}
```

## Documentation Standards

### 1. README Structure

**✅ Follow standard README structure:**
```markdown
# {Module Name} Example

## Overview
Brief description of what the example demonstrates.

## Features Demonstrated
- Feature 1 with brief explanation
- Feature 2 with integration details
- Feature 3 with configuration options

## Configuration
### Required Settings
- `setting1`: Description and valid values
- `setting2`: Description and format

### Optional Settings
- `setting3`: Description with default value

## Usage
```bash
cd examples/{module_name}
python example_basic.py
```

## Output
Description of generated files and their contents.

## Tested Methods
- `method_name()` - Verified in `test_{module}.py::TestClass::test_method`
- `another_method()` - Verified in `test_{module}.py::TestClass::test_another`

## Dependencies
- Module dependencies
- External requirements
- System prerequisites
```

### 2. Code Documentation

**✅ Document complex logic:**
```python
def process_complex_workflow(config):
    """
    Process a complex multi-step workflow.

    This function orchestrates multiple modules to perform
    a complete data processing pipeline including:
    1. Data ingestion from multiple sources
    2. Validation and transformation
    3. Analysis and reporting
    4. Result persistence

    Args:
        config: Configuration dictionary containing:
            - sources: List of data source configurations
            - validation_rules: Data validation specifications
            - analysis_params: Analysis configuration
            - output_config: Result output settings

    Returns:
        dict: Processing results with metrics and status

    Raises:
        WorkflowError: If any step in the workflow fails
        ValidationError: If input data fails validation
    """
    # Implementation with detailed comments
    pass
```

### 3. Configuration Documentation

**✅ Document all configuration options:**
```yaml
# config.yaml with comprehensive comments
api:
  # API server configuration
  host: localhost                    # Server hostname or IP
  port: 8000                        # Server port (1000-9999)
  timeout: 30                       # Request timeout in seconds
  retry_count: 3                    # Number of retry attempts

database:
  # Database connection settings
  type: sqlite                      # Database type: sqlite, postgresql, mysql
  database: data/api.db             # Database file path or name
  connection_pool:                  # Connection pool configuration
    min_connections: 5              # Minimum pool size
    max_connections: 20             # Maximum pool size
    timeout: 30                     # Connection timeout
```

## Performance Optimization

### 1. Resource Management

**✅ Optimize memory usage:**
```python
def process_large_dataset_efficiently(data_path, batch_size=1000):
    """Process large datasets in batches to manage memory."""
    results = []

    with open(data_path, 'r') as file:
        batch = []
        for line in file:
            batch.append(process_line(line))

            if len(batch) >= batch_size:
                # Process batch
                batch_results = process_batch(batch)
                results.extend(batch_results)

                # Clear batch to free memory
                batch.clear()

        # Process remaining items
        if batch:
            batch_results = process_batch(batch)
            results.extend(batch_results)

    return results
```

**✅ Use streaming for large files:**
```python
def stream_process_log_file(log_path, pattern):
    """Process large log files without loading into memory."""
    matches = []

    with open(log_path, 'r') as file:
        for line_num, line in enumerate(file, 1):
            if pattern.search(line):
                matches.append({
                    'line_number': line_num,
                    'content': line.strip(),
                    'timestamp': extract_timestamp(line)
                })

    return matches
```

### 2. Caching Strategies

**✅ Implement result caching:**
```python
from functools import lru_cache
import hashlib

@lru_cache(maxsize=100)
def cached_expensive_operation(param1, param2):
    """Cache results of expensive operations."""
    # Expensive computation
    result = perform_expensive_calculation(param1, param2)
    return result

def get_cache_key(data):
    """Generate cache key for complex data."""
    key_data = json.dumps(data, sort_keys=True)
    return hashlib.md5(key_data.encode()).hexdigest()
```

### 3. Asynchronous Processing

**✅ Use async for I/O operations:**
```python
import asyncio
from typing import List, Dict, Any

async def process_api_requests_async(urls: List[str]) -> List[Dict[str, Any]]:
    """Process multiple API requests concurrently."""

    async def fetch_single(url):
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                return await response.json()

    # Execute all requests concurrently
    tasks = [fetch_single(url) for url in urls]
    results = await asyncio.gather(*tasks, return_exceptions=True)

    # Handle results and exceptions
    processed_results = []
    for i, result in enumerate(results):
        if isinstance(result, Exception):
            logger.error(f"Request {i} failed: {result}")
            processed_results.append({"error": str(result)})
        else:
            processed_results.append(result)

    return processed_results
```

## Security Considerations

### 1. Secure Configuration Handling

**✅ Never hardcode secrets:**
```python
# ❌ Bad: Hardcoded secrets
config = {
    "api_key": "sk-1234567890abcdef",
    "database_password": "secret123"
}

# ✅ Good: Environment variables
config = {
    "api_key": os.environ["API_KEY"],
    "database_password": os.environ["DB_PASSWORD"]
}
```

**✅ Validate input data:**
```python
def sanitize_user_input(user_data: dict) -> dict:
    """Sanitize and validate user input."""
    sanitized = {}

    # Validate and sanitize each field
    if 'username' in user_data:
        username = user_data['username'].strip()
        if not re.match(r'^[a-zA-Z0-9_]{3,20}$', username):
            raise ValueError("Invalid username format")
        sanitized['username'] = username

    if 'email' in user_data:
        email = user_data['email'].strip().lower()
        if not re.match(r'^[^@]+@[^@]+\.[^@]+$', email):
            raise ValueError("Invalid email format")
        sanitized['email'] = email

    return sanitized
```

### 2. Safe File Operations

**✅ Use secure file paths:**
```python
def safe_write_output(data, output_path):
    """Safely write output to file."""
    output_path = Path(output_path).resolve()

    # Ensure output directory exists and is writable
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Write to temporary file first, then rename
    temp_path = output_path.with_suffix('.tmp')
    with open(temp_path, 'w') as f:
        json.dump(data, f, indent=2)

    # Atomic rename
    temp_path.rename(output_path)
```

### 3. Error Message Security

**✅ Don't leak sensitive information in errors:**
```python
# ❌ Bad: Leaks database details
except DatabaseError as e:
    logger.error(f"Database error: {e}")
    raise

# ✅ Good: Generic error message
except DatabaseError as e:
    logger.error("Database operation failed", exc_info=True)
    raise RuntimeError("Database operation failed. Check logs for details.")
```

## Maintenance Guidelines

### 1. Regular Updates

**✅ Keep examples current:**
- Update to latest module APIs
- Refresh configuration examples
- Update dependency versions
- Test with new Python versions

**✅ Monitor for breaking changes:**
```python
# Check for deprecated methods
import warnings
warnings.simplefilter('always')

# Test imports
try:
    from codomyrmex.module import OldMethod
    warnings.warn("OldMethod is deprecated", DeprecationWarning)
except ImportError:
    pass
```

### 2. Code Review Checklist

**✅ Use this checklist for example reviews:**
- [ ] Example follows standard template
- [ ] Configuration files are valid YAML/JSON
- [ ] All imports work correctly
- [ ] Error handling is comprehensive
- [ ] Output files are generated correctly
- [ ] Documentation is complete and accurate
- [ ] Tested methods are properly referenced
- [ ] Performance is reasonable
- [ ] Security best practices followed
- [ ] No hardcoded secrets or paths

### 3. Version Compatibility

**✅ Test across Python versions:**
```bash
# Test with multiple Python versions
for version in 3.8 3.9 3.10 3.11; do
    echo "Testing Python $version"
    pyenv local $version
    python example_basic.py
done
```

**✅ Handle version-specific code:**
```python
import sys

if sys.version_info >= (3, 9):
    # Use Python 3.9+ features
    from typing import Annotated
else:
    # Fallback for older versions
    from typing_extensions import Annotated
```

### 4. Dependency Management

**✅ Keep dependencies minimal and current:**
```txt
# requirements.txt
codomyrmex>=1.0.0
pyyaml>=6.0
requests>=2.28.0
```

**✅ Test with different dependency versions:**
```python
# In CI/test script
test_versions = [
    ("pyyaml", ["5.4.1", "6.0"]),
    ("requests", ["2.25.0", "2.28.0"]),
]

for package, versions in test_versions:
    for version in versions:
        subprocess.run([
            "pip", "install", f"{package}=={version}"
        ])
        # Run tests
        run_example_tests()
```

## Code Quality Standards

### 1. Style Consistency

**✅ Follow PEP 8:**
```python
# Good naming
def get_user_by_id(user_id: int) -> User:
    """Get user by their unique identifier."""

# Good formatting
user_data = {
    'id': user.id,
    'name': user.name,
    'email': user.email,
    'created_at': user.created_at.isoformat()
}

# Good error handling
try:
    result = process_data(data)
except DataProcessingError as e:
    logger.error(f"Data processing failed: {e}")
    raise
except Exception as e:
    logger.error(f"Unexpected error: {e}")
    raise RuntimeError("Data processing failed") from e
```

### 2. Type Hints

**✅ Use comprehensive type hints:**
```python
from typing import Dict, List, Optional, Union, Any
from pathlib import Path

def process_configuration(
    config_path: Union[str, Path],
    overrides: Optional[Dict[str, Any]] = None,
    validate: bool = True
) -> Dict[str, Any]:
    """
    Process configuration with optional overrides.

    Args:
        config_path: Path to configuration file
        overrides: Optional configuration overrides
        validate: Whether to validate configuration

    Returns:
        Processed configuration dictionary

    Raises:
        FileNotFoundError: If config file doesn't exist
        ValueError: If configuration is invalid
    """
    pass
```

### 3. Logging Best Practices

**✅ Use structured logging:**
```python
import logging

logger = logging.getLogger(__name__)

def process_with_logging(data: dict) -> dict:
    """Process data with comprehensive logging."""

    logger.info("Starting data processing", extra={
        'data_size': len(data),
        'operation': 'process_data'
    })

    try:
        # Processing logic
        result = perform_processing(data)

        logger.info("Data processing completed successfully", extra={
            'result_size': len(result),
            'processing_time': time.time() - start_time
        })

        return result

    except Exception as e:
        logger.error("Data processing failed", extra={
            'error_type': type(e).__name__,
            'data_size': len(data)
        }, exc_info=True)
        raise
```

## Integration Patterns

### 1. Module Coordination

**✅ Use event-driven communication:**
```python
from codomyrmex.events import EventBus, EventEmitter

def coordinate_modules_with_events(config):
    """Coordinate multiple modules using events."""

    event_bus = EventBus()

    # Initialize modules
    db_manager = DatabaseManager()
    api_handler = APIHandler()
    monitor = SystemMonitor()

    # Subscribe to events
    event_bus.subscribe("data_processed", db_manager.save_results)
    event_bus.subscribe("api_request", monitor.log_request)
    event_bus.subscribe("error_occurred", monitor.alert_admin)

    # Process workflow
    emitter = EventEmitter(event_bus)

    try:
        # Emit events as workflow progresses
        emitter.emit("workflow_started", {"workflow_id": "data_pipeline"})

        data = api_handler.fetch_data()
        emitter.emit("data_received", {"data_size": len(data)})

        processed_data = process_data(data)
        emitter.emit("data_processed", {"result": processed_data})

        emitter.emit("workflow_completed", {"status": "success"})

    except Exception as e:
        emitter.emit("error_occurred", {"error": str(e)})
        raise
```

### 2. Configuration Sharing

**✅ Share configuration between modules:**
```python
def create_shared_config(base_config: dict) -> dict:
    """Create configuration shared across modules."""

    shared_config = {
        "logging": base_config.get("logging", {}),
        "performance": base_config.get("performance", {}),
        "security": base_config.get("security", {}),
    }

    # Module-specific configurations
    configs = {
        "database": {
            **shared_config,
            "connection": base_config["database"],
            "migrations": base_config.get("migrations", {}),
        },
        "api": {
            **shared_config,
            "server": base_config["api"],
            "authentication": base_config.get("auth", {}),
        },
        "monitoring": {
            **shared_config,
            "metrics": base_config.get("metrics", {}),
            "alerts": base_config.get("alerts", {}),
        }
    }

    return configs
```

---

**Remember**: Examples should demonstrate best practices, not just functionality. Each example is a learning opportunity for users to understand how to properly use Codomyrmex modules.

## Navigation Links

- **Parent**: [Project Overview](../README.md)
- **Module Index**: [All Agents](../../AGENTS.md)
- **Documentation**: [Reference Guides](../docs/README.md)
- **Home**: [Root README](../../../README.md)
