# Personal AI Infrastructure - Agent Scripts Context

**Module**: scripts/agents  
**Version**: v0.2.0  
**Status**: Active

## Context

Utility scripts for testing and demonstrating the Codomyrmex agent ecosystem.

## AI Strategy

As an AI agent working with these scripts:

### Core Principles

1. **Graceful Degradation**: Always handle missing API keys gracefully - return 0
2. **Test Mode Awareness**: Check `CODOMYRMEX_TEST_MODE=1` to skip intensive tests
3. **Consistent Output**: Use `cli_helpers` for formatted success/error/info messages
4. **Timeout Protection**: Wrap long operations with subprocess timeouts

### Script Execution Pattern

```python
# Standard pattern for agent scripts
try:
    client = ClaudeClient()
except AgentConfigurationError as e:
    print_warning(f"Not configured: {e}")
    return 0  # Exit gracefully

if not client.test_connection():
    print_warning("Connection test failed")
    return 0
```

### Claude Code Integration

When using Claude Code methods:

```python
# File operations (no API needed for some)
result = client.scan_directory("/path")
diff = client.generate_diff(original, modified)

# API-dependent operations
if client.test_connection():
    result = client.review_code(code)
    explanation = client.explain_code(code)
    tests = client.suggest_tests(code)
```

## Key Files

| File | Purpose |
|------|---------|
| `agent_status.py` | Health checks, configuration discovery |
| `run_all_agents.py` | Orchestrate all examples |
| `claude_code_demo.py` | Claude Code method demonstrations |

## Future Considerations

1. **Parallel Execution**: Run examples concurrently for faster validation
2. **Report Generation**: Output JSON/HTML reports of test results
3. **CI Integration**: GitHub Actions workflow for automated testing
