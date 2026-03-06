"""Tests for embodiment transformation and Vec3 classes."""

import math

import pytest

from codomyrmex.embodiment.transformation.transformation import Transform3D, Vec3


@pytest.mark.unit
class TestVec3:
    def test_init(self):
        v = Vec3(1.0, 2.0, 3.0)
        assert v.x == 1.0
        assert v.y == 2.0
        assert v.z == 3.0

    def test_addition(self):
        v1 = Vec3(1.0, 2.0, 3.0)
        v2 = Vec3(4.0, 5.0, 6.0)
        v3 = v1 + v2
        assert v3.to_tuple() == (5.0, 7.0, 9.0)

    def test_subtraction(self):
        v1 = Vec3(4.0, 5.0, 6.0)
        v2 = Vec3(1.0, 2.0, 3.0)
        v3 = v1 - v2
        assert v3.to_tuple() == (3.0, 3.0, 3.0)

    def test_multiplication(self):
        v = Vec3(1.0, 2.0, 3.0)
        v2 = v * 2.5
        assert v2.to_tuple() == (2.5, 5.0, 7.5)
        v3 = 2.0 * v
        assert v3.to_tuple() == (2.0, 4.0, 6.0)

    def test_length(self):
        v = Vec3(3.0, 4.0, 0.0)
        assert v.length() == 5.0

    def test_normalized(self):
        v = Vec3(3.0, 4.0, 0.0)
        n = v.normalized()
        assert n.to_tuple() == (0.6, 0.8, 0.0)

        # zero vector case
        v0 = Vec3(0.0, 0.0, 0.0)
        n0 = v0.normalized()
        assert n0.to_tuple() == (0.0, 0.0, 0.0)

    def test_dot(self):
        v1 = Vec3(1.0, 2.0, 3.0)
        v2 = Vec3(4.0, -5.0, 6.0)
        assert v1.dot(v2) == 4.0 - 10.0 + 18.0

    def test_cross(self):
        vx = Vec3(1.0, 0.0, 0.0)
        vy = Vec3(0.0, 1.0, 0.0)
        vz = vx.cross(vy)
        assert vz.to_tuple() == (0.0, 0.0, 1.0)

    def test_dict(self):
        v = Vec3(1.5, -2.5, 3.5)
        assert v.to_dict() == {"x": 1.5, "y": -2.5, "z": 3.5}

@pytest.mark.unit
class TestTransform3D:
    def test_identity(self):
        t = Transform3D.identity()
        assert t.translation.to_tuple() == (0.0, 0.0, 0.0)
        assert t.rotation == (0.0, 0.0, 0.0)

    def test_from_translation(self):
        t = Transform3D.from_translation(1.0, 2.0, 3.0)
        assert t.translation.to_tuple() == (1.0, 2.0, 3.0)

    def test_from_yaw(self):
        t = Transform3D.from_yaw(math.pi)
        assert t.rotation == (0.0, 0.0, math.pi)

    def test_transform_vector(self):
        t = Transform3D.from_yaw(math.pi / 2.0)
        v = t.transform_vector((1.0, 0.0, 0.0))
        assert v[0] == pytest.approx(0.0)
        assert v[1] == pytest.approx(1.0)
        assert v[2] == pytest.approx(0.0)

    def test_compose(self):
        t1 = Transform3D.from_translation(1.0, 0.0, 0.0)
        t2 = Transform3D.from_translation(0.0, 2.0, 0.0)
        t3 = t1.compose(t2)
        # Applying t2 then t1: point + (0,2,0) then + (1,0,0) -> (1,2,0)
        assert t3.translation.to_tuple() == (1.0, 2.0, 0.0)

    def test_inverse(self):
        t = Transform3D(translation=(1.0, 2.0, 3.0), rotation=(math.pi/4, math.pi/6, math.pi/3))
        t_inv = t.inverse()
        t_ident = t.compose(t_inv)
        assert t_ident.translation.x == pytest.approx(0.0, abs=1e-9)
        assert t_ident.translation.y == pytest.approx(0.0, abs=1e-9)
        assert t_ident.translation.z == pytest.approx(0.0, abs=1e-9)

        assert t_ident.rotation[0] == pytest.approx(0.0, abs=1e-9)
        assert t_ident.rotation[1] == pytest.approx(0.0, abs=1e-9)
        assert t_ident.rotation[2] == pytest.approx(0.0, abs=1e-9)

    def test_rad_deg(self):
        assert Transform3D.rad_to_deg(math.pi) == 180.0
        assert Transform3D.deg_to_rad(180.0) == math.pi

    def test_to_dict(self):
        t = Transform3D.from_translation(1.0, 2.0, 3.0)
        d = t.to_dict()
        assert d["translation"]["x"] == 1.0
        assert d["rotation"]["roll"] == 0.0

    def test_repr(self):
        t = Transform3D.from_translation(1.0, 2.0, 3.0)
        s = repr(t)
        assert "Transform3D" in s
        assert "1.000, 2.000, 3.000" in s
