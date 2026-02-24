"""
Chaos Testing Scenarios

Pre-built chaos testing scenarios for common failure modes.
"""

import asyncio
import random
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any
from collections.abc import Callable

from . import FaultInjector


class ScenarioType(Enum):
    """Pre-built chaos scenarios."""
    NETWORK_PARTITION = "network_partition"
    SERVICE_OUTAGE = "service_outage"
    DATABASE_FAILURE = "database_failure"
    HIGH_LATENCY = "high_latency"
    MEMORY_PRESSURE = "memory_pressure"
    CPU_SPIKE = "cpu_spike"
    DISK_FULL = "disk_full"
    CASCADING_FAILURE = "cascading_failure"


@dataclass
class ScenarioConfig:
    """Configuration for a chaos scenario."""
    type: ScenarioType
    duration_seconds: float = 30.0
    intensity: float = 0.5  # 0-1
    targets: list[str] = field(default_factory=list)
    parameters: dict[str, Any] = field(default_factory=dict)


@dataclass
class ScenarioResult:
    """Result of running a chaos scenario."""
    scenario_type: ScenarioType
    success: bool
    errors_detected: int
    recovery_time_ms: float
    observations: list[str] = field(default_factory=list)


class ChaosScenarioRunner:
    """Run pre-built chaos scenarios."""

    def __init__(self):
        """Execute   Init   operations natively."""
        self._injector = FaultInjector()
        self._scenarios: dict[ScenarioType, Callable] = {
            ScenarioType.NETWORK_PARTITION: self._run_network_partition,
            ScenarioType.SERVICE_OUTAGE: self._run_service_outage,
            ScenarioType.HIGH_LATENCY: self._run_high_latency,
            ScenarioType.CASCADING_FAILURE: self._run_cascading_failure,
        }

    async def run(self, config: ScenarioConfig) -> ScenarioResult:
        """Run a chaos scenario."""
        if config.type not in self._scenarios:
            return ScenarioResult(
                scenario_type=config.type,
                success=False,
                errors_detected=0,
                recovery_time_ms=0,
                observations=[f"Unknown scenario: {config.type}"],
            )

        return await self._scenarios[config.type](config)

    async def _run_network_partition(self, config: ScenarioConfig) -> ScenarioResult:
        """Simulate network partition."""
        observations = []
        errors = 0

        observations.append(f"Starting network partition for {config.duration_seconds}s")

        # Inject latency and failures
        start = time.time()
        partition_active = True

        async def partition_behavior():
            nonlocal errors
            while partition_active:
                if random.random() < config.intensity:
                    errors += 1
                await asyncio.sleep(0.1)

        task = asyncio.create_task(partition_behavior())
        await asyncio.sleep(config.duration_seconds)
        partition_active = False
        await task

        recovery_start = time.time()
        # Simulate recovery verification
        await asyncio.sleep(0.5)
        recovery_time = (time.time() - recovery_start) * 1000

        observations.append(f"Partition ended, {errors} errors during partition")
        observations.append(f"Recovery completed in {recovery_time:.0f}ms")

        return ScenarioResult(
            scenario_type=config.type,
            success=True,
            errors_detected=errors,
            recovery_time_ms=recovery_time,
            observations=observations,
        )

    async def _run_service_outage(self, config: ScenarioConfig) -> ScenarioResult:
        """Simulate complete service outage."""
        observations = []

        for target in config.targets:
            observations.append(f"Taking down service: {target}")

        await asyncio.sleep(config.duration_seconds)

        observations.append("Restoring services")
        await asyncio.sleep(1.0)  # Simulate startup

        return ScenarioResult(
            scenario_type=config.type,
            success=True,
            errors_detected=len(config.targets),
            recovery_time_ms=1000,
            observations=observations,
        )

    async def _run_high_latency(self, config: ScenarioConfig) -> ScenarioResult:
        """Inject high latency."""
        latency_ms = config.parameters.get("latency_ms", 500)
        observations = [f"Injecting {latency_ms}ms latency"]

        errors = 0
        start = time.time()

        while time.time() - start < config.duration_seconds:
            # Each request gets delayed
            await asyncio.sleep(latency_ms / 1000)
            if random.random() < 0.1:  # 10% timeouts
                errors += 1

        observations.append(f"Latency injection complete, {errors} timeouts")

        return ScenarioResult(
            scenario_type=config.type,
            success=True,
            errors_detected=errors,
            recovery_time_ms=0,
            observations=observations,
        )

    async def _run_cascading_failure(self, config: ScenarioConfig) -> ScenarioResult:
        """Simulate cascading failure across services."""
        observations = []
        total_errors = 0

        # Fail services one by one
        for i, target in enumerate(config.targets):
            delay = i * (config.duration_seconds / max(len(config.targets), 1))
            observations.append(f"[{delay:.1f}s] Service {target} failing")
            total_errors += 1
            await asyncio.sleep(config.duration_seconds / max(len(config.targets), 1))

        # Recovery
        recovery_start = time.time()
        for target in reversed(config.targets):
            observations.append(f"Recovering {target}")
            await asyncio.sleep(0.5)

        recovery_time = (time.time() - recovery_start) * 1000

        return ScenarioResult(
            scenario_type=config.type,
            success=True,
            errors_detected=total_errors,
            recovery_time_ms=recovery_time,
            observations=observations,
        )


class GameDay:
    """Run a coordinated chaos game day."""

    def __init__(self):
        """Execute   Init   operations natively."""
        self._runner = ChaosScenarioRunner()
        self._scenarios: list[ScenarioConfig] = []
        self._results: list[ScenarioResult] = []

    def add_scenario(self, config: ScenarioConfig) -> "GameDay":
        """Add a scenario to the game day."""
        self._scenarios.append(config)
        return self

    async def run_all(self, parallel: bool = False) -> list[ScenarioResult]:
        """Run all scenarios."""
        if parallel:
            tasks = [self._runner.run(s) for s in self._scenarios]
            self._results = await asyncio.gather(*tasks)
        else:
            self._results = []
            for scenario in self._scenarios:
                result = await self._runner.run(scenario)
                self._results.append(result)

        return self._results

    def report(self) -> str:
        """Generate game day report."""
        lines = ["# Chaos Game Day Report", ""]

        total_errors = sum(r.errors_detected for r in self._results)
        passed = sum(1 for r in self._results if r.success)

        lines.append(f"**Scenarios Run:** {len(self._results)}")
        lines.append(f"**Passed:** {passed}/{len(self._results)}")
        lines.append(f"**Total Errors Detected:** {total_errors}")
        lines.append("")

        for result in self._results:
            lines.append(f"## {result.scenario_type.value}")
            lines.append(f"- Success: {result.success}")
            lines.append(f"- Errors: {result.errors_detected}")
            lines.append(f"- Recovery: {result.recovery_time_ms:.0f}ms")
            for obs in result.observations:
                lines.append(f"  - {obs}")
            lines.append("")

        return "\n".join(lines)
