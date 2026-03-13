# Spatial — MCP Tool Specification

**Version**: v1.3.0 | **Last Updated**: March 2026

Tools are registered via `@mcp_tool(category="spatial")` and auto-discovered by the PAI MCP bridge.

---

## Tool: `spatial_generate_geodesic_mesh`

Generate an icosahedral geodesic mesh at the given subdivision frequency.

- **Category**: spatial
- **Parameters**:
  - `frequency` (integer, optional, default 2): Subdivision frequency (1 = base icosahedron).
  - `radius` (float, optional, default 1.0): Sphere radius.
- **Returns**: `{"status": "success", "vertex_count": <int>, "face_count": <int>, "frequency": <int>}`

---

## Tool: `spatial_rotate_point`

Rotate a 3D point using quaternion rotation (axis-angle input).

- **Category**: spatial
- **Parameters**:
  - `x`, `y`, `z` (float, required): Point coordinates.
  - `axis_x`, `axis_y`, `axis_z` (float, required): Rotation axis components.
  - `angle` (float, required): Rotation angle in radians.
- **Returns**: `{"status": "success", "x": <float>, "y": <float>, "z": <float>}`

---

## Tool: `spatial_geodesic_distance`

Compute geodesic (great-circle) distance between two points on a sphere.

- **Category**: spatial
- **Parameters**:
  - `x1`, `y1`, `z1` (float, required): First point coordinates.
  - `x2`, `y2`, `z2` (float, required): Second point coordinates.
  - `radius` (float, optional, default 1.0): Sphere radius.
- **Returns**: `{"status": "success", "geodesic_distance": <float>}`

---

## Error Handling

All tools return `{"status": "error", "message": "<message>"}` on failure.

For additional spatial tools (coordinate transformations, point distance), see `mcp_tools.py`.

## Navigation Links

- **Parent**: [Project Overview](../README.md)
- **Module Index**: [All Agents](../../AGENTS.md)
- **Documentation**: [Reference Guides](../../../docs/README.md)
- **Home**: [Root README](../../../README.md)
