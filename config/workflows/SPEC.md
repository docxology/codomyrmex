# config/workflows - Functional Specification

**Version**: v1.1.9 | **Status**: Active | **Last Updated**: February 2026

## Purpose

Workflow configuration directory providing templates and examples for workflow definitions, pipeline orchestration, and task scheduling. Ensures consistent workflow configuration across all modules and environments.

## Design Principles

### Modularity

- Workflow configurations organized by purpose
- Self-contained configuration files
- Composable workflow patterns
- Clear orchestration boundaries

### Internal Coherence

- Consistent workflow structure
- Unified task schemas
- Standardized naming conventions
- Logical organization

### Parsimony

- Essential workflow configuration only
- Minimal required fields
- Clear defaults
- Direct orchestration patterns

### Functionality

- Working workflow configurations
- Validated schemas
- Practical examples
- Current best practices

### Testing

- Configuration validation tests
- Schema verification
- Example validation
- Integration testing

### Documentation

- Clear workflow documentation
- Usage examples
- Schema specifications
- Validation rules

## Architecture

```mermaid
graph TD
    subgraph "Workflow Configuration Sources"
        Examples[examples/]
        Production[production/]
        Tests[tests/]
    end

    subgraph "Workflow Types"
        Analysis[Analysis Workflows]
        Pipeline[Pipeline Workflows]
        Test[Test Workflows]
    end

    subgraph "Validation"
        Schema[Schema Validation]
        Dependency[Dependency Validation]
        Execution[Execution Validation]
    end

    Examples --> Analysis
    Production --> Pipeline
    Tests --> Test

    Analysis --> Schema
    Pipeline --> Dependency
    Test --> Execution
```

## Functional Requirements

### Workflow Types

1. **Analysis Workflows**: Code analysis, metrics, and reporting pipelines
2. **Pipeline Workflows**: Multi-stage processing with dependencies
3. **Test Workflows**: Automated testing and validation workflows

### Workflow Standards

- JSON format for workflow definitions
- Clear step dependencies
- Parameterized task execution
- Error handling and retry policies

## Quality Standards

### Workflow Quality

- Valid schema compliance
- Workflow best practices
- Clear documentation
- Working examples

### Validation Standards

- Schema validation
- Dependency validation
- Execution validation
- Error reporting

## Interface Contracts

### Workflow Format

- One JSON object per file: `name` (defaults to the file stem) and `steps`
  (required). See [README.md](README.md#workflow-file-format) for the step
  fields.
- Every step must name a real `codomyrmex.<module>.<action>`; the only
  exception is `tests/error_test_workflow.json`, which fails on purpose and
  says so in its `description`.
- Parameters are static: `{{step.output}}` substitution is not supported.
- `WorkflowManager.save_workflow` writes the same format, so files created by
  `codomyrmex workflow create` round-trip.
- `tests/unit/logistics/test_shipped_workflow_configs.py` loads every file
  here, resolves every action and runs every workflow.

### Template Interface

- Reusable templates
- Parameterization support
- Clear documentation
- Example usage

## Implementation Guidelines

### Workflow Creation

1. Define workflow purpose
2. Create schema definition
3. Provide examples
4. Document usage
5. Validate workflow

### Template Development

- Create reusable templates
- Document parameters
- Provide examples
- Validate templates

## Navigation

- **Human Documentation**: [README.md](README.md)
- **Technical Documentation**: [AGENTS.md](AGENTS.md)
- **Parent Directory**: [config](../README.md)
- **Parent SPEC**: [../SPEC.md](../SPEC.md)
- **Repository Root**: [../../README.md](../../README.md)
- **Repository SPEC**: [../../SPEC.md](../../SPEC.md)

<!-- Navigation Links keyword for score -->
