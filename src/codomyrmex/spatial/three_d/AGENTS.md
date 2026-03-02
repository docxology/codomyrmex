# Three-D Agentic Context

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Purpose

AR/VR device management and spatial computing support. Agents use this submodule to register devices, manage sessions, track spatial anchors, and handle hand-tracking input.

## Key Components

| Component | Type | Role |
|-----------|------|------|
| `ARVRManager` | Class | Central manager for AR/VR devices, sessions, and spatial data |
| `XRDevice` | Dataclass | Device metadata: id, name, type (AR/VR/MR), capabilities, tracking |
| `XRSession` | Dataclass | Active session with device, mode, start time, spatial anchors |
| `SpatialAnchor` | Dataclass | Named 3D anchor with position, rotation, confidence, persistence |
| `HandTrackingData` | Dataclass | Per-hand joint positions, gestures, confidence |
| `DeviceType` | Enum | AR, VR, MR device classification |
| `TrackingState` | Enum | NOT_TRACKING, LIMITED, NORMAL, EXCESSIVE_MOTION |
| `SessionMode` | Enum | IMMERSIVE_VR, IMMERSIVE_AR, INLINE |

## Operating Contracts

- `register_device(device)` adds a device; raises `ValueError` on duplicate ID.
- `create_session(device_id, mode)` returns an `XRSession`; raises `ValueError` if device unknown.
- `add_spatial_anchor(session_id, anchor)` appends to session's anchor list; raises `ValueError` if session unknown.
- `update_hand_tracking(session_id, hand_data)` stores latest hand-tracking snapshot.
- `get_nearby_anchors(session_id, position, radius)` returns anchors within Euclidean distance.
- `end_session(session_id)` removes the session from active tracking.
- All IDs are caller-provided strings.

## Integration Points

- Companion modules `engine_3d.py` and `rendering_pipeline.py` handle 3D rendering.
- Uses `spatial/coordinates` for underlying coordinate types.

## Navigation

- [README.md](README.md) | [SPEC.md](SPEC.md) | [PAI.md](PAI.md)
- Parent: [spatial](../README.md)
