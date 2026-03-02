"""
Deployment orchestration.

Provides a DeploymentOrchestrator that plans, executes, and verifies
deployments using pluggable strategies and health checks.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any

from codomyrmex.deployment.health_checks import HealthChecker, HealthStatus
from codomyrmex.deployment.strategies import (
    DeploymentResult,
    DeploymentState,
    DeploymentStrategy,
    DeploymentTarget,
)


class PlanState(Enum):
    """Lifecycle states of a deployment plan."""
    DRAFT = "draft"
    APPROVED = "approved"
    EXECUTING = "executing"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class DeploymentPlan:
    """A structured plan for a deployment.

    Attributes:
        version: The target version to deploy.
        targets: The set of deployment targets.
        strategy: The deployment strategy to use.
        state: Current lifecycle state of the plan.
        created_at: When the plan was created.
        metadata: Arbitrary extra configuration or notes.
    """
    version: str
    targets: list[DeploymentTarget]
    strategy: DeploymentStrategy
    state: PlanState = PlanState.DRAFT
    created_at: datetime = field(default_factory=datetime.now)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class DeploymentStatus:
    """Current status of the orchestrator.

    Attributes:
        active_plan: The plan currently being executed, or the most recent one.
        last_result: Result of the most recent deployment execution.
        last_health: Overall health status from the most recent verification.
        deployments_completed: Running count of successful deployments.
        deployments_failed: Running count of failed deployments.
    """
    active_plan: DeploymentPlan | None = None
    last_result: DeploymentResult | None = None
    last_health: HealthStatus | None = None
    deployments_completed: int = 0
    deployments_failed: int = 0


class DeploymentOrchestrator:
    """High-level deployment orchestration.

    Coordinates the full deploy lifecycle: plan -> execute -> verify.

    Args:
        health_checker: An optional HealthChecker used during verification.
        deploy_fn: The function called to actually deploy a version to a
                   target.  Signature: ``(target, version) -> bool``.
    """

    def __init__(
        self,
        health_checker: HealthChecker | None = None,
        deploy_fn: Callable[[DeploymentTarget, str], bool] | None = None,
    ) -> None:
        self._health_checker = health_checker
        self._deploy_fn = deploy_fn or self._default_deploy
        self._status = DeploymentStatus()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def plan_deployment(
        self,
        version: str,
        targets: list[DeploymentTarget],
        strategy: DeploymentStrategy,
        metadata: dict[str, Any] | None = None,
    ) -> DeploymentPlan:
        """Create a deployment plan.

        Args:
            version: The version to deploy.
            targets: The list of targets to deploy to.
            strategy: The strategy governing how the deployment proceeds.
            metadata: Optional extra data attached to the plan.

        Returns:
            A new DeploymentPlan in DRAFT state.
        """
        plan = DeploymentPlan(
            version=version,
            targets=targets,
            strategy=strategy,
            metadata=metadata or {},
        )
        self._status.active_plan = plan
        return plan

    def execute_deployment(self, plan: DeploymentPlan) -> DeploymentResult:
        """Execute a deployment plan.

        The plan's state transitions through APPROVED -> EXECUTING ->
        COMPLETED/FAILED.

        Args:
            plan: The deployment plan to execute.

        Returns:
            The DeploymentResult from the strategy.

        Raises:
            RuntimeError: If the plan is not in DRAFT or APPROVED state.
        """
        if plan.state not in (PlanState.DRAFT, PlanState.APPROVED):
            raise RuntimeError(
                f"Cannot execute plan in state {plan.state.value}"
            )

        plan.state = PlanState.EXECUTING
        result = plan.strategy.deploy(
            targets=plan.targets,
            version=plan.version,
            deploy_fn=self._deploy_fn,
        )

        if result.success:
            plan.state = PlanState.COMPLETED
            self._status.deployments_completed += 1
        else:
            plan.state = PlanState.FAILED
            self._status.deployments_failed += 1

        self._status.last_result = result
        return result

    def verify_deployment(self) -> HealthStatus:
        """Run health checks against the current deployment.

        If no HealthChecker was provided at construction time the method
        returns ``HealthStatus.HEALTHY`` optimistically.

        Returns:
            The overall HealthStatus.
        """
        if self._health_checker is None:
            self._status.last_health = HealthStatus.HEALTHY
            return HealthStatus.HEALTHY

        aggregated = self._health_checker.run_all()
        self._status.last_health = aggregated.overall_status
        return aggregated.overall_status

    def get_deployment_status(self) -> DeploymentStatus:
        """Return the current orchestrator status.

        Returns:
            A DeploymentStatus snapshot.
        """
        return self._status

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    @staticmethod
    def _default_deploy(target: DeploymentTarget, version: str) -> bool:
        """Default no-op deploy function (always succeeds)."""
        target.version = version
        return True

    def __repr__(self) -> str:
        """repr ."""
        return (
            f"DeploymentOrchestrator("
            f"completed={self._status.deployments_completed}, "
            f"failed={self._status.deployments_failed})"
        )


__all__ = [
    "DeploymentOrchestrator",
    "DeploymentPlan",
    "DeploymentStatus",
    "PlanState",
]
