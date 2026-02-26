"""Unit tests for codomyrmex.testing.chaos.scenarios module.

Tests cover: ScenarioType, ScenarioConfig, ScenarioResult, ChaosScenarioRunner, GameDay.
"""

import asyncio

import pytest

from codomyrmex.testing.chaos.scenarios import (
    ChaosScenarioRunner,
    GameDay,
    ScenarioConfig,
    ScenarioResult,
    ScenarioType,
)


# ============================================================================
# ScenarioType enum tests
# ============================================================================


@pytest.mark.unit
class TestScenarioType:
    """Test ScenarioType enum values."""

    def test_all_scenario_types_present(self):
        """All 8 scenario types are defined."""
        expected = {
            "NETWORK_PARTITION",
            "SERVICE_OUTAGE",
            "DATABASE_FAILURE",
            "HIGH_LATENCY",
            "MEMORY_PRESSURE",
            "CPU_SPIKE",
            "DISK_FULL",
            "CASCADING_FAILURE",
        }
        actual = {member.name for member in ScenarioType}
        assert actual == expected

    def test_scenario_type_values(self):
        """Enum values are lowercase snake_case strings."""
        assert ScenarioType.NETWORK_PARTITION.value == "network_partition"
        assert ScenarioType.SERVICE_OUTAGE.value == "service_outage"
        assert ScenarioType.HIGH_LATENCY.value == "high_latency"
        assert ScenarioType.CASCADING_FAILURE.value == "cascading_failure"


# ============================================================================
# ScenarioConfig dataclass tests
# ============================================================================


@pytest.mark.unit
class TestScenarioConfig:
    """Test ScenarioConfig dataclass construction and defaults."""

    def test_defaults(self):
        """Default values for duration, intensity, targets, parameters."""
        cfg = ScenarioConfig(type=ScenarioType.HIGH_LATENCY)
        assert cfg.duration_seconds == 30.0
        assert cfg.intensity == 0.5
        assert cfg.targets == []
        assert cfg.parameters == {}

    def test_custom_values(self):
        """Custom values override defaults."""
        cfg = ScenarioConfig(
            type=ScenarioType.SERVICE_OUTAGE,
            duration_seconds=5.0,
            intensity=0.9,
            targets=["svc-a", "svc-b"],
            parameters={"retries": 3},
        )
        assert cfg.type == ScenarioType.SERVICE_OUTAGE
        assert cfg.duration_seconds == 5.0
        assert cfg.intensity == 0.9
        assert cfg.targets == ["svc-a", "svc-b"]
        assert cfg.parameters == {"retries": 3}

    def test_targets_list_is_independent(self):
        """Each config gets its own targets list (no shared default)."""
        cfg1 = ScenarioConfig(type=ScenarioType.CPU_SPIKE)
        cfg2 = ScenarioConfig(type=ScenarioType.CPU_SPIKE)
        cfg1.targets.append("service-x")
        assert cfg2.targets == []


# ============================================================================
# ScenarioResult dataclass tests
# ============================================================================


@pytest.mark.unit
class TestScenarioResult:
    """Test ScenarioResult dataclass construction and defaults."""

    def test_defaults(self):
        """Observations default to empty list."""
        result = ScenarioResult(
            scenario_type=ScenarioType.HIGH_LATENCY,
            success=True,
            errors_detected=0,
            recovery_time_ms=100.0,
        )
        assert result.observations == []
        assert result.success is True
        assert result.errors_detected == 0
        assert result.recovery_time_ms == 100.0

    def test_with_observations(self):
        """Result with explicit observations."""
        result = ScenarioResult(
            scenario_type=ScenarioType.NETWORK_PARTITION,
            success=False,
            errors_detected=5,
            recovery_time_ms=2500.0,
            observations=["partition started", "errors detected"],
        )
        assert len(result.observations) == 2
        assert result.errors_detected == 5


# ============================================================================
# ChaosScenarioRunner tests
# ============================================================================


@pytest.mark.unit
class TestChaosScenarioRunner:
    """Test ChaosScenarioRunner async run methods."""

    def test_runner_creation(self):
        """Runner initializes with scenario handlers dict."""
        runner = ChaosScenarioRunner()
        assert runner._injector is not None
        assert len(runner._scenarios) == 4  # 4 implemented scenarios

    def test_unknown_scenario_returns_failure(self):
        """Running an unsupported scenario type returns failure result."""
        runner = ChaosScenarioRunner()
        config = ScenarioConfig(type=ScenarioType.DATABASE_FAILURE)
        result = asyncio.get_event_loop().run_until_complete(runner.run(config))
        assert result.success is False
        assert "Unknown scenario" in result.observations[0]
        assert result.errors_detected == 0

    def test_network_partition_scenario(self):
        """Network partition runs and returns a valid result."""
        runner = ChaosScenarioRunner()
        config = ScenarioConfig(
            type=ScenarioType.NETWORK_PARTITION,
            duration_seconds=0.2,
            intensity=0.3,
        )
        result = asyncio.get_event_loop().run_until_complete(runner.run(config))
        assert result.success is True
        assert result.scenario_type == ScenarioType.NETWORK_PARTITION
        assert result.recovery_time_ms >= 0
        assert len(result.observations) >= 2  # start + end observations

    def test_service_outage_scenario(self):
        """Service outage runs with targets and returns expected result."""
        runner = ChaosScenarioRunner()
        config = ScenarioConfig(
            type=ScenarioType.SERVICE_OUTAGE,
            duration_seconds=0.1,
            targets=["api", "db"],
        )
        result = asyncio.get_event_loop().run_until_complete(runner.run(config))
        assert result.success is True
        assert result.errors_detected == 2  # one per target
        assert result.recovery_time_ms == 1000
        # Should have observations for each target plus "Restoring services"
        target_obs = [o for o in result.observations if "Taking down" in o]
        assert len(target_obs) == 2

    def test_high_latency_scenario(self):
        """High latency scenario runs with custom latency_ms param."""
        runner = ChaosScenarioRunner()
        config = ScenarioConfig(
            type=ScenarioType.HIGH_LATENCY,
            duration_seconds=0.15,
            parameters={"latency_ms": 50},
        )
        result = asyncio.get_event_loop().run_until_complete(runner.run(config))
        assert result.success is True
        assert result.scenario_type == ScenarioType.HIGH_LATENCY
        assert "50ms" in result.observations[0]

    def test_cascading_failure_scenario(self):
        """Cascading failure runs through targets sequentially."""
        runner = ChaosScenarioRunner()
        config = ScenarioConfig(
            type=ScenarioType.CASCADING_FAILURE,
            duration_seconds=0.3,
            targets=["front", "middle", "back"],
        )
        result = asyncio.get_event_loop().run_until_complete(runner.run(config))
        assert result.success is True
        assert result.errors_detected == 3  # one per target
        assert result.recovery_time_ms > 0
        # Should have failing + recovering observations
        failing_obs = [o for o in result.observations if "failing" in o]
        recovering_obs = [o for o in result.observations if "Recovering" in o]
        assert len(failing_obs) == 3
        assert len(recovering_obs) == 3

    def test_cascading_failure_empty_targets(self):
        """Cascading failure with no targets still succeeds."""
        runner = ChaosScenarioRunner()
        config = ScenarioConfig(
            type=ScenarioType.CASCADING_FAILURE,
            duration_seconds=0.1,
            targets=[],
        )
        result = asyncio.get_event_loop().run_until_complete(runner.run(config))
        assert result.success is True
        assert result.errors_detected == 0


# ============================================================================
# GameDay tests
# ============================================================================


@pytest.mark.unit
class TestGameDay:
    """Test GameDay coordinated chaos testing."""

    def test_game_day_creation(self):
        """GameDay initializes with empty scenario and result lists."""
        gd = GameDay()
        assert gd._scenarios == []
        assert gd._results == []

    def test_add_scenario_returns_self(self):
        """add_scenario returns the GameDay for chaining."""
        gd = GameDay()
        config = ScenarioConfig(type=ScenarioType.HIGH_LATENCY, duration_seconds=0.1)
        returned = gd.add_scenario(config)
        assert returned is gd
        assert len(gd._scenarios) == 1

    def test_run_all_sequential(self):
        """Run all scenarios sequentially."""
        gd = GameDay()
        gd.add_scenario(ScenarioConfig(
            type=ScenarioType.HIGH_LATENCY,
            duration_seconds=0.1,
            parameters={"latency_ms": 30},
        ))
        gd.add_scenario(ScenarioConfig(
            type=ScenarioType.SERVICE_OUTAGE,
            duration_seconds=0.1,
            targets=["svc-a"],
        ))
        results = asyncio.get_event_loop().run_until_complete(gd.run_all(parallel=False))
        assert len(results) == 2
        assert all(r.success for r in results)

    def test_run_all_parallel(self):
        """Run all scenarios in parallel."""
        gd = GameDay()
        gd.add_scenario(ScenarioConfig(
            type=ScenarioType.HIGH_LATENCY,
            duration_seconds=0.1,
            parameters={"latency_ms": 30},
        ))
        gd.add_scenario(ScenarioConfig(
            type=ScenarioType.SERVICE_OUTAGE,
            duration_seconds=0.1,
            targets=["svc-x"],
        ))
        results = asyncio.get_event_loop().run_until_complete(gd.run_all(parallel=True))
        assert len(results) == 2
        assert all(r.success for r in results)

    def test_report_empty(self):
        """Report with no results produces header but zero counts."""
        gd = GameDay()
        report = gd.report()
        assert "Chaos Game Day Report" in report
        assert "Scenarios Run:** 0" in report
        assert "Passed:** 0/0" in report
        assert "Total Errors Detected:** 0" in report

    def test_report_after_run(self):
        """Report after running scenarios includes scenario details."""
        gd = GameDay()
        gd.add_scenario(ScenarioConfig(
            type=ScenarioType.SERVICE_OUTAGE,
            duration_seconds=0.1,
            targets=["svc-a"],
        ))
        asyncio.get_event_loop().run_until_complete(gd.run_all())
        report = gd.report()
        assert "Scenarios Run:** 1" in report
        assert "service_outage" in report
        assert "Success: True" in report

    def test_chaining_multiple_add_scenario(self):
        """Chaining multiple add_scenario calls works."""
        gd = GameDay()
        gd.add_scenario(
            ScenarioConfig(type=ScenarioType.HIGH_LATENCY, duration_seconds=0.05)
        ).add_scenario(
            ScenarioConfig(type=ScenarioType.NETWORK_PARTITION, duration_seconds=0.05)
        )
        assert len(gd._scenarios) == 2
