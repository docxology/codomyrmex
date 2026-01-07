# three_d

## Signposting
- **Parent**: [spatial](../README.md)
- **Children**:
    - [docs](docs/README.md)
    - [examples](scripts/examples/README.md)
    - [tests](tests/README.md)
- **Key Artifacts**:
    - [Agent Guide](AGENTS.md)
    - [Functional Spec](SPEC.md)

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: January 2026

## Overview

3D modeling, rendering, and AR/VR/XR capabilities for spatial computing. Provides scene creation and manipulation, mesh generation, camera and lighting control, image rendering, AR tracking and world understanding, stereo rendering for VR, and unified interface for AR/VR/XR experiences.

## Directory Contents
- `API_SPECIFICATION.md` – File
- `README.md` – File
- `SECURITY.md` – File
- `SPEC.md` – File
- `__init__.py` – File
- `ar_vr_support.py` – File
- `docs/` – Subdirectory
- `engine_3d.py` – File
- `examples/` – Subdirectory
- `rendering_pipeline.py` – File
- `requirements.txt` – File
- `tests/` – Subdirectory

## Navigation
- **Technical Documentation**: [AGENTS.md](AGENTS.md)
- **Functional Specification**: [SPEC.md](SPEC.md)
- **Parent Directory**: [spatial](../README.md)
- **Project Root**: [README](../../../../README.md)

## Getting Started

To use this module in your project, import the necessary components:

```python
from codomyrmex.spatial.three_d import (
    Scene3D,
    Object3D,
    Camera3D,
    ARSession,
    VRRenderer,
)

# Create a 3D scene
scene = Scene3D()
cube = Object3D(position=(0, 0, 0), mesh="cube", scale=(1, 1, 1))
scene.add_object(cube)

# Set up camera
camera = Camera3D(position=(5, 5, 5), target=(0, 0, 0), fov=60)
image = scene.render(camera)

# AR support
ar_session = ARSession()
ar_session.initialize()
tracking = ar_session.track_pose()

# VR rendering
vr_renderer = VRRenderer()
vr_renderer.render_scene(scene, stereo=True)
```

