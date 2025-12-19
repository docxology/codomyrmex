"""Unit tests for language_models module."""

import sys
import pytest
from pathlib import Path


class TestLanguageModels:
    """Test cases for language models functionality."""

    def test_language_models_import(self, code_dir):
        """Test that we can import language_models module."""
        if str(code_dir) not in sys.path:
            sys.path.insert(0, str(code_dir))

        try:
            from codomyrmex import language_models
            assert language_models is not None
        except ImportError as e:
            pytest.fail(f"Failed to import language_models: {e}")

    def test_language_models_module_exists(self, code_dir):
        """Test that language_models module directory exists."""
        lm_path = code_dir / "codomyrmex" / "language_models"
        assert lm_path.exists()
        assert lm_path.is_dir()

    def test_language_models_init_file(self, code_dir):
        """Test that language_models has __init__.py."""
        init_path = code_dir / "codomyrmex" / "language_models" / "__init__.py"
        assert init_path.exists()

    def test_config_module_exists(self, code_dir):
        """Test that config module exists."""
        config_path = code_dir / "codomyrmex" / "language_models" / "config.py"
        assert config_path.exists()

    def test_ollama_client_exists(self, code_dir):
        """Test that ollama_client module exists."""
        client_path = code_dir / "codomyrmex" / "language_models" / "ollama_client.py"
        assert client_path.exists()

    def test_ollama_integration_exists(self, code_dir):
        """Test that ollama_integration module exists."""
        integration_path = code_dir / "codomyrmex" / "language_models" / "ollama_integration.py"
        assert integration_path.exists()

    def test_llm_config_import(self, code_dir):
        """Test that LLMConfig class can be imported."""
        if str(code_dir) not in sys.path:
            sys.path.insert(0, str(code_dir))

        try:
            from codomyrmex.language_models import LLMConfig
            assert LLMConfig is not None
        except ImportError as e:
            pytest.fail(f"Failed to import LLMConfig: {e}")

    def test_llm_config_presets_import(self, code_dir):
        """Test that LLMConfigPresets class can be imported."""
        if str(code_dir) not in sys.path:
            sys.path.insert(0, str(code_dir))

        try:
            from codomyrmex.language_models import LLMConfigPresets
            assert LLMConfigPresets is not None
        except ImportError as e:
            pytest.fail(f"Failed to import LLMConfigPresets: {e}")

    def test_config_functions_import(self, code_dir):
        """Test that config functions can be imported."""
        if str(code_dir) not in sys.path:
            sys.path.insert(0, str(code_dir))

        try:
            from codomyrmex.language_models import get_config, set_config, reset_config
            assert callable(get_config)
            assert callable(set_config)
            assert callable(reset_config)
        except ImportError as e:
            pytest.fail(f"Failed to import config functions: {e}")

    def test_ollama_client_import(self, code_dir):
        """Test that OllamaClient class can be imported."""
        if str(code_dir) not in sys.path:
            sys.path.insert(0, str(code_dir))

        try:
            from codomyrmex.language_models import OllamaClient
            assert OllamaClient is not None
        except ImportError as e:
            pytest.fail(f"Failed to import OllamaClient: {e}")

    def test_ollama_exceptions_import(self, code_dir):
        """Test that Ollama exception classes can be imported."""
        if str(code_dir) not in sys.path:
            sys.path.insert(0, str(code_dir))

        try:
            from codomyrmex.language_models import (
                OllamaError,
                OllamaConnectionError,
                OllamaTimeoutError,
                OllamaModelError,
            )
            assert OllamaError is not None
            assert OllamaConnectionError is not None
            assert OllamaTimeoutError is not None
            assert OllamaModelError is not None
        except ImportError as e:
            pytest.fail(f"Failed to import Ollama exceptions: {e}")

    def test_ollama_manager_import(self, code_dir):
        """Test that OllamaManager class can be imported."""
        if str(code_dir) not in sys.path:
            sys.path.insert(0, str(code_dir))

        try:
            from codomyrmex.language_models import OllamaManager
            assert OllamaManager is not None
        except ImportError as e:
            pytest.fail(f"Failed to import OllamaManager: {e}")

    def test_ollama_utility_functions_import(self, code_dir):
        """Test that Ollama utility functions can be imported."""
        if str(code_dir) not in sys.path:
            sys.path.insert(0, str(code_dir))

        try:
            from codomyrmex.language_models import (
                generate_with_ollama,
                stream_with_ollama,
                chat_with_ollama,
                stream_chat_with_ollama,
                check_ollama_availability,
                get_available_models,
                create_chat_messages,
                get_default_manager,
            )
            assert callable(generate_with_ollama)
            assert callable(stream_with_ollama)
            assert callable(chat_with_ollama)
            assert callable(stream_chat_with_ollama)
            assert callable(check_ollama_availability)
            assert callable(get_available_models)
            assert callable(create_chat_messages)
            assert callable(get_default_manager)
        except ImportError as e:
            pytest.fail(f"Failed to import Ollama utility functions: {e}")

    def test_language_models_all_exports(self, code_dir):
        """Test that language_models exports all expected symbols."""
        if str(code_dir) not in sys.path:
            sys.path.insert(0, str(code_dir))

        from codomyrmex import language_models

        expected_exports = [
            "LLMConfig",
            "LLMConfigPresets",
            "get_config",
            "set_config",
            "reset_config",
            "OllamaClient",
            "OllamaError",
            "OllamaConnectionError",
            "OllamaTimeoutError",
            "OllamaModelError",
            "OllamaManager",
            "generate_with_ollama",
            "chat_with_ollama",
            "check_ollama_availability",
            "get_available_models",
        ]

        for export in expected_exports:
            assert hasattr(language_models, export), f"Missing export: {export}"

    def test_agents_md_exists(self, code_dir):
        """Test that AGENTS.md exists for language_models module."""
        agents_path = code_dir / "codomyrmex" / "language_models" / "AGENTS.md"
        assert agents_path.exists()

    def test_readme_exists(self, code_dir):
        """Test that README.md exists for language_models module."""
        readme_path = code_dir / "codomyrmex" / "language_models" / "README.md"
        assert readme_path.exists()

    def test_tests_directory_exists(self, code_dir):
        """Test that tests directory exists for language_models module."""
        tests_path = code_dir / "codomyrmex" / "language_models" / "tests"
        assert tests_path.exists()
        assert tests_path.is_dir()



