#!/usr/bin/env python3
"""
Orchestrator script for the dependency_injection module.
Demonstrates the use of the IoC container, scoping, and auto-injection.
"""

import sys
from typing import Protocol

from codomyrmex.dependency_injection import (
    Container,
    ScopeContext,
    inject,
    injectable,
)
from codomyrmex.logging_monitoring.core.logger_config import get_logger

logger = get_logger(__name__)


# ---------------------------------------------------------------------------
# Domain Models & Interfaces
# ---------------------------------------------------------------------------

class IDataRepository(Protocol):
    def get_data(self) -> str:
        ...


class IProcessingService(Protocol):
    def process(self) -> str:
        ...


# ---------------------------------------------------------------------------
# Implementations
# ---------------------------------------------------------------------------

@injectable(scope="singleton")
class Configuration:
    def __init__(self):
        self.app_name = "DI-Orchestrator"
        self.version = "1.1.0"


@injectable(scope="transient")
class MockRepository:
    def get_data(self) -> str:
        return f"Real-time data from MockRepository ({id(self)})"


@injectable(scope="scoped")
class ProcessingService:
    @inject
    def __init__(self, repos: list[IDataRepository], config: Configuration):
        self.repos = repos
        self.config = config

    def process(self) -> str:
        results = [repo.get_data() for repo in self.repos]
        return f"[{self.config.app_name} v{self.config.version}] Processed with {len(results)} repos: {results}"


# ---------------------------------------------------------------------------
# Orchestration
# ---------------------------------------------------------------------------

def run_orchestrator():
    print("=== Codomyrmex Dependency Injection Orchestrator ===\n")

    # 1. Initialize Container
    container = Container()

    # 2. Register Services via scanning
    print("[1] Scanning for @injectable services...")
    import __main__
    container.scan(__main__)

    # Also register some named repositories to demonstrate collection resolution
    container.register(IDataRepository, MockRepository, scope="transient", name="repo1")
    container.register(IDataRepository, MockRepository, scope="transient", name="repo2")

    # Register the interface for the service
    container.register(IProcessingService, ProcessingService, scope="scoped")

    print(f"Container state: {container}\n")

    # 3. Resolve Singleton
    print("[2] Resolving singleton configuration...")
    config1 = container.resolve(Configuration)
    config2 = container.resolve(Configuration)
    print(f"Config 1: {config1.app_name}")
    print(f"Singleton check: {config1 is config2}\n")

    # 4. Scoped and Transient Resolution
    print("[3] Entering Scoped Context...")
    with ScopeContext(container) as scope:
        service1 = scope.resolve(IProcessingService)
        service2 = scope.resolve(IProcessingService)

        print(f"Service 1 output: {service1.process()}")
        print(f"Scoped check (service): {service1 is service2}")

        # Demonstrating transient behavior: resolve twice from container
        repo_a = container.resolve(IDataRepository, name="repo1")
        repo_b = container.resolve(IDataRepository, name="repo1")
        print(f"Transient check (repo): {repo_a is not repo_b} (IDs: {id(repo_a)}, {id(repo_b)})")

    print("\n[4] Collection Resolution...")
    all_repos = container.resolve_all(IDataRepository)
    print(f"Resolved all {len(all_repos)} repositories.")

    print("\nOrchestration complete.")



    # Auto-injected: Load configuration
    from pathlib import Path

    import yaml
    config_path = Path(__file__).resolve().parent.parent.parent / "config" / "dependency_injection" / "config.yaml"
    if config_path.exists():
        with open(config_path) as f:
            yaml.safe_load(f) or {}
            print("Loaded config from config/dependency_injection/config.yaml")

if __name__ == "__main__":
    try:
        run_orchestrator()
    except Exception as e:
        logger.exception("Orchestrator failed")
        print(f"Error: {e}")
        sys.exit(1)
