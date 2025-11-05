# System Discovery Orchestrator

Thin orchestrator script providing CLI access to the `codomyrmex.system_discovery` module.

## Purpose

This orchestrator provides command-line interface for system introspection and capability mapping.

## Usage

```bash
# Generate system status report
python scripts/system_discovery/orchestrate.py status

# Scan system capabilities
python scripts/system_discovery/orchestrate.py scan

# Discover system components
python scripts/system_discovery/orchestrate.py discover
```

## Commands

- `status` - Generate system status report
- `scan` - Scan system capabilities
- `discover` - Discover system components

## Related Documentation

- **[Module README](../../src/codomyrmex/system_discovery/README.md)**: Complete module documentation
- **[API Specification](../../src/codomyrmex/system_discovery/API_SPECIFICATION.md)**: Detailed API reference
- **[Usage Examples](../../src/codomyrmex/system_discovery/USAGE_EXAMPLES.md)**: Practical examples
- **[CLI Reference](../../docs/reference/cli.md)**: Main CLI documentation

## Integration

This orchestrator calls functions from:
- `codomyrmex.system_discovery.StatusReporter`
- `codomyrmex.system_discovery.CapabilityScanner`
- `codomyrmex.system_discovery.SystemDiscovery`

See `codomyrmex.cli.py` for main CLI integration.

