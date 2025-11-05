# Model Context Protocol Orchestrator

Thin orchestrator script providing CLI access to the `codomyrmex.model_context_protocol` module.

## Purpose

This orchestrator provides command-line interface for Model Context Protocol (MCP) operations, which serves as the foundation for all AI-enhanced modules in Codomyrmex.

## Usage

```bash
# Show module information
python scripts/model_context_protocol/orchestrate.py info

# List available MCP tools
python scripts/model_context_protocol/orchestrate.py list-tools
```

## Commands

- `info` - Show module information
- `list-tools` - List available MCP tools

## Related Documentation

- **[Module README](../../src/codomyrmex/model_context_protocol/README.md)**: Complete module documentation
- **[API Specification](../../src/codomyrmex/model_context_protocol/API_SPECIFICATION.md)**: Detailed API reference
- **[Usage Examples](../../src/codomyrmex/model_context_protocol/USAGE_EXAMPLES.md)**: Practical examples
- **[CLI Reference](../../docs/reference/cli.md)**: Main CLI documentation

## Integration

This orchestrator provides access to the Model Context Protocol framework, which is the foundation for:
- All AI-enhanced modules
- LLM tool interactions
- Standardized protocol enforcement

See `codomyrmex.cli.py` for main CLI integration.

