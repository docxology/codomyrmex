"""Tests for ProviderRouter rotation logic.

Zero-Mock Policy: Uses real subclasses and monkeypatch for attribute
injection. No unittest.mock usage.
"""

import time
from pathlib import Path
from typing import Any

import pytest

from codomyrmex.agents.hermes.provider_router_pkg import ProviderRouter


@pytest.fixture
def rotation_router(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> ProviderRouter:
    """Build a ProviderRouter with a real rotation config file."""
    hermes_home = tmp_path / "hermes-home"
    hermes_home.mkdir()
    monkeypatch.setenv("HERMES_HOME", str(hermes_home))
    for variable in (
        "OPENROUTER_API_KEY",
        "NOUS_API_KEY",
        "OPENAI_API_KEY",
        "ANTHROPIC_API_KEY",
        "ZAI_API_KEY",
    ):
        monkeypatch.delenv(variable, raising=False)
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
    return ProviderRouter(
        primary_provider="openrouter",
        model="google/gemini-flash-1.5-free",
        env_path=str(hermes_home / ".env"),
        rotation_path=str(rotation_file),
    )


def test_constructor_isolates_rotation_and_credentials_before_io(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Recognized home and explicit paths take effect before constructor I/O."""
    home = tmp_path / "hermes-home"
    home.mkdir()
    monkeypatch.setenv("HERMES_HOME", str(home))
    for variable in (
        "OPENROUTER_API_KEY",
        "NOUS_API_KEY",
        "OPENAI_API_KEY",
        "ANTHROPIC_API_KEY",
        "ZAI_API_KEY",
    ):
        monkeypatch.delenv(variable, raising=False)
    (home / ".env").write_text(
        "OPENROUTER_API_KEY=unit-only-default\n"  # pragma: allowlist secret
    )
    default = ProviderRouter()
    assert default._env_path == str(home / ".env")
    assert default._rotation_path == str(home / "rotation.json")
    assert default.has_credentials("openrouter")
    assert (home / "rotation.json").is_file()

    explicit_env = tmp_path / "explicit.env"
    explicit_env.write_text(
        "OPENROUTER_API_KEY=unit-only-explicit\n"  # pragma: allowlist secret
    )
    explicit_rotation = tmp_path / "explicit" / "rotation.json"
    router = ProviderRouter(
        env_path=str(explicit_env), rotation_path=str(explicit_rotation)
    )
    assert router._env_path == str(explicit_env)
    assert router._rotation_path == str(explicit_rotation)
    assert router.has_credentials("openrouter")
    assert explicit_rotation.is_file()

    monkeypatch.chdir(tmp_path)
    relative = ProviderRouter(env_path=str(explicit_env), rotation_path="rotation.json")
    assert relative._rotation_path == "rotation.json"
    assert (tmp_path / "rotation.json").is_file()


def test_rotation_on_429(
    rotation_router: ProviderRouter, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Verify that the router rotates to model-2 if model-1 fails with 429."""

    def side_effect(
        prompt: str, provider: str, model: str, timeout: int
    ) -> dict[str, Any]:
        if model == "model-1":
            raise RuntimeError("Error 429: Rate limit exceeded")
        return {
            "success": True,
            "content": f"Success from {model}",
            "provider": provider,
            "model": model,
        }

    monkeypatch.setattr(rotation_router, "_dispatch", side_effect)
    res = rotation_router.call_llm("hello", provider="openrouter")
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
    res = rotation_router.call_llm("hello", provider="openrouter")

    assert res["model"] == "model-2"
    # Verify model-1 was NEVER called
    for call in dispatch_calls:
        assert call[2] != "model-1"


def test_rotation_all_fail(
    rotation_router: ProviderRouter, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Verify that if all models fail, we return a failure."""

    def always_fail(prompt: str, provider: str, model: str, timeout: int) -> None:
        raise RuntimeError("Generic Error")

    monkeypatch.setattr(rotation_router, "_dispatch", always_fail)
    res = rotation_router.call_llm("hello", provider="openrouter")
    assert res["success"] is False
    assert "Generic Error" in res["error"]
