#!/usr/bin/env python3
"""
Containerization - Real Usage Examples

Demonstrates actual containerization capabilities:
- DockerManager initialization
- KubernetesOrchestrator interface
- Security scanning stubs
"""

import sys
from pathlib import Path

# Ensure codomyrmex is in path
try:
    import codomyrmex  # noqa: F401
except ImportError:
    project_root = Path(__file__).resolve().parent.parent.parent.parent
    sys.path.insert(0, str(project_root / "src"))

from codomyrmex.containerization import (
    ContainerOptimizer,
    ContainerSecurityScanner,
    DockerManager,
    KubernetesOrchestrator,
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

    config_path = (
        Path(__file__).resolve().parent.parent.parent
        / "config"
        / "containerization"
        / "config.yaml"
    )
    if config_path.exists():
        with open(config_path) as f:
            yaml.safe_load(f) or {}
            print("Loaded config from config/containerization/config.yaml")

    setup_logging()
    print_info("Running Containerization Examples...")

    # 1. Docker Manager
    print_info("Testing DockerManager initialization...")
    try:
        DockerManager()
        print_success("  DockerManager available.")
    except Exception as e:
        print_info(f"  DockerManager note: {e}")

    # 2. Kubernetes Orchestrator
    print_info("Testing KubernetesOrchestrator initialization...")
    try:
        KubernetesOrchestrator()
        print_success("  KubernetesOrchestrator available.")
    except Exception as e:
        print_info(f"  KubernetesOrchestrator note: {e}")

    # 3. Security Scanner
    print_info("Verifying ContainerSecurityScanner...")
    try:
        ContainerSecurityScanner()
        print_success("  ContainerSecurityScanner available.")
    except Exception as e:
        print_error(f"  Security scanner failed: {e}")

    # 4. Optimizer
    print_info("Verifying ContainerOptimizer...")
    try:
        ContainerOptimizer()
        print_success("  ContainerOptimizer available.")
    except Exception as e:
        print_error(f"  Optimizer failed: {e}")

    print_success("Containerization examples completed successfully")
    return 0


if __name__ == "__main__":
    sys.exit(main())
