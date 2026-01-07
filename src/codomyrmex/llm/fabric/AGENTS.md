# Codomyrmex Agents — src/codomyrmex/llm/fabric

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
Integration with Fabric AI framework. Provides comprehensive pattern management, execution, and workflow orchestration optimized for the Codomyrmex ecosystem. Supports pattern listing, execution, configuration management, and integration with Codomyrmex modules.

## Active Components
- `README.md` – Project file
- `SPEC.md` – Project file
- `__init__.py` – Module exports and public API
- `fabric_manager.py` – Main Fabric integration manager
- `fabric_orchestrator.py` – Workflow orchestration
- `fabric_config_manager.py` – Configuration management

## Key Classes and Functions

### FabricManager (`fabric_manager.py`)
- `FabricManager(fabric_binary: str = "fabric")` – Main Fabric integration manager
- `list_patterns() -> List[str]` – Retrieve available Fabric patterns
- `run_pattern(pattern: str, input_text: str, additional_args: Optional[List[str]] = None) -> Dict[str, Any]` – Execute Fabric pattern with input
- `is_available() -> bool` – Check if Fabric binary is available
- `get_results_history() -> List[Dict[str, Any]]` – Get history of pattern execution results

### FabricOrchestrator (`fabric_orchestrator.py`)
- `FabricOrchestrator(fabric_binary: str = "fabric")` – Orchestrates workflows combining Fabric patterns with Codomyrmex capabilities
- `analyze_code(code_content: str, analysis_type: str = "comprehensive") -> Dict[str, Any]` – Analyze code using appropriate Fabric patterns
- `create_workflow_visualization(output_path: str = "workflow_metrics.png") -> bool` – Create visualization of workflow results
- `list_patterns() -> List[str]` – Get list of available Fabric patterns
- `is_available() -> bool` – Check if Fabric is available

### FabricConfigManager (`fabric_config_manager.py`)
- `FabricConfigManager(config_dir: Optional[str] = None)` – Manages Fabric configuration and integration settings
- `ensure_directories() -> bool` – Ensure all required directories exist
- `list_available_patterns() -> List[str]` – List all available Fabric patterns
- `create_custom_pattern(name: str, system_prompt: str, description: str = "") -> bool` – Create a custom Fabric pattern
- `create_codomyrmex_patterns() -> bool` – Create Codomyrmex-specific Fabric patterns
- `export_configuration(output_file: str) -> bool` – Export current Fabric configuration

## Operating Contracts
- Maintain alignment between code, documentation, and configured workflows.
- Ensure Model Context Protocol interfaces remain available for sibling agents.
- Record outcomes in shared telemetry and update TODO queues when necessary.

## Navigation Links
- **Human Documentation**: [README.md](README.md)
- **Functional Specification**: [SPEC.md](SPEC.md)
- **📁 Parent Directory**: [llm](../README.md) - Parent directory documentation
- **🏠 Project Root**: [README](../../../../README.md) - Main project documentation

