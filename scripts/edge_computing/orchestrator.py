#!/usr/bin/env python3
"""Edge Computing Orchestrator Example.

Demonstrates the full lifecycle of edge node management, function deployment,
state synchronization, and monitoring.
"""

import time
from codomyrmex.edge_computing import (
    EdgeCluster,
    EdgeNode,
    EdgeFunction,
    EdgeSynchronizer,
    SyncState,
    EdgeMetrics,
    InvocationRecord,
    DeploymentManager,
    DeploymentStrategy,
)
from codomyrmex.edge_computing.scheduling import EdgeScheduler
from codomyrmex.logging_monitoring.core.logger_config import get_logger

logger = get_logger(__name__)

def main():
    # Auto-injected: Load configuration
    import yaml
    from pathlib import Path
    config_path = Path(__file__).resolve().parent.parent.parent / "config" / "edge_computing" / "config.yaml"
    config_data = {}
    if config_path.exists():
        with open(config_path, "r") as f:
            config_data = yaml.safe_load(f) or {}
            print(f"Loaded config from config/edge_computing/config.yaml")

    print("--- Edge Computing Orchestrator Starting ---")

    # 1. Initialize Cluster and Infrastructure
    cluster = EdgeCluster()
    metrics = EdgeMetrics()
    scheduler = EdgeScheduler()
    deploy_manager = DeploymentManager(cluster)

    # 2. Register Edge Nodes
    print("\n[1/5] Registering edge nodes...")
    nodes = [
        EdgeNode(id="edge-east-01", name="East Gateway", location="New York", capabilities=["gpu", "storage"]),
        EdgeNode(id="edge-west-01", name="West Gateway", location="San Francisco", capabilities=["camera"]),
        EdgeNode(id="edge-central-01", name="Central Hub", location="Chicago", capabilities=["storage"]),
    ]
    for node in nodes:
        cluster.register_node(node)
        print(f"  Registered: {node.name} ({node.id}) at {node.location}")

    # 3. Define and Deploy Edge Functions
    print("\n[2/5] Deploying functions...")

    def process_image(image_data):
        """Simulate image processing."""
        return {"processed": True, "objects": ["person", "car"], "latency_ms": 12.5}

    def aggregate_metrics(data):
        """Simulate metrics aggregation."""
        return {"count": len(data), "average": sum(data)/len(data) if data else 0}

    img_func = EdgeFunction(
        id="img-proc",
        name="Image Processor",
        handler=process_image,
        required_capabilities=["camera"]
    )

    agg_func = EdgeFunction(
        id="metric-agg",
        name="Metric Aggregator",
        handler=aggregate_metrics,
        memory_mb=256
    )

    # Deploy Image Processor to nodes with 'camera' capability
    for node in cluster.list_nodes():
        if img_func.can_run_on(node):
            cluster.deploy_to_node(node.id, img_func)
            print(f"  Deployed '{img_func.name}' to {node.id}")

    # Deploy Metric Aggregator using Canary strategy to all nodes
    plan = deploy_manager.create_plan(
        agg_func,
        strategy=DeploymentStrategy.CANARY,
        canary_percent=33
    )
    deploy_manager.execute(plan)
    print(f"  Deployed '{agg_func.name}' via CANARY strategy. Status: {plan.state.value}")

    # 4. Execute and Track Invocations
    print("\n[3/5] Executing functions and tracking metrics...")

    # Invoke on a specific node
    runtime = cluster.get_runtime("edge-east-01")
    if runtime:
        try:
            start_time = time.time()
            result = runtime.invoke("metric-agg", [10, 20, 30, 40])
            duration = (time.time() - start_time) * 1000

            metrics.record(InvocationRecord(
                function_id="metric-agg",
                node_id="edge-east-01",
                duration_ms=duration,
                success=True
            ))
            print(f"  Invocation 'metric-agg' on edge-east-01: {result}")
        except Exception as e:
            print(f"  Invocation failed: {e}")

    # 5. State Synchronization
    print("\n[4/5] Synchronizing state...")
    sync = EdgeSynchronizer()
    local_update = sync.update_local({"last_seen": time.time(), "status": "active"})
    print(f"  Local state updated to version {local_update.version}")

    # Simulate remote update
    remote_state = SyncState.from_data(
        {"last_seen": time.time(), "status": "active", "remote_config": "v2"},
        version=10
    )
    if sync.apply_remote(remote_state):
        print(f"  Remote state applied. New local version: {sync.local_version}")

    # 6. Cluster Health and Summary
    print("\n[5/5] Final Cluster Status:")
    health = cluster.health()
    print(f"  Total Nodes: {health['total_nodes']}")
    print(f"  Online Nodes: {health['online']}")
    print(f"  Total Functions Deployed: {health['total_functions']}")

    m_summary = metrics.summary()
    print(f"  Metrics: {m_summary['total']} total calls, {m_summary['success_rate']}% success")

    print("\n--- Edge Computing Orchestrator Finished ---")

if __name__ == "__main__":
    main()
