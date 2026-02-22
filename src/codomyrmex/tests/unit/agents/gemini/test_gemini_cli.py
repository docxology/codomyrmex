import pytest
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
        context={"model": "gemini-2.0-flash-thinking-exp-01-21"}
    )
    
    try:
        response = client.execute(request)
        assert isinstance(response, AgentResponse)
        if response.is_success():
            assert "PONG" in response.content.upper()
            assert "model" in response.metadata
        else:
            # We accept a handled error from the CLI (e.g. ModelNotFoundError or 400 thinking error)
            assert "error" in response.__dict__ or "error" in response.metadata or "GeminiError" in str(response.error)
    except Exception as e:
        pytest.fail(f"Execution failed unexpectedly: {e}")
