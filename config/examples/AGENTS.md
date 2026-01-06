# Codomyrmex Agents — config/examples

## Signposting
- **Parent**: [Parent](../AGENTS.md)
- **Self**: [Agents](AGENTS.md)
- **Children**:
    - None
- **Key Artifacts**:
    - [Functional Spec](SPEC.md)
    - [Human Readme](README.md)

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: December 2025

## Purpose

This directory contains example implementations and demonstrations of configuration patterns for the Codomyrmex system. These examples serve as templates and reference implementations for common configuration scenarios.

## Configuration Examples

### Docker Compose Example (`docker-compose.yml`)
**Purpose**: Multi-service container orchestration configuration
**Key Components**:
- Service definitions with resource limits
- Network configuration for service communication
- Volume mounts for persistent data
- Environment variable management
- Health check configurations

**Key Functions**:
```yaml
services:
  codomyrmex-api:
    image: codomyrmex/api:latest
    ports:
      - "8080:8080"
    environment:
      - CODOMYRMEX_ENV=production
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8080/health"]
      interval: 30s
      timeout: 10s
      retries: 3
```

### Project Template Example (`project-template-custom.json`)
**Purpose**: Custom project scaffolding configuration
**Key Components**:
- Project structure definitions
- Module dependencies specification
- Configuration inheritance patterns
- Template variable substitution

**Key Functions**:
```json
{
  "project": {
    "name": "{{project_name}}",
    "type": "codomyrmex-module",
    "version": "0.1.0"
  },
  "modules": [
    {
      "name": "ai_code_editing",
      "enabled": true,
      "config": {
        "max_tokens": 4096,
        "temperature": 0.7
      }
    }
  ]
}
```

### Resource Configuration (`resources-custom.json`)
**Purpose**: Resource allocation and scaling configuration
**Key Components**:
- CPU and memory limits/requests
- Storage allocation specifications
- Scaling policies and thresholds
- Resource monitoring configurations

**Key Functions**:
```json
{
  "resources": {
    "cpu": {
      "request": "500m",
      "limit": "2000m"
    },
    "memory": {
      "request": "1Gi",
      "limit": "4Gi"
    },
    "scaling": {
      "min_replicas": 1,
      "max_replicas": 10,
      "target_cpu_utilization": 70
    }
  }
}
```

### Basic Workflow (`workflow-basic.json`)
**Purpose**: Simple linear workflow configuration
**Key Components**:
- Sequential task execution
- Error handling and rollback
- Task dependencies and ordering
- Resource allocation per task

**Key Functions**:
```json
{
  "workflow": {
    "name": "basic-build",
    "steps": [
      {
        "name": "lint",
        "command": "ruff check src/",
        "timeout": 300,
        "on_failure": "stop"
      },
      {
        "name": "test",
        "command": "pytest testing/",
        "timeout": 600,
        "depends_on": ["lint"]
      }
    ]
  }
}
```

### Complex Workflow (`workflow-with-dependencies.json`)
**Purpose**: Advanced workflow with parallel execution and dependencies
**Key Components**:
- Parallel task execution
- Complex dependency graphs
- Conditional execution logic
- Resource pooling and allocation

**Key Functions**:
```json
{
  "workflow": {
    "name": "complex-deployment",
    "parallel_execution": true,
    "steps": [
      {
        "name": "build-api",
        "command": "docker build -t api ./api",
        "resources": {"cpu": "1000m", "memory": "2Gi"}
      },
      {
        "name": "build-worker",
        "command": "docker build -t worker ./worker",
        "resources": {"cpu": "500m", "memory": "1Gi"},
        "depends_on": ["build-api"]
      },
      {
        "name": "deploy",
        "command": "kubectl apply -f k8s/",
        "depends_on": ["build-api", "build-worker"],
        "condition": "all_previous_succeeded"
      }
    ]
  }
}
```

## Active Components
- `README.md` – Directory documentation
- `docker-compose.yml` – Multi-service container orchestration (services: codomyrmex-api, codomyrmex-worker, codomyrmex-db)
- `project-template-custom.json` – Custom project scaffolding (function: create_project_template(name: str, config: dict) -> bool)
- `resources-custom.json` – Resource allocation configuration (function: allocate_resources(config: dict) -> ResourceAllocation)
- `workflow-basic.json` – Basic sequential workflow (function: execute_workflow(workflow: dict) -> WorkflowResult)
- `workflow-with-dependencies.json` – Complex parallel workflow (function: execute_parallel_workflow(workflow: dict) -> WorkflowResult)

## Operating Contracts

### Example Maintenance
1. **Keep Examples Current** - Update examples to reflect latest Codomyrmex features
2. **Test Examples Regularly** - Ensure all examples work with current codebase
3. **Document Changes** - Update example documentation when configurations change
4. **Security Review** - Regularly audit examples for security best practices

### Quality Standards
- Examples must be functional and tested
- Include comments explaining configuration options
- Follow security best practices (no hardcoded secrets)
- Provide clear usage instructions

## Navigation Links
- **Human Documentation**: [README.md](README.md)
- **Functional Specification**: [SPEC.md](SPEC.md)
- **Parent Directory**: [config](../README.md)
- **Parent AGENTS**: [../AGENTS.md](../AGENTS.md)
- **Repository Root**: [../../README.md](../../README.md)