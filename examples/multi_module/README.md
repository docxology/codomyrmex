# Multi-Module Integration Examples

This directory contains examples demonstrating integration of multiple Codomyrmex modules working together in real-world workflows.

## Overview

These examples show how different modules can be composed to create powerful, production-ready workflows. Each workflow uses multiple modules with event-driven communication and centralized logging.

## Workflows

### Analysis Pipeline (`example_workflow_analysis.py`)

**Modules Integrated:**
- Static Analysis - Code quality checking
- Security Audit - Vulnerability scanning  
- Data Visualization - Results visualization
- Logging Monitoring - Centralized logging
- Events - Event-driven communication

**Use Case:** Analyze codebase for quality and security issues, generate visual reports

**Configuration:** `config_workflow_analysis.yaml`

```bash
python example_workflow_analysis.py
```

### Build Pipeline (`example_workflow_build.py`)

**Modules Integrated:**
- Build Synthesis - Build orchestration
- CI/CD Automation - Pipeline execution
- Containerization - Docker image creation
- Logging Monitoring - Build logging
- Events - Build event tracking

**Use Case:** Complete build, test, and containerization pipeline

**Configuration:** `config_workflow_build.yaml`

### Development Workflow (`example_workflow_development.py`)

**Modules Integrated:**
- AI Code Editing - Code generation and refactoring
- Code Review - Automated review
- Git Operations - Version control
- Static Analysis - Quality checks
- Logging Monitoring - Development logging

**Use Case:** AI-assisted development with automated quality checks

**Configuration:** `config_workflow_development.yaml`

### Monitoring Dashboard (`example_workflow_monitoring.py`)

**Modules Integrated:**
- Logging Monitoring - Centralized logs
- Performance - System metrics
- System Discovery - Module health
- Data Visualization - Metrics visualization
- Events - Real-time event streaming

**Use Case:** System monitoring and observability dashboard

**Configuration:** `config_workflow_monitoring.yaml`

### API Workflow (`example_workflow_api.py`)

**Modules Integrated:**
- API Standardization - REST/GraphQL APIs
- API Documentation - OpenAPI specs
- Database Management - Data persistence
- Config Management - API configuration
- Events - API event logging

**Use Case:** Complete API development and documentation workflow

**Configuration:** `config_workflow_api.yaml`

## Common Patterns

### Event-Driven Communication

All workflows use the Events module for inter-module communication:

```python
from codomyrmex.events import publish_event, subscribe_to_events, EventType

# Publish event
publish_event(EventType.ANALYSIS_START, source='workflow', data={...})

# Subscribe to events
subscribe_to_events([EventType.ANALYSIS_COMPLETE], handler_function)
```

### Centralized Logging

All workflows use consistent logging:

```python
from codomyrmex.logging_monitoring import setup_logging, get_logger

setup_logging()
logger = get_logger('workflow.name')
logger.info("Workflow step completed")
```

### Configuration-Driven

All workflows are fully configurable via YAML/JSON:

```yaml
workflow:
  modules:
    - module_name: static_analysis
      config: {...}
    - module_name: security_audit
      config: {...}
```

## Running Workflows

```bash
# Navigate to multi_module directory
cd examples/multi_module

# Run a specific workflow
python example_workflow_analysis.py

# With custom config
python example_workflow_analysis.py --config my_config.yaml

# Check results
ls output/workflow_*/
cat output/workflow_*_results.json
```

## Output Structure

Each workflow generates:
- JSON results file: `output/workflow_name_results.json`
- Visualizations: `output/workflow_name/*.png`
- Logs: `logs/workflow_name.log`
- Event logs (if enabled)

## Extending Workflows

To create custom workflows:

1. Copy an existing workflow example
2. Modify the configuration file
3. Add/remove modules as needed
4. Customize the workflow logic
5. Update event types if needed

## Related Documentation

- [Events Module](../../src/codomyrmex/events/README.md)
- [Logging Module](../../src/codomyrmex/logging_monitoring/README.md)
- [Project Orchestration](../../src/codomyrmex/project_orchestration/README.md)
- [Integration Tests](../../testing/integration/)

