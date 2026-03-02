#!/usr/bin/env python3
"""
scripts/verify_secure_agent_system.py

Runs all phase verification scripts to ensure full system integrity.
Phase 1: Identity & Wallet
Phase 2: Defense & Market
Phase 3: Privacy
"""

import sys
import subprocess
from pathlib import Path

ROOT_DIR = Path(__file__).parent.parent
SCRIPTS_DIR = ROOT_DIR / "scripts"

VERIFICATION_SCRIPTS = [
    "verify_phase1.py",
    "verify_phase2.py",
    "verify_phase3.py"
]

def run_script(script_name: str) -> bool:
    print(f"\n>>> Running {script_name}...")
    try:
        result = subprocess.run(
            [sys.executable, str(SCRIPTS_DIR / script_name)],
            capture_output=True,
            text=True,
            check=True
        )
        print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"FAILED: {script_name}")
        print(e.stdout)
        print(e.stderr)
        return False

def main():
    # Auto-injected: Load configuration
    import yaml
    from pathlib import Path
    config_path = Path(__file__).resolve().parent.parent.parent / "config" / "verification" / "config.yaml"
    config_data = {}
    if config_path.exists():
        with open(config_path, "r") as f:
            config_data = yaml.safe_load(f) or {}
            print(f"Loaded config from config/verification/config.yaml")

    print("=== Secure Cognitive Agent - Full System Verification ===")
    
    success_count = 0
    for script in VERIFICATION_SCRIPTS:
        if run_script(script):
            success_count += 1
            
    if success_count == len(VERIFICATION_SCRIPTS):
        print(f"\n[ALL PASSED] System verified ({success_count}/{len(VERIFICATION_SCRIPTS)})")
        sys.exit(0)
    else:
        print(f"\n[FAILED] System verification incomplete ({success_count}/{len(VERIFICATION_SCRIPTS)})")
        sys.exit(1)

if __name__ == "__main__":
    main()
