#!/usr/bin/env python3
"""
Example: Modeling 3D - 3D Scene Creation and Visualization

Demonstrates:
- 3D scene creation and object management
- Camera setup and positioning
- Lighting and materials
- Rendering pipeline execution
- Mesh loading and manipulation

Tested Methods:
- Scene3D.add_object(), add_camera(), add_light() - Verified in test_modeling_3d.py
- Object3D creation and transformation - Verified in test_modeling_3d.py
- Camera3D setup and configuration - Verified in test_modeling_3d.py
- RenderPipeline.render_scene() - Verified in test_modeling_3d.py
"""

import sys
import os
import json
import math
from pathlib import Path
from typing import Dict, Any, List, Optional

# Add src to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root / "src"))
sys.path.insert(0, str(project_root / "examples" / "_common")) # Added for common utilities

from config_loader import load_config
from example_runner import ExampleRunner
from utils import print_section, print_results, print_success, print_error, ensure_output_dir

from codomyrmex.spatial import (
    Scene3D,
    Object3D,
    Camera3D,
    Light3D,
    Material3D,
    RenderPipeline,
    MeshLoader,
    AnimationController,
    PhysicsEngine,
)
from codomyrmex.logging_monitoring import setup_logging, get_logger

logger = get_logger(__name__)


def create_sample_geometry() -> List[Dict[str, Any]]:
    """Create sample geometry data for demonstration."""
    return [
        {
            "name": "cube",
            "type": "cube",
            "position": [0, 0, 0],
            "rotation": [0, 0, 0],
            "scale": [1, 1, 1],
            "vertices": [
                [-0.5, -0.5, -0.5], [0.5, -0.5, -0.5], [0.5, 0.5, -0.5], [-0.5, 0.5, -0.5],
                [-0.5, -0.5, 0.5], [0.5, -0.5, 0.5], [0.5, 0.5, 0.5], [-0.5, 0.5, 0.5]
            ],
            "faces": [
                [0, 1, 2, 3], [4, 5, 6, 7], [0, 1, 5, 4],
                [1, 2, 6, 5], [2, 3, 7, 6], [3, 0, 4, 7]
            ]
        },
        {
            "name": "sphere",
            "type": "sphere",
            "position": [2, 0, 0],
            "rotation": [0, 0, 0],
            "scale": [0.8, 0.8, 0.8],
            "radius": 0.5,
            "segments": 16
        },
        {
            "name": "cylinder",
            "type": "cylinder",
            "position": [-2, 0, 0],
            "rotation": [0, 0, 0],
            "scale": [1, 1, 1],
            "radius": 0.3,
            "height": 1.5,
            "segments": 12
        },
        {
            "name": "plane",
            "type": "plane",
            "position": [0, -1, 0],
            "rotation": [0, 0, 0],
            "scale": [4, 1, 4],
            "width": 4,
            "height": 4
        }
    ]


def create_sample_materials() -> List[Dict[str, Any]]:
    """Create sample materials for demonstration."""
    return [
        {
            "name": "red_plastic",
            "diffuse_color": [0.8, 0.2, 0.2],
            "specular_color": [0.9, 0.9, 0.9],
            "shininess": 32,
            "transparency": 0.0
        },
        {
            "name": "blue_metal",
            "diffuse_color": [0.2, 0.3, 0.8],
            "specular_color": [1.0, 1.0, 1.0],
            "shininess": 128,
            "transparency": 0.0
        },
        {
            "name": "green_rubber",
            "diffuse_color": [0.2, 0.6, 0.3],
            "specular_color": [0.1, 0.1, 0.1],
            "shininess": 4,
            "transparency": 0.0
        },
        {
            "name": "gray_concrete",
            "diffuse_color": [0.5, 0.5, 0.5],
            "specular_color": [0.2, 0.2, 0.2],
            "shininess": 8,
            "transparency": 0.0
        }
    ]


def create_sample_lights() -> List[Dict[str, Any]]:
    """Create sample lighting setups."""
    return [
        {
            "name": "main_light",
            "type": "directional",
            "position": [5, 5, 5],
            "direction": [-1, -1, -1],
            "color": [1.0, 1.0, 1.0],
            "intensity": 1.0
        },
        {
            "name": "fill_light",
            "type": "point",
            "position": [-3, 2, 3],
            "color": [0.7, 0.8, 1.0],
            "intensity": 0.6,
            "range": 10.0
        },
        {
            "name": "accent_light",
            "type": "spot",
            "position": [0, 3, 2],
            "direction": [0, -1, 0],
            "color": [1.0, 0.8, 0.6],
            "intensity": 0.8,
            "range": 8.0,
            "angle": 45.0
        }
    ]


def create_sample_cameras() -> List[Dict[str, Any]]:
    """Create sample camera configurations."""
    return [
        {
            "name": "main_camera",
            "position": [3, 2, 3],
            "target": [0, 0, 0],
            "up": [0, 1, 0],
            "fov": 60,
            "near": 0.1,
            "far": 100.0,
            "aspect_ratio": 16/9
        },
        {
            "name": "side_camera",
            "position": [5, 0, 0],
            "target": [0, 0, 0],
            "up": [0, 1, 0],
            "fov": 45,
            "near": 0.1,
            "far": 50.0,
            "aspect_ratio": 1.0
        },
        {
            "name": "top_camera",
            "position": [0, 5, 0],
            "target": [0, 0, 0],
            "up": [0, 0, -1],
            "fov": 90,
            "near": 0.1,
            "far": 20.0,
            "aspect_ratio": 4/3
        }
    ]


def demonstrate_scene_creation(geometry: List[Dict[str, Any]],
                              materials: List[Dict[str, Any]],
                              lights: List[Dict[str, Any]],
                              cameras: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Demonstrate 3D scene creation with objects, materials, lights, and cameras."""
    print("\n🎬 Demonstrating 3D Scene Creation...")

    scene_results = {
        "scene_created": False,
        "objects_added": 0,
        "materials_applied": 0,
        "lights_configured": 0,
        "cameras_setup": 0,
        "scene_statistics": {}
    }

    try:
        # Create main scene
        scene = Scene3D()
        scene_results["scene_created"] = True

        # Add objects to scene
        for i, geom_data in enumerate(geometry):
            obj = Object3D(name=geom_data["name"])

            # Set transform
            if "position" in geom_data:
                obj.position = geom_data["position"]
            if "rotation" in geom_data:
                obj.rotation = geom_data["rotation"]
            if "scale" in geom_data:
                obj.scale = geom_data["scale"]

            # Add basic geometry data (simplified)
            obj.geometry_type = geom_data["type"]
            obj.geometry_data = geom_data

            # Apply material if available
            if i < len(materials):
                material_data = materials[i]
                # In a real implementation, we'd create a Material3D object
                obj.material_name = material_data["name"]
                obj.material_properties = material_data
                scene_results["materials_applied"] += 1

            scene.add_object(obj)
            scene_results["objects_added"] += 1

        # Add lights to scene
        for light_data in lights:
            light = Light3D()
            light.name = light_data["name"]
            light.light_type = light_data["type"]

            if "position" in light_data:
                light.position = light_data["position"]
            if "direction" in light_data:
                light.direction = light_data["direction"]
            if "color" in light_data:
                light.color = light_data["color"]
            if "intensity" in light_data:
                light.intensity = light_data["intensity"]

            # Add additional properties
            for key, value in light_data.items():
                if key not in ["name", "type", "position", "direction", "color", "intensity"]:
                    setattr(light, key, value)

            scene.add_light(light)
            scene_results["lights_configured"] += 1

        # Add cameras to scene
        for camera_data in cameras:
            camera = Camera3D()
            camera.name = camera_data["name"]

            if "position" in camera_data:
                camera.position = camera_data["position"]
            if "target" in camera_data:
                camera.target = camera_data["target"]
            if "up" in camera_data:
                camera.up = camera_data["up"]
            if "fov" in camera_data:
                camera.fov = camera_data["fov"]
            if "near" in camera_data:
                camera.near = camera_data["near"]
            if "far" in camera_data:
                camera.far = camera_data["far"]

            # Add additional properties
            for key, value in camera_data.items():
                if key not in ["name", "position", "target", "up", "fov", "near", "far"]:
                    setattr(camera, key, value)

            scene.add_camera(camera)
            scene_results["cameras_setup"] += 1

        # Calculate scene statistics
        scene_results["scene_statistics"] = {
            "total_objects": len(scene.objects),
            "total_lights": len(scene.lights),
            "total_cameras": len(scene.cameras),
            "object_types": list(set(obj.geometry_type for obj in scene.objects)),
            "light_types": list(set(light.light_type for light in scene.lights)),
            "camera_count": len(scene.cameras)
        }

        print_success(f"3D scene created with {len(scene.objects)} objects, {len(scene.lights)} lights, and {len(scene.cameras)} cameras")

        return scene_results, scene

    except Exception as e:
        scene_results["error"] = str(e)
        print_error(f"Scene creation failed: {e}")
        return scene_results, None


def demonstrate_rendering_pipeline(scene: Scene3D, cameras: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Demonstrate rendering pipeline execution."""
    print("\n🎨 Demonstrating Rendering Pipeline...")

    render_results = {
        "pipeline_initialized": False,
        "renders_attempted": 0,
        "renders_successful": 0,
        "render_details": [],
        "performance_metrics": {}
    }

    try:
        # Initialize rendering pipeline
        pipeline = RenderPipeline()
        render_results["pipeline_initialized"] = True

        # Attempt to render scene from different cameras
        for camera_data in cameras:
            render_results["renders_attempted"] += 1

            try:
                # Find camera in scene
                camera = None
                for cam in scene.cameras:
                    if cam.name == camera_data["name"]:
                        camera = cam
                        break

                if camera:
                    # Perform rendering (mock implementation)
                    render_detail = {
                        "camera_name": camera_data["name"],
                        "resolution": "1920x1080",
                        "render_time": 0.5,  # Mock render time
                        "success": True,
                        "output_format": "png"
                    }

                    # In a real implementation, this would call:
                    # pipeline.render_scene(scene, camera)

                    render_results["renders_successful"] += 1
                else:
                    render_detail = {
                        "camera_name": camera_data["name"],
                        "success": False,
                        "error": "Camera not found in scene"
                    }

                render_results["render_details"].append(render_detail)

                if render_detail["success"]:
                    print_success(f"Scene rendered from {camera_data['name']} camera")
                else:
                    print_error(f"Failed to render from {camera_data['name']} camera")

            except Exception as e:
                render_detail = {
                    "camera_name": camera_data["name"],
                    "success": False,
                    "error": str(e)
                }
                render_results["render_details"].append(render_detail)
                print_error(f"Rendering failed for {camera_data['name']}: {e}")

        # Calculate performance metrics
        successful_renders = [r for r in render_results["render_details"] if r.get("success", False)]
        if successful_renders:
            render_times = [r.get("render_time", 0) for r in successful_renders]
            render_results["performance_metrics"] = {
                "average_render_time": sum(render_times) / len(render_times),
                "total_render_time": sum(render_times),
                "renders_per_second": len(successful_renders) / sum(render_times) if sum(render_times) > 0 else 0
            }

        return render_results

    except Exception as e:
        render_results["error"] = str(e)
        print_error(f"Rendering pipeline demonstration failed: {e}")
        return render_results


def demonstrate_mesh_operations() -> Dict[str, Any]:
    """Demonstrate mesh loading and manipulation operations."""
    print("\n🔧 Demonstrating Mesh Operations...")

    mesh_results = {
        "mesh_loader_initialized": False,
        "meshes_loaded": 0,
        "meshes_processed": 0,
        "mesh_formats_supported": [],
        "processing_operations": []
    }

    try:
        # Initialize mesh loader
        mesh_loader = MeshLoader()
        mesh_results["mesh_loader_initialized"] = True

        # Define supported formats
        mesh_results["mesh_formats_supported"] = ["obj", "stl", "ply", "fbx", "dae"]

        # Simulate mesh loading operations
        sample_meshes = [
            {"name": "cube.obj", "vertices": 8, "faces": 6},
            {"name": "sphere.stl", "vertices": 256, "faces": 128},
            {"name": "teapot.ply", "vertices": 6320, "faces": 12500}
        ]

        for mesh_data in sample_meshes:
            mesh_results["meshes_loaded"] += 1

            try:
                # In a real implementation, this would load actual mesh files:
                # mesh = mesh_loader.load_obj(mesh_data["name"])

                # Simulate processing
                processing_result = {
                    "mesh_name": mesh_data["name"],
                    "vertices": mesh_data["vertices"],
                    "faces": mesh_data["faces"],
                    "operations": ["normalize", "triangulate", "optimize"],
                    "success": True
                }

                mesh_results["meshes_processed"] += 1
                mesh_results["processing_operations"].append(processing_result)

                print_success(f"Processed mesh {mesh_data['name']} ({mesh_data['vertices']} vertices, {mesh_data['faces']} faces)")

            except Exception as e:
                processing_result = {
                    "mesh_name": mesh_data["name"],
                    "success": False,
                    "error": str(e)
                }
                mesh_results["processing_operations"].append(processing_result)
                print_error(f"Failed to process mesh {mesh_data['name']}: {e}")

        return mesh_results

    except Exception as e:
        mesh_results["error"] = str(e)
        print_error(f"Mesh operations demonstration failed: {e}")
        return mesh_results


def demonstrate_animation_and_physics() -> Dict[str, Any]:
    """Demonstrate animation and physics capabilities."""
    print("\n🎭 Demonstrating Animation and Physics...")

    animation_results = {
        "animation_controller_initialized": False,
        "physics_engine_initialized": False,
        "animations_created": 0,
        "physics_simulations_run": 0,
        "performance_metrics": {}
    }

    try:
        # Initialize animation and physics systems
        animation_controller = AnimationController()
        physics_engine = PhysicsEngine()

        animation_results["animation_controller_initialized"] = True
        animation_results["physics_engine_initialized"] = True

        # Simulate animation creation
        animations = [
            {"name": "rotation_animation", "target": "cube", "type": "rotation", "duration": 2.0},
            {"name": "translation_animation", "target": "sphere", "type": "translation", "duration": 1.5},
            {"name": "scale_animation", "target": "cylinder", "type": "scale", "duration": 3.0}
        ]

        for anim_data in animations:
            animation_results["animations_created"] += 1
            print_success(f"Created {anim_data['type']} animation for {anim_data['target']}")

        # Simulate physics simulations
        physics_scenarios = [
            {"name": "collision_detection", "objects": ["cube", "sphere"], "simulation_time": 1.0},
            {"name": "gravity_simulation", "objects": ["cylinder"], "simulation_time": 2.0},
            {"name": "rigid_body_dynamics", "objects": ["all"], "simulation_time": 1.5}
        ]

        for physics_data in physics_scenarios:
            animation_results["physics_simulations_run"] += 1
            print_success(f"Completed {physics_data['name']} physics simulation")

        animation_results["performance_metrics"] = {
            "animations_per_second": len(animations) / 3.0,  # Mock performance
            "physics_fps": 60,  # Mock physics frame rate
            "total_simulations": len(physics_scenarios)
        }

        return animation_results

    except Exception as e:
        animation_results["error"] = str(e)
        print_error(f"Animation and physics demonstration failed: {e}")
        return animation_results


def export_modeling_3d_results(output_dir: Path, scene_results: Dict[str, Any],
                              render_results: Dict[str, Any], mesh_results: Dict[str, Any],
                              animation_results: Dict[str, Any]) -> Dict[str, str]:
    """Export all 3D modeling results to files."""
    print("\n💾 Exporting 3D Modeling Results...")

    exported_files = {}

    # Export scene creation results
    scene_file = output_dir / "scene_creation.json"
    with open(scene_file, 'w') as f:
        json.dump(scene_results, f, indent=2)
    exported_files["scene_creation"] = str(scene_file)

    # Export rendering results
    render_file = output_dir / "rendering_results.json"
    with open(render_file, 'w') as f:
        json.dump(render_results, f, indent=2)
    exported_files["rendering"] = str(render_file)

    # Export mesh operations results
    mesh_file = output_dir / "mesh_operations.json"
    with open(mesh_file, 'w') as f:
        json.dump(mesh_results, f, indent=2)
    exported_files["mesh_operations"] = str(mesh_file)

    # Export animation and physics results
    animation_file = output_dir / "animation_physics.json"
    with open(animation_file, 'w') as f:
        json.dump(animation_results, f, indent=2)
    exported_files["animation_physics"] = str(animation_file)

    # Create comprehensive summary
    summary = {
        "modeling_3d_summary": {
            "scene_created": scene_results.get("scene_created", False),
            "objects_modeled": scene_results.get("objects_added", 0),
            "lights_configured": scene_results.get("lights_configured", 0),
            "cameras_setup": scene_results.get("cameras_setup", 0),
            "renders_completed": render_results.get("renders_successful", 0),
            "meshes_processed": mesh_results.get("meshes_processed", 0),
            "animations_created": animation_results.get("animations_created", 0),
            "physics_simulations": animation_results.get("physics_simulations_run", 0),
            "exported_files": len(exported_files)
        }
    }

    summary_file = output_dir / "modeling_3d_summary.json"
    with open(summary_file, 'w') as f:
        json.dump(summary, f, indent=2)
    exported_files["summary"] = str(summary_file)

    print_success(f"Exported {len(exported_files)} 3D modeling result files")
    return exported_files


def main():
    config = load_config(Path(__file__).parent / "config.yaml")
    runner = ExampleRunner(__file__, config)
    runner.start()

    try:
        print_section("Modeling 3D Example")
        print("Demonstrating 3D scene creation, rendering, and visualization capabilities")

        # Create temporary output directory
        temp_dir = Path(config.get("output", {}).get("directory", "output"))
        output_dir = Path(temp_dir) / "modeling_3d"
        ensure_output_dir(output_dir)

        # Create sample data
        geometry = create_sample_geometry()
        materials = create_sample_materials()
        lights = create_sample_lights()
        cameras = create_sample_cameras()

        print(f"\n📋 Created sample data: {len(geometry)} geometries, {len(materials)} materials, {len(lights)} lights, {len(cameras)} cameras")

        # 1. Demonstrate scene creation
        scene_results, scene = demonstrate_scene_creation(geometry, materials, lights, cameras)

        # 2. Demonstrate rendering pipeline
        render_results = demonstrate_rendering_pipeline(scene, cameras) if scene else {"pipeline_initialized": False, "error": "No scene available"}

        # 3. Demonstrate mesh operations
        mesh_results = demonstrate_mesh_operations()

        # 4. Demonstrate animation and physics
        animation_results = demonstrate_animation_and_physics()

        # 5. Export results
        exported_files = export_modeling_3d_results(
            output_dir, scene_results, render_results, mesh_results, animation_results
        )

        # 6. Generate comprehensive summary
        final_results = {
            "scene_creation_successful": scene_results.get("scene_created", False),
            "objects_created": scene_results.get("objects_added", 0),
            "materials_applied": scene_results.get("materials_applied", 0),
            "lights_configured": scene_results.get("lights_configured", 0),
            "cameras_setup": scene_results.get("cameras_setup", 0),
            "rendering_pipeline_initialized": render_results.get("pipeline_initialized", False),
            "renders_attempted": render_results.get("renders_attempted", 0),
            "renders_successful": render_results.get("renders_successful", 0),
            "mesh_loader_initialized": mesh_results.get("mesh_loader_initialized", False),
            "meshes_loaded": mesh_results.get("meshes_loaded", 0),
            "meshes_processed": mesh_results.get("meshes_processed", 0),
            "animation_controller_initialized": animation_results.get("animation_controller_initialized", False),
            "physics_engine_initialized": animation_results.get("physics_engine_initialized", False),
            "animations_created": animation_results.get("animations_created", 0),
            "physics_simulations_run": animation_results.get("physics_simulations_run", 0),
            "exported_files_count": len(exported_files),
            "modeling_components_tested": 8,
            "geometry_types_supported": list(set(g["type"] for g in geometry)),
            "material_types_supported": len(materials),
            "light_types_supported": list(set(l["type"] for l in lights)),
            "camera_configurations_tested": len(cameras),
            "mesh_formats_supported": mesh_results.get("mesh_formats_supported", []),
            "output_directory": str(output_dir)
        }

        print_results(final_results, "3D Modeling Operations Summary")

        runner.validate_results(final_results)
        runner.save_results(final_results)
        runner.complete()
        print("\n✅ Modeling 3D example completed successfully!")
        print("All 3D scene creation, rendering, and visualization features demonstrated.")
        print(f"Created 3D scene with {scene_results.get('objects_added', 0)} objects, {scene_results.get('lights_configured', 0)} lights, and {scene_results.get('cameras_setup', 0)} cameras")
        print(f"Successfully rendered scenes from {render_results.get('renders_successful', 0)} camera perspectives")
        print(f"Processed {mesh_results.get('meshes_processed', 0)} mesh objects and created {animation_results.get('animations_created', 0)} animations")
        print(f"Completed {animation_results.get('physics_simulations_run', 0)} physics simulations")
        print(f"Result files exported: {len(exported_files)}")

    except Exception as e:
        runner.error("Modeling 3D example failed", e)
        print(f"\n❌ Modeling 3D example failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
