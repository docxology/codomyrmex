"""
World modeling module for Codomyrmex.

Integrates 4D time-series data with the existing four_d/ submodule to provide
spatial world models for agent trajectory analysis and visualization.

Provides:
    - WorldModel ABC (existing, re-exported)
    - Trajectory4D: a time-series of (x, y, z, t) waypoints
    - TrialSummary: aggregated metrics from an agent trial
    - render_agent_trial: render an agent's trajectory through 4D space-time

The render_agent_trial function produces a structured description of the
agent's journey suitable for consumption by downstream rendering pipelines
(e.g. spatial/rendering/ or spatial/three_d/). It does not depend on any
graphics backend, keeping the spatial world-model layer pure-Python.
"""

from __future__ import annotations

import math
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any

from codomyrmex.spatial.coordinates import Point3D
from codomyrmex.spatial.four_d import QuadrayCoordinate


@dataclass
class TrajectoryPoint4D:
    """A single waypoint in 4D space-time (x, y, z, t).

    Attributes:
        x: Spatial X coordinate.
        y: Spatial Y coordinate.
        z: Spatial Z coordinate.
        t: Temporal coordinate (seconds or arbitrary time unit).
        label: Optional human-readable annotation for the waypoint.
    """

    x: float = 0.0
    y: float = 0.0
    z: float = 0.0
    t: float = 0.0
    label: str = ""

    def to_point3d(self) -> Point3D:
        """Return the spatial (x, y, z) component as a Point3D."""
        return Point3D(self.x, self.y, self.z)

    def to_quadray(self) -> QuadrayCoordinate:
        """Convert the spatial component to a QuadrayCoordinate.

        Uses the standard 3D → quadray mapping:

            a = (x + y + z) / 2   (positive tetrahedral axis)
            b = (-x - y + z) / 2
            c = (-x + y - z) / 2
            d = (x - y - z) / 2

        This maps Cartesian coordinates into the four basis directions of the
        Synergetics quadray system. The temporal component ``t`` is preserved
        separately on the TrajectoryPoint4D itself.
        """
        x, y, z = self.x, self.y, self.z
        return QuadrayCoordinate(
            (x + y + z) / 2.0,
            (-x - y + z) / 2.0,
            (-x + y - z) / 2.0,
            (x - y - z) / 2.0,
        )

    def to_dict(self) -> dict[str, Any]:
        """Serialize to a JSON-safe dictionary."""
        return {
            "x": self.x,
            "y": self.y,
            "z": self.z,
            "t": self.t,
            "label": self.label,
        }


@dataclass
class Trajectory4D:
    """An ordered sequence of 4D waypoints forming an agent trajectory.

    Attributes:
        agent_id: Identifier for the agent that produced this trajectory.
        waypoints: Ordered list of TrajectoryPoint4D (monotonic in ``t``).
        metadata: Optional free-form metadata dictionary.
    """

    agent_id: str = "default"
    waypoints: list[TrajectoryPoint4D] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def add_waypoint(
        self,
        x: float,
        y: float,
        z: float,
        t: float,
        label: str = "",
    ) -> TrajectoryPoint4D:
        """Append a new waypoint and return it.

        Raises:
            ValueError: if ``t`` is earlier than the last waypoint's time.
        """
        if self.waypoints and t < self.waypoints[-1].t:
            msg = (
                f"Waypoint time {t} precedes last waypoint time "
                f"{self.waypoints[-1].t}; trajectory must be time-monotonic."
            )
            raise ValueError(msg)
        point = TrajectoryPoint4D(x=x, y=y, z=z, t=t, label=label)
        self.waypoints.append(point)
        return point

    @property
    def duration(self) -> float:
        """Total temporal span (last.t - first.t), or 0 if fewer than 2 points."""
        if len(self.waypoints) < 2:
            return 0.0
        return self.waypoints[-1].t - self.waypoints[0].t

    @property
    def path_length(self) -> float:
        """Total Euclidean path length through the spatial waypoints."""
        total = 0.0
        for i in range(1, len(self.waypoints)):
            total += (
                self.waypoints[i]
                .to_point3d()
                .distance_to(self.waypoints[i - 1].to_point3d())
            )
        return total

    @property
    def displacement(self) -> float:
        """Straight-line distance from first to last spatial waypoint."""
        if len(self.waypoints) < 2:
            return 0.0
        return (
            self.waypoints[0].to_point3d().distance_to(self.waypoints[-1].to_point3d())
        )

    def to_dict(self) -> dict[str, Any]:
        """Serialize to a JSON-safe dictionary."""
        return {
            "agent_id": self.agent_id,
            "waypoints": [wp.to_dict() for wp in self.waypoints],
            "metadata": dict(self.metadata),
        }


@dataclass
class TrialSummary:
    """Aggregated metrics from an agent trial trajectory.

    Attributes:
        agent_id: Identifier of the agent.
        waypoint_count: Number of waypoints in the trajectory.
        duration: Temporal span of the trajectory.
        path_length: Total Euclidean distance traveled.
        displacement: Straight-line start→end distance.
        average_speed: path_length / duration (0 if duration is 0).
        bounding_box: Dict with min/max x/y/z over all waypoints.
        quadray_coords: List of quadray 4-tuples for each waypoint.
    """

    agent_id: str
    waypoint_count: int
    duration: float
    path_length: float
    displacement: float
    average_speed: float
    bounding_box: dict[str, float]
    quadray_coords: list[tuple[float, float, float, float]]

    def to_dict(self) -> dict[str, Any]:
        """Serialize to a JSON-safe dictionary."""
        return {
            "agent_id": self.agent_id,
            "waypoint_count": self.waypoint_count,
            "duration": self.duration,
            "path_length": self.path_length,
            "displacement": self.displacement,
            "average_speed": self.average_speed,
            "bounding_box": dict(self.bounding_box),
            "quadray_coords": [list(q) for q in self.quadray_coords],
        }


class WorldModel(ABC):
    """Represents a model of the agent's environment."""

    def __init__(self, environment_type: str = "generic"):
        """Initialize the world model."""
        self.environment_type = environment_type
        self.entities: list[Any] = []

    @abstractmethod
    def update(self, perception_data: Any) -> None:
        """Updates the world model based on new perception data."""


def summarize_trial(trajectory: Trajectory4D) -> TrialSummary:
    """Compute summary metrics for a 4D agent trajectory.

    Args:
        trajectory: A Trajectory4D with one or more waypoints.

    Returns:
        TrialSummary with path length, displacement, speed, bounding box,
        and quadray projections of each waypoint.
    """
    wps = trajectory.waypoints
    count = len(wps)
    duration = trajectory.duration
    path_len = trajectory.path_length
    disp = trajectory.displacement
    speed = path_len / duration if duration > 0 else 0.0

    if wps:
        xs = [w.x for w in wps]
        ys = [w.y for w in wps]
        zs = [w.z for w in wps]
        bbox: dict[str, float] = {
            "min_x": min(xs),
            "max_x": max(xs),
            "min_y": min(ys),
            "max_y": max(ys),
            "min_z": min(zs),
            "max_z": max(zs),
        }
    else:
        bbox = {
            "min_x": 0.0,
            "max_x": 0.0,
            "min_y": 0.0,
            "max_y": 0.0,
            "min_z": 0.0,
            "max_z": 0.0,
        }

    quads = [w.to_quadray().coords for w in wps]

    return TrialSummary(
        agent_id=trajectory.agent_id,
        waypoint_count=count,
        duration=duration,
        path_length=path_len,
        displacement=disp,
        average_speed=speed,
        bounding_box=bbox,
        quadray_coords=quads,
    )


def render_agent_trial(
    trajectory: Trajectory4D,
    include_summary: bool = True,
    include_segments: bool = True,
) -> dict[str, Any]:
    """Render an agent's trajectory through 4D space-time.

    Produces a structured, backend-agnostic description of the trajectory
    suitable for consumption by rendering pipelines (spatial/rendering/,
    spatial/three_d/) or direct inspection. The output includes:

    - The full list of waypoints (x, y, z, t, label).
    - Optional segment list: each consecutive pair with its segment length,
      time delta, and instantaneous speed.
    - Optional TrialSummary: aggregated metrics (path length, displacement,
      average speed, bounding box, quadray projections).

    Args:
        trajectory: A Trajectory4D with ordered waypoints.
        include_summary: If True, include the TrialSummary in the output.
        include_segments: If True, include per-segment details.

    Returns:
        dict with keys:
            status: always "success"
            agent_id: the trajectory's agent_id
            waypoint_count: number of waypoints
            waypoints: list of waypoint dicts
            segments: list of segment dicts (if include_segments)
            summary: TrialSummary dict (if include_summary)
    """
    waypoints_out = [wp.to_dict() for wp in trajectory.waypoints]

    result: dict[str, Any] = {
        "status": "success",
        "agent_id": trajectory.agent_id,
        "waypoint_count": len(trajectory.waypoints),
        "waypoints": waypoints_out,
    }

    if include_segments:
        segments: list[dict[str, Any]] = []
        for i in range(1, len(trajectory.waypoints)):
            prev = trajectory.waypoints[i - 1]
            curr = trajectory.waypoints[i]
            seg_len = prev.to_point3d().distance_to(curr.to_point3d())
            dt = curr.t - prev.t
            speed = seg_len / dt if dt > 0 else 0.0
            segments.append(
                {
                    "from_index": i - 1,
                    "to_index": i,
                    "segment_length": seg_len,
                    "time_delta": dt,
                    "instantaneous_speed": speed,
                }
            )
        result["segments"] = segments

    if include_summary:
        summary = summarize_trial(trajectory)
        result["summary"] = summary.to_dict()

    return result


__all__ = [
    "Trajectory4D",
    "TrajectoryPoint4D",
    "TrialSummary",
    "WorldModel",
    "render_agent_trial",
    "summarize_trial",
]
