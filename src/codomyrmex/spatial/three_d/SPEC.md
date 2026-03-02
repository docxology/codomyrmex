# Three-D -- Technical Specification

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Overview

AR/VR device management, spatial anchoring, and hand-tracking support for extended reality applications. The `ARVRManager` orchestrates device registration, session lifecycle, and spatial data queries.

## Architecture

```
ARVRManager
  +-- devices: dict[str, XRDevice]
  +-- sessions: dict[str, XRSession]
  +-- register_device(device)
  +-- create_session(device_id, mode) -> XRSession
  +-- add_spatial_anchor(session_id, anchor)
  +-- update_hand_tracking(session_id, hand_data)
  +-- get_nearby_anchors(session_id, position, radius)
  +-- end_session(session_id)
```

## Key Classes

### XRDevice

| Field | Type | Notes |
|-------|------|-------|
| `id` | `str` | Unique device identifier |
| `name` | `str` | Human-readable device name |
| `device_type` | `DeviceType` | AR, VR, or MR |
| `capabilities` | `list[str]` | Feature strings (e.g., "hand_tracking") |
| `tracking_state` | `TrackingState` | Current tracking quality |

### XRSession

| Field | Type | Notes |
|-------|------|-------|
| `id` | `str` | UUID4 auto-generated |
| `device_id` | `str` | Associated device |
| `mode` | `SessionMode` | IMMERSIVE_VR, IMMERSIVE_AR, or INLINE |
| `started_at` | `datetime` | Session creation time |
| `spatial_anchors` | `list[SpatialAnchor]` | Anchors added during session |
| `hand_tracking` | `HandTrackingData or None` | Latest hand-tracking snapshot |

### SpatialAnchor

| Field | Type | Notes |
|-------|------|-------|
| `id` | `str` | Unique anchor identifier |
| `name` | `str` | Human-readable label |
| `position` | `tuple[float, float, float]` | 3D world position (x, y, z) |
| `rotation` | `tuple[float, float, float, float]` | Quaternion (x, y, z, w) |
| `confidence` | `float` | Tracking confidence 0.0-1.0 |
| `persistent` | `bool` | Whether anchor survives session end |

### ARVRManager Methods

| Method | Returns | Description |
|--------|---------|-------------|
| `register_device(device)` | `None` | Add device; `ValueError` on duplicate |
| `create_session(device_id, mode)` | `XRSession` | Start session for device |
| `add_spatial_anchor(session_id, anchor)` | `None` | Attach anchor to session |
| `update_hand_tracking(session_id, data)` | `None` | Update hand-tracking snapshot |
| `get_nearby_anchors(session_id, pos, radius)` | `list[SpatialAnchor]` | Euclidean proximity query |
| `end_session(session_id)` | `None` | Remove session from active tracking |

## Dependencies

- `uuid`, `datetime`, `math` (stdlib)
- `spatial/coordinates` for coordinate primitives

## Constraints

- All data is in-memory; no persistence across process restarts.
- Proximity search is O(n) linear scan over session anchors.
- Quaternion rotation is stored but not validated for unit length.

## Navigation

- [README.md](README.md) | [AGENTS.md](AGENTS.md) | [PAI.md](PAI.md)
- Parent: [spatial](../README.md)
