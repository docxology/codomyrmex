"""Tests for edge_computing module."""

from datetime import datetime

import pytest

try:
    from codomyrmex.edge_computing import (
        EdgeCluster,
        EdgeExecutionError,
        EdgeFunction,
        EdgeNode,
        EdgeNodeStatus,
        EdgeRuntime,
        EdgeSynchronizer,
        SyncState,
    )
    HAS_MODULE = True
except ImportError:
    HAS_MODULE = False

if not HAS_MODULE:
    pytest.skip("edge_computing module not available", allow_module_level=True)


@pytest.mark.unit
class TestEdgeNodeStatus:
    def test_online(self):
        assert EdgeNodeStatus.ONLINE is not None

    def test_offline(self):
        assert EdgeNodeStatus.OFFLINE is not None

    def test_degraded(self):
        assert EdgeNodeStatus.DEGRADED is not None

    def test_syncing(self):
        assert EdgeNodeStatus.SYNCING is not None


@pytest.mark.unit
class TestEdgeNode:
    def test_create_node(self):
        node = EdgeNode(id="node-1", name="Edge US West")
        assert node.id == "node-1"
        assert node.name == "Edge US West"

    def test_node_defaults(self):
        node = EdgeNode(id="n1", name="test")
        assert node.location == ""
        assert node.status == EdgeNodeStatus.ONLINE
        assert node.capabilities == []
        assert isinstance(node.last_heartbeat, datetime)


@pytest.mark.unit
class TestEdgeFunction:
    def test_create_function(self):
        func = EdgeFunction(id="fn-1", name="handler", handler=lambda: None)
        assert func.id == "fn-1"
        assert func.memory_mb == 128
        assert func.timeout_seconds == 30

    def test_function_with_env(self):
        func = EdgeFunction(
            id="fn-2",
            name="worker",
            handler=lambda: None,
            environment={"API_KEY": "test"},
        )
        assert func.environment["API_KEY"] == "test"


@pytest.mark.unit
class TestSyncState:
    def test_create_sync_state(self):
        state = SyncState(version=1, data={"key": "value"}, checksum="abc123")
        assert state.version == 1
        assert state.checksum == "abc123"

    def test_from_data(self):
        state = SyncState.from_data(data={"test": 1}, version=2)
        assert state.version == 2
        assert state.data == {"test": 1}


@pytest.mark.unit
class TestEdgeExecutionError:
    def test_is_exception(self):
        with pytest.raises(EdgeExecutionError):
            raise EdgeExecutionError("execution failed")


@pytest.mark.unit
class TestEdgeSynchronizer:
    def test_create_synchronizer(self):
        sync = EdgeSynchronizer()
        assert sync is not None


@pytest.mark.unit
class TestEdgeRuntime:
    def test_create_runtime(self):
        node = EdgeNode(id="n1", name="test")
        runtime = EdgeRuntime(node=node)
        assert runtime is not None


@pytest.mark.unit
class TestEdgeCluster:
    def test_create_cluster(self):
        cluster = EdgeCluster()
        assert cluster is not None
