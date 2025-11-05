# Codomyrmex Examples

This directory contains executable demonstration scripts that showcase Codomyrmex capabilities through complete workflows.

## Structure

- `basic/` - Basic single-module demonstrations
- `integration/` - Multi-module integration orchestrators

## Usage

### Running Examples

```bash
# Basic examples
./scripts/examples/basic/data-visualization-demo.sh
./scripts/examples/basic/static-analysis-demo.sh

# Integration examples
./scripts/examples/integration/environment-health-monitor.sh
./scripts/examples/integration/code-quality-pipeline.sh

# Run all examples
./scripts/development/run_all_examples.sh

# Test all examples
./scripts/development/test_examples.sh
```

### Output

All examples generate output in `scripts/output/` at the project root.

## Quick Start

1. Check prerequisites:
   ```bash
   ./scripts/development/check_prerequisites.sh
   ```

2. Run a basic example:
   ```bash
   ./scripts/examples/basic/data-visualization-demo.sh
   ```

3. Try an integration example:
   ```bash
   ./scripts/examples/integration/environment-health-monitor.sh
   ```

## Documentation

- [Advanced Orchestrators Guide](../docs/advanced_orchestrators_guide.md)
- [Orchestrator Status Report](../docs/orchestrator_status_report.md)

