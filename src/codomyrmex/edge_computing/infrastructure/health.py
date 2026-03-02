"""Health monitoring for edge nodes.

Tracks heartbeats, detects failures, and provides cluster health reports.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any

from codomyrmex.edge_computing.core.models import EdgeNode, EdgeNodeStatus


@dataclass
class HealthCheck:
    """Result of a single health check."""

    node_id: str
    healthy: bool
    latency_ms: float = 0.0
    checked_at: datetime = field(default_factory=datetime.now)
    details: dict[str, Any] = field(default_factory=dict)


class HealthMonitor:
    """Monitor health of edge nodes in a cluster."""

    def __init__(self, heartbeat_timeout_seconds: float = 60.0):
        self._timeout = timedelta(seconds=heartbeat_timeout_seconds)
        self._checks: dict[str, list[HealthCheck]] = {}
        self._max_history = 100

    def check_node(self, node: EdgeNode) -> HealthCheck:
        """Check the health of a single node based on heartbeat age."""
        now = datetime.now()
        age = now - node.last_heartbeat
        healthy = age < self._timeout and node.status != EdgeNodeStatus.OFFLINE

        result = HealthCheck(
            node_id=node.id,
            healthy=healthy,
            latency_ms=age.total_seconds() * 1000,
            details={
                "status": node.status.value,
                "heartbeat_age_seconds": age.total_seconds(),
                "location": node.location,
            },
        )

        if node.id not in self._checks:
            self._checks[node.id] = []
        self._checks[node.id].append(result)
        if len(self._checks[node.id]) > self._max_history:
            self._checks[node.id] = self._checks[node.id][-self._max_history :]

        return result

    def check_cluster(self, nodes: list[EdgeNode]) -> dict[str, Any]:
        """Check health of all nodes and return a cluster health report."""
        checks = [self.check_node(n) for n in nodes]
        healthy_count = sum(1 for c in checks if c.healthy)
        total = len(checks)

        return {
            "total_nodes": total,
            "healthy_nodes": healthy_count,
            "unhealthy_nodes": total - healthy_count,
            "health_percent": (healthy_count / total * 100.0) if total else 100.0,
            "checks": [
                {
                    "node_id": c.node_id,
                    "healthy": c.healthy,
                    "latency_ms": c.latency_ms,
                }
                for c in checks
            ],
        }

    def get_history(self, node_id: str, limit: int = 10) -> list[HealthCheck]:
        """Get recent health check history for a node."""
        checks = self._checks.get(node_id, [])
        return checks[-limit:]

    def detect_flapping(self, node_id: str, window: int = 10) -> bool:
        """Detect if a node is flapping (alternating healthy/unhealthy).

        Returns True if there were 3+ state transitions in the last
        ``window`` checks.
        """
        history = self.get_history(node_id, limit=window)
        if len(history) < 3:
            return False
        transitions = sum(
            1
            for i in range(1, len(history))
            if history[i].healthy != history[i - 1].healthy
        )
        return transitions >= 3

    def summary(self) -> dict[str, Any]:
        """Overall monitoring summary."""
        total_checks = sum(len(v) for v in self._checks.values())
        node_count = len(self._checks)
        return {
            "monitored_nodes": node_count,
            "total_checks": total_checks,
            "timeout_seconds": self._timeout.total_seconds(),
        }
