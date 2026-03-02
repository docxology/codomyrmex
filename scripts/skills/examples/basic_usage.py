#!/usr/bin/env python3
"""
Skills Management - Real Usage Examples

Demonstrates actual skills capabilities:
- SkillsManager initialization
- Skill loading and registration via custom skills
- Skill discovery and status
"""

import sys
import shutil
from pathlib import Path

# Ensure codomyrmex is in path
try:
    import codomyrmex  # noqa: F401
except ImportError:
    project_root = Path(__file__).resolve().parent.parent.parent.parent
    sys.path.insert(0, str(project_root / "src"))

from codomyrmex.utils.cli_helpers import setup_logging, print_success, print_info, print_error
from codomyrmex.skills import (
    get_skills_manager,
    SkillsManager
)

def main():
    setup_logging()
    print_info("Running Skills Management Examples...")

    # 1. Skills Manager
    print_info("Testing SkillsManager initialization...")
    try:
        # Use a temporary directory for skills to avoid polluting the repo
        temp_skills_dir = Path("output/skills_test")
        if temp_skills_dir.exists():
            shutil.rmtree(temp_skills_dir)
        temp_skills_dir.mkdir(parents=True, exist_ok=True)
        
        mgr = get_skills_manager(
            skills_dir=temp_skills_dir,
            auto_sync=False
        )
        if isinstance(mgr, SkillsManager):
            print_success(f"  SkillsManager initialized at: {mgr.skills_dir}")
            
        # Initialize directories
        mgr.initialize()
        print_success("  SkillsManager directories initialized.")
    except Exception as e:
        print_error(f"  SkillsManager failed: {e}")

    # 2. Add Custom Skill
    print_info("Testing add_custom_skill...")
    try:
        skill_data = {
            "name": "Greeter",
            "description": "Greets the user",
            "version": "1.0.0",
            "patterns": [
                {"name": "hello", "description": "Responds to hello"}
            ]
        }
        if mgr.add_custom_skill(category="general", name="greeter", skill_data=skill_data):
            print_success("  Custom skill 'general/greeter' added successfully.")
            
        # Verify it's in the registry
        skills = mgr.list_skills(category="general")
        if any(s["name"] == "greeter" for s in skills):
            print_success("  Skill found in registry listing.")
            
        # Search
        search_results = mgr.search_skills("greet")
        if search_results:
            print_success(f"  Search for 'greet' found {len(search_results)} result(s).")
            
    except Exception as e:
        print_error(f"  Custom skill operations failed: {e}")

    print_success("Skills management examples completed successfully")
    return 0

if __name__ == "__main__":
    sys.exit(main())
