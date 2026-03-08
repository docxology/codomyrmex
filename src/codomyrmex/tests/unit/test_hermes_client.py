"""Tests for agents.hermes.hermes_client — HermesClient dual-backend.

Zero-Mock: Tests verify real client instantiation and method signatures.
Backend-dependent tests use skipif for Ollama availability.
"""

from __future__ import annotations

import pytest

from codomyrmex.agents.hermes.hermes_client import HermesClient

# ── Client instantiation ─────────────────────────────────────────────


class TestHermesClientInit:
    """Verify client initialization and backend selection."""

    def test_default_init(self) -> None:
        client = HermesClient()
        assert client is not None

    def test_active_backend_property(self) -> None:
        client = HermesClient()
        backend = client.active_backend
        assert backend in ("cli", "ollama", "none")

    def test_repr(self) -> None:
        client = HermesClient()
        r = repr(client)
        assert "HermesClient" in r


class TestHermesClientMethods:
    """Verify client method signatures exist and are callable."""

    def test_list_skills_returns_dict(self) -> None:
        client = HermesClient()
        skills = client.list_skills()
        assert isinstance(skills, dict)

    def test_get_hermes_status(self) -> None:
        client = HermesClient()
        status = client.get_hermes_status()
        assert isinstance(status, dict)

    @pytest.mark.skipif(
        HermesClient().active_backend == "none",
        reason="No Hermes backend available",
    )
    def test_execute_returns_response(self) -> None:
        """Execute a simple prompt if a backend is available.

        Note: HermesClient.execute() requires an AgentRequest object,
        not a plain string. This test validates the end-to-end flow.
        """
        from codomyrmex.agents.core.base import AgentRequest

        client = HermesClient()
        request = AgentRequest(prompt="What is 2+2?")
        response = client.execute(request)
        assert response is not None
