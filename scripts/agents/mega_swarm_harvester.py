#!/usr/bin/env python3
"""
Jules Mega Swarm Harvester.

This script lists all Jules sessions, finds those that are 'Completed',
and automatically applies their changes to the local repository.
"""

import subprocess

def get_completed_sessions() -> list[str]:
    """Parse 'jules remote list --session' to find Completed session IDs."""
    try:
        result = subprocess.run(
            ["jules", "remote", "list", "--session"],
            capture_output=True,
            text=True,
            check=True
        )
    except subprocess.CalledProcessError as e:
        print(f"Error running jules list: {e}")
        return []

    lines = result.stdout.splitlines()
    if not lines:
        return []

    completed_ids = []
    
    # Skip header
    for line in lines[1:]:
        line = line.strip()
        if not line:
            continue
            
        parts = line.split()
        if not parts:
            continue
            
        session_id = parts[0]
        
        # Check if the line ends with "Completed"
        if line.endswith("Completed"):
            completed_ids.append(session_id)
            
    return completed_ids

def apply_session(session_id: str) -> bool:
    """Run jules remote pull --session <ID> --apply."""
    print(f"Applying session {session_id}...")
    try:
        # Run the pull and apply command
        subprocess.run(
            ["jules", "remote", "pull", "--session", session_id, "--apply"],
            check=True
        )
        return True
    except subprocess.CalledProcessError as e:
        print(f"Failed to apply session {session_id}: {e}")
        return False

def harvest():
    completed_ids = get_completed_sessions()
    print(f"Found {len(completed_ids)} completed sessions.")
    
    success_count = 0
    for sid in completed_ids:
        if apply_session(sid):
            success_count += 1
            
    print(f"\nSuccessfully applied {success_count} out of {len(completed_ids)} completed sessions.")


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
    harvest()
