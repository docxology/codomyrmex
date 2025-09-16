"""
Comprehensive tests for AI code editing functionality.

This module tests all AI code editing functions including generation, refactoring,
analysis, and utility functions.
"""

import pytest
import os
import sys
import tempfile
import json
from unittest.mock import Mock, patch, MagicMock
from typing import Dict, Any

# Add project root to Python path
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, '..', '..', '..'))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from ai_code_editing.ai_code_helpers import (
    get_llm_client,
    generate_code_snippet,
    refactor_code_snippet,
    analyze_code_quality,
    generate_code_batch,
    compare_code_versions,
    generate_code_documentation,
    get_supported_languages,
    get_supported_providers,
    get_available_models,
    validate_api_keys,
    setup_environment,
    CodeGenerationRequest,
    CodeRefactoringRequest,
    CodeAnalysisRequest,
    CodeGenerationResult,
    CodeLanguage,
    CodeComplexity,
    CodeStyle,
)


class TestCodeEnums:
    """Test code-related enums."""
    
    def test_code_language_enum(self):
        """Test CodeLanguage enum values."""
        assert CodeLanguage.PYTHON.value == "python"
        assert CodeLanguage.JAVASCRIPT.value == "javascript"
        assert CodeLanguage.TYPESCRIPT.value == "typescript"
        assert len(list(CodeLanguage)) > 10  # Should have many languages
    
    def test_code_complexity_enum(self):
        """Test CodeComplexity enum values."""
        assert CodeComplexity.SIMPLE.value == "simple"
        assert CodeComplexity.INTERMEDIATE.value == "intermediate"
        assert CodeComplexity.COMPLEX.value == "complex"
        assert CodeComplexity.EXPERT.value == "expert"
    
    def test_code_style_enum(self):
        """Test CodeStyle enum values."""
        assert CodeStyle.CLEAN.value == "clean"
        assert CodeStyle.VERBOSE.value == "verbose"
        assert CodeStyle.CONCISE.value == "concise"
        assert CodeStyle.FUNCTIONAL.value == "functional"


class TestDataStructures:
    """Test data structure classes."""
    
    def test_code_generation_request(self):
        """Test CodeGenerationRequest creation."""
        request = CodeGenerationRequest(
            prompt="Create a function",
            language=CodeLanguage.PYTHON,
            complexity=CodeComplexity.INTERMEDIATE,
            style=CodeStyle.CLEAN
        )
        
        assert request.prompt == "Create a function"
        assert request.language == CodeLanguage.PYTHON
        assert request.complexity == CodeComplexity.INTERMEDIATE
        assert request.style == CodeStyle.CLEAN
        assert request.temperature == 0.7  # Default value
    
    def test_code_refactoring_request(self):
        """Test CodeRefactoringRequest creation."""
        request = CodeRefactoringRequest(
            code="def func(): pass",
            language=CodeLanguage.PYTHON,
            refactoring_type="optimize"
        )
        
        assert request.code == "def func(): pass"
        assert request.language == CodeLanguage.PYTHON
        assert request.refactoring_type == "optimize"
        assert request.preserve_functionality is True  # Default value
    
    def test_code_analysis_request(self):
        """Test CodeAnalysisRequest creation."""
        request = CodeAnalysisRequest(
            code="def func(): pass",
            language=CodeLanguage.PYTHON,
            analysis_type="quality"
        )
        
        assert request.code == "def func(): pass"
        assert request.language == CodeLanguage.PYTHON
        assert request.analysis_type == "quality"
        assert request.include_suggestions is True  # Default value


class TestUtilityFunctions:
    """Test utility functions."""
    
    def test_get_supported_languages(self):
        """Test getting supported languages."""
        languages = get_supported_languages()
        assert isinstance(languages, list)
        assert len(languages) > 10
        assert CodeLanguage.PYTHON in languages
        assert CodeLanguage.JAVASCRIPT in languages
    
    def test_get_supported_providers(self):
        """Test getting supported providers."""
        providers = get_supported_providers()
        assert isinstance(providers, list)
        assert "openai" in providers
        assert "anthropic" in providers
        assert "google" in providers
    
    def test_get_available_models(self):
        """Test getting available models for providers."""
        openai_models = get_available_models("openai")
        assert isinstance(openai_models, list)
        assert "gpt-3.5-turbo" in openai_models
        
        anthropic_models = get_available_models("anthropic")
        assert isinstance(anthropic_models, list)
        assert "claude-instant-1" in anthropic_models
        
        google_models = get_available_models("google")
        assert isinstance(google_models, list)
        assert "gemini-pro" in google_models
        
        # Test unknown provider
        unknown_models = get_available_models("unknown")
        assert unknown_models == []
    
    def test_validate_api_keys(self):
        """Test API key validation."""
        with patch.dict(os.environ, {
            "OPENAI_API_KEY": "test-key",
            "ANTHROPIC_API_KEY": "",
            "GOOGLE_API_KEY": "test-key"
        }):
            results = validate_api_keys()
            assert results["openai"] is True
            assert results["anthropic"] is False
            assert results["google"] is True


class TestLLMClientInitialization:
    """Test LLM client initialization."""
    
    def test_get_llm_client_openai_success(self):
        """Test successful OpenAI client initialization."""
        with patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"}):
            with patch("ai_code_editing.ai_code_helpers.OpenAI") as mock_openai:
                mock_client = Mock()
                mock_openai.return_value = mock_client
                
                client, model = get_llm_client("openai")
                
                assert client == mock_client
                assert model == "gpt-3.5-turbo"
                mock_openai.assert_called_once_with(api_key="test-key")
    
    def test_get_llm_client_openai_missing_key(self):
        """Test OpenAI client initialization with missing API key."""
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(ValueError, match="OPENAI_API_KEY environment variable not set"):
                get_llm_client("openai")
    
    def test_get_llm_client_openai_import_error(self):
        """Test OpenAI client initialization with import error."""
        with patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"}):
            with patch("ai_code_editing.ai_code_helpers.OpenAI", side_effect=ImportError):
                with pytest.raises(ImportError, match="OpenAI Python package not installed"):
                    get_llm_client("openai")
    
    def test_get_llm_client_anthropic_success(self):
        """Test successful Anthropic client initialization."""
        with patch.dict(os.environ, {"ANTHROPIC_API_KEY": "test-key"}):
            with patch("ai_code_editing.ai_code_helpers.Anthropic") as mock_anthropic:
                mock_client = Mock()
                mock_anthropic.return_value = mock_client
                
                client, model = get_llm_client("anthropic")
                
                assert client == mock_client
                assert model == "claude-instant-1"
                mock_anthropic.assert_called_once_with(api_key="test-key")
    
    def test_get_llm_client_google_success(self):
        """Test successful Google client initialization."""
        with patch.dict(os.environ, {"GOOGLE_API_KEY": "test-key"}):
            with patch("ai_code_editing.ai_code_helpers.genai") as mock_genai:
                client, model = get_llm_client("google")
                
                assert client == mock_genai
                assert model == "gemini-pro"
                mock_genai.configure.assert_called_once_with(api_key="test-key")
    
    def test_get_llm_client_unsupported_provider(self):
        """Test unsupported provider."""
        with pytest.raises(ValueError, match="Unsupported LLM provider: unsupported"):
            get_llm_client("unsupported")
    
    def test_get_llm_client_custom_model(self):
        """Test client initialization with custom model."""
        with patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"}):
            with patch("ai_code_editing.ai_code_helpers.OpenAI") as mock_openai:
                mock_client = Mock()
                mock_openai.return_value = mock_client
                
                client, model = get_llm_client("openai", "gpt-4")
                
                assert client == mock_client
                assert model == "gpt-4"


class TestCodeGeneration:
    """Test code generation functionality."""
    
    def test_generate_code_snippet_openai_success(self):
        """Test successful code generation with OpenAI."""
        with patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"}):
            with patch("ai_code_editing.ai_code_helpers.get_llm_client") as mock_get_client:
                mock_client = Mock()
                mock_response = Mock()
                mock_response.choices = [Mock()]
                mock_response.choices[0].message.content = "def hello(): print('Hello')"
                mock_response.usage.total_tokens = 100
                mock_client.chat.completions.create.return_value = mock_response
                mock_get_client.return_value = (mock_client, "gpt-3.5-turbo")
                
                result = generate_code_snippet(
                    prompt="Create a hello function",
                    language="python",
                    provider="openai"
                )
                
                assert result["generated_code"] == "def hello(): print('Hello')"
                assert result["language"] == "python"
                assert result["provider"] == "openai"
                assert result["tokens_used"] == 100
                assert "execution_time" in result
    
    def test_generate_code_snippet_anthropic_success(self):
        """Test successful code generation with Anthropic."""
        with patch.dict(os.environ, {"ANTHROPIC_API_KEY": "test-key"}):
            with patch("ai_code_editing.ai_code_helpers.get_llm_client") as mock_get_client:
                mock_client = Mock()
                mock_response = Mock()
                mock_response.content = [Mock()]
                mock_response.content[0].text = "def hello(): print('Hello')"
                mock_response.usage.input_tokens = 50
                mock_response.usage.output_tokens = 50
                mock_client.messages.create.return_value = mock_response
                mock_get_client.return_value = (mock_client, "claude-instant-1")
                
                result = generate_code_snippet(
                    prompt="Create a hello function",
                    language="python",
                    provider="anthropic"
                )
                
                assert result["generated_code"] == "def hello(): print('Hello')"
                assert result["language"] == "python"
                assert result["provider"] == "anthropic"
                assert result["tokens_used"] == 100
    
    def test_generate_code_snippet_google_success(self):
        """Test successful code generation with Google."""
        with patch.dict(os.environ, {"GOOGLE_API_KEY": "test-key"}):
            with patch("ai_code_editing.ai_code_helpers.get_llm_client") as mock_get_client:
                mock_genai = Mock()
                mock_model = Mock()
                mock_response = Mock()
                mock_response.text = "def hello(): print('Hello')"
                mock_model.generate_content.return_value = mock_response
                mock_genai.GenerativeModel.return_value = mock_model
                mock_get_client.return_value = (mock_genai, "gemini-pro")
                
                result = generate_code_snippet(
                    prompt="Create a hello function",
                    language="python",
                    provider="google"
                )
                
                assert result["generated_code"] == "def hello(): print('Hello')"
                assert result["language"] == "python"
                assert result["provider"] == "google"
                assert result["tokens_used"] is None
    
    def test_generate_code_snippet_invalid_prompt(self):
        """Test code generation with invalid prompt."""
        with pytest.raises(ValueError, match="Prompt cannot be empty"):
            generate_code_snippet("", "python")
    
    def test_generate_code_snippet_invalid_language(self):
        """Test code generation with invalid language."""
        with pytest.raises(ValueError, match="Language must be specified"):
            generate_code_snippet("Create a function", "")
    
    def test_generate_code_snippet_with_context(self):
        """Test code generation with context."""
        with patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"}):
            with patch("ai_code_editing.ai_code_helpers.get_llm_client") as mock_get_client:
                mock_client = Mock()
                mock_response = Mock()
                mock_response.choices = [Mock()]
                mock_response.choices[0].message.content = "def hello(): print('Hello')"
                mock_response.usage.total_tokens = 100
                mock_client.chat.completions.create.return_value = mock_response
                mock_get_client.return_value = (mock_client, "gpt-3.5-turbo")
                
                result = generate_code_snippet(
                    prompt="Create a hello function",
                    language="python",
                    provider="openai",
                    context="This is for a greeting module"
                )
                
                assert result["metadata"]["context"] == "This is for a greeting module"
                # Check that context was included in the API call
                call_args = mock_client.chat.completions.create.call_args
                assert "This is for a greeting module" in call_args[1]["messages"][0]["content"]


class TestCodeRefactoring:
    """Test code refactoring functionality."""
    
    def test_refactor_code_snippet_success(self):
        """Test successful code refactoring."""
        with patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"}):
            with patch("ai_code_editing.ai_code_helpers.get_llm_client") as mock_get_client:
                mock_client = Mock()
                mock_response = Mock()
                mock_response.choices = [Mock()]
                mock_response.choices[0].message.content = "def optimized_func(): print('Hello')"
                mock_response.usage.total_tokens = 100
                mock_client.chat.completions.create.return_value = mock_response
                mock_get_client.return_value = (mock_client, "gpt-3.5-turbo")
                
                result = refactor_code_snippet(
                    code="def func(): print('Hello')",
                    refactoring_type="optimize",
                    language="python",
                    provider="openai"
                )
                
                assert result["original_code"] == "def func(): print('Hello')"
                assert result["refactored_code"] == "def optimized_func(): print('Hello')"
                assert result["refactoring_type"] == "optimize"
                assert result["language"] == "python"
    
    def test_refactor_code_snippet_invalid_code(self):
        """Test refactoring with invalid code."""
        with pytest.raises(ValueError, match="Code cannot be empty"):
            refactor_code_snippet("", "optimize", "python")
    
    def test_refactor_code_snippet_invalid_type(self):
        """Test refactoring with invalid type."""
        with pytest.raises(ValueError, match="Refactoring type must be specified"):
            refactor_code_snippet("def func(): pass", "", "python")


class TestCodeAnalysis:
    """Test code analysis functionality."""
    
    def test_analyze_code_quality_success(self):
        """Test successful code quality analysis."""
        with patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"}):
            with patch("ai_code_editing.ai_code_helpers.get_llm_client") as mock_get_client:
                mock_client = Mock()
                mock_response = Mock()
                mock_response.choices = [Mock()]
                mock_response.choices[0].message.content = "The code looks good with minor improvements needed."
                mock_response.usage.total_tokens = 100
                mock_client.chat.completions.create.return_value = mock_response
                mock_get_client.return_value = (mock_client, "gpt-3.5-turbo")
                
                result = analyze_code_quality(
                    code="def func(): pass",
                    language="python",
                    analysis_type="quality",
                    provider="openai"
                )
                
                assert result["code"] == "def func(): pass"
                assert result["analysis"] == "The code looks good with minor improvements needed."
                assert result["analysis_type"] == "quality"
                assert result["language"] == "python"
    
    def test_analyze_code_quality_invalid_code(self):
        """Test analysis with invalid code."""
        with pytest.raises(ValueError, match="Code cannot be empty"):
            analyze_code_quality("", "python")


class TestCodeComparison:
    """Test code comparison functionality."""
    
    def test_compare_code_versions_success(self):
        """Test successful code comparison."""
        with patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"}):
            with patch("ai_code_editing.ai_code_helpers.get_llm_client") as mock_get_client:
                mock_client = Mock()
                mock_response = Mock()
                mock_response.choices = [Mock()]
                mock_response.choices[0].message.content = "Version 2 is better optimized."
                mock_response.usage.total_tokens = 100
                mock_client.chat.completions.create.return_value = mock_response
                mock_get_client.return_value = (mock_client, "gpt-3.5-turbo")
                
                result = compare_code_versions(
                    code1="def func(): pass",
                    code2="def optimized_func(): pass",
                    language="python",
                    provider="openai"
                )
                
                assert result["code1"] == "def func(): pass"
                assert result["code2"] == "def optimized_func(): pass"
                assert result["comparison"] == "Version 2 is better optimized."
                assert result["language"] == "python"
    
    def test_compare_code_versions_invalid_code1(self):
        """Test comparison with invalid first code."""
        with pytest.raises(ValueError, match="First code version cannot be empty"):
            compare_code_versions("", "def func(): pass", "python")
    
    def test_compare_code_versions_invalid_code2(self):
        """Test comparison with invalid second code."""
        with pytest.raises(ValueError, match="Second code version cannot be empty"):
            compare_code_versions("def func(): pass", "", "python")


class TestCodeDocumentation:
    """Test code documentation functionality."""
    
    def test_generate_code_documentation_success(self):
        """Test successful code documentation generation."""
        with patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"}):
            with patch("ai_code_editing.ai_code_helpers.get_llm_client") as mock_get_client:
                mock_client = Mock()
                mock_response = Mock()
                mock_response.choices = [Mock()]
                mock_response.choices[0].message.content = "This function does something useful."
                mock_response.usage.total_tokens = 100
                mock_client.chat.completions.create.return_value = mock_response
                mock_get_client.return_value = (mock_client, "gpt-3.5-turbo")
                
                result = generate_code_documentation(
                    code="def func(): pass",
                    language="python",
                    doc_type="comprehensive",
                    provider="openai"
                )
                
                assert result["code"] == "def func(): pass"
                assert result["documentation"] == "This function does something useful."
                assert result["doc_type"] == "comprehensive"
                assert result["language"] == "python"
    
    def test_generate_code_documentation_invalid_code(self):
        """Test documentation generation with invalid code."""
        with pytest.raises(ValueError, match="Code cannot be empty"):
            generate_code_documentation("", "python")


class TestBatchGeneration:
    """Test batch code generation functionality."""
    
    def test_generate_code_batch_success(self):
        """Test successful batch code generation."""
        requests = [
            CodeGenerationRequest(
                prompt="Create a function",
                language=CodeLanguage.PYTHON
            ),
            CodeGenerationRequest(
                prompt="Create a class",
                language=CodeLanguage.PYTHON
            )
        ]
        
        with patch("ai_code_editing.ai_code_helpers.generate_code_snippet") as mock_generate:
            mock_generate.side_effect = [
                {
                    "generated_code": "def func(): pass",
                    "language": "python",
                    "metadata": {},
                    "execution_time": 1.0,
                    "tokens_used": 50
                },
                {
                    "generated_code": "class MyClass: pass",
                    "language": "python",
                    "metadata": {},
                    "execution_time": 1.5,
                    "tokens_used": 75
                }
            ]
            
            results = generate_code_batch(requests)
            
            assert len(results) == 2
            assert results[0].generated_code == "def func(): pass"
            assert results[1].generated_code == "class MyClass: pass"
            assert mock_generate.call_count == 2
    
    def test_generate_code_batch_empty_requests(self):
        """Test batch generation with empty requests."""
        with pytest.raises(ValueError, match="Requests list cannot be empty"):
            generate_code_batch([])
    
    def test_generate_code_batch_with_errors(self):
        """Test batch generation with some errors."""
        requests = [
            CodeGenerationRequest(
                prompt="Create a function",
                language=CodeLanguage.PYTHON
            )
        ]
        
        with patch("ai_code_editing.ai_code_helpers.generate_code_snippet") as mock_generate:
            mock_generate.side_effect = Exception("API Error")
            
            results = generate_code_batch(requests)
            
            assert len(results) == 1
            assert results[0].generated_code == ""
            assert "error" in results[0].metadata


class TestEnvironmentSetup:
    """Test environment setup functionality."""
    
    def test_setup_environment_success(self):
        """Test successful environment setup."""
        with patch("ai_code_editing.ai_code_helpers.check_and_setup_env_vars") as mock_setup:
            with patch("ai_code_editing.ai_code_helpers.validate_api_keys") as mock_validate:
                mock_validate.return_value = {"openai": True, "anthropic": False, "google": True}
                
                result = setup_environment()
                
                assert result is True
                mock_setup.assert_called_once()
                mock_validate.assert_called_once()
    
    def test_setup_environment_no_api_keys(self):
        """Test environment setup with no API keys."""
        with patch("ai_code_editing.ai_code_helpers.check_and_setup_env_vars"):
            with patch("ai_code_editing.ai_code_helpers.validate_api_keys") as mock_validate:
                mock_validate.return_value = {"openai": False, "anthropic": False, "google": False}
                
                result = setup_environment()
                
                assert result is False
    
    def test_setup_environment_error(self):
        """Test environment setup with error."""
        with patch("ai_code_editing.ai_code_helpers.check_and_setup_env_vars", side_effect=Exception("Setup error")):
            result = setup_environment()
            
            assert result is False


class TestIntegration:
    """Integration tests for AI code editing functionality."""
    
    def test_full_workflow_generation_to_analysis(self):
        """Test full workflow from generation to analysis."""
        with patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"}):
            with patch("ai_code_editing.ai_code_helpers.get_llm_client") as mock_get_client:
                mock_client = Mock()
                
                # Mock generation response
                gen_response = Mock()
                gen_response.choices = [Mock()]
                gen_response.choices[0].message.content = "def hello(): print('Hello')"
                gen_response.usage.total_tokens = 50
                
                # Mock analysis response
                analysis_response = Mock()
                analysis_response.choices = [Mock()]
                analysis_response.choices[0].message.content = "Good function, well structured."
                analysis_response.usage.total_tokens = 75
                
                mock_client.chat.completions.create.side_effect = [gen_response, analysis_response]
                mock_get_client.return_value = (mock_client, "gpt-3.5-turbo")
                
                # Generate code
                gen_result = generate_code_snippet(
                    prompt="Create a hello function",
                    language="python",
                    provider="openai"
                )
                
                # Analyze the generated code
                analysis_result = analyze_code_quality(
                    code=gen_result["generated_code"],
                    language="python",
                    provider="openai"
                )
                
                assert gen_result["generated_code"] == "def hello(): print('Hello')"
                assert analysis_result["analysis"] == "Good function, well structured."
                assert mock_client.chat.completions.create.call_count == 2


if __name__ == "__main__":
    pytest.main([__file__])
