# Validation Module API Specification

**Version**: v0.1.0 | **Status**: Stable | **Last Updated**: January 2026

## 1. Overview
The `validation` module provides a unified framework for validating data structures against schemas, supporting JSON Schema and Pydantic.

## 2. Core Components

### 2.1 Functions
- **`validate(data: Any, schema: Any, validator_type: str) -> ValidationResult`**: Main validation entry point.
- **`is_valid(...) -> bool`**: Boolean check convenience function.
- **`get_errors(...) -> list[ValidationError]`**: Retrieve error details.

### 2.2 Classes
- **`Validator`**: Validation engine.
- **`ValidationManager`**: System-wide validation configuration.
- **`ValidationResult`**: Outcome of a validation operation.
- **`ValidationError`**: Detailed error information.

## 3. Usage Example

```python
from codomyrmex.validation import is_valid

schema = {"type": "integer"}
data = 42

if is_valid(data, schema):
    print("Valid integer!")
```
