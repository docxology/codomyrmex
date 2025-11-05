# Pattern Matching Orchestrator

Thin orchestrator script providing CLI access to the `codomyrmex.pattern_matching` module.

## Purpose

This orchestrator provides command-line interface for advanced pattern matching and code structure analysis.

## Usage

```bash
# Analyze repository patterns
python scripts/pattern_matching/orchestrate.py analyze --path src/

# Run full pattern analysis
python scripts/pattern_matching/orchestrate.py full-analysis --path . --output results.json
```

## Commands

- `analyze` - Analyze repository patterns
- `full-analysis` - Run full pattern analysis

## Related Documentation

- **[Module README](../../src/codomyrmex/pattern_matching/README.md)**: Complete module documentation
- **[API Specification](../../src/codomyrmex/pattern_matching/API_SPECIFICATION.md)**: Detailed API reference
- **[Usage Examples](../../src/codomyrmex/pattern_matching/USAGE_EXAMPLES.md)**: Practical examples
- **[CLI Reference](../../docs/reference/cli.md)**: Main CLI documentation

## Integration

This orchestrator calls functions from:
- `codomyrmex.pattern_matching.analyze_repository_path`
- `codomyrmex.pattern_matching.run_full_analysis`

See `codomyrmex.cli.py` for main CLI integration.

