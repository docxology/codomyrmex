"""
Unit tests for the ai_code_helpers module.
"""

import os
import sys
import unittest
from unittest.mock import patch, MagicMock

# Add the parent directory to the sys.path to allow importing from the parent directory
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from ai_code_editing.ai_code_helpers import (
    get_llm_client,
    generate_code_snippet,
    refactor_code_snippet
)

class TestGetLLMClient(unittest.TestCase):
    """Tests for the get_llm_client function."""
    
    @patch('ai_code_editing.ai_code_helpers.OpenAI')
    @patch.dict(os.environ, {"OPENAI_API_KEY": "fake-key"})
    def test_get_openai_client(self, mock_openai):
        """Test get_llm_client with OpenAI provider."""
        mock_client = MagicMock()
        mock_openai.return_value = mock_client
        
        client, model = get_llm_client("openai")
        
        self.assertEqual(client, mock_client)
        self.assertEqual(model, "gpt-3.5-turbo")  # Default OpenAI model
        mock_openai.assert_called_once_with(api_key="fake-key")
    
    @patch('ai_code_editing.ai_code_helpers.Anthropic')
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
    
    @patch('ai_code_editing.ai_code_helpers.get_llm_client')
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
            llm_provider="openai"
        )
        
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["generated_code"], "def max_value(numbers):\n    return max(numbers)")
        self.assertIsNone(result["error_message"])
    
    @patch('ai_code_editing.ai_code_helpers.get_llm_client')
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
            llm_provider="anthropic"
        )
        
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["generated_code"], "def max_value(numbers):\n    return max(numbers)")
        self.assertIsNone(result["error_message"])
    
    def test_generate_code_invalid_inputs(self):
        """Test code generation with invalid inputs."""
        # Missing prompt
        result = generate_code_snippet(
            prompt="",
            language="python"
        )
        self.assertEqual(result["status"], "failure")
        self.assertIsNone(result["generated_code"])
        self.assertIsNotNone(result["error_message"])
        
        # Missing language
        result = generate_code_snippet(
            prompt="Find maximum value",
            language=""
        )
        self.assertEqual(result["status"], "failure")
        self.assertIsNone(result["generated_code"])
        self.assertIsNotNone(result["error_message"])


class TestRefactorCodeSnippet(unittest.TestCase):
    """Tests for the refactor_code_snippet function."""
    
    @patch('ai_code_editing.ai_code_helpers.get_llm_client')
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
            llm_provider="openai"
        )
        
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["refactored_code"], "def max_value(numbers: list) -> int:\n    return max(numbers)")
        self.assertIsNotNone(result["explanation"])
        self.assertIsNone(result["error_message"])
    
    @patch('ai_code_editing.ai_code_helpers.get_llm_client')
    def test_refactor_code_no_change(self, mock_get_client):
        """Test refactoring when no changes are needed."""
        # Mock the client response where code doesn't change
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_message = MagicMock()
        mock_choice = MagicMock()
        
        original_code = "def max_value(numbers):\n    return max(numbers)"
        mock_choice.message.content = f"```python\n{original_code}\n```\nThe code is already optimal."
        mock_response.choices = [mock_choice]
        mock_client.chat.completions.create.return_value = mock_response
        
        mock_get_client.return_value = (mock_client, "gpt-3.5-turbo")
        
        result = refactor_code_snippet(
            code_snippet=original_code,
            refactoring_instruction="Optimize",
            language="python",
            llm_provider="openai"
        )
        
        self.assertEqual(result["status"], "no_change_needed")
        self.assertEqual(result["refactored_code"], original_code)
    

if __name__ == '__main__':
    unittest.main() 