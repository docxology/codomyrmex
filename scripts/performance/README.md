# Performance Orchestrator

Thin orchestrator script providing CLI access to the `codomyrmex.performance` module.

## Purpose

This orchestrator provides command-line interface for performance monitoring and optimization utilities.

## Usage

```bash
# Get performance monitor statistics
python scripts/performance/orchestrate.py monitor-stats

# Get cache manager information
python scripts/performance/orchestrate.py cache-info
```

## Commands

- `monitor-stats` - Get performance monitor statistics
- `cache-info` - Get cache manager information

## Related Documentation

- **[Module README](../../src/codomyrmex/performance/README.md)**: Complete module documentation
- **[API Specification](../../src/codomyrmex/performance/API_SPECIFICATION.md)**: Detailed API reference
- **[Usage Examples](../../src/codomyrmex/performance/USAGE_EXAMPLES.md)**: Practical examples
- **[CLI Reference](../../docs/reference/cli.md)**: Main CLI documentation

## Integration

This orchestrator calls functions from:
- `codomyrmex.performance.PerformanceMonitor`
- `codomyrmex.performance.CacheManager`

See `codomyrmex.cli.py` for main CLI integration.

## Requirements

- `psutil` package is required for PerformanceMonitor functionality

