# deployment - Technical Documentation

## Operating Contract

- Encapsulate deployment logic in strategy-specific classes.
- Provide a unified `DeploymentManager` for orchestration.
- Use structured events/logging for all deployment stages.
- Ensure all actions are reversible (rollback support).

## Directory Structure

- `__init__.py`: Module entry point and exports.
- `manager.py`: Core `DeploymentManager` implementation.
- `strategies.py`: Implementation of Canary, Blue-Green, and Rolling strategies.
- `gitops.py`: Git-based state synchronization logic.
- `verifiers.py`: Deployment health check utilities.

## Deployment Workflow

1. **Plan**: Define target version and strategy.
2. **Pre-flight**: Run verification checks on the new version.
3. **Execute**: Perform the rollout according to the strategy.
4. **Post-flight**: Monitor health and adjust traffic (e.g., in Canary).
5. **Finalize**: Shift 100% traffic or rollback if unhealthy.

## Testing Strategy

- Unit tests for strategy logic (percentage calculations, slot swapping).
- Mocked environment state for end-to-end flow verification.
- Simulation of failure scenarios to test rollback triggers.
