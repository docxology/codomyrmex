#!/usr/bin/env python3
"""
Jules Mega Swarm Dispatcher.

This script identifies all valid modules across `scripts/` and `src/codomyrmex/`
and dispatches one Jules coding agent per module to create/improve thin orchestrators,
comprehensive zero-mock tests, and documentation (AGENTS.md, README.md, SPEC.md).

It executes agents in parallel batches to respect rate limits.
"""

import os
import subprocess
import time
from pathlib import Path

# Repository root relative to this script
REPO_ROOT = Path(__file__).resolve().parent.parent.parent
SCRIPTS_DIR = REPO_ROOT / "scripts"
SRC_DIR = REPO_ROOT / "src" / "codomyrmex"
REPO_NAME = "docxology/codomyrmex"

# Skip directories that aren't source modules
EXCLUDES = {
    "__pycache__", ".claude", ".pipelines", ".workflows", 
    "build", "dist", "docs", "tests", "examples"
}

BATCH_SIZE = 5      # Number of agents to dispatch concurrently before waiting
BATCH_DELAY = 10.0  # Seconds to wait between batches

def get_valid_modules() -> list[str]:
    """Find all valid top-level directories common to scripts/ or src/codomyrmex/."""
    modules = set()
    
    # Check src/codomyrmex/
    if SRC_DIR.exists():
        for item in SRC_DIR.iterdir():
            if item.is_dir() and item.name not in EXCLUDES:
                modules.add(item.name)
                
    # Check scripts/
    if SCRIPTS_DIR.exists():
        for item in SCRIPTS_DIR.iterdir():
            if item.is_dir() and item.name not in EXCLUDES:
                modules.add(item.name)
                
    return sorted(list(modules))

def dispatch_jules(module_name: str) -> None:
    """Launch a Jules agent for the given module."""
    prompt = (
        f"For the '{module_name}' module: Write a thin orchestrator script in `scripts/{module_name}/` "
        f"(or improve the existing one). Then go to `src/codomyrmex/{module_name}/` and comprehensively "
        "add/improve all methods, strictly zero-mock tests, and documentation (AGENTS.md, README.md, SPEC.md). "
        "Ensure the orchestrator is a working, tested example of the improved module."
    )
    
    print(f"\n🚀 Dispatching agent for: {module_name}")
    try:
        # Launch non-blocking (in background)
        subprocess.Popen(
            ["jules", "new", "--repo", REPO_NAME, prompt],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
    except FileNotFoundError:
        print("Error: 'jules' CLI not found. Is it installed?")
        exit(1)

def run_swarm(max_agents: int = None) -> None:
    """Run the mega swarm in batches."""
    modules = get_valid_modules()
    if not modules:
        print("No valid modules found to dispatch.")
        return
        
    print(f"Found {len(modules)} modules for the swarm: {', '.join(modules[:5])}...")
    
    if max_agents:
        modules = modules[:max_agents]
        print(f"Limiting to first {max_agents} agents for testing.")
        
    print(f"Dispatching {len(modules)} Jules agents in batches of {BATCH_SIZE}...")
    
    for i in range(0, len(modules), BATCH_SIZE):
        batch = modules[i:i + BATCH_SIZE]
        print(f"\n--- Batch {i//BATCH_SIZE + 1} ({len(batch)} agents) ---")
        
        for module in batch:
            dispatch_jules(module)
            
        if i + BATCH_SIZE < len(modules):
            print(f"Waiting {BATCH_DELAY}s before next batch...")
            time.sleep(BATCH_DELAY)
            
    print("\n✅ Mega Swarm Initialized.")
    print("Use 'jules remote list --session' to monitor your agents.")
    print("Use 'jules remote pull --session <ID> --apply' to merge completed work.")


    # Auto-injected: Load configuration
    import yaml
    from pathlib import Path
    config_path = Path(__file__).resolve().parent.parent.parent / "config" / "agents" / "config.yaml"
    config_data = {}
    if config_path.exists():
        with open(config_path, "r") as f:
            config_data = yaml.safe_load(f) or {}
            print(f"Loaded config from config/agents/config.yaml")

if __name__ == "__main__":
    import sys
    # Optional arg to limit agents (e.g. ./mega_swarm_dispatcher.py 5)
    limit = int(sys.argv[1]) if len(sys.argv) > 1 else None
    run_swarm(limit)
