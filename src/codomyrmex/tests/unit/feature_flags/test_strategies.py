"""Tests for feature flag evaluation strategies.

Tests PercentageStrategy, UserListStrategy, and TimeWindowStrategy
with real inputs -- no mocks, no stubs, no fakes.
"""

from __future__ import annotations

import hashlib
from datetime import datetime, timedelta

import pytest

from codomyrmex.feature_flags.strategies import (
    EvaluationContext,
    PercentageStrategy,
    TimeWindowStrategy,
    UserListStrategy,
    create_strategy,
)

# ---------------------------------------------------------------------------
# PercentageStrategy tests
# ---------------------------------------------------------------------------


class TestPercentageStrategy:
    """Tests for deterministic percentage-based rollout."""

    def test_zero_percentage_always_disabled(self):
        """A 0% rollout should never enable the flag."""
        strategy = PercentageStrategy(percentage=0.0)
        context = EvaluationContext(user_id="user-123")
        result = strategy.evaluate(context)
        assert result.enabled is False

    def test_hundred_percentage_always_enabled(self):
        """A 100% rollout should always enable the flag."""
        strategy = PercentageStrategy(percentage=100.0)
        context = EvaluationContext(user_id="user-123")
        result = strategy.evaluate(context)
        assert result.enabled is True

    def test_deterministic_for_same_user(self):
        """Same user should get the same result on repeated evaluations."""
        strategy = PercentageStrategy(percentage=50.0, sticky=True)
        context = EvaluationContext(user_id="deterministic-user")
        results = [strategy.evaluate(context).enabled for _ in range(10)]
        # All results must be identical -- deterministic hashing
        assert len(set(results)) == 1

    def test_different_users_get_different_buckets(self):
        """With enough users, some should be enabled and some disabled at 50%."""
        strategy = PercentageStrategy(percentage=50.0, sticky=True)
        enabled_count = 0
        total = 200
        for i in range(total):
            context = EvaluationContext(user_id=f"user-{i}")
            if strategy.evaluate(context).enabled:
                enabled_count += 1
        # Expect roughly 50% enabled -- allow 30-70% range for statistical safety
        assert 30 <= enabled_count <= 140, (
            f"Expected ~100 enabled out of {total}, got {enabled_count}"
        )

    def test_percentage_clamped_above_100(self):
        """Percentage above 100 should be clamped to 100."""
        strategy = PercentageStrategy(percentage=150.0)
        assert strategy.percentage == 100.0

    def test_percentage_clamped_below_zero(self):
        """Percentage below 0 should be clamped to 0."""
        strategy = PercentageStrategy(percentage=-10.0)
        assert strategy.percentage == 0.0

    def test_metadata_includes_percentage(self):
        """Result metadata should include the configured percentage."""
        strategy = PercentageStrategy(percentage=25.0)
        context = EvaluationContext(user_id="meta-user")
        result = strategy.evaluate(context)
        assert result.metadata["percentage"] == 25.0

    def test_serialization_roundtrip(self):
        """to_dict / from_dict should preserve strategy configuration."""
        original = PercentageStrategy(percentage=42.0, sticky=False)
        data = original.to_dict()
        restored = PercentageStrategy.from_dict(data)
        assert restored.percentage == 42.0
        assert restored.sticky is False


# ---------------------------------------------------------------------------
# UserListStrategy tests
# ---------------------------------------------------------------------------


class TestUserListStrategy:
    """Tests for user allowlist/blocklist strategy."""

    def test_allowed_user_is_enabled(self):
        """A user on the allowlist should have the flag enabled."""
        strategy = UserListStrategy(allowed_users=["alice", "bob"])
        context = EvaluationContext(user_id="alice")
        result = strategy.evaluate(context)
        assert result.enabled is True
        assert result.reason == "allowed_user"

    def test_unknown_user_gets_default(self):
        """A user not on any list gets the default value."""
        strategy = UserListStrategy(
            allowed_users=["alice"],
            default=False,
        )
        context = EvaluationContext(user_id="charlie")
        result = strategy.evaluate(context)
        assert result.enabled is False
        assert result.reason == "default"

    def test_blocked_user_is_disabled(self):
        """A user on the blocklist should have the flag disabled."""
        strategy = UserListStrategy(
            allowed_users=["alice", "bob"],
            blocked_users=["alice"],
        )
        context = EvaluationContext(user_id="alice")
        result = strategy.evaluate(context)
        # Blocked takes precedence over allowed
        assert result.enabled is False
        assert result.reason == "blocked_user"

    def test_no_user_id_returns_default(self):
        """When no user_id is present, should return default."""
        strategy = UserListStrategy(allowed_users=["alice"], default=True)
        context = EvaluationContext()  # no user_id
        result = strategy.evaluate(context)
        assert result.enabled is True
        assert result.reason == "no_user_id"

    def test_add_user_adds_to_allowlist(self):
        """add_user should make a user pass the allowlist check."""
        strategy = UserListStrategy(allowed_users=[])
        strategy.add_user("new-user")
        context = EvaluationContext(user_id="new-user")
        result = strategy.evaluate(context)
        assert result.enabled is True

    def test_block_user_overrides_allowed(self):
        """Blocking a user who is also allowed should disable the flag."""
        strategy = UserListStrategy(allowed_users=["user-x"])
        strategy.block_user("user-x")
        context = EvaluationContext(user_id="user-x")
        result = strategy.evaluate(context)
        assert result.enabled is False

    def test_set_based_lookup_performance(self):
        """Allowlist uses set for O(1) lookup -- verify large lists work."""
        users = [f"user-{i}" for i in range(10000)]
        strategy = UserListStrategy(allowed_users=users)
        # Check last user
        context = EvaluationContext(user_id="user-9999")
        result = strategy.evaluate(context)
        assert result.enabled is True

    def test_serialization_roundtrip(self):
        """to_dict / from_dict should preserve strategy configuration."""
        original = UserListStrategy(
            allowed_users=["a", "b"],
            blocked_users=["c"],
            default=True,
        )
        data = original.to_dict()
        restored = UserListStrategy.from_dict(data)
        assert restored.default is True
        assert "a" in restored.allowed_users
        assert "c" in restored.blocked_users


# ---------------------------------------------------------------------------
# TimeWindowStrategy tests
# ---------------------------------------------------------------------------


class TestTimeWindowStrategy:
    """Tests for time-window based feature flag strategy."""

    def test_enabled_within_window(self):
        """Flag should be enabled when evaluated within the time window."""
        now = datetime.now()
        strategy = TimeWindowStrategy(
            start_time=now - timedelta(hours=1),
            end_time=now + timedelta(hours=1),
        )
        context = EvaluationContext(timestamp=now)
        result = strategy.evaluate(context)
        assert result.enabled is True
        assert result.reason == "time_window_active"

    def test_disabled_before_window(self):
        """Flag should be disabled when evaluated before the window opens."""
        future_start = datetime.now() + timedelta(days=1)
        future_end = future_start + timedelta(hours=2)
        strategy = TimeWindowStrategy(
            start_time=future_start,
            end_time=future_end,
        )
        context = EvaluationContext(timestamp=datetime.now())
        result = strategy.evaluate(context)
        assert result.enabled is False
        assert result.reason == "time_window_inactive"

    def test_disabled_after_window(self):
        """Flag should be disabled when evaluated after the window closes."""
        past_start = datetime.now() - timedelta(days=2)
        past_end = datetime.now() - timedelta(days=1)
        strategy = TimeWindowStrategy(
            start_time=past_start,
            end_time=past_end,
        )
        context = EvaluationContext(timestamp=datetime.now())
        result = strategy.evaluate(context)
        assert result.enabled is False
        assert result.reason == "time_window_inactive"

    def test_enabled_at_exact_start_boundary(self):
        """Flag should be enabled at exactly start_time (inclusive)."""
        start = datetime(2026, 6, 15, 12, 0, 0)
        end = datetime(2026, 6, 15, 18, 0, 0)
        strategy = TimeWindowStrategy(start_time=start, end_time=end)
        context = EvaluationContext(timestamp=start)
        result = strategy.evaluate(context)
        assert result.enabled is True

    def test_enabled_at_exact_end_boundary(self):
        """Flag should be enabled at exactly end_time (inclusive)."""
        start = datetime(2026, 6, 15, 12, 0, 0)
        end = datetime(2026, 6, 15, 18, 0, 0)
        strategy = TimeWindowStrategy(start_time=start, end_time=end)
        context = EvaluationContext(timestamp=end)
        result = strategy.evaluate(context)
        assert result.enabled is True

    def test_invalid_window_raises(self):
        """end_time before start_time should raise ValueError."""
        now = datetime.now()
        with pytest.raises(ValueError, match="end_time.*must be after.*start_time"):
            TimeWindowStrategy(
                start_time=now + timedelta(hours=1),
                end_time=now,
            )

    def test_metadata_includes_timestamps(self):
        """Result metadata should include start, end, and evaluation time."""
        start = datetime(2026, 3, 1, 0, 0, 0)
        end = datetime(2026, 3, 2, 0, 0, 0)
        strategy = TimeWindowStrategy(start_time=start, end_time=end)
        eval_time = datetime(2026, 3, 1, 12, 0, 0)
        context = EvaluationContext(timestamp=eval_time)
        result = strategy.evaluate(context)
        assert result.metadata["start_time"] == start.isoformat()
        assert result.metadata["end_time"] == end.isoformat()
        assert result.metadata["evaluated_at"] == eval_time.isoformat()

    def test_serialization_roundtrip(self):
        """to_dict / from_dict should preserve strategy configuration."""
        start = datetime(2026, 1, 1, 0, 0, 0)
        end = datetime(2026, 12, 31, 23, 59, 59)
        original = TimeWindowStrategy(start_time=start, end_time=end)
        data = original.to_dict()
        assert data["type"] == "time_window"
        restored = TimeWindowStrategy.from_dict(data)
        assert restored.start_time == start
        assert restored.end_time == end

    def test_factory_creates_time_window(self):
        """create_strategy should handle time_window type."""
        start = datetime(2026, 6, 1, 0, 0, 0)
        end = datetime(2026, 6, 30, 23, 59, 59)
        data = {
            "type": "time_window",
            "start_time": start.isoformat(),
            "end_time": end.isoformat(),
        }
        strategy = create_strategy(data)
        assert isinstance(strategy, TimeWindowStrategy)
        assert strategy.start_time == start
        assert strategy.end_time == end

    def test_equal_start_and_end_raises(self):
        """Identical start and end times should raise ValueError."""
        now = datetime.now()
        with pytest.raises(ValueError):
            TimeWindowStrategy(start_time=now, end_time=now)
