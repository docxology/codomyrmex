# world_models

## Signposting
- **Parent**: [spatial](../README.md)
- **Children**:
    - None
- **Key Artifacts**:
    - [Agent Guide](AGENTS.md)
    - [Functional Spec](SPEC.md)

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: January 2026

## Overview

World model and simulation including environment representation, physics simulation, and agent-environment interaction. Provides comprehensive world modeling capabilities for spatial computing.

## Directory Contents
- `__init__.py` – File

## Navigation
- **Technical Documentation**: [AGENTS.md](AGENTS.md)
- **Functional Specification**: [SPEC.md](SPEC.md)
- **Parent Directory**: [spatial](../README.md)
- **Project Root**: [README](../../../../README.md)

## Getting Started

To use this module in your project, import the necessary components:

```python
from codomyrmex.spatial.world_models import WorldModel

# Create a world model
world = WorldModel()

# Add environment
world.add_environment(
    env_id="test_room",
    properties={
        "size": (10, 10, 3),
        "gravity": 9.81,
        "lighting": "ambient"
    }
)

# Add objects to environment
world.add_object(
    env_id="test_room",
    obj_id="box_1",
    position=(0, 0, 0),
    properties={"mass": 1.0, "shape": "cube"}
)

# Simulate physics
world.step_simulation(dt=0.01)
state = world.get_object_state("test_room", "box_1")
print(f"Object position: {state.position}")
```

