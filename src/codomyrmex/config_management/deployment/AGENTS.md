# Codomyrmex Agents -- src/codomyrmex/config_management/deployment

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Purpose

Provides configuration deployment and environment management for pushing configuration files across development, staging, production, and testing environments. Supports environment variable substitution, deployment tracking, and rollback capabilities.

## Key Components

| File | Class / Function | Role |
|------|-----------------|------|
| `config_deployer.py` | `ConfigurationDeployer` | Main deployer managing environments, deployments, and rollbacks |
| `config_deployer.py` | `ConfigurationDeployer.create_environment` | Creates a named environment with type, config path, and variables |
| `config_deployer.py` | `ConfigurationDeployer.deploy_configuration` | Deploys config files to an environment with change analysis |
| `config_deployer.py` | `ConfigurationDeployer.rollback_deployment` | Rolls back a specific deployment by ID |
| `config_deployer.py` | `Environment` | Dataclass holding environment name, type, config path, variables, and secrets |
| `config_deployer.py` | `ConfigDeployment` | Dataclass representing a deployment record with status tracking |
| `config_deployer.py` | `DeploymentStatus` | Enum: `PENDING`, `IN_PROGRESS`, `SUCCESS`, `FAILED`, `ROLLED_BACK` |
| `config_deployer.py` | `EnvironmentType` | Enum: `DEVELOPMENT`, `STAGING`, `PRODUCTION`, `TESTING` |
| `config_deployer.py` | `deploy_configuration` | Convenience function for quick deployment |

## Operating Contracts

- Environment and deployment records are persisted as JSON files under `config_deployments/` and `environments/` directories.
- Environment variable substitution supports both `${KEY}` and `$KEY` placeholder syntax.
- Deployment IDs are generated from environment name and Unix timestamp.
- A deployment that fails has its status set to `FAILED` and the record is still saved.
- Rollback creates a new deployment record with status tracking independent of the original.
- Errors must be logged via `logging_monitoring` before re-raising.

## Integration Points

- **Depends on**: `codomyrmex.exceptions.CodomyrmexError`, `codomyrmex.logging_monitoring.core.logger_config`
- **Used by**: CI/CD pipelines, orchestrator workflows, environment management

## Navigation

- **Parent**: [../AGENTS.md](../AGENTS.md)
- **Root**: [../../../../README.md](../../../../README.md)
