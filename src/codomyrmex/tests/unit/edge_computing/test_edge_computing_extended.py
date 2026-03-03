"""Extended unit tests for edge_computing module.

Focuses on resource management, rebalancing, delta sync, and scheduling.
Strictly zero-mock.
"""

import time
from datetime import UTC, datetime, timedelta

import pytest

from codomyrmex.edge_computing import (
    EdgeCluster,
    EdgeFunction,
    EdgeNode,
    EdgeSynchronizer,
)
from codomyrmex.edge_computing.infrastructure import EdgeCache, HealthMonitor
from codomyrmex.edge_computing.scheduling import EdgeScheduler, ScheduleType


@pytest.mark.unit
class TestEdgeResourceManagement:
    def test_node_resource_update(self):
        node = EdgeNode(id="n1", name="test")
        node.resources.memory_max_mb = 1000
        node.resources.update_usage(cpu=50.0, mem=200.0)

        assert node.resources.cpu_percent == 50.0
        assert node.resources.memory_mb == 200.0
        assert node.resources.memory_percent == 20.0
        assert not node.resources.is_overloaded

    def test_node_overload_status(self):
        node = EdgeNode(id="n1", name="test")
        node.resources.memory_max_mb = 1000
        node.resources.update_usage(cpu=95.0, mem=100.0)
        assert node.resources.is_overloaded


@pytest.mark.unit
class TestClusterRebalancing:
    def test_rebalance_cluster(self):
        cluster = EdgeCluster()

        # Node A is overloaded
        node_a = EdgeNode(id="a", name="Node A")
        node_a.resources.memory_max_mb = 100
        node_a.resources.update_usage(cpu=95.0, mem=10.0)
        cluster.register_node(node_a)

        # Node B is healthy
        node_b = EdgeNode(id="b", name="Node B")
        node_b.resources.memory_max_mb = 1000
        node_b.resources.update_usage(cpu=10.0, mem=10.0)
        cluster.register_node(node_b)

        # Deploy to Node A
        func = EdgeFunction(id="f1", name="f1", handler=lambda: 1)
        cluster.deploy_to_node("a", func)

        assert cluster.get_runtime("a").function_count == 1
        assert cluster.get_runtime("b").function_count == 0

        # Rebalance
        moves = cluster.rebalance_cluster()
        assert moves == 1
        assert cluster.get_runtime("a").function_count == 0
        assert cluster.get_runtime("b").function_count == 1


@pytest.mark.unit
class TestDeltaSynchronization:
    def test_delta_update_local(self):
        sync = EdgeSynchronizer()
        sync.update_local({"a": 1, "b": 2})

        # Apply delta
        sync.update_local({"b": 3, "c": 4}, is_delta=True)

        state = sync.get_local_state()
        assert state.version == 2
        assert state.data == {"a": 1, "b": 3, "c": 4}


@pytest.mark.unit
class TestAdvancedHealthMonitoring:
    def test_recovery_recommendations(self):
        monitor = HealthMonitor(heartbeat_timeout_seconds=1.0)
        node = EdgeNode(id="n1", name="test")

        # Initially healthy
        monitor.check_node(node)
        assert monitor.get_recovery_recommendation("n1") == "Normal"

        # Make stale
        node.last_heartbeat = datetime.now(UTC) - timedelta(seconds=10)
        monitor.check_node(node)
        assert (
            monitor.get_recovery_recommendation("n1")
            == "Investigate connectivity (stale heartbeat)"
        )


@pytest.mark.unit
class TestEdgeSchedulerExecution:
    def test_scheduler_execute_tick(self):
        cluster = EdgeCluster()
        node = EdgeNode(id="n1", name="test")
        cluster.register_node(node)

        func = EdgeFunction(id="echo", name="echo", handler=lambda: "hello")
        cluster.deploy_to_node("n1", func)

        scheduler = EdgeScheduler()
        scheduler.add_job(
            job_id="j1",
            function_id="echo",
            schedule_type=ScheduleType.INTERVAL,
            interval_seconds=0.1,
        )

        # First tick should execute
        count = scheduler.execute_tick(cluster)
        assert count == 1
        job = scheduler.get_job("j1")
        assert job.run_count == 1
        assert job.next_run > datetime.now(UTC)

        # Second tick immediately after shouldn't execute because of interval
        count = scheduler.execute_tick(cluster)
        assert count == 0


@pytest.mark.unit
class TestEdgeCacheAdvanced:
    def test_lru_eviction_with_tie_break(self):
        # Small cache
        cache = EdgeCache(max_size=2)
        cache.put("k1", "v1")
        time.sleep(0.01)  # Ensure different created_at
        cache.put("k2", "v2")

        # Access k2, so k1 is least accessed
        cache.get("k2")

        # Put k3, should evict k1
        cache.put("k3", "v3")

        assert cache.get("k1") is None
        assert cache.get("k2") == "v2"
        assert cache.get("k3") == "v3"
