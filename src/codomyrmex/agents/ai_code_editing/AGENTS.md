# Codomyrmex Agents — src/codomyrmex/agents/ai_code_editing

## Signposting
- **Parent**: [agents](../AGENTS.md)
- **Self**: [Agents](AGENTS.md)
- **Children**:
    - [docs](docs/AGENTS.md)
    - [tests](tests/AGENTS.md)
- **Key Artifacts**:
    - [Functional Spec](SPEC.md)
    - [Human Readme](README.md)

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: January 2026

## Purpose
Semantic intelligence layer for AI-powered code generation, editing, and analysis. Abstracts complexity of interacting with various LLM providers (OpenAI, Anthropic, Google) to provide high-level code manipulation capabilities: generation, refactoring, analysis, and documentation. Provider-agnostic with unified prompting and standardized context.

## Active Components
- `API_SPECIFICATION.md` – Detailed API specification
- `CHANGELOG.md` – Version history
- `MCP_TOOL_SPECIFICATION.md` – MCP tool specification
- `PROMPT_ENGINEERING.md` – Prompt engineering documentation
- `README.md` – Project file
- `SECURITY.md` – Security considerations
- `SPEC.md` – Project file
- `USAGE_EXAMPLES.md` – Usage examples
- `__init__.py` – Module exports and public API
- `ai_code_helpers.py` – Core code generation and analysis helpers
- `claude_task_master.py` – Claude-based task management
- `docs/` – Directory containing docs components
- `droid_manager.py` – Droid management for autonomous agents
- `openai_codex.py` – OpenAI Codex integration
- `prompt_composition.py` – Prompt composition utilities
- `requirements.txt` – Project file
- `tests/` – Directory containing tests components

## Key Classes and Functions

### Code Generation (`ai_code_helpers.py`)
- `generate_code_snippet(prompt: str, language: str, provider: str = "openai", model_name: Optional[str] = None, context: Optional[str] = None, max_length: Optional[int] = None, temperature: float = 0.7, **kwargs) -> dict` – Generate code in requested language
- `generate_code_batch(prompts: list[str], language: str, **kwargs) -> list[dict]` – Generate multiple code snippets in batch
- `generate_code_documentation(code: str, language: str, **kwargs) -> str` – Generate documentation for code

### Code Refactoring (`ai_code_helpers.py`)
- `refactor_code_snippet(code: str, refactoring_type: str, language: str, provider: str = "openai", model_name: Optional[str] = None, context: Optional[str] = None, preserve_functionality: bool = True, **kwargs) -> dict` – Refactor existing code

### Code Analysis (`ai_code_helpers.py`)
- `analyze_code_quality(code: str, language: str, **kwargs) -> dict` – Analyze code quality and provide suggestions
- `compare_code_versions(code1: str, code2: str, language: str, **kwargs) -> dict` – Compare two versions of code

### Data Structures (`ai_code_helpers.py`)
- `CodeGenerationRequest` (dataclass) – Request structure for code generation
- `CodeRefactoringRequest` (dataclass) – Request structure for code refactoring
- `CodeAnalysisRequest` (dataclass) – Request structure for code analysis
- `CodeGenerationResult` (dataclass) – Result structure for code generation
- `CodeLanguage` (Enum) – Enum of supported programming languages
- `CodeComplexity` (Enum) – Enum of code complexity levels
- `CodeStyle` (Enum) – Enum of code style preferences

### Provider Management (`ai_code_helpers.py`)
- `get_supported_languages() -> list[str]` – Get list of supported programming languages
- `get_supported_providers() -> list[str]` – Get list of supported LLM providers
- `get_available_models(provider: str) -> list[str]` – Get available models for a provider
- `validate_api_keys() -> dict[str, bool]` – Validate API keys for all providers
- `setup_environment() -> bool` – Setup environment and check dependencies

### PromptComposition (`prompt_composition.py`)
- `PromptComposition()` – Prompt composition utilities
- `compose_prompt(template: str, context: dict) -> str` – Compose prompt from template

### DroidManager (`droid_manager.py`)
- `DroidManager()` – Manage autonomous agent droids
- Integrates with droid module for task execution

## Operating Contracts
- Maintain alignment between code, documentation, and configured workflows.
- Ensure Model Context Protocol interfaces remain available for sibling agents.
- Record outcomes in shared telemetry and update TODO queues when necessary.

## Navigation Links
- **Human Documentation**: [README.md](README.md)
- **Functional Specification**: [SPEC.md](SPEC.md)
- **📁 Parent Directory**: [agents](../README.md) - Parent directory documentation
- **🏠 Project Root**: [README](../../../../README.md) - Main project documentation