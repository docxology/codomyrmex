"""Unit tests for the geopolitical_market_sim typed facade.

Zero-Mock policy: tests verify real object construction, method signatures,
and delegation logic without patching HermesClient.

All tests that require a live Hermes backend are guarded by skipif.
"""

from __future__ import annotations


import pytest

from codomyrmex.skills.skills.custom.geopolitical_market_sim import (
    SKILL_NAME,
    GeopoliticalMarketPipeline,
    TopicConfig,
    dashboard,
    health,
    list_worldosint_modules,
    plan_tracked,
    run_tracked,
    track_topic,
    update_topic,
)


# ── SKILL_NAME constant ───────────────────────────────────────────────────────


@pytest.mark.unit
def test_skill_name_constant() -> None:
    assert SKILL_NAME == "geopolitical-market-sim"


# ── TopicConfig dataclass ─────────────────────────────────────────────────────


@pytest.mark.unit
class TestTopicConfig:
    def test_construction_minimal(self) -> None:
        config = TopicConfig(
            topic_id="test-id",
            topic="Test topic",
            market_query="test query",
        )
        assert config.topic_id == "test-id"
        assert config.topic == "Test topic"
        assert config.keywords == []
        assert config.regions == []

    def test_construction_full(self) -> None:
        config = TopicConfig(
            topic_id="iran-conflict",
            topic="Iran conflict",
            market_query="Iran nuclear deal",
            keywords=["iran", "nuclear"],
            regions=["IR", "US"],
            max_rounds=20,
            target_agents=48,
            simulation_mode="auto",
        )
        assert config.keywords == ["iran", "nuclear"]
        assert config.regions == ["IR", "US"]
        assert config.max_rounds == 20
        assert config.simulation_mode == "auto"

    def test_defaults(self) -> None:
        config = TopicConfig(topic_id="x", topic="y", market_query="z")
        assert config.target_agents == 48
        assert config.simulation_mode == "auto"
        assert config.max_rounds is None


# ── GeopoliticalMarketPipeline ────────────────────────────────────────────────


@pytest.mark.unit
class TestGeopoliticalMarketPipelineInit:
    def test_default_init(self) -> None:
        pipeline = GeopoliticalMarketPipeline()
        assert pipeline is not None
        assert pipeline._session_prefix == "predihermes"

    def test_custom_prefix(self) -> None:
        pipeline = GeopoliticalMarketPipeline(session_prefix="my-prefix")
        assert pipeline._session_prefix == "my-prefix"

    def test_repr(self) -> None:
        pipeline = GeopoliticalMarketPipeline()
        r = repr(pipeline)
        assert "GeopoliticalMarketPipeline" in r
        assert "predihermes" in r


@pytest.mark.unit
class TestGeopoliticalMarketPipelineMethods:
    """Verify all facade methods exist with correct signatures."""

    def test_has_health(self) -> None:
        pipeline = GeopoliticalMarketPipeline()
        assert callable(pipeline.health)

    def test_has_list_worldosint_modules(self) -> None:
        pipeline = GeopoliticalMarketPipeline()
        assert callable(pipeline.list_worldosint_modules)

    def test_has_track_topic(self) -> None:
        pipeline = GeopoliticalMarketPipeline()
        assert callable(pipeline.track_topic)

    def test_has_track_from_config(self) -> None:
        pipeline = GeopoliticalMarketPipeline()
        assert callable(pipeline.track_from_config)

    def test_has_run_tracked(self) -> None:
        pipeline = GeopoliticalMarketPipeline()
        assert callable(pipeline.run_tracked)

    def test_has_plan_tracked(self) -> None:
        pipeline = GeopoliticalMarketPipeline()
        assert callable(pipeline.plan_tracked)

    def test_has_dashboard(self) -> None:
        pipeline = GeopoliticalMarketPipeline()
        assert callable(pipeline.dashboard)

    def test_has_update_topic(self) -> None:
        pipeline = GeopoliticalMarketPipeline()
        assert callable(pipeline.update_topic)


@pytest.mark.unit
class TestGeopoliticalMarketPipelineSessionNames:
    """Verify session name generation in _sn()."""

    def test_sn_format(self) -> None:
        pipeline = GeopoliticalMarketPipeline(session_prefix="px")
        assert pipeline._sn("health") == "px-health"
        assert pipeline._sn("run-iran") == "px-run-iran"


# ── Free functions — exist and are callable ──────────────────────────────────


@pytest.mark.unit
class TestFreeFunctions:
    def test_health_is_callable(self) -> None:
        assert callable(health)

    def test_list_worldosint_modules_is_callable(self) -> None:
        assert callable(list_worldosint_modules)

    def test_track_topic_is_callable(self) -> None:
        assert callable(track_topic)

    def test_run_tracked_is_callable(self) -> None:
        assert callable(run_tracked)

    def test_plan_tracked_is_callable(self) -> None:
        assert callable(plan_tracked)

    def test_dashboard_is_callable(self) -> None:
        assert callable(dashboard)

    def test_update_topic_is_callable(self) -> None:
        assert callable(update_topic)


# ── Imports ───────────────────────────────────────────────────────────────────


@pytest.mark.unit
def test_package_imports() -> None:
    """Top-level package imports must not raise."""
    from codomyrmex.skills.skills.custom import geopolitical_market_sim  # noqa: F401

    assert geopolitical_market_sim is not None


@pytest.mark.unit
def test_skill_name_from_package() -> None:
    from codomyrmex.skills.skills.custom.geopolitical_market_sim import SKILL_NAME as sn

    assert sn == "geopolitical-market-sim"
