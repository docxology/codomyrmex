# Static Analysis Orchestrator

Thin orchestrator script providing CLI access to the `codomyrmex.static_analysis` module.

## Purpose

This orchestrator provides command-line interface for code quality analysis, security scanning, and metrics collection.

## Usage

```bash
# Analyze a single file
python scripts/static_analysis/orchestrate.py analyze-file file.py --output results.json

# Analyze an entire project
python scripts/static_analysis/orchestrate.py analyze-project . --output analysis_report.json

# List available analysis tools
python scripts/static_analysis/orchestrate.py list-tools
```

## Commands

- `analyze-file` - Analyze a single file for various issues
- `analyze-project` - Analyze an entire project
- `list-tools` - List available analysis tools

## Related Documentation

- **[Module README](../../src/codomyrmex/static_analysis/README.md)**: Complete module documentation
- **[API Specification](../../src/codomyrmex/static_analysis/API_SPECIFICATION.md)**: Detailed API reference
- **[MCP Tools](../../src/codomyrmex/static_analysis/MCP_TOOL_SPECIFICATION.md)**: AI integration tools
- **[Usage Examples](../../src/codomyrmex/static_analysis/USAGE_EXAMPLES.md)**: Practical examples
- **[CLI Reference](../../docs/reference/cli.md)**: Main CLI documentation

## Integration

This orchestrator calls functions from:
- `codomyrmex.static_analysis.analyze_file`
- `codomyrmex.static_analysis.analyze_project`
- `codomyrmex.static_analysis.get_available_tools`

See `codomyrmex.cli.py` for main CLI integration.

