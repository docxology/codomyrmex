import pytest

from codomyrmex.spatial.four_d import (
    ClosePackedSphere,
    IsotropicVectorMatrix,
    QuadrayCoordinate,
    synergetics_transform,
)


@pytest.mark.unit
class TestFourD:
    def test_quadray_coordinate(self):
        quad = QuadrayCoordinate(1.0, 2.0, 3.0, 4.0)
        assert quad.coords == (1.0, 2.0, 3.0, 4.0)

        default_quad = QuadrayCoordinate()
        assert default_quad.coords == (0.0, 0.0, 0.0, 0.0)

    def test_isotropic_vector_matrix(self):
        ivm = IsotropicVectorMatrix()
        assert isinstance(ivm, IsotropicVectorMatrix)

    def test_close_packed_sphere(self):
        cps = ClosePackedSphere()
        assert isinstance(cps, ClosePackedSphere)

    def test_synergetics_transform_raises(self):
        with pytest.raises(NotImplementedError) as exc_info:
            synergetics_transform((1.0, 2.0, 3.0))
        assert "not yet implemented" in str(exc_info.value)
