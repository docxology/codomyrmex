# Codomyrmex Agents — src/codomyrmex/llm/fabric

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: January 2026

## Purpose

Provides integration with the Fabric AI framework, enabling pattern-based AI workflows and orchestration. Fabric provides pre-built AI patterns for common tasks like summarization, extraction, and analysis.

## Active Components

- `fabric_manager.py` - Core Fabric service management
- `fabric_orchestrator.py` - Pattern-based workflow orchestration
- `fabric_config_manager.py` - Configuration management for Fabric settings
- `__init__.py` - Module exports
- `SPEC.md` - Module specification
- `README.md` - Module documentation

## Key Classes and Functions

### fabric_manager.py
- **`FabricManager`** - Main interface for Fabric operations
  - `list_patterns()` - Lists available Fabric patterns
  - `run_pattern(pattern_name, input_text, options)` - Executes a pattern
  - `get_pattern_info(pattern_name)` - Gets pattern documentation
  - `install_pattern(pattern_name)` - Installs a pattern from repository
  - `check_fabric_installation()` - Verifies Fabric is installed

### fabric_orchestrator.py
- **`FabricOrchestrator`** - Orchestrates multi-pattern workflows
  - `create_pipeline(patterns)` - Creates a pattern pipeline
  - `execute_pipeline(input_text)` - Runs pipeline sequentially
  - `parallel_execute(patterns, input_texts)` - Runs patterns in parallel
  - `get_pipeline_status()` - Gets current pipeline execution status

### fabric_config_manager.py
- **`FabricConfigManager`** - Manages Fabric configuration
  - `load_config()` - Loads Fabric configuration
  - `save_config(config)` - Persists configuration
  - `get_default_model()` - Gets default model for patterns
  - `set_patterns_path(path)` - Sets custom patterns directory

## Operating Contracts

- Fabric CLI must be installed and accessible
- Patterns validated before execution
- Pipeline failures handled with partial result recovery
- Configuration changes validated before persistence
- Pattern outputs conform to expected schemas

## Signposting

- **Dependencies**: Requires Fabric CLI installation, Go runtime
- **Parent Directory**: [llm](../README.md) - Parent module documentation
- **Related Modules**:
  - `ollama/` - Local LLM backend for Fabric
  - `outputs/` - Output storage and analysis
  - `prompt_templates/` - Complementary prompt templates
- **Project Root**: [../../../../README.md](../../../../README.md) - Main project documentation
