import time
from unittest.mock import (
    patch,
)

import pytest

from codomyrmex.agents.hermes._provider_router import ProviderRouter


@pytest.fixture
def mock_router():
    router = ProviderRouter(primary_provider="openrouter", model="google/gemini-flash-1.5-free")
    router._rotation_path = "/tmp/hermes_rotation_test.json"
    with open(router._rotation_path, "w") as f:
        f.write("""
        {
          "rotation_models": [
            {"provider": "openrouter", "model": "model-1", "priority": 1, "cooldown_seconds": 2},
            {"provider": "openrouter", "model": "model-2", "priority": 2, "cooldown_seconds": 2}
          ]
        }
        """)
    return router

def test_rotation_on_429(mock_router):
    """Verify that the router rotates to model-2 if model-1 fails with 429."""
    # Mock _dispatch to fail for model-1 with a simulated 429 error message
    # but succeed for model-2
    def side_effect(prompt, provider, model, timeout):
        if model == "model-1":
            raise RuntimeError("Error 429: Rate limit exceeded")
        return {"success": True, "content": f"Success from {model}", "provider": provider, "model": model}

    with patch.object(mock_router, "_dispatch", side_effect=side_effect):
        res = mock_router.call_llm("hello")
        assert res["success"] is True
        assert res["model"] == "model-2"
        assert "model-1" in mock_router._cooldowns

def test_rotation_cooldown(mock_router):
    """Verify that a model in cooldown is skipped."""
    mock_router._cooldowns["model-1"] = time.time() + 10

    with patch.object(mock_router, "_dispatch") as mock_dispatch:
        mock_dispatch.return_value = {"success": True, "content": "Success", "provider": "openrouter", "model": "model-2"}
        res = mock_router.call_llm("hello")

        assert res["model"] == "model-2"
        # Verify model-1 was NEVER called
        for call in mock_dispatch.call_args_list:
            assert call.args[2] != "model-1"

def test_rotation_all_fail(mock_router):
    """Verify that if all models fail, we return a failure."""
    with patch.object(mock_router, "_dispatch", side_effect=RuntimeError("Generic Error")):
        res = mock_router.call_llm("hello")
        assert res["success"] is False
        assert "Generic Error" in res["error"]
