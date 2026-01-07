# Basic Template Example

**Template Type**: Basic Module Example
**Purpose**: Standard template for creating simple module demonstration examples
**Complexity**: Low to Medium

## Overview

This template provides a comprehensive structure for creating examples that demonstrate a single Codomyrmex module's functionality. It includes proper error handling, logging, performance monitoring, and result validation.

## Template Features

### Core Structure
- **Standard Template**: Follows all Codomyrmex example conventions
- **Class-Based Design**: Organized example logic in a dedicated class
- **Comprehensive Workflow**: Setup → Core Demo → Error Handling → Cleanup
- **Result Validation**: Built-in result validation and reporting

### Included Functionality
- **Configuration Loading**: YAML/JSON config with environment variable support
- **Logging Integration**: Centralized logging with configurable levels
- **Error Handling**: Comprehensive exception handling with recovery
- **Performance Monitoring**: Execution time and resource usage tracking
- **Resource Management**: Proper setup and cleanup of resources
- **Result Validation**: Automated validation of example outputs

### Demonstration Sections
1. **Setup Phase**: Environment preparation and validation
2. **Core Functionality**: Main module feature demonstrations
3. **Error Handling**: Fault tolerance and recovery patterns
4. **Performance Metrics**: Execution statistics and monitoring
5. **Cleanup Phase**: Resource cleanup and finalization

## Usage Instructions

### 1. Copy Template Files

```bash
# Copy template files to new module directory
cp scripts/_templates/basic_template.py scripts/your_module/examples/example_basic.py
cp scripts/_templates/basic_template_config.yaml scripts/your_module/examples/config.yaml
cp scripts/_templates/basic_template_README.md scripts/your_module/examples/README.md
```

### 2. Customize Module-Specific Code

**Update imports:**
```python
# Replace template imports
from codomyrmex.{module} import (
    {ActualFunction},
    {AnotherActualFunction}
)
```

**Update class name:**
```python
# Change class name
class {YourModuleName}Example:
```

**Implement core methods:**
```python
def _run_basic_example(self) -> Dict[str, Any]:
    # Replace with actual module functionality
    result = {module}.basic_function(self.config)
    return {"status": "success", "data": result}

def _run_advanced_example(self) -> Dict[str, Any]:
    # Replace with advanced features
    result = {module}.advanced_function(self.config)
    return {"status": "success", "data": result}

def _run_integration_example(self) -> Dict[str, Any]:
    # Replace with integration scenario
    result = {module}.integration_scenario(self.config)
    return {"status": "success", "data": result}
```

### 3. Update Configuration

**Customize config.yaml:**
```yaml
module:
  name: "your_module"           # Change module name
  debug: true                   # Module-specific settings
  max_operations: 10           # Adjust parameters

# Add module-specific configuration sections
your_module:
  specific_setting: value
  another_setting: value
```

### 4. Update Documentation

**Customize README.md:**
```markdown
# Your Module Example

## Overview
Brief description of what your module does.

## Features Demonstrated
- Feature 1 with brief explanation
- Feature 2 with integration details
- Feature 3 with configuration options

## Configuration
### Required Settings
- `setting1`: Description and valid values
- `setting2`: Description and format

## Tested Methods
- `method_name()` - Verified in `test_your_module.py::TestClass::test_method`
```

### 5. Update Template Placeholders

**Global search and replace:**
- `{Module Name}` → `Your Module Name`
- `{module}` → `your_module`
- `{TestedFunction}` → `actual_function_name`
- `{ModuleName}` → `YourModuleName`

## Configuration Options

### Core Settings

| Setting | Type | Default | Description |
|---------|------|---------|-------------|
| `module.name` | string | `"basic_template"` | Module identifier |
| `module.debug` | boolean | `true` | Enable debug mode |
| `module.max_operations` | integer | `10` | Maximum operations to perform |
| `module.timeout` | integer | `30` | Operation timeout in seconds |

### Performance Settings

| Setting | Type | Default | Description |
|---------|------|---------|-------------|
| `performance.enable_monitoring` | boolean | `true` | Enable performance monitoring |
| `performance.memory_limit` | string | `"512MB"` | Memory usage limit |
| `performance.cpu_limit` | integer | `80` | CPU usage limit (percentage) |

### Error Handling Settings

| Setting | Type | Default | Description |
|---------|------|---------|-------------|
| `error_handling.fail_fast` | boolean | `false` | Stop on first error |
| `error_handling.continue_on_error` | boolean | `true` | Continue after errors |
| `error_handling.log_errors` | boolean | `true` | Log all errors |

## Output Format

The template generates a comprehensive JSON result file:

```json
{
  "status": "completed",
  "module": "your_module",
  "core_functionality": {
    "basic_example": {
      "operation": "basic_functionality",
      "status": "success",
      "data": "..."
    },
    "advanced_example": {
      "operation": "advanced_functionality",
      "status": "success",
      "data": "..."
    },
    "integration_example": {
      "operation": "integration_scenario",
      "status": "success",
      "data": "..."
    }
  },
  "error_handling": {
    "invalid_input_handled": true,
    "network_error_handled": true,
    "permission_error_handled": true
  },
  "performance": {
    "total_execution_time": 1.234,
    "operations_per_second": 8.1,
    "error_rate": 0.0,
    "memory_usage": "N/A",
    "cpu_usage": "N/A"
  },
  "cleanup_success": true,
  "execution_summary": {
    "total_operations": 3,
    "errors_encountered": 0,
    "success_rate": 1.0
  }
}
```

## Extension Points

### Adding New Demonstration Methods

```python
def demonstrate_custom_feature(self) -> Dict[str, Any]:
    """Demonstrate a custom feature."""
    print_section("Custom Feature Demonstration")

    try:
        result = self._run_custom_example()
        print_success("Custom feature demonstrated")
        return {"custom_feature": result}
    except Exception as e:
        print_error(f"Custom feature failed: {e}")
        return {"error": str(e)}

def _run_custom_example(self) -> Dict[str, Any]:
    """Implement custom example logic."""
    # Your custom implementation
    return {"status": "success", "custom_data": "value"}
```

### Adding Performance Monitoring

```python
import psutil
from functools import wraps

def monitor_performance(func):
    """Decorator to monitor function performance."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_memory = psutil.Process().memory_info().rss
        start_time = time.time()

        result = func(*args, **kwargs)

        end_time = time.time()
        end_memory = psutil.Process().memory_info().rss

        return {
            **result,
            "performance": {
                "execution_time": end_time - start_time,
                "memory_used": end_memory - start_memory
            }
        }

    return wrapper

@monitor_performance
def _run_basic_example(self) -> Dict[str, Any]:
    # Your implementation with automatic performance monitoring
    pass
```

### Adding Resource Management

```python
from contextlib import contextmanager

@contextmanager
def managed_resource(self, resource_type: str):
    """Context manager for resource management."""
    resource = self._create_resource(resource_type)
    try:
        yield resource
    finally:
        self._cleanup_resource(resource)

def _create_resource(self, resource_type: str):
    """Create a resource."""
    # Implementation for resource creation
    pass

def _cleanup_resource(self, resource):
    """Clean up a resource."""
    # Implementation for resource cleanup
    pass
```

## Best Practices for Using This Template

### 1. Keep It Simple
- Focus on demonstrating core module functionality
- Avoid overly complex integration scenarios
- Use clear, descriptive variable names

### 2. Comprehensive Error Handling
- Handle all expected error conditions
- Provide meaningful error messages
- Log errors with appropriate levels

### 3. Performance Considerations
- Monitor execution time for long-running operations
- Use appropriate batch sizes for data processing
- Clean up resources promptly

### 4. Documentation
- Update all docstrings with actual functionality
- Document configuration options clearly
- Reference actual tested methods from unit tests

### 5. Testing
- Test with various configuration options
- Verify error handling works correctly
- Check that outputs are generated correctly

## Common Customization Patterns

### Database Module Example

```python
def _run_basic_example(self) -> Dict[str, Any]:
    """Basic database operations."""
    db_config = self.config.get('database', {})

    # Connect to database
    connection = DatabaseConnection(db_config)

    # Execute queries
    users = connection.execute_query("SELECT * FROM users")

    return {
        "operation": "database_query",
        "status": "success",
        "records_found": len(users)
    }
```

### API Module Example

```python
def _run_basic_example(self) -> Dict[str, Any]:
    """Basic API operations."""
    api_config = self.config.get('api', {})

    # Create API client
    client = APIClient(api_config)

    # Make API call
    response = client.get("/users")

    return {
        "operation": "api_call",
        "status": "success",
        "response_code": response.status_code,
        "data_size": len(response.json())
    }
```

### File Processing Example

```python
def _run_basic_example(self) -> Dict[str, Any]:
    """Basic file processing operations."""
    fs_config = self.config.get('filesystem', {})

    # Process files
    input_dir = Path(fs_config.get('input_dir', 'input'))
    processed_count = 0

    for file_path in input_dir.glob("*.txt"):
        self._process_file(file_path)
        processed_count += 1

    return {
        "operation": "file_processing",
        "status": "success",
        "files_processed": processed_count
    }
```

## Troubleshooting Template Usage

### Import Errors
```
Error: cannot import name 'SomeFunction'
```
**Solution**: Check that the module is properly installed and the function exists in the current version.

### Configuration Errors
```
Error: Missing required config field: api.key
```
**Solution**: Add the missing field to your config.yaml or set the environment variable.

### Permission Errors
```
Error: [Errno 13] Permission denied: 'output/'
```
**Solution**: Ensure the output directory exists and is writable:
```bash
mkdir -p output logs
chmod 755 output logs
```

### Performance Issues
```
Warning: Operation took longer than expected
```
**Solution**: Check system resources and adjust batch sizes or timeouts in configuration.

## Related Templates

- **Async Template** (`async_template.py`): For examples with async/await patterns
- **Integration Template** (`integration_template.py`): For multi-module integration examples
- **Advanced Template** (`advanced_template.py`): For complex, feature-rich examples

## Contributing Improvements

To improve this template:

1. **Add New Features**: Suggest additional demonstration patterns
2. **Improve Error Handling**: Enhance error recovery mechanisms
3. **Add Performance Features**: Include more detailed monitoring
4. **Update Documentation**: Keep examples current with module changes
5. **Add Testing**: Include more comprehensive validation

---

**Status**: Active Template
**Last Updated**: December 2025
**Compatibility**: Codomyrmex v1.0+
