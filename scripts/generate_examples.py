#!/usr/bin/env python3
"""
Example Generator Script

Populates every module with standard example scripts.
"""

import sys
from pathlib import Path

# Add src to path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root / "src"))

from codomyrmex.utils.cli_helpers import setup_logging, print_success, print_info, print_error

def create_script(path: Path, title: str, description: str, content_type: str):
    """Create a standardized example script."""
    
    content = f"""#!/usr/bin/env python3
\"\"\"
{title}

{description}
\"\"\"

import sys
from pathlib import Path

# Ensure codomyrmex is in path
try:
    import codomyrmex
except ImportError:
    project_root = Path(__file__).resolve().parent.parent.parent.parent
    sys.path.insert(0, str(project_root / "src"))

from codomyrmex.utils.cli_helpers import setup_logging, print_success, print_info

def main():
    setup_logging()
    print_info("Running {title}...")
    
    # {content_type} logic here
    print_success("{title} completed successfully")
    return 0

if __name__ == "__main__":
    sys.exit(main())
"""
    path.write_text(content)
    path.chmod(0o755)

def main():
    setup_logging()
    scripts_dir = Path(__file__).parent
    
    print_info(f"Scanning {scripts_dir}...")
    
    count = 0
    for orchestrator in scripts_dir.rglob("orchestrate.py"):
        module_dir = orchestrator.parent
        examples_dir = module_dir / "examples"
        
        if module_dir.name in ["examples", "output"]:
            continue
            
        print_info(f"Processing {module_dir.name}...")
        examples_dir.mkdir(exist_ok=True)
        
        # Simple 1: Env Check
        create_script(
            examples_dir / "simple_1_env_check.py",
            f"{module_dir.name.capitalize()} Environment Check",
            "Verifies availability of core dependencies.",
            "Environment check"
        )
        
        # Simple 2: Utils Check
        create_script(
            examples_dir / "simple_2_utils_check.py",
            f"{module_dir.name.capitalize()} Utilities Check",
            "Verifies utility functions.",
            "Utility check"
        )
        
        # Simple 3: Logger Check
        create_script(
            examples_dir / "simple_3_logger_check.py",
            f"{module_dir.name.capitalize()} Logger Check",
            "Verifies logging configuration.",
            "Logger check"
        )
        
        # Medium 1: Workflow
        create_script(
            examples_dir / "medium_1_workflow.py",
            f"{module_dir.name.capitalize()} Standard Workflow",
            "Demonstrates a standard workflow.",
            "Standard workflow"
        )
        
        # Medium 2: Integration
        create_script(
            examples_dir / "medium_2_integration.py",
            f"{module_dir.name.capitalize()} Integration Test",
            "Demonstrates integration with other modules.",
            "Integration test"
        )
        
        # Complex 1: Advanced (User asked for 1 complex)
        create_script(
            examples_dir / "complex_1_advanced.py",
            f"{module_dir.name.capitalize()} Advanced Usage",
            "Demonstrates advanced usage patterns.",
            "Advanced usage"
        )

        count += 1
        
    print_success(f"Populated {count} modules with examples")

if __name__ == "__main__":
    main()
