# Codomyrmex Agents — src/codomyrmex/llm

## Signposting
- **Parent**: [codomyrmex](../AGENTS.md)
- **Self**: [LLM Agents](AGENTS.md)
- **Children**:
    - [ollama](ollama/AGENTS.md)
    - [prompt_templates](prompt_templates/AGENTS.md)
    - [outputs](outputs/AGENTS.md)
- **Key Artifacts**:
    - None

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: December 2025

## Purpose

LLM integration namespace for Codomyrmex, providing a logical grouping for Large Language Model provider integrations. This namespace currently contains the Ollama integration module and is designed to accommodate future LLM provider integrations.

## Module Overview

### Key Capabilities
- **Provider Integration**: Integration with local and cloud LLM providers
- **Unified Interface**: Common API patterns across different providers
- **Model Management**: Provider-agnostic model management capabilities

### Current Modules
- `ollama/` - Ollama local LLM integration
- `prompt_templates/` - Standardized prompt templates for AI interactions
- `outputs/` - LLM output management and processing
  - `outputs/llm_outputs/` - Core LLM output handling
  - `outputs/integration/` - Integration testing outputs
  - `outputs/performance/` - Performance evaluation outputs
  - `outputs/reports/` - Generated reports
  - `outputs/test_results/` - Test result outputs

## Navigation Links
- **Human Documentation**: [README.md](README.md)
- **Functional Specification**: [SPEC.md](SPEC.md)
- **Parent**: [codomyrmex](../AGENTS.md) - Package overview
- **Ollama Integration**: [ollama/AGENTS.md](ollama/AGENTS.md) - Ollama integration documentation



## Active Components
- `__init__.py` - Component file.
- `ollama/` - Agent surface for ollama components.
- `prompt_templates/` - Agent surface for prompt_templates components.


### Additional Files
- `__pycache__` –   Pycache  
- `ollama` – Ollama
- `prompt_templates` – Prompt Templates

## Operating Contracts
- Maintain alignment between code, documentation, and configured workflows.
- Ensure Model Context Protocol interfaces remain available for sibling agents.
- Record outcomes in shared telemetry and update task queues when necessary.

## Detailed Architecture and Implementation

The implementation of this component follows the core principles of the Codomyrmex ecosystem: modularity, performance, and reliability. By adhering to standardized interfaces, this module ensures seamless integration with the broader platform.

### Design Principles
1.  **Strict Modularity**: Each component is isolated and communicates via well-defined APIs.
2.  **Performance Optimization**: Implementation leverages lazy loading and intelligent caching to minimize resource overhead.
3.  **Error Resilience**: Robust exception handling ensures system stability even under unexpected conditions.
4.  **Extensibility**: The architecture is designed to accommodate future enhancements without breaking existing contracts.

### Technical Implementation
The codebase utilizes modern Python features (version 3.10+) to provide a clean, type-safe API. Interaction patterns are documented in the corresponding `AGENTS.md` and `SPEC.md` files, ensuring that both human developers and automated agents can effectively utilize these capabilities.
