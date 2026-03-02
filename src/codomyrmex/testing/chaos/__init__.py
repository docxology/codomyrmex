"""
Chaos Engineering Module

Fault injection and resilience testing.
"""

__version__ = "0.1.0"

import random
import threading
import time
from abc import ABC, abstractmethod
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Optional

# Shared schemas for cross-module interop
try:
    from codomyrmex.validation.schemas import Result, ResultStatus
except ImportError:
    Result = None
    ResultStatus = None

class FaultType(Enum):
    """Types of injectable faults."""
    LATENCY = "latency"
    ERROR = "error"
    TIMEOUT = "timeout"
    RESOURCE_EXHAUSTION = "resource_exhaustion"
    NETWORK_PARTITION = "network_partition"

@dataclass
class FaultConfig:
    """Configuration for a fault."""
    fault_type: FaultType
    probability: float = 0.1  # 0-1
    duration_seconds: float = 0.0
    error_message: str = "Injected fault"
    metadata: dict[str, Any] = field(default_factory=dict)

class FaultInjector:
    """Inject faults into system components."""

    def __init__(self):
        self._active_faults: dict[str, FaultConfig] = {}
        self._lock = threading.Lock()

    def register_fault(self, name: str, config: FaultConfig) -> None:
        """Register a fault."""
        with self._lock:
            self._active_faults[name] = config

    def remove_fault(self, name: str) -> bool:
        """Remove a fault."""
        with self._lock:
            if name in self._active_faults:
                del self._active_faults[name]
                return True
        return False

    def should_inject(self, name: str) -> bool:
        """Check if fault should be injected."""
        config = self._active_faults.get(name)
        if not config:
            return False
        return random.random() < config.probability

    def inject(self, name: str) -> None:
        """Inject the fault (call after should_inject)."""
        config = self._active_faults.get(name)
        if not config:
            return

        if config.fault_type == FaultType.LATENCY:
            time.sleep(config.duration_seconds)

        elif config.fault_type == FaultType.ERROR:
            raise InjectedFaultError(config.error_message)

        elif config.fault_type == FaultType.TIMEOUT:
            time.sleep(config.duration_seconds)
            raise TimeoutError(config.error_message)

    def maybe_inject(self, name: str) -> None:
        """Inject fault probabilistically."""
        if self.should_inject(name):
            self.inject(name)

class InjectedFaultError(Exception):
    """Raised when a fault is injected."""
    pass

@dataclass
class SteadyStateHypothesis:
    """Define expected steady state."""
    name: str
    check_fn: Callable[[], bool]
    description: str = ""

@dataclass
class ExperimentResult:
    """Result of a chaos experiment."""
    experiment_name: str
    success: bool
    steady_state_before: bool
    steady_state_after: bool
    duration_seconds: float
    error: str | None = None
    started_at: datetime = field(default_factory=datetime.now)

class ChaosExperiment:
    """A chaos engineering experiment."""

    def __init__(
        self,
        name: str,
        hypothesis: SteadyStateHypothesis,
        action: Callable[[], None],
        rollback: Callable[[], None] | None = None,
    ):
        self.name = name
        self.hypothesis = hypothesis
        self.action = action
        self.rollback = rollback

    def run(self) -> ExperimentResult:
        """Run the experiment."""
        start_time = time.time()
        error = None

        # Check steady state before
        try:
            steady_before = self.hypothesis.check_fn()
        except Exception as e:
            return ExperimentResult(
                experiment_name=self.name,
                success=False,
                steady_state_before=False,
                steady_state_after=False,
                duration_seconds=time.time() - start_time,
                error=f"Failed to verify initial steady state: {e}",
            )

        if not steady_before:
            return ExperimentResult(
                experiment_name=self.name,
                success=False,
                steady_state_before=False,
                steady_state_after=False,
                duration_seconds=time.time() - start_time,
                error="System not in steady state before experiment",
            )

        # Execute chaos action
        try:
            self.action()
        except Exception as e:
            error = f"Action failed: {e}"

        # Check steady state after
        try:
            steady_after = self.hypothesis.check_fn()
        except Exception as e:
            steady_after = False
            error = error or f"Failed to verify steady state after: {e}"

        # Rollback if needed
        if self.rollback:
            try:
                self.rollback()
            except Exception as e:
                error = (error or "") + f"; Rollback failed: {e}"

        return ExperimentResult(
            experiment_name=self.name,
            success=steady_after,
            steady_state_before=steady_before,
            steady_state_after=steady_after,
            duration_seconds=time.time() - start_time,
            error=error,
        )

class ChaosMonkey:
    """Automated chaos testing."""

    def __init__(self, injector: FaultInjector | None = None):
        self.injector = injector or FaultInjector()
        self._experiments: list[ChaosExperiment] = []
        self._results: list[ExperimentResult] = []

    def add_experiment(self, experiment: ChaosExperiment) -> None:
        """Add an experiment."""
        self._experiments.append(experiment)

    def run_all(self) -> list[ExperimentResult]:
        """Run all experiments."""
        self._results = []
        for exp in self._experiments:
            result = exp.run()
            self._results.append(result)
        return self._results

    def run_random(self) -> ExperimentResult | None:
        """Run a random experiment."""
        if not self._experiments:
            return None
        exp = random.choice(self._experiments)
        result = exp.run()
        self._results.append(result)
        return result

    @property
    def results(self) -> list[ExperimentResult]:
        """results ."""
        return self._results

# Decorators
def with_chaos(
    injector: FaultInjector,
    fault_name: str,
) -> Callable:
    """Decorator to inject chaos into a function."""
    def decorator(func: Callable) -> Callable:
        """decorator ."""
        def wrapper(*args, **kwargs):
            """wrapper ."""
            injector.maybe_inject(fault_name)
            return func(*args, **kwargs)
        return wrapper
    return decorator

def cli_commands():
    """Return CLI commands for the chaos_engineering module."""

    def _experiments():
        """List registered chaos experiments."""
        print("Chaos Engineering Experiments")
        print(f"  Fault Types: {[ft.value for ft in FaultType]}")
        monkey = ChaosMonkey()
        print(f"  Registered Experiments: {len(monkey._experiments)}")
        print(f"  Past Results: {len(monkey.results)}")

    def _run(name: str = ""):
        """Run a chaos experiment by --name."""
        if not name:
            print("Usage: chaos_engineering run --name <experiment_name>")
            return
        print(f"Running chaos experiment: {name}")
        print("  (No experiments registered in default context)")
        print(f"  Available fault types: {[ft.value for ft in FaultType]}")

    return {
        "experiments": _experiments,
        "run": _run,
    }

__all__ = [
    "FaultInjector",
    "FaultType",
    "FaultConfig",
    "ChaosExperiment",
    "ChaosMonkey",
    "SteadyStateHypothesis",
    "ExperimentResult",
    "InjectedFaultError",
    "with_chaos",
    "cli_commands",
]
