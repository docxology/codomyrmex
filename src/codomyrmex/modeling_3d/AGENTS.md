# Codomyrmex Agents — src/codomyrmex/modeling_3d

## Signposting
- **Parent**: [codomyrmex](../AGENTS.md)
- **Self**: [Modeling 3D Agents](AGENTS.md)
- **Children**:
    - [docs](docs/AGENTS.md)
    - [examples](examples/AGENTS.md)
    - [tests](tests/AGENTS.md)
- **Key Artifacts**:
    - [Functional Spec](SPEC.md)
    - [Human Readme](README.md)

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: December 2025

## Purpose

Specialized Layer module providing 3D modeling, rendering, and AR/VR/XR capabilities for the Codomyrmex platform. This module enables spatial computing, 3D visualization, and immersive experiences through 3D engine support.

The modeling_3d module serves as the spatial computing layer, providing foundational 3D capabilities for applications requiring geometric modeling, rendering, and immersive interfaces.

## Module Overview

### Key Capabilities
- **3D Scene Management**: Scene composition with objects, cameras, and lighting
- **Geometric Modeling**: Mesh loading, transformation, and manipulation
- **Rendering Pipeline**: GPU-accelerated rendering with shaders and textures
- **AR/VR/XR Support**: Augmented, virtual, and mixed reality interfaces
- **Animation System**: Object animation and physics simulation
- **Material System**: Advanced material properties and shader management

### Key Features
- Multi-format mesh loading (OBJ, STL, etc.)
- Real-time rendering pipeline
- AR/VR device integration
- Physics-based animation
- Shader programming support
- Cross-platform rendering

## Function Signatures

### Scene3D Class Methods

```python
def __init__(self) -> None
```

Initialize an empty 3D scene.

**Returns:** None

```python
def add_object(self, obj: "Object3D") -> None
```

Add an object to the scene.

**Parameters:**
- `obj` (Object3D): 3D object to add to the scene

**Returns:** None

```python
def add_camera(self, camera: "Camera3D") -> None
```

Add a camera to the scene.

**Parameters:**
- `camera` (Camera3D): Camera to add to the scene

**Returns:** None

```python
def add_light(self, light: "Light3D") -> None
```

Add a light source to the scene.

**Parameters:**
- `light` (Light3D): Light source to add to the scene

**Returns:** None

```python
def remove_object(self, obj: "Object3D") -> None
```

Remove an object from the scene.

**Parameters:**
- `obj` (Object3D): 3D object to remove from the scene

**Returns:** None

```python
def get_objects_by_name(self, name: str) -> list["Object3D"]
```

Get all objects in the scene with a specific name.

**Parameters:**
- `name` (str): Name of objects to find

**Returns:** `list[Object3D]` - List of objects with matching name

### Object3D Class Methods

```python
def __init__(self, name: str = "Object") -> None
```

Initialize a 3D object.

**Parameters:**
- `name` (str): Name of the object. Defaults to "Object"

**Returns:** None

```python
def set_position(self, x: float, y: float, z: float) -> None
```

Set the position of the object in 3D space.

**Parameters:**
- `x` (float): X coordinate
- `y` (float): Y coordinate
- `z` (float): Z coordinate

**Returns:** None

```python
def set_rotation(self, w: float, x: float, y: float, z: float) -> None
```

Set the rotation of the object using quaternion.

**Parameters:**
- `w` (float): Quaternion W component
- `x` (float): Quaternion X component
- `y` (float): Quaternion Y component
- `z` (float): Quaternion Z component

**Returns:** None

```python
def set_scale(self, x: float, y: float, z: float) -> None
```

Set the scale of the object.

**Parameters:**
- `x` (float): X scale factor
- `y` (float): Y scale factor
- `z` (float): Z scale factor

**Returns:** None

### Camera3D Class Methods

```python
def __init__(self, name: str = "Camera") -> None
```

Initialize a 3D camera.

**Parameters:**
- `name` (str): Name of the camera. Defaults to "Camera"

**Returns:** None

```python
def set_position(self, x: float, y: float, z: float) -> None
```

Set the camera position.

**Parameters:**
- `x` (float): X coordinate
- `y` (float): Y coordinate
- `z` (float): Z coordinate

**Returns:** None

```python
def look_at(self, target_x: float, target_y: float, target_z: float) -> None
```

Make the camera look at a target point.

**Parameters:**
- `target_x` (float): Target X coordinate
- `target_y` (float): Target Y coordinate
- `target_z` (float): Target Z coordinate

**Returns:** None

```python
def set_perspective(self, fov: float, aspect_ratio: float, near: float, far: float) -> None
```

Set camera perspective parameters.

**Parameters:**
- `fov` (float): Field of view in degrees
- `aspect_ratio` (float): Aspect ratio (width/height)
- `near` (float): Near clipping plane
- `far` (float): Far clipping plane

**Returns:** None

### Light3D Class Methods

```python
def __init__(self, name: str = "Light") -> None
```

Initialize a 3D light source.

**Parameters:**
- `name` (str): Name of the light. Defaults to "Light"

**Returns:** None

```python
def set_position(self, x: float, y: float, z: float) -> None
```

Set the light position.

**Parameters:**
- `x` (float): X coordinate
- `y` (float): Y coordinate
- `z` (float): Z coordinate

**Returns:** None

```python
def set_color(self, r: float, g: float, b: float) -> None
```

Set the light color.

**Parameters:**
- `r` (float): Red component (0.0-1.0)
- `g` (float): Green component (0.0-1.0)
- `b` (float): Blue component (0.0-1.0)

**Returns:** None

```python
def set_intensity(self, intensity: float) -> None
```

Set the light intensity.

**Parameters:**
- `intensity` (float): Light intensity multiplier

**Returns:** None

### Material3D Class Methods

```python
def __init__(self, name: str = "Material") -> None
```

Initialize a 3D material.

**Parameters:**
- `name` (str): Name of the material. Defaults to "Material"

**Returns:** None

```python
def set_diffuse_color(self, r: float, g: float, b: float) -> None
```

Set the diffuse color of the material.

**Parameters:**
- `r` (float): Red component (0.0-1.0)
- `g` (float): Green component (0.0-1.0)
- `b` (float): Blue component (0.0-1.0)

**Returns:** None

```python
def set_specular_color(self, r: float, g: float, b: float) -> None
```

Set the specular color of the material.

**Parameters:**
- `r` (float): Red component (0.0-1.0)
- `g` (float): Green component (0.0-1.0)
- `b` (float): Blue component (0.0-1.0)

**Returns:** None

```python
def set_texture(self, texture_path: str) -> None
```

Set the texture for the material.

**Parameters:**
- `texture_path` (str): Path to texture file

**Returns:** None

### MeshLoader Utility Methods

```python
@staticmethod
def load_obj(file_path: str) -> Object3D
```

Load a 3D mesh from OBJ file format.

**Parameters:**
- `file_path` (str): Path to OBJ file

**Returns:** `Object3D` - Loaded 3D object

### AnimationController Class Methods

```python
def __init__(self) -> None
```

Initialize the animation controller.

**Returns:** None

```python
def play_animation(self, name: str) -> None
```

Play an animation by name.

**Parameters:**
- `name` (str): Name of the animation to play

**Returns:** None

```python
def stop_animation(self) -> None
```

Stop the currently playing animation.

**Returns:** None

```python
def pause_animation(self) -> None
```

Pause the currently playing animation.

**Returns:** None

### PhysicsEngine Class Methods

```python
def __init__(self) -> None
```

Initialize the physics engine.

**Returns:** None

```python
def update_physics(self, objects: list[Object3D], delta_time: float) -> None
```

Update physics simulation for objects.

**Parameters:**
- `objects` (list[Object3D]): Objects to simulate physics for
- `delta_time` (float): Time delta for simulation step

**Returns:** None

```python
def add_force(self, obj: Object3D, force: Vector3D) -> None
```

Apply a force to an object.

**Parameters:**
- `obj` (Object3D): Object to apply force to
- `force` (Vector3D): Force vector to apply

**Returns:** None

### AR/VR/XR Support Classes

### ARSession Class Methods

```python
def __init__(self) -> None
```

Initialize an AR session.

**Returns:** None

```python
def start_session(self) -> bool
```

Start the AR session.

**Returns:** `bool` - True if session started successfully

```python
def stop_session(self) -> None
```

Stop the AR session.

**Returns:** None

```python
def get_camera_pose(self) -> tuple[Vector3D, Quaternion]
```

Get the current camera pose in AR space.

**Returns:** `tuple[Vector3D, Quaternion]` - Camera position and rotation

```python
def detect_planes(self) -> list[dict[str, Any]]
```

Detect real-world planes in AR space.

**Returns:** `list[dict[str, Any]]` - Detected planes with position and extent data

### VRRenderer Class Methods

```python
def __init__(self) -> None
```

Initialize the VR renderer.

**Returns:** None

```python
def render_stereo(self, scene) -> None
```

Render the scene in stereo for VR display.

**Parameters:**
- `scene`: Scene to render

**Returns:** None

```python
def get_eye_poses(self) -> tuple[tuple[Vector3D, Quaternion], tuple[Vector3D, Quaternion]]
```

Get the poses for left and right eyes.

**Returns:** `tuple[tuple[Vector3D, Quaternion], tuple[Vector3D, Quaternion]]` - Left and right eye poses

### XRInterface Class Methods

```python
def __init__(self) -> None
```

Initialize the XR interface.

**Returns:** None

```python
def initialize(self) -> bool
```

Initialize the XR runtime.

**Returns:** `bool` - True if XR initialized successfully

```python
def get_mixed_reality_frame(self) -> dict[str, Any]
```

Get a mixed reality frame combining real and virtual content.

**Returns:** `dict[str, Any]` - Frame data with camera image and virtual overlays

```python
def submit_frame(self, rendered_frame: Any) -> None
```

Submit a rendered frame to the XR display.

**Parameters:**
- `rendered_frame` (Any): Rendered frame data

**Returns:** None

### Rendering Pipeline Classes

### ShaderManager Class Methods

```python
def __init__(self) -> None
```

Initialize the shader manager.

**Returns:** None

```python
def load_shader(self, name: str, vertex_code: str, fragment_code: str) -> None
```

Load a shader program.

**Parameters:**
- `name` (str): Name of the shader
- `vertex_code` (str): Vertex shader source code
- `fragment_code` (str): Fragment shader source code

**Returns:** None

```python
def get_shader(self, name: str) -> Optional[Any]
```

Get a loaded shader by name.

**Parameters:**
- `name` (str): Name of the shader

**Returns:** `Optional[Any]` - Shader object or None if not found

### TextureManager Class Methods

```python
def __init__(self) -> None
```

Initialize the texture manager.

**Returns:** None

```python
def load_texture(self, name: str, file_path: str) -> bool
```

Load a texture from file.

**Parameters:**
- `name` (str): Name of the texture
- `file_path` (str): Path to texture file

**Returns:** `bool` - True if texture loaded successfully

```python
def get_texture(self, name: str) -> Optional[Any]
```

Get a loaded texture by name.

**Parameters:**
- `name` (str): Name of the texture

**Returns:** `Optional[Any]` - Texture object or None if not found

### RenderPipeline Class Methods

```python
def __init__(self) -> None
```

Initialize the rendering pipeline.

**Returns:** None

```python
def render_scene(self, scene: Scene3D, camera: Camera3D) -> None
```

Render a 3D scene from a camera perspective.

**Parameters:**
- `scene` (Scene3D): Scene to render
- `camera` (Camera3D): Camera to render from

**Returns:** None

```python
def set_render_target(self, width: int, height: int) -> None
```

Set the render target dimensions.

**Parameters:**
- `width` (int): Render target width
- `height` (int): Render target height

**Returns:** None

## Data Structures

### Vector3D
```python
@dataclass
class Vector3D:
    x: float = 0.0
    y: float = 0.0
    z: float = 0.0

    def __add__(self, other: Vector3D) -> Vector3D
    def __mul__(self, scalar: float) -> Vector3D
    def dot(self, other: Vector3D) -> float
    def cross(self, other: Vector3D) -> Vector3D
    def magnitude(self) -> float
    def normalize(self) -> Vector3D
```

3D vector representation with mathematical operations.

### Quaternion
```python
@dataclass
class Quaternion:
    w: float = 1.0
    x: float = 0.0
    y: float = 0.0
    z: float = 0.0
```

Quaternion for 3D rotations.

## Active Components

### Core Implementation
- `__init__.py` – Module initialization and public API exports
- `engine_3d.py` – Core 3D engine with scene, objects, cameras, and lights
- `rendering_pipeline.py` – GPU rendering pipeline with shaders and textures
- `ar_vr_support.py` – AR/VR/XR device interfaces and session management

### Documentation
- `README.md` – Module usage and overview
- `API_SPECIFICATION.md` – Complete API documentation
- `USAGE_EXAMPLES.md` – Practical usage demonstrations
- `SECURITY.md` – Security considerations for 3D content and XR

### Examples and Testing
- `examples/` – Usage examples and demonstrations
- `tests/` – Comprehensive test suite
- `docs/` – Additional documentation and guides

## Operating Contracts

### Universal 3D Modeling Protocols

All 3D operations within the Codomyrmex platform must:

1. **Performance Optimized** - 3D rendering maintains acceptable frame rates
2. **Memory Efficient** - 3D assets are loaded and managed efficiently
3. **Cross-Platform Compatible** - 3D functionality works across supported platforms
4. **Safety Conscious** - XR experiences include appropriate safety boundaries
5. **Accessibility Aware** - 3D content considers accessibility requirements

### Module-Specific Guidelines

#### 3D Scene Management
- Maintain scene graph consistency
- Provide efficient object culling
- Support level-of-detail (LOD) systems
- Include scene serialization capabilities

#### Rendering Pipeline
- Support multiple rendering backends
- Implement efficient shader management
- Provide post-processing effects pipeline
- Support multiple output formats

#### AR/VR/XR Support
- Implement device-specific optimizations
- Provide calibration and setup procedures
- Include safety and comfort features
- Support multiple XR runtimes

#### Asset Management
- Support multiple 3D file formats
- Implement asset streaming for large scenes
- Provide asset compression and optimization
- Include asset validation and error handling

## Navigation Links
- **Human Documentation**: [README.md](README.md)
- **Functional Specification**: [SPEC.md](SPEC.md)

### Module Documentation
- **Module Overview**: [README.md](README.md) - Complete module documentation
- **API Reference**: [API_SPECIFICATION.md](API_SPECIFICATION.md) - Detailed API specification (if applicable)

### Platform Navigation
- **Parent Directory**: [codomyrmex](../README.md) - Package overview
- **Project Root**: [README](../../../README.md) - Main project documentation
- **Source Root**: [src](../../README.md) - Source code documentation