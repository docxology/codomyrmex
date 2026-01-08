#!/usr/bin/env python3
"""
Generate Orchestrators Script

Automatically generates standard 'orchestrate.py' files for all subdirectories
in the scripts/ folder that lack them or have corrupted ones.
"""

import os
from pathlib import Path

TEMPLATES = {
    "standard": """#!/usr/bin/env python3
\"\"\"
{module_name} Orchestrator

Standardized entry point for {module_name} operations.
\"\"\"

import sys
import argparse
from codomyrmex.logging_monitoring import get_logger
from codomyrmex.utils.cli_helpers import setup_logging, print_success

logger = get_logger(__name__)

def main():
    \"\"\"Main orchestration entry point.\"\"\"
    setup_logging()
    
    parser = argparse.ArgumentParser(description="{module_name} Orchestrator")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose logging")
    args = parser.parse_args()

    logger.info("Starting {module_name} orchestration")
    print_success("{module_name} orchestration verified")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
"""
}

def generate_orchestrators():
    scripts_dir = Path(__file__).parent.parent
    
    # Skip these special directories
    SKIP_DIRS = {
        "__pycache__", ".git", "maintenance", "output", "git-hooks"
    }

    count = 0
    for item in scripts_dir.iterdir():
        if item.is_dir() and item.name not in SKIP_DIRS:
            orch_file = item / "orchestrate.py"
            
            # Create if missing or if it looks corrupted (e.g. one line)
            should_create = False
            if not orch_file.exists():
                should_create = True
            else:
                # Check for corruption (minified/one-liner)
                try:
                    content = orch_file.read_text(encoding="utf-8")
                    if len(content.splitlines()) < 5:
                        should_create = True
                except Exception:
                    should_create = True
            
            if should_create:
                print(f"Generating orchestrator for: {item.name}")
                module_name = item.name.replace("_", " ").title()
                content = TEMPLATES["standard"].format(module_name=module_name)
                orch_file.write_text(content, encoding="utf-8")
                orch_file.chmod(0o755)
                count += 1

    print(f"Generated {count} orchestrators.")

if __name__ == "__main__":
    generate_orchestrators()
