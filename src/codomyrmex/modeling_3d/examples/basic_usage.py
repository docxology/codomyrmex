"""Basic usage examples for the 3D Modeling module."""

from codomyrmex.modeling_3d import (
    Camera3D,
    Light3D,
    Material3D,
    Object3D,
    RenderPipeline,
    Scene3D,
    Vector3D,
)


def basic_scene_example():
    """Create and render a basic 3D scene."""

    # Create scene
    scene = Scene3D()

    # Create objects
    cube = Object3D("Cube")
    cube.set_position(0.0, 0.0, 0.0)

    # Add material
    material = Material3D("RedPlastic")
    material.diffuse_color = Vector3D(1.0, 0.0, 0.0)
    cube.material = material

    scene.add_object(cube)

    # Setup camera
    camera = Camera3D("MainCamera")
    camera.set_position(0.0, 0.0, 5.0)
    scene.add_camera(camera)

    # Add lighting
    light = Light3D("KeyLight")
    light.set_position(-2.0, 2.0, 2.0)
    light.intensity = 1.5
    scene.add_light(light)

    # Render
    pipeline = RenderPipeline()
    pipeline.render_scene(scene, camera)

    return scene


def ar_example():
    """Demonstrate AR capabilities."""

    from codomyrmex.modeling_3d import ARSession

    ar_session = ARSession()

    if ar_session.start_session():
        pose = ar_session.get_camera_pose()
        print(f"Camera position: {pose[0]}")
        print(f"Camera rotation: {pose[1]}")
    else:
        print("Failed to start AR session")


def vr_example():
    """Demonstrate VR rendering."""

    from codomyrmex.modeling_3d import Scene3D, VRRenderer

    scene = Scene3D()
    vr_renderer = VRRenderer()

    # Render for VR headset
    vr_renderer.render_stereo(scene)


if __name__ == "__main__":
    print("Running 3D Modeling examples...")

    # Run basic example
    scene = basic_scene_example()
    print(f"Created scene with {len(scene.objects)} objects")

    # Run AR example
    ar_example()

    print("Examples completed!")
