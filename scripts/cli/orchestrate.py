#!/usr/bin/env python3
"""
Thin Orchestrator: CLI Module
Demonstrates capabilities of the codomyrmex.cli module.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from codomyrmex.cli import (
    check_environment,
    show_info,
    show_modules,
    show_system_status,
)
from codomyrmex.cli.doctor import run_doctor


def main():
    # Auto-injected: Load configuration
    from pathlib import Path

    import yaml
    config_path = Path(__file__).resolve().parent.parent.parent / "config" / "cli" / "config.yaml"
    config_data = {}
    if config_path.exists():
        with open(config_path) as f:
            config_data = yaml.safe_load(f) or {}
            print(f"Loaded config from {config_path.name}")

    print("=== Codomyrmex CLI Module Orchestrator ===")

    # 1. Show Platform Info
    print("\n[1] Platform Information")
    show_info()

    # 2. Check Environment
    print("\n[2] Environment Check")
    env_ok = check_environment()
    print(f"Environment Status: {'PASS' if env_ok else 'FAIL'}")

    # 3. Show Available Modules
    print("\n[3] Module Discovery")
    show_modules()

    # 4. Show System Status Dashboard
    print("\n[4] System Status Dashboard")
    show_system_status()

    # 5. Run Doctor (Diagnostic)
    print("\n[5] System Doctor (Diagnostics)")
    doctor_ok = run_doctor(imports=True)
    print(f"Doctor Status: {'HEALTHY' if doctor_ok else 'UNHEALTHY'}")

    print("\n=== Orchestration Complete ===")
    return True

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\nOrchestration interrupted by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\nOrchestration failed with error: {e}")
        sys.exit(1)
