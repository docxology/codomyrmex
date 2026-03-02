"""Edge node cluster management with drain, rebalance, and monitoring.

Provides:
- EdgeCluster: multi-node orchestration (register/deregister/heartbeat)
- Function deploy/undeploy across nodes
- Node draining (graceful removal)
- Load-aware scheduling (deploy to least-loaded node)
- Cluster health overview
"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from .models import EdgeFunction, EdgeNode, EdgeNodeStatus
from .runtime import EdgeRuntime


class EdgeCluster:
    """Manage a cluster of edge nodes with function deployment and monitoring.

    Example::

        cluster = EdgeCluster()
        node = EdgeNode(id="edge-1", region="us-west")
        cluster.register_node(node)
        fn = EdgeFunction(id="hello", handler=lambda: "hi")
        cluster.deploy_to_all(fn)
        cluster.heartbeat("edge-1")
        print(cluster.health())
    """

    def __init__(self) -> None:
        self._nodes: dict[str, EdgeNode] = {}
        self._runtimes: dict[str, EdgeRuntime] = {}
        self._draining: set[str] = set()

    # ── Node lifecycle ──────────────────────────────────────────────

    def register_node(self, node: EdgeNode) -> None:
        """Register an edge node in the cluster."""
        self._nodes[node.id] = node
        self._runtimes[node.id] = EdgeRuntime(node)

    def deregister_node(self, node_id: str) -> bool:
        """Deregister a node from the cluster."""
        if node_id in self._nodes:
            del self._nodes[node_id]
            del self._runtimes[node_id]
            self._draining.discard(node_id)
            return True
        return False

    def get_node(self, node_id: str) -> EdgeNode | None:
        return self._nodes.get(node_id)

    def get_runtime(self, node_id: str) -> EdgeRuntime | None:
        return self._runtimes.get(node_id)

    def list_nodes(self, status: EdgeNodeStatus | None = None) -> list[EdgeNode]:
        """List nodes, optionally filtered by status."""
        nodes = list(self._nodes.values())
        if status:
            nodes = [n for n in nodes if n.status == status]
        return nodes

    # ── Heartbeat / Health ──────────────────────────────────────────

    def heartbeat(self, node_id: str) -> None:
        """Update node heartbeat timestamp and mark online."""
        if node_id in self._nodes:
            self._nodes[node_id].last_heartbeat = datetime.now(UTC)
            self._nodes[node_id].status = EdgeNodeStatus.ONLINE

    def mark_offline(self, node_id: str) -> None:
        """Mark a node as offline."""
        if node_id in self._nodes:
            self._nodes[node_id].status = EdgeNodeStatus.OFFLINE

    def detect_stale_nodes(self, timeout_seconds: float = 60.0) -> list[str]:
        """Find nodes whose heartbeat is older than timeout.

        Returns:
            List of stale node IDs.
        """
        now = datetime.now()
        stale = []
        for nid, node in self._nodes.items():
            if hasattr(node, "last_heartbeat") and node.last_heartbeat:
                delta = (now - node.last_heartbeat).total_seconds()
                if delta > timeout_seconds:
                    stale.append(nid)
        return stale

    # ── Function deployment ─────────────────────────────────────────

    def deploy_to_all(self, function: EdgeFunction) -> int:
        """Deploy a function to all active (non-draining) nodes."""
        count = 0
        for nid, runtime in self._runtimes.items():
            if nid not in self._draining:
                runtime.deploy(function)
                count += 1
        return count

    def deploy_to_node(self, node_id: str, function: EdgeFunction) -> bool:
        """Deploy a function to a specific node."""
        runtime = self._runtimes.get(node_id)
        if runtime and node_id not in self._draining:
            runtime.deploy(function)
            return True
        return False

    def deploy_least_loaded(self, function: EdgeFunction) -> str | None:
        """Deploy function to the node with fewest deployed functions.

        Returns:
            The node_id where function was deployed, or None.
        """
        best_nid = None
        best_count = float("inf")
        for nid, runtime in self._runtimes.items():
            if nid not in self._draining:
                fc = runtime.function_count
                if fc < best_count:
                    best_count = fc
                    best_nid = nid
        if best_nid:
            self._runtimes[best_nid].deploy(function)
        return best_nid

    def undeploy_from_all(self, function_id: str) -> int:
        """Remove a function from all nodes."""
        count = 0
        for runtime in self._runtimes.values():
            if runtime.undeploy(function_id):
                count += 1
        return count

    # ── Draining ────────────────────────────────────────────────────

    def drain_node(self, node_id: str) -> bool:
        """Start draining a node — no new deploys, existing functions remain.

        Returns:
            True if the node exists and was marked for draining.
        """
        if node_id in self._nodes:
            self._draining.add(node_id)
            return True
        return False

    def is_draining(self, node_id: str) -> bool:
        return node_id in self._draining

    def undrain_node(self, node_id: str) -> bool:
        if node_id in self._draining:
            self._draining.discard(node_id)
            return True
        return False

    # ── Cluster overview ────────────────────────────────────────────

    @property
    def node_count(self) -> int:
        return len(self._nodes)

    @property
    def online_count(self) -> int:
        return sum(1 for n in self._nodes.values() if n.status == EdgeNodeStatus.ONLINE)

    def health(self) -> dict[str, Any]:
        """Return cluster health summary."""
        total_functions = sum(r.function_count for r in self._runtimes.values())
        total_invocations = sum(r.total_invocations for r in self._runtimes.values())
        return {
            "total_nodes": self.node_count,
            "online": self.online_count,
            "draining": len(self._draining),
            "total_functions": total_functions,
            "total_invocations": total_invocations,
            "nodes": [
                {
                    "id": nid,
                    "status": node.status.value if hasattr(node.status, "value") else str(node.status),
                    "functions": self._runtimes[nid].function_count,
                    "draining": nid in self._draining,
                }
                for nid, node in self._nodes.items()
            ],
        }
