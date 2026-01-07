# Codomyrmex Agents — src/codomyrmex/llm

## Signposting
- **Parent**: [codomyrmex](../AGENTS.md)
- **Self**: [Agents](AGENTS.md)
- **Children**:
    - [ollama](ollama/AGENTS.md)
    - [fabric](fabric/AGENTS.md)
    - [outputs](outputs/AGENTS.md)
    - [prompt_templates](prompt_templates/AGENTS.md)
- **Key Artifacts**:
    - [Functional Spec](SPEC.md)
    - [Human Readme](README.md)

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: January 2026

## Purpose
Language model integration, prompt management, and output handling for the Codomyrmex platform. Provides multi-provider support (Ollama, OpenAI, Anthropic, local models), prompt template management, output parsing and validation, and streaming response support.

## Active Components
- `README.md` – Project file
- `SPEC.md` – Project file
- `__init__.py` – Module exports and public API
- `config.py` – LLM configuration management (LLMConfig, LLMConfigPresets)
- `ollama/` – Directory containing Ollama integration (OllamaManager, ModelRunner, OutputManager, ConfigManager)
- `fabric/` – Directory containing Fabric integration (FabricManager, FabricOrchestrator, FabricConfigManager)
- `outputs/` – Directory containing output handling components
- `prompt_templates/` – Directory containing prompt template management

## Key Classes and Functions

### OllamaManager (`ollama/ollama_manager.py`)
- `OllamaManager(ollama_binary: str = "ollama", auto_start_server: bool = True, base_url: str = "http://localhost:11434", use_http_api: bool = True)` – Main Ollama integration manager
- `list_models() -> List[Dict]` – Retrieve available Ollama models
- `pull_model(model_name: str, **kwargs) -> Dict` – Download and install Ollama model
- `run_model(model_name: str, prompt: str, **kwargs) -> Dict` – Execute model inference with prompt
- `get_model_info(model_name: str) -> Dict` – Retrieve detailed model information

### ModelRunner (`ollama/model_runner.py`)
- `ModelRunner(ollama_manager: OllamaManager)` – Specialized model execution with performance optimization
- `execute(prompt: str, model: str, **kwargs) -> Dict` – Execute model inference with optimized performance

### OutputManager (`ollama/output_manager.py`)
- `OutputManager()` – Manages output formatting and processing

### ConfigManager (`ollama/config_manager.py`)
- `ConfigManager()` – Manages Ollama-specific configuration

### LLMConfig (`config.py`)
- `LLMConfig` – Configuration class for LLM operations
- `LLMConfigPresets` – Preset configurations for common use cases

### FabricManager (`fabric/fabric_manager.py`)
- `FabricManager(fabric_binary: str = "fabric")` – Main Fabric integration manager
- `list_patterns() -> List[str]` – Retrieve available Fabric patterns
- `run_pattern(pattern: str, input_text: str, additional_args: Optional[List[str]] = None) -> Dict[str, Any]` – Execute Fabric pattern

### FabricOrchestrator (`fabric/fabric_orchestrator.py`)
- `FabricOrchestrator(fabric_binary: str = "fabric")` – Orchestrates workflows combining Fabric patterns with Codomyrmex capabilities
- `analyze_code(code_content: str, analysis_type: str = "comprehensive") -> Dict[str, Any]` – Analyze code using appropriate Fabric patterns

### FabricConfigManager (`fabric/fabric_config_manager.py`)
- `FabricConfigManager(config_dir: Optional[str] = None)` – Manages Fabric configuration and integration settings
- `create_codomyrmex_patterns() -> bool` – Create Codomyrmex-specific Fabric patterns

### Module Functions (`__init__.py`)
- `get_config() -> LLMConfig` – Get current LLM configuration
- `set_config(config: LLMConfig) -> None` – Set LLM configuration
- `reset_config() -> None` – Reset configuration to defaults

## Operating Contracts
- Maintain alignment between code, documentation, and configured workflows.
- Ensure Model Context Protocol interfaces remain available for sibling agents.
- Record outcomes in shared telemetry and update TODO queues when necessary.

## Navigation Links
- **Human Documentation**: [README.md](README.md)
- **Functional Specification**: [SPEC.md](SPEC.md)
- **📁 Parent Directory**: [codomyrmex](../README.md) - Parent directory documentation
- **🏠 Project Root**: [README](../../../README.md) - Main project documentation