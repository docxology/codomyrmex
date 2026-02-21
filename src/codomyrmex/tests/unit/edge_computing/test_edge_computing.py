"""Tests for edge_computing module."""

from datetime import datetime, timezone

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
    from codomyrmex.edge_computing.metrics import EdgeMetrics, InvocationRecord

    HAS_MODULE = True
except ImportError:
    HAS_MODULE = False

if not HAS_MODULE:
    pytest.skip("edge_computing module not available", allow_module_level=True)


# ---------------------------------------------------------------------------
# Original 14 tests (preserved exactly)
# ---------------------------------------------------------------------------


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


# ---------------------------------------------------------------------------
# Deep behavioral tests
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestSyncStateFromData:
    """Deep tests for SyncState.from_data class method."""

    def test_from_data_generates_valid_checksum(self):
        state = SyncState.from_data({"key": "value"}, version=1)
        assert isinstance(state.checksum, str)
        assert len(state.checksum) == 32  # MD5 hex digest length

    def test_same_data_produces_same_checksum(self):
        state_a = SyncState.from_data({"key": "value"}, version=1)
        state_b = SyncState.from_data({"key": "value"}, version=2)
        assert state_a.checksum == state_b.checksum

    def test_different_data_produces_different_checksum(self):
        state_a = SyncState.from_data({"key": "alpha"}, version=1)
        state_b = SyncState.from_data({"key": "beta"}, version=1)
        assert state_a.checksum != state_b.checksum

    def test_from_data_preserves_data_dict(self):
        data = {"nested": {"a": 1}, "list": [1, 2, 3]}
        state = SyncState.from_data(data, version=5)
        assert state.data == data

    def test_from_data_sets_updated_at(self):
        before = datetime.now(timezone.utc)
        state = SyncState.from_data({"x": 1}, version=1)
        after = datetime.now(timezone.utc)
        assert before <= state.updated_at <= after


@pytest.mark.unit
class TestEdgeSynchronizerLifecycle:
    """Full lifecycle tests for EdgeSynchronizer."""

    def test_initial_local_state_is_none(self):
        sync = EdgeSynchronizer()
        assert sync.get_local_state() is None

    def test_update_local_creates_state(self):
        sync = EdgeSynchronizer()
        state = sync.update_local({"key": "val"})
        assert state.version == 1
        assert state.data == {"key": "val"}

    def test_update_local_increments_version(self):
        sync = EdgeSynchronizer()
        sync.update_local({"a": 1})
        state2 = sync.update_local({"b": 2})
        assert state2.version == 2

    def test_update_local_increments_version_three_times(self):
        sync = EdgeSynchronizer()
        sync.update_local({"a": 1})
        sync.update_local({"b": 2})
        state3 = sync.update_local({"c": 3})
        assert state3.version == 3

    def test_apply_remote_with_newer_version_succeeds(self):
        sync = EdgeSynchronizer()
        sync.update_local({"old": True})
        remote = SyncState.from_data({"new": True}, version=10)
        result = sync.apply_remote(remote)
        assert result is True
        assert sync.get_local_state().version == 10
        assert sync.get_local_state().data == {"new": True}

    def test_apply_remote_with_older_version_rejected(self):
        sync = EdgeSynchronizer()
        sync.update_local({"a": 1})
        sync.update_local({"b": 2})
        sync.update_local({"c": 3})  # version 3
        old_remote = SyncState.from_data({"stale": True}, version=1)
        result = sync.apply_remote(old_remote)
        assert result is False
        assert sync.get_local_state().version == 3

    def test_apply_remote_with_equal_version_rejected(self):
        sync = EdgeSynchronizer()
        sync.update_local({"a": 1})  # version 1
        equal_remote = SyncState.from_data({"equal": True}, version=1)
        result = sync.apply_remote(equal_remote)
        assert result is False

    def test_apply_remote_when_no_local_state(self):
        sync = EdgeSynchronizer()
        remote = SyncState.from_data({"first": True}, version=5)
        result = sync.apply_remote(remote)
        assert result is True
        assert sync.get_local_state().version == 5

    def test_pending_changes_tracked(self):
        sync = EdgeSynchronizer()
        sync.update_local({"a": 1})
        sync.update_local({"b": 2})
        pending = sync.get_pending_changes()
        assert len(pending) == 2
        assert pending[0]["version"] == 1
        assert pending[1]["version"] == 2
        assert pending[0]["type"] == "update"

    def test_confirm_sync_clears_confirmed_changes(self):
        sync = EdgeSynchronizer()
        sync.update_local({"a": 1})
        sync.update_local({"b": 2})
        sync.update_local({"c": 3})
        sync.confirm_sync(up_to_version=2)
        pending = sync.get_pending_changes()
        assert len(pending) == 1
        assert pending[0]["version"] == 3

    def test_confirm_sync_all_clears_everything(self):
        sync = EdgeSynchronizer()
        sync.update_local({"a": 1})
        sync.update_local({"b": 2})
        sync.confirm_sync(up_to_version=2)
        assert len(sync.get_pending_changes()) == 0

    def test_pending_changes_returns_copy(self):
        sync = EdgeSynchronizer()
        sync.update_local({"a": 1})
        pending = sync.get_pending_changes()
        pending.clear()
        assert len(sync.get_pending_changes()) == 1


@pytest.mark.unit
class TestEdgeRuntimeBehavior:
    """Deep behavioral tests for EdgeRuntime."""

    @pytest.fixture()
    def runtime(self):
        node = EdgeNode(id="rt-node", name="Runtime Test Node")
        return EdgeRuntime(node=node)

    @pytest.fixture()
    def adder_function(self):
        return EdgeFunction(
            id="adder",
            name="Adder",
            handler=lambda a, b: a + b,
        )

    def test_deploy_adds_function(self, runtime, adder_function):
        runtime.deploy(adder_function)
        assert len(runtime.list_functions()) == 1
        assert runtime.list_functions()[0].id == "adder"

    def test_deploy_multiple_functions(self, runtime):
        fn1 = EdgeFunction(id="f1", name="f1", handler=lambda: 1)
        fn2 = EdgeFunction(id="f2", name="f2", handler=lambda: 2)
        runtime.deploy(fn1)
        runtime.deploy(fn2)
        assert len(runtime.list_functions()) == 2

    def test_undeploy_removes_function(self, runtime, adder_function):
        runtime.deploy(adder_function)
        result = runtime.undeploy("adder")
        assert result is True
        assert len(runtime.list_functions()) == 0

    def test_undeploy_nonexistent_returns_false(self, runtime):
        result = runtime.undeploy("nonexistent")
        assert result is False

    def test_invoke_returns_handler_result(self, runtime, adder_function):
        runtime.deploy(adder_function)
        result = runtime.invoke("adder", 3, 7)
        assert result == 10

    def test_invoke_missing_function_raises_value_error(self, runtime):
        with pytest.raises(ValueError, match="Function not found"):
            runtime.invoke("missing-fn")

    def test_invoke_failure_wraps_in_edge_execution_error(self, runtime):
        def broken():
            raise RuntimeError("boom")

        fn = EdgeFunction(id="broken", name="broken", handler=broken)
        runtime.deploy(fn)
        with pytest.raises(EdgeExecutionError, match="boom"):
            runtime.invoke("broken")

    def test_invoke_failure_chains_original_exception(self, runtime):
        def broken():
            raise RuntimeError("original")

        fn = EdgeFunction(id="broken", name="broken", handler=broken)
        runtime.deploy(fn)
        with pytest.raises(EdgeExecutionError) as exc_info:
            runtime.invoke("broken")
        assert isinstance(exc_info.value.__cause__, RuntimeError)

    def test_list_functions_empty_initially(self, runtime):
        assert runtime.list_functions() == []

    def test_invoke_with_kwargs(self, runtime):
        def greeter(name="world"):
            return f"hello {name}"

        fn = EdgeFunction(id="greet", name="greet", handler=greeter)
        runtime.deploy(fn)
        result = runtime.invoke("greet", name="edge")
        assert result == "hello edge"


@pytest.mark.unit
class TestEdgeClusterBehavior:
    """Deep behavioral tests for EdgeCluster."""

    @pytest.fixture()
    def cluster(self):
        return EdgeCluster()

    @pytest.fixture()
    def node_a(self):
        return EdgeNode(id="a", name="Node A", location="US-West")

    @pytest.fixture()
    def node_b(self):
        return EdgeNode(id="b", name="Node B", location="US-East")

    def test_register_node(self, cluster, node_a):
        cluster.register_node(node_a)
        assert cluster.get_node("a") is node_a

    def test_register_creates_runtime(self, cluster, node_a):
        cluster.register_node(node_a)
        rt = cluster.get_runtime("a")
        assert rt is not None
        assert isinstance(rt, EdgeRuntime)

    def test_deregister_node(self, cluster, node_a):
        cluster.register_node(node_a)
        result = cluster.deregister_node("a")
        assert result is True
        assert cluster.get_node("a") is None
        assert cluster.get_runtime("a") is None

    def test_deregister_nonexistent_returns_false(self, cluster):
        result = cluster.deregister_node("ghost")
        assert result is False

    def test_deploy_to_all_deploys_to_all_registered_nodes(
        self, cluster, node_a, node_b
    ):
        cluster.register_node(node_a)
        cluster.register_node(node_b)
        fn = EdgeFunction(id="fn1", name="fn1", handler=lambda: 42)
        count = cluster.deploy_to_all(fn)
        assert count == 2
        rt_a = cluster.get_runtime("a")
        rt_b = cluster.get_runtime("b")
        assert len(rt_a.list_functions()) == 1
        assert len(rt_b.list_functions()) == 1

    def test_deploy_to_all_empty_cluster(self, cluster):
        fn = EdgeFunction(id="fn1", name="fn1", handler=lambda: 42)
        count = cluster.deploy_to_all(fn)
        assert count == 0

    def test_heartbeat_updates_node(self, cluster, node_a):
        node_a.status = EdgeNodeStatus.DEGRADED
        cluster.register_node(node_a)
        before = node_a.last_heartbeat
        cluster.heartbeat("a")
        assert node_a.status == EdgeNodeStatus.ONLINE
        assert node_a.last_heartbeat >= before

    def test_heartbeat_nonexistent_node_no_error(self, cluster):
        cluster.heartbeat("nonexistent")  # should not raise

    def test_list_nodes_returns_all(self, cluster, node_a, node_b):
        cluster.register_node(node_a)
        cluster.register_node(node_b)
        nodes = cluster.list_nodes()
        assert len(nodes) == 2

    def test_list_nodes_with_status_filter(self, cluster, node_a, node_b):
        node_a.status = EdgeNodeStatus.ONLINE
        node_b.status = EdgeNodeStatus.OFFLINE
        cluster.register_node(node_a)
        cluster.register_node(node_b)
        online = cluster.list_nodes(status=EdgeNodeStatus.ONLINE)
        assert len(online) == 1
        assert online[0].id == "a"

    def test_list_nodes_filter_returns_empty_when_none_match(
        self, cluster, node_a
    ):
        node_a.status = EdgeNodeStatus.ONLINE
        cluster.register_node(node_a)
        degraded = cluster.list_nodes(status=EdgeNodeStatus.DEGRADED)
        assert degraded == []

    def test_get_node_missing_returns_none(self, cluster):
        assert cluster.get_node("missing") is None

    def test_get_runtime_missing_returns_none(self, cluster):
        assert cluster.get_runtime("missing") is None

    def test_invoke_through_cluster(self, cluster, node_a):
        cluster.register_node(node_a)
        fn = EdgeFunction(id="echo", name="echo", handler=lambda x: x)
        cluster.deploy_to_all(fn)
        rt = cluster.get_runtime("a")
        result = rt.invoke("echo", "hello")
        assert result == "hello"


# ---------------------------------------------------------------------------
# Metrics tests
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestInvocationRecord:
    """Tests for InvocationRecord dataclass."""

    def test_create_record(self):
        rec = InvocationRecord(
            function_id="fn1",
            node_id="node1",
            duration_ms=42.5,
            success=True,
        )
        assert rec.function_id == "fn1"
        assert rec.node_id == "node1"
        assert rec.duration_ms == 42.5
        assert rec.success is True
        assert isinstance(rec.timestamp, datetime)
        assert rec.error == ""

    def test_create_failed_record(self):
        rec = InvocationRecord(
            function_id="fn1",
            node_id="node1",
            duration_ms=100.0,
            success=False,
            error="timeout",
        )
        assert rec.success is False
        assert rec.error == "timeout"


@pytest.mark.unit
class TestEdgeMetrics:
    """Tests for EdgeMetrics tracking class."""

    @pytest.fixture()
    def metrics(self):
        return EdgeMetrics()

    def _make_record(
        self,
        function_id="fn1",
        node_id="node1",
        duration_ms=10.0,
        success=True,
        error="",
    ):
        return InvocationRecord(
            function_id=function_id,
            node_id=node_id,
            duration_ms=duration_ms,
            success=success,
            error=error,
        )

    def test_record_adds_entry(self, metrics):
        metrics.record(self._make_record())
        assert metrics.total_invocations() == 1

    def test_total_invocations_no_filter(self, metrics):
        metrics.record(self._make_record(function_id="a"))
        metrics.record(self._make_record(function_id="b"))
        assert metrics.total_invocations() == 2

    def test_total_invocations_filter_by_function_id(self, metrics):
        metrics.record(self._make_record(function_id="a"))
        metrics.record(self._make_record(function_id="a"))
        metrics.record(self._make_record(function_id="b"))
        assert metrics.total_invocations(function_id="a") == 2
        assert metrics.total_invocations(function_id="b") == 1

    def test_total_invocations_filter_by_node_id(self, metrics):
        metrics.record(self._make_record(node_id="n1"))
        metrics.record(self._make_record(node_id="n2"))
        metrics.record(self._make_record(node_id="n1"))
        assert metrics.total_invocations(node_id="n1") == 2
        assert metrics.total_invocations(node_id="n2") == 1

    def test_total_invocations_filter_both(self, metrics):
        metrics.record(self._make_record(function_id="a", node_id="n1"))
        metrics.record(self._make_record(function_id="a", node_id="n2"))
        metrics.record(self._make_record(function_id="b", node_id="n1"))
        assert metrics.total_invocations(function_id="a", node_id="n1") == 1

    def test_success_rate_all_success(self, metrics):
        metrics.record(self._make_record(success=True))
        metrics.record(self._make_record(success=True))
        assert metrics.success_rate() == 100.0

    def test_success_rate_mixed(self, metrics):
        metrics.record(self._make_record(success=True))
        metrics.record(self._make_record(success=False))
        assert metrics.success_rate() == 50.0

    def test_success_rate_all_failed(self, metrics):
        metrics.record(self._make_record(success=False))
        metrics.record(self._make_record(success=False))
        assert metrics.success_rate() == 0.0

    def test_success_rate_no_records(self, metrics):
        assert metrics.success_rate() == 100.0

    def test_success_rate_filter_by_function(self, metrics):
        metrics.record(self._make_record(function_id="a", success=True))
        metrics.record(self._make_record(function_id="a", success=False))
        metrics.record(self._make_record(function_id="b", success=True))
        assert metrics.success_rate(function_id="a") == 50.0
        assert metrics.success_rate(function_id="b") == 100.0

    def test_avg_latency_ms(self, metrics):
        metrics.record(self._make_record(duration_ms=10.0))
        metrics.record(self._make_record(duration_ms=30.0))
        assert metrics.avg_latency_ms() == 20.0

    def test_avg_latency_no_records(self, metrics):
        assert metrics.avg_latency_ms() == 0.0

    def test_avg_latency_filter_by_function(self, metrics):
        metrics.record(self._make_record(function_id="a", duration_ms=10.0))
        metrics.record(self._make_record(function_id="a", duration_ms=20.0))
        metrics.record(self._make_record(function_id="b", duration_ms=100.0))
        assert metrics.avg_latency_ms(function_id="a") == 15.0
        assert metrics.avg_latency_ms(function_id="b") == 100.0

    def test_error_count(self, metrics):
        metrics.record(self._make_record(success=True))
        metrics.record(self._make_record(success=False))
        metrics.record(self._make_record(success=False))
        assert metrics.error_count() == 2

    def test_error_count_none(self, metrics):
        metrics.record(self._make_record(success=True))
        assert metrics.error_count() == 0

    def test_error_count_filter_by_node(self, metrics):
        metrics.record(self._make_record(node_id="n1", success=False))
        metrics.record(self._make_record(node_id="n1", success=False))
        metrics.record(self._make_record(node_id="n2", success=False))
        assert metrics.error_count(node_id="n1") == 2
        assert metrics.error_count(node_id="n2") == 1

    def test_summary(self, metrics):
        metrics.record(self._make_record(duration_ms=10.0, success=True))
        metrics.record(self._make_record(duration_ms=20.0, success=False))
        summary = metrics.summary()
        assert summary["total"] == 2
        assert summary["success_rate"] == 50.0
        assert summary["avg_latency"] == 15.0
        assert summary["error_count"] == 1

    def test_summary_empty(self, metrics):
        summary = metrics.summary()
        assert summary["total"] == 0
        assert summary["success_rate"] == 100.0
        assert summary["avg_latency"] == 0.0
        assert summary["error_count"] == 0
