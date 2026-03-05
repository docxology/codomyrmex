"""AI Code Editing Helpers.

This module provides AI-powered code generation, refactoring, analysis,
and documentation utilities using multiple LLM providers.
"""

from .analysis import analyze_code_quality, compare_code_versions
from .config import (
    DEFAULT_LLM_MODEL,
    DEFAULT_LLM_PROVIDER,
    MAX_RETRIES,
    OLLAMA_AVAILABLE,
    RETRY_DELAY,
    get_llm_client,
)
from .generation import (
    generate_code_batch,
    generate_code_documentation,
    generate_code_snippet,
)
from .models import (
    CodeAnalysisRequest,
    CodeComplexity,
    CodeGenerationRequest,
    CodeGenerationResult,
    CodeLanguage,
    CodeRefactoringRequest,
    CodeStyle,
)
from .refactoring import refactor_code_snippet
from .utils import (
    get_available_models,
    get_supported_languages,
    get_supported_providers,
    setup_environment,
    validate_api_keys,
)

__all__ = [
    "DEFAULT_LLM_MODEL",
    "DEFAULT_LLM_PROVIDER",
    "MAX_RETRIES",
    "OLLAMA_AVAILABLE",
    "RETRY_DELAY",
    "CodeAnalysisRequest",
    "CodeComplexity",
    "CodeGenerationRequest",
    "CodeGenerationResult",
    "CodeLanguage",
    "CodeRefactoringRequest",
    "CodeStyle",
    "analyze_code_quality",
    "compare_code_versions",
    "generate_code_batch",
    "generate_code_documentation",
    "generate_code_snippet",
    "get_available_models",
    "get_llm_client",
    "get_supported_languages",
    "get_supported_providers",
    "refactor_code_snippet",
    "setup_environment",
    "validate_api_keys",
]
