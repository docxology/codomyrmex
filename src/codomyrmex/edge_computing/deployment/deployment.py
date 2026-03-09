"""Deployment strategies for edge functions.

Supports blue-green, canary, and rolling deployment patterns.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import TYPE_CHECKING, Any

from codomyrmex.edge_computing.core.models import EdgeFunction, EdgeNodeStatus
from codomyrmex.logging_monitoring import get_logger

logger = get_logger(__name__)

if TYPE_CHECKING:
    from codomyrmex.edge_computing.core.cluster import EdgeCluster


class DeploymentStrategy(Enum):
    """Available deployment strategies."""

    ROLLING = "rolling"
    BLUE_GREEN = "blue_green"
    CANARY = "canary"


class DeploymentState(Enum):
    """State of a deployment."""

    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    ROLLED_BACK = "rolled_back"
    FAILED = "failed"


@dataclass
class DeploymentPlan:
    """A planned deployment of a function across edge nodes."""

    function: EdgeFunction
    strategy: DeploymentStrategy
    target_nodes: list[str] = field(default_factory=list)
    canary_percent: int = 10
    rollback_on_error: bool = True
    state: DeploymentState = DeploymentState.PENDING
    deployed_nodes: list[str] = field(default_factory=list)
    failed_nodes: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)


class DeploymentManager:
    """Manage function deployments across an edge cluster."""

    def __init__(self, cluster: EdgeCluster):
        self._cluster = cluster
        self._deployments: list[DeploymentPlan] = []

    def create_plan(
        self,
        function: EdgeFunction,
        strategy: DeploymentStrategy = DeploymentStrategy.ROLLING,
        target_nodes: list[str] | None = None,
        canary_percent: int = 10,
    ) -> DeploymentPlan:
        """Create a deployment plan."""
        nodes = target_nodes or [
            n.id for n in self._cluster.list_nodes(status=EdgeNodeStatus.ONLINE)
        ]
        plan = DeploymentPlan(
            function=function,
            strategy=strategy,
            target_nodes=nodes,
            canary_percent=canary_percent,
        )
        self._deployments.append(plan)
        return plan

    def execute(self, plan: DeploymentPlan) -> DeploymentPlan:
        """Execute a deployment plan using the chosen strategy."""
        plan.state = DeploymentState.IN_PROGRESS

        if plan.strategy == DeploymentStrategy.ROLLING:
            return self._rolling_deploy(plan)
        if plan.strategy == DeploymentStrategy.BLUE_GREEN:
            return self._blue_green_deploy(plan)
        if plan.strategy == DeploymentStrategy.CANARY:
            return self._canary_deploy(plan)

        plan.state = DeploymentState.FAILED
        return plan

    def rollback(self, plan: DeploymentPlan) -> int:
        """Rollback a deployment — undeploy from all deployed nodes."""
        count = 0
        for node_id in plan.deployed_nodes:
            runtime = self._cluster.get_runtime(node_id)
            if runtime and runtime.undeploy(plan.function.id):
                count += 1
        plan.state = DeploymentState.ROLLED_BACK
        return count

    def list_deployments(self) -> list[DeploymentPlan]:
        return list(self._deployments)

    def get_deployment_status(self, function_id: str) -> dict[str, Any]:
        """Get the current deployment status of a function across the cluster."""
        deployed_nodes = []
        for node in self._cluster.list_nodes():
            runtime = self._cluster.get_runtime(node.id)
            if runtime and any(f.id == function_id for f in runtime.list_functions()):
                deployed_nodes.append(node.id)

        return {
            "function_id": function_id,
            "deployed_node_count": len(deployed_nodes),
            "deployed_nodes": deployed_nodes,
            "target_node_count": self._cluster.node_count,
        }

    # --- Strategy implementations ---

    def _deploy_node(
        self, plan: DeploymentPlan, node_id: str, *, stop_on_error: bool
    ) -> bool:
        """Deploy to a single node; return False if caller should abort iteration.

        When *stop_on_error* is True and an error occurs, triggers rollback and
        signals the caller to halt by returning False.  When False, the node is
        recorded as failed and the caller continues to the next node.
        """
        runtime = self._cluster.get_runtime(node_id)
        if not runtime:
            logger.warning("No runtime found for node %s; skipping", node_id)
            plan.failed_nodes.append(node_id)
            if stop_on_error and plan.rollback_on_error:
                self.rollback(plan)
                plan.state = DeploymentState.ROLLED_BACK
                return False
            return True
        try:
            runtime.deploy(plan.function)
            plan.deployed_nodes.append(node_id)
        except Exception as exc:
            logger.warning("Deploy to node %s failed: %s", node_id, exc)
            plan.failed_nodes.append(node_id)
            if stop_on_error and plan.rollback_on_error:
                self.rollback(plan)
                plan.state = DeploymentState.ROLLED_BACK
                return False
        return True

    def _finalise_state(self, plan: DeploymentPlan) -> None:
        """Set terminal state based on whether any nodes failed."""
        plan.state = (
            DeploymentState.COMPLETED
            if not plan.failed_nodes
            else DeploymentState.FAILED
        )

    def _rolling_deploy(self, plan: DeploymentPlan) -> DeploymentPlan:
        """Deploy one node at a time, stop on failure if rollback enabled."""
        for node_id in plan.target_nodes:
            if not self._deploy_node(plan, node_id, stop_on_error=True):
                return plan
        self._finalise_state(plan)
        return plan

    def _blue_green_deploy(self, plan: DeploymentPlan) -> DeploymentPlan:
        """Deploy to all targets simultaneously (blue-green swap).

        In a real system this would deploy to the 'green' set while 'blue'
        remains active, then swap traffic. Here we simulate by deploying to
        all nodes at once.
        """
        for node_id in plan.target_nodes:
            self._deploy_node(plan, node_id, stop_on_error=False)

        if plan.failed_nodes and plan.rollback_on_error:
            self.rollback(plan)
            plan.state = DeploymentState.ROLLED_BACK
        else:
            self._finalise_state(plan)
        return plan

    def _canary_deploy(self, plan: DeploymentPlan) -> DeploymentPlan:
        """Deploy to a canary subset first, then the rest.

        Canary size is determined by ``canary_percent``.
        """
        total = len(plan.target_nodes)
        canary_count = max(1, total * plan.canary_percent // 100)
        canary_nodes = plan.target_nodes[:canary_count]
        remaining_nodes = plan.target_nodes[canary_count:]

        # Phase 1: canary — stop immediately on failure
        for node_id in canary_nodes:
            if not self._deploy_node(plan, node_id, stop_on_error=True):
                return plan

        plan.metadata["canary_nodes"] = canary_nodes
        plan.metadata["canary_complete"] = True

        # Phase 2: remaining — continue past failures (canary already validated)
        for node_id in remaining_nodes:
            self._deploy_node(plan, node_id, stop_on_error=False)

        self._finalise_state(plan)
        return plan
