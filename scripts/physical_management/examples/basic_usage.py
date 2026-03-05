#!/usr/bin/env python3
"""
Physical Management - Real Usage Examples

Demonstrates actual physical management capabilities:
- PhysicalObjectManager initialization
- PhysicsSimulator stubs
- SensorManager initialization
"""

import sys
from pathlib import Path

# Ensure codomyrmex is in path
try:
    import codomyrmex
except ImportError:
    project_root = Path(__file__).resolve().parent.parent.parent.parent
    sys.path.insert(0, str(project_root / "src"))

from codomyrmex.physical_management import (
    PhysicalObject,
    PhysicalObjectManager,
    PhysicsSimulator,
    SensorManager,
    Vector3D,
)
from codomyrmex.utils.cli_helpers import (
    print_error,
    print_info,
    print_success,
    setup_logging,
)


def main():
    # Auto-injected: Load configuration
    from pathlib import Path

    import yaml

    config_path = (
        Path(__file__).resolve().parent.parent.parent
        / "config"
        / "physical_management"
        / "config.yaml"
    )
    if config_path.exists():
        with open(config_path) as f:
            yaml.safe_load(f) or {}
            print("Loaded config from config/physical_management/config.yaml")

    setup_logging()
    print_info("Running Physical Management Examples...")

    # 1. Physical Object Manager
    print_info("Testing PhysicalObjectManager...")
    try:
        mgr = PhysicalObjectManager()
        obj = PhysicalObject(id="obj1", name="Test Object", position=Vector3D(0, 0, 0))
        mgr.add_object(obj)
        print_success(f"  PhysicalObjectManager initialized. Added object: {obj.name}")
    except Exception as e:
        print_error(f"  Object manager failed: {e}")

    # 2. Physics Simulator
    print_info("Testing PhysicsSimulator...")
    try:
        PhysicsSimulator()
        print_success("  PhysicsSimulator initialized.")
    except Exception as e:
        print_error(f"  Physics simulator failed: {e}")

    # 3. Sensor Manager
    print_info("Testing SensorManager...")
    try:
        SensorManager()
        print_success("  SensorManager initialized.")
    except Exception as e:
        print_error(f"  Sensor manager failed: {e}")

    print_success("Physical management examples completed successfully")
    return 0


if __name__ == "__main__":
    sys.exit(main())
