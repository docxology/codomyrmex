# Environment Setup Orchestrator

Thin orchestrator script providing CLI access to the `codomyrmex.environment_setup` module.

## Purpose

This orchestrator provides command-line interface for development environment validation and setup automation.

## Usage

```bash
# Check if all dependencies are installed
python scripts/environment_setup/orchestrate.py check-dependencies

# Check and setup required environment variables
python scripts/environment_setup/orchestrate.py setup-env-vars

# Check UV availability and environment
python scripts/environment_setup/orchestrate.py check-uv
```

## Commands

- `check-dependencies` - Check if all dependencies are installed
- `setup-env-vars` - Check and setup required environment variables
- `check-uv` - Check UV availability and environment

## Related Documentation

- **[Module README](../../src/codomyrmex/environment_setup/README.md)**: Complete module documentation
- **[API Specification](../../src/codomyrmex/environment_setup/API_SPECIFICATION.md)**: Detailed API reference
- **[Usage Examples](../../src/codomyrmex/environment_setup/USAGE_EXAMPLES.md)**: Practical examples
- **[CLI Reference](../../docs/reference/cli.md)**: Main CLI documentation

## Integration

This orchestrator calls functions from:
- `codomyrmex.environment_setup.ensure_dependencies_installed`
- `codomyrmex.environment_setup.check_and_setup_env_vars`
- `codomyrmex.environment_setup.is_uv_available`
- `codomyrmex.environment_setup.is_uv_environment`

See `codomyrmex.cli.py` for main CLI integration.

