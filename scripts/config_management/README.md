# Config Management Orchestrator

Thin orchestrator script providing CLI access to the `codomyrmex.config_management` module.

## Purpose

This orchestrator provides command-line interface for configuration management and validation.

## Usage

```bash
# Load configuration
python scripts/config_management/orchestrate.py load-config --path config.json

# Validate configuration
python scripts/config_management/orchestrate.py validate-config --path config.json
```

## Commands

- `load-config` - Load configuration from file
- `validate-config` - Validate configuration

## Related Documentation

- **[Module README](../../src/codomyrmex/config_management/README.md)**: Complete module documentation
- **[CLI Reference](../../docs/reference/cli.md)**: Main CLI documentation

## Integration

This orchestrator calls functions from:
- `codomyrmex.config_management.load_configuration`
- `codomyrmex.config_management.validate_configuration`

See `codomyrmex.cli.py` for main CLI integration.

