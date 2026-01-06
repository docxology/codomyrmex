# Ollama Integration Test Suite Documentation

## Overview

This document provides comprehensive documentation for the Ollama integration test suite. The test suite ensures all Ollama integration methods work correctly using real Ollama API calls (no mocks).

## Test Structure and Organization

### Test Files

1. **`test_ollama_integration.py`** - Original unit tests (maintained for compatibility)
2. **`test_ollama_integration_comprehensive.py`** - Comprehensive test suite with full coverage
3. **`ollama_test_helpers.py`** - Reusable test utilities and helpers

### Test Scripts (in `scripts/llm/ollama/`)

1. **`test_usage_patterns.py`** - Real-world usage pattern demonstrations
2. **`test_error_scenarios.py`** - Error handling and edge case tests
3. **`test_configuration_patterns.py`** - Configuration management tests
4. **`verify_integration.py`** - Integration verification script
5. **`test_all_parameters_rnj.py`** - Parameter-specific tests

## Test Categories

### Category A: Initialization Patterns

**Purpose**: Verify all ways to initialize Ollama components work correctly

**Tests**:
- `test_http_api_initialization` - HTTP API initialization
- `test_cli_fallback_initialization` - CLI fallback initialization
- `test_custom_host_port_configuration` - Custom connection parameters
- `test_auto_start_server_behavior` - Auto-start server functionality
- `test_configuration_loading_from_files` - File-based configuration loading

**When to use**: Testing different initialization scenarios

### Category B: Model Management

**Purpose**: Verify all model management operations work correctly

**Tests**:
- `test_model_listing_with_caching` - Model list caching
- `test_model_listing_with_force_refresh` - Force refresh functionality
- `test_model_availability_checking` - Availability checking
- `test_model_info_retrieval` - Model information retrieval
- `test_model_name_variations` - Name format handling

**When to use**: Testing model discovery and management

### Category C: Execution Methods

**Purpose**: Verify all model execution methods and patterns work correctly

**Tests**:
- `test_direct_ollama_manager_run` - Direct manager execution
- `test_model_runner_with_options` - ModelRunner execution
- `test_execution_with_presets` - Preset-based execution
- `test_execution_with_json_format` - JSON format output
- `test_execution_with_system_prompt` - System prompt usage
- `test_execution_with_context_window` - Context window settings
- `test_batch_execution_multiple_prompts` - Batch processing

**When to use**: Testing execution functionality

### Category D: Configuration Management

**Purpose**: Verify all configuration management operations work correctly

**Tests**:
- `test_loading_default_configuration` - Default config loading
- `test_saving_model_specific_configuration` - Model-specific configs
- `test_configuration_validation` - Configuration validation
- `test_preset_retrieval_and_usage` - Preset functionality

**When to use**: Testing configuration system

### Category E: Output Management

**Purpose**: Verify all output management operations work correctly

**Tests**:
- `test_output_saving_with_default_directory` - Default directory saving
- `test_output_saving_with_custom_directory` - Custom directory saving
- `test_output_statistics_retrieval` - Statistics functionality

**When to use**: Testing output persistence

### Category F: Error Handling

**Purpose**: Verify error handling works correctly for various failure scenarios

**Tests**:
- `test_model_not_found_error` - Model not found handling
- `test_invalid_parameter_values` - Invalid parameter handling

**When to use**: Testing robustness

### Category G: Integration Patterns

**Purpose**: Verify integration with other Codomyrmex components works correctly

**Tests**:
- `test_logging_integration` - Logging integration
- `test_resource_cleanup` - Resource cleanup

**When to use**: Testing ecosystem integration

## Running Tests

### Run All Unit Tests

```bash
# Run comprehensive test suite
uv run pytest src/codomyrmex/tests/unit/test_ollama_integration_comprehensive.py -v

# Run original test suite
uv run pytest src/codomyrmex/tests/unit/test_ollama_integration.py -v

# Run all Ollama tests
uv run pytest src/codomyrmex/tests/unit/test_ollama*.py -v
```

### Run Specific Test Categories

```bash
# Run only initialization tests
uv run pytest src/codomyrmex/tests/unit/test_ollama_integration_comprehensive.py::TestInitializationPatterns -v

# Run only execution tests
uv run pytest src/codomyrmex/tests/unit/test_ollama_integration_comprehensive.py::TestExecutionMethods -v
```

### Run Test Scripts

```bash
# Usage patterns
uv run python scripts/llm/ollama/test_usage_patterns.py

# Error scenarios
uv run python scripts/llm/ollama/test_error_scenarios.py

# Configuration patterns
uv run python scripts/llm/ollama/test_configuration_patterns.py

# Full verification
uv run python scripts/llm/ollama/verify_integration.py
```

## Test Documentation Standards

Each test includes:

1. **Purpose**: What the test verifies
2. **Context**: When/why this test is important
3. **Setup**: What conditions are required
4. **Execution**: What actions are performed
5. **Assertions**: What outcomes are expected
6. **Cleanup**: What resources are released

### Example Test Documentation

```python
def test_model_execution(self):
    """
    Test basic model execution.
    
    Purpose: Verify model execution returns valid results
    Context: Execution is the primary use case
    Setup: Available model and prompt
    Execution: Run model with prompt
    Assertions: Result is valid, response is non-empty
    Cleanup: No persistent resources
    """
    # Test implementation
```

## Test Utilities

### OllamaTestFixture

Provides initialized managers and test environment:

```python
fixture = OllamaTestFixture(use_http_api=True)
model_name = fixture.get_available_model()
result = fixture.runner.run_with_options(model_name, prompt, options)
```

### TestDataGenerator

Generates test data:

```python
prompts = TestDataGenerator.simple_prompts()
options_variations = TestDataGenerator.execution_options_variations()
```

### AssertionHelpers

Domain-specific assertions:

```python
AssertionHelpers.assert_model_execution_success(result, model_name)
AssertionHelpers.assert_valid_execution_options(options)
```

### ModelAvailabilityChecker

Handles model availability:

```python
checker = ModelAvailabilityChecker(manager)
model = checker.find_suitable_model(requirements=["small", "fast"])
```

## Adding New Tests

### Step 1: Choose Test Category

Determine which category your test belongs to (A-G).

### Step 2: Write Test Method

Follow the documentation standard:

```python
def test_new_feature(self):
    """
    Test description.
    
    Purpose: What this test verifies
    Context: When/why this is important
    Setup: Required conditions
    Execution: Actions performed
    Assertions: Expected outcomes
    Cleanup: Resources released
    """
    # Use fixture for setup
    fixture = OllamaTestFixture()
    
    # Get available model
    model_name = fixture.get_available_model()
    if not model_name:
        self.skipTest("No model available")
    
    # Perform test
    result = fixture.runner.run_with_options(...)
    
    # Assert results
    AssertionHelpers.assert_model_execution_success(result, model_name)
    
    # Cleanup
    fixture.cleanup()
```

### Step 3: Add to Appropriate Test Class

Add your test to the appropriate test class in `test_ollama_integration_comprehensive.py`.

### Step 4: Run and Verify

```bash
uv run pytest src/codomyrmex/tests/unit/test_ollama_integration_comprehensive.py::TestCategory::test_new_feature -v
```

## Test Data Requirements

### Models

Tests use available models from the Ollama installation. Tests will:
- Use the smallest available model for speed
- Skip if no models are available
- Attempt to pull models if needed (with timeout)

### Network

Tests require:
- Ollama server running (or auto-start capability)
- Network access to Ollama API (localhost:11434)

### Storage

Tests create temporary directories for:
- Output files
- Configuration files
- Test artifacts

All temporary resources are cleaned up automatically.

## Expected Behaviors

### Success Criteria

- All tests pass with real Ollama API calls
- No mocks are used
- Resources are cleaned up
- Error messages are clear and helpful

### Failure Handling

- Tests skip gracefully when Ollama is unavailable
- Tests skip gracefully when no models are available
- Error scenarios are tested explicitly
- Failures provide clear diagnostic information

## Troubleshooting

### Tests Fail with "No models available"

1. Ensure Ollama is installed and running
2. Pull at least one model: `ollama pull gemma3:4b`
3. Verify models: `ollama list`

### Tests Fail with Connection Errors

1. Check Ollama server is running: `ollama list`
2. Verify server is on default port (11434)
3. Check firewall settings

### Tests Are Slow

1. Use smaller models for testing
2. Reduce `max_tokens` in test options
3. Run specific test categories instead of full suite

## Best Practices

1. **Always use real API calls** - No mocks
2. **Document tests clearly** - Include purpose and context
3. **Handle missing resources gracefully** - Skip tests when needed
4. **Clean up resources** - Use fixtures for automatic cleanup
5. **Use assertion helpers** - For clearer test failures
6. **Test error scenarios** - Not just success cases

## Related Documentation

- [Ollama Integration README](../../../codomyrmex/llm/ollama/README.md)
- [API Specification](../../../codomyrmex/llm/ollama/API_SPECIFICATION.md)
- [Model Configurations](../../../codomyrmex/llm/ollama/MODEL_CONFIGS.md)
- [Verification Status](../../../codomyrmex/llm/ollama/VERIFICATION.md)


## Navigation Links

- **Parent**: [Project Overview](../README.md)
- **Module Index**: [All Agents](../../AGENTS.md)
- **Documentation**: [Reference Guides](../../../../docs/README.md)
- **Home**: [Root README](../../../README.md)
