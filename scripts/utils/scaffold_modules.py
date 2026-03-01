#!/usr/bin/env python3
"""
Module Scaffolding Script

Generates the RASP documentation structure (README, AGENTS, SPEC, PAI)
plus __init__.py for new submodules and modules.

Usage:
    python scaffold_modules.py --dry-run  # Preview changes
    python scaffold_modules.py            # Execute creation
"""

import sys
from pathlib import Path
from datetime import datetime
from codomyrmex.utils.cli_helpers import setup_logging, print_info, print_success, print_warning

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# ============================================================================
# SUBMODULE DEFINITIONS
# ============================================================================

SUBMODULES = {
    "agents": [
        ("o1", "OpenAI o1/o3 reasoning model integration for advanced multi-step reasoning tasks"),
        ("deepseek", "DeepSeek Coder integration for code generation and analysis"),
        ("qwen", "Qwen-Coder integration for multilingual code assistance"),
        ("pooling", "Multi-agent load balancing, failover, and intelligent routing"),
        ("evaluation", "Agent benchmarking, quality metrics, and performance comparison"),
        ("history", "Conversation and context persistence for stateful interactions"),
    ],
    "llm": [
        ("guardrails", "Input/output safety validation including prompt injection defense"),
        ("streaming", "Streaming response handlers for real-time LLM output processing"),
        ("embeddings", "Text embedding generation, caching, and similarity search"),
        ("rag", "Retrieval-Augmented Generation pipeline with document processing"),
        ("cost_tracking", "Token counting, billing estimation, and usage analytics"),
        ("prompts", "Enhanced prompt versioning, storage, and template management"),
    ],
    "api": [
        ("webhooks", "Webhook dispatch and receipt management for event-driven APIs"),
        ("mocking", "API mock server for development and testing workflows"),
        ("circuit_breaker", "Resilience patterns including retry, circuit breaker, and bulkhead"),
        ("pagination", "Cursor and offset pagination utilities for API responses"),
    ],
    "cache": [
        ("warmers", "Cache pre-population and predictive caching strategies"),
        ("async_ops", "Async cache operations for non-blocking cache access"),
        ("replication", "Cross-region cache synchronization and consistency"),
    ],
    "security": [
        ("scanning", "SAST/DAST integration for automated security testing"),
        ("secrets", "Secret detection, rotation, and secure storage management"),
        ("compliance", "GDPR, SOC2, HIPAA compliance checking and reporting"),
        ("audit", "Security audit logging and forensic analysis"),
    ],
    "telemetry": [
        ("tracing", "Distributed tracing setup helpers and context propagation"),
        ("sampling", "Dynamic sampling strategies for high-volume telemetry"),
        ("alerting", "Alert rule configuration and notification routing"),
    ],
    "orchestrator": [
        ("pipelines", "Multi-step pipeline definitions with DAG support"),
        ("triggers", "Event and time-based workflow triggers"),
        ("state", "State machine implementations for workflow control"),
        ("templates", "Reusable workflow templates and patterns"),
    ],
    "database_management": [
        ("connections", "Connection pooling, lifecycle management, and health checks"),
        ("replication", "Read replica routing and load balancing"),
        ("sharding", "Horizontal sharding utilities and partition management"),
        ("audit", "Query logging, analysis, and slow query detection"),
    ],
    "validation": [
        ("schemas", "Schema registry, versioning, and evolution management"),
        ("sanitizers", "Input sanitization and normalization utilities"),
        ("rules", "Custom validation rule definitions and composition"),
    ],
    "skills": [
        ("marketplace", "Skill discovery from external sources and repositories"),
        ("versioning", "Skill version management and compatibility tracking"),
        ("permissions", "Skill capability permissions and access control"),
    ],
}

# ============================================================================
# NEW MODULE DEFINITIONS
# ============================================================================

NEW_MODULES = [
    ("graph_rag", "Knowledge graph integration with RAG for structured knowledge retrieval and reasoning"),
    ("agentic_memory", "Long-term agent memory systems for stateful, persistent agent interactions"),
    ("prompt_testing", "Prompt evaluation, A/B testing, and quality assurance at scale"),
    ("inference_optimization", "Model quantization, distillation, and pruning for cost-effective inference"),
    ("multimodal", "Vision, audio, and image processing for multi-modal AI workflows"),
    ("cost_management", "Cloud and API spend tracking, optimization, and budget alerting"),
    ("observability_dashboard", "Unified dashboards for telemetry visualization and monitoring"),
    ("workflow_testing", "End-to-end workflow validation and integration testing"),
    ("migration", "Cross-provider migration tools for cloud and database transitions"),
    ("data_lineage", "Data provenance tracking and transformation audit trails"),
    ("notification", "Multi-channel notification dispatch including email, Slack, and SMS"),
    ("feature_store", "ML feature management, versioning, and serving"),
    ("model_registry", "ML model versioning, storage, and deployment tracking"),
]


def generate_readme(name: str, description: str, parent: str = None) -> str:
    """Generate README.md content."""
    full_name = f"{parent}/{name}" if parent else name
    return f'''# {name.replace("_", " ").title()}

{description}

## Overview

The `{name}` {"submodule" if parent else "module"} provides {description.lower()}.

## Installation

This {"submodule" if parent else "module"} is part of the Codomyrmex platform and is installed with the main package.

```bash
pip install codomyrmex
```

## Quick Start

```python
from codomyrmex.{full_name.replace("/", ".")} import *

# Minimal usage example (update after implementation):
# obj = SomeClass()
# result = obj.some_method()
```

## Features

- Feature 1: Description
- Feature 2: Description
- Feature 3: Description

## API Reference

See [API_SPECIFICATION.md](./API_SPECIFICATION.md) for detailed API documentation.

## Related Modules

- [`{parent}`](../) - Parent module
'''


def generate_agents(name: str, description: str, parent: str = None) -> str:
    """Generate AGENTS.md content."""
    full_name = f"{parent}/{name}" if parent else name
    return f'''# AI Agent Guidelines - {name.replace("_", " ").title()}

**Module**: `codomyrmex.{full_name.replace("/", ".")}`  
**Version**: v0.1.0  
**Status**: Active

## Purpose

{description}

## Agent Instructions

When working with this {"submodule" if parent else "module"}:

### Key Patterns

1. **Import Convention**:
   ```python
   from codomyrmex.{full_name.replace("/", ".")} import <specific_import>
   ```

2. **Error Handling**: Always handle exceptions gracefully
3. **Configuration**: Check for required environment variables

### Common Operations

- Operation 1: Description
- Operation 2: Description

### Integration Points

- Integrates with: `{parent}` (parent module)
- Dependencies: Listed in `__init__.py`

## File Reference

| File | Purpose |
|------|---------|
| `__init__.py` | Module exports and initialization |
| `README.md` | User documentation |
| `SPEC.md` | Technical specification |

## Troubleshooting

Common issues and solutions:

1. **Issue**: Description
   **Solution**: Resolution steps
'''


def generate_spec(name: str, description: str, parent: str = None) -> str:
    """Generate SPEC.md content."""
    full_name = f"{parent}/{name}" if parent else name
    return f'''# Technical Specification - {name.replace("_", " ").title()}

**Module**: `codomyrmex.{full_name.replace("/", ".")}`  
**Version**: v0.1.0  
**Last Updated**: {datetime.now().strftime("%Y-%m-%d")}

## 1. Purpose

{description}

## 2. Architecture

### 2.1 Components

```
{name}/
├── __init__.py          # Module exports
├── README.md            # Documentation
├── AGENTS.md            # Agent guidelines
├── SPEC.md              # This file
├── PAI.md               # Personal AI context
└── core.py              # Core implementation
```

### 2.2 Dependencies

- Python 3.10+
- Parent module: `{parent or "codomyrmex"}`

## 3. Interfaces

### 3.1 Public API

```python
# Primary exports — fill in after implementing src/codomyrmex/{full_name}/core.py:
# from .core import MainClass
```

### 3.2 Configuration

Environment variables:
- `CODOMYRMEX_*`: Configuration options

## 4. Implementation Notes

### 4.1 Design Decisions

1. **Decision 1**: Rationale

### 4.2 Limitations

- Known limitation 1
- Known limitation 2

## 5. Testing

```bash
# Run tests for this module
pytest tests/{full_name.replace("/", "_")}/
```

## 6. Future Considerations

- Enhancement 1
- Enhancement 2
'''


def generate_pai(name: str, description: str, parent: str = None) -> str:
    """Generate PAI.md content."""
    full_name = f"{parent}/{name}" if parent else name
    return f'''# Personal AI Infrastructure - {name.replace("_", " ").title()}

**Module**: `codomyrmex.{full_name.replace("/", ".")}`  
**Version**: v0.1.0  
**Status**: Active

## Context

{description}

## AI Strategy

As an AI agent working with this {"submodule" if parent else "module"}:

### Core Principles

1. **Graceful Degradation**: Handle missing dependencies gracefully
2. **Configuration Awareness**: Check environment and config before operations
3. **Consistent Patterns**: Follow established module patterns

### Usage Pattern

```python
from codomyrmex.{full_name.replace("/", ".")} import <component>

# Pattern for safe usage
try:
    result = component.operation()
except Exception as e:
    logger.warning(f"Operation failed: {{e}}")
    # Fallback behavior
```

## Key Files

| File | Purpose |
|------|---------|
| `__init__.py` | Module initialization |
| `core.py` | Core implementation |

## Future Considerations

1. **Enhancement Area 1**: Description
2. **Enhancement Area 2**: Description
'''


def generate_init(name: str, description: str, parent: str = None) -> str:
    """Generate __init__.py content."""
    full_name = f"{parent}.{name}" if parent else name
    return f'''"""
{name.replace("_", " ").title()} {"Submodule" if parent else "Module"}

{description}
"""

__version__ = "0.1.0"
__all__ = []

# Lazy imports for performance
# from .core import *
'''


def create_module_structure(
    base_path: Path, 
    name: str, 
    description: str, 
    parent: str = None,
    dry_run: bool = False
) -> list:
    """Create the full module/submodule structure."""
    created_files = []
    module_path = base_path / name
    
    if not dry_run:
        module_path.mkdir(parents=True, exist_ok=True)
    
    files = {
        "README.md": generate_readme(name, description, parent),
        "AGENTS.md": generate_agents(name, description, parent),
        "SPEC.md": generate_spec(name, description, parent),
        "PAI.md": generate_pai(name, description, parent),
        "__init__.py": generate_init(name, description, parent),
    }
    
    for filename, content in files.items():
        file_path = module_path / filename
        if not dry_run:
            if not file_path.exists():
                file_path.write_text(content)
                created_files.append(str(file_path))
        else:
            created_files.append(f"[DRY RUN] Would create: {file_path}")
    
    return created_files


def create_script_structure(
    scripts_base: Path,
    name: str, 
    description: str,
    parent: str = None,
    dry_run: bool = False
) -> list:
    """Create corresponding script directory."""
    created_files = []
    
    if parent:
        script_path = scripts_base / parent / name
    else:
        script_path = scripts_base / name
    
    if not dry_run:
        script_path.mkdir(parents=True, exist_ok=True)
    
    # Construct components
    title = name.replace("_", " ").title()
    submod_type = "submodule" if parent else "module"
    parent_levels = "/.." if parent else ""
    
    demo_script = f'''#!/usr/bin/env python3
"""
{title} Demo Script

Demonstrates functionality of the {name} {submod_type}.
"""

import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.parent{parent_levels}
sys.path.insert(0, str(PROJECT_ROOT / "src"))

def main():
    """Main demonstration."""
    raise NotImplementedError(
        "Demo for '{name}' is not yet implemented. "
        "Implement src/codomyrmex/{name}/ first, "
        "then replace this with real demonstrations."
    )

if __name__ == "__main__":
    sys.exit(main())
'''

    demo_path = script_path / f"{name}_demo.py"
    if not dry_run:
        if not demo_path.exists():
            demo_path.write_text(demo_script)
            created_files.append(str(demo_path))
    else:
        created_files.append(f"[DRY RUN] Would create: {demo_path}")
    
    return created_files


def main() -> int:
    """Main execution."""
    setup_logging()
    dry_run = "--dry-run" in sys.argv
    
    src_base = PROJECT_ROOT / "src" / "codomyrmex"
    scripts_base = PROJECT_ROOT / "scripts"
    
    all_created = []
    
    print("=" * 60)
    print_info("CODOMYRMEX MODULE SCAFFOLDING")
    print("=" * 60)
    if dry_run:
        print_info("DRY RUN MODE - No files will be created")
    
    # Phase 1: Create submodules
    print_info("Phase 1: Creating Submodules")
    for parent, submodules in SUBMODULES.items():
        parent_path = src_base / parent
        if not parent_path.exists():
            print_warning(f"Parent module not found: {parent}")
            continue
            
        print(f"\n  {parent}/")
        for name, description in submodules:
            files = create_module_structure(parent_path, name, description, parent, dry_run)
            all_created.extend(files)
            script_files = create_script_structure(scripts_base, name, description, parent, dry_run)
            all_created.extend(script_files)
            print_success(f"  {name}")
    
    # Phase 2: Create new modules
    print_info("Phase 2: Creating New Modules")
    for name, description in NEW_MODULES:
        files = create_module_structure(src_base, name, description, None, dry_run)
        all_created.extend(files)
        script_files = create_script_structure(scripts_base, name, description, None, dry_run)
        all_created.extend(script_files)
        print_success(f"  {name}")
    
    # Summary
    print("\n" + "=" * 60)
    print_info(f"{'Would create' if dry_run else 'Created'} {len(all_created)} files")
    print("=" * 60)
    
    if dry_run:
        print_info("Run without --dry-run to create files")
    else:
        print_success("All modules scaffolded successfully")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
