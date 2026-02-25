"""Tests for Ollama integration with agents module.

This module tests the Ollama provider integration in ai_code_helpers,
ensuring code generation, refactoring, and analysis work with local LLMs.

Uses the smallest available Ollama model to keep tests fast.
"""

import subprocess

import pytest

try:
    from codomyrmex.agents.ai_code_editing.ai_code_helpers import (
        OLLAMA_AVAILABLE,
        analyze_code_quality,
        compare_code_versions,
        generate_code_documentation,
        generate_code_snippet,
        get_available_models,
        get_llm_client,
        get_supported_providers,
        refactor_code_snippet,
    )
    _HAS_AGENTS = True
except ImportError:
    _HAS_AGENTS = False

if not _HAS_AGENTS:
    pytest.skip("agents deps not available", allow_module_level=True)


def _get_installed_ollama_models() -> list[str]:
    """Query the local Ollama server for actually installed models."""
    try:
        result = subprocess.run(
            ["ollama", "list"],
            capture_output=True, text=True, timeout=10,
        )
        if result.returncode != 0:
            return []
        lines = result.stdout.strip().split("\n")[1:]  # Skip header
        return [line.split()[0] for line in lines if line.strip()]
    except Exception:
        return []


_INSTALLED_MODELS = _get_installed_ollama_models()
# Prefer smallest model for speed (sorted by name, :1b < :latest)
_TEST_MODEL = sorted(_INSTALLED_MODELS)[0] if _INSTALLED_MODELS else None


class TestOllamaProviderIntegration:
    """Test Ollama as an LLM provider in ai_code_helpers."""

    def test_ollama_available(self):
        """Test that Ollama integration is available."""
        assert OLLAMA_AVAILABLE is True, "Ollama should be available"

    def test_ollama_in_supported_providers(self):
        """Test that ollama is in the list of supported providers."""
        providers = get_supported_providers()
        assert "ollama" in providers, "ollama should be in supported providers"

    def test_ollama_models_available(self):
        """Test that Ollama models are listed."""
        models = get_available_models("ollama")
        assert len(models) > 0, "Should have ollama models available"

    def test_get_llm_client_ollama(self):
        """Test initializing Ollama client."""
        client, model = get_llm_client("ollama")
        assert client is not None, "Ollama client should be initialized"
        assert isinstance(model, str) and len(model) > 0

    def test_get_llm_client_ollama_custom_model(self):
        """Test initializing Ollama client with custom model."""
        if not _TEST_MODEL:
            pytest.fail("No Ollama models installed")
        client, model = get_llm_client("ollama", model_name=_TEST_MODEL)
        assert client is not None, "Ollama client should be initialized"
        assert model == _TEST_MODEL, f"Model should be {_TEST_MODEL}, got {model}"


def _ollama_model_responsive() -> bool:
    """Check if an installed Ollama model actually generates non-empty responses."""
    if not _TEST_MODEL:
        return False
    try:
        result = generate_code_snippet(
            prompt="Return 1", language="python", provider="ollama",
            model_name=_TEST_MODEL, max_length=32,
        )
        return len(result.get("generated_code", "")) > 0
    except Exception:
        return False


_OLLAMA_RESPONSIVE = OLLAMA_AVAILABLE and _ollama_model_responsive()


@pytest.mark.skipif(not _OLLAMA_RESPONSIVE, reason="Ollama not available or model not responding")
class TestOllamaCodeGeneration:
    """Test code generation with Ollama (requires Ollama server running)."""

    @pytest.mark.slow
    def test_generate_code_with_ollama(self):
        """Test generating code with Ollama."""
        result = generate_code_snippet(
            prompt="Create a simple function that adds two numbers",
            language="python",
            provider="ollama",
            model_name=_TEST_MODEL,
            max_length=256,
        )

        assert "generated_code" in result, "Result should have generated_code"
        assert result["provider"] == "ollama"
        assert result["language"] == "python"
        assert result["execution_time"] > 0
        assert len(result["generated_code"]) > 10

    @pytest.mark.slow
    def test_refactor_code_with_ollama(self):
        """Test refactoring code with Ollama."""
        code = """
def add(a, b):
    return a + b
"""
        result = refactor_code_snippet(
            code=code,
            refactoring_type="add type hints and docstring",
            language="python",
            provider="ollama",
            model_name=_TEST_MODEL,
        )

        assert "refactored_code" in result, "Result should have refactored_code"
        assert result["provider"] == "ollama"
        assert result["original_code"] == code

    @pytest.mark.slow
    def test_analyze_code_with_ollama(self):
        """Test analyzing code with Ollama."""
        code = """
def factorial(n):
    if n <= 1:
        return 1
    return n * factorial(n - 1)
"""
        result = analyze_code_quality(
            code=code,
            language="python",
            analysis_type="comprehensive",
            provider="ollama",
            model_name=_TEST_MODEL,
        )

        assert "analysis" in result, "Result should have analysis"
        assert result["provider"] == "ollama"
        assert result["analysis_type"] == "comprehensive"

    @pytest.mark.slow
    def test_compare_code_with_ollama(self):
        """Test comparing code versions with Ollama."""
        code1 = "def add(a, b): return a + b"
        code2 = """
def add(a: int, b: int) -> int:
    '''Add two integers.'''
    return a + b
"""
        result = compare_code_versions(
            code1=code1,
            code2=code2,
            language="python",
            provider="ollama",
            model_name=_TEST_MODEL,
        )

        assert "comparison" in result, "Result should have comparison"
        assert result["provider"] == "ollama"

    @pytest.mark.slow
    def test_generate_documentation_with_ollama(self):
        """Test generating documentation with Ollama."""
        code = """
class Calculator:
    def add(self, a, b):
        return a + b

    def subtract(self, a, b):
        return a - b
"""
        result = generate_code_documentation(
            code=code,
            language="python",
            doc_type="api",
            provider="ollama",
            model_name=_TEST_MODEL,
        )

        assert "documentation" in result, "Result should have documentation"
        assert result["provider"] == "ollama"
        assert result["doc_type"] == "api"


class TestOllamaFallback:
    """Test fallback behavior when Ollama is not available."""

    def test_provider_list_without_ollama(self):
        """Test that provider list works even if Ollama check fails."""
        providers = get_supported_providers()
        # Should always include cloud providers
        assert "openai" in providers
        assert "anthropic" in providers
        assert "google" in providers

    def test_invalid_provider_error(self):
        """Test that invalid provider raises error."""
        with pytest.raises(ValueError, match="Unsupported LLM provider"):
            get_llm_client("invalid_provider")
