# Terminal Interface Orchestrator

Thin orchestrator script providing CLI access to the `codomyrmex.terminal_interface` module.

## Purpose

This orchestrator provides command-line interface for interactive shell and terminal utilities.

## Usage

```bash
# Launch interactive shell
python scripts/terminal_interface/orchestrate.py shell

# Test terminal formatting
python scripts/terminal_interface/orchestrate.py format
```

## Commands

- `shell` - Launch interactive Codomyrmex shell
- `format` - Test terminal formatting capabilities

## Related Documentation

- **[Module README](../../src/codomyrmex/terminal_interface/README.md)**: Complete module documentation
- **[API Specification](../../src/codomyrmex/terminal_interface/API_SPECIFICATION.md)**: Detailed API reference
- **[Usage Examples](../../src/codomyrmex/terminal_interface/USAGE_EXAMPLES.md)**: Practical examples
- **[CLI Reference](../../docs/reference/cli.md)**: Main CLI documentation

## Integration

This orchestrator calls functions from:
- `codomyrmex.terminal_interface.InteractiveShell`
- `codomyrmex.terminal_interface.TerminalFormatter`

See `codomyrmex.cli.py` for main CLI integration.

