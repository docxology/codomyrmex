"""validate_api_keys reports key-based providers only."""

from __future__ import annotations

import pytest

from codomyrmex.agents.ai_code_editing.ai_code_helpers.utils import (
    get_supported_providers,
    validate_api_keys,
)


@pytest.mark.unit
def test_ollama_is_supported_without_a_key(monkeypatch: pytest.MonkeyPatch) -> None:
    for name in ("OPENAI_API_KEY", "ANTHROPIC_API_KEY", "GOOGLE_API_KEY"):
        monkeypatch.delenv(name, raising=False)
    monkeypatch.setenv("ANTHROPIC_API_KEY", "set-for-test")  # pragma: allowlist secret

    assert "ollama" in get_supported_providers()
    assert validate_api_keys() == {
        "openai": False,
        "anthropic": True,
        "google": False,
    }
