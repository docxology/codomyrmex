"""IdeoscapeEngine — orchestrator for visualization."""

from __future__ import annotations

import numpy as np

from codomyrmex.meme.ideoscape.cartography import generate_terrain
from codomyrmex.meme.ideoscape.models import IdeoscapeLayer, TerrainMap


class IdeoscapeEngine:
    """Engine for rendering information landscapes."""

    def render_layer(self, layer: IdeoscapeLayer, resolution: int = 100) -> TerrainMap:
        """Render a single layer into a terrain map."""
        return generate_terrain(
            features=layer.data_points,
            resolution=resolution
        )

    def composite(self, layers: list[IdeoscapeLayer]) -> TerrainMap:
        """Combine multiple layers into a composite view."""
        # Simple additive compositing
        base_h = None
        all_features = []

        for layer in layers:
            t = self.render_layer(layer)
            if base_h is None:
                base_h = t.height_map * layer.opacity
            else:
                base_h += t.height_map * layer.opacity
            all_features.extend(layer.data_points)

        if base_h is None:
            # Empty map 100x100 default
            base_h = np.zeros((100, 100))

        return TerrainMap(height_map=base_h, features=all_features)
