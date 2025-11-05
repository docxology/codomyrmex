# Codomyrmex Examples Documentation

Comprehensive documentation for all Codomyrmex examples, including purpose, configuration, execution steps, and expected outcomes.

## Overview

The Codomyrmex examples directory contains executable demonstrations organized into three categories:

- **Basic Examples**: Single-module demonstrations showcasing individual capabilities
- **Integration Examples**: Multi-module workflows demonstrating cross-module coordination
- **Orchestration Examples**: Task/project/workflow orchestration demonstrations

## Directory Structure

```
scripts/examples/
├── basic/                    # Basic single-module examples
│   ├── data-visualization-demo.sh
│   ├── static-analysis-demo.sh
│   └── advanced_data_visualization_demo.sh
├── integration/              # Multi-module integration examples
│   ├── code-quality-pipeline.sh
│   ├── ai-enhanced-analysis.sh
│   ├── environment-health-monitor.sh
│   └── ... (more examples)
└── project_orchestration/   # Orchestration examples
    └── examples.py
```

## Quick Start

### Running Examples

```bash
# Basic examples
./scripts/examples/basic/data-visualization-demo.sh
./scripts/examples/basic/static-analysis-demo.sh

# Integration examples
./scripts/examples/integration/code-quality-pipeline.sh
./scripts/examples/integration/ai-enhanced-analysis.sh

# Orchestration examples
python scripts/project_orchestration/examples.py
```

### Prerequisites

Most examples require:
- Python 3.10+
- Codomyrmex installed (see [Installation Guide](../getting-started/installation.md))
- Required modules available (checked automatically)

## Example Categories

### Basic Examples

Demonstrate individual module capabilities:
- Data visualization
- Static analysis
- Advanced data visualization

See [Basic Examples Guide](./basic-examples.md) for detailed documentation.

### Integration Examples

Demonstrate multi-module workflows:
- Code quality pipelines
- AI-enhanced analysis
- Environment health monitoring
- Development workflows

See [Integration Examples Guide](./integration-examples.md) for detailed documentation.

### Orchestration Examples

Demonstrate task/project/workflow orchestration:
- Task orchestration
- Project management
- Workflow execution
- Resource management

See [Orchestration Examples Guide](./orchestration-examples.md) for detailed documentation.

## Configuration Files

Example-specific configuration files are available in:
- `config/examples/` - Example workflow and project configurations
- `scripts/examples/configs/` - Example-specific configurations

## Output Locations

All examples generate output in:
- `scripts/output/` - Example outputs organized by example name
- `output/` - General project outputs

## Related Documentation

- [Basic Examples Guide](./basic-examples.md)
- [Integration Examples Guide](./integration-examples.md)
- [Orchestration Examples Guide](./orchestration-examples.md)
- [Configuration Examples](../project_orchestration/config-driven-operations.md)

