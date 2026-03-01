"""Zero-Mock tests for OllamaClient session management.

Documents the unimplemented state of session management per zero-mock policy.
These tests verify that the production code explicitly raises NotImplementedError
rather than silently returning placeholder data.
"""

import pytest

from codomyrmex.agents.llm_client import OllamaClient


@pytest.mark.unit
class TestOllamaClientSession:
    """Test suite for OllamaClient session create/close."""

    def test_create_session_raises_not_implemented(self):
        """create_session raises NotImplementedError — not yet implemented."""
        client = OllamaClient()
        with pytest.raises(NotImplementedError, match="LLM session management not implemented"):
            client.create_session("sess_1")

    def test_session_manager_is_none_by_default(self):
        """session_manager starts as None since session management is unimplemented."""
        client = OllamaClient()
        assert client.session_manager is None

    def test_create_session_multiple_calls_all_raise(self):
        """Every call to create_session raises NotImplementedError."""
        client = OllamaClient()
        with pytest.raises(NotImplementedError):
            client.create_session("a")
        with pytest.raises(NotImplementedError):
            client.create_session("b")

    def test_close_session_not_implemented(self):
        """close_session is not yet part of the OllamaClient interface."""
        client = OllamaClient()
        assert not hasattr(client, "close_session"), (
            "close_session should not exist until session management is implemented"
        )
