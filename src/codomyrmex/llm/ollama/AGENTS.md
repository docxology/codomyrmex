# Codomyrmex Agents — src/codomyrmex/llm/ollama

## Signposting
- **Parent**: [llm](../AGENTS.md)
- **Self**: [Agents](AGENTS.md)
- **Children**:
    - None
- **Key Artifacts**:
    - [Functional Spec](SPEC.md)
    - [Human Readme](README.md)

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: January 2026

## Purpose
Integration with Ollama local Large Language Models. Provides comprehensive model management, execution, and output handling optimized for the Codomyrmex ecosystem. Supports model listing, pulling, execution, configuration management, and output persistence.

## Active Components
- `API_SPECIFICATION.md` – Detailed API specification
- `MODEL_CONFIGS.md` – Model configuration documentation
- `PARAMETERS.md` – Parameter documentation
- `README.md` – Project file
- `SECURITY.md` – Security considerations
- `SPEC.md` – Project file
- `VERIFICATION.md` – Verification documentation
- `__init__.py` – Module exports and public API
- `config_manager.py` – Configuration management
- `model_runner.py` – Model execution with performance optimization
- `ollama_manager.py` – Main Ollama integration manager
- `output_manager.py` – Output handling and persistence

## Key Classes and Functions

### OllamaManager (`ollama_manager.py`)
- `OllamaManager(ollama_binary: str = "ollama", auto_start_server: bool = True, base_url: str = "http://localhost:11434", use_http_api: bool = True)` – Main Ollama integration manager
- `list_models() -> List[OllamaModel]` – Retrieve available Ollama models
- `pull_model(model_name: str, **kwargs) -> Dict` – Download and install Ollama model
- `run_model(model_name: str, prompt: str, **kwargs) -> ModelExecutionResult` – Execute model inference with prompt
- `get_model_info(model_name: str) -> Dict` – Retrieve detailed model information
- `_ensure_server_running() -> bool` – Ensure Ollama server is running

### OllamaModel (`ollama_manager.py`)
- `OllamaModel` (dataclass) – Represents an Ollama model with metadata:
  - `name: str` – Model name
  - `id: str` – Model ID
  - `size: int` – Size in bytes
  - `modified: str` – Modification timestamp
  - `parameters: Optional[str]` – Model parameters
  - `family: Optional[str]` – Model family
  - `format: Optional[str]` – Model format
  - `status: str` – Model status

### ModelRunner (`model_runner.py`)
- `ModelRunner()` – Specialized model execution with performance optimization
- `execute(prompt: str, model: str, **kwargs) -> Dict` – Execute model inference with optimized performance
- `stream(prompt: str, model: str, **kwargs) -> Iterator[StreamingChunk]` – Stream model inference

### ExecutionOptions (`model_runner.py`)
- `ExecutionOptions` (dataclass) – Execution options:
  - `temperature: Optional[float]` – Temperature parameter
  - `top_p: Optional[float]` – Top-p parameter
  - `top_k: Optional[int]` – Top-k parameter
  - `context_window: Optional[int]` – Context window size

### ConfigManager (`config_manager.py`)
- `ConfigManager()` – Handles Ollama configurations and settings
- `OllamaConfig` (dataclass) – Complete Ollama configuration
- `load_config(config_path: str) -> OllamaConfig` – Load configuration
- `save_config(config: OllamaConfig, config_path: str) -> None` – Save configuration

### OutputManager (`output_manager.py`)
- `OutputManager()` – Output handling and persistence
- `save_output(output: dict, output_path: str) -> None` – Save model output
- `load_output(output_path: str) -> dict` – Load model output

## Operating Contracts
- Maintain alignment between code, documentation, and configured workflows.
- Ensure Model Context Protocol interfaces remain available for sibling agents.
- Record outcomes in shared telemetry and update TODO queues when necessary.

## Navigation Links
- **Human Documentation**: [README.md](README.md)
- **Functional Specification**: [SPEC.md](SPEC.md)
- **📁 Parent Directory**: [llm](../README.md) - Parent directory documentation
- **🏠 Project Root**: [README](../../../../README.md) - Main project documentation