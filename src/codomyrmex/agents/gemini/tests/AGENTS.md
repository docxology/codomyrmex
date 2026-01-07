# Codomyrmex Agents — src/codomyrmex/agents/gemini/tests

## Signposting
- **Parent**: [gemini](../AGENTS.md)
- **Self**: [Gemini Tests](AGENTS.md)

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: December 2025

## Purpose

Test suite for Gemini agent integration module. Includes unit tests for GeminiClient and integration tests for GeminiIntegrationAdapter.

**Tests use real implementations only.** When Gemini CLI is not available, tests are skipped rather than using mocks. All data processing and conversion logic is tested with real data structures.

## Test Files

- `test_gemini_client.py` - Unit tests for GeminiClient
- `test_gemini_integration.py` - Integration tests for GeminiIntegrationAdapter and orchestration

## Test Coverage

### GeminiClient Tests
- Initialization and configuration
- Capability declarations
- Command execution (success and failure cases)
- Streaming output
- Slash command execution
- Chat session management (save, resume, list)
- Help information retrieval
- Timeout handling
- File operations
- Configuration override

### Integration Adapter Tests
- Adapter initialization
- AI code editing adaptation
- LLM module adaptation
- Code execution adaptation
- Error handling

### Orchestration Tests
- Multi-agent coordination
- Fallback mechanisms

## Running Tests

```bash
# Run all Gemini tests
pytest src/codomyrmex/agents/gemini/tests/

# Run specific test file
pytest src/codomyrmex/agents/gemini/tests/test_gemini_client.py

# Run with coverage
pytest src/codomyrmex/agents/gemini/tests/ --cov=codomyrmex.agents.gemini
```

## Test Approach

### Real Implementations Only
- **No Mock Methods**: All tests use real implementations. No `unittest.mock`, `MagicMock`, or `@patch` decorators.
- **Real CLI Calls**: Tests use real Gemini CLI when available, or skip when not installed.
- **Real Error Handling**: Error conditions tested with real failures, not mocked failures.
- **Test Adapters**: Use test adapters that implement BaseAgent interface, not mocks.

### Skip Conditions
- Tests requiring Gemini CLI are marked with `@pytest.mark.skipif(not GEMINI_AVAILABLE)`
- Tests requiring authentication may skip if authentication fails
- Tests use real subprocess calls when CLI tools are available

### Test Structure
- **Unit Tests**: Test configuration, initialization, data structures, and command building logic
- **Integration Tests**: Require real CLI tools installed and test real subprocess execution
- **Error Tests**: Test real error conditions (invalid commands, timeouts, etc.)

## Navigation Links

- **Parent Module**: [gemini](../AGENTS.md)

