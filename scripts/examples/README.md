# Codomyrmex Examples

This directory contains executable demonstration scripts that showcase Codomyrmex capabilities through complete workflows.

## Structure

- `basic/` - Basic single-module demonstrations
- `integration/` - Multi-module integration orchestrators
- `configs/` - Example-specific configuration files

## Usage

### Running Examples

```bash
# Basic examples
./scripts/examples/basic/data-visualization-demo.sh
./scripts/examples/basic/static-analysis-demo.sh

# Integration examples
./scripts/examples/integration/environment-health-monitor.sh
./scripts/examples/integration/code-quality-pipeline.sh

# Orchestration examples
python scripts/project_orchestration/examples.py

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

4. Try orchestration examples:
   ```bash
   python scripts/project_orchestration/examples.py
   ```

## Configuration Files

Example-specific configuration files are available:
- `configs/` - Example workflow configurations
- `config/examples/` - Reusable configuration templates

### Using Configuration Files

```bash
# Copy example configuration
cp config/examples/workflow-basic.json .codomyrmex/workflows/my_workflow.json

# Use with workflow manager
python -c "
from codomyrmex.project_orchestration import get_workflow_manager
import asyncio

async def main():
    manager = get_workflow_manager()
    # Workflow is automatically loaded from .codomyrmex/workflows/
    execution = await manager.execute_workflow('my_workflow')
    print(f'Status: {execution.status}')

asyncio.run(main())
"
```

## Documentation

### Comprehensive Examples Documentation

- [Examples Overview](../../docs/examples/README.md) - Complete examples documentation
- [Basic Examples Guide](../../docs/examples/basic-examples.md) - Single-module examples
- [Integration Examples Guide](../../docs/examples/integration-examples.md) - Multi-module workflows
- [Orchestration Examples Guide](../../docs/examples/orchestration-examples.md) - Task/project/workflow orchestration

### Configuration Guides

- [Workflow Configuration Schema](../../docs/project_orchestration/workflow-configuration-schema.md)
- [Project Template Schema](../../docs/project_orchestration/project-template-schema.md)
- [Resource Configuration](../../docs/project_orchestration/resource-configuration.md)
- [Config-Driven Operations](../../docs/project_orchestration/config-driven-operations.md)

### Other Documentation

- [Advanced Orchestrators Guide](../docs/advanced_orchestrators_guide.md)
- [Orchestrator Status Report](../docs/orchestrator_status_report.md)

