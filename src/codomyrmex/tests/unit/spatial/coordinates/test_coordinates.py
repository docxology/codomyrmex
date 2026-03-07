import math

import pytest

from codomyrmex.spatial.coordinates import (
    CoordinateTransformer,
    CylindricalCoord,
    GeographicCoord,
    Matrix4x4,
    Point3D,
    SphericalCoord,
)


@pytest.mark.unit
class TestPoint3D:
    def test_point_addition(self):
        p1 = Point3D(1.0, 2.0, 3.0)
        p2 = Point3D(4.0, 5.0, 6.0)
        p3 = p1 + p2
        assert p3.x == 5.0
        assert p3.y == 7.0
        assert p3.z == 9.0

    def test_point_subtraction(self):
        p1 = Point3D(4.0, 5.0, 6.0)
        p2 = Point3D(1.0, 2.0, 3.0)
        p3 = p1 - p2
        assert p3.x == 3.0
        assert p3.y == 3.0
        assert p3.z == 3.0

    def test_point_scalar_multiplication(self):
        p = Point3D(1.0, 2.0, 3.0)
        res = p * 2.5
        assert res.x == 2.5
        assert res.y == 5.0
        assert res.z == 7.5

    def test_point_scalar_division(self):
        p = Point3D(10.0, 20.0, 30.0)
        res = p / 2.0
        assert res.x == 5.0
        assert res.y == 10.0
        assert res.z == 15.0

    def test_point_magnitude(self):
        p = Point3D(3.0, 4.0, 0.0)
        assert p.magnitude() == 5.0

    def test_point_normalize(self):
        p = Point3D(3.0, 4.0, 0.0)
        norm = p.normalize()
        assert norm.x == 3.0 / 5.0
        assert norm.y == 4.0 / 5.0
        assert norm.z == 0.0

    def test_point_normalize_zero(self):
        p = Point3D(0.0, 0.0, 0.0)
        norm = p.normalize()
        assert norm.x == 0.0
        assert norm.y == 0.0
        assert norm.z == 0.0

    def test_point_dot_product(self):
        p1 = Point3D(1.0, 2.0, 3.0)
        p2 = Point3D(4.0, 5.0, 6.0)
        assert p1.dot(p2) == 1 * 4 + 2 * 5 + 3 * 6

    def test_point_cross_product(self):
        p1 = Point3D(1.0, 0.0, 0.0)
        p2 = Point3D(0.0, 1.0, 0.0)
        cross = p1.cross(p2)
        assert cross.x == 0.0
        assert cross.y == 0.0
        assert cross.z == 1.0

    def test_point_distance_to(self):
        p1 = Point3D(1.0, 1.0, 1.0)
        p2 = Point3D(4.0, 5.0, 1.0)
        assert p1.distance_to(p2) == 5.0

    def test_point_tuples(self):
        p1 = Point3D(1.5, 2.5, 3.5)
        t = p1.to_tuple()
        assert t == (1.5, 2.5, 3.5)
        p2 = Point3D.from_tuple(t)
        assert p2 == p1


@pytest.mark.unit
class TestSphericalCoord:
    def test_to_cartesian(self):
        s = SphericalCoord(r=10.0, theta=math.pi / 2, phi=math.pi / 2)
        p = s.to_cartesian()
        assert math.isclose(p.x, 0.0, abs_tol=1e-9)
        assert math.isclose(p.y, 10.0, abs_tol=1e-9)
        assert math.isclose(p.z, 0.0, abs_tol=1e-9)

    def test_from_cartesian(self):
        p = Point3D(0.0, 10.0, 0.0)
        s = SphericalCoord.from_cartesian(p)
        assert math.isclose(s.r, 10.0)
        assert math.isclose(s.theta, math.pi / 2)
        assert math.isclose(s.phi, math.pi / 2)

    def test_from_cartesian_origin(self):
        p = Point3D(0.0, 0.0, 0.0)
        s = SphericalCoord.from_cartesian(p)
        assert s.r == 0.0
        assert s.theta == 0.0
        assert s.phi == 0.0


@pytest.mark.unit
class TestCylindricalCoord:
    def test_to_cartesian(self):
        c = CylindricalCoord(r=5.0, theta=math.pi, z=10.0)
        p = c.to_cartesian()
        assert math.isclose(p.x, -5.0, abs_tol=1e-9)
        assert math.isclose(p.y, 0.0, abs_tol=1e-9)
        assert p.z == 10.0

    def test_from_cartesian(self):
        p = Point3D(-5.0, 0.0, 10.0)
        c = CylindricalCoord.from_cartesian(p)
        assert math.isclose(c.r, 5.0)
        assert math.isclose(c.theta, math.pi)
        assert c.z == 10.0


@pytest.mark.unit
class TestGeographicCoord:
    def test_to_cartesian(self):
        g = GeographicCoord(lat=0.0, lon=90.0, alt=0.0)
        p = g.to_cartesian()
        assert math.isclose(p.x, 0.0, abs_tol=1e-3)
        assert math.isclose(p.y, GeographicCoord.EARTH_RADIUS, abs_tol=1e-3)
        assert math.isclose(p.z, 0.0, abs_tol=1e-3)

    def test_from_cartesian(self):
        p = Point3D(0.0, GeographicCoord.EARTH_RADIUS, 0.0)
        g = GeographicCoord.from_cartesian(p)
        assert math.isclose(g.lat, 0.0, abs_tol=1e-3)
        assert math.isclose(g.lon, 90.0, abs_tol=1e-3)
        assert math.isclose(g.alt, 0.0, abs_tol=1e-3)

    def test_from_cartesian_origin(self):
        p = Point3D(0.0, 0.0, 0.0)
        g = GeographicCoord.from_cartesian(p)
        assert g.lat == 0.0
        assert g.lon == 0.0
        assert g.alt == -GeographicCoord.EARTH_RADIUS

    def test_distance_to(self):
        # New York
        ny = GeographicCoord(lat=40.7128, lon=-74.0060)
        # London
        ldn = GeographicCoord(lat=51.5074, lon=-0.1278)
        dist = ny.distance_to(ldn)
        # should be approx 5.58M meters
        assert 5_500_000 < dist < 5_600_000

    def test_bearing_to(self):
        p1 = GeographicCoord(lat=0.0, lon=0.0)
        p2 = GeographicCoord(lat=10.0, lon=0.0)
        bearing = p1.bearing_to(p2)
        assert math.isclose(bearing, 0.0, abs_tol=1e-3)

        p3 = GeographicCoord(lat=0.0, lon=10.0)
        bearing2 = p1.bearing_to(p3)
        assert math.isclose(bearing2, 90.0, abs_tol=1e-3)


@pytest.mark.unit
class TestMatrix4x4:
    def test_identity(self):
        mat = Matrix4x4.identity()
        assert mat.data[0][0] == 1.0
        assert mat.data[1][1] == 1.0

    def test_translation(self):
        mat = Matrix4x4.translation(2.0, 3.0, 4.0)
        p = Point3D(1.0, 1.0, 1.0)
        p_t = mat.transform_point(p)
        assert p_t.x == 3.0
        assert p_t.y == 4.0
        assert p_t.z == 5.0

    def test_scale(self):
        mat = Matrix4x4.scale(2.0, 3.0, 4.0)
        p = Point3D(10.0, 10.0, 10.0)
        p_s = mat.transform_point(p)
        assert p_s.x == 20.0
        assert p_s.y == 30.0
        assert p_s.z == 40.0

    def test_rotation_x(self):
        mat = Matrix4x4.rotation_x(math.pi / 2)
        p = Point3D(0.0, 1.0, 0.0)
        p_r = mat.transform_point(p)
        assert math.isclose(p_r.x, 0.0, abs_tol=1e-9)
        assert math.isclose(p_r.y, 0.0, abs_tol=1e-9)
        assert math.isclose(p_r.z, 1.0, abs_tol=1e-9)

    def test_rotation_y(self):
        mat = Matrix4x4.rotation_y(math.pi / 2)
        p = Point3D(1.0, 0.0, 0.0)
        p_r = mat.transform_point(p)
        assert math.isclose(p_r.x, 0.0, abs_tol=1e-9)
        assert math.isclose(p_r.y, 0.0, abs_tol=1e-9)
        assert math.isclose(p_r.z, -1.0, abs_tol=1e-9)

    def test_rotation_z(self):
        mat = Matrix4x4.rotation_z(math.pi / 2)
        p = Point3D(1.0, 0.0, 0.0)
        p_r = mat.transform_point(p)
        assert math.isclose(p_r.x, 0.0, abs_tol=1e-9)
        assert math.isclose(p_r.y, 1.0, abs_tol=1e-9)
        assert math.isclose(p_r.z, 0.0, abs_tol=1e-9)

    def test_multiplication(self):
        m1 = Matrix4x4.translation(1, 2, 3)
        m2 = Matrix4x4.scale(2, 2, 2)
        m3 = m1 * m2
        p = Point3D(1, 1, 1)
        p_t = m3.transform_point(p)
        assert p_t.x == 3.0
        assert p_t.y == 4.0
        assert p_t.z == 5.0

    def test_w_not_one(self):
        mat = Matrix4x4()
        mat.data[3][3] = 2.0  # Making w=2
        p = Point3D(10.0, 20.0, 30.0)
        p_t = mat.transform_point(p)
        assert p_t.x == 5.0
        assert p_t.y == 10.0
        assert p_t.z == 15.0


@pytest.mark.unit
class TestCoordinateTransformer:
    def test_transformers(self):
        p = Point3D(1.0, 0.0, 0.0)
        s = CoordinateTransformer.cartesian_to_spherical(p)
        assert s.r == 1.0

        p2 = CoordinateTransformer.spherical_to_cartesian(s)
        assert math.isclose(p2.x, 1.0, abs_tol=1e-3)

        c = CoordinateTransformer.cartesian_to_cylindrical(p)
        assert c.r == 1.0

        p3 = CoordinateTransformer.cylindrical_to_cartesian(c)
        assert math.isclose(p3.x, 1.0, abs_tol=1e-3)

        # Geographics
        geo = CoordinateTransformer.cartesian_to_geographic(
            Point3D(GeographicCoord.EARTH_RADIUS, 0, 0)
        )
        assert math.isclose(geo.lat, 0.0, abs_tol=1e-3)

        p4 = CoordinateTransformer.geographic_to_cartesian(geo)
        assert math.isclose(p4.x, GeographicCoord.EARTH_RADIUS, abs_tol=1e-3)

        assert math.isclose(CoordinateTransformer.degrees_to_radians(180), math.pi)
        assert math.isclose(CoordinateTransformer.radians_to_degrees(math.pi), 180)
