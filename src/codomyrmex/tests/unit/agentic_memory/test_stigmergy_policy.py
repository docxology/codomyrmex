"""Tests for stigmergy policy helpers."""

from codomyrmex.agentic_memory.stigmergy.policy import (
    boost_importance_value,
    importance_boost_from_trace,
)


def test_boost_importance_value_steps() -> None:
    assert boost_importance_value(1, 0.0) == 1
    assert boost_importance_value(1, 0.3) == 1
    assert boost_importance_value(1, 1.0) == 2
    assert boost_importance_value(3, 3.0) == 4
    assert boost_importance_value(4, 99.0) == 4


def test_importance_boost_from_trace() -> None:
    assert importance_boost_from_trace(0.0) == 0
    assert importance_boost_from_trace(0.4) == 0
    assert importance_boost_from_trace(1.0) == 1
    assert importance_boost_from_trace(3.0, max_bonus_steps=1) == 1
