# Code Generation Context

## Project Environment

### Runtime Information
- **Python Version**: 3.10+ (specify exact version if known)
- **Operating System**: Cross-platform (Linux/Windows/macOS)
- **Execution Environment**: [CLI/web application/desktop app/etc.]

### Dependencies and Libraries
- **Standard Library**: All standard library modules available
- **Third-party Packages**: [List specific packages if required]
- **Framework**: [Django/Flask/FastAPI/etc. if applicable]

## Existing Codebase Structure

### Import Patterns
```python
# Common import structure used in this project
from typing import List, Dict, Optional, Any
from dataclasses import dataclass
from pathlib import Path
import logging

# Project-specific imports
from codomyrmex.logging_monitoring import get_logger
from codomyrmex.config_management import load_config
```

### Error Handling Patterns
```python
# Standard error handling approach
try:
    result = perform_operation(data)
except ValueError as e:
    logger.error(f"Invalid input: {e}")
    raise
except Exception as e:
    logger.error(f"Unexpected error: {e}")
    raise RuntimeError("Operation failed") from e
```

### Logging Patterns
```python
# Standard logging usage
logger = get_logger(__name__)

logger.debug("Detailed debugging information")
logger.info("General information about operation")
logger.warning("Warning about potential issues")
logger.error("Error conditions")
```

## Code Style and Conventions

### Naming Conventions
- **Functions**: `snake_case` (e.g., `process_data`, `validate_input`)
- **Classes**: `PascalCase` (e.g., `DataProcessor`, `ConfigManager`)
- **Constants**: `UPPER_CASE` (e.g., `MAX_RETRIES`, `DEFAULT_TIMEOUT`)
- **Private**: Prefix with underscore (e.g., `_internal_method`)

### Documentation Standards
```python
def process_data(data: List[Dict[str, Any]], config: Optional[Dict] = None) -> List[Dict]:
    """
    Process input data according to configuration.

    Args:
        data: List of dictionaries containing data to process
        config: Optional configuration dictionary for processing rules

    Returns:
        List of processed data dictionaries

    Raises:
        ValueError: If data format is invalid
        RuntimeError: If processing fails unexpectedly

    Example:
        >>> data = [{"value": 10}, {"value": 20}]
        >>> result = process_data(data)
        [{"value": 10, "processed": True}, {"value": 20, "processed": True}]
    """
```

## Related Functions and Classes

### Utility Functions
```python
def validate_input(data: Any) -> bool:
    """Validate input data structure and content."""
    pass

def sanitize_string(input_str: str) -> str:
    """Sanitize string input for security."""
    pass
```

### Data Structures
```python
@dataclass
class ProcessingResult:
    """Result of data processing operation."""
    success: bool
    data: Optional[List[Dict]] = None
    errors: Optional[List[str]] = None
    metadata: Optional[Dict] = None
```

### Configuration Patterns
```python
# Configuration loading and validation
config_schema = {
    "input_path": str,
    "output_path": str,
    "max_workers": int,
    "timeout": int
}

def load_and_validate_config(config_path: Path) -> Dict:
    """Load and validate configuration from file."""
    pass
```

## Testing Patterns

### Unit Test Structure
```python
import pytest
from unittest.mock import Mock, patch

class TestDataProcessor:
    def test_process_valid_data(self):
        """Test processing of valid input data."""
        pass

    def test_process_invalid_data_raises_error(self):
        """Test that invalid data raises appropriate errors."""
        pass

    def test_process_empty_data_returns_empty(self):
        """Test handling of empty input data."""
        pass
```

## Integration Points

### File System Operations
- Use `pathlib.Path` for all file operations
- Handle permissions and encoding properly
- Use temporary directories for testing

### Configuration Management
- Load configuration from JSON/YAML files
- Validate configuration against schema
- Provide sensible defaults

### Logging Integration
- Use structured logging with context
- Include relevant metadata in log messages
- Support different log levels appropriately

## Performance Considerations

### Efficiency Guidelines
- Prefer list/dict comprehensions over explicit loops
- Use generators for large data processing
- Implement caching where appropriate
- Avoid unnecessary object creation

### Memory Management
- Process large files in chunks
- Clean up resources in finally blocks
- Use context managers for resource handling
- Monitor memory usage in long-running processes

## Security Requirements

### Input Validation
- Validate all external inputs
- Sanitize file paths and URLs
- Check data type and range constraints
- Handle encoding properly

### Safe Execution
- Use subprocess with restricted permissions
- Validate shell commands before execution
- Limit resource usage (CPU, memory, time)
- Log security-relevant operations