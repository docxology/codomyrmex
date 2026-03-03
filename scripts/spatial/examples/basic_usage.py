#!/usr/bin/env python3
"""
Spatial Modeling - Real Usage Examples

Demonstrates actual spatial capabilities:
- WorldModel initialization
- 3D Engine objects (Vector3D, Object3D, Scene3D)
- PhysicsEngine simulation
- 4D Synergetics (QuadrayCoordinate)
"""

import sys
from pathlib import Path

# Ensure codomyrmex is in path
try:
    import codomyrmex  # noqa: F401
except ImportError:
    project_root = Path(__file__).resolve().parent.parent.parent.parent
    sys.path.insert(0, str(project_root / "src"))

from codomyrmex.spatial.four_d import QuadrayCoordinate
from codomyrmex.spatial.three_d.engine_3d import (
    Object3D,
    PhysicsEngine,
    Scene3D,
    Vector3D,
)
from codomyrmex.spatial.world_models import WorldModel
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
        / "spatial"
        / "config.yaml"
    )
    config_data = {}
    if config_path.exists():
        with open(config_path) as f:
            config_data = yaml.safe_load(f) or {}
            print("Loaded config from config/spatial/config.yaml")

    setup_logging()
    print_info("Running Spatial Examples...")

    # 1. World Model
    print_info("Testing WorldModel...")
    try:
        model = WorldModel(environment_type="test_lab")
        if model.environment_type == "test_lab":
            print_success(f"  WorldModel for '{model.environment_type}' initialized.")
    except Exception as e:
        print_error(f"  WorldModel failed: {e}")

    # 2. 3D Engine
    print_info("Testing 3D Engine components...")
    try:
        pos = Vector3D(1.0, 2.0, 3.0)
        obj = Object3D(name="TestObject", position=pos)
        scene = Scene3D(objects=[obj])
        print_success(f"  Scene3D created with object '{obj.name}' at {pos}")

        # Physics
        physics = PhysicsEngine()
        # Initialize gravity to a known value for testing
        physics.gravity = Vector3D(0.0, -9.81, 0.0)

        initial_y = obj.position.y
        physics.update_physics(scene.objects, delta_time=0.1)

        if obj.position.y != initial_y:
            print_success(f"  Physics updated. New y-position: {obj.position.y:.4f}")
    except Exception as e:
        print_error(f"  3D Engine testing failed: {e}")

    # 3. 4D Synergetics
    print_info("Testing 4D Synergetics...")
    try:
        qc = QuadrayCoordinate(1, 0, 0, 0)
        print_success(f"  QuadrayCoordinate created: {qc.coords}")
    except Exception as e:
        print_error(f"  4D Synergetics failed: {e}")

    print_success("Spatial modeling examples completed successfully")
    return 0


if __name__ == "__main__":
    sys.exit(main())
