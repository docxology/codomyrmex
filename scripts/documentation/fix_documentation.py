#!/usr/bin/env python3
"""Documentation Fix Script.

Automatically generates missing documentation files (PAI.md, SPEC.md, AGENTS.md)
and upgrades stub READMEs to meet repository standards.
"""

from pathlib import Path
from typing import Dict, Any, List
import textwrap
import os
import sys

# Ensure codomyrmex is in path
_project_root = Path(__file__).resolve().parents[2]
if str(_project_root / "src") not in sys.path:
    sys.path.insert(0, str(_project_root / "src"))

from codomyrmex.utils import ScriptBase

class DocumentationFixer(ScriptBase):
    def __init__(self):
        super().__init__(
            name="doc_fix",
            description="Fixes missing or stub documentation",
            version="1.0.0"
        )
        self.stub_threshold = 500

    def add_arguments(self, parser):
        parser.add_argument(
            "--target", type=Path, default=Path.cwd() / "src/codomyrmex",
            help="Target directory to fix"
        )
        parser.add_argument(
            "--dry-run-fix", action="store_true",
            help="Don't write files, just log intention"
        )

    def generate_pai(self, module_name: str) -> str:
        name_title = module_name.replace("_", " ").title()
        return textwrap.dedent(f"""\
            # Personal AI Infrastructure - {name_title} Context
            
            **Module**: {module_name}
            **Status**: Active
            
            ## Context
            This module provides {name_title} capabilities to the Codomyrmex ecosystem.
            
            ## AI Strategy
            As an AI agent, when working with this module:
            1.  **Respect Interfaces**: Use the public API defined in `__init__.py`.
            2.  **Maintain State**: Ensure any stateful operations are documented in `SPEC.md`.
            3.  **Error Handling**: Wrap external calls in try/except blocks and log using `logging_monitoring`.
            
            ## Key Files
            - `__init__.py`: Public API export.
            - `SPEC.md`: Technical specification.
            
            ## Future Considerations
            - Modularization: Keep dependencies minimal.
            - Telemetry: Ensure operations emit performace metrics.
            """)

    def generate_spec(self, module_name: str) -> str:
        name_title = module_name.replace("_", " ").title()
        return textwrap.dedent(f"""\
            # {name_title} Specification
            
            ## 1. Functional Requirements
            The `{module_name}` module must:
            - Provide robust implementations of {name_title} logic.
            - Handle errors gracefully without crashing the host process.
            - Expose a clean, type-hinted API.
            
            ## 2. API Surface
            See `API_SPECIFICATION.md` (if available) or `__init__.py` for exact signatures.
            
            ## 3. Dependencies
            - **Internal**: `codomyrmex.logging_monitoring`, `codomyrmex.utils`.
            - **External**: Standard library.
            
            ## 4. Constraints
            - **Performance**: Operations should be non-blocking where possible.
            - **Security**: Validate all inputs; sanity check paths.
            """)

    def generate_agents(self, module_name: str) -> str:
        name_title = module_name.replace("_", " ").title()
        return textwrap.dedent(f"""\
            # Codomyrmex Agents - {name_title}
            
            **Scope**: `{module_name}` directory.
            
            ## Operating Rules
            1.  **Modularity**: Do not import from sibling modules unless necessary.
            2.  **Testing**: Create unit tests in `src/codomyrmex/tests/unit/{module_name}/`.
            3.  **Documentation**: Keep `README.md` updated with new features.
            
            ## Task Queue
            - [ ] Review implementation for edge cases.
            - [ ] Add type hints to all public methods.
            """)

    def generate_readme(self, module_name: str) -> str:
        name_title = module_name.replace("_", " ").title()
        return textwrap.dedent(f"""\
            # {name_title}
            
            **Version**: v0.1.0 | **Status**: Active
            
            ## Overview
            The `{module_name}` module provides core functionality for {name_title}.
            
            ## Architecture
            
            ```mermaid
            graph TD
                {module_name} --> Utils[codomyrmex.utils]
                {module_name} --> Logs[codomyrmex.logging_monitoring]
                
                subgraph {module_name}
                    Core[Core Logic]
                    API[Public Interface]
                end
            ```
            
            ## Components
            - **Core**: Implementation logic.
            - **API**: Exposed functions and classes.
            
            ## Usage
            
            ```python
            from codomyrmex.{module_name} import ...
            
            # Example usage
            # result = process(...)
            ```
            
            ## Navigation
            - **Parent**: [codomyrmex](../README.md)
            - **Spec**: [SPEC.md](SPEC.md)
            - **Agents**: [AGENTS.md](AGENTS.md)
            """)

    def fix_directory(self, path: Path) -> None:
        if self.config.verbose:
             self.log_debug(f"Visiting {path}")

        if path.name.startswith(".") or path.name == "__pycache__":
            return

        # Check if it looks like a module
        if not (path / "__init__.py").exists():
             # Only fix if it has python files
             if not any(p.suffix == ".py" for p in path.iterdir()):
                 return

        module_name = path.name
        
        # Files to check/generate
        generators = {
            "PAI.md": self.generate_pai,
            "SPEC.md": self.generate_spec,
            "AGENTS.md": self.generate_agents,
            "README.md": self.generate_readme
        }
        
        for filename, generator in generators.items():
            file_path = path / filename
            content = generator(module_name)
            
            should_write = False
            action = ""
            
            if not file_path.exists():
                should_write = True
                action = "Created"
            elif filename == "README.md" and file_path.stat().st_size < self.stub_threshold:
                should_write = True
                action = "Upgraded Stub"
                
            if should_write:
                if self.config and self.config.dry_run: # fix: access via config
                    self.log_info(f"[DRY RUN] Would write {file_path}")
                elif not (self.config and hasattr(self.config, 'custom') and self.config.custom.get('dry_run_fix')):
                     with open(file_path, "w") as f:
                         f.write(content)
                     self.log_success(f"{action} {file_path}")

    def run(self, args, config):
        self.target_dir = args.target.resolve()
        
        # fix: handle arg passing logic vs config
        is_dry = args.dry_run_fix
        if is_dry:
             self.log_info("Running in DRY RUN FIX mode")

        # Walk
        for root, dirs, files in os.walk(self.target_dir):
            path = Path(root)
            self.fix_directory(path)
            
        return {"status": "completed"}

if __name__ == "__main__":
    import sys
    # Ensure src is in path for imports (file-relative for any working directory)
    project_root = Path(__file__).resolve().parent.parent.parent
    sys.path.insert(0, str(project_root / "src"))
    DocumentationFixer().execute()
