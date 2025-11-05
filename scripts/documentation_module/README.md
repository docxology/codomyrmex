# Documentation Module Orchestrator

Thin orchestrator script providing CLI access to the `codomyrmex.documentation` module.

**Note**: This is for the codomyrmex.documentation module (Docusaurus website generation), not the scripts/documentation/ utilities.

## Purpose

This orchestrator provides command-line interface for documentation website generation and management.

## Usage

```bash
# Check documentation environment
python scripts/documentation_module/orchestrate.py check-environment

# Build static documentation site
python scripts/documentation_module/orchestrate.py build --output docs/build/

# Start development server
python scripts/documentation_module/orchestrate.py dev-server --port 3000

# Aggregate documentation
python scripts/documentation_module/orchestrate.py aggregate --source docs/ --output docs/aggregated/

# Assess documentation site
python scripts/documentation_module/orchestrate.py assess --path docs/build/
```

## Commands

- `check-environment` - Check documentation environment setup
- `build` - Build static documentation site
- `dev-server` - Start development server
- `aggregate` - Aggregate documentation from multiple sources
- `assess` - Assess documentation site quality

## Related Documentation

- **[Module README](../../src/codomyrmex/documentation/README.md)**: Complete module documentation
- **[API Specification](../../src/codomyrmex/documentation/API_SPECIFICATION.md)**: Detailed API reference
- **[Usage Examples](../../src/codomyrmex/documentation/USAGE_EXAMPLES.md)**: Practical examples
- **[CLI Reference](../../docs/reference/cli.md)**: Main CLI documentation

## Integration

This orchestrator calls functions from:
- `codomyrmex.documentation.check_doc_environment`
- `codomyrmex.documentation.build_static_site`
- `codomyrmex.documentation.start_dev_server`
- `codomyrmex.documentation.aggregate_docs`
- `codomyrmex.documentation.assess_site`

See `codomyrmex.cli.py` for main CLI integration.

