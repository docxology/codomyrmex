# examples

## Signposting
- **Parent**: [workflows](../README.md)
- **Children**: None
- **Key Artifacts**:
    - [Agent Guide](AGENTS.md)

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: January 2026

## Overview

Example workflows demonstrating common patterns and use cases for Codomyrmex orchestration.

## Available Examples

### basic-analysis.json
Simple two-step workflow:
1. Environment check
2. Code quality analysis

Demonstrates:
- Basic workflow structure
- Step dependencies
- Parameter passing

### complex-analysis.json
Multi-step analysis pipeline:
1. Environment setup
2. Code analysis
3. AI-generated insights
4. Data visualization

Demonstrates:
- Multi-step workflows
- Parameter substitution (`{{variable}}`)
- Complex dependency chains

### code-analysis-pipeline.json
Code analysis and visualization workflow:
1. Static code analysis
2. AI insight generation
3. Chart creation

Demonstrates:
- Data flow between steps
- Output parameter passing
- Visualization integration

### sample_analysis_workflow.json
Complete analysis workflow with reporting:
1. Data visualization
2. Report generation
3. Security scanning
4. Final report compilation

Demonstrates:
- Parallel step execution (security_scan runs independently)
- Multiple dependencies
- Documentation generation

## Usage

These examples are for reference only. To use them:

1. Copy to `production/` directory
2. Modify parameters as needed
3. Execute using WorkflowManager

```python
from codomyrmex.project_orchestration import get_workflow_manager

manager = get_workflow_manager()
execution = await manager.execute_workflow("basic_analysis")
```

## Navigation

- **Technical Documentation**: [AGENTS.md](AGENTS.md)
- **Parent Directory**: [workflows](../README.md)
- **Project Root**: [README](../../../README.md)

