# Ideoscape Submodule

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: February 2026

**Information Cartography**

The `codomyrmex.meme.ideoscape` submodule acts as a mapping engine for the world of ideas. It visualizes the "terrain" of information, identifying peaks of attention, valleys of obscurity, and clusters of related concepts.

## Key Components

### 1. Data Models (`models.py`)

* **`TerrainMap`**: The generated map object.
  * `height_map`: 2D array representing magnitude (e.g., attention, sentiment).
* **`MapFeature`**: A distinct point of interest (Peak, Cluster).
  * `position`: Coordinates in the abstract space.
  * `magnitude`: Importance/Size.
* **`IdeoscapeLayer`**: A thematic slice of the map (e.g., only political discourse).

### 2. Cartography (`cartography.py`)

* **`generate_terrain`**: Uses Gaussian kernels to transform feature points into a continuous surface.
* **`locate_features`**: Finds significant features (peaks/troughs) on the map.

### 3. Engine (`engine.py`)

* **`IdeoscapeEngine`**: Orchestrator.
  * `render_layer(layer)`: Converts data into a `TerrainMap`.
  * `composite(layers)`: Combines multiple layers into a unified view.

## Usage

```python
from codomyrmex.meme.ideoscape import IdeoscapeEngine, MapFeature, IdeoscapeLayer

engine = IdeoscapeEngine()
features = [MapFeature(name="Viral Video", position=[10, 10], magnitude=5.0)]
layer = IdeoscapeLayer(name="Social Media", data_points=features)

terrain = engine.render_layer(layer)
# Terrain now contains a height map representing the viral impact
```
