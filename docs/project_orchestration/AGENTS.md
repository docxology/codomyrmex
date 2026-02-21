# Codomyrmex Agents — docs/project_orchestration

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: February 2026

## Purpose

Advanced documentation for multi-project workflow orchestration, task coordination, and resource management at scale.

## Active Components

| File | Priority | Description |
|------|----------|-------------|
| [task-orchestration-guide.md](task-orchestration-guide.md) | **Critical** | Complete orchestration guide |
| [workflow-configuration-schema.md](workflow-configuration-schema.md) | **Critical** | Workflow schema spec |
| [project-lifecycle-guide.md](project-lifecycle-guide.md) | High | Lifecycle management |
| [dispatch-coordination.md](dispatch-coordination.md) | High | Task dispatch patterns |
| [config-driven-operations.md](config-driven-operations.md) | High | Config-driven workflows |
| [project-template-schema.md](project-template-schema.md) | Medium | Project templates |
| [resource-configuration.md](resource-configuration.md) | Medium | Resource management |

## Agent Guidelines

### Orchestration Quality Standards

1. **Correctness**: Workflow schemas must be valid YAML/JSON
2. **Examples**: Include runnable workflow examples
3. **Patterns**: Document common orchestration patterns
4. **Error Handling**: Document retry and fallback strategies

### When Modifying Orchestration Docs

- Validate all workflow schemas against current spec
- Test orchestration examples with the orchestrator module
- Update DAG visualization when dependencies change
- Keep resource limits current with available hardware

## Operating Contracts

- Maintain alignment between orchestration docs and orchestrator module
- Ensure Model Context Protocol interfaces remain available for sibling agents
- Record outcomes in shared telemetry and update TODO queues when necessary

## Navigation Links

- **📁 Parent Directory**: [docs/](../README.md)
- **🏠 Project Root**: [../../README.md](../../README.md)
- **📦 Related**: [Orchestrator Reference](../reference/orchestrator.md) | [Examples](../examples/orchestration-examples.md)
