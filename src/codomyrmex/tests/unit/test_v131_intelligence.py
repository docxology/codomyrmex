"""Tests for v1.3.1 'Autonomous Intelligence' deliverables.

D1: AABB scene graph — spatial queries, ray casting
D2: Gated self-rewrite — verifier + attestation pipeline
D3: Raft consensus — leader election, log replication
D4: Hierarchical FE-loop planner — multi-level active inference
"""

from __future__ import annotations

import pytest

# ---------------------------------------------------------------------------
# D1: AABB Scene Graph
# ---------------------------------------------------------------------------
from codomyrmex.spatial.three_d.engine_3d import Object3D, Vector3D
from codomyrmex.spatial.three_d.scene_graph import AABB, RayHit, SceneGraph, SceneNode


class TestAABB:
    """AABB geometry tests."""

    def test_contains_inside_point(self):
        box = AABB(Vector3D(0, 0, 0), Vector3D(2, 2, 2))
        assert box.contains(Vector3D(1, 1, 1))

    def test_contains_outside_point(self):
        box = AABB(Vector3D(0, 0, 0), Vector3D(2, 2, 2))
        assert not box.contains(Vector3D(3, 1, 1))

    def test_contains_boundary_point(self):
        box = AABB(Vector3D(0, 0, 0), Vector3D(2, 2, 2))
        assert box.contains(Vector3D(0, 0, 0))  # corner
        assert box.contains(Vector3D(2, 2, 2))  # opposite corner

    def test_intersects_overlapping(self):
        a = AABB(Vector3D(0, 0, 0), Vector3D(2, 2, 2))
        b = AABB(Vector3D(1, 1, 1), Vector3D(3, 3, 3))
        assert a.intersects(b)
        assert b.intersects(a)

    def test_intersects_disjoint(self):
        a = AABB(Vector3D(0, 0, 0), Vector3D(1, 1, 1))
        b = AABB(Vector3D(5, 5, 5), Vector3D(6, 6, 6))
        assert not a.intersects(b)

    def test_volume(self):
        box = AABB(Vector3D(0, 0, 0), Vector3D(3, 4, 5))
        assert box.volume() == pytest.approx(60.0)

    def test_center(self):
        box = AABB(Vector3D(0, 0, 0), Vector3D(4, 6, 8))
        c = box.center()
        assert (c.x, c.y, c.z) == pytest.approx((2, 3, 4))

    def test_ray_intersect_hit(self):
        box = AABB(Vector3D(1, 1, 1), Vector3D(3, 3, 3))
        t = box.ray_intersect(Vector3D(0, 2, 2), Vector3D(1, 0, 0))
        assert t is not None
        assert t == pytest.approx(1.0)

    def test_ray_intersect_miss(self):
        box = AABB(Vector3D(1, 1, 1), Vector3D(3, 3, 3))
        t = box.ray_intersect(Vector3D(0, 0, 0), Vector3D(0, 1, 0))
        assert t is None


class TestSceneGraph:
    """Scene graph hierarchy and query tests."""

    def test_add_and_query_point(self):
        sg = SceneGraph()
        n = SceneNode("box", bounds=AABB(Vector3D(0, 0, 0), Vector3D(2, 2, 2)))
        sg.add_node(n)
        hits = sg.query_point(Vector3D(1, 1, 1))
        assert len(hits) == 1
        assert hits[0].name == "box"

    def test_query_point_miss(self):
        sg = SceneGraph()
        n = SceneNode("box", bounds=AABB(Vector3D(0, 0, 0), Vector3D(1, 1, 1)))
        sg.add_node(n)
        assert sg.query_point(Vector3D(5, 5, 5)) == []

    def test_query_region(self):
        sg = SceneGraph()
        sg.add_node(SceneNode("a", bounds=AABB(Vector3D(0, 0, 0), Vector3D(2, 2, 2))))
        sg.add_node(SceneNode("b", bounds=AABB(Vector3D(5, 5, 5), Vector3D(7, 7, 7))))
        region = AABB(Vector3D(1, 1, 1), Vector3D(3, 3, 3))
        hits = sg.query_region(region)
        assert len(hits) == 1
        assert hits[0].name == "a"

    def test_hierarchy_depth(self):
        sg = SceneGraph()
        parent = SceneNode("parent", bounds=AABB(Vector3D(0, 0, 0), Vector3D(10, 10, 10)))
        child = SceneNode("child", bounds=AABB(Vector3D(1, 1, 1), Vector3D(3, 3, 3)))
        sg.add_node(parent)
        sg.add_node(child, parent=parent)
        assert child.depth == 2  # root -> parent -> child
        assert parent.depth == 1  # root -> parent

    def test_remove_node(self):
        sg = SceneGraph()
        n = SceneNode("temp", bounds=AABB(Vector3D(0, 0, 0), Vector3D(1, 1, 1)))
        sg.add_node(n)
        assert sg.node_count == 1
        sg.remove_node(n)
        assert sg.node_count == 0
        assert sg.query_point(Vector3D(0.5, 0.5, 0.5)) == []

    def test_ray_cast(self):
        sg = SceneGraph()
        sg.add_node(SceneNode("near", bounds=AABB(Vector3D(1, -1, -1), Vector3D(3, 1, 1))))
        sg.add_node(SceneNode("far", bounds=AABB(Vector3D(5, -1, -1), Vector3D(7, 1, 1))))
        hits = sg.ray_cast(Vector3D(0, 0, 0), Vector3D(1, 0, 0))
        assert len(hits) == 2
        assert hits[0].node.name == "near"
        assert hits[1].node.name == "far"
        assert hits[0].t < hits[1].t

    def test_empty_scene_queries(self):
        sg = SceneGraph()
        assert sg.query_point(Vector3D(0, 0, 0)) == []
        assert sg.query_region(AABB()) == []
        assert sg.ray_cast(Vector3D(0, 0, 0), Vector3D(1, 0, 0)) == []
        assert sg.node_count == 0

    def test_node_with_object(self):
        obj = Object3D(name="cube")
        n = SceneNode("cube_node", obj=obj, bounds=AABB(Vector3D(0, 0, 0), Vector3D(1, 1, 1)))
        sg = SceneGraph()
        sg.add_node(n)
        found = sg.get_node("cube_node")
        assert found is not None
        assert found.obj is not None
        assert found.obj.name == "cube"


# ---------------------------------------------------------------------------
# D2: Gated Self-Rewrite
# ---------------------------------------------------------------------------

from codomyrmex.formal_verification.gated_rewrite import (
    GateDecision,
    GatedRewriter,
    RewriteGate,
    RewriteProposal,
)


class TestGatedRewrite:
    """Gated self-rewrite pipeline tests."""

    ORIGINAL = "def foo(x, y):\n    return x + y\n"

    def test_approved_rewrite_with_attestation(self):
        """Adding a parameter should pass and produce attestation."""
        modified = "def foo(x, y, z=0):\n    return x + y + z\n"
        rewriter = GatedRewriter()
        decision = rewriter.propose(
            agent_id="agent-1",
            file_path="module.py",
            original=self.ORIGINAL,
            modified=modified,
            rationale="Added optional z parameter",
        )
        assert decision.approved
        assert decision.attestation is not None
        assert decision.attestation.agent_id == "agent-1"

    def test_rejected_rewrite_no_attestation(self):
        """Deleting a public function should be rejected."""
        modified = "# foo removed\n"
        rewriter = GatedRewriter()
        decision = rewriter.propose(
            agent_id="agent-2",
            file_path="module.py",
            original=self.ORIGINAL,
            modified=modified,
        )
        assert not decision.approved
        assert decision.attestation is None

    def test_attestation_verification_round_trip(self):
        """Attestation from approved rewrite should verify."""
        from codomyrmex.collaboration.coordination.attestation import (
            AttestationAuthority,
        )

        authority = AttestationAuthority()
        rewriter = GatedRewriter(authority=authority)
        modified = "def foo(x, y):\n    return x * y\n"
        decision = rewriter.propose(
            agent_id="agent-3",
            file_path="calc.py",
            original=self.ORIGINAL,
            modified=modified,
        )
        assert decision.approved
        assert decision.attestation is not None
        valid = authority.verify(decision.attestation, modified.encode())
        assert valid

    def test_empty_diff_passes(self):
        """Identical source should pass verification."""
        rewriter = GatedRewriter()
        decision = rewriter.propose(
            agent_id="agent-4",
            file_path="noop.py",
            original=self.ORIGINAL,
            modified=self.ORIGINAL,
        )
        assert decision.approved

    def test_parameter_removal_rejected(self):
        """Removing a parameter should fail no_parameter_removal rule."""
        modified = "def foo(x):\n    return x\n"
        rewriter = GatedRewriter()
        decision = rewriter.propose(
            agent_id="agent-5",
            file_path="module.py",
            original=self.ORIGINAL,
            modified=modified,
        )
        assert not decision.approved
        failed_rules = [r.rule_name for r in decision.verification_result.rule_results if not r.passed]
        assert "no_removed_parameters" in failed_rules

    def test_gate_decision_serialization(self):
        """GateDecision.to_dict should be JSON-serializable."""
        import json

        rewriter = GatedRewriter()
        decision = rewriter.propose(
            agent_id="agent-6",
            file_path="test.py",
            original=self.ORIGINAL,
            modified=self.ORIGINAL,
        )
        d = decision.to_dict()
        assert isinstance(json.dumps(d), str)
        assert "approved" in d


# ---------------------------------------------------------------------------
# D3: Raft Consensus
# ---------------------------------------------------------------------------

from codomyrmex.collaboration.coordination.raft import (
    LogEntry,
    RaftCluster,
    RaftNode,
    RaftState,
)


class TestRaftNode:
    """Raft node state machine tests."""

    def test_initial_state_is_follower(self):
        node = RaftNode("n1")
        assert node.state == RaftState.FOLLOWER
        assert node.current_term == 0

    def test_request_vote_grants_on_higher_term(self):
        node = RaftNode("n1")
        resp = node.request_vote(term=1, candidate_id="n2")
        assert resp.vote_granted
        assert node.voted_for == "n2"

    def test_request_vote_rejects_stale_term(self):
        node = RaftNode("n1")
        node.current_term = 5
        resp = node.request_vote(term=3, candidate_id="n2")
        assert not resp.vote_granted

    def test_propose_on_non_leader_raises(self):
        node = RaftNode("n1")
        with pytest.raises(RuntimeError, match="not the leader"):
            node.propose("cmd")

    def test_append_entries_replicates_log(self):
        node = RaftNode("n1")
        entry = LogEntry(term=1, index=1, command="set x=1")
        resp = node.append_entries(
            term=1,
            leader_id="leader",
            entries=[entry],
            prev_log_index=0,
            prev_log_term=0,
            leader_commit=0,
        )
        assert resp.success
        assert len(node.log) == 1
        assert node.log[0].command == "set x=1"


class TestRaftCluster:
    """Raft cluster tests."""

    def test_leader_election_3_nodes(self):
        cluster = RaftCluster(
            node_ids=["n1", "n2", "n3"],
            election_timeout_range=(2, 4),
        )
        leader = cluster.elect_leader(max_rounds=30)
        assert leader is not None
        assert leader.state == RaftState.LEADER

    def test_log_replication(self):
        cluster = RaftCluster(
            node_ids=["n1", "n2", "n3"],
            election_timeout_range=(2, 4),
        )
        cluster.elect_leader(max_rounds=30)
        entry = cluster.propose("set x=1")
        assert entry.committed
        assert cluster.get_committed_log() == [entry]

    def test_multiple_proposals(self):
        cluster = RaftCluster(
            node_ids=["n1", "n2", "n3"],
            election_timeout_range=(2, 4),
        )
        cluster.elect_leader(max_rounds=30)
        e1 = cluster.propose("cmd1")
        e2 = cluster.propose("cmd2")
        e3 = cluster.propose("cmd3")
        assert all(e.committed for e in [e1, e2, e3])
        assert len(cluster.get_committed_log()) == 3

    def test_committed_entry_on_followers(self):
        cluster = RaftCluster(
            node_ids=["n1", "n2", "n3"],
            election_timeout_range=(2, 4),
        )
        leader = cluster.elect_leader(max_rounds=30)
        cluster.propose("data")
        for nid, node in cluster.nodes.items():
            if nid != leader.node_id:
                assert len(node.log) >= 1

    def test_single_node_cluster(self):
        cluster = RaftCluster(
            node_ids=["solo"],
            election_timeout_range=(2, 3),
        )
        leader = cluster.elect_leader(max_rounds=30)
        assert leader.node_id == "solo"
        entry = cluster.propose("lonely")
        assert entry.committed

    def test_empty_cluster_raises(self):
        with pytest.raises(ValueError, match="at least one node"):
            RaftCluster(node_ids=[])

    def test_cluster_serialization(self):
        cluster = RaftCluster(node_ids=["a", "b", "c"], election_timeout_range=(2, 4))
        cluster.elect_leader(max_rounds=30)
        d = cluster.to_dict()
        assert d["cluster_size"] == 3
        assert d["leader"] is not None

    def test_propose_without_leader_raises(self):
        cluster = RaftCluster(
            node_ids=["n1", "n2", "n3"],
            election_timeout_range=(100, 200),  # high timeout = no election
        )
        with pytest.raises(RuntimeError, match="No leader"):
            cluster.propose("impossible")


# ---------------------------------------------------------------------------
# D4: Hierarchical FE-Loop Planner
# ---------------------------------------------------------------------------

from codomyrmex.cerebrum import ActiveInferenceAgent
from codomyrmex.cerebrum.inference.free_energy_loop import FreeEnergyLoop
from codomyrmex.cerebrum.inference.hierarchical_planner import (
    HierarchicalPlan,
    HierarchicalPlanner,
    LevelResult,
    PlanLevel,
)


class TestHierarchicalPlanner:
    """Hierarchical planning tests."""

    @staticmethod
    def _make_agent():
        """Create a default 2-state active inference agent."""
        return ActiveInferenceAgent(
            states=["s0", "s1"],
            observations=["o0", "o1"],
            actions=["a0", "a1"],
        )

    def test_two_level_planning(self):
        planner = HierarchicalPlanner(
            levels=[
                PlanLevel("strategic", FreeEnergyLoop(self._make_agent(), max_steps=10)),
                PlanLevel("tactical", FreeEnergyLoop(self._make_agent(), max_steps=10)),
            ],
        )
        plan = planner.plan({"strategic": {"sensor": 0.5}})
        assert len(plan.levels) == 2
        assert plan.total_steps > 0

    def test_three_level_chaining(self):
        planner = HierarchicalPlanner(
            levels=[
                PlanLevel("high", FreeEnergyLoop(self._make_agent(), max_steps=5)),
                PlanLevel("mid", FreeEnergyLoop(self._make_agent(), max_steps=5)),
                PlanLevel("low", FreeEnergyLoop(self._make_agent(), max_steps=5)),
            ],
        )
        plan = planner.plan({})
        assert len(plan.levels) == 3
        # Each level after the first should have received parent_action
        for lv in plan.levels[1:]:
            assert lv.output_action is not None

    def test_single_level_fallback(self):
        planner = HierarchicalPlanner(
            levels=[
                PlanLevel("only", FreeEnergyLoop(self._make_agent(), max_steps=10)),
            ],
        )
        plan = planner.plan({"only": {"sensor": 0.3}})
        assert len(plan.levels) == 1
        assert plan.total_steps > 0

    def test_max_steps_budget(self):
        planner = HierarchicalPlanner(
            levels=[
                PlanLevel("top", FreeEnergyLoop(self._make_agent(), max_steps=100)),
                PlanLevel("bot", FreeEnergyLoop(self._make_agent(), max_steps=100)),
            ],
            max_total_steps=5,  # very tight budget
        )
        plan = planner.plan({})
        assert plan.total_steps <= 5

    def test_plan_serialization(self):
        import json

        planner = HierarchicalPlanner(
            levels=[
                PlanLevel("x", FreeEnergyLoop(self._make_agent(), max_steps=5)),
            ],
        )
        plan = planner.plan({})
        d = plan.to_dict()
        assert isinstance(json.dumps(d), str)
        assert "levels" in d

    def test_empty_levels_raises(self):
        with pytest.raises(ValueError, match="At least one"):
            HierarchicalPlanner(levels=[])
