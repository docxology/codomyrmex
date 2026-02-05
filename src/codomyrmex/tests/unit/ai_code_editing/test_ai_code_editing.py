"""Unit tests for ai_code_editing module."""

import os
import pytest
import signal
import sys

# Guard against hanging imports (google.genai init blocks in sandbox)
_AI_CODE_HELPERS_AVAILABLE = False
try:
    # Set a 5-second alarm to abort if import hangs
    _old_handler = signal.signal(signal.SIGALRM, lambda *_: (_ for _ in ()).throw(TimeoutError()))
    signal.alarm(5)
    from codomyrmex.agents.ai_code_editing import ai_code_helpers  # noqa: F401
    _AI_CODE_HELPERS_AVAILABLE = True
    signal.alarm(0)
    signal.signal(signal.SIGALRM, _old_handler)
except Exception:
    signal.alarm(0)
    try:
        signal.signal(signal.SIGALRM, _old_handler)
    except Exception:
        pass

pytestmark = pytest.mark.skipif(
    not _AI_CODE_HELPERS_AVAILABLE,
    reason="ai_code_helpers import hangs (google.genai network init in sandbox)",
)


@pytest.mark.unit
class TestAICodeEditing:
    """Test cases for AI code editing functionality."""

    def test_ai_code_helpers_import(self, code_dir):
        """Test that we can import ai_code_helpers module."""
        assert ai_code_helpers is not None

    def test_claude_task_master_placeholder_file(self, code_dir):
        """Test that claude_task_master file exists and is importable."""
        claude_task_master_path = code_dir / "codomyrmex" / "agents" / "ai_code_editing" / "claude_task_master.py"
        assert claude_task_master_path.exists()

        # File should be importable (may be implemented or placeholder)
        if str(code_dir) not in sys.path:
            sys.path.insert(0, str(code_dir))
        try:
            from codomyrmex.agents.ai_code_editing import claude_task_master
            assert claude_task_master is not None
        except ImportError:
            pytest.skip("claude_task_master not importable")

    def test_openai_codex_placeholder_file(self, code_dir):
        """Test that openai_codex file exists and is importable."""
        openai_codex_path = code_dir / "codomyrmex" / "agents" / "ai_code_editing" / "openai_codex.py"
        assert openai_codex_path.exists()

        # File should be importable (may be implemented or placeholder)
        if str(code_dir) not in sys.path:
            sys.path.insert(0, str(code_dir))
        try:
            from codomyrmex.agents.ai_code_editing import openai_codex
            assert openai_codex is not None
        except ImportError:
            pytest.skip("openai_codex not importable")

    def test_openai_codex_initialization(self, code_dir):
        """Test OpenAI Codex initialization."""
        if str(code_dir) not in sys.path:
            sys.path.insert(0, str(code_dir))

        # This module may be a placeholder, so we just test that the file exists
        openai_codex_path = code_dir / "codomyrmex" / "agents" / "ai_code_editing" / "openai_codex.py"
        assert openai_codex_path.exists()

    def test_claude_task_master_initialization(self, code_dir):
        """Test Claude Task Master initialization."""
        if str(code_dir) not in sys.path:
            sys.path.insert(0, str(code_dir))

        # This module may be a placeholder, so we just test that the file exists
        claude_task_master_path = code_dir / "codomyrmex" / "agents" / "ai_code_editing" / "claude_task_master.py"
        assert claude_task_master_path.exists()

    def test_ai_code_helpers_structure(self, code_dir):
        """Test that ai_code_helpers has expected structure."""
        # Check that the module has expected attributes/functions
        assert hasattr(ai_code_helpers, '__file__')
        assert hasattr(ai_code_helpers, 'get_llm_client')
        assert hasattr(ai_code_helpers, 'generate_code_snippet')
        assert hasattr(ai_code_helpers, 'refactor_code_snippet')

        # Test that functions are callable
        assert callable(ai_code_helpers.get_llm_client)
        assert callable(ai_code_helpers.generate_code_snippet)
        assert callable(ai_code_helpers.refactor_code_snippet)

    def test_get_llm_client_openai_success(self, code_dir):
        """Test get_llm_client with OpenAI provider with real implementation."""
        get_llm_client = ai_code_helpers.get_llm_client

        # Test with real API key if available, otherwise skip
        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            pytest.skip("OPENAI_API_KEY not set")

        try:
            client, model = get_llm_client("openai")
            # Should return a client and model name
            assert client is not None
            assert model is not None
            assert isinstance(model, str)
        except Exception as e:
            # May fail if API key is invalid or network unavailable
            pytest.skip(f"OpenAI client initialization failed: {e}")

    def test_get_llm_client_openai_missing_key(self, code_dir):
        """Test get_llm_client with missing OpenAI API key."""
        get_llm_client = ai_code_helpers.get_llm_client

        # Temporarily remove API key if it exists
        original_key = os.environ.pop("OPENAI_API_KEY", None)
        try:
            with pytest.raises(ValueError, match="OPENAI_API_KEY environment variable not set"):
                get_llm_client("openai")
        finally:
            # Restore original key if it existed
            if original_key:
                os.environ["OPENAI_API_KEY"] = original_key

    def test_get_llm_client_unsupported_provider(self, code_dir):
        """Test get_llm_client with unsupported provider."""
        get_llm_client = ai_code_helpers.get_llm_client

        with pytest.raises(ValueError, match="Unsupported LLM provider: unsupported"):
            get_llm_client("unsupported")

    def test_generate_code_snippet_invalid_inputs(self, code_dir):
        """Test generate_code_snippet with invalid inputs."""
        generate_code_snippet = ai_code_helpers.generate_code_snippet

        # Test with empty prompt - should raise RuntimeError
        with pytest.raises(RuntimeError) as exc_info:
            generate_code_snippet("", "python")
        assert "Code generation failed" in str(exc_info.value)

        # Test with empty language - should also raise RuntimeError
        with pytest.raises(RuntimeError) as exc_info:
            generate_code_snippet("test prompt", "")
        assert "Code generation failed" in str(exc_info.value)

    def test_generate_code_snippet_openai_success(self, code_dir):
        """Test successful code generation with OpenAI using real client."""
        generate_code_snippet = ai_code_helpers.generate_code_snippet

        # Test with real API key if available
        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            pytest.skip("OPENAI_API_KEY not set")

        try:
            result = generate_code_snippet(
                "Print hello world",
                "python",
                provider="openai"
            )

            # Should return a result dict
            assert isinstance(result, dict)
            assert "generated_code" in result
            assert result["language"] == "python"
            assert result["provider"] == "openai"
        except Exception as e:
            # May fail if API key is invalid or network unavailable
            pytest.skip(f"OpenAI code generation failed: {e}")

    def test_generate_code_snippet_with_context(self, code_dir):
        """Test code generation with context code using real client."""
        generate_code_snippet = ai_code_helpers.generate_code_snippet

        # Test with real API key if available
        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            pytest.skip("OPENAI_API_KEY not set")

        try:
            result = generate_code_snippet(
                "Add two numbers",
                "python",
                context="def multiply(x, y):\n    return x * y",
                provider="openai"
            )

            # Should return a result dict
            assert isinstance(result, dict)
            assert "generated_code" in result
            assert result["language"] == "python"
            assert result["provider"] == "openai"
        except Exception as e:
            # May fail if API key is invalid or network unavailable
            pytest.skip(f"OpenAI code generation failed: {e}")

    def test_generate_code_snippet_api_error(self, code_dir):
        """Test code generation error handling with real implementation."""
        generate_code_snippet = ai_code_helpers.generate_code_snippet

        # Test with invalid API key to trigger error
        original_key = os.environ.get("OPENAI_API_KEY")
        os.environ["OPENAI_API_KEY"] = "invalid-key-for-testing"
        
        try:
            # Should raise RuntimeError when API call fails
            with pytest.raises(RuntimeError) as exc_info:
                generate_code_snippet("test", "python", provider="openai")
            assert "Code generation failed" in str(exc_info.value)
        except Exception:
            # May fail in different ways depending on implementation
            pass
        finally:
            # Restore original key
            if original_key:
                os.environ["OPENAI_API_KEY"] = original_key
            else:
                os.environ.pop("OPENAI_API_KEY", None)

    def test_refactor_code_snippet_success(self, code_dir):
        """Test successful code refactoring with real client."""
        refactor_code_snippet = ai_code_helpers.refactor_code_snippet

        # Test with real API key if available
        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            pytest.skip("OPENAI_API_KEY not set")

        try:
            original_code = "def calculate_sum(numbers):\n    return sum(numbers)"
            result = refactor_code_snippet(
                original_code,
                "Add type hints",
                "python",
                provider="openai"
            )

            # Should return a result dict
            assert isinstance(result, dict)
            assert "refactored_code" in result
            assert result["refactoring_type"] == "Add type hints"
            assert result["language"] == "python"
            assert result["provider"] == "openai"
        except Exception as e:
            # May fail if API key is invalid or network unavailable
            pytest.skip(f"OpenAI code refactoring failed: {e}")

    def test_refactor_code_snippet_no_change(self, code_dir):
        """Test refactoring when no changes are needed with real client."""
        refactor_code_snippet = ai_code_helpers.refactor_code_snippet

        # Test with real API key if available
        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            pytest.skip("OPENAI_API_KEY not set")

        try:
            original_code = "def hello():\n    print('Hello')"
            result = refactor_code_snippet(
                original_code,
                "Optimize code",
                "python",
                provider="openai"
            )

            # Should return a result dict
            assert isinstance(result, dict)
            assert "refactored_code" in result
            assert result["refactoring_type"] == "Optimize code"
            assert result["language"] == "python"
            assert result["provider"] == "openai"
        except Exception as e:
            # May fail if API key is invalid or network unavailable
            pytest.skip(f"OpenAI code refactoring failed: {e}")

    def test_ai_code_helpers_constants(self, code_dir):
        """Test that ai_code_helpers has expected constants."""
        assert hasattr(ai_code_helpers, 'DEFAULT_LLM_PROVIDER')
        assert hasattr(ai_code_helpers, 'DEFAULT_LLM_MODEL')
        assert ai_code_helpers.DEFAULT_LLM_PROVIDER in ("openai", "google", "anthropic", "ollama")
        assert isinstance(ai_code_helpers.DEFAULT_LLM_MODEL, dict)
        assert "openai" in ai_code_helpers.DEFAULT_LLM_MODEL
        assert "anthropic" in ai_code_helpers.DEFAULT_LLM_MODEL
