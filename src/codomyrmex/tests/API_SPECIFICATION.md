# Tests Module API Specification

**Version**: v0.1.0 | **Status**: Stable | **Last Updated**: January 2026

## 1. Overview
The `tests` module provides shared testing infrastructure, fixtures, and utility functions used across the test suite. This document defines the interface for test helpers and common fixtures.

## 2. Shared Fixtures (`conftest.py`)

### 2.1 Project Setup
- **`temp_project`**: Creates a temporary project directory with a valid structure.
- **`mock_config`**: Provides a default `Config` object for testing without a disk file.

### 2.2 External Mocks
- **`mock_db`**: Simulates a database connection session.
- **`mock_llm`**: Simulates LLM responses for deterministic agent testing.

## 3. Test Helpers

### 3.1 Assertions
- `assert_valid_schema(data, schema)`: Helper to validate JSON schema compliance.
- `assert_execution_time(func, max_ms)`: Helper to verify performance constraints.

### 3.2 Factories
- `make_dummy_agent(name="test")`: Factory for creating minimal agent instances.
- `make_sample_dataset(rows=10)`: Factory for generating test dataframes.

## 4. Usage Example

```python
# specific_test.py
def test_agent_config(mock_config, make_dummy_agent):
    agent = make_dummy_agent()
    agent.configure(mock_config)
    assert agent.is_configured
```
