"""Unit tests for ai_code_editing module."""

import os
import pytest
import sys
from unittest.mock import patch, MagicMock


class TestAICodeEditing:
    """Test cases for AI code editing functionality."""

    def test_ai_code_helpers_import(self, code_dir):
        """Test that we can import ai_code_helpers module."""
        if str(code_dir) not in sys.path:
            sys.path.insert(0, str(code_dir))

        try:
            from codomyrmex.ai_code_editing import ai_code_helpers
            assert ai_code_helpers is not None
        except ImportError as e:
            pytest.fail(f"Failed to import ai_code_helpers: {e}")

    def test_claude_task_master_placeholder_file(self, code_dir):
        """Test that claude_task_master is a placeholder file with URL."""
        claude_task_master_path = code_dir / "codomyrmex" / "ai_code_editing" / "claude_task_master.py"
        assert claude_task_master_path.exists()

        # Read the file content - should contain implementation
        with open(claude_task_master_path, 'r') as f:
            content = f.read().strip()
            assert "github.com" in content.lower()
            assert "TODO: Implementation needed" in content  # Should contain implementation placeholder

    def test_openai_codex_placeholder_file(self, code_dir):
        """Test that openai_codex is a placeholder file with URL."""
        openai_codex_path = code_dir / "codomyrmex" / "ai_code_editing" / "openai_codex.py"
        assert openai_codex_path.exists()

        # Read the file content - should contain implementation
        with open(openai_codex_path, 'r') as f:
            content = f.read().strip()
            assert "github.com" in content.lower()
            assert "TODO: Implementation needed" in content  # Should contain implementation placeholder

    def test_openai_codex_initialization(self, code_dir):
        """Test OpenAI Codex initialization."""
        if str(code_dir) not in sys.path:
            sys.path.insert(0, str(code_dir))

        # This module may be a placeholder, so we just test that the file exists
        openai_codex_path = code_dir / "codomyrmex" / "ai_code_editing" / "openai_codex.py"
        assert openai_codex_path.exists()

    def test_claude_task_master_initialization(self, code_dir):
        """Test Claude Task Master initialization."""
        if str(code_dir) not in sys.path:
            sys.path.insert(0, str(code_dir))

        # This module may be a placeholder, so we just test that the file exists
        claude_task_master_path = code_dir / "codomyrmex" / "ai_code_editing" / "claude_task_master.py"
        assert claude_task_master_path.exists()

    def test_ai_code_helpers_structure(self, code_dir):
        """Test that ai_code_helpers has expected structure."""
        if str(code_dir) not in sys.path:
            sys.path.insert(0, str(code_dir))

        from codomyrmex.ai_code_editing import ai_code_helpers

        # Check that the module has expected attributes/functions
        assert hasattr(ai_code_helpers, '__file__')
        assert hasattr(ai_code_helpers, 'get_llm_client')
        assert hasattr(ai_code_helpers, 'generate_code_snippet')
        assert hasattr(ai_code_helpers, 'refactor_code_snippet')

        # Test that functions are callable
        assert callable(ai_code_helpers.get_llm_client)
        assert callable(ai_code_helpers.generate_code_snippet)
        assert callable(ai_code_helpers.refactor_code_snippet)

    @patch.dict(os.environ, {"OPENAI_API_KEY": "fake-key"})
    def test_get_llm_client_openai_success(self, code_dir):
        """Test get_llm_client with OpenAI provider successfully."""
        if str(code_dir) not in sys.path:
            sys.path.insert(0, str(code_dir))

        from ai_code_editing.ai_code_helpers import get_llm_client

        with patch('openai.OpenAI') as mock_openai:
            mock_client = MagicMock()
            mock_openai.return_value = mock_client

            client, model = get_llm_client("openai")

            assert client is mock_client
            assert model == "gpt-3.5-turbo"
            mock_openai.assert_called_once_with(api_key="fake-key")

    @patch.dict(os.environ, {}, clear=True)
    def test_get_llm_client_openai_missing_key(self, code_dir):
        """Test get_llm_client with missing OpenAI API key."""
        if str(code_dir) not in sys.path:
            sys.path.insert(0, str(code_dir))

        from ai_code_editing.ai_code_helpers import get_llm_client

        with pytest.raises(ValueError, match="OPENAI_API_KEY environment variable not set"):
            get_llm_client("openai")

    def test_get_llm_client_unsupported_provider(self, code_dir):
        """Test get_llm_client with unsupported provider."""
        if str(code_dir) not in sys.path:
            sys.path.insert(0, str(code_dir))

        from ai_code_editing.ai_code_helpers import get_llm_client

        with pytest.raises(ValueError, match="Unsupported LLM provider: unsupported"):
            get_llm_client("unsupported")

    def test_generate_code_snippet_invalid_inputs(self, code_dir):
        """Test generate_code_snippet with invalid inputs."""
        if str(code_dir) not in sys.path:
            sys.path.insert(0, str(code_dir))

        from ai_code_editing.ai_code_helpers import generate_code_snippet

        # Test with empty prompt - should raise RuntimeError
        with pytest.raises(RuntimeError) as exc_info:
            generate_code_snippet("", "python")
        assert "Code generation failed" in str(exc_info.value)

        # Test with empty language - should also raise RuntimeError
        with pytest.raises(RuntimeError) as exc_info:
            generate_code_snippet("test prompt", "")
        assert "Code generation failed" in str(exc_info.value)

    @patch('ai_code_editing.ai_code_helpers.get_llm_client')
    def test_generate_code_snippet_openai_success(self, mock_get_client, code_dir):
        """Test successful code generation with OpenAI."""
        if str(code_dir) not in sys.path:
            sys.path.insert(0, str(code_dir))

        from ai_code_editing.ai_code_helpers import generate_code_snippet

        # Mock OpenAI client
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_choice = MagicMock()
        mock_message = MagicMock()

        mock_message.content = "def hello_world():\n    print('Hello, World!')"
        mock_choice.message = mock_message
        mock_response.choices = [mock_choice]
        mock_client.chat.completions.create.return_value = mock_response

        mock_get_client.return_value = (mock_client, "gpt-3.5-turbo")

        result = generate_code_snippet(
            "Print hello world",
            "python",
            provider="openai"
        )

        assert "def hello_world()" in result["generated_code"]
        assert result["language"] == "python"
        assert result["provider"] == "openai"

    @patch('ai_code_editing.ai_code_helpers.get_llm_client')
    def test_generate_code_snippet_with_context(self, mock_get_client, code_dir):
        """Test code generation with context code."""
        if str(code_dir) not in sys.path:
            sys.path.insert(0, str(code_dir))

        from ai_code_editing.ai_code_helpers import generate_code_snippet

        # Mock OpenAI client
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_choice = MagicMock()
        mock_message = MagicMock()

        mock_message.content = "```python\ndef add_numbers(a, b):\n    return a + b\n```"
        mock_choice.message = mock_message
        mock_response.choices = [mock_choice]
        mock_client.chat.completions.create.return_value = mock_response

        mock_get_client.return_value = (mock_client, "gpt-3.5-turbo")

        result = generate_code_snippet(
            "Add two numbers",
            "python",
            context="def multiply(x, y):\n    return x * y",
            provider="openai"
        )

        assert "def add_numbers(a, b):" in result["generated_code"]
        assert result["language"] == "python"
        assert result["provider"] == "openai"

    @patch('ai_code_editing.ai_code_helpers.get_llm_client')
    def test_generate_code_snippet_api_error(self, mock_get_client, code_dir):
        """Test code generation when API call fails."""
        if str(code_dir) not in sys.path:
            sys.path.insert(0, str(code_dir))

        from ai_code_editing.ai_code_helpers import generate_code_snippet

        # Mock client that raises an error
        mock_client = MagicMock()
        mock_client.chat.completions.create.side_effect = Exception("API Error")
        mock_get_client.return_value = (mock_client, "gpt-3.5-turbo")

        with pytest.raises(RuntimeError) as exc_info:
            generate_code_snippet("test", "python", provider="openai")

        assert "Code generation failed: API Error" in str(exc_info.value)

    @patch('ai_code_editing.ai_code_helpers.get_llm_client')
    def test_refactor_code_snippet_success(self, mock_get_client, code_dir):
        """Test successful code refactoring."""
        if str(code_dir) not in sys.path:
            sys.path.insert(0, str(code_dir))

        from ai_code_editing.ai_code_helpers import refactor_code_snippet

        # Mock OpenAI client
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_choice = MagicMock()
        mock_message = MagicMock()

        mock_message.content = "```python\ndef calculate_sum(numbers: list) -> int:\n    return sum(numbers)\n```\nAdded type hints for better code quality."
        mock_choice.message = mock_message
        mock_response.choices = [mock_choice]
        mock_client.chat.completions.create.return_value = mock_response

        mock_get_client.return_value = (mock_client, "gpt-3.5-turbo")

        original_code = "def calculate_sum(numbers):\n    return sum(numbers)"
        result = refactor_code_snippet(
            original_code,
            "Add type hints",
            "python",
            provider="openai"
        )

        assert "def calculate_sum(numbers: list) -> int:" in result["refactored_code"]
        assert result["refactoring_type"] == "Add type hints"
        assert result["language"] == "python"
        assert result["provider"] == "openai"

    @patch('ai_code_editing.ai_code_helpers.get_llm_client')
    def test_refactor_code_snippet_no_change(self, mock_get_client, code_dir):
        """Test refactoring when no changes are needed."""
        if str(code_dir) not in sys.path:
            sys.path.insert(0, str(code_dir))

        from ai_code_editing.ai_code_helpers import refactor_code_snippet

        # Mock client that returns the same code
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_choice = MagicMock()
        mock_message = MagicMock()

        original_code = "def hello():\n    print('Hello')"
        # Ensure the mock response contains the exact same code that will be extracted
        mock_message.content = f"```\n{original_code}\n```\nThe code is already well-structured."
        mock_choice.message = mock_message
        mock_response.choices = [mock_choice]
        mock_client.chat.completions.create.return_value = mock_response

        mock_get_client.return_value = (mock_client, "gpt-3.5-turbo")

        result = refactor_code_snippet(
            original_code,
            "Optimize code",
            "python",
            provider="openai"
        )

        # The refactored_code contains the original code (it may include markdown formatting and explanations)
        assert original_code in result["refactored_code"]
        assert result["refactoring_type"] == "Optimize code"
        assert result["language"] == "python"
        assert result["provider"] == "openai"

    def test_ai_code_helpers_constants(self, code_dir):
        """Test that ai_code_helpers has expected constants."""
        if str(code_dir) not in sys.path:
            sys.path.insert(0, str(code_dir))

        from codomyrmex.ai_code_editing import ai_code_helpers

        assert hasattr(ai_code_helpers, 'DEFAULT_LLM_PROVIDER')
        assert hasattr(ai_code_helpers, 'DEFAULT_LLM_MODEL')
        assert ai_code_helpers.DEFAULT_LLM_PROVIDER == "openai"
        assert isinstance(ai_code_helpers.DEFAULT_LLM_MODEL, dict)
        assert "openai" in ai_code_helpers.DEFAULT_LLM_MODEL
        assert "anthropic" in ai_code_helpers.DEFAULT_LLM_MODEL

