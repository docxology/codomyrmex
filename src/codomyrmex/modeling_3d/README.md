# 3D Modeling and Rendering Module

A comprehensive 3D modeling, rendering, and AR/VR/XR module for the Codomyrmex platform.

## Features

- **Core 3D Engine**: Scene management, objects, cameras, and lighting
- **AR/VR/XR Support**: Augmented, Virtual, and Extended Reality capabilities
- **Rendering Pipeline**: Advanced rendering with shaders and post-processing
- **Physics Integration**: Basic physics simulation for realistic interactions
- **Animation System**: Keyframe and procedural animation support
- **Asset Loading**: Support for common 3D file formats

## Installation

```bash
pip install -r requirements.txt
```

## Quick Start

```python
from codomyrmex.modeling_3d import Scene3D, Object3D, Camera3D

# Create a scene
scene = Scene3D()

# Add objects
cube = Object3D("Cube")
scene.add_object(cube)

# Setup camera
camera = Camera3D("MainCamera")
scene.add_camera(camera)

# Render
from codomyrmex.modeling_3d import RenderPipeline
pipeline = RenderPipeline()
pipeline.render_scene(scene, camera)
```

## AR/VR Usage

```python
from codomyrmex.modeling_3d import ARSession, VRRenderer

# Augmented Reality
ar_session = ARSession()
ar_session.start_session()

# Virtual Reality
vr_renderer = VRRenderer()
vr_renderer.render_stereo(scene)
```

## Documentation

- [API Specification](API_SPECIFICATION.md)
- [Architecture Guide](docs/architecture.md)
- [Usage Examples](examples/)
- [Test Suite](tests/)

## Requirements

See [requirements.txt](requirements.txt) for dependencies.
