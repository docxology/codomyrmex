"""Tests for ProviderRouter rotation logic.

Zero-Mock Policy: Uses real subclasses and monkeypatch for attribute
injection. No unittest.mock usage.
"""

import time
from pathlib import Path
from typing import Any

import pytest

from codomyrmex.agents.hermes._provider_router import ProviderRouter


@pytest.fixture
def rotation_router(tmp_path: Path) -> ProviderRouter:
    """Build a ProviderRouter with a real rotation config file."""
    router = ProviderRouter(
        primary_provider="openrouter", model="google/gemini-flash-1.5-free"
    )
    rotation_file = tmp_path / "hermes_rotation_test.json"
    rotation_file.write_text(
        """
        {
          "rotation_models": [
            {"provider": "openrouter", "model": "model-1", "priority": 1, "cooldown_seconds": 2},
            {"provider": "openrouter", "model": "model-2", "priority": 2, "cooldown_seconds": 2}
          ]
        }
        """
    )
    router._rotation_path = str(rotation_file)
    return router


def test_rotation_on_429(
    rotation_router: ProviderRouter, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Verify that the router rotates to model-2 if model-1 fails with 429."""

    def side_effect(prompt: str, provider: str, model: str, timeout: int) -> dict[str, Any]:
        if model == "model-1":
            raise RuntimeError("Error 429: Rate limit exceeded")
        return {
            "success": True,
            "content": f"Success from {model}",
            "provider": provider,
            "model": model,
        }

    monkeypatch.setattr(rotation_router, "_dispatch", side_effect)
    res = rotation_router.call_llm("hello")
    assert res["success"] is True
    assert res["model"] == "model-2"
    assert "model-1" in rotation_router._cooldowns


def test_rotation_cooldown(
    rotation_router: ProviderRouter, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Verify that a model in cooldown is skipped."""
    rotation_router._cooldowns["model-1"] = time.time() + 10

    dispatch_calls: list[tuple[str, str, str, int]] = []

    def tracking_dispatch(
        prompt: str, provider: str, model: str, timeout: int
    ) -> dict[str, Any]:
        dispatch_calls.append((prompt, provider, model, timeout))
        return {
            "success": True,
            "content": "Success",
            "provider": "openrouter",
            "model": "model-2",
        }

    monkeypatch.setattr(rotation_router, "_dispatch", tracking_dispatch)
    res = rotation_router.call_llm("hello")

    assert res["model"] == "model-2"
    # Verify model-1 was NEVER called
    for call in dispatch_calls:
        assert call[2] != "model-1"


def test_rotation_all_fail(
    rotation_router: ProviderRouter, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Verify that if all models fail, we return a failure."""

    def always_fail(
        prompt: str, provider: str, model: str, timeout: int
    ) -> None:
        raise RuntimeError("Generic Error")

    monkeypatch.setattr(rotation_router, "_dispatch", always_fail)
    res = rotation_router.call_llm("hello")
    assert res["success"] is False
    assert "Generic Error" in res["error"]
