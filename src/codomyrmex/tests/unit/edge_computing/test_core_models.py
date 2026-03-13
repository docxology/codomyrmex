"""Tests for edge_computing.core.models."""

import time

from codomyrmex.edge_computing.core.models import (
    EdgeDeployment,
    EdgeExecutionError,
    EdgeFunction,
    EdgeNode,
    EdgeNodeStatus,
    ResourceUsage,
    SyncState,
)


class TestEdgeNodeStatus:
    def test_all_values(self):
        values = {s.value for s in EdgeNodeStatus}
        assert "online" in values
        assert "offline" in values
        assert "degraded" in values
        assert "syncing" in values
        assert "maintenance" in values


class TestResourceUsage:
    def test_defaults(self):
        r = ResourceUsage()
        assert r.cpu_percent == 0.0
        assert r.memory_mb == 0.0
        assert r.memory_max_mb == 0.0
        assert r.active_functions == 0

    def test_memory_percent_zero_max(self):
        r = ResourceUsage(memory_mb=100.0, memory_max_mb=0.0)
        assert r.memory_percent == 0.0

    def test_memory_percent_computed(self):
        r = ResourceUsage(memory_mb=512.0, memory_max_mb=1024.0)
        assert r.memory_percent == 50.0

    def test_is_overloaded_high_cpu(self):
        r = ResourceUsage(cpu_percent=95.0)
        assert r.is_overloaded is True

    def test_is_overloaded_high_memory(self):
        r = ResourceUsage(memory_mb=950.0, memory_max_mb=1000.0)
        assert r.is_overloaded is True

    def test_not_overloaded_normal(self):
        r = ResourceUsage(cpu_percent=50.0, memory_mb=400.0, memory_max_mb=1000.0)
        assert r.is_overloaded is False

    def test_update_usage_clamps_cpu(self):
        r = ResourceUsage()
        r.update_usage(cpu=150.0, mem=0.0)
        assert r.cpu_percent == 100.0

    def test_update_usage_clamps_negative_cpu(self):
        r = ResourceUsage()
        r.update_usage(cpu=-10.0, mem=0.0)
        assert r.cpu_percent == 0.0

    def test_update_usage_clamps_memory(self):
        r = ResourceUsage(memory_max_mb=512.0)
        r.update_usage(cpu=50.0, mem=1000.0)
        assert r.memory_mb == 512.0

    def test_update_usage_disk(self):
        r = ResourceUsage()
        r.update_usage(cpu=50.0, mem=100.0, disk=200.0)
        assert r.disk_mb == 200.0


class TestEdgeNode:
    def test_construction(self):
        node = EdgeNode(id="n1", name="Edge Node 1")
        assert node.id == "n1"
        assert node.status == EdgeNodeStatus.ONLINE

    def test_heartbeat_updates_time(self):
        node = EdgeNode(id="n1", name="n1")
        time.sleep(0.01)
        node.heartbeat()
        assert node.seconds_since_heartbeat < 0.5

    def test_heartbeat_updates_status(self):
        node = EdgeNode(id="n1", name="n1", status=EdgeNodeStatus.DEGRADED)
        node.heartbeat(status=EdgeNodeStatus.ONLINE)
        assert node.status == EdgeNodeStatus.ONLINE

    def test_heartbeat_no_status_sets_online(self):
        node = EdgeNode(id="n1", name="n1", status=EdgeNodeStatus.DEGRADED)
        node.heartbeat()
        assert node.status == EdgeNodeStatus.ONLINE

    def test_is_healthy_recent_heartbeat(self):
        node = EdgeNode(id="n1", name="n1", status=EdgeNodeStatus.ONLINE)
        node.heartbeat()
        assert node.is_healthy is True

    def test_has_capability_true(self):
        node = EdgeNode(id="n1", name="n1", capabilities=["gpu", "tpu"])
        assert node.has_capability("gpu") is True

    def test_has_capability_false(self):
        node = EdgeNode(id="n1", name="n1", capabilities=["cpu"])
        assert node.has_capability("gpu") is False

    def test_to_dict_keys(self):
        node = EdgeNode(id="n1", name="Node1", location="us-east-1")
        d = node.to_dict()
        assert d["id"] == "n1"
        assert d["name"] == "Node1"
        assert d["location"] == "us-east-1"
        assert "status" in d
        assert "healthy" in d
        assert "seconds_since_heartbeat" in d

    def test_not_healthy_when_offline(self):
        node = EdgeNode(id="n1", name="n1", status=EdgeNodeStatus.OFFLINE)
        assert node.is_healthy is False

    def test_seconds_since_heartbeat_positive(self):
        node = EdgeNode(id="n1", name="n1")
        assert node.seconds_since_heartbeat >= 0.0


class TestEdgeFunction:
    def test_construction(self):
        fn = EdgeFunction(id="f1", name="my_fn", handler=lambda: None)
        assert fn.id == "f1"
        assert fn.memory_mb == 128
        assert fn.timeout_seconds == 30

    def test_can_run_on_no_requirements(self):
        node = EdgeNode(id="n1", name="n1")
        fn = EdgeFunction(id="f1", name="fn", handler=lambda: None)
        assert fn.can_run_on(node) is True

    def test_can_run_on_with_matching_capabilities(self):
        node = EdgeNode(id="n1", name="n1", capabilities=["gpu", "fast-storage"])
        fn = EdgeFunction(
            id="f1", name="fn", handler=lambda: None, required_capabilities=["gpu"]
        )
        assert fn.can_run_on(node) is True

    def test_cannot_run_on_missing_capability(self):
        node = EdgeNode(id="n1", name="n1", capabilities=["cpu"])
        fn = EdgeFunction(
            id="f1", name="fn", handler=lambda: None, required_capabilities=["gpu"]
        )
        assert fn.can_run_on(node) is False


class TestEdgeDeployment:
    def test_construction(self):
        d = EdgeDeployment(function_id="f1", node_id="n1")
        assert d.function_id == "f1"
        assert d.node_id == "n1"
        assert d.active is True
        assert d.invocations == 0

    def test_record_invocation(self):
        d = EdgeDeployment(function_id="f1", node_id="n1")
        d.record_invocation()
        d.record_invocation()
        assert d.invocations == 2


class TestSyncState:
    def test_from_data_creates_checksum(self):
        ss = SyncState.from_data({"key": "value"}, version=1)
        assert ss.version == 1
        assert ss.data == {"key": "value"}
        assert len(ss.checksum) == 32  # MD5 hex

    def test_verify_valid(self):
        ss = SyncState.from_data({"x": 1}, version=1)
        assert ss.verify() is True

    def test_verify_tampered(self):
        ss = SyncState.from_data({"x": 1}, version=1)
        ss.data["x"] = 999  # tamper without updating checksum
        assert ss.verify() is False

    def test_checksum_deterministic(self):
        ss1 = SyncState.from_data({"a": 1, "b": 2}, version=1)
        ss2 = SyncState.from_data({"b": 2, "a": 1}, version=1)
        # json.dumps with sort_keys=True ensures same checksum regardless of dict order
        assert ss1.checksum == ss2.checksum


class TestEdgeExecutionError:
    def test_is_exception(self):
        e = EdgeExecutionError("execution failed")
        assert isinstance(e, Exception)
        assert "execution failed" in str(e)
