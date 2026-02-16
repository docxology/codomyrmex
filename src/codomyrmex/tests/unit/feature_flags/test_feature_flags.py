"""Comprehensive tests for the feature_flags module.

Tests cover FeatureManager, evaluation strategies, storage backends,
rollout management, targeting rules, and the experiment system.
"""

import json

import pytest

from codomyrmex.feature_flags import FeatureManager
from codomyrmex.feature_flags.strategies import (
    AttributeStrategy,
    BooleanStrategy,
    CompositeStrategy,
    EnvironmentStrategy,
    EvaluationContext,
    EvaluationResult,
    PercentageStrategy,
    UserListStrategy,
    create_strategy,
)
from codomyrmex.feature_flags.storage import (
    FileFlagStore,
    InMemoryFlagStore,
)
from codomyrmex.feature_flags.rollout import (
    RolloutConfig,
    RolloutManager,
    RolloutState,
)
from codomyrmex.feature_flags.evaluation import (
    FlagDefinition,
    FlagEvaluator,
    TargetingRule,
)


# ---------------------------------------------------------------------------
# FeatureManager (core manager)
# ---------------------------------------------------------------------------

@pytest.mark.unit
def test_static_flags_enabled():
    """Test simple boolean flag evaluation - enabled."""
    manager = FeatureManager({"feature-a": True})
    assert manager.is_enabled("feature-a") is True


@pytest.mark.unit
def test_static_flags_disabled():
    """Test simple boolean flag evaluation - disabled."""
    manager = FeatureManager({"feature-b": False})
    assert manager.is_enabled("feature-b") is False


@pytest.mark.unit
def test_static_flags_missing_default():
    """Test missing flag returns default."""
    manager = FeatureManager({})
    assert manager.is_enabled("missing") is False
    assert manager.is_enabled("missing", default=True) is True


@pytest.mark.unit
def test_percentage_rollout_deterministic():
    """Test percentage rollout gives deterministic results per user."""
    manager = FeatureManager({"feat": {"percentage": 50}})
    r1 = manager.is_enabled("feat", user_id="user_1")
    r2 = manager.is_enabled("feat", user_id="user_1")
    assert r1 == r2


@pytest.mark.unit
def test_percentage_rollout_no_user_id():
    """Test percentage rollout returns False without user_id."""
    manager = FeatureManager({"feat": {"percentage": 50}})
    assert manager.is_enabled("feat") is False


@pytest.mark.unit
def test_multivariate_flags():
    """Test non-boolean flag value retrieval."""
    manager = FeatureManager({"theme": "dark", "max": 10})
    assert manager.get_value("theme") == "dark"
    assert manager.get_value("max") == 10
    assert manager.get_value("missing", default="blue") == "blue"


@pytest.mark.unit
def test_flag_persistence_save_load(tmp_path):
    """Test saving and loading flags from file."""
    file_path = str(tmp_path / "flags.json")
    manager = FeatureManager({"feat-c": True, "feat-d": False})
    manager.save_to_file(file_path)

    new_manager = FeatureManager()
    new_manager.load_from_file(file_path)
    assert new_manager.is_enabled("feat-c") is True
    assert new_manager.is_enabled("feat-d") is False


# ---------------------------------------------------------------------------
# EvaluationContext
# ---------------------------------------------------------------------------

@pytest.mark.unit
def test_evaluation_context_defaults():
    """Test EvaluationContext default values."""
    ctx = EvaluationContext()
    assert ctx.user_id is None
    assert ctx.environment == "production"
    assert ctx.attributes == {}


@pytest.mark.unit
def test_evaluation_context_get_attribute():
    """Test EvaluationContext attribute lookup."""
    ctx = EvaluationContext(attributes={"country": "US", "plan": "pro"})
    assert ctx.get_attribute("country") == "US"
    assert ctx.get_attribute("missing") is None
    assert ctx.get_attribute("missing", "default") == "default"


@pytest.mark.unit
def test_evaluation_context_hash_key():
    """Test EvaluationContext hash key is consistent."""
    ctx = EvaluationContext(user_id="user-1")
    h1 = ctx.get_hash_key()
    h2 = ctx.get_hash_key()
    assert h1 == h2
    assert len(h1) == 32  # MD5 hex digest


# ---------------------------------------------------------------------------
# BooleanStrategy
# ---------------------------------------------------------------------------

@pytest.mark.unit
def test_boolean_strategy_enabled():
    """Test BooleanStrategy when enabled."""
    strategy = BooleanStrategy(enabled=True)
    result = strategy.evaluate(EvaluationContext())
    assert result.enabled is True
    assert result.reason == "boolean"


@pytest.mark.unit
def test_boolean_strategy_disabled():
    """Test BooleanStrategy when disabled."""
    strategy = BooleanStrategy(enabled=False)
    result = strategy.evaluate(EvaluationContext())
    assert result.enabled is False


@pytest.mark.unit
def test_boolean_strategy_serialization():
    """Test BooleanStrategy round-trip serialization."""
    strategy = BooleanStrategy(enabled=True)
    data = strategy.to_dict()
    restored = BooleanStrategy.from_dict(data)
    assert restored.enabled is True


# ---------------------------------------------------------------------------
# PercentageStrategy
# ---------------------------------------------------------------------------

@pytest.mark.unit
def test_percentage_strategy_zero():
    """Test PercentageStrategy at 0% disables for all."""
    strategy = PercentageStrategy(percentage=0.0)
    ctx = EvaluationContext(user_id="anyone")
    result = strategy.evaluate(ctx)
    assert result.enabled is False


@pytest.mark.unit
def test_percentage_strategy_hundred():
    """Test PercentageStrategy at 100% enables for all."""
    strategy = PercentageStrategy(percentage=100.0)
    ctx = EvaluationContext(user_id="anyone")
    result = strategy.evaluate(ctx)
    assert result.enabled is True


@pytest.mark.unit
def test_percentage_strategy_sticky():
    """Test PercentageStrategy is deterministic for same user."""
    strategy = PercentageStrategy(percentage=50.0, sticky=True)
    ctx = EvaluationContext(user_id="user-42")
    r1 = strategy.evaluate(ctx).enabled
    r2 = strategy.evaluate(ctx).enabled
    assert r1 == r2


# ---------------------------------------------------------------------------
# UserListStrategy
# ---------------------------------------------------------------------------

@pytest.mark.unit
def test_user_list_strategy_allowed():
    """Test UserListStrategy allows listed users."""
    strategy = UserListStrategy(allowed_users=["alice", "bob"])
    ctx = EvaluationContext(user_id="alice")
    assert strategy.evaluate(ctx).enabled is True


@pytest.mark.unit
def test_user_list_strategy_blocked():
    """Test UserListStrategy blocks listed users."""
    strategy = UserListStrategy(blocked_users=["eve"])
    ctx = EvaluationContext(user_id="eve")
    assert strategy.evaluate(ctx).enabled is False


@pytest.mark.unit
def test_user_list_strategy_no_user_id():
    """Test UserListStrategy returns default when no user_id."""
    strategy = UserListStrategy(default=True)
    ctx = EvaluationContext()
    assert strategy.evaluate(ctx).enabled is True


@pytest.mark.unit
def test_user_list_strategy_add_remove():
    """Test dynamically adding and removing users."""
    strategy = UserListStrategy()
    strategy.add_user("charlie")
    ctx = EvaluationContext(user_id="charlie")
    assert strategy.evaluate(ctx).enabled is True
    strategy.remove_user("charlie")
    assert strategy.evaluate(ctx).enabled is False


# ---------------------------------------------------------------------------
# AttributeStrategy
# ---------------------------------------------------------------------------

@pytest.mark.unit
def test_attribute_strategy_eq():
    """Test AttributeStrategy with equality operator."""
    strategy = AttributeStrategy(attribute="plan", operator="eq", value="pro")
    ctx = EvaluationContext(attributes={"plan": "pro"})
    assert strategy.evaluate(ctx).enabled is True


@pytest.mark.unit
def test_attribute_strategy_missing_attribute():
    """Test AttributeStrategy when attribute is missing."""
    strategy = AttributeStrategy(attribute="plan", operator="eq", value="pro")
    ctx = EvaluationContext(attributes={})
    assert strategy.evaluate(ctx).enabled is False


@pytest.mark.unit
def test_attribute_strategy_gt():
    """Test AttributeStrategy with greater-than operator."""
    strategy = AttributeStrategy(attribute="age", operator="gt", value=18)
    ctx = EvaluationContext(attributes={"age": 25})
    assert strategy.evaluate(ctx).enabled is True


# ---------------------------------------------------------------------------
# EnvironmentStrategy
# ---------------------------------------------------------------------------

@pytest.mark.unit
def test_environment_strategy_enabled_env():
    """Test EnvironmentStrategy enables for matching environment."""
    strategy = EnvironmentStrategy(enabled_environments=["staging", "production"])
    ctx = EvaluationContext(environment="production")
    assert strategy.evaluate(ctx).enabled is True


@pytest.mark.unit
def test_environment_strategy_disabled_env():
    """Test EnvironmentStrategy disables for non-matching environment."""
    strategy = EnvironmentStrategy(enabled_environments=["staging"])
    ctx = EvaluationContext(environment="production")
    assert strategy.evaluate(ctx).enabled is False


# ---------------------------------------------------------------------------
# CompositeStrategy
# ---------------------------------------------------------------------------

@pytest.mark.unit
def test_composite_strategy_and():
    """Test CompositeStrategy with AND logic."""
    strategy = CompositeStrategy(
        strategies=[BooleanStrategy(True), BooleanStrategy(True)],
        operator="and",
    )
    result = strategy.evaluate(EvaluationContext())
    assert result.enabled is True


@pytest.mark.unit
def test_composite_strategy_and_one_false():
    """Test CompositeStrategy AND returns false if one is false."""
    strategy = CompositeStrategy(
        strategies=[BooleanStrategy(True), BooleanStrategy(False)],
        operator="and",
    )
    result = strategy.evaluate(EvaluationContext())
    assert result.enabled is False


@pytest.mark.unit
def test_composite_strategy_or():
    """Test CompositeStrategy with OR logic."""
    strategy = CompositeStrategy(
        strategies=[BooleanStrategy(False), BooleanStrategy(True)],
        operator="or",
    )
    result = strategy.evaluate(EvaluationContext())
    assert result.enabled is True


@pytest.mark.unit
def test_composite_strategy_empty():
    """Test CompositeStrategy with no strategies returns disabled."""
    strategy = CompositeStrategy(strategies=[], operator="and")
    result = strategy.evaluate(EvaluationContext())
    assert result.enabled is False


# ---------------------------------------------------------------------------
# create_strategy factory
# ---------------------------------------------------------------------------

@pytest.mark.unit
def test_create_strategy_boolean():
    """Test create_strategy factory for boolean."""
    s = create_strategy({"type": "boolean", "enabled": True})
    assert isinstance(s, BooleanStrategy)
    assert s.enabled is True


@pytest.mark.unit
def test_create_strategy_percentage():
    """Test create_strategy factory for percentage."""
    s = create_strategy({"type": "percentage", "percentage": 50.0})
    assert isinstance(s, PercentageStrategy)


@pytest.mark.unit
def test_create_strategy_unknown_raises():
    """Test create_strategy raises on unknown type."""
    with pytest.raises(ValueError, match="Unknown strategy type"):
        create_strategy({"type": "nonexistent"})


# ---------------------------------------------------------------------------
# InMemoryFlagStore
# ---------------------------------------------------------------------------

@pytest.mark.unit
def test_in_memory_store_basic():
    """Test InMemoryFlagStore basic operations."""
    store = InMemoryFlagStore()
    store.set("flag-a", True)
    assert store.get("flag-a") is True
    assert store.get("missing") is None


@pytest.mark.unit
def test_in_memory_store_delete():
    """Test InMemoryFlagStore delete operation."""
    store = InMemoryFlagStore()
    store.set("flag-b", "value")
    assert store.delete("flag-b") is True
    assert store.delete("flag-b") is False  # already deleted
    assert store.get("flag-b") is None


@pytest.mark.unit
def test_in_memory_store_list_all():
    """Test InMemoryFlagStore lists all flags."""
    store = InMemoryFlagStore()
    store.set("a", 1)
    store.set("b", 2)
    all_flags = store.list_all()
    assert all_flags == {"a": 1, "b": 2}


@pytest.mark.unit
def test_in_memory_store_len():
    """Test InMemoryFlagStore length."""
    store = InMemoryFlagStore()
    assert len(store) == 0
    store.set("x", True)
    assert len(store) == 1


# ---------------------------------------------------------------------------
# FileFlagStore
# ---------------------------------------------------------------------------

@pytest.mark.unit
def test_file_store_basic(tmp_path):
    """Test FileFlagStore basic set/get."""
    store = FileFlagStore(str(tmp_path / "flags.json"))
    store.set("flag-x", True)
    assert store.get("flag-x") is True


@pytest.mark.unit
def test_file_store_persistence(tmp_path):
    """Test FileFlagStore persists across instances."""
    path = str(tmp_path / "flags.json")
    store1 = FileFlagStore(path)
    store1.set("persistent", "value")

    store2 = FileFlagStore(path)
    assert store2.get("persistent") == "value"


@pytest.mark.unit
def test_file_store_delete(tmp_path):
    """Test FileFlagStore delete operation."""
    store = FileFlagStore(str(tmp_path / "flags.json"))
    store.set("temp", True)
    assert store.delete("temp") is True
    assert store.get("temp") is None


@pytest.mark.unit
def test_file_store_list_all(tmp_path):
    """Test FileFlagStore list_all."""
    store = FileFlagStore(str(tmp_path / "flags.json"))
    store.set("a", 1)
    store.set("b", 2)
    all_flags = store.list_all()
    assert all_flags["a"] == 1
    assert all_flags["b"] == 2


# ---------------------------------------------------------------------------
# RolloutManager
# ---------------------------------------------------------------------------

@pytest.mark.unit
def test_rollout_config_valid():
    """Test RolloutConfig with valid stages."""
    config = RolloutConfig(stages=[5, 25, 50, 100])
    assert config.stages == [5, 25, 50, 100]


@pytest.mark.unit
def test_rollout_config_empty_raises():
    """Test RolloutConfig raises on empty stages."""
    with pytest.raises(ValueError, match="at least one"):
        RolloutConfig(stages=[])


@pytest.mark.unit
def test_rollout_config_invalid_percentage_raises():
    """Test RolloutConfig raises on invalid percentage."""
    with pytest.raises(ValueError):
        RolloutConfig(stages=[0.0])


@pytest.mark.unit
def test_rollout_create_and_advance():
    """Test creating and advancing a rollout."""
    mgr = RolloutManager()
    config = RolloutConfig(stages=[10, 50, 100])
    status = mgr.create_rollout("feat-new", config)
    assert status.state == RolloutState.ACTIVE
    assert status.current_percentage == 10

    status = mgr.advance_rollout("feat-new")
    assert status.current_percentage == 50
    assert status.state == RolloutState.ACTIVE

    status = mgr.advance_rollout("feat-new")
    assert status.current_percentage == 100
    assert status.state == RolloutState.ACTIVE

    status = mgr.advance_rollout("feat-new")
    assert status.state == RolloutState.COMPLETED


@pytest.mark.unit
def test_rollout_pause():
    """Test pausing a rollout."""
    mgr = RolloutManager()
    config = RolloutConfig(stages=[10, 50, 100])
    mgr.create_rollout("feat-p", config)
    status = mgr.pause_rollout("feat-p")
    assert status.state == RolloutState.PAUSED


@pytest.mark.unit
def test_rollout_advance_from_paused():
    """Test advancing a paused rollout."""
    mgr = RolloutManager()
    config = RolloutConfig(stages=[10, 50, 100])
    mgr.create_rollout("feat-ap", config)
    mgr.pause_rollout("feat-ap")
    status = mgr.advance_rollout("feat-ap")
    assert status.state == RolloutState.ACTIVE
    assert status.current_percentage == 50


@pytest.mark.unit
def test_rollout_nonexistent_raises():
    """Test accessing nonexistent rollout raises KeyError."""
    mgr = RolloutManager()
    with pytest.raises(KeyError):
        mgr.get_rollout_status("nonexistent")


# ---------------------------------------------------------------------------
# FlagEvaluator and TargetingRule
# ---------------------------------------------------------------------------

@pytest.mark.unit
def test_targeting_rule_eq_matches():
    """Test TargetingRule with eq operator."""
    rule = TargetingRule(attribute="plan", operator="eq", value="enterprise")
    ctx = EvaluationContext(attributes={"plan": "enterprise"})
    assert rule.matches(ctx) is True


@pytest.mark.unit
def test_targeting_rule_eq_no_match():
    """Test TargetingRule with eq operator - no match."""
    rule = TargetingRule(attribute="plan", operator="eq", value="enterprise")
    ctx = EvaluationContext(attributes={"plan": "free"})
    assert rule.matches(ctx) is False


@pytest.mark.unit
def test_targeting_rule_missing_attribute():
    """Test TargetingRule returns False for missing attribute."""
    rule = TargetingRule(attribute="plan", operator="eq", value="enterprise")
    ctx = EvaluationContext(attributes={})
    assert rule.matches(ctx) is False


@pytest.mark.unit
def test_flag_evaluator_disabled_flag():
    """Test FlagEvaluator returns disabled for globally disabled flag."""
    evaluator = FlagEvaluator()
    flag = FlagDefinition(name="disabled-flag", enabled=False)
    ctx = EvaluationContext(user_id="user-1")
    result = evaluator.evaluate(flag, ctx)
    assert result.enabled is False
    assert result.reason == "flag_disabled"


@pytest.mark.unit
def test_flag_evaluator_targeting_rules_match():
    """Test FlagEvaluator passes when targeting rules match."""
    evaluator = FlagEvaluator()
    flag = FlagDefinition(
        name="targeted-flag", enabled=True,
        targeting_rules=[TargetingRule("plan", "eq", "pro")],
    )
    ctx = EvaluationContext(attributes={"plan": "pro"})
    result = evaluator.evaluate(flag, ctx)
    assert result.enabled is True


@pytest.mark.unit
def test_flag_evaluator_targeting_rules_no_match():
    """Test FlagEvaluator disables when targeting rules do not match."""
    evaluator = FlagEvaluator()
    flag = FlagDefinition(
        name="targeted-flag", enabled=True,
        targeting_rules=[TargetingRule("plan", "eq", "pro")],
    )
    ctx = EvaluationContext(attributes={"plan": "free"})
    result = evaluator.evaluate(flag, ctx)
    assert result.enabled is False


@pytest.mark.unit
def test_flag_evaluator_percentage_rollout():
    """Test FlagEvaluator percentage rollout is deterministic."""
    evaluator = FlagEvaluator()
    flag = FlagDefinition(name="pct-flag", enabled=True, percentage=50.0)
    ctx = EvaluationContext(user_id="user-42")
    r1 = evaluator.evaluate(flag, ctx).enabled
    r2 = evaluator.evaluate(flag, ctx).enabled
    assert r1 == r2
