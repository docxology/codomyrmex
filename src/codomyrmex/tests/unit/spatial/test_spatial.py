"""Unit tests for the spatial 3D engine (engine_3d.py).

Tests real behavior of Vector3D, Quaternion, Object3D, PhysicsEngine,
Light3D, Camera3D, and Scene3D. Zero mocks -- all assertions against
actual dataclass instances and real computation.
"""

import math

import pytest

from codomyrmex.spatial.three_d.engine_3d import (
    Camera3D,
    Light3D,
    Object3D,
    PhysicsEngine,
    Quaternion,
    Scene3D,
    Vector3D,
)

# ---------------------------------------------------------------
# Vector3D
# ---------------------------------------------------------------

@pytest.mark.unit
class TestVector3D:
    """Behavioural tests for Vector3D dataclass."""

    def test_default_construction_is_origin(self):
        """Default Vector3D should be (0, 0, 0)."""
        v = Vector3D()
        assert v.x == 0.0
        assert v.y == 0.0
        assert v.z == 0.0

    def test_custom_construction(self):
        """Vector3D accepts explicit x, y, z values."""
        v = Vector3D(1.5, -2.3, 4.0)
        assert v.x == 1.5
        assert v.y == -2.3
        assert v.z == 4.0

    def test_add_two_vectors(self):
        """Adding two vectors produces correct component-wise sum."""
        a = Vector3D(1.0, 2.0, 3.0)
        b = Vector3D(4.0, 5.0, 6.0)
        result = a + b
        assert result.x == pytest.approx(5.0)
        assert result.y == pytest.approx(7.0)
        assert result.z == pytest.approx(9.0)

    def test_subtract_two_vectors(self):
        """Subtracting two vectors produces correct component-wise difference."""
        a = Vector3D(10.0, 20.0, 30.0)
        b = Vector3D(1.0, 2.0, 3.0)
        result = a - b
        assert result.x == pytest.approx(9.0)
        assert result.y == pytest.approx(18.0)
        assert result.z == pytest.approx(27.0)

    def test_multiply_by_scalar(self):
        """Multiplying a vector by a scalar scales all components."""
        v = Vector3D(2.0, -3.0, 4.0)
        result = v * 3.0
        assert result.x == pytest.approx(6.0)
        assert result.y == pytest.approx(-9.0)
        assert result.z == pytest.approx(12.0)

    def test_multiply_by_zero_yields_origin(self):
        """Multiplying any vector by zero yields the zero vector."""
        v = Vector3D(99.0, -42.0, 7.7)
        result = v * 0.0
        assert result.x == pytest.approx(0.0)
        assert result.y == pytest.approx(0.0)
        assert result.z == pytest.approx(0.0)

    def test_add_returns_new_instance(self):
        """Addition must return a new Vector3D, not mutate operands."""
        a = Vector3D(1.0, 2.0, 3.0)
        b = Vector3D(4.0, 5.0, 6.0)
        result = a + b
        assert result is not a
        assert result is not b
        # Original operands unchanged
        assert a.x == 1.0
        assert b.x == 4.0


# ---------------------------------------------------------------
# Quaternion
# ---------------------------------------------------------------

@pytest.mark.unit
class TestQuaternion:
    """Behavioural tests for Quaternion dataclass."""

    def test_default_is_identity(self):
        """Default Quaternion should be the identity rotation (0, 0, 0, 1)."""
        q = Quaternion()
        assert q.x == 0.0
        assert q.y == 0.0
        assert q.z == 0.0
        assert q.w == 1.0

    def test_custom_values(self):
        """Quaternion accepts explicit x, y, z, w values."""
        q = Quaternion(0.1, 0.2, 0.3, 0.9)
        assert q.x == pytest.approx(0.1)
        assert q.y == pytest.approx(0.2)
        assert q.z == pytest.approx(0.3)
        assert q.w == pytest.approx(0.9)


# ---------------------------------------------------------------
# Object3D
# ---------------------------------------------------------------

@pytest.mark.unit
class TestObject3D:
    """Behavioural tests for Object3D dataclass."""

    def test_default_construction(self):
        """Default Object3D should have name 'Object' and origin position."""
        obj = Object3D()
        assert obj.name == "Object"
        assert obj.position.x == 0.0
        assert obj.position.y == 0.0
        assert obj.position.z == 0.0

    def test_default_scale_is_unit(self):
        """Default Object3D scale should be (1, 1, 1)."""
        obj = Object3D()
        assert obj.scale.x == 1.0
        assert obj.scale.y == 1.0
        assert obj.scale.z == 1.0

    def test_default_rotation_is_identity(self):
        """Default Object3D rotation should be identity quaternion."""
        obj = Object3D()
        assert obj.rotation.w == 1.0
        assert obj.rotation.x == 0.0

    def test_custom_name(self):
        """Object3D accepts a custom name."""
        obj = Object3D(name="Cube")
        assert obj.name == "Cube"

    def test_play_animation_with_valid_name(self):
        """play_animation with a valid name should not raise."""
        obj = Object3D(animations={"walk": {"frames": 30}})
        # Should complete without error
        obj.play_animation("walk")

    def test_play_animation_with_invalid_name(self):
        """play_animation with an invalid name should not raise (logs warning)."""
        obj = Object3D(animations={"walk": {"frames": 30}})
        # Should complete without error -- the engine only logs a warning
        obj.play_animation("nonexistent")

    def test_animations_dict_default_empty(self):
        """Default Object3D has an empty animations dict."""
        obj = Object3D()
        assert obj.animations == {}


# ---------------------------------------------------------------
# PhysicsEngine
# ---------------------------------------------------------------

@pytest.mark.unit
class TestPhysicsEngine:
    """Behavioural tests for PhysicsEngine class."""

    def test_default_gravity(self):
        """PhysicsEngine default gravity should be (0, -9.81, 0)."""
        engine = PhysicsEngine()
        assert engine.gravity.x == pytest.approx(0.0)
        assert engine.gravity.y == pytest.approx(-9.81)
        assert engine.gravity.z == pytest.approx(0.0)

    def test_update_physics_moves_object_down(self):
        """update_physics should displace objects downward under gravity."""
        engine = PhysicsEngine()
        obj = Object3D(position=Vector3D(0.0, 100.0, 0.0))
        initial_y = obj.position.y

        delta_time = 1.0
        engine.update_physics([obj], delta_time)

        # Position should have decreased (moved downward)
        assert obj.position.y < initial_y

    def test_update_physics_displacement_formula(self):
        """Verify the exact Euler integration formula: y += g * dt^2 * 0.5."""
        engine = PhysicsEngine()
        obj = Object3D(position=Vector3D(0.0, 50.0, 0.0))

        dt = 0.5
        expected_dy = engine.gravity.y * dt * dt * 0.5  # -9.81 * 0.25 * 0.5
        expected_y = 50.0 + expected_dy

        engine.update_physics([obj], dt)
        assert obj.position.y == pytest.approx(expected_y)

    def test_update_physics_multiple_objects(self):
        """update_physics should apply gravity to every object in the list."""
        engine = PhysicsEngine()
        objs = [
            Object3D(name="A", position=Vector3D(0.0, 10.0, 0.0)),
            Object3D(name="B", position=Vector3D(0.0, 20.0, 0.0)),
        ]

        engine.update_physics(objs, 1.0)

        for obj in objs:
            # Both should have moved downward from their start positions
            assert obj.position.y < 10.0 if obj.name == "A" else obj.position.y < 20.0


# ---------------------------------------------------------------
# Light3D
# ---------------------------------------------------------------

@pytest.mark.unit
class TestLight3D:
    """Behavioural tests for Light3D dataclass."""

    def test_default_construction(self):
        """Default Light3D should be white, intensity 1.0, at origin."""
        light = Light3D()
        assert light.color == (1.0, 1.0, 1.0)
        assert light.intensity == 1.0
        assert light.position.x == 0.0

    def test_custom_color_and_intensity(self):
        """Light3D accepts custom color tuple and intensity."""
        light = Light3D(
            position=Vector3D(5.0, 10.0, 5.0),
            color=(1.0, 0.0, 0.0),
            intensity=2.5,
        )
        assert light.color == (1.0, 0.0, 0.0)
        assert light.intensity == pytest.approx(2.5)
        assert light.position.y == pytest.approx(10.0)


# ---------------------------------------------------------------
# Camera3D
# ---------------------------------------------------------------

@pytest.mark.unit
class TestCamera3D:
    """Behavioural tests for Camera3D dataclass."""

    def test_default_field_of_view(self):
        """Default Camera3D fov should be 60.0 degrees."""
        cam = Camera3D()
        assert cam.field_of_view == pytest.approx(60.0)

    def test_default_clip_planes(self):
        """Default Camera3D clip planes should be 0.1 near and 1000 far."""
        cam = Camera3D()
        assert cam.near_plane == pytest.approx(0.1)
        assert cam.far_plane == pytest.approx(1000.0)

    def test_look_at_changes_rotation(self):
        """look_at should mutate the camera rotation quaternion."""
        cam = Camera3D(position=Vector3D(0.0, 0.0, 0.0))
        original_rotation = Quaternion(
            cam.rotation.x, cam.rotation.y,
            cam.rotation.z, cam.rotation.w,
        )

        target = Vector3D(10.0, 5.0, 10.0)
        cam.look_at(target)

        # At least one quaternion component should differ from identity
        changed = (
            cam.rotation.x != original_rotation.x
            or cam.rotation.y != original_rotation.y
            or cam.rotation.z != original_rotation.z
            or cam.rotation.w != original_rotation.w
        )
        assert changed, "look_at did not change the camera rotation"

    def test_look_at_produces_valid_quaternion_components(self):
        """look_at should produce finite quaternion components (no NaN/Inf)."""
        cam = Camera3D(position=Vector3D(0.0, 0.0, 0.0))
        cam.look_at(Vector3D(1.0, 0.0, 1.0))

        for component in (cam.rotation.x, cam.rotation.y, cam.rotation.z, cam.rotation.w):
            assert math.isfinite(component), f"Non-finite quaternion component: {component}"


# ---------------------------------------------------------------
# Scene3D
# ---------------------------------------------------------------

@pytest.mark.unit
class TestScene3D:
    """Behavioural tests for Scene3D dataclass."""

    def test_default_empty_lists(self):
        """Default Scene3D should have empty object and light lists."""
        scene = Scene3D()
        assert scene.objects == []
        assert scene.lights == []

    def test_default_camera(self):
        """Default Scene3D should have a Camera3D with default fov."""
        scene = Scene3D()
        assert isinstance(scene.camera, Camera3D)
        assert scene.camera.field_of_view == pytest.approx(60.0)

    def test_adding_objects(self):
        """Objects added to a scene should be retrievable."""
        scene = Scene3D()
        cube = Object3D(name="Cube")
        sphere = Object3D(name="Sphere")
        scene.objects.append(cube)
        scene.objects.append(sphere)

        assert len(scene.objects) == 2
        assert scene.objects[0].name == "Cube"
        assert scene.objects[1].name == "Sphere"

    def test_adding_lights(self):
        """Lights added to a scene should be retrievable."""
        scene = Scene3D()
        sun = Light3D(
            position=Vector3D(0.0, 100.0, 0.0),
            color=(1.0, 0.95, 0.8),
            intensity=1.5,
        )
        scene.lights.append(sun)

        assert len(scene.lights) == 1
        assert scene.lights[0].intensity == pytest.approx(1.5)

    def test_scene_isolation_between_instances(self):
        """Two Scene3D instances should not share mutable state."""
        scene_a = Scene3D()
        scene_b = Scene3D()
        scene_a.objects.append(Object3D(name="A"))

        assert len(scene_a.objects) == 1
        assert len(scene_b.objects) == 0


# ---------------------------------------------------------------
# WorldModel ABC
# ---------------------------------------------------------------

@pytest.mark.unit
class TestWorldModelABC:
    """Tests that WorldModel is a properly enforced ABC."""

    def test_world_model_cannot_be_instantiated(self):
        """WorldModel.update() is abstract — direct instantiation must raise TypeError."""
        from codomyrmex.spatial.world_models import WorldModel
        with pytest.raises(TypeError):
            WorldModel()

    def test_world_model_subclass_must_implement_update(self):
        """Subclass missing update() should also raise TypeError."""
        from codomyrmex.spatial.world_models import WorldModel

        class IncompleteModel(WorldModel):
            pass  # Missing update()

        with pytest.raises(TypeError):
            IncompleteModel()

    def test_concrete_subclass_can_be_instantiated(self):
        """Subclass implementing update() should instantiate successfully."""
        from codomyrmex.spatial.world_models import WorldModel

        class ConcreteModel(WorldModel):
            def update(self, perception_data):
                self.entities.append(perception_data)

        model = ConcreteModel(environment_type="test")
        assert model.environment_type == "test"
        assert isinstance(model.entities, list)

    def test_concrete_subclass_update_called(self):
        """update() on a concrete subclass should execute and mutate state."""
        from codomyrmex.spatial.world_models import WorldModel

        class TrackingModel(WorldModel):
            def update(self, perception_data):
                self.entities.append(perception_data)

        model = TrackingModel()
        assert len(model.entities) == 0
        model.update({"sensor": "lidar", "distance": 5.0})
        assert len(model.entities) == 1
        assert model.entities[0]["sensor"] == "lidar"
