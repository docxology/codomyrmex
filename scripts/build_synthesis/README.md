# Build Synthesis Orchestrator

Thin orchestrator script providing CLI access to the `codomyrmex.build_synthesis` module.

## Purpose

This orchestrator provides command-line interface for build automation, dependency management, and artifact synthesis.

## Usage

```bash
# Check build environment
python scripts/build_synthesis/orchestrate.py check-environment

# Run build pipeline
python scripts/build_synthesis/orchestrate.py build --config build_config.json

# Trigger specific build target
python scripts/build_synthesis/orchestrate.py trigger-build --target python --environment production

# List available build types
python scripts/build_synthesis/orchestrate.py list-build-types

# List available build environments
python scripts/build_synthesis/orchestrate.py list-environments
```

## Commands

- `check-environment` - Check build environment setup
- `build` - Run complete build pipeline
- `trigger-build` - Trigger a specific build target
- `list-build-types` - List available build types
- `list-environments` - List available build environments

## Related Documentation

- **[Module README](../../src/codomyrmex/build_synthesis/README.md)**: Complete module documentation
- **[API Specification](../../src/codomyrmex/build_synthesis/API_SPECIFICATION.md)**: Detailed API reference
- **[MCP Tools](../../src/codomyrmex/build_synthesis/MCP_TOOL_SPECIFICATION.md)**: AI integration tools
- **[Usage Examples](../../src/codomyrmex/build_synthesis/USAGE_EXAMPLES.md)**: Practical examples
- **[CLI Reference](../../docs/reference/cli.md)**: Main CLI documentation

## Integration

This orchestrator calls functions from:
- `codomyrmex.build_synthesis.check_build_environment`
- `codomyrmex.build_synthesis.orchestrate_build_pipeline`
- `codomyrmex.build_synthesis.trigger_build`
- `codomyrmex.build_synthesis.get_available_build_types`
- `codomyrmex.build_synthesis.get_available_environments`

See `codomyrmex.cli.py` for main CLI integration.

