# Code Execution Sandbox Orchestrator

Thin orchestrator script providing CLI access to the `codomyrmex.code_execution_sandbox` module.

## Purpose

This orchestrator provides command-line interface for secure code execution in sandboxed Docker environments.

## Usage

```bash
# Execute code from file
python scripts/code_execution_sandbox/orchestrate.py execute --file script.py

# Execute inline code
python scripts/code_execution_sandbox/orchestrate.py execute --code "print('Hello, World!')" --language python

# Execute with custom timeout
python scripts/code_execution_sandbox/orchestrate.py execute --file script.js --language javascript --timeout 30
```

## Commands

- `execute` - Execute code in sandboxed environment

## Related Documentation

- **[Module README](../../src/codomyrmex/code_execution_sandbox/README.md)**: Complete module documentation
- **[API Specification](../../src/codomyrmex/code_execution_sandbox/API_SPECIFICATION.md)**: Detailed API reference
- **[MCP Tools](../../src/codomyrmex/code_execution_sandbox/MCP_TOOL_SPECIFICATION.md)**: AI integration tools
- **[Usage Examples](../../src/codomyrmex/code_execution_sandbox/USAGE_EXAMPLES.md)**: Practical examples
- **[CLI Reference](../../docs/reference/cli.md)**: Main CLI documentation

## Integration

This orchestrator calls functions from:
- `codomyrmex.code_execution_sandbox.execute_code`

See `codomyrmex.cli.py` for main CLI integration.

## Requirements

- Docker must be installed and running
- Appropriate language runtime images must be available

