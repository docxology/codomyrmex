"""Comprehensive tests for Ollama integration utilities."""

import asyncio
import json
import os
import pytest
import subprocess
import time
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

from codomyrmex.language_models.ollama_integration import (
    OllamaManager,
    generate_with_ollama,
    stream_with_ollama,
    chat_with_ollama,
    stream_chat_with_ollama,
    check_ollama_availability,
    get_available_models,
    create_chat_messages,
    get_default_manager,
)
from codomyrmex.language_models.ollama_client import (
    OllamaError,
    OllamaConnectionError,
    OllamaModelError,
)

# Test configuration and utilities
from codomyrmex.language_models.config import get_config

# Get configuration
config = get_config()

# Use correct model name format
TEST_MODEL = "llama3.1:latest"

def is_ollama_available() -> bool:
    """Check if Ollama is available and running."""
    try:
        import requests
        response = requests.get(f"{config.base_url}/api/version", timeout=5)
        return response.status_code == 200
    except:
        return False

def download_model_if_missing(model_name: str) -> bool:
    """Download a model if it's not available."""
    if not is_ollama_available():
        return False

    try:
        import requests
        response = requests.get(f"{config.base_url}/api/tags", timeout=10)
        if response.status_code == 200:
            data = response.json()
            available_models = [model.get("name", "") for model in data.get("models", [])]
            if model_name in available_models:
                return True
    except:
        pass

    try:
        print(f"Downloading model: {model_name}")
        result = subprocess.run(
            ["ollama", "pull", model_name],
            capture_output=True,
            text=True,
            timeout=300
        )
        return result.returncode == 0
    except Exception as e:
        print(f"Error downloading model {model_name}: {e}")
        return False

def save_test_output(filename: str, data: dict, output_type: str = "json"):
    """Save test output to file in organized directory structure."""
    if output_type == "json":
        # Save to test results directory
        config.test_results_dir.mkdir(parents=True, exist_ok=True)
        filepath = config.test_results_dir / f"{filename}.json"
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    elif output_type == "md":
        # Save to LLM outputs directory
        config.llm_outputs_dir.mkdir(parents=True, exist_ok=True)
        filepath = config.llm_outputs_dir / f"{filename}.md"
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(f"# Test Output: {filename}\n\n")
            f.write(f"**Generated:** {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write(f"**Configuration:** Model: {config.model}, Temperature: {config.temperature}, Max Tokens: {config.max_tokens}\n\n")
            if isinstance(data, dict):
                for key, value in data.items():
                    f.write(f"## {key.replace('_', ' ').title()}\n\n")
                    f.write(f"{value}\n\n")
            else:
                f.write(str(data))


class TestOllamaManager:
    """Test suite for OllamaManager."""

    @pytest.fixture
    def manager(self):
        """Create a test manager."""
        mock_client = Mock()
        mock_client.generate.return_value = "Generated response"
        mock_client.chat.return_value = "Chat response"
        mock_client.list_models.return_value = [{"name": "test-model"}]

        manager = OllamaManager(
            base_url="http://test:11434",
            model="test-model",
            timeout=5
        )
        manager.client = mock_client  # Replace the real client with our mock
        yield manager

    @pytest.fixture
    def mock_client(self):
        """Mock OllamaClient."""
        client = Mock()
        client.generate.return_value = "Generated response"
        client.chat.return_value = "Chat response"
        client.list_models.return_value = [{"name": "test-model"}]
        return client

    def test_initialization(self, manager, mock_client):
        """Test manager initialization."""
        with patch('codomyrmex.language_models.ollama_integration.OllamaClient', return_value=mock_client):
            manager = OllamaManager(base_url="http://test:11434")

            assert manager.client == mock_client
            assert manager._default_options == {}

    def test_set_default_options(self, manager):
        """Test setting default options."""
        manager.set_default_options(temperature=0.8, top_p=0.9)

        assert manager._default_options == {"temperature": 0.8, "top_p": 0.9}

        # Test updating options
        manager.set_default_options(temperature=0.7)
        assert manager._default_options == {"temperature": 0.7, "top_p": 0.9}

    @patch('codomyrmex.language_models.ollama_integration.OllamaClient')
    def test_generate_with_defaults(self, mock_client_class, manager, mock_client):
        """Test generation with default options."""
        mock_client_class.return_value = mock_client

        manager.set_default_options(temperature=0.8)
        result = manager.generate("Test prompt")

        assert result == "Generated response"
        mock_client.generate.assert_called_once()

        # Check that default options are merged
        call_kwargs = mock_client.generate.call_args[1]
        assert call_kwargs["options"] == {"temperature": 0.8}

    @patch('codomyrmex.language_models.ollama_integration.OllamaClient')
    def test_generate_with_override_options(self, mock_client_class, manager, mock_client):
        """Test generation with option overrides."""
        mock_client_class.return_value = mock_client

        manager.set_default_options(temperature=0.8)
        override_options = {"temperature": 0.5, "top_k": 40}
        result = manager.generate("Test prompt", options=override_options)

        # Check that override options take precedence
        call_kwargs = mock_client.generate.call_args[1]
        expected_options = {"temperature": 0.5, "top_k": 40}
        assert call_kwargs["options"] == expected_options

    @patch('codomyrmex.language_models.ollama_integration.OllamaClient')
    def test_chat_with_defaults(self, mock_client_class, manager, mock_client):
        """Test chat with default options."""
        mock_client_class.return_value = mock_client

        manager.set_default_options(temperature=0.8)
        messages = [{"role": "user", "content": "Hello"}]
        result = manager.chat(messages)

        assert result == "Chat response"
        mock_client.chat.assert_called_once()

        # Check that default options are merged
        call_kwargs = mock_client.chat.call_args[1]
        assert call_kwargs["options"] == {"temperature": 0.8}

    @patch('codomyrmex.language_models.ollama_integration.OllamaClient')
    def test_list_models_error_handling(self, mock_client_class, manager, mock_client):
        """Test list_models with error handling."""
        mock_client_class.return_value = mock_client
        mock_client.list_models.side_effect = OllamaConnectionError("Connection failed")

        with pytest.raises(OllamaConnectionError):
            manager.list_models()

    @patch('codomyrmex.language_models.ollama_integration.OllamaClient')
    def test_check_health_success(self, mock_client_class, manager, mock_client):
        """Test health check success."""
        mock_client_class.return_value = mock_client
        mock_client.list_models.return_value = [{"name": "test-model"}]

        result = manager.check_health()
        assert result is True

    @patch('codomyrmex.language_models.ollama_integration.OllamaClient')
    def test_check_health_failure(self, mock_client_class, manager, mock_client):
        """Test health check failure."""
        mock_client_class.return_value = mock_client
        mock_client.list_models.side_effect = OllamaConnectionError("Connection failed")

        result = manager.check_health()
        assert result is False

    def test_close(self, manager, mock_client):
        """Test manager cleanup."""
        manager.client = mock_client
        manager.close()
        mock_client.close.assert_called_once()

    @pytest.mark.integration
    def test_manager_generation(self):
        """Test real manager with real Ollama."""
        if not is_ollama_available():
            pytest.skip("Ollama not available for integration tests")

        # First check if model exists or download it
        available_models = get_available_models()
        model_exists = TEST_MODEL in available_models

        if not model_exists:
            if not download_model_if_missing(TEST_MODEL):
                pytest.skip(f"Could not download or find model: {TEST_MODEL}")
            # Refresh model list after download
            available_models = get_available_models()

        manager = OllamaManager(model=TEST_MODEL, timeout=30)

        try:
            # Test basic generation
            prompt = "What is the capital of France?"
            response = manager.generate(prompt)

            assert len(response) > 0
            assert "paris" in response.lower()

            # Save test output
            test_output = {
                "test_name": "manager_generation",
                "status": "passed",
                "timestamp": time.time(),
                "prompt": prompt,
                "response_length": len(response),
                "response": response,
                "model": TEST_MODEL
            }
            save_test_output("manager_generation", test_output, "md")

        finally:
            manager.close()

    @pytest.mark.integration
    def test_manager_with_options(self):
        """Test manager with various options."""
        if not is_ollama_available():
            pytest.skip("Ollama not available for integration tests")

        # First check if model exists or download it
        available_models = get_available_models()
        model_exists = TEST_MODEL in available_models

        if not model_exists:
            if not download_model_if_missing(TEST_MODEL):
                pytest.skip(f"Could not download or find model: {TEST_MODEL}")
            # Refresh model list after download
            available_models = get_available_models()

        manager = OllamaManager(model=TEST_MODEL, timeout=30)

        try:
            # Set default options
            manager.set_default_options(temperature=0.8, top_p=0.9)

            prompt = "Write a short poem about programming."
            response = manager.generate(prompt)

            assert len(response) > 0

            # Test override options
            override_response = manager.generate(
                prompt,
                options={"temperature": 0.3, "num_predict": 50}
            )

            assert len(override_response) > 0

            # Save test output
            test_output = {
                "test_name": "manager_with_options",
                "status": "passed",
                "timestamp": time.time(),
                "prompt": prompt,
                "default_options": manager._default_options,
                "response_length": len(response),
                "override_response_length": len(override_response),
                "response_preview": response[:100] + "...",
                "override_response_preview": override_response[:100] + "..."
            }
            save_test_output("manager_with_options", test_output, "md")

        finally:
            manager.close()

    @pytest.mark.integration
    def test_streaming_manager(self):
        """Test real streaming with manager."""
        if not is_ollama_available():
            pytest.skip("Ollama not available for integration tests")

        # First check if model exists or download it
        available_models = get_available_models()
        model_exists = TEST_MODEL in available_models

        if not model_exists:
            if not download_model_if_missing(TEST_MODEL):
                pytest.skip(f"Could not download or find model: {TEST_MODEL}")
            # Refresh model list after download
            available_models = get_available_models()

        manager = OllamaManager(model=TEST_MODEL, timeout=30)

        try:
            prompt = "Tell me about machine learning in 3 sentences."
            chunks = []

            # Use synchronous iteration for testing
            for chunk in manager.generate(prompt, stream=True):
                chunks.append(chunk)

            assert len(chunks) > 0
            full_response = "".join(chunks)

            # Save test output
            test_output = {
                "test_name": "streaming_manager",
                "status": "passed",
                "timestamp": time.time(),
                "prompt": prompt,
                "chunks_count": len(chunks),
                "total_length": len(full_response),
                "response": full_response
            }
            save_test_output("streaming_manager", test_output, "md")

        finally:
            manager.close()


class TestConvenienceFunctions:
    """Test convenience functions."""

    @patch('codomyrmex.language_models.ollama_integration.get_default_manager')
    def test_generate_with_ollama(self, mock_get_manager):
        """Test generate_with_ollama function."""
        mock_manager = Mock()
        mock_manager.generate.return_value = "Generated text"
        mock_get_manager.return_value = mock_manager

        result = generate_with_ollama("Test prompt", model="test-model")

        assert result == "Generated text"
        mock_get_manager.assert_called_once()
        mock_manager.generate.assert_called_once_with("Test prompt", options=None)

    @patch('codomyrmex.language_models.ollama_integration.get_default_manager')
    def test_generate_with_ollama_with_options(self, mock_get_manager):
        """Test generate_with_ollama with options."""
        mock_manager = Mock()
        mock_manager.generate.return_value = "Generated text"
        mock_get_manager.return_value = mock_manager

        options = {"temperature": 0.8}
        result = generate_with_ollama("Test prompt", options=options)

        mock_manager.generate.assert_called_once_with("Test prompt", options=options)

    @patch('codomyrmex.language_models.ollama_integration.get_default_manager')
    def test_stream_with_ollama(self, mock_get_manager):
        """Test stream_with_ollama function."""

        async def mock_generate(*args, **kwargs):
            yield "chunk1"
            yield "chunk2"

        mock_manager = Mock()
        mock_manager.generate = mock_generate
        mock_get_manager.return_value = mock_manager

        async def test_stream():
            chunks = []
            async for chunk in stream_with_ollama("Test prompt"):
                chunks.append(chunk)
            return chunks

        chunks = asyncio.run(test_stream())
        assert chunks == ["chunk1", "chunk2"]

    @patch('codomyrmex.language_models.ollama_integration.get_default_manager')
    def test_chat_with_ollama(self, mock_get_manager):
        """Test chat_with_ollama function."""
        mock_manager = Mock()
        mock_manager.chat.return_value = "Chat response"
        mock_get_manager.return_value = mock_manager

        messages = [{"role": "user", "content": "Hello"}]
        result = chat_with_ollama(messages, model="test-model")

        assert result == "Chat response"
        mock_manager.chat.assert_called_once_with(messages, options=None)

    @patch('codomyrmex.language_models.ollama_integration.get_default_manager')
    def test_stream_chat_with_ollama(self, mock_get_manager):
        """Test stream_chat_with_ollama function."""

        async def mock_chat(*args, **kwargs):
            yield "response chunk1"
            yield "response chunk2"

        mock_manager = Mock()
        mock_manager.chat = mock_chat
        mock_get_manager.return_value = mock_manager

        messages = [{"role": "user", "content": "Hello"}]

        async def test_stream_chat():
            chunks = []
            async for chunk in stream_chat_with_ollama(messages):
                chunks.append(chunk)
            return chunks

        chunks = asyncio.run(test_stream_chat())
        assert chunks == ["response chunk1", "response chunk2"]

    @pytest.mark.integration
    def test_generate_with_ollama(self):
        """Test real generate_with_ollama function."""
        if not is_ollama_available():
            pytest.skip("Ollama not available for integration tests")

        if not download_model_if_missing(TEST_MODEL):
            pytest.skip(f"Could not download model: {TEST_MODEL}")

        prompt = "What is the meaning of life?"
        response = generate_with_ollama(prompt, model=TEST_MODEL)

        assert len(response) > 0

        # Save test output
        test_output = {
            "test_name": "generate_with_ollama",
            "status": "passed",
            "timestamp": time.time(),
            "prompt": prompt,
            "response_length": len(response),
            "response": response
        }
        save_test_output("generate_with_ollama", test_output, "md")

    @pytest.mark.integration
    def test_stream_with_ollama(self):
        """Test real stream_with_ollama function."""
        if not is_ollama_available():
            pytest.skip("Ollama not available for integration tests")

        # First check if model exists or download it
        available_models = get_available_models()
        model_exists = TEST_MODEL in available_models

        if not model_exists:
            if not download_model_if_missing(TEST_MODEL):
                pytest.skip(f"Could not download or find model: {TEST_MODEL}")
            # Refresh model list after download
            available_models = get_available_models()

        prompt = "Count from 1 to 3 slowly."
        chunks = []

        # Use synchronous iteration for testing
        for chunk in stream_with_ollama(prompt, model=TEST_MODEL):
            chunks.append(chunk)

        assert len(chunks) > 0
        full_response = "".join(chunks)

        # Save test output
        test_output = {
            "test_name": "stream_with_ollama",
            "status": "passed",
            "timestamp": time.time(),
            "prompt": prompt,
            "chunks_count": len(chunks),
            "response": full_response
        }
        save_test_output("stream_with_ollama", test_output, "md")

    @pytest.mark.integration
    def test_chat_with_ollama(self):
        """Test real chat_with_ollama function."""
        if not is_ollama_available():
            pytest.skip("Ollama not available for integration tests")

        if not download_model_if_missing(TEST_MODEL):
            pytest.skip(f"Could not download model: {TEST_MODEL}")

        messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "What is 3 + 5?"}
        ]

        response = chat_with_ollama(messages, model=TEST_MODEL)

        assert len(response) > 0
        assert "8" in response or "eight" in response.lower()

        # Save test output
        test_output = {
            "test_name": "chat_with_ollama",
            "status": "passed",
            "timestamp": time.time(),
            "messages": messages,
            "response": response
        }
        save_test_output("chat_with_ollama", test_output, "md")


class TestUtilityFunctions:
    """Test utility functions."""

    @patch('codomyrmex.language_models.ollama_integration.OllamaClient')
    def test_check_ollama_availability_success(self, mock_client_class):
        """Test successful availability check."""
        mock_client = Mock()
        mock_client._check_connection.return_value = True
        mock_client_class.return_value = mock_client

        result = check_ollama_availability()
        assert result is True
        mock_client.close.assert_called_once()

    @patch('codomyrmex.language_models.ollama_integration.OllamaClient')
    def test_check_ollama_availability_failure(self, mock_client_class):
        """Test failed availability check."""
        mock_client = Mock()
        mock_client._check_connection.return_value = False
        mock_client_class.return_value = mock_client

        result = check_ollama_availability()
        assert result is False
        mock_client.close.assert_called_once()

    @patch('codomyrmex.language_models.ollama_integration.OllamaClient')
    def test_check_ollama_availability_exception(self, mock_client_class):
        """Test availability check with exception."""
        mock_client = Mock()
        mock_client._check_connection.side_effect = Exception("Connection error")
        mock_client_class.return_value = mock_client

        result = check_ollama_availability()
        assert result is False
        mock_client.close.assert_called_once()

    @patch('codomyrmex.language_models.ollama_integration.OllamaClient')
    def test_get_available_models_success(self, mock_client_class):
        """Test successful model listing."""
        mock_client = Mock()
        mock_client.list_models.return_value = [
            {"name": "model1"},
            {"name": "model2"}
        ]
        mock_client_class.return_value = mock_client

        result = get_available_models()
        assert result == ["model1", "model2"]
        mock_client.close.assert_called_once()

    @patch('codomyrmex.language_models.ollama_integration.OllamaClient')
    def test_get_available_models_error(self, mock_client_class):
        """Test model listing with error."""
        mock_client = Mock()
        mock_client.list_models.side_effect = OllamaError("Server error")
        mock_client_class.return_value = mock_client

        result = get_available_models()
        assert result == []
        mock_client.close.assert_called_once()

    def test_create_chat_messages_system_only(self):
        """Test creating chat messages with system prompt only."""
        system_prompt = "You are a helpful assistant."
        messages = create_chat_messages(system_prompt=system_prompt)

        expected = [{"role": "system", "content": system_prompt}]
        assert messages == expected

    def test_create_chat_messages_user_only(self):
        """Test creating chat messages with user message only."""
        user_message = "Hello, how are you?"
        messages = create_chat_messages(user_message=user_message)

        expected = [{"role": "user", "content": user_message}]
        assert messages == expected

    def test_create_chat_messages_both(self):
        """Test creating chat messages with both system and user."""
        system_prompt = "You are a helpful assistant."
        user_message = "Hello, how are you?"
        messages = create_chat_messages(
            system_prompt=system_prompt,
            user_message=user_message
        )

        expected = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message}
        ]
        assert messages == expected

    def test_create_chat_messages_with_history(self):
        """Test creating chat messages with conversation history."""
        history = [
            {"role": "user", "content": "Hi"},
            {"role": "assistant", "content": "Hello"}
        ]
        user_message = "How are you?"

        messages = create_chat_messages(
            user_message=user_message,
            conversation_history=history
        )

        expected = [
            {"role": "user", "content": "Hi"},
            {"role": "assistant", "content": "Hello"},
            {"role": "user", "content": user_message}
        ]
        assert messages == expected

    def test_create_chat_messages_with_system_and_history(self):
        """Test creating chat messages with system prompt and history."""
        system_prompt = "You are a helpful assistant."
        history = [
            {"role": "user", "content": "Hi"},
            {"role": "assistant", "content": "Hello"}
        ]
        user_message = "How are you?"

        messages = create_chat_messages(
            system_prompt=system_prompt,
            user_message=user_message,
            conversation_history=history
        )

        expected = [
            {"role": "user", "content": "Hi"},
            {"role": "assistant", "content": "Hello"},
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message}
        ]
        assert messages == expected


class TestDefaultManager:
    """Test default manager functionality."""

    def test_get_default_manager_singleton(self):
        """Test that get_default_manager returns singleton."""
        with patch('codomyrmex.language_models.ollama_integration.OllamaManager') as mock_manager_class:
            mock_manager_class.return_value = Mock()

            manager1 = get_default_manager()
            manager2 = get_default_manager()

            # Should be the same instance
            assert manager1 is manager2
            # Should only be created once
            assert mock_manager_class.call_count == 1

    def test_get_default_manager_with_args(self):
        """Test get_default_manager with creation arguments."""
        with patch('codomyrmex.language_models.ollama_integration.OllamaManager') as mock_manager_class:
            mock_manager_class.return_value = Mock()

            manager = get_default_manager(model="test-model", timeout=30)

            # Should create with provided arguments
            mock_manager_class.assert_called_once_with(model="test-model", timeout=30)
            assert manager is mock_manager_class.return_value

            # Reset the global manager for other tests
            import codomyrmex.language_models.ollama_integration as ollama_integration
            ollama_integration._default_manager = None
