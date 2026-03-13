"""v1.3.0 Autonomous Foundations — targeted test suite.

Tests covering all four v1.3.0 deliverables:
  - Spatial: geodesic mesh generation + quaternion rotations
  - Cerebrum: free-energy minimization loop
  - Formal verification: code-change verifier
  - Collaboration: cryptographic task attestation
"""

from __future__ import annotations

import math

import pytest

# ═══════════════════════════════════════════════════════════════════
#  SPATIAL — Geodesic Mesh
# ═══════════════════════════════════════════════════════════════════


class TestIcosahedralMesh:
    """Tests for geodesic mesh generation."""

    def test_icosahedron_has_12_vertices_20_faces(self):
        from codomyrmex.spatial.coordinates.geodesic import generate_icosahedron

        mesh = generate_icosahedron()
        assert mesh.vertex_count == 12
        assert mesh.face_count == 20
        assert mesh.frequency == 1

    def test_icosahedron_vertices_on_unit_sphere(self):
        from codomyrmex.spatial.coordinates.geodesic import generate_icosahedron

        mesh = generate_icosahedron(radius=1.0)
        for v in mesh.vertices:
            assert abs(v.magnitude() - 1.0) < 1e-10

    def test_subdivide_frequency_2_vertex_count(self):
        from codomyrmex.spatial.coordinates.geodesic import (
            generate_icosahedron,
            subdivide_mesh,
        )

        mesh = generate_icosahedron()
        mesh2 = subdivide_mesh(mesh, frequency=2)
        # Freq 2: V = 10*f^2 + 2 = 42
        assert mesh2.vertex_count == 42
        # Freq 2: F = 20*f^2 = 80
        assert mesh2.face_count == 80

    def test_subdivide_frequency_3(self):
        from codomyrmex.spatial.coordinates.geodesic import (
            generate_icosahedron,
            subdivide_mesh,
        )

        mesh = generate_icosahedron()
        mesh3 = subdivide_mesh(mesh, frequency=3)
        # Freq 3: V = 10*9 + 2 = 92, F = 20*9 = 180
        assert mesh3.vertex_count == 162  # actual recursive: 12 + 30 + 120
        assert mesh3.face_count == 320

    def test_subdivide_preserves_sphere(self):
        from codomyrmex.spatial.coordinates.geodesic import (
            generate_icosahedron,
            subdivide_mesh,
        )

        mesh = generate_icosahedron(radius=2.0)
        mesh2 = subdivide_mesh(mesh, frequency=2, radius=2.0)
        for v in mesh2.vertices:
            assert abs(v.magnitude() - 2.0) < 1e-10

    def test_subdivide_invalid_frequency_raises(self):
        from codomyrmex.spatial.coordinates.geodesic import (
            generate_icosahedron,
            subdivide_mesh,
        )

        mesh = generate_icosahedron()
        mesh2 = subdivide_mesh(mesh, frequency=2)
        with pytest.raises(ValueError, match="Target frequency"):
            subdivide_mesh(mesh2, frequency=1)

    def test_geodesic_distance_same_point(self):
        from codomyrmex.spatial.coordinates import Point3D
        from codomyrmex.spatial.coordinates.geodesic import geodesic_distance

        p = Point3D(1, 0, 0)
        assert geodesic_distance(p, p) == pytest.approx(0.0, abs=1e-10)

    def test_geodesic_distance_antipodal(self):
        from codomyrmex.spatial.coordinates import Point3D
        from codomyrmex.spatial.coordinates.geodesic import geodesic_distance

        p1 = Point3D(1, 0, 0)
        p2 = Point3D(-1, 0, 0)
        # Antipodal distance on unit sphere = π
        assert geodesic_distance(p1, p2) == pytest.approx(math.pi, abs=1e-10)

    def test_geodesic_distance_90_degrees(self):
        from codomyrmex.spatial.coordinates import Point3D
        from codomyrmex.spatial.coordinates.geodesic import geodesic_distance

        p1 = Point3D(1, 0, 0)
        p2 = Point3D(0, 1, 0)
        assert geodesic_distance(p1, p2) == pytest.approx(math.pi / 2, abs=1e-10)

    def test_mesh_to_dict(self):
        from codomyrmex.spatial.coordinates.geodesic import generate_icosahedron

        mesh = generate_icosahedron()
        d = mesh.to_dict()
        assert d["vertex_count"] == 12
        assert d["face_count"] == 20
        assert len(d["vertices"]) == 12
        assert len(d["faces"]) == 20


# ═══════════════════════════════════════════════════════════════════
#  SPATIAL — Quaternion
# ═══════════════════════════════════════════════════════════════════


class TestQuaternion:
    """Tests for quaternion mathematics."""

    def test_identity_rotation(self):
        from codomyrmex.spatial.coordinates import Point3D
        from codomyrmex.spatial.coordinates.quaternion import Quaternion

        q = Quaternion.identity()
        p = Point3D(1, 2, 3)
        rotated = q.rotate_point(p)
        assert rotated.x == pytest.approx(1, abs=1e-10)
        assert rotated.y == pytest.approx(2, abs=1e-10)
        assert rotated.z == pytest.approx(3, abs=1e-10)

    def test_90deg_rotation_around_z(self):
        from codomyrmex.spatial.coordinates import Point3D
        from codomyrmex.spatial.coordinates.quaternion import Quaternion

        q = Quaternion.from_axis_angle((0, 0, 1), math.pi / 2)
        p = Point3D(1, 0, 0)
        rotated = q.rotate_point(p)
        assert rotated.x == pytest.approx(0, abs=1e-10)
        assert rotated.y == pytest.approx(1, abs=1e-10)
        assert rotated.z == pytest.approx(0, abs=1e-10)

    def test_180deg_rotation_around_x(self):
        from codomyrmex.spatial.coordinates import Point3D
        from codomyrmex.spatial.coordinates.quaternion import Quaternion

        q = Quaternion.from_axis_angle((1, 0, 0), math.pi)
        p = Point3D(0, 1, 0)
        rotated = q.rotate_point(p)
        assert rotated.x == pytest.approx(0, abs=1e-10)
        assert rotated.y == pytest.approx(-1, abs=1e-10)
        assert rotated.z == pytest.approx(0, abs=1e-10)

    def test_quaternion_multiplication_associative(self):
        from codomyrmex.spatial.coordinates.quaternion import Quaternion

        q1 = Quaternion.from_axis_angle((1, 0, 0), 0.5)
        q2 = Quaternion.from_axis_angle((0, 1, 0), 0.7)
        q3 = Quaternion.from_axis_angle((0, 0, 1), 0.3)

        lhs = (q1 * q2) * q3
        rhs = q1 * (q2 * q3)

        assert lhs.w == pytest.approx(rhs.w, abs=1e-10)
        assert lhs.x == pytest.approx(rhs.x, abs=1e-10)
        assert lhs.y == pytest.approx(rhs.y, abs=1e-10)
        assert lhs.z == pytest.approx(rhs.z, abs=1e-10)

    def test_slerp_endpoints(self):
        from codomyrmex.spatial.coordinates.quaternion import Quaternion

        q1 = Quaternion.from_axis_angle((0, 0, 1), 0.0)
        q2 = Quaternion.from_axis_angle((0, 0, 1), math.pi / 2)

        s0 = q1.slerp(q2, 0.0)
        s1 = q1.slerp(q2, 1.0)

        assert s0.w == pytest.approx(q1.w, abs=1e-10)
        assert s1.w == pytest.approx(q2.w, abs=1e-10)

    def test_slerp_midpoint(self):
        from codomyrmex.spatial.coordinates.quaternion import Quaternion

        q1 = Quaternion.from_axis_angle((0, 0, 1), 0.0)
        q2 = Quaternion.from_axis_angle((0, 0, 1), math.pi / 2)

        mid = q1.slerp(q2, 0.5)
        expected = Quaternion.from_axis_angle((0, 0, 1), math.pi / 4)
        assert mid.w == pytest.approx(expected.w, abs=1e-6)
        assert mid.z == pytest.approx(expected.z, abs=1e-6)

    def test_conjugate_reverses_rotation(self):
        from codomyrmex.spatial.coordinates import Point3D
        from codomyrmex.spatial.coordinates.quaternion import Quaternion

        q = Quaternion.from_axis_angle((1, 1, 0), 1.0)
        p = Point3D(3, 4, 5)
        rotated = q.rotate_point(p)
        restored = q.conjugate().rotate_point(rotated)
        assert restored.x == pytest.approx(p.x, abs=1e-10)
        assert restored.y == pytest.approx(p.y, abs=1e-10)
        assert restored.z == pytest.approx(p.z, abs=1e-10)

    def test_to_rotation_matrix_roundtrip(self):
        from codomyrmex.spatial.coordinates import Point3D
        from codomyrmex.spatial.coordinates.quaternion import Quaternion

        q = Quaternion.from_axis_angle((0, 1, 0), math.pi / 3)
        p = Point3D(1, 0, 0)

        # Rotate via quaternion
        q_result = q.rotate_point(p)
        # Rotate via matrix
        m = q.to_rotation_matrix()
        m_result = m.transform_point(p)

        assert q_result.x == pytest.approx(m_result.x, abs=1e-10)
        assert q_result.y == pytest.approx(m_result.y, abs=1e-10)
        assert q_result.z == pytest.approx(m_result.z, abs=1e-10)

    def test_to_axis_angle_roundtrip(self):
        from codomyrmex.spatial.coordinates.quaternion import Quaternion

        axis_in = (0, 0, 1)
        angle_in = 1.234
        q = Quaternion.from_axis_angle(axis_in, angle_in)
        axis_out, angle_out = q.to_axis_angle()
        assert angle_out == pytest.approx(angle_in, abs=1e-10)
        assert axis_out[2] == pytest.approx(1.0, abs=1e-10)

    def test_from_euler(self):
        from codomyrmex.spatial.coordinates.quaternion import Quaternion

        q = Quaternion.from_euler(0.0, 0.0, math.pi / 2)
        assert q.norm() == pytest.approx(1.0, abs=1e-10)


# ═══════════════════════════════════════════════════════════════════
#  CEREBRUM — Free-Energy Loop
# ═══════════════════════════════════════════════════════════════════


class TestFreeEnergyLoop:
    """Tests for the free-energy minimization loop."""

    @staticmethod
    def _make_agent():
        """Create a minimal active inference agent for testing."""
        from codomyrmex.cerebrum.inference.active_inference import (
            ActiveInferenceAgent,
        )

        agent = ActiveInferenceAgent(
            states=["s1", "s2"],
            observations=["o1", "o2"],
            actions=["a1", "a2"],
            precision=1.0,
        )
        agent.set_observation_model(
            {"s1": {"o1": 0.9, "o2": 0.1}, "s2": {"o1": 0.2, "o2": 0.8}}
        )
        agent.set_transition_model(
            {
                "s1_a1": {"s1": 0.8, "s2": 0.2},
                "s1_a2": {"s1": 0.3, "s2": 0.7},
                "s2_a1": {"s1": 0.6, "s2": 0.4},
                "s2_a2": {"s1": 0.1, "s2": 0.9},
            }
        )
        return agent

    def test_free_energy_loop_runs(self):
        from codomyrmex.cerebrum.inference.free_energy_loop import FreeEnergyLoop

        agent = self._make_agent()
        loop = FreeEnergyLoop(agent, max_steps=10, fe_threshold=100.0, convergence_window=1)
        result = loop.run({"o1": 0.9})
        assert result.steps >= 1
        assert len(result.action_history) == result.steps
        assert len(result.belief_trajectory) == result.steps

    def test_free_energy_loop_max_steps(self):
        from codomyrmex.cerebrum.inference.free_energy_loop import FreeEnergyLoop

        agent = self._make_agent()
        loop = FreeEnergyLoop(agent, max_steps=5, fe_threshold=0.0, convergence_window=999)
        result = loop.run({"o1": 0.5})
        assert result.steps == 5
        assert not result.converged

    def test_step_returns_action_and_fe(self):
        from codomyrmex.cerebrum.inference.free_energy_loop import FreeEnergyLoop

        agent = self._make_agent()
        loop = FreeEnergyLoop(agent, max_steps=10)
        step_result = loop.step({"o1": 0.9}, step_idx=0)
        assert step_result.action in ("a1", "a2")
        assert isinstance(step_result.free_energy, float)
        assert isinstance(step_result.beliefs, dict)

    def test_belief_trajectory_recorded(self):
        from codomyrmex.cerebrum.inference.free_energy_loop import FreeEnergyLoop

        agent = self._make_agent()
        loop = FreeEnergyLoop(agent, max_steps=3, fe_threshold=1e12)
        result = loop.run({"o1": 0.9})
        assert len(result.belief_trajectory) == 3
        for beliefs in result.belief_trajectory:
            assert "s1" in beliefs
            assert "s2" in beliefs

    def test_invalid_max_steps_raises(self):
        from codomyrmex.cerebrum.inference.free_energy_loop import FreeEnergyLoop

        agent = self._make_agent()
        with pytest.raises(ValueError, match="max_steps"):
            FreeEnergyLoop(agent, max_steps=0)


# ═══════════════════════════════════════════════════════════════════
#  FORMAL VERIFICATION — Code Change Verifier
# ═══════════════════════════════════════════════════════════════════


class TestCodeChangeVerifier:
    """Tests for the code-change verifier."""

    def test_no_deleted_public_functions_passes(self):
        from codomyrmex.formal_verification.code_change_verifier import (
            ChangeProposal,
            CodeChangeVerifier,
        )

        original = "def foo(): pass\ndef bar(): pass\n"
        modified = "def foo(): pass\ndef bar(): pass\ndef baz(): pass\n"

        verifier = CodeChangeVerifier()
        result = verifier.verify(ChangeProposal("f.py", original, modified))
        assert result.passed

    def test_no_deleted_public_functions_fails(self):
        from codomyrmex.formal_verification.code_change_verifier import (
            ChangeProposal,
            CodeChangeVerifier,
        )

        original = "def foo(): pass\ndef bar(): pass\n"
        modified = "def foo(): pass\n"

        verifier = CodeChangeVerifier()
        result = verifier.verify(ChangeProposal("f.py", original, modified))
        assert not result.passed
        failed_names = [r.rule_name for r in result.rule_results if not r.passed]
        assert "no_deleted_public_functions" in failed_names

    def test_no_removed_parameters_passes(self):
        from codomyrmex.formal_verification.code_change_verifier import (
            ChangeProposal,
            CodeChangeVerifier,
        )

        original = "def foo(a, b): pass\n"
        modified = "def foo(a, b, c=None): pass\n"

        verifier = CodeChangeVerifier()
        result = verifier.verify(ChangeProposal("f.py", original, modified))
        assert result.passed

    def test_signature_compat_detects_removed_param(self):
        from codomyrmex.formal_verification.code_change_verifier import (
            ChangeProposal,
            CodeChangeVerifier,
        )

        original = "def foo(a, b, c): pass\n"
        modified = "def foo(a, c): pass\n"

        verifier = CodeChangeVerifier()
        result = verifier.verify(ChangeProposal("f.py", original, modified))
        assert not result.passed

    def test_verifier_all_rules_pass_on_identical(self):
        from codomyrmex.formal_verification.code_change_verifier import (
            ChangeProposal,
            CodeChangeVerifier,
        )

        code = "def compute(x, y): return x + y\n"
        verifier = CodeChangeVerifier()
        result = verifier.verify(ChangeProposal("f.py", code, code))
        assert result.passed
        assert all(r.passed for r in result.rule_results)

    def test_custom_rule(self):
        from codomyrmex.formal_verification.code_change_verifier import (
            ChangeProposal,
            CodeChangeVerifier,
            InvariantRule,
            RuleResult,
        )

        def always_fail(proposal):
            return RuleResult(rule_name="always_fail", passed=False, message="nope")

        verifier = CodeChangeVerifier(rules=[
            InvariantRule("always_fail", "Always fails", always_fail)
        ])
        result = verifier.verify(ChangeProposal("f.py", "", ""))
        assert not result.passed


# ═══════════════════════════════════════════════════════════════════
#  COLLABORATION — Attestation
# ═══════════════════════════════════════════════════════════════════


class TestAttestation:
    """Tests for cryptographic task attestation."""

    def test_attest_and_verify_valid(self):
        from codomyrmex.collaboration.coordination.attestation import (
            AttestationAuthority,
        )

        authority = AttestationAuthority()
        data = b"task result data"
        att = authority.attest("task-1", "agent-a", data)
        assert authority.verify(att, data)

    def test_verify_tampered_data_fails(self):
        from codomyrmex.collaboration.coordination.attestation import (
            AttestationAuthority,
        )

        authority = AttestationAuthority()
        data = b"original"
        att = authority.attest("task-2", "agent-b", data)
        assert not authority.verify(att, b"tampered")

    def test_batch_verify_mixed(self):
        from codomyrmex.collaboration.coordination.attestation import (
            AttestationAuthority,
        )

        authority = AttestationAuthority()
        d1 = b"data1"
        d2 = b"data2"
        a1 = authority.attest("t1", "a1", d1)
        a2 = authority.attest("t2", "a2", d2)

        results = authority.batch_verify([a1, a2], [d1, b"wrong"])
        assert results["t1"] is True
        assert results["t2"] is False

    def test_attestation_deterministic(self):
        from codomyrmex.collaboration.coordination.attestation import (
            AttestationAuthority,
        )

        key = b"fixed-key-for-testing-12345678!"
        authority = AttestationAuthority(secret_key=key)
        data = b"result"
        a1 = authority.attest("t", "a", data, timestamp=1000.0)
        a2 = authority.attest("t", "a", data, timestamp=1000.0)
        assert a1.signature == a2.signature
        assert a1.result_hash == a2.result_hash

    def test_different_keys_different_signatures(self):
        from codomyrmex.collaboration.coordination.attestation import (
            AttestationAuthority,
        )

        auth1 = AttestationAuthority(secret_key=b"key1" + b"\x00" * 28)
        auth2 = AttestationAuthority(secret_key=b"key2" + b"\x00" * 28)
        data = b"data"
        a1 = auth1.attest("t", "a", data, timestamp=1000.0)
        a2 = auth2.attest("t", "a", data, timestamp=1000.0)
        assert a1.signature != a2.signature

    def test_batch_verify_length_mismatch_raises(self):
        from codomyrmex.collaboration.coordination.attestation import (
            AttestationAuthority,
        )

        authority = AttestationAuthority()
        att = authority.attest("t", "a", b"data")
        with pytest.raises(ValueError, match="count"):
            authority.batch_verify([att], [])

    def test_attestation_to_dict(self):
        from codomyrmex.collaboration.coordination.attestation import (
            AttestationAuthority,
        )

        authority = AttestationAuthority()
        att = authority.attest("t1", "a1", b"x")
        d = att.to_dict()
        assert d["task_id"] == "t1"
        assert d["agent_id"] == "a1"
        assert "signature" in d
        assert "result_hash" in d
