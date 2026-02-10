"""Edge node cluster management."""

from datetime import datetime

from .models import EdgeFunction, EdgeNode, EdgeNodeStatus
from .runtime import EdgeRuntime


class EdgeCluster:
    """Manage a cluster of edge nodes."""

    def __init__(self):
        self._nodes: dict[str, EdgeNode] = {}
        self._runtimes: dict[str, EdgeRuntime] = {}

    def register_node(self, node: EdgeNode) -> None:
        """Register an edge node."""
        self._nodes[node.id] = node
        self._runtimes[node.id] = EdgeRuntime(node)

    def deregister_node(self, node_id: str) -> bool:
        """Deregister a node."""
        if node_id in self._nodes:
            del self._nodes[node_id]
            del self._runtimes[node_id]
            return True
        return False

    def get_node(self, node_id: str) -> EdgeNode | None:
        return self._nodes.get(node_id)

    def get_runtime(self, node_id: str) -> EdgeRuntime | None:
        return self._runtimes.get(node_id)

    def list_nodes(self, status: EdgeNodeStatus | None = None) -> list[EdgeNode]:
        nodes = list(self._nodes.values())
        if status:
            nodes = [n for n in nodes if n.status == status]
        return nodes

    def deploy_to_all(self, function: EdgeFunction) -> int:
        """Deploy function to all nodes."""
        count = 0
        for runtime in self._runtimes.values():
            runtime.deploy(function)
            count += 1
        return count

    def heartbeat(self, node_id: str) -> None:
        """Update node heartbeat."""
        if node_id in self._nodes:
            self._nodes[node_id].last_heartbeat = datetime.now()
            self._nodes[node_id].status = EdgeNodeStatus.ONLINE
