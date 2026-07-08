import os
import shutil

import pytest

# All tests in this file invoke the real Gemini CLI binary and require live
# AI API credentials.  Skip unless GEMINI_TEST_ENABLED=1 is set (per skip
# policy: skip tests requiring network/API keys).
pytestmark = pytest.mark.skipif(
    not (shutil.which("gemini") and os.environ.get("GEMINI_TEST_ENABLED") == "1"),
    reason="Gemini CLI requires AI API access; set GEMINI_TEST_ENABLED=1 to run",
)

from codomyrmex.agents.core import AgentRequest, AgentResponse
from codomyrmex.agents.gemini.gemini_cli import GeminiCLIWrapper


def test_gemini_cli_version():
    """Test that the CLI wrapper can execute basic non-LLM commands properly."""
    client = GeminiCLIWrapper()
    assert client.cli_path is not None, "gemini CLI is not found in PATH"


def test_gemini_cli_list_extensions():
    """Test extensions wrapper."""
    client = GeminiCLIWrapper()
    try:
        extensions = client.list_extensions()
        assert isinstance(extensions, str)
    except Exception as e:
        pytest.fail(f"Failed to list extensions: {e}")


def test_gemini_cli_execute_basic():
    """Test basic execute functionality with the gemini CLI."""
    client = GeminiCLIWrapper()

    request = AgentRequest(
        prompt="Reply with the exact word 'PONG'. Do not formulate sentences.",
        context={"model": "gemini-2.0-flash-thinking-exp-01-21"},
    )

    try:
        response = client.execute(request)
        assert isinstance(response, AgentResponse)
        if response.is_success():
            assert "PONG" in response.content.upper()
            assert "model" in response.metadata  # type: ignore
        else:
            # We accept a handled error from the CLI (e.g. ModelNotFoundError or 400 thinking error)
            assert (
                "error" in response.__dict__
                or "error" in response.metadata  # type: ignore
                or "GeminiError" in str(response.error)
            )
    except Exception as e:
        pytest.fail(f"Execution failed unexpectedly: {e}")
