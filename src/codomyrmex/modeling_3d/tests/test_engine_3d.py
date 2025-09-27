"""Test suite for 3D Modeling module."""

import pytest
from codomyrmex.modeling_3d import (
    Scene3D,
    Object3D,
    Camera3D,
    Light3D,
    Material3D,
    Vector3D,
    Quaternion,
    RenderPipeline,
)


class TestScene3D:
    """Test cases for Scene3D class."""

    def test_scene_creation(self):
        """Test creating an empty scene."""
        scene = Scene3D()
        assert len(scene.objects) == 0
        assert len(scene.cameras) == 0
        assert len(scene.lights) == 0

    def test_add_object(self):
        """Test adding objects to scene."""
        scene = Scene3D()
        obj = Object3D("TestObject")

        scene.add_object(obj)
        assert len(scene.objects) == 1
        assert scene.objects[0] == obj

    def test_add_camera(self):
        """Test adding cameras to scene."""
        scene = Scene3D()
        camera = Camera3D("TestCamera")

        scene.add_camera(camera)
        assert len(scene.cameras) == 1
        assert scene.cameras[0] == camera

    def test_add_light(self):
        """Test adding lights to scene."""
        scene = Scene3D()
        light = Light3D("TestLight")

        scene.add_light(light)
        assert len(scene.lights) == 1
        assert scene.lights[0] == light


class TestObject3D:
    """Test cases for Object3D class."""

    def test_object_creation(self):
        """Test creating a 3D object."""
        obj = Object3D("TestObject")
        assert obj.name == "TestObject"
        assert obj.position.x == 0.0
        assert obj.position.y == 0.0
        assert obj.position.z == 0.0

    def test_set_position(self):
        """Test setting object position."""
        obj = Object3D("TestObject")
        obj.set_position(1.0, 2.0, 3.0)

        assert obj.position.x == 1.0
        assert obj.position.y == 2.0
        assert obj.position.z == 3.0

    def test_set_rotation(self):
        """Test setting object rotation."""
        obj = Object3D("TestObject")
        obj.set_rotation(1.0, 0.0, 0.0, 0.0)

        assert obj.rotation.w == 1.0
        assert obj.rotation.x == 0.0
        assert obj.rotation.y == 0.0
        assert obj.rotation.z == 0.0


class TestVector3D:
    """Test cases for Vector3D class."""

    def test_vector_creation(self):
        """Test creating a 3D vector."""
        vec = Vector3D(1.0, 2.0, 3.0)
        assert vec.x == 1.0
        assert vec.y == 2.0
        assert vec.z == 3.0

    def test_vector_addition(self):
        """Test vector addition."""
        vec1 = Vector3D(1.0, 2.0, 3.0)
        vec2 = Vector3D(4.0, 5.0, 6.0)
        result = vec1 + vec2

        assert result.x == 5.0
        assert result.y == 7.0
        assert result.z == 9.0

    def test_vector_scaling(self):
        """Test vector scaling."""
        vec = Vector3D(1.0, 2.0, 3.0)
        result = vec * 2.0

        assert result.x == 2.0
        assert result.y == 4.0
        assert result.z == 6.0


class TestRenderPipeline:
    """Test cases for RenderPipeline class."""

    def test_pipeline_creation(self):
        """Test creating a render pipeline."""
        pipeline = RenderPipeline()
        assert pipeline is not None

    def test_render_scene(self):
        """Test rendering a scene."""
        pipeline = RenderPipeline()
        scene = Scene3D()
        camera = Camera3D("TestCamera")

        # Should not raise an exception
        pipeline.render_scene(scene, camera)


if __name__ == "__main__":
    pytest.main([__file__])
