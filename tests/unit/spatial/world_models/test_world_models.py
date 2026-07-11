"""Tests for the spatial world_models module (R1: 4D time-series integration).

Covers TrajectoryPoint4D, Trajectory4D, TrialSummary, summarize_trial,
and render_agent_trial — as well as the spatial_render_agent_trial MCP tool.
"""

from __future__ import annotations

import math

import pytest

from codomyrmex.spatial.coordinates import Point3D
from codomyrmex.spatial.four_d import QuadrayCoordinate
from codomyrmex.spatial.world_models import (
    Trajectory4D,
    TrajectoryPoint4D,
    TrialSummary,
    WorldModel,
    render_agent_trial,
    summarize_trial,
)


@pytest.mark.unit
class TestTrajectoryPoint4D:
    """Tests for the TrajectoryPoint4D dataclass."""

    def test_default_construction(self):
        """Default point is origin at t=0 with empty label."""
        pt = TrajectoryPoint4D()
        assert pt.x == 0.0
        assert pt.y == 0.0
        assert pt.z == 0.0
        assert pt.t == 0.0
        assert pt.label == ""

    def test_custom_construction(self):
        """Point accepts explicit coordinates and time."""
        pt = TrajectoryPoint4D(1.0, 2.0, 3.0, 4.5, label="start")
        assert pt.x == 1.0
        assert pt.y == 2.0
        assert pt.z == 3.0
        assert pt.t == 4.5
        assert pt.label == "start"

    def test_to_point3d(self):
        """to_point3d returns correct spatial component."""
        pt = TrajectoryPoint4D(5.0, 6.0, 7.0, 99.0)
        p3d = pt.to_point3d()
        assert isinstance(p3d, Point3D)
        assert p3d.x == 5.0
        assert p3d.y == 6.0
        assert p3d.z == 7.0

    def test_to_quadray_origin(self):
        """Origin maps to all-zero quadray."""
        pt = TrajectoryPoint4D(0.0, 0.0, 0.0, 0.0)
        quad = pt.to_quadray()
        assert isinstance(quad, QuadrayCoordinate)
        assert quad.coords == (0.0, 0.0, 0.0, 0.0)

    def test_to_quadray_known_point(self):
        """Cartesian (1,1,0) maps to known quadray values."""
        pt = TrajectoryPoint4D(1.0, 1.0, 0.0, 0.0)
        quad = pt.to_quadray()
        # a = (1+1+0)/2 = 1.0
        # b = (-1-1+0)/2 = -1.0
        # c = (-1+1-0)/2 = 0.0
        # d = (1-1-0)/2 = 0.0
        assert quad.coords == pytest.approx((1.0, -1.0, 0.0, 0.0))

    def test_to_dict(self):
        """to_dict returns all fields."""
        pt = TrajectoryPoint4D(1.0, 2.0, 3.0, 4.0, label="wp1")
        d = pt.to_dict()
        assert d["x"] == 1.0
        assert d["y"] == 2.0
        assert d["z"] == 3.0
        assert d["t"] == 4.0
        assert d["label"] == "wp1"


@pytest.mark.unit
class TestTrajectory4D:
    """Tests for the Trajectory4D class."""

    def test_default_construction(self):
        """Default trajectory has empty waypoints and default agent_id."""
        traj = Trajectory4D()
        assert traj.agent_id == "default"
        assert traj.waypoints == []
        assert traj.metadata == {}

    def test_add_waypoint(self):
        """add_waypoint appends a point and returns it."""
        traj = Trajectory4D(agent_id="bot-1")
        wp = traj.add_waypoint(1.0, 2.0, 3.0, 0.5, label="here")
        assert wp.x == 1.0
        assert wp.label == "here"
        assert len(traj.waypoints) == 1
        assert traj.waypoints[0] is wp

    def test_add_waypoint_time_monotonic_violation(self):
        """Adding a waypoint with t earlier than the last raises ValueError."""
        traj = Trajectory4D()
        traj.add_waypoint(0.0, 0.0, 0.0, 10.0)
        with pytest.raises(ValueError, match="precedes last waypoint"):
            traj.add_waypoint(1.0, 1.0, 1.0, 5.0)

    def test_add_waypoint_equal_time_is_allowed(self):
        """Adding a waypoint with equal t is allowed (not strictly monotonic)."""
        traj = Trajectory4D()
        traj.add_waypoint(0.0, 0.0, 0.0, 5.0)
        traj.add_waypoint(1.0, 1.0, 1.0, 5.0)  # same time, should not raise
        assert len(traj.waypoints) == 2

    def test_duration_empty(self):
        """Duration of empty trajectory is 0."""
        traj = Trajectory4D()
        assert traj.duration == 0.0

    def test_duration_single_point(self):
        """Duration with one waypoint is 0."""
        traj = Trajectory4D()
        traj.add_waypoint(0.0, 0.0, 0.0, 5.0)
        assert traj.duration == 0.0

    def test_duration_two_points(self):
        """Duration is last.t - first.t."""
        traj = Trajectory4D()
        traj.add_waypoint(0.0, 0.0, 0.0, 2.0)
        traj.add_waypoint(1.0, 1.0, 1.0, 7.0)
        assert traj.duration == pytest.approx(5.0)

    def test_path_length_empty(self):
        """Path length of empty trajectory is 0."""
        traj = Trajectory4D()
        assert traj.path_length == 0.0

    def test_path_length_known(self):
        """Path length sums consecutive Euclidean distances."""
        traj = Trajectory4D()
        traj.add_waypoint(0.0, 0.0, 0.0, 0.0)
        traj.add_waypoint(3.0, 4.0, 0.0, 1.0)  # distance = 5
        traj.add_waypoint(3.0, 4.0, 12.0, 2.0)  # distance = 12
        assert traj.path_length == pytest.approx(17.0)

    def test_displacement_empty(self):
        """Displacement with no waypoints is 0."""
        traj = Trajectory4D()
        assert traj.displacement == 0.0

    def test_displacement_known(self):
        """Displacement is straight-line start→end distance."""
        traj = Trajectory4D()
        traj.add_waypoint(0.0, 0.0, 0.0, 0.0)
        traj.add_waypoint(3.0, 4.0, 0.0, 1.0)
        assert traj.displacement == pytest.approx(5.0)

    def test_to_dict(self):
        """to_dict serializes agent_id, waypoints, and metadata."""
        traj = Trajectory4D(agent_id="alpha", metadata={"env": "grid"})
        traj.add_waypoint(1.0, 2.0, 3.0, 0.0, label="start")
        d = traj.to_dict()
        assert d["agent_id"] == "alpha"
        assert d["metadata"] == {"env": "grid"}
        assert len(d["waypoints"]) == 1
        assert d["waypoints"][0]["x"] == 1.0


@pytest.mark.unit
class TestSummarizeTrial:
    """Tests for the summarize_trial function."""

    def test_empty_trajectory(self):
        """Summarizing an empty trajectory returns zeroed metrics."""
        traj = Trajectory4D(agent_id="empty")
        summary = summarize_trial(traj)
        assert isinstance(summary, TrialSummary)
        assert summary.agent_id == "empty"
        assert summary.waypoint_count == 0
        assert summary.duration == 0.0
        assert summary.path_length == 0.0
        assert summary.displacement == 0.0
        assert summary.average_speed == 0.0
        assert summary.quadray_coords == []

    def test_single_waypoint(self):
        """Single waypoint: duration 0, speed 0, but bbox and quadray present."""
        traj = Trajectory4D()
        traj.add_waypoint(1.0, 2.0, 3.0, 5.0)
        summary = summarize_trial(traj)
        assert summary.waypoint_count == 1
        assert summary.duration == 0.0
        assert summary.average_speed == 0.0
        assert summary.bounding_box["min_x"] == 1.0
        assert summary.bounding_box["max_x"] == 1.0
        assert len(summary.quadray_coords) == 1

    def test_known_trajectory(self):
        """Verify path_length, displacement, and speed for a known trajectory."""
        traj = Trajectory4D(agent_id="bot")
        traj.add_waypoint(0.0, 0.0, 0.0, 0.0)
        traj.add_waypoint(3.0, 4.0, 0.0, 1.0)  # dist=5, dt=1
        traj.add_waypoint(3.0, 4.0, 0.0, 3.0)  # dist=0, dt=2
        summary = summarize_trial(traj)
        assert summary.waypoint_count == 3
        assert summary.duration == pytest.approx(3.0)
        assert summary.path_length == pytest.approx(5.0)
        assert summary.displacement == pytest.approx(5.0)
        # average_speed = path_length / duration = 5/3
        assert summary.average_speed == pytest.approx(5.0 / 3.0)
        assert summary.bounding_box["min_z"] == 0.0
        assert summary.bounding_box["max_z"] == 0.0
        assert len(summary.quadray_coords) == 3

    def test_bounding_box(self):
        """Bounding box spans min/max across all waypoints."""
        traj = Trajectory4D()
        traj.add_waypoint(-1.0, -2.0, -3.0, 0.0)
        traj.add_waypoint(5.0, 6.0, 7.0, 1.0)
        traj.add_waypoint(0.0, 0.0, 0.0, 2.0)
        summary = summarize_trial(traj)
        assert summary.bounding_box["min_x"] == -1.0
        assert summary.bounding_box["max_x"] == 5.0
        assert summary.bounding_box["min_y"] == -2.0
        assert summary.bounding_box["max_y"] == 6.0
        assert summary.bounding_box["min_z"] == -3.0
        assert summary.bounding_box["max_z"] == 7.0

    def test_summary_to_dict(self):
        """to_dict produces JSON-safe structures."""
        traj = Trajectory4D(agent_id="d1")
        traj.add_waypoint(1.0, 0.0, 0.0, 0.0)
        summary = summarize_trial(traj)
        d = summary.to_dict()
        assert d["agent_id"] == "d1"
        assert d["waypoint_count"] == 1
        assert isinstance(d["quadray_coords"], list)
        assert isinstance(d["quadray_coords"][0], list)


@pytest.mark.unit
class TestRenderAgentTrial:
    """Tests for the render_agent_trial function."""

    def test_empty_trajectory(self):
        """Rendering an empty trajectory still returns success with zeroed counts."""
        traj = Trajectory4D(agent_id="nobody")
        result = render_agent_trial(traj)
        assert result["status"] == "success"
        assert result["agent_id"] == "nobody"
        assert result["waypoint_count"] == 0
        assert result["waypoints"] == []

    def test_basic_render(self):
        """Rendering a trajectory with 3 waypoints produces correct structure."""
        traj = Trajectory4D(agent_id="bot-7")
        traj.add_waypoint(0.0, 0.0, 0.0, 0.0, label="start")
        traj.add_waypoint(1.0, 0.0, 0.0, 1.0)
        traj.add_waypoint(1.0, 1.0, 0.0, 2.0, label="end")
        result = render_agent_trial(traj)
        assert result["status"] == "success"
        assert result["agent_id"] == "bot-7"
        assert result["waypoint_count"] == 3
        assert len(result["waypoints"]) == 3
        assert result["waypoints"][0]["label"] == "start"
        assert result["waypoints"][2]["label"] == "end"

    def test_segments_included(self):
        """Segments are included by default and have correct metrics."""
        traj = Trajectory4D()
        traj.add_waypoint(0.0, 0.0, 0.0, 0.0)
        traj.add_waypoint(3.0, 4.0, 0.0, 1.0)  # dist=5, dt=1, speed=5
        result = render_agent_trial(traj)
        assert "segments" in result
        assert len(result["segments"]) == 1
        seg = result["segments"][0]
        assert seg["from_index"] == 0
        assert seg["to_index"] == 1
        assert seg["segment_length"] == pytest.approx(5.0)
        assert seg["time_delta"] == pytest.approx(1.0)
        assert seg["instantaneous_speed"] == pytest.approx(5.0)

    def test_segments_excluded(self):
        """Setting include_segments=False omits segments."""
        traj = Trajectory4D()
        traj.add_waypoint(0.0, 0.0, 0.0, 0.0)
        traj.add_waypoint(1.0, 1.0, 1.0, 1.0)
        result = render_agent_trial(traj, include_segments=False)
        assert "segments" not in result

    def test_summary_included(self):
        """Summary is included by default with correct metrics."""
        traj = Trajectory4D(agent_id="s1")
        traj.add_waypoint(0.0, 0.0, 0.0, 0.0)
        traj.add_waypoint(0.0, 0.0, 10.0, 5.0)  # dist=10, dt=5
        result = render_agent_trial(traj)
        assert "summary" in result
        summary = result["summary"]
        assert summary["agent_id"] == "s1"
        assert summary["path_length"] == pytest.approx(10.0)
        assert summary["duration"] == pytest.approx(5.0)
        assert summary["average_speed"] == pytest.approx(2.0)
        assert len(summary["quadray_coords"]) == 2

    def test_summary_excluded(self):
        """Setting include_summary=False omits the summary."""
        traj = Trajectory4D()
        traj.add_waypoint(0.0, 0.0, 0.0, 0.0)
        result = render_agent_trial(traj, include_summary=False)
        assert "summary" not in result

    def test_zero_duration_speed_is_zero(self):
        """A segment with dt=0 should yield instantaneous_speed=0, not NaN."""
        traj = Trajectory4D()
        traj.add_waypoint(0.0, 0.0, 0.0, 5.0)
        traj.add_waypoint(1.0, 1.0, 1.0, 5.0)  # dt=0
        result = render_agent_trial(traj)
        seg = result["segments"][0]
        assert seg["instantaneous_speed"] == 0.0
        assert not math.isnan(seg["instantaneous_speed"])

    def test_waypoint_dict_structure(self):
        """Each waypoint dict has x, y, z, t, label keys."""
        traj = Trajectory4D()
        traj.add_waypoint(1.5, 2.5, 3.5, 4.5, label="mid")
        result = render_agent_trial(traj)
        wp = result["waypoints"][0]
        assert set(wp.keys()) == {"x", "y", "z", "t", "label"}
        assert wp["x"] == 1.5
        assert wp["label"] == "mid"


@pytest.mark.unit
class TestWorldModelABC:
    """Tests that WorldModel ABC is still properly enforced (regression)."""

    def test_cannot_instantiate_directly(self):
        """WorldModel is abstract and cannot be instantiated directly."""
        with pytest.raises(TypeError):
            WorldModel()

    def test_subclass_must_implement_update(self):
        """Subclass missing update() raises TypeError."""

        class IncompleteModel(WorldModel):
            pass

        with pytest.raises(TypeError):
            IncompleteModel()

    def test_concrete_subclass_works(self):
        """A concrete subclass implementing update() instantiates and works."""

        class ConcreteModel(WorldModel):
            def update(self, perception_data):
                self.entities.append(perception_data)

        model = ConcreteModel(environment_type="test_env")
        assert model.environment_type == "test_env"
        assert model.entities == []
        model.update({"sensor": "lidar", "distance": 5.0})
        assert len(model.entities) == 1
        assert model.entities[0]["sensor"] == "lidar"


@pytest.mark.unit
class TestSpatialRenderAgentTrialMCPTool:
    """Tests for the spatial_render_agent_trial MCP tool."""

    def test_basic_mcp_tool_call(self):
        """The MCP tool returns structured trajectory data."""
        from codomyrmex.spatial.mcp_tools import spatial_render_agent_trial

        result = spatial_render_agent_trial(
            agent_id="mcp-bot",
            waypoints=[
                {"x": 0.0, "y": 0.0, "z": 0.0, "t": 0.0, "label": "start"},
                {"x": 3.0, "y": 4.0, "z": 0.0, "t": 1.0, "label": "end"},
            ],
        )
        assert result["status"] == "success"
        assert result["agent_id"] == "mcp-bot"
        assert result["waypoint_count"] == 2
        assert len(result["segments"]) == 1
        assert result["segments"][0]["segment_length"] == pytest.approx(5.0)
        assert "summary" in result

    def test_mcp_tool_empty_waypoints(self):
        """MCP tool with no waypoints returns empty trajectory."""
        from codomyrmex.spatial.mcp_tools import spatial_render_agent_trial

        result = spatial_render_agent_trial(agent_id="idle")
        assert result["status"] == "success"
        assert result["waypoint_count"] == 0
        assert result["waypoints"] == []

    def test_mcp_tool_default_agent_id(self):
        """MCP tool defaults agent_id to 'default'."""
        from codomyrmex.spatial.mcp_tools import spatial_render_agent_trial

        result = spatial_render_agent_trial(waypoints=[])
        assert result["agent_id"] == "default"

    def test_mcp_tool_exclude_summary_and_segments(self):
        """MCP tool respects include_summary and include_segments flags."""
        from codomyrmex.spatial.mcp_tools import spatial_render_agent_trial

        result = spatial_render_agent_trial(
            waypoints=[{"x": 1.0, "y": 0.0, "z": 0.0, "t": 0.0}],
            include_summary=False,
            include_segments=False,
        )
        assert "summary" not in result
        assert "segments" not in result

    def test_mcp_tool_has_mcp_metadata(self):
        """The tool function has _mcp_tool metadata attached."""
        from codomyrmex.spatial.mcp_tools import spatial_render_agent_trial

        assert hasattr(spatial_render_agent_trial, "_mcp_tool")
        meta = spatial_render_agent_trial._mcp_tool
        assert meta["category"] == "spatial"
        assert "render" in meta["description"].lower()
        assert meta["name"].startswith("codomyrmex.")

    def test_mcp_tool_waypoints_without_label(self):
        """MCP tool handles waypoints that omit the label key."""
        from codomyrmex.spatial.mcp_tools import spatial_render_agent_trial

        result = spatial_render_agent_trial(
            waypoints=[
                {"x": 0.0, "y": 0.0, "z": 0.0, "t": 0.0},
                {"x": 1.0, "y": 1.0, "z": 1.0, "t": 1.0},
            ],
        )
        assert result["status"] == "success"
        assert result["waypoints"][0]["label"] == ""

    def test_mcp_tool_time_violation_returns_error(self):
        """MCP tool returns error status when waypoints violate time monotonicity."""
        from codomyrmex.spatial.mcp_tools import spatial_render_agent_trial

        result = spatial_render_agent_trial(
            waypoints=[
                {"x": 0.0, "y": 0.0, "z": 0.0, "t": 10.0},
                {"x": 1.0, "y": 1.0, "z": 1.0, "t": 5.0},
            ],
        )
        assert result["status"] == "error"
        assert "precedes" in result["message"]
