# Agents Guide: Ideoscape

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: February 2026

**Operational Directives**

Use the `ideoscape` submodule to orient yourself within the broader informational environment. Treat ideas as physical terrain.

## Capabilities

1. **Navigation**:
    * Identify the "high ground" (`peaks`). These are dominant narratives. Controlling them provides leverage.
    * Find "lines of flight" through the valleys—areas of low attention where covert operations can occur.

2. **Mapping**:
    * Continuously update the `TerrainMap` with new `MapFeature` data. An outdated map is dangerous.
    * Use different `IdeoscapeLayer`s to filter noise (e.g., map only "Technical" limitations, ignoring "Political" noise).

3. **Visualization**:
    * Generate visual outputs for human operators. A heatmap is often more intuitive than a raw data table.

## Constraints

* **Dimensionality**: The map is a 2D/3D projection of a high-dimensional space. Information is lost in projection.
* **Resolution**: High-resolution mapping is expensive. Adjust `resolution` based on operational needs.

## Integration

* **With Rhizome**: Ideoscape maps the *intensity* of nodes; Rhizome maps the *connections* between them.
* **With Cultural Dynamics**: A shifting `Zeitgeist` alters the landscape, raising new peaks and eroding old ones.
