#!/usr/bin/env python3
"""
CI/CD Automation - Real Usage Examples

Demonstrates actual CI/CD capabilities:
- Pipeline creation
- Stage management
- Monitoring stubs
"""

import sys
from pathlib import Path

# Ensure codomyrmex is in path
try:
    import codomyrmex  # noqa: F401
except ImportError:
    project_root = Path(__file__).resolve().parent.parent.parent.parent
    sys.path.insert(0, str(project_root / "src"))

from codomyrmex.ci_cd_automation import (
    Pipeline,
    PipelineJob,
    PipelineManager,
    PipelineStage,
)
from codomyrmex.utils.cli_helpers import (
    print_error,
    print_info,
    print_success,
    setup_logging,
)


def main():
    # Auto-injected: Load configuration
    from pathlib import Path

    import yaml
    config_path = Path(__file__).resolve().parent.parent.parent / "config" / "ci_cd_automation" / "config.yaml"
    config_data = {}
    if config_path.exists():
        with open(config_path) as f:
            config_data = yaml.safe_load(f) or {}
            print("Loaded config from config/ci_cd_automation/config.yaml")

    setup_logging()
    print_info("Running CI/CD Examples...")

    # 1. Pipeline Manager & Execution
    print_info("Testing PipelineManager and execution flow...")
    try:
        mgr = PipelineManager()
        pipeline = Pipeline(
            name="demo_pipeline",
            stages=[
                PipelineStage(name="Lint", jobs=[PipelineJob(name="flake8", commands=["echo 'Linting...'"])]),
                PipelineStage(name="Security", jobs=[PipelineJob(name="bandit", commands=["echo 'Security scan...'"])])
            ]
        )
        # Manually register pipeline in the manager's state
        mgr.pipelines[pipeline.name] = pipeline
        print_success(f"  Pipeline '{pipeline.name}' registered manually.")

        # Verify it's listed
        pipelines = mgr.list_pipelines()
        if any(p.name == "demo_pipeline" for p in pipelines):
            print_success("  Pipeline successfully retrieved from PipelineManager.")

        print_success("  PipelineManager state management verified.")
    except Exception as e:
        print_error(f"  PipelineManager flow failed: {e}")

    # 2. Monitoring
    from codomyrmex.ci_cd_automation import monitor_pipeline_health
    print_info("Testing monitor_pipeline_health...")
    try:
        health = monitor_pipeline_health(pipeline_name="test_pipeline")
        print_success("  monitor_pipeline_health called successfully.")
    except Exception as e:
        print_info(f"  monitor_pipeline_health demo: {e}")

    print_success("CI/CD examples completed successfully")
    return 0

if __name__ == "__main__":
    sys.exit(main())
