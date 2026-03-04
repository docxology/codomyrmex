#!/usr/bin/env python3
"""
Example orchestrator demonstrating full CI/CD flow using the ci_cd_automation module.
"""

import os
import sys
from pathlib import Path

# Add project src to path
project_root = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(project_root / "src"))

from codomyrmex.ci_cd_automation import (
    PipelineBuilder,
    WorkflowGenerator,
    ArtifactManager,
    PipelineManager,
    DeploymentOrchestrator,
)

def run_example():
    print("--- CI/CD Automation Example ---")

    # 1. Build a pipeline programmatically
    print("\n1. Building pipeline...")
    builder = PipelineBuilder("webapp-ci-cd")
    builder.add_stage("lint", ["echo 'Running ruff check...'"])
    builder.add_stage("test", ["echo 'Running pytest...'"], dependencies=["lint"])
    builder.add_stage("build", ["echo 'Building package...'", "mkdir -p dist", "touch dist/app.tar.gz"], dependencies=["test"])
    builder.add_stage("deploy", ["echo 'Deploying to staging...'"], dependencies=["build"], on_branch="main")

    pipeline = builder.build()
    print(f"Pipeline '{pipeline.name}' built with {len(pipeline.stages)} stages.")

    # 2. Generate GitHub Actions workflow
    print("\n2. Generating GitHub Actions workflow...")
    generator = WorkflowGenerator("github")
    workflow = generator.from_pipeline(pipeline)
    workflow_dict = workflow.to_dict()
    print(f"Generated workflow for {workflow_dict['name']} with {len(workflow_dict['jobs'])} jobs.")

    # 3. Execute the pipeline locally
    print("\n3. Executing pipeline locally...")
    mgr = PipelineManager()
    # We'll manually add the built pipeline to the manager since it was built programmatically
    mgr.pipelines[pipeline.name] = pipeline

    # Run it
    results = mgr.run_pipeline(pipeline.name)
    print(f"Pipeline execution finished with status: {results.status.value}")

    # 4. Manage artifacts
    print("\n4. Managing artifacts...")
    artifacts = ArtifactManager(".example_artifacts")
    # Simulate an artifact created during build
    Path("dist").mkdir(exist_ok=True)
    with open("dist/app.tar.gz", "w") as f:
        f.write("dummy app content")

    artifacts.upload("dist/app.tar.gz", version="1.0.0")
    print("Artifact 'app.tar.gz' v1.0.0 uploaded.")

    # 5. Orchestrate deployment
    print("\n5. Orchestrating deployment...")
    # Create a deployment config for demonstration
    deploy_config = {
        "environments": [
            {
                "name": "staging",
                "type": "staging",
                "host": "staging.example.com",
                "variables": {"deploy_path": "/var/www/staging"},
                "health_checks": [{"type": "tcp", "endpoint": "localhost:8000"}]
            }
        ]
    }

    config_path = "example_deployment_config.json"
    import json
    with open(config_path, "w") as f:
        json.dump(deploy_config, f)

    orchestrator = DeploymentOrchestrator(config_path)

    # Mocking deployment success since we don't have a real staging server
    print("Creating deployment to staging...")
    deployment = orchestrator.create_deployment(
        name="webapp-deploy",
        version="1.0.0",
        environment_name="staging",
        artifacts=["dist/app.tar.gz"]
    )

    # In a real scenario, we'd call orchestrator.deploy("webapp-deploy")
    # Here we just show the state
    print(f"Deployment to {deployment.environment.name} created.")

    # Cleanup example files
    if os.path.exists(config_path): os.remove(config_path)
    import shutil
    if os.path.exists("dist"): shutil.rmtree("dist")
    if os.path.exists(".example_artifacts"): shutil.rmtree(".example_artifacts")
    if os.path.exists(".pipelines"): shutil.rmtree(".pipelines")

    print("\n--- Example Completed Successfully ---")


    # Auto-injected: Load configuration
    import yaml
    from pathlib import Path
    config_path = Path(__file__).resolve().parent.parent.parent / "config" / "ci_cd_automation" / "config.yaml"
    config_data = {}
    if config_path.exists():
        with open(config_path, "r") as f:
            config_data = yaml.safe_load(f) or {}
            print(f"Loaded config from config/ci_cd_automation/config.yaml")

if __name__ == "__main__":
    run_example()
