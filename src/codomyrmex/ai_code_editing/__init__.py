"""
AI Code Editing Module for Codomyrmex.

This module provides comprehensive utilities for AI-powered code generation, editing, and analysis.

Integration:
- Uses `logging_monitoring` for all logging (ensure `setup_logging()` is called in your main app).
- Relies on `environment_setup` for environment and dependency checks (see project setup docs).

Available functions:
- generate_code_snippet: Generate code snippets using LLMs
- refactor_code_snippet: Refactor existing code using LLMs
- analyze_code_quality: Analyze code quality and provide suggestions
- generate_code_batch: Generate multiple code snippets in batch
- compare_code_versions: Compare two versions of code
- generate_code_documentation: Generate documentation for code
- get_supported_languages: Get list of supported programming languages
- get_supported_providers: Get list of supported LLM providers
- get_available_models: Get available models for a provider
- validate_api_keys: Validate API keys for all providers
- setup_environment: Setup environment and check dependencies

Data structures:
- CodeGenerationRequest: Request structure for code generation
- CodeRefactoringRequest: Request structure for code refactoring
- CodeAnalysisRequest: Request structure for code analysis
- CodeGenerationResult: Result structure for code generation
- CodeLanguage: Enum of supported programming languages
- CodeComplexity: Enum of code complexity levels
- CodeStyle: Enum of code style preferences
"""

from .ai_code_helpers import (
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

__all__ = [
    'generate_code_snippet',
    'refactor_code_snippet',
    'analyze_code_quality',
    'generate_code_batch',
    'compare_code_versions',
    'generate_code_documentation',
    'get_supported_languages',
    'get_supported_providers',
    'get_available_models',
    'validate_api_keys',
    'setup_environment',
    'CodeGenerationRequest',
    'CodeRefactoringRequest',
    'CodeAnalysisRequest',
    'CodeGenerationResult',
    'CodeLanguage',
    'CodeComplexity',
    'CodeStyle',
] 