# Codomyrmex Agents — src/codomyrmex/agents/ai_code_editing

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: January 2026

## Purpose

AI Code Editing module providing comprehensive utilities for AI-powered code generation, refactoring, analysis, and documentation. This module serves as the primary interface for code transformation tasks using various LLM providers.

## Active Components

- `ai_code_helpers.py` - Core code generation and analysis functions
- `code_editor.py` - Code editing utilities
- `claude_task_master.py` - Claude-specific task handling
- `openai_codex.py` - OpenAI Codex integration
- `droid_manager.py` - Droid task management integration
- `prompt_composition.py` - Prompt engineering utilities
- `__init__.py` - Module exports
- `README.md` - Module documentation
- `SPEC.md` - Specification document
- `API_SPECIFICATION.md` - API documentation
- `MCP_TOOL_SPECIFICATION.md` - MCP tool specifications
- `PROMPT_ENGINEERING.md` - Prompt engineering guide
- `USAGE_EXAMPLES.md` - Usage examples
- `requirements.txt` - Module dependencies

## Key Classes and Functions

### Code Generation
- **`generate_code_snippet()`** - Generate code snippets using LLMs
- **`generate_code_batch()`** - Generate multiple code snippets in batch
- **`generate_code_documentation()`** - Generate documentation for code

### Code Transformation
- **`refactor_code_snippet()`** - Refactor existing code using LLMs
- **`compare_code_versions()`** - Compare two versions of code

### Code Analysis
- **`analyze_code_quality()`** - Analyze code quality and provide suggestions

### Configuration and Setup
- **`get_supported_languages()`** - Get list of supported programming languages
- **`get_supported_providers()`** - Get list of supported LLM providers
- **`get_available_models()`** - Get available models for a provider
- **`validate_api_keys()`** - Validate API keys for all providers
- **`setup_environment()`** - Setup environment and check dependencies

### Data Structures
- **`CodeGenerationRequest`** - Request structure for code generation
- **`CodeRefactoringRequest`** - Request structure for code refactoring
- **`CodeAnalysisRequest`** - Request structure for code analysis
- **`CodeGenerationResult`** - Result structure for code generation
- **`CodeLanguage`** - Enum of supported programming languages
- **`CodeComplexity`** - Enum of code complexity levels
- **`CodeStyle`** - Enum of code style preferences

### Droid Integration (re-exported from droid module)
- **`DroidController`** - Task automation controller
- **`DroidConfig`** - Droid configuration
- **`DroidMode`** - Operation mode enum
- **`DroidStatus`** - Status enum
- **`DroidMetrics`** - Performance metrics
- **`TodoManager`** - Todo list management
- **`TodoItem`** - Todo item dataclass
- **`create_default_controller()`** - Factory for default controller
- **`load_config_from_file()`** - Load configuration from file
- **`save_config_to_file()`** - Save configuration to file

## Operating Contracts

- Uses `logging_monitoring` for all logging (ensure `setup_logging()` is called).
- Relies on `environment_setup` for environment and dependency checks.
- Requires valid API keys for the LLM providers being used.
- Follows structured request/response patterns for all operations.
- Supports multiple code styles and complexity levels.

## Signposting

- **Generating code?** Use `generate_code_snippet()` with `CodeGenerationRequest`.
- **Refactoring?** Use `refactor_code_snippet()` with `CodeRefactoringRequest`.
- **Code analysis?** Use `analyze_code_quality()` with `CodeAnalysisRequest`.
- **Batch operations?** Use `generate_code_batch()` for multiple snippets.
- **Task automation?** Use the re-exported Droid classes.
- **Prompt customization?** See `prompt_composition.py` and `PROMPT_ENGINEERING.md`.

## Navigation Links

- **Parent Directory**: [agents](../README.md) - Parent directory documentation
- **Droid Module**: [droid](../droid/AGENTS.md) - Task automation
- **Core Module**: [core](../core/AGENTS.md) - Base classes and interfaces
- **Project Root**: ../../../../README.md - Main project documentation
