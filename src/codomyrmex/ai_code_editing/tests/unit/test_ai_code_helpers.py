"""
Unit tests for the ai_code_helpers module.
"""

import os
import sys
import unittest
from unittest.mock import patch, MagicMock
from codomyrmex.exceptions import CodomyrmexError

# Add the parent directory to the sys.path to allow importing from the parent directory
# sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))  # Removed sys.path manipulation

from ai_code_editing.ai_code_helpers import (
from codomyrmex.logging_monitoring.logger_config import get_logger

logger = get_logger(__name__)

    get_llm_client,
    generate_code_snippet,
    refactor_code_snippet,
)


class TestGetLLMClient(unittest.TestCase):
    """Tests for the get_llm_client function."""

    @patch("ai_code_editing.ai_code_helpers.OpenAI")
    @patch.dict(os.environ, {"OPENAI_API_KEY": "fake-key"})
    def test_get_openai_client(self, mock_openai):
        """Test get_llm_client with OpenAI provider."""
        mock_client = MagicMock()
        mock_openai.return_value = mock_client

        client, model = get_llm_client("openai")

        self.assertEqual(client, mock_client)
        self.assertEqual(model, "gpt-3.5-turbo")  # Default OpenAI model
        mock_openai.assert_called_once_with(api_key="fake-key")

    @patch("ai_code_editing.ai_code_helpers.Anthropic")
    @patch.dict(os.environ, {"ANTHROPIC_API_KEY": "fake-key"})
    def test_get_anthropic_client(self, mock_anthropic):
        """Test get_llm_client with Anthropic provider."""
        mock_client = MagicMock()
        mock_anthropic.return_value = mock_client

        client, model = get_llm_client("anthropic", "claude-opus")

        self.assertEqual(client, mock_client)
        self.assertEqual(model, "claude-opus")  # Specified model
        mock_anthropic.assert_called_once_with(api_key="fake-key")

    def test_get_client_unsupported_provider(self):
        """Test get_llm_client with an unsupported provider."""
        with self.assertRaises(ValueError):
            get_llm_client("unsupported-provider")

    @patch.dict(os.environ, {}, clear=True)
    def test_get_openai_client_missing_key(self):
        """Test get_llm_client with missing API key."""
        with self.assertRaises(ValueError):
            get_llm_client("openai")


class TestGenerateCodeSnippet(unittest.TestCase):
    """Tests for the generate_code_snippet function."""

    @patch("ai_code_editing.ai_code_helpers.get_llm_client")
    def test_generate_code_success_openai(self, mock_get_client):
        """Test successful code generation with OpenAI."""
        # Mock the OpenAI client
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_message = MagicMock()
        mock_choice = MagicMock()

        mock_choice.message.content = "def max_value(numbers):\n    return max(numbers)"
        mock_response.choices = [mock_choice]
        mock_client.chat.completions.create.return_value = mock_response

        mock_get_client.return_value = (mock_client, "gpt-3.5-turbo")

        result = generate_code_snippet(
            prompt="Find maximum value in list",
            language="python",
            llm_provider="openai",
        )

        self.assertEqual(result["status"], "success")
        self.assertEqual(
            result["generated_code"], "def max_value(numbers):\n    return max(numbers)"
        )
        self.assertIsNone(result["error_message"])

    @patch("ai_code_editing.ai_code_helpers.get_llm_client")
    def test_generate_code_success_anthropic(self, mock_get_client):
        """Test successful code generation with Anthropic."""
        # Mock the Anthropic client
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_content = MagicMock()

        mock_content.text = "def max_value(numbers):\n    return max(numbers)"
        mock_response.content = [mock_content]
        mock_client.messages.create.return_value = mock_response

        mock_get_client.return_value = (mock_client, "claude-instant-1")

        result = generate_code_snippet(
            prompt="Find maximum value in list",
            language="python",
            llm_provider="anthropic",
        )

        self.assertEqual(result["status"], "success")
        self.assertEqual(
            result["generated_code"], "def max_value(numbers):\n    return max(numbers)"
        )
        self.assertIsNone(result["error_message"])

    def test_generate_code_invalid_inputs(self):
        """Test code generation with invalid inputs."""
        # Missing prompt
        result = generate_code_snippet(prompt="", language="python")
        self.assertEqual(result["status"], "failure")
        self.assertIsNone(result["generated_code"])
        self.assertIsNotNone(result["error_message"])

        # Missing language
        result = generate_code_snippet(prompt="Find maximum value", language="")
        self.assertEqual(result["status"], "failure")
        self.assertIsNone(result["generated_code"])
        self.assertIsNotNone(result["error_message"])

    @patch("ai_code_editing.ai_code_helpers.get_llm_client")
    def test_generate_code_openai_api_error(self, mock_get_client):
        """Test code generation when OpenAI API call fails."""
        mock_client = MagicMock()
        mock_client.chat.completions.create.side_effect = Exception("OpenAI API Error")
        mock_get_client.return_value = (mock_client, "gpt-3.5-turbo")

        result = generate_code_snippet(
            prompt="Test prompt", language="python", llm_provider="openai"
        )

        self.assertEqual(result["status"], "failure")
        self.assertIsNone(result["generated_code"])
        self.assertIn("OpenAI API Error", result["error_message"])

    @patch("ai_code_editing.ai_code_helpers.get_llm_client")
    def test_generate_code_anthropic_api_error(self, mock_get_client):
        """Test code generation when Anthropic API call fails."""
        mock_client = MagicMock()
        mock_client.messages.create.side_effect = Exception("Anthropic API Error")
        mock_get_client.return_value = (mock_client, "claude-instant-1")

        result = generate_code_snippet(
            prompt="Test prompt", language="python", llm_provider="anthropic"
        )

        self.assertEqual(result["status"], "failure")
        self.assertIsNone(result["generated_code"])
        self.assertIn("Anthropic API Error", result["error_message"])

    @patch("ai_code_editing.ai_code_helpers.get_llm_client")
    def test_generate_code_openai_malformed_response(self, mock_get_client):
        """Test code generation with OpenAI when LLM response is malformed."""
        mock_client = MagicMock()
        # Malformed: choices list is empty
        mock_response_empty_choices = MagicMock()
        mock_response_empty_choices.choices = []
        mock_client.chat.completions.create.return_value = mock_response_empty_choices
        mock_get_client.return_value = (mock_client, "gpt-3.5-turbo")

        result = generate_code_snippet(
            prompt="Test", language="python", llm_provider="openai"
        )
        self.assertEqual(result["status"], "failure")
        self.assertIsNone(result["generated_code"])
        self.assertIn("Malformed response from OpenAI", result["error_message"].lower())

        # Malformed: message.content is missing
        mock_response_missing_content = MagicMock()
        mock_choice_no_content = MagicMock()
        mock_message_no_content = MagicMock()
        del mock_message_no_content.content  # Or mock_message_no_content.content = None
        mock_choice_no_content.message = mock_message_no_content
        mock_response_missing_content.choices = [mock_choice_no_content]
        mock_client.chat.completions.create.return_value = mock_response_missing_content

        result = generate_code_snippet(
            prompt="Test", language="python", llm_provider="openai"
        )
        self.assertEqual(result["status"], "failure")
        self.assertIsNone(result["generated_code"])
        self.assertIn("malformed response from openai", result["error_message"].lower())

    @patch("ai_code_editing.ai_code_helpers.get_llm_client")
    def test_generate_code_anthropic_malformed_response(self, mock_get_client):
        """Test code generation with Anthropic when LLM response is malformed."""
        mock_client = MagicMock()
        # Malformed: content list is empty
        mock_response_empty_content_list = MagicMock()
        mock_response_empty_content_list.content = []
        mock_client.messages.create.return_value = mock_response_empty_content_list
        mock_get_client.return_value = (mock_client, "claude-instant-1")

        result = generate_code_snippet(
            prompt="Test", language="python", llm_provider="anthropic"
        )
        self.assertEqual(result["status"], "failure")
        self.assertIsNone(result["generated_code"])
        self.assertIn(
            "malformed response from anthropic", result["error_message"].lower()
        )

        # Malformed: text attribute is missing from content block
        mock_response_missing_text = MagicMock()
        mock_content_block_no_text = MagicMock()
        del mock_content_block_no_text.text  # Or mock_content_block_no_text.text = None
        mock_response_missing_text.content = [mock_content_block_no_text]
        mock_client.messages.create.return_value = mock_response_missing_text

        result = generate_code_snippet(
            prompt="Test", language="python", llm_provider="anthropic"
        )
        self.assertEqual(result["status"], "failure")
        self.assertIsNone(result["generated_code"])
        self.assertIn(
            "malformed response from anthropic", result["error_message"].lower()
        )


class TestRefactorCodeSnippet(unittest.TestCase):
    """Tests for the refactor_code_snippet function."""

    @patch("ai_code_editing.ai_code_helpers.get_llm_client")
    def test_refactor_code_success_openai(self, mock_get_client):
        """Test successful code refactoring with OpenAI."""
        # Mock the OpenAI client
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_message = MagicMock()
        mock_choice = MagicMock()

        mock_choice.message.content = "```python\ndef max_value(numbers: list) -> int:\n    return max(numbers)\n```\nAdded type hints to the function."
        mock_response.choices = [mock_choice]
        mock_client.chat.completions.create.return_value = mock_response

        mock_get_client.return_value = (mock_client, "gpt-3.5-turbo")

        original_code = "def max_value(numbers):\n    return max(numbers)"
        result = refactor_code_snippet(
            code_snippet=original_code,
            refactoring_instruction="Add type hints",
            language="python",
            llm_provider="openai",
        )

        self.assertEqual(result["status"], "success")
        self.assertEqual(
            result["refactored_code"],
            "def max_value(numbers: list) -> int:\n    return max(numbers)",
        )
        self.assertIsNotNone(result["explanation"])
        self.assertIsNone(result["error_message"])

    @patch("ai_code_editing.ai_code_helpers.get_llm_client")
    def test_refactor_code_no_change(self, mock_get_client):
        """Test refactoring when no changes are needed."""
        # Mock the client response where code doesn't change
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_message = MagicMock()
        mock_choice = MagicMock()

        original_code = "def max_value(numbers):\n    return max(numbers)"
        mock_choice.message.content = (
            f"```python\n{original_code}\n```\nThe code is already optimal."
        )
        mock_response.choices = [mock_choice]
        mock_client.chat.completions.create.return_value = mock_response

        mock_get_client.return_value = (mock_client, "gpt-3.5-turbo")

        result = refactor_code_snippet(
            code_snippet=original_code,
            refactoring_instruction="Optimize",
            language="python",
            llm_provider="openai",
        )

        self.assertEqual(result["status"], "no_change_needed")
        self.assertEqual(result["refactored_code"], original_code)

    @patch("ai_code_editing.ai_code_helpers.get_llm_client")
    def test_refactor_code_openai_api_error(self, mock_get_client):
        """Test code refactoring when OpenAI API call fails."""
        mock_client = MagicMock()
        mock_client.chat.completions.create.side_effect = Exception("OpenAI API Error")
        mock_get_client.return_value = (mock_client, "gpt-3.5-turbo")

        result = refactor_code_snippet(
            code_snippet="print('hello')",
            refactoring_instruction="Optimize",
            language="python",
            llm_provider="openai",
        )

        self.assertEqual(result["status"], "failure")
        self.assertIsNone(result["refactored_code"])
        self.assertIn("OpenAI API Error", result["error_message"])

    @patch("ai_code_editing.ai_code_helpers.get_llm_client")
    def test_refactor_code_anthropic_api_error(self, mock_get_client):
        """Test code refactoring when Anthropic API call fails."""
        mock_client = MagicMock()
        mock_client.messages.create.side_effect = Exception("Anthropic API Error")
        mock_get_client.return_value = (mock_client, "claude-instant-1")

        result = refactor_code_snippet(
            code_snippet="print('hello')",
            refactoring_instruction="Optimize",
            language="python",
            llm_provider="anthropic",
        )

        self.assertEqual(result["status"], "failure")
        self.assertIsNone(result["refactored_code"])
        self.assertIn("Anthropic API Error", result["error_message"])

    @patch("ai_code_editing.ai_code_helpers.get_llm_client")
    def test_refactor_code_openai_malformed_response(self, mock_get_client):
        """Test code refactoring with OpenAI when LLM response is malformed (e.g., no code block)."""
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_choice_no_code_block = MagicMock()
        mock_message_no_code_block = MagicMock()
        mock_message_no_code_block.content = "This is not a code block."
        mock_choice_no_code_block.message = mock_message_no_code_block
        mock_response.choices = [mock_choice_no_code_block]
        mock_client.chat.completions.create.return_value = mock_response
        mock_get_client.return_value = (mock_client, "gpt-3.5-turbo")

        result = refactor_code_snippet(
            code_snippet="print('hello')",
            refactoring_instruction="Optimize",
            language="python",
            llm_provider="openai",
        )
        self.assertEqual(
            result["status"], "failure"
        )  # Or "no_change_needed" if that's the fallback
        self.assertIn(
            "could not extract refactored code", result["error_message"].lower()
        )

        # Test case: response is None or not a string (OpenAI)
        mock_message_none_content = MagicMock()
        mock_message_none_content.content = None
        mock_choice_none_content = MagicMock()
        mock_choice_none_content.message = mock_message_none_content
        mock_response_none_content = MagicMock()
        mock_response_none_content.choices = [mock_choice_none_content]
        mock_client.chat.completions.create.return_value = mock_response_none_content
        mock_get_client.return_value = (mock_client, "gpt-3.5-turbo")

        result = refactor_code_snippet(
            code_snippet="print('hello')",
            refactoring_instruction="Optimize",
            language="python",
            llm_provider="openai",
        )
        self.assertEqual(result["status"], "failure")
        self.assertIn("empty or invalid response", result["error_message"].lower())

    @patch("ai_code_editing.ai_code_helpers.get_llm_client")
    def test_refactor_code_anthropic_malformed_response(self, mock_get_client):
        """Test code refactoring with Anthropic when LLM response is malformed (e.g., no code block)."""
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_content_block_no_code = MagicMock()
        mock_content_block_no_code.text = "This is not a code block."
        mock_response.content = [mock_content_block_no_code]
        mock_client.messages.create.return_value = mock_response
        mock_get_client.return_value = (mock_client, "claude-instant-1")

        result = refactor_code_snippet(
            code_snippet="print('hello')",
            refactoring_instruction="Optimize",
            language="python",
            llm_provider="anthropic",
        )
        self.assertEqual(result["status"], "failure")  # Or "no_change_needed"
        self.assertIn(
            "could not extract refactored code", result["error_message"].lower()
        )

        # Test case: response is None or not a string (Anthropic)
        mock_content_block_none = MagicMock()
        mock_content_block_none.text = None
        mock_response_none_content = MagicMock()
        mock_response_none_content.content = [mock_content_block_none]
        mock_client.messages.create.return_value = mock_response_none_content
        mock_get_client.return_value = (mock_client, "claude-instant-1")

        result = refactor_code_snippet(
            code_snippet="print('hello')",
            refactoring_instruction="Optimize",
            language="python",
            llm_provider="anthropic",
        )
        self.assertEqual(result["status"], "failure")
        self.assertIn("empty or invalid response", result["error_message"].lower())


if __name__ == "__main__":
    # unittest.main()
    # Using a more explicit way to run tests, which might satisfy some linters
    suite = unittest.TestLoader().loadTestsFromModule(__import__(__name__))
    unittest.TextTestRunner().run(suite)
