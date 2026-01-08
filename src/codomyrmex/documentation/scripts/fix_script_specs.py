from pathlib import Path
import os


from codomyrmex.logging_monitoring import get_logger






























































"""Core functionality module

"""Core functionality module

This module provides fix_script_specs functionality including:
- 1 functions: fix_script_specs
- 0 classes: 

Usage:
    # Example usage here
"""
logger = get_logger(__name__)
This module provides fix_script_specs functionality including:
- 1 functions: fix_script_specs
- 0 classes: 

Usage:
    # Example usage here
"""
WRAPPER_TEMPLATE = """# scripts/{module_name} - Functional Specification

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: January 2026

## Purpose

This module contains the **automation scripts** and **CLI entry points** for the `{module_name}` system. Its primary function is to expose the core library functionality (located in `src/codomyrmex/{module_name}`) to the terminal and CI/CD pipelines.

## Design Principles

### Modularity
- **Thin Wrapper**: Scripts should contain minimal business logic, delegating immediately to `src` modules.
- **CLI Standard**: Uses `argparse` or `click` (via `kit`) for consistent flag handling.

### Internal Coherence
- **Reflection**: The directory structure mirrors `src/codomyrmex` to make finding the "executable version" of a library intuitive.

## Functional Requirements

### Core Capabilities
1.  **Orchestration**: CLI signals triggering library logic.
2.  **Output formatting**: JSON/Text output modes for machine/human consumption.

## Interface Contracts

### Public API
- Check `AGENTS.md` or run with `--help` for specific command usage.

### Dependencies
- **Core Library**: `codomyrmex.{module_name}`.

## Navigation

- **Human Documentation**: [README.md](README.md)
- **Technical Documentation**: [AGENTS.md](AGENTS.md)
- **Library Spec**: [../../src/codomyrmex/{module_name}/SPEC.md](../../src/codomyrmex/{module_name}/SPEC.md)
"""

def fix_script_specs(root_dir):
    """Brief description of fix_script_specs.

Args:
    root_dir : Description of root_dir

    Returns: Description of return value
"""
    root = Path(root_dir)
    count = 0
    
    for path in root.iterdir():
        if path.is_dir() and not path.name.startswith(('.', '__')):
            spec_path = path / "SPEC.md"
            module_name = path.name
            
            # Check if it needs fixing (small size or placeholder text)
            should_fix = False
            if not spec_path.exists():
                print(f"Missing SPEC.md in {module_name}")
                should_fix = True
            else:
                content = spec_path.read_text(encoding='utf-8')
                if "Functional requirements for" in content and len(content) < 2000:
                    should_fix = True
                elif len(content) < 500: # Very small files
                    should_fix = True
            
            if should_fix:
                print(f"Fixing {module_name} SPEC.md...")
                new_content = WRAPPER_TEMPLATE.format(module_name=module_name)
                spec_path.write_text(new_content, encoding='utf-8')
                count += 1
    
    print(f"Fixed {count} files.")

if __name__ == "__main__":
    fix_script_specs("scripts")
