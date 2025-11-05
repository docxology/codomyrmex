# Containerization Orchestrator

Thin orchestrator script providing CLI access to the `codomyrmex.containerization` module.

## Purpose

This orchestrator provides command-line interface for container management and security scanning.

## Usage

```bash
# Build containers
python scripts/containerization/orchestrate.py build --source .

# Scan container security
python scripts/containerization/orchestrate.py scan --container my-container
```

## Commands

- `build` - Build Docker containers from source
- `scan` - Scan container security

## Related Documentation

- **[Module README](../../src/codomyrmex/containerization/README.md)**: Complete module documentation
- **[CLI Reference](../../docs/reference/cli.md)**: Main CLI documentation

## Integration

This orchestrator calls functions from:
- `codomyrmex.containerization.build_containers`
- `codomyrmex.containerization.scan_container_security`

See `codomyrmex.cli.py` for main CLI integration.

