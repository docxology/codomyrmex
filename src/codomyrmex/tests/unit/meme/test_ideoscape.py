"""Tests for meme.ideoscape -- zero-mock, real instances only.

Covers ProjectionType, CoordinateSystem, MapFeature, IdeoscapeLayer,
TerrainMap, IdeoscapeEngine, generate_terrain, and locate_features.
"""

from __future__ import annotations

import numpy as np
import pytest

from codomyrmex.meme.ideoscape.cartography import generate_terrain, locate_features
from codomyrmex.meme.ideoscape.engine import IdeoscapeEngine
from codomyrmex.meme.ideoscape.models import (
    CoordinateSystem,
    IdeoscapeLayer,
    MapFeature,
    ProjectionType,
    TerrainMap,
)

# ---------------------------------------------------------------------------
# ProjectionType enum
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestProjectionType:
    """Tests for the ProjectionType enum."""

    def test_four_types_present(self) -> None:
        """MERCATOR, HYPERBOLIC, TOROIDAL, SPHERICAL are all present."""
        expected = {"mercator", "hyperbolic", "toroidal", "spherical"}
        assert {pt.value for pt in ProjectionType} == expected

    def test_str_subclass(self) -> None:
        """ProjectionType is a StrEnum."""
        assert isinstance(ProjectionType.MERCATOR, str)
        assert ProjectionType.SPHERICAL == "spherical"


# ---------------------------------------------------------------------------
# CoordinateSystem dataclass
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestCoordinateSystem:
    """Tests for the CoordinateSystem dataclass."""

    def test_default_dimensions(self) -> None:
        """Default dimensions is 2."""
        cs = CoordinateSystem()
        assert cs.dimensions == 2

    def test_default_bounds(self) -> None:
        """Default bounds are [-100, 100, -100, 100]."""
        cs = CoordinateSystem()
        assert cs.bounds == [-100.0, 100.0, -100.0, 100.0]

    def test_default_projection(self) -> None:
        """Default projection is MERCATOR."""
        cs = CoordinateSystem()
        assert cs.projection == ProjectionType.MERCATOR

    def test_custom_fields_stored(self) -> None:
        """Custom field values are stored correctly."""
        cs = CoordinateSystem(
            dimensions=3,
            bounds=[-50.0, 50.0, -50.0, 50.0],
            projection=ProjectionType.SPHERICAL,
        )
        assert cs.dimensions == 3
        assert cs.projection == ProjectionType.SPHERICAL


# ---------------------------------------------------------------------------
# MapFeature dataclass
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestMapFeature:
    """Tests for the MapFeature dataclass."""

    def test_creation_stores_name(self) -> None:
        """name field is stored correctly."""
        feature = MapFeature(name="Mount Doge")
        assert feature.name == "Mount Doge"

    def test_default_position_is_zero_array(self) -> None:
        """Default position is a 2-element zero array."""
        feature = MapFeature(name="x")
        assert feature.position.shape == (2,)
        assert np.all(feature.position == 0.0)

    def test_default_feature_type(self) -> None:
        """Default feature_type is 'point'."""
        feature = MapFeature(name="x")
        assert feature.feature_type == "point"

    def test_default_magnitude(self) -> None:
        """Default magnitude is 1.0."""
        feature = MapFeature(name="x")
        assert feature.magnitude == pytest.approx(1.0)

    def test_default_metadata_empty(self) -> None:
        """Default metadata is empty dict."""
        feature = MapFeature(name="x")
        assert feature.metadata == {}

    def test_list_position_converted_to_ndarray(self) -> None:
        """List position is converted to numpy array via __post_init__."""
        feature = MapFeature(name="peak", position=[10.0, -20.0])
        assert isinstance(feature.position, np.ndarray)
        assert feature.position[0] == pytest.approx(10.0)
        assert feature.position[1] == pytest.approx(-20.0)

    def test_explicit_magnitude_stored(self) -> None:
        """Explicit magnitude is stored correctly."""
        feature = MapFeature(name="cluster", magnitude=5.0)
        assert feature.magnitude == pytest.approx(5.0)


# ---------------------------------------------------------------------------
# IdeoscapeLayer dataclass
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestIdeoscapeLayer:
    """Tests for the IdeoscapeLayer dataclass."""

    def test_creation_stores_name(self) -> None:
        """name is stored correctly."""
        layer = IdeoscapeLayer(name="Sentiment")
        assert layer.name == "Sentiment"

    def test_data_points_default_empty(self) -> None:
        """Default data_points is empty list."""
        layer = IdeoscapeLayer(name="x")
        assert layer.data_points == []

    def test_opacity_default_one(self) -> None:
        """Default opacity is 1.0."""
        layer = IdeoscapeLayer(name="x")
        assert layer.opacity == pytest.approx(1.0)

    def test_data_points_stored(self) -> None:
        """data_points list is stored and retrievable."""
        features = [MapFeature(name="f1"), MapFeature(name="f2")]
        layer = IdeoscapeLayer(name="Keywords", data_points=features)
        assert len(layer.data_points) == 2

    def test_custom_opacity_stored(self) -> None:
        """Custom opacity value is stored correctly."""
        layer = IdeoscapeLayer(name="x", opacity=0.5)
        assert layer.opacity == pytest.approx(0.5)


# ---------------------------------------------------------------------------
# TerrainMap dataclass
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestTerrainMap:
    """Tests for the TerrainMap dataclass."""

    def test_default_height_map_shape(self) -> None:
        """Default height_map is 100x100 zeros."""
        terrain = TerrainMap()
        assert terrain.height_map.shape == (100, 100)
        assert np.all(terrain.height_map == 0.0)

    def test_default_resolution(self) -> None:
        """Default resolution is 100."""
        terrain = TerrainMap()
        assert terrain.resolution == 100

    def test_default_features_empty(self) -> None:
        """Default features is empty list."""
        terrain = TerrainMap()
        assert terrain.features == []

    def test_list_height_map_converted_to_ndarray(self) -> None:
        """List height_map is converted to numpy array via __post_init__."""
        data = [[0.1, 0.2], [0.3, 0.4]]
        terrain = TerrainMap(height_map=data)
        assert isinstance(terrain.height_map, np.ndarray)
        assert terrain.height_map.shape == (2, 2)

    def test_timestamp_is_float(self) -> None:
        """timestamp is a non-zero float."""
        terrain = TerrainMap()
        assert isinstance(terrain.timestamp, float)
        assert terrain.timestamp > 0


# ---------------------------------------------------------------------------
# generate_terrain
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestGenerateTerrain:
    """Tests for the generate_terrain function."""

    def test_empty_features_returns_zero_map(self) -> None:
        """No features produces an all-zero height map."""
        terrain = generate_terrain([], resolution=10)
        assert np.all(terrain.height_map == 0.0)

    def test_terrain_shape_matches_resolution(self) -> None:
        """Height map shape matches the resolution parameter."""
        terrain = generate_terrain([], resolution=50)
        assert terrain.height_map.shape == (50, 50)

    def test_returns_terrain_map_type(self) -> None:
        """generate_terrain always returns a TerrainMap."""
        result = generate_terrain([], resolution=10)
        assert isinstance(result, TerrainMap)

    def test_feature_at_center_creates_peak(self) -> None:
        """A feature at origin (0, 0) creates a peak near the center."""
        feature = MapFeature(
            name="center", position=np.array([0.0, 0.0]), magnitude=10.0
        )
        terrain = generate_terrain([feature], resolution=100)
        # The center of the map should have the highest value
        center = 50
        center_val = terrain.height_map[center, center]
        assert center_val > 0.0

    def test_multiple_features_additive(self) -> None:
        """Multiple features add their Gaussian contributions."""
        f1 = MapFeature(name="p1", position=np.array([0.0, 0.0]), magnitude=1.0)
        f2 = MapFeature(name="p2", position=np.array([0.0, 0.0]), magnitude=1.0)
        terrain_single = generate_terrain([f1], resolution=50)
        terrain_double = generate_terrain([f1, f2], resolution=50)
        # Double feature at same position should give ~double the peak value
        assert terrain_double.height_map.max() > terrain_single.height_map.max()

    def test_features_stored_in_terrain(self) -> None:
        """Generated terrain stores the input features."""
        features = [MapFeature(name="x"), MapFeature(name="y")]
        terrain = generate_terrain(features, resolution=10)
        assert len(terrain.features) == 2

    def test_resolution_stored_in_terrain(self) -> None:
        """Generated terrain stores the resolution."""
        terrain = generate_terrain([], resolution=42)
        assert terrain.resolution == 42


# ---------------------------------------------------------------------------
# locate_features
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestLocateFeatures:
    """Tests for the locate_features function."""

    def test_empty_terrain_no_peaks(self) -> None:
        """All-zero terrain has no peaks above positive threshold."""
        terrain = TerrainMap(height_map=np.zeros((10, 10)))
        peaks = locate_features(terrain, threshold=0.1)
        assert peaks == []

    def test_single_peak_detected(self) -> None:
        """A single elevated cell is detected as a peak."""
        hm = np.zeros((10, 10))
        hm[5, 5] = 1.0
        terrain = TerrainMap(height_map=hm)
        peaks = locate_features(terrain, threshold=0.5)
        assert len(peaks) == 1
        assert peaks[0] == (5, 5)

    def test_multiple_peaks_detected(self) -> None:
        """Multiple elevated cells above threshold are all detected."""
        hm = np.zeros((10, 10))
        hm[2, 3] = 0.9
        hm[7, 8] = 0.8
        terrain = TerrainMap(height_map=hm)
        peaks = locate_features(terrain, threshold=0.5)
        peak_set = set(peaks)
        assert (2, 3) in peak_set
        assert (7, 8) in peak_set

    def test_threshold_excludes_sub_threshold_cells(self) -> None:
        """Cells below threshold are not returned."""
        hm = np.zeros((5, 5))
        hm[1, 1] = 0.3  # below threshold
        hm[3, 3] = 0.7  # above threshold
        terrain = TerrainMap(height_map=hm)
        peaks = locate_features(terrain, threshold=0.5)
        assert (3, 3) in set(peaks)
        assert (1, 1) not in set(peaks)


# ---------------------------------------------------------------------------
# IdeoscapeEngine
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestIdeoscapeEngineRenderLayer:
    """Tests for IdeoscapeEngine.render_layer."""

    def test_render_empty_layer_returns_zero_terrain(self) -> None:
        """Empty layer produces an all-zero terrain map."""
        engine = IdeoscapeEngine()
        layer = IdeoscapeLayer(name="empty")
        terrain = engine.render_layer(layer, resolution=10)
        assert np.all(terrain.height_map == 0.0)

    def test_render_returns_terrain_map(self) -> None:
        """render_layer always returns a TerrainMap."""
        engine = IdeoscapeEngine()
        layer = IdeoscapeLayer(name="test")
        result = engine.render_layer(layer, resolution=20)
        assert isinstance(result, TerrainMap)

    def test_render_respects_resolution(self) -> None:
        """render_layer height map has the requested resolution."""
        engine = IdeoscapeEngine()
        layer = IdeoscapeLayer(name="test")
        terrain = engine.render_layer(layer, resolution=30)
        assert terrain.height_map.shape == (30, 30)

    def test_render_with_feature_creates_nonzero_map(self) -> None:
        """Layer with a feature produces a nonzero terrain map."""
        engine = IdeoscapeEngine()
        feature = MapFeature(name="peak", position=np.array([0.0, 0.0]), magnitude=5.0)
        layer = IdeoscapeLayer(name="test", data_points=[feature])
        terrain = engine.render_layer(layer, resolution=50)
        assert terrain.height_map.max() > 0.0


@pytest.mark.unit
class TestIdeoscapeEngineComposite:
    """Tests for IdeoscapeEngine.composite."""

    def test_composite_empty_layers_returns_zero_terrain(self) -> None:
        """Compositing no layers gives an all-zero 100x100 map."""
        engine = IdeoscapeEngine()
        result = engine.composite([])
        assert isinstance(result, TerrainMap)
        assert np.all(result.height_map == 0.0)

    def test_composite_returns_terrain_map(self) -> None:
        """composite always returns a TerrainMap."""
        engine = IdeoscapeEngine()
        result = engine.composite([IdeoscapeLayer(name="x")])
        assert isinstance(result, TerrainMap)

    def test_composite_combines_features_from_all_layers(self) -> None:
        """All layer features appear in the composite terrain features."""
        engine = IdeoscapeEngine()
        f1 = MapFeature(name="feature_A")
        f2 = MapFeature(name="feature_B")
        layer1 = IdeoscapeLayer(name="L1", data_points=[f1])
        layer2 = IdeoscapeLayer(name="L2", data_points=[f2])
        result = engine.composite([layer1, layer2])
        feature_names = {f.name for f in result.features}
        assert "feature_A" in feature_names
        assert "feature_B" in feature_names

    def test_composite_two_layers_additive(self) -> None:
        """Compositing two identical layers with full opacity doubles peak height."""
        engine = IdeoscapeEngine()
        feature = MapFeature(name="peak", position=np.array([0.0, 0.0]), magnitude=1.0)
        layer1 = IdeoscapeLayer(name="L1", data_points=[feature], opacity=1.0)
        layer2 = IdeoscapeLayer(name="L2", data_points=[feature], opacity=1.0)
        single = engine.composite([layer1])
        double = engine.composite([layer1, layer2])
        assert double.height_map.max() > single.height_map.max()

    def test_composite_opacity_zero_gives_zero_contribution(self) -> None:
        """Layer with opacity=0 contributes nothing to the terrain."""
        engine = IdeoscapeEngine()
        feature = MapFeature(name="peak", position=np.array([0.0, 0.0]), magnitude=10.0)
        layer = IdeoscapeLayer(name="invisible", data_points=[feature], opacity=0.0)
        result = engine.composite([layer])
        assert result.height_map.max() == pytest.approx(0.0, abs=1e-9)
