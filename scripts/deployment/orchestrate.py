#!/usr/bin/env python3
"""
Orchestrator for deployment module - demonstrates the improved module functionality.

This script demonstrates:
1. Initializing the DeploymentManager
2. Syncing configuration from Git (simulated)
3. Executing a rolling deployment
4. Performing health checks
5. Executing a canary rollout with analysis
6. Demonstrating a rollback on failure
"""

import sys
from pathlib import Path

# Add src to path if needed
try:
    import codomyrmex  # noqa: F401
except ImportError:
    project_root = Path(__file__).resolve().parent.parent.parent
    sys.path.insert(0, str(project_root / "src"))

from codomyrmex.deployment import (
    CanaryAnalyzer,
    CanaryDecision,
    CanaryStrategy,
    DeploymentManager,
    DeploymentTarget,
    RollingStrategy,
)


def run_orchestration():
    print("🚀 Starting Deployment Orchestration Demo")
    print("=========================================")

    # 1. Initialize Manager
    manager = DeploymentManager()

    # 2. Define Targets
    targets = [
        DeploymentTarget(id="web-01", name="Web Server 01", address="10.0.0.1"),
        DeploymentTarget(id="web-02", name="Web Server 02", address="10.0.0.2"),
        DeploymentTarget(id="web-03", name="Web Server 03", address="10.0.0.3"),
    ]

    print(f"\n📦 Target inventory: {len(targets)} nodes identified.")

    # 3. Rolling Deployment
    print("\n🔄 Step 1: Performing Rolling Deployment of 'api-service' v1.2.0")

    # Create a health checker to be used during deployment
    # (Simulated: in real scenario, this would check the actual target)
    def simple_hc(target):
        print(f"   🔍 Health checking {target.id}...")
        return True

    rolling = RollingStrategy(batch_size=1, delay_seconds=0.1, health_check=simple_hc)
    result = manager.deploy("api-service", "v1.2.0", strategy=rolling, targets=targets)

    if result.success:
        print(f"✅ Rolling deployment completed successfully in {result.duration_ms:.1f}ms")
    else:
        print(f"❌ Rolling deployment failed: {result.errors}")
        return

    # 4. Canary Rollout
    print("\n🐥 Step 2: Starting Canary Rollout of 'api-service' v1.3.0-rc1")

    canary_strat = CanaryStrategy(
        stages=[33.0, 66.0, 100.0],
        stage_duration_seconds=0.1,
        health_check=simple_hc
    )

    # Execute canary rollout
    canary_result = manager.deploy("api-service", "v1.3.0-rc1", strategy=canary_strat, targets=targets)

    if canary_result.success:
        print(f"✅ Canary rollout completed: {canary_result.targets_updated} targets updated.")
    else:
        print(f"⚠️ Canary rollout stopped at stage {canary_result.metadata.get('stopped_at_stage')}%")

    # 5. Canary Analysis
    print("\n📊 Step 3: Analyzing Canary Metrics")
    analyzer = CanaryAnalyzer(promote_threshold=0.8)

    # Simulated metrics
    baseline = {"error_rate": 0.02, "p99_latency": 120}
    canary = {"error_rate": 0.05, "p99_latency": 145}

    report = analyzer.analyze(baseline, canary)
    print(f"   Result: {report.decision.value.upper()} (Pass rate: {report.pass_rate:.1%})")

    for comp in report.comparisons:
        status = "✅" if comp.passed else "❌"
        print(f"   {status} {comp.metric_name}: baseline={comp.baseline_value}, canary={comp.canary_value}")

    # 6. Rollback if needed
    if report.decision == CanaryDecision.ROLLBACK or report.decision == CanaryDecision.CONTINUE:
        print(f"\n🔙 Step 4: Decision is {report.decision.value}, rolling back to v1.2.0")
        rb_result = manager.rollback("api-service", "v1.2.0", strategy=RollingStrategy(batch_size=3), targets=targets)
        if rb_result.success:
            print("✅ Rollback successful. Service restored to v1.2.0")
        else:
            print(f"❌ Rollback failed: {rb_result.errors}")

    # 7. Summary
    print("\n📈 Deployment Summary")
    print("---------------------")
    summary = manager.summary()
    print(f"Total Operations: {summary['total_deployments']}")
    print(f"Completed:        {summary['completed']}")
    print(f"Rolled Back:      {summary['rolled_back']}")
    print(f"Active Services:  {', '.join(summary['active_services'])}")
    print(f"Current Version:  {manager.get_active_version('api-service')}")

    print("\n✨ Orchestration Demo Finished Successfully")



    # Auto-injected: Load configuration
    from pathlib import Path

    import yaml
    config_path = Path(__file__).resolve().parent.parent.parent / "config" / "deployment" / "config.yaml"
    if config_path.exists():
        with open(config_path) as f:
            yaml.safe_load(f) or {}
            print("Loaded config from config/deployment/config.yaml")

if __name__ == "__main__":
    try:
        run_orchestration()
    except KeyboardInterrupt:
        print("\nAborted by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Critical error during orchestration: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
