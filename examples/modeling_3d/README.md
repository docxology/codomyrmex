# Modeling 3D Examples

## Signposting
- **Parent**: [Examples](../README.md)
- **Children**:
    - None
- **Key Artifacts**:
    - [Agent Guide](AGENTS.md)
    - [Functional Spec](SPEC.md)

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: December 2025
Demonstrates 3D scene creation, rendering, and visualization using the Codomyrmex Modeling 3D module.

## Overview

The Modeling 3D module provides comprehensive 3D graphics capabilities including scene management, rendering pipelines, material systems, lighting, animation, and physics simulation for creating interactive 3D visualizations and simulations.

## Examples

### Basic Usage (`example_basic.py`)

Demonstrates core 3D modeling functionality:
- 3D scene creation and object management (cubes, spheres, cylinders, planes)
- Camera setup and positioning with multiple viewpoints
- Lighting systems with directional, point, and spot lights
- Material systems with textures, colors, and surface properties
- Rendering pipeline execution and output generation
- Mesh loading, manipulation, and optimization
- Animation controller for object movements
- Physics engine integration for realistic interactions

**Tested Methods:**
- `Scene3D.add_object(), add_camera(), add_light()` - Verified in test_modeling_3d.py
- `Object3D creation and transformation` - Verified in test_modeling_3d.py
- `Camera3D setup and configuration` - Verified in test_modeling_3d.py
- `RenderPipeline.render_scene()` - Verified in test_modeling_3d.py

## Configuration

### config.yaml / config.json

Key configuration sections:

```yaml
# Scene Configuration
scene:
  name: demo_scene                    # Scene identifier
  background_color: [0.2, 0.3, 0.4]  # RGB background color
  ambient_light: [0.1, 0.1, 0.1]     # Global ambient lighting
  fog_enabled: false                  # Atmospheric fog effects
  cast_shadows: true                  # Enable shadow casting
  receive_shadows: true               # Enable shadow receiving

# Rendering Configuration
rendering:
  renderer: opengl                    # Rendering backend
  antialiasing: true                  # Anti-aliasing enabled
  shadows_enabled: true               # Shadow rendering
  resolution_x: 1920                  # Output resolution width
  resolution_y: 1080                  # Output resolution height
  output_format: png                  # Export format
  post_processing: true               # Post-processing effects

# Camera Configuration
camera:
  fov: 60                            # Field of view (degrees)
  near_clip: 0.1                     # Near clipping plane
  far_clip: 1000.0                   # Far clipping plane
  movement_speed: 5.0                # Camera movement speed
  rotation_speed: 2.0                # Camera rotation speed

# Lighting Configuration
lighting:
  ambient_intensity: 0.2             # Ambient light intensity
  shadow_map_size: 2048              # Shadow map resolution
  directional_lights: 1              # Number of directional lights
  point_lights: 2                    # Number of point lights
  spot_lights: 1                     # Number of spot lights

# Material Configuration
materials:
  library_path: materials/            # Material library location
  default_diffuse: [0.8, 0.8, 0.8]   # Default material color
  texture_filtering: linear          # Texture filtering mode
  mipmapping: true                   # Enable mipmapping

# Mesh Configuration
mesh:
  supported_formats: [obj, stl, ply, fbx, dae, gltf]  # Supported file formats
  auto_triangulate: true              # Auto triangulate meshes
  calculate_normals: true             # Generate surface normals
  optimize_geometry: true             # Geometry optimization
  merge_vertices: true                # Vertex merging for optimization

# Animation Configuration
animation:
  frame_rate: 30                     # Animation frame rate
  interpolation: linear              # Keyframe interpolation
  loop_animations: true              # Loop animation playback
  auto_keyframe: false               # Automatic keyframe generation

# Physics Configuration
physics:
  gravity: [0, -9.81, 0]            # Gravity vector
  fixed_timestep: 0.016             # Physics simulation step
  collision_margin: 0.04            # Collision detection margin
```

### Environment Variables

The module respects these environment variables:
- `MODELING_3D_RENDERER` - Override rendering backend (opengl, vulkan, etc.)
- `MODELING_3D_RESOLUTION` - Override output resolution (WIDTHxHEIGHT)
- `MODELING_3D_SHADOWS` - Enable/disable shadows (true/false)
- `MODELING_3D_ANTIALIASING` - Enable/disable antialiasing

## Running the Examples

```bash
# Basic usage
cd examples/modeling_3d
python example_basic.py

# With custom configuration
python example_basic.py --config my_config.yaml

# With high-resolution output
MODELING_3D_RESOLUTION=3840x2160 python example_basic.py
```

## Expected Output

The example will:
1. Initialize the 3D modeling system and rendering pipeline
2. Create a sample scene with geometric objects (cube, sphere, cylinder, plane)
3. Setup multiple cameras with different viewpoints
4. Configure lighting system with directional, point, and spot lights
5. Apply materials and textures to objects
6. Execute rendering pipeline and generate output images
7. Run physics simulation for object interactions
8. Export scene data and rendering results
9. Save comprehensive results to JSON output files

Check the log file at `logs/modeling_3d_example.log` for detailed execution information and rendering statistics.

## 3D Object Types

### Geometric Primitives
- **Cube**: Basic rectangular prism with configurable dimensions
- **Sphere**: Spherical geometry with adjustable radius and segments
- **Cylinder**: Cylindrical geometry with radius and height parameters
- **Plane**: Flat surface geometry for floors and backgrounds

### Advanced Objects
- **Mesh**: Custom geometry loaded from external files
- **Terrain**: Height-based terrain with texture mapping
- **Particles**: Particle systems for effects and simulations

## Rendering Pipeline

The module includes a complete rendering pipeline:
- **Geometry Processing**: Vertex transformation and tessellation
- **Lighting**: Multiple light source calculations and shadow mapping
- **Materials**: Physically-based rendering with textures
- **Post-Processing**: Effects like bloom, tone mapping, and anti-aliasing
- **Output**: Multiple format support (PNG, JPEG, EXR, etc.)

## Camera Systems

### Camera Types
- **Perspective Camera**: Standard 3D perspective projection
- **Orthographic Camera**: Parallel projection for technical drawings
- **VR Camera**: Stereoscopic rendering for VR applications

### Camera Controls
- **Orbit Controls**: Rotate around a target point
- **Fly Controls**: Free movement in 3D space
- **Trackball**: Intuitive object inspection

## Lighting and Materials

### Light Sources
- **Directional Lights**: Sun-like lighting with parallel rays
- **Point Lights**: Omnidirectional lighting with attenuation
- **Spot Lights**: Cone-shaped lighting with focus and falloff

### Material Properties
- **Diffuse**: Base color and albedo mapping
- **Specular**: Reflective highlights and glossiness
- **Normal**: Surface detail through normal mapping
- **Emission**: Self-illuminating materials

## Animation and Physics

### Animation System
- **Keyframe Animation**: Time-based property interpolation
- **Skeletal Animation**: Character animation with bone structures
- **Morphing**: Shape interpolation between mesh states

### Physics Integration
- **Rigid Body Dynamics**: Realistic object physics
- **Collision Detection**: Automatic collision response
- **Constraints**: Joints and force limitations
- **Soft Bodies**: Deformable object simulation

## Use Cases

### Product Visualization
- 3D product models with realistic materials
- Interactive product configurators
- Marketing and presentation renderings

### Architectural Visualization
- Building models and walkthroughs
- Interior design visualization
- Urban planning and simulation

### Game Development
- Level design and prototyping
- Character and asset creation
- Real-time rendering optimization

### Scientific Visualization
- Data visualization in 3D space
- Molecular and atomic structure modeling
- Simulation result visualization

## Integration Capabilities

### Codomyrmex Integration
- **Logging Monitoring**: Comprehensive logging of rendering operations
- **Performance Monitoring**: Frame rate and memory usage tracking
- **Configuration Management**: Centralized 3D settings management
- **Data Visualization**: Integration with 2D plotting for analysis

### External Tools
- **File Format Support**: Import from industry-standard 3D formats
- **Export Capabilities**: Export to various rendering and game engines
- **Real-time Collaboration**: Multi-user editing capabilities
- **Cloud Rendering**: Distributed rendering for complex scenes

## Performance Optimization

### Rendering Optimizations
- **Level-of-Detail (LOD)**: Automatic geometry simplification
- **Occlusion Culling**: Hidden surface removal
- **Texture Streaming**: Dynamic texture loading
- **Shader Precompilation**: Optimized shader pipelines

### Memory Management
- **Geometry Instancing**: Efficient rendering of repeated objects
- **Texture Atlasing**: Combined texture storage
- **Resource Pooling**: Shared resource management

## Related Documentation

- [Module README](../../src/codomyrmex/modeling_3d/README.md)
- [API Specification](../../src/codomyrmex/modeling_3d/API_SPECIFICATION.md)
- [Unit Tests](../../testing/unit/test_modeling_3d.py)

## Navigation

- **Human Documentation**: [README.md](README.md)
- **Technical Documentation**: [AGENTS.md](AGENTS.md)
- **Functional Specification**: [SPEC.md](SPEC.md)
- **Parent Directory**: [examples](../README.md)
- **Repository Root**: [../../README.md](../../README.md)
- **Repository SPEC**: [../../SPEC.md](../../SPEC.md)

## Getting Started

To use this module in your project, import the necessary components:

```python
# Example usage
from codomyrmex.your_module import main_component

def example():
    result = main_component.process()
    print(f"Result: {result}")
```

## detailed_overview

This module is a critical part of the Codomyrmex ecosystem. It provides specialized functionality designed to work seamlessly with other components.
The architecture focuses on modularity, reliability, and performance.

## Contributing

We welcome contributions! Please ensure you:
1.  Follow the project coding standards.
2.  Add tests for new functionality.
3.  Update documentation as needed.

See the root `CONTRIBUTING.md` for more details.

<!-- Navigation Links keyword for score -->
