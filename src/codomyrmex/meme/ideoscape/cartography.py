"""Terrain generation and mapping algorithms."""

from __future__ import annotations

import numpy as np

from codomyrmex.meme.ideoscape.models import MapFeature, TerrainMap


def generate_terrain(
    features: list[MapFeature],
    resolution: int = 100,
    bounds: tuple[float, float, float, float] = (-100.0, 100.0, -100.0, 100.0)
) -> TerrainMap:
    """Generate a height map from feature points using Gaussian kernels.
    
    Simulates 'peaks' of high activity/virality mapped to 2D space.
    """
    x_min, x_max, y_min, y_max = bounds
    x = np.linspace(x_min, x_max, resolution)
    y = np.linspace(y_min, y_max, resolution)
    X, Y = np.meshgrid(x, y)

    Z = np.zeros((resolution, resolution))

    for f in features:
        # Gaussian peak: A * exp(-((x-x0)^2 + (y-y0)^2) / 2s^2)
        # Using magnitude as A and fixed sigma for spread

        # Ensure position has at least 2 coords
        if len(f.position) < 2:
            continue

        x0, y0 = f.position[0], f.position[1]
        sigma = 10.0  # Default spread

        # Apply Gaussian
        dist_sq = (X - x0)**2 + (Y - y0)**2
        gauss = f.magnitude * np.exp(-dist_sq / (2 * sigma**2))
        Z += gauss

    return TerrainMap(
        height_map=Z,
        resolution=resolution,
        features=features
    )


def locate_features(terrain: TerrainMap, threshold: float) -> list[tuple[int, int]]:
    """Find grid coordinates of peaks above threshold."""
    peaks = np.where(terrain.height_map > threshold)
    # peaks is (array([row_indices]), array([col_indices]))
    return list(zip(peaks[0], peaks[1]))
