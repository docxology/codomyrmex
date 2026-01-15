# Integration Examples Guide

Documentation for integration examples demonstrating multi-module workflows and coordination patterns.

## Overview

Integration examples demonstrate how multiple Codomyrmex modules work together to create comprehensive workflows. These examples showcase:
- Cross-module coordination
- Multi-step workflows
- Data flow between modules
- Resource management
- Error handling across modules

## Available Examples

### 1. Code Quality Pipeline

**File**: `scripts/examples/integration/code-quality-pipeline.sh`

**Purpose**: Complete code quality analysis workflow combining environment validation, static analysis, and data visualization.

**Modules Used**:
- `environment_setup` - Environment validation
- `static_analysis` - Code quality analysis
- `data_visualization` - Results visualization
- `logging_monitoring` - Structured logging

**Configuration**:
- Target directory: Current directory or `--target=PATH`
- Analysis tools: Pylint, Flake8, Bandit (automatic selection)
- Output format: JSON, HTML, PNG

**Execution**:
```bash
./scripts/examples/integration/code-quality-pipeline.sh
# Or with custom target
./scripts/examples/integration/code-quality-pipeline.sh --target=./src
```

**Workflow Steps**:
1. Environment validation and setup
2. Static code analysis
3. Quality metrics calculation
4. Visualization generation
5. Report compilation

**Expected Output**:
- Analysis reports in `scripts/output/code-quality-pipeline/`
- Quality metrics dashboard
- Visualization charts
- Comprehensive quality report

**Duration**: ~4 minutes

### 2. AI-Enhanced Analysis

**File**: `scripts/examples/integration/ai-enhanced-analysis.sh`

**Purpose**: Demonstrates AI-powered code analysis combining static analysis with AI insights.

**Modules Used**:
- `static_analysis` - Initial code analysis
- `ai_code_editing` - AI-powered insights
- `data_visualization` - Results visualization

**Configuration**:
- AI provider: OpenAI (configurable)
- Analysis depth: Comprehensive
- Output formats: JSON, HTML

**Execution**:
```bash
./scripts/examples/integration/ai-enhanced-analysis.sh
```

**Workflow Steps**:
1. Static analysis of codebase
2. AI analysis of findings
3. Insight generation
4. Visualization creation
5. Report generation

**Expected Output**:
- AI-enhanced analysis reports
- Insight visualizations
- Recommendations and suggestions
- Quality improvement metrics

**Duration**: ~5-7 minutes (depends on AI provider response time)

### 3. Environment Health Monitor

**File**: `scripts/examples/integration/environment-health-monitor.sh`

**Purpose**: Monitors system health and environment status across multiple components.

**Modules Used**:
- `environment_setup` - Environment checks
- `logging_monitoring` - Health metrics
- `data_visualization` - Health dashboards

**Configuration**:
- Check interval: Configurable
- Metrics tracked: System resources, module status, dependencies

**Execution**:
```bash
./scripts/examples/integration/environment-health-monitor.sh
```

**Expected Output**:
- Health status reports
- System metrics dashboards
- Environment validation results
- Resource utilization charts

**Duration**: ~2 minutes

### 4. Development Workflow Orchestrator

**File**: `scripts/examples/integration/development-workflow-orchestrator.sh`

**Purpose**: Complete development workflow from code analysis to visualization.

**Modules Used**:
- Multiple modules coordinated through orchestration

**Configuration**:
- Workflow definition: Configurable
- Resource allocation: Automatic

**Execution**:
```bash
./scripts/examples/integration/development-workflow-orchestrator.sh
```

**Expected Output**:
- Complete workflow results
- Execution metrics
- Generated artifacts
- Performance reports

**Duration**: ~5 minutes

### 5. Comprehensive Analysis Pipeline

**File**: `scripts/examples/integration/comprehensive_analysis_pipeline.sh`

**Purpose**: Comprehensive analysis combining multiple analysis types and visualization.

**Modules Used**:
- `static_analysis` - Code analysis
- `pattern_matching` - Pattern detection
- `data_visualization` - Visualization
- `ai_code_editing` - AI insights

**Configuration**:
- Analysis types: Configurable
- Output formats: Multiple

**Execution**:
```bash
./scripts/examples/integration/comprehensive_analysis_pipeline.sh
```

**Expected Output**:
- Comprehensive analysis reports
- Pattern detection results
- Multi-dimensional visualizations
- AI-generated insights

**Duration**: ~6-8 minutes

### 6. AI-Driven Development Workflow

**File**: `scripts/examples/integration/ai_driven_development_workflow.sh`

**Purpose**: AI-assisted development workflow from code generation to analysis.

**Modules Used**:
- `ai_code_editing` - Code generation
- `static_analysis` - Code analysis
- `data_visualization` - Results visualization

**Configuration**:
- AI provider: Configurable
- Generation parameters: Customizable

**Execution**:
```bash
./scripts/examples/integration/ai_driven_development_workflow.sh
```

**Expected Output**:
- Generated code samples
- Analysis of generated code
- Quality metrics
- Visualization of results

**Duration**: ~5-7 minutes

## Configuration Requirements

### Environment Variables

Some integration examples require environment variables:

```bash
# AI provider API keys
export OPENAI_API_KEY="your-key"
export ANTHROPIC_API_KEY="your-key"

# Configuration paths
export CODOMYRMEX_WORKFLOWS_DIR="./workflows"
export CODOMYRMEX_RESOURCE_CONFIG="./resources.json"
```

### Module Dependencies

Integration examples require multiple modules:

```python
# Check module availability
from codomyrmex.project_orchestration import get_orchestration_engine

engine = get_orchestration_engine()
status = engine.get_system_status()
print(status)
```

## Coordination Patterns

### Sequential Execution

Modules execute in sequence:

```
Module A → Module B → Module C
```

### Parallel Execution

Independent modules execute in parallel:

```
Module A ──┐
           ├─> Module D
Module B ──┘
Module C ──┐
           └─> Module E
```

### Conditional Execution

Modules execute based on conditions:

```
Module A → [condition] → Module B or Module C
```

## Error Handling

Integration examples handle errors across modules:

1. **Module-Level Errors**: Handled within module
2. **Workflow-Level Errors**: Propagated and logged
3. **Resource Errors**: Automatic cleanup
4. **Timeout Errors**: Handled with retries

## Best Practices

1. **Configuration**: Use configuration files for complex workflows
2. **Resource Management**: Specify resource requirements
3. **Error Handling**: Implement comprehensive error handling
4. **Logging**: Use structured logging for debugging
5. **Monitoring**: Monitor execution metrics
6. **Testing**: Test workflows with sample data first

## Troubleshooting

### Module Import Errors

**Error**: Module not found or import fails

**Solution**:
```bash
# Verify module installation
uv run python -c "import codomyrmex.static_analysis; print('OK')"

# Reinstall if needed
uv sync
```

### Resource Allocation Failures

**Error**: Resources not available

**Solution**:
```bash
# Check resource configuration
cat resources.json

# Verify resource availability
python -c "from codomyrmex.project_orchestration import get_resource_manager; rm = get_resource_manager(); print(rm.get_resource_usage())"
```

### Workflow Execution Failures

**Error**: Workflow fails or times out

**Solution**:
- Check workflow configuration
- Verify module dependencies
- Review execution logs
- Check resource availability

## Related Documentation

- [Basic Examples Guide](./basic-examples.md)
- [Orchestration Examples Guide](./orchestration-examples.md)
- [Dispatch and Coordination](../project_orchestration/dispatch-coordination.md)
- [Config-Driven Operations](../project_orchestration/config-driven-operations.md)


## Navigation Links

- **Parent**: [Project Overview](../README.md)
- **Module Index**: [All Agents](../../AGENTS.md)
- **Documentation**: [Reference Guides](../../docs/README.md)
- **Home**: [Repository Root](../../README.md)
