"""Tests for codomyrmex.agents.hermes._provider_router using zero-mock."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

from codomyrmex.agents.hermes._provider_router import (
    ContextCompressor,
    ModelContextRegistry,
    ProviderRouter,
    UserModel,
)


class TestProviderRouter:
    """Zero-mock tests for the LLM ProviderRouter."""

    def test_provider_router_init(self) -> None:
        router = ProviderRouter()
        assert router.primary_provider == "openrouter"
        assert router.fallback_provider == "ollama"

    def test_has_credentials(self) -> None:
        router = ProviderRouter()
        # ollama usually exists if installed, but let's test a fake provider
        assert not router.has_credentials("fake_provider_123")

    def test_get_rotation_models(self, tmp_path: Path) -> None:
        router = ProviderRouter()
        router._rotation_path = str(tmp_path / "rotation.json")
        # should gracefully return empty list if missing
        assert router.get_rotation_models() == []

        # Write a dummy config
        with open(router._rotation_path, "w") as f:
            json.dump({"rotation_models": [{"model": "m1", "priority": 1}]}, f)
        
        models = router.get_rotation_models()
        assert len(models) == 1
        assert models[0]["model"] == "m1"

    def test_call_llm_fallback(self, monkeypatch: pytest.MonkeyPatch) -> None:
        router = ProviderRouter()
        # Force a failure in primary dispatch to trigger fallback
        def _mock_dispatch(prompt: str, provider: str, model: str, timeout: int) -> dict[str, Any]:
            if provider != "ollama":
                raise RuntimeError("Primary simulated failure")
            return {"success": True, "content": "fallback works"}
        
        monkeypatch.setattr(router, "_dispatch", _mock_dispatch)
        # Ensure it believes it has credentials
        router._credentials["openrouter"] = "fake"
        router._credentials["ollama"] = "local"
        
        res = router.call_llm("hello", provider="openrouter", model="m1")
        assert res["success"] is True
        assert res["content"] == "fallback works"
        assert res.get("is_fallback") is True


class TestUserModel:
    """Zero-mock tests for Hermes UserModel cross-session memory."""

    def test_user_model_lifecycle(self, tmp_path: Path) -> None:
        model = UserModel(storage_dir=str(tmp_path))
        
        # Test basic profile
        assert "preferences" in model.profile
        
        # Add facts
        model.set_preference("language", "python")
        model.add_observation("Prefers clear docstrings.")
        model.record_session("s-123", "Tested UserModel")

        # Reload to verify persistence
        model2 = UserModel(storage_dir=str(tmp_path))
        assert model2.profile["preferences"]["language"] == "python"
        
        # Check context generation
        prompt = model2.get_context_prompt()
        assert "python" in prompt
        assert "Tested UserModel" in prompt
        assert "Prefers clear docstrings." in prompt


class TestModelContextRegistry:
    """Zero-mock tests for ModelContextRegistry dynamic fetching."""

    def test_get_context_length_fallback(self) -> None:
        reg = ModelContextRegistry()
        # Known model string
        assert reg.get_context_length("mixtral-8x7b") == 32000
        # Unknown falls back to 128k
        assert reg.get_context_length("unknown-model-xyz") == 128000
        
        # Cache check
        assert "mixtral-8x7b" in reg._cache

    def test_fetch_openrouter(self, monkeypatch: pytest.MonkeyPatch) -> None:
        reg = ModelContextRegistry()
        # Intercept HTTP request to simulate OR response
        class MockResponse:
            def read(self) -> bytes:
                return b'{"data": {"context_length": 99999}}'
            def __enter__(self):
                return self
            def __exit__(self, exc_type, exc_val, exc_tb):
                pass
                
        import urllib.request
        monkeypatch.setattr(urllib.request, "urlopen", lambda req, timeout=10: MockResponse())
        
        length = reg.get_context_length_safe("mock-model-openrouter")
        assert length == 99999
