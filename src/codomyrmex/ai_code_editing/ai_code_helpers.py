"""
Core implementation of AI code editing functionality.

This module contains functions for generating and refactoring code using LLMs.
"""

import os
import sys
import json
import time
import random
from typing import Dict, Any, Optional, Tuple, Union, List, Callable
from dataclasses import dataclass
from enum import Enum

# Add project root to Python path to allow sibling module imports if needed
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# Import logger setup
try:
    from logging_monitoring import setup_logging, get_logger
except ImportError:
    # Fallback if logging module isn't available
    import logging

    def get_logger(name):
        logger = logging.getLogger(name)
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            logger.setLevel(logging.INFO)
        return logger


# Get module logger
logger = get_logger(__name__)

# Import performance monitoring
try:
    from performance import monitor_performance, performance_context

    PERFORMANCE_MONITORING_AVAILABLE = True
except ImportError:
    logger.warning("Performance monitoring not available - decorators will be no-op")
    PERFORMANCE_MONITORING_AVAILABLE = False

    # Create no-op decorators
    def monitor_performance(*args, **kwargs):
        def decorator(func):
            return func

        return decorator

    class performance_context:
        def __init__(self, *args, **kwargs):
            pass

        def __enter__(self):
            return self

        def __exit__(self, *args):
            pass


# Import environment setup utilities if available
try:
    from environment_setup.env_checker import check_and_setup_env_vars
except ImportError:
    logger.warning(
        "Could not import from environment_setup.env_checker. Environment variables may need to be set manually."
    )
    check_and_setup_env_vars = None


# Enums for better type safety
class CodeLanguage(Enum):
    """Supported programming languages."""

    PYTHON = "python"
    JAVASCRIPT = "javascript"
    TYPESCRIPT = "typescript"
    JAVA = "java"
    CPP = "cpp"
    CSHARP = "csharp"
    GO = "go"
    RUST = "rust"
    PHP = "php"
    RUBY = "ruby"
    SWIFT = "swift"
    KOTLIN = "kotlin"
    SCALA = "scala"
    R = "r"
    MATLAB = "matlab"
    SHELL = "shell"
    SQL = "sql"
    HTML = "html"
    CSS = "css"
    XML = "xml"
    YAML = "yaml"
    JSON = "json"
    MARKDOWN = "markdown"


class CodeComplexity(Enum):
    """Code complexity levels."""

    SIMPLE = "simple"
    INTERMEDIATE = "intermediate"
    COMPLEX = "complex"
    EXPERT = "expert"


class CodeStyle(Enum):
    """Code style preferences."""

    CLEAN = "clean"
    VERBOSE = "verbose"
    CONCISE = "concise"
    FUNCTIONAL = "functional"
    OBJECT_ORIENTED = "object_oriented"
    PROCEDURAL = "procedural"


@dataclass
class CodeGenerationRequest:
    """Request structure for code generation."""

    prompt: str
    language: CodeLanguage
    complexity: CodeComplexity = CodeComplexity.INTERMEDIATE
    style: CodeStyle = CodeStyle.CLEAN
    context: Optional[str] = None
    requirements: Optional[List[str]] = None
    examples: Optional[List[str]] = None
    max_length: Optional[int] = None
    temperature: float = 0.7


@dataclass
class CodeRefactoringRequest:
    """Request structure for code refactoring."""

    code: str
    language: CodeLanguage
    refactoring_type: str  # e.g., "optimize", "simplify", "add_error_handling"
    context: Optional[str] = None
    preserve_functionality: bool = True
    add_tests: bool = False
    add_documentation: bool = False


@dataclass
class CodeAnalysisRequest:
    """Request structure for code analysis."""

    code: str
    language: CodeLanguage
    analysis_type: str  # e.g., "quality", "security", "performance", "maintainability"
    context: Optional[str] = None
    include_suggestions: bool = True


@dataclass
class CodeGenerationResult:
    """Result structure for code generation."""

    generated_code: str
    language: CodeLanguage
    metadata: Dict[str, Any]
    execution_time: float
    tokens_used: Optional[int] = None
    confidence_score: Optional[float] = None


# Default LLM configurations
DEFAULT_LLM_PROVIDER = "openai"
DEFAULT_LLM_MODEL = {
    "openai": "gpt-3.5-turbo",
    "anthropic": "claude-instant-1",
    "google": "gemini-pro",
}

# Retry configuration for API calls
MAX_RETRIES = 3
RETRY_DELAY = 1.0  # seconds


# LLM client initialization
@monitor_performance("llm_client_initialization")
def get_llm_client(provider: str, model_name: Optional[str] = None) -> Tuple[Any, str]:
    """
    Initialize and return an LLM client based on the specified provider.

    Args:
        provider: The LLM provider to use (e.g., "openai", "anthropic")
        model_name: Optional specific model to use

    Returns:
        Tuple of (client, model_name)

    Raises:
        ImportError: If the required client library is not installed
        ValueError: If the provider is not supported or configuration is invalid
    """
    provider = provider.lower()

    if provider == "openai":
        try:
            from openai import OpenAI

            # Check for API key
            api_key = os.environ.get("OPENAI_API_KEY")
            if not api_key:
                raise ValueError("OPENAI_API_KEY environment variable not set")

            client = OpenAI(api_key=api_key)
            model = model_name or DEFAULT_LLM_MODEL["openai"]
            return client, model

        except ImportError:
            raise ImportError(
                "OpenAI Python package not installed. Install with: pip install openai"
            )

    elif provider == "anthropic":
        try:
            from anthropic import Anthropic

            # Check for API key
            api_key = os.environ.get("ANTHROPIC_API_KEY")
            if not api_key:
                raise ValueError("ANTHROPIC_API_KEY environment variable not set")

            client = Anthropic(api_key=api_key)
            model = model_name or DEFAULT_LLM_MODEL["anthropic"]
            return client, model

        except ImportError:
            raise ImportError(
                "Anthropic Python package not installed. Install with: pip install anthropic"
            )

    elif provider == "google":
        try:
            import google.generativeai as genai

            # Check for API key
            api_key = os.environ.get("GOOGLE_API_KEY")
            if not api_key:
                raise ValueError("GOOGLE_API_KEY environment variable not set")

            genai.configure(api_key=api_key)
            model = model_name or DEFAULT_LLM_MODEL["google"]
            return genai, model

        except ImportError:
            raise ImportError(
                "Google Generative AI package not installed. Install with: pip install google-generativeai"
            )

    else:
        raise ValueError(
            f"Unsupported LLM provider: {provider}. Supported providers: openai, anthropic, google"
        )


@monitor_performance("ai_code_generation")
def generate_code_snippet(
    prompt: str,
    language: str,
    provider: str = DEFAULT_LLM_PROVIDER,
    model_name: Optional[str] = None,
    context: Optional[str] = None,
    max_length: Optional[int] = None,
    temperature: float = 0.7,
    **kwargs,
) -> Dict[str, Any]:
    """
    Generate a code snippet using an LLM.

    Args:
        prompt: The prompt describing what code to generate
        language: Programming language for the generated code
        provider: LLM provider to use ("openai", "anthropic", "google")
        model_name: Specific model to use (optional)
        context: Additional context for the generation
        max_length: Maximum length of generated code
        temperature: Sampling temperature (0.0 to 1.0)
        **kwargs: Additional parameters for the LLM

    Returns:
        Dictionary containing generated code and metadata

    Raises:
        ValueError: If parameters are invalid
        RuntimeError: If code generation fails
    """
    start_time = time.time()

    try:
        # Validate inputs
        if not prompt or not prompt.strip():
            raise ValueError("Prompt cannot be empty")

        if not language:
            raise ValueError("Language must be specified")

        # Get LLM client
        client, model = get_llm_client(provider, model_name)

        # Prepare the prompt
        full_prompt = f"Generate {language} code for: {prompt}"
        if context:
            full_prompt += f"\n\nContext: {context}"

        # Add language-specific instructions
        language_instructions = {
            "python": "Follow PEP 8 style guidelines and include proper error handling.",
            "javascript": "Use modern ES6+ syntax and include JSDoc comments.",
            "typescript": "Use TypeScript best practices with proper type annotations.",
            "java": "Follow Java naming conventions and include JavaDoc comments.",
            "cpp": "Use modern C++ features and include proper memory management.",
        }

        if language.lower() in language_instructions:
            full_prompt += f"\n\n{language_instructions[language.lower()]}"

        # Generate code based on provider
        if provider == "openai":
            response = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": full_prompt}],
                max_tokens=max_length or 1000,
                temperature=temperature,
                **kwargs,
            )
            generated_code = response.choices[0].message.content
            tokens_used = response.usage.total_tokens if response.usage else None

        elif provider == "anthropic":
            response = client.messages.create(
                model=model,
                max_tokens=max_length or 1000,
                temperature=temperature,
                messages=[{"role": "user", "content": full_prompt}],
                **kwargs,
            )
            generated_code = response.content[0].text
            tokens_used = (
                response.usage.input_tokens + response.usage.output_tokens
                if response.usage
                else None
            )

        elif provider == "google":
            model_instance = client.GenerativeModel(model)
            response = model_instance.generate_content(
                full_prompt,
                generation_config={
                    "max_output_tokens": max_length or 1000,
                    "temperature": temperature,
                },
            )
            generated_code = response.text
            tokens_used = None  # Google doesn't provide token count in basic response

        else:
            raise ValueError(f"Unsupported provider: {provider}")

        execution_time = time.time() - start_time

        # Return result
        result = {
            "generated_code": generated_code,
            "language": language,
            "provider": provider,
            "model": model,
            "execution_time": execution_time,
            "tokens_used": tokens_used,
            "metadata": {
                "prompt": prompt,
                "context": context,
                "temperature": temperature,
                "max_length": max_length,
            },
        }

        logger.info(
            f"Generated {language} code snippet using {provider}/{model} in {execution_time:.2f}s"
        )
        return result

    except Exception as e:
        logger.error(f"Error generating code snippet: {e}")
        raise RuntimeError(f"Code generation failed: {e}")


@monitor_performance("ai_code_refactoring")
def refactor_code_snippet(
    code: str,
    refactoring_type: str,
    language: str,
    provider: str = DEFAULT_LLM_PROVIDER,
    model_name: Optional[str] = None,
    context: Optional[str] = None,
    preserve_functionality: bool = True,
    **kwargs,
) -> Dict[str, Any]:
    """
    Refactor existing code using an LLM.

    Args:
        code: The code to refactor
        refactoring_type: Type of refactoring (e.g., "optimize", "simplify", "add_error_handling")
        language: Programming language of the code
        provider: LLM provider to use
        model_name: Specific model to use (optional)
        context: Additional context for refactoring
        preserve_functionality: Whether to preserve original functionality
        **kwargs: Additional parameters for the LLM

    Returns:
        Dictionary containing refactored code and metadata

    Raises:
        ValueError: If parameters are invalid
        RuntimeError: If refactoring fails
    """
    start_time = time.time()

    try:
        # Validate inputs
        if not code or not code.strip():
            raise ValueError("Code cannot be empty")

        if not refactoring_type:
            raise ValueError("Refactoring type must be specified")

        # Get LLM client
        client, model = get_llm_client(provider, model_name)

        # Prepare the prompt
        functionality_note = (
            "Preserve the original functionality exactly."
            if preserve_functionality
            else "You may modify functionality if it improves the code."
        )

        prompt = f"""Refactor the following {language} code to {refactoring_type}:

{code}

{functionality_note}"""

        if context:
            prompt += f"\n\nAdditional context: {context}"

        # Generate refactored code based on provider
        if provider == "openai":
            response = client.chat.completions.create(
                model=model, messages=[{"role": "user", "content": prompt}], **kwargs
            )
            refactored_code = response.choices[0].message.content
            tokens_used = response.usage.total_tokens if response.usage else None

        elif provider == "anthropic":
            response = client.messages.create(
                model=model, messages=[{"role": "user", "content": prompt}], **kwargs
            )
            refactored_code = response.content[0].text
            tokens_used = (
                response.usage.input_tokens + response.usage.output_tokens
                if response.usage
                else None
            )

        elif provider == "google":
            model_instance = client.GenerativeModel(model)
            response = model_instance.generate_content(prompt)
            refactored_code = response.text
            tokens_used = None

        else:
            raise ValueError(f"Unsupported provider: {provider}")

        execution_time = time.time() - start_time

        # Return result
        result = {
            "original_code": code,
            "refactored_code": refactored_code,
            "refactoring_type": refactoring_type,
            "language": language,
            "provider": provider,
            "model": model,
            "execution_time": execution_time,
            "tokens_used": tokens_used,
            "metadata": {
                "context": context,
                "preserve_functionality": preserve_functionality,
            },
        }

        logger.info(
            f"Refactored {language} code using {provider}/{model} in {execution_time:.2f}s"
        )
        return result

    except Exception as e:
        logger.error(f"Error refactoring code: {e}")
        raise RuntimeError(f"Code refactoring failed: {e}")


@monitor_performance("ai_code_analysis")
def analyze_code_quality(
    code: str,
    language: str,
    analysis_type: str = "comprehensive",
    provider: str = DEFAULT_LLM_PROVIDER,
    model_name: Optional[str] = None,
    context: Optional[str] = None,
    **kwargs,
) -> Dict[str, Any]:
    """
    Analyze code quality using an LLM.

    Args:
        code: The code to analyze
        language: Programming language of the code
        analysis_type: Type of analysis ("comprehensive", "security", "performance", "maintainability")
        provider: LLM provider to use
        model_name: Specific model to use (optional)
        context: Additional context for analysis
        **kwargs: Additional parameters for the LLM

    Returns:
        Dictionary containing analysis results and suggestions

    Raises:
        ValueError: If parameters are invalid
        RuntimeError: If analysis fails
    """
    start_time = time.time()

    try:
        # Validate inputs
        if not code or not code.strip():
            raise ValueError("Code cannot be empty")

        # Get LLM client
        client, model = get_llm_client(provider, model_name)

        # Prepare the prompt based on analysis type
        analysis_prompts = {
            "comprehensive": f"Analyze the following {language} code for overall quality, including readability, maintainability, performance, and best practices:",
            "security": f"Analyze the following {language} code for security vulnerabilities and potential issues:",
            "performance": f"Analyze the following {language} code for performance issues and optimization opportunities:",
            "maintainability": f"Analyze the following {language} code for maintainability, readability, and code organization:",
        }

        prompt = analysis_prompts.get(analysis_type, analysis_prompts["comprehensive"])
        prompt += f"\n\n{code}"

        if context:
            prompt += f"\n\nAdditional context: {context}"

        prompt += "\n\nProvide specific suggestions for improvement with code examples where appropriate."

        # Generate analysis based on provider
        if provider == "openai":
            response = client.chat.completions.create(
                model=model, messages=[{"role": "user", "content": prompt}], **kwargs
            )
            analysis = response.choices[0].message.content
            tokens_used = response.usage.total_tokens if response.usage else None

        elif provider == "anthropic":
            response = client.messages.create(
                model=model, messages=[{"role": "user", "content": prompt}], **kwargs
            )
            analysis = response.content[0].text
            tokens_used = (
                response.usage.input_tokens + response.usage.output_tokens
                if response.usage
                else None
            )

        elif provider == "google":
            model_instance = client.GenerativeModel(model)
            response = model_instance.generate_content(prompt)
            analysis = response.text
            tokens_used = None

        else:
            raise ValueError(f"Unsupported provider: {provider}")

        execution_time = time.time() - start_time

        # Return result
        result = {
            "code": code,
            "analysis": analysis,
            "analysis_type": analysis_type,
            "language": language,
            "provider": provider,
            "model": model,
            "execution_time": execution_time,
            "tokens_used": tokens_used,
            "metadata": {
                "context": context,
            },
        }

        logger.info(
            f"Analyzed {language} code using {provider}/{model} in {execution_time:.2f}s"
        )
        return result

    except Exception as e:
        logger.error(f"Error analyzing code: {e}")
        raise RuntimeError(f"Code analysis failed: {e}")


@monitor_performance("ai_code_generation_batch")
def generate_code_batch(
    requests: List[CodeGenerationRequest],
    provider: str = DEFAULT_LLM_PROVIDER,
    model_name: Optional[str] = None,
    parallel: bool = False,
    **kwargs,
) -> List[CodeGenerationResult]:
    """
    Generate multiple code snippets in batch.

    Args:
        requests: List of code generation requests
        provider: LLM provider to use
        model_name: Specific model to use (optional)
        parallel: Whether to process requests in parallel
        **kwargs: Additional parameters for the LLM

    Returns:
        List of code generation results

    Raises:
        ValueError: If parameters are invalid
        RuntimeError: If batch generation fails
    """
    if not requests:
        raise ValueError("Requests list cannot be empty")

    results = []

    if parallel:
        # TODO: Implement parallel processing
        logger.warning(
            "Parallel processing not yet implemented, falling back to sequential"
        )
        parallel = False

    if not parallel:
        for request in requests:
            try:
                result = generate_code_snippet(
                    prompt=request.prompt,
                    language=request.language.value,
                    provider=provider,
                    model_name=model_name,
                    context=request.context,
                    max_length=request.max_length,
                    temperature=request.temperature,
                    **kwargs,
                )

                code_result = CodeGenerationResult(
                    generated_code=result["generated_code"],
                    language=request.language,
                    metadata=result["metadata"],
                    execution_time=result["execution_time"],
                    tokens_used=result.get("tokens_used"),
                )
                results.append(code_result)

            except Exception as e:
                logger.error(f"Error processing request: {e}")
                # Add error result
                error_result = CodeGenerationResult(
                    generated_code="",
                    language=request.language,
                    metadata={"error": str(e)},
                    execution_time=0.0,
                )
                results.append(error_result)

    return results


@monitor_performance("ai_code_comparison")
def compare_code_versions(
    code1: str,
    code2: str,
    language: str,
    provider: str = DEFAULT_LLM_PROVIDER,
    model_name: Optional[str] = None,
    context: Optional[str] = None,
    **kwargs,
) -> Dict[str, Any]:
    """
    Compare two versions of code and provide analysis.

    Args:
        code1: First version of code
        code2: Second version of code
        language: Programming language of the code
        provider: LLM provider to use
        model_name: Specific model to use (optional)
        context: Additional context for comparison
        **kwargs: Additional parameters for the LLM

    Returns:
        Dictionary containing comparison analysis

    Raises:
        ValueError: If parameters are invalid
        RuntimeError: If comparison fails
    """
    start_time = time.time()

    try:
        # Validate inputs
        if not code1 or not code1.strip():
            raise ValueError("First code version cannot be empty")

        if not code2 or not code2.strip():
            raise ValueError("Second code version cannot be empty")

        # Get LLM client
        client, model = get_llm_client(provider, model_name)

        # Prepare the prompt
        prompt = f"""Compare the following two versions of {language} code and provide a detailed analysis:

VERSION 1:
{code1}

VERSION 2:
{code2}

Please analyze:
1. Functional differences
2. Performance implications
3. Code quality improvements/regressions
4. Maintainability changes
5. Best practices adherence
6. Overall recommendation

{context if context else ""}"""

        # Generate comparison based on provider
        if provider == "openai":
            response = client.chat.completions.create(
                model=model, messages=[{"role": "user", "content": prompt}], **kwargs
            )
            comparison = response.choices[0].message.content
            tokens_used = response.usage.total_tokens if response.usage else None

        elif provider == "anthropic":
            response = client.messages.create(
                model=model, messages=[{"role": "user", "content": prompt}], **kwargs
            )
            comparison = response.content[0].text
            tokens_used = (
                response.usage.input_tokens + response.usage.output_tokens
                if response.usage
                else None
            )

        elif provider == "google":
            model_instance = client.GenerativeModel(model)
            response = model_instance.generate_content(prompt)
            comparison = response.text
            tokens_used = None

        else:
            raise ValueError(f"Unsupported provider: {provider}")

        execution_time = time.time() - start_time

        # Return result
        result = {
            "code1": code1,
            "code2": code2,
            "comparison": comparison,
            "language": language,
            "provider": provider,
            "model": model,
            "execution_time": execution_time,
            "tokens_used": tokens_used,
            "metadata": {
                "context": context,
            },
        }

        logger.info(
            f"Compared {language} code versions using {provider}/{model} in {execution_time:.2f}s"
        )
        return result

    except Exception as e:
        logger.error(f"Error comparing code versions: {e}")
        raise RuntimeError(f"Code comparison failed: {e}")


@monitor_performance("ai_code_documentation")
def generate_code_documentation(
    code: str,
    language: str,
    doc_type: str = "comprehensive",
    provider: str = DEFAULT_LLM_PROVIDER,
    model_name: Optional[str] = None,
    context: Optional[str] = None,
    **kwargs,
) -> Dict[str, Any]:
    """
    Generate documentation for code using an LLM.

    Args:
        code: The code to document
        language: Programming language of the code
        doc_type: Type of documentation ("comprehensive", "api", "inline", "readme")
        provider: LLM provider to use
        model_name: Specific model to use (optional)
        context: Additional context for documentation
        **kwargs: Additional parameters for the LLM

    Returns:
        Dictionary containing generated documentation

    Raises:
        ValueError: If parameters are invalid
        RuntimeError: If documentation generation fails
    """
    start_time = time.time()

    try:
        # Validate inputs
        if not code or not code.strip():
            raise ValueError("Code cannot be empty")

        # Get LLM client
        client, model = get_llm_client(provider, model_name)

        # Prepare the prompt based on documentation type
        doc_prompts = {
            "comprehensive": f"Generate comprehensive documentation for the following {language} code, including overview, function descriptions, parameters, return values, and usage examples:",
            "api": f"Generate API documentation for the following {language} code, focusing on public interfaces, method signatures, and parameters:",
            "inline": f"Generate inline documentation (comments) for the following {language} code, following the language's documentation standards:",
            "readme": f"Generate a README-style documentation for the following {language} code, including installation, usage, and examples:",
        }

        prompt = doc_prompts.get(doc_type, doc_prompts["comprehensive"])
        prompt += f"\n\n{code}"

        if context:
            prompt += f"\n\nAdditional context: {context}"

        # Generate documentation based on provider
        if provider == "openai":
            response = client.chat.completions.create(
                model=model, messages=[{"role": "user", "content": prompt}], **kwargs
            )
            documentation = response.choices[0].message.content
            tokens_used = response.usage.total_tokens if response.usage else None

        elif provider == "anthropic":
            response = client.messages.create(
                model=model, messages=[{"role": "user", "content": prompt}], **kwargs
            )
            documentation = response.content[0].text
            tokens_used = (
                response.usage.input_tokens + response.usage.output_tokens
                if response.usage
                else None
            )

        elif provider == "google":
            model_instance = client.GenerativeModel(model)
            response = model_instance.generate_content(prompt)
            documentation = response.text
            tokens_used = None

        else:
            raise ValueError(f"Unsupported provider: {provider}")

        execution_time = time.time() - start_time

        # Return result
        result = {
            "code": code,
            "documentation": documentation,
            "doc_type": doc_type,
            "language": language,
            "provider": provider,
            "model": model,
            "execution_time": execution_time,
            "tokens_used": tokens_used,
            "metadata": {
                "context": context,
            },
        }

        logger.info(
            f"Generated {doc_type} documentation for {language} code using {provider}/{model} in {execution_time:.2f}s"
        )
        return result

    except Exception as e:
        logger.error(f"Error generating documentation: {e}")
        raise RuntimeError(f"Documentation generation failed: {e}")


def get_supported_languages() -> List[CodeLanguage]:
    """Get list of supported programming languages."""
    return list(CodeLanguage)


def get_supported_providers() -> List[str]:
    """Get list of supported LLM providers."""
    return ["openai", "anthropic", "google"]


def get_available_models(provider: str) -> List[str]:
    """Get list of available models for a provider."""
    models = {
        "openai": ["gpt-3.5-turbo", "gpt-4", "gpt-4-turbo"],
        "anthropic": ["claude-instant-1", "claude-2", "claude-3-sonnet"],
        "google": ["gemini-pro", "gemini-pro-vision"],
    }
    return models.get(provider.lower(), [])


def validate_api_keys() -> Dict[str, bool]:
    """Validate API keys for all supported providers."""
    validation_results = {}

    for provider in get_supported_providers():
        key_name = f"{provider.upper()}_API_KEY"
        validation_results[provider] = bool(os.environ.get(key_name))

    return validation_results


def setup_environment() -> bool:
    """Setup environment variables and check dependencies."""
    try:
        # Check and setup environment variables if available
        if check_and_setup_env_vars:
            check_and_setup_env_vars()

        # Validate API keys
        api_keys = validate_api_keys()
        available_providers = [
            provider for provider, available in api_keys.items() if available
        ]

        if not available_providers:
            logger.warning("No API keys found for any LLM provider")
            return False

        logger.info(f"Available LLM providers: {', '.join(available_providers)}")
        return True

    except Exception as e:
        logger.error(f"Error setting up environment: {e}")
        return False
