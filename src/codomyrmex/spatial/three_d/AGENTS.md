# Codomyrmex Agents — src/codomyrmex/spatial/three_d

## Signposting
- **Parent**: [spatial](../AGENTS.md)
- **Self**: [Agents](AGENTS.md)
- **Children**:
    - [docs](docs/AGENTS.md)
    - [examples](scripts/examples/AGENTS.md)
    - [tests](tests/AGENTS.md)
- **Key Artifacts**:
    - [Functional Spec](SPEC.md)
    - [Human Readme](README.md)

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: January 2026

## Purpose
3D modeling, rendering, and AR/VR/XR capabilities for spatial computing. Provides scene creation and manipulation, mesh generation, camera and lighting control, image rendering, AR tracking and world understanding, stereo rendering for VR, and unified interface for AR/VR/XR experiences.

## Active Components
- `API_SPECIFICATION.md` – Detailed API specification
- `README.md` – Project file
- `SECURITY.md` – Security considerations
- `SPEC.md` – Project file
- `__init__.py` – Module exports and public API
- `ar_vr_support.py` – AR/VR/XR support implementation
- `docs/` – Directory containing docs components
- `engine_3d.py` – Core 3D engine implementation
- `examples/` – Directory containing examples components
- `rendering_pipeline.py` – Rendering pipeline implementation
- `requirements.txt` – Project file
- `tests/` – Directory containing tests components

## Key Classes and Functions

### Scene3D (`engine_3d.py`)
- `Scene3D()` – Container for 3D scenes
- `add_object(obj: Object3D) -> None` – Add 3D object to scene
- `add_camera(camera: Camera3D) -> None` – Add camera to scene
- `add_light(light: Light3D) -> None` – Add light to scene

### Object3D (`engine_3d.py`)
- `Object3D()` – 3D object with geometry and materials
- Properties: `position: Vector3D`, `rotation: Quaternion`, `scale: Vector3D`, `material: Optional[Material3D]`

### Camera3D (`engine_3d.py`)
- `Camera3D()` – Camera for viewing 3D scenes
- Properties: `position: Vector3D`, `target: Vector3D`, `fov: float`, `near_plane: float`, `far_plane: float`

### Vector3D (`engine_3d.py`)
- `Vector3D(x: float, y: float, z: float)` – 3D vector operations
- `__mul__(scalar: float) -> Vector3D` – Scalar multiplication

### Quaternion (`engine_3d.py`)
- `Quaternion()` – Quaternion for rotations

### RenderPipeline (`rendering_pipeline.py`)
- `RenderPipeline()` – Main rendering system
- `render_scene(scene: Scene3D, camera: Camera3D) -> None` – Render scene

### ShaderManager (`rendering_pipeline.py`)
- `ShaderManager()` – Manages shader programs
- `load_shader(name: str, vertex_code: str, fragment_code: str) -> None` – Load shader

### TextureManager (`rendering_pipeline.py`)
- `TextureManager()` – Manages texture resources
- `load_texture(name: str, file_path: str) -> bool` – Load texture

### ARSession (`ar_vr_support.py`)
- `ARSession()` – Manages AR tracking and world understanding
- `start_session() -> bool` – Start AR session
- `stop_session() -> None` – Stop AR session
- `get_camera_pose() -> tuple[Vector3D, Quaternion]` – Get camera pose

### VRRenderer (`ar_vr_support.py`)
- `VRRenderer()` – Handles stereo rendering for VR
- `render_stereo(scene) -> None` – Render stereo scene

### XRInterface (`ar_vr_support.py`)
- `XRInterface()` – Unified interface for AR/VR/XR experiences
- `initialize() -> bool` – Initialize XR interface
- `get_mixed_reality_frame() -> Dict[str, Any]` – Get mixed reality frame

## Operating Contracts
- Maintain alignment between code, documentation, and configured workflows.
- Ensure Model Context Protocol interfaces remain available for sibling agents.
- Record outcomes in shared telemetry and update TODO queues when necessary.

## Navigation Links
- **Human Documentation**: [README.md](README.md)
- **Functional Specification**: [SPEC.md](SPEC.md)
- **📁 Parent Directory**: [spatial](../README.md) - Parent directory documentation
- **🏠 Project Root**: [README](../../../../README.md) - Main project documentation