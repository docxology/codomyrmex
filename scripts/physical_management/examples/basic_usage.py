#!/usr/bin/env python3
"""
Physical Management - Real Usage Examples

Demonstrates actual physical management capabilities:
- PhysicalObjectManager initialization
- PhysicsSimulator stubs
- SensorManager initialization
"""

import sys
import os
from pathlib import Path

# Ensure codomyrmex is in path
try:
    import codomyrmex
except ImportError:
    project_root = Path(__file__).resolve().parent.parent.parent.parent
    sys.path.insert(0, str(project_root / "src"))

from codomyrmex.utils.cli_helpers import setup_logging, print_success, print_info, print_error
from codomyrmex.physical_management import (
    PhysicalObjectManager,
    PhysicsSimulator,
    SensorManager,
    PhysicalObject,
    Vector3D
)

def main():
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
        sim = PhysicsSimulator()
        print_success("  PhysicsSimulator initialized.")
    except Exception as e:
        print_error(f"  Physics simulator failed: {e}")

    # 3. Sensor Manager
    print_info("Testing SensorManager...")
    try:
        sensor_mgr = SensorManager()
        print_success("  SensorManager initialized.")
    except Exception as e:
        print_error(f"  Sensor manager failed: {e}")

    print_success("Physical management examples completed successfully")
    return 0

if __name__ == "__main__":
    sys.exit(main())
