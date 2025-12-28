# testing/fixtures - Test Data and Fixtures

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: December 2025

## Purpose

This directory contains test fixtures, data factories, and mock data generation utilities for the Codomyrmex testing suite. It provides realistic test data and controlled environments for comprehensive testing.

## Directory Structure

### Data Generation
- `real_data_factory.py` - Factory for generating realistic test data

## Function Signatures

### Test Data Generation Functions

```python
def create_valid_python_code() -> str
```

Generate valid Python code for testing purposes.

**Returns:** `str` - Valid Python code string

```python
def calculate_fibonacci(n)
```

Calculate the nth Fibonacci number (test function).

**Parameters:**
- `n` - Fibonacci sequence position

**Returns:** Fibonacci number

```python
def create_invalid_python_code(error_type: str) -> str
```

Generate Python code with specific types of errors for testing.

**Parameters:**
- `error_type` (str): Type of error to introduce ("syntax", "name", "indentation", etc.)

**Returns:** `str` - Python code with intentional errors

```python
def create_sample_config() -> Dict[str, Any]
```

Create a sample configuration dictionary for testing.

**Returns:** `Dict[str, Any]` - Sample configuration data

```python
def create_sample_workflow_config() -> Dict[str, Any]
```

Create a sample workflow configuration for testing.

**Returns:** `Dict[str, Any]` - Sample workflow configuration

### Problematic Code Functions

```python
def broken_function()
```

Function with intentional bugs for testing error handling.

**Returns:** None

```python
def problematic_function()
```

Function with issues for testing static analysis.

**Returns:** None

```python
def function_with_missing_imports()
```

Function that references undefined imports for testing.

**Returns:** None

```python
def type_mismatch()
```

Function with type mismatches for testing.

**Returns:** None

```python
def bad_indentation()
```

Function with indentation errors for testing.

**Returns:** None

### Core Test Functions

```python
def core_function()
```

Core functionality for testing.

**Returns:** None

```python
def helper_function()
```

Helper function for testing.

**Returns:** None

```python
def test_core_function()
```

Test function for the core functionality.

**Returns:** None

### Additional Error Functions

```python
def bad_function()
```

Intentionally broken function for testing.

**Returns:** None

```python
def syntax_error()
```

Function with syntax errors for testing.

**Returns:** None

```python
def name_error()
```

Function with name errors for testing.

**Returns:** None

## Agent Coordination

### Data Generation Agents

**DataFactory**
- **Purpose**: Generates realistic test data for various testing scenarios
- **Inputs**: Data schemas, generation parameters, randomization seeds
- **Outputs**: Structured test data, mock objects, sample datasets
- **Key Functions**:
  - `create_valid_python_code() -> str` - Generate valid Python code
  - `create_invalid_python_code(error_type: str) -> str` - Generate code with specific errors
  - `create_sample_config() -> Dict[str, Any]` - Create sample configurations
  - `create_sample_workflow_config() -> Dict[str, Any]` - Create workflow configurations

## Operating Contracts

### Data Generation Rules
1. **Realistic Data**: Generated data should be representative of real-world scenarios
2. **Deterministic Seeds**: Use seeds for reproducible test results
3. **Schema Compliance**: Generated data should conform to defined schemas
4. **Performance Considerations**: Data generation should be efficient for testing

### Agent Communication
1. **Factory Patterns**: Use factory patterns for consistent data generation
2. **Parameter Validation**: Validate input parameters for data generation
3. **Error Handling**: Handle edge cases and invalid parameters gracefully

## Navigation

- **Testing Root**: [../README.md](../README.md) - Testing suite documentation
- **Testing Agents**: [../AGENTS.md](../AGENTS.md) - Test coordination
- **Integration Tests**: [../integration/AGENTS.md](../integration/AGENTS.md) - Integration testing

## Related Documentation

- **[AGENTS Root](../../AGENTS.md)** - Repository-level agent coordination
- **[Testing Agents](../AGENTS.md)** - Test suite coordination