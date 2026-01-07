# fabric

## Signposting
- **Parent**: [llm](../README.md)
- **Children**:
    - None
- **Key Artifacts**:
    - [Agent Guide](AGENTS.md)
    - [Functional Spec](SPEC.md)

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: January 2026

## Overview

Integration with Fabric AI framework. Provides comprehensive pattern management, execution, and workflow orchestration optimized for the Codomyrmex ecosystem. Supports pattern listing, execution, configuration management, and integration with Codomyrmex modules.

## Directory Contents
- `README.md` – File
- `SPEC.md` – File
- `AGENTS.md` – File
- `__init__.py` – File
- `fabric_manager.py` – File
- `fabric_orchestrator.py` – File
- `fabric_config_manager.py` – File

## Navigation
- **Technical Documentation**: [AGENTS.md](AGENTS.md)
- **Functional Specification**: [SPEC.md](SPEC.md)
- **Parent Directory**: [llm](../README.md)
- **Project Root**: [README](../../../../README.md)

## Getting Started

To use this module in your project, import the necessary components:

```python
from codomyrmex.llm.fabric import FabricManager, FabricOrchestrator, FabricConfigManager

# Initialize Fabric manager
manager = FabricManager()

# Check if Fabric is available
if manager.is_available():
    # List available patterns
    patterns = manager.list_patterns()
    print(f"Available patterns: {patterns[:5]}")
    
    # Run a pattern
    result = manager.run_pattern("summarize", "Your text here")
    print(f"Result: {result['output']}")
else:
    print("Fabric not available. Please install Fabric first.")

# Use orchestrator for workflows
orchestrator = FabricOrchestrator()
analysis = orchestrator.analyze_code(code_content, analysis_type="quality")

# Manage configuration
config_manager = FabricConfigManager()
config_manager.ensure_directories()
config_manager.create_codomyrmex_patterns()
```

