"""Tests for quantum module."""

import math

import pytest

try:
    from codomyrmex.quantum import (
        Gate,
        GateType,
        QuantumCircuit,
        QuantumSimulator,
        Qubit,
        bell_state,
        ghz_state,
        qft,
        circuit_to_ascii,
        circuit_stats,
    )
    HAS_MODULE = True
except ImportError:
    HAS_MODULE = False

if not HAS_MODULE:
    pytest.skip("quantum module not available", allow_module_level=True)


# ---------------------------------------------------------------------------
# Original 19 tests (preserved)
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestGateType:
    def test_hadamard(self):
        assert GateType.H is not None

    def test_pauli_x(self):
        assert GateType.X is not None

    def test_cnot(self):
        assert GateType.CNOT is not None

    def test_swap(self):
        assert GateType.SWAP is not None

    def test_rotation_gates(self):
        assert GateType.RX is not None
        assert GateType.RY is not None
        assert GateType.RZ is not None


@pytest.mark.unit
class TestGate:
    def test_create_gate(self):
        gate = Gate(gate_type=GateType.H, target=0)
        assert gate.gate_type == GateType.H
        assert gate.target == 0
        assert gate.control is None

    def test_cnot_gate(self):
        gate = Gate(gate_type=GateType.CNOT, target=1, control=0)
        assert gate.control == 0
        assert gate.target == 1

    def test_parametric_gate(self):
        gate = Gate(gate_type=GateType.RX, target=0, parameter=math.pi / 2)
        assert gate.parameter is not None


@pytest.mark.unit
class TestQubit:
    def test_create_qubit(self):
        qubit = Qubit()
        assert qubit.alpha == 1.0 + 0j
        assert qubit.beta == 0.0 + 0j

    def test_zero_state(self):
        qubit = Qubit.zero()
        assert qubit is not None

    def test_one_state(self):
        qubit = Qubit.one()
        assert qubit is not None

    def test_plus_state(self):
        qubit = Qubit.plus()
        assert qubit is not None

    def test_minus_state(self):
        qubit = Qubit.minus()
        assert qubit is not None


@pytest.mark.unit
class TestQuantumCircuit:
    def test_create_circuit(self):
        circuit = QuantumCircuit(num_qubits=2)
        assert circuit is not None

    def test_circuit_with_classical_bits(self):
        circuit = QuantumCircuit(num_qubits=3, num_classical_bits=3)
        assert circuit is not None


@pytest.mark.unit
class TestQuantumSimulator:
    def test_create_simulator(self):
        sim = QuantumSimulator()
        assert sim is not None


@pytest.mark.unit
class TestBellState:
    def test_creates_circuit(self):
        circuit = bell_state()
        assert isinstance(circuit, QuantumCircuit)


@pytest.mark.unit
class TestGHZState:
    def test_creates_circuit(self):
        circuit = ghz_state(3)
        assert isinstance(circuit, QuantumCircuit)


@pytest.mark.unit
class TestQFT:
    def test_creates_circuit(self):
        circuit = qft(3)
        assert isinstance(circuit, QuantumCircuit)


# ---------------------------------------------------------------------------
# NEW: Deep behavioral tests
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestQubitAmplitudes:
    """Verify qubit state amplitudes and probability distributions."""

    def test_zero_state_amplitudes(self):
        q = Qubit.zero()
        assert q.alpha == 1.0 + 0j
        assert q.beta == 0.0 + 0j

    def test_zero_state_probabilities(self):
        q = Qubit.zero()
        assert q.prob_0 == pytest.approx(1.0)
        assert q.prob_1 == pytest.approx(0.0)

    def test_one_state_amplitudes(self):
        q = Qubit.one()
        assert q.alpha == 0.0 + 0j
        assert q.beta == 1.0 + 0j

    def test_one_state_probabilities(self):
        q = Qubit.one()
        assert q.prob_0 == pytest.approx(0.0)
        assert q.prob_1 == pytest.approx(1.0)

    def test_plus_state_equal_superposition(self):
        q = Qubit.plus()
        assert q.prob_0 == pytest.approx(0.5)
        assert q.prob_1 == pytest.approx(0.5)

    def test_plus_state_amplitudes_positive(self):
        q = Qubit.plus()
        s = 1 / math.sqrt(2)
        assert q.alpha == pytest.approx(s)
        assert q.beta == pytest.approx(s)

    def test_minus_state_equal_superposition(self):
        q = Qubit.minus()
        assert q.prob_0 == pytest.approx(0.5)
        assert q.prob_1 == pytest.approx(0.5)

    def test_minus_state_amplitudes_differ_in_sign(self):
        q = Qubit.minus()
        s = 1 / math.sqrt(2)
        assert q.alpha == pytest.approx(s)
        assert q.beta == pytest.approx(-s)

    def test_probabilities_sum_to_one_zero(self):
        q = Qubit.zero()
        assert q.prob_0 + q.prob_1 == pytest.approx(1.0)

    def test_probabilities_sum_to_one_plus(self):
        q = Qubit.plus()
        assert q.prob_0 + q.prob_1 == pytest.approx(1.0)


@pytest.mark.unit
class TestQubitMeasurement:
    """Verify measurement collapses qubit state."""

    def test_measure_zero_always_collapses_to_zero(self):
        q = Qubit.zero()
        result = q.measure()
        assert result == 0
        assert q.prob_0 == pytest.approx(1.0)
        assert q.prob_1 == pytest.approx(0.0)

    def test_measure_one_always_collapses_to_one(self):
        q = Qubit.one()
        result = q.measure()
        assert result == 1
        assert q.prob_0 == pytest.approx(0.0)
        assert q.prob_1 == pytest.approx(1.0)

    def test_measure_plus_collapses_state(self):
        """After measuring |+>, the qubit must be in a definite state."""
        q = Qubit.plus()
        result = q.measure()
        assert result in (0, 1)
        # After collapse, one probability must be 1.0 and the other 0.0
        assert q.prob_0 == pytest.approx(1.0) or q.prob_0 == pytest.approx(0.0)
        assert q.prob_1 == pytest.approx(1.0) or q.prob_1 == pytest.approx(0.0)
        assert q.prob_0 + q.prob_1 == pytest.approx(1.0)

    def test_measure_plus_is_idempotent_after_collapse(self):
        """Repeated measurements after collapse yield the same result."""
        q = Qubit.plus()
        first = q.measure()
        for _ in range(10):
            assert q.measure() == first

    def test_measure_plus_produces_both_outcomes(self):
        """Over many trials, |+> should produce both 0 and 1."""
        outcomes = set()
        for _ in range(200):
            q = Qubit.plus()
            outcomes.add(q.measure())
            if outcomes == {0, 1}:
                break
        assert outcomes == {0, 1}, "Expected both 0 and 1 outcomes from |+> state"


@pytest.mark.unit
class TestCircuitGateOperations:
    """Each gate method adds the correct gate to the gates list."""

    def test_h_adds_hadamard_gate(self):
        c = QuantumCircuit(1)
        c.h(0)
        assert len(c.gates) == 1
        assert c.gates[0].gate_type == GateType.H
        assert c.gates[0].target == 0

    def test_x_adds_pauli_x_gate(self):
        c = QuantumCircuit(1)
        c.x(0)
        assert len(c.gates) == 1
        assert c.gates[0].gate_type == GateType.X
        assert c.gates[0].target == 0

    def test_y_adds_pauli_y_gate(self):
        c = QuantumCircuit(1)
        c.y(0)
        assert len(c.gates) == 1
        assert c.gates[0].gate_type == GateType.Y
        assert c.gates[0].target == 0

    def test_z_adds_pauli_z_gate(self):
        c = QuantumCircuit(1)
        c.z(0)
        assert len(c.gates) == 1
        assert c.gates[0].gate_type == GateType.Z
        assert c.gates[0].target == 0

    def test_cnot_adds_cnot_gate_with_control(self):
        c = QuantumCircuit(2)
        c.cnot(0, 1)
        assert len(c.gates) == 1
        assert c.gates[0].gate_type == GateType.CNOT
        assert c.gates[0].target == 1
        assert c.gates[0].control == 0

    def test_cz_adds_cz_gate_with_control(self):
        c = QuantumCircuit(2)
        c.cz(0, 1)
        assert len(c.gates) == 1
        assert c.gates[0].gate_type == GateType.CZ
        assert c.gates[0].target == 1
        assert c.gates[0].control == 0

    def test_rx_adds_rotation_with_parameter(self):
        c = QuantumCircuit(1)
        c.rx(0, math.pi / 4)
        assert len(c.gates) == 1
        assert c.gates[0].gate_type == GateType.RX
        assert c.gates[0].parameter == pytest.approx(math.pi / 4)

    def test_ry_adds_rotation_with_parameter(self):
        c = QuantumCircuit(1)
        c.ry(0, math.pi / 3)
        assert len(c.gates) == 1
        assert c.gates[0].gate_type == GateType.RY
        assert c.gates[0].parameter == pytest.approx(math.pi / 3)

    def test_rz_adds_rotation_with_parameter(self):
        c = QuantumCircuit(1)
        c.rz(0, math.pi / 6)
        assert len(c.gates) == 1
        assert c.gates[0].gate_type == GateType.RZ
        assert c.gates[0].parameter == pytest.approx(math.pi / 6)

    def test_measure_all_sets_measurements(self):
        c = QuantumCircuit(3)
        c.measure_all()
        assert c.measurements == {0: 0, 1: 1, 2: 2}

    def test_measure_single_qubit(self):
        c = QuantumCircuit(2)
        c.measure(0, 0)
        assert c.measurements == {0: 0}

    def test_multiple_gates_accumulate(self):
        c = QuantumCircuit(2)
        c.h(0).x(1).cnot(0, 1)
        assert len(c.gates) == 3
        assert c.gates[0].gate_type == GateType.H
        assert c.gates[1].gate_type == GateType.X
        assert c.gates[2].gate_type == GateType.CNOT


@pytest.mark.unit
class TestCircuitFluentAPI:
    """Fluent API: each gate method returns self for chaining."""

    def test_h_returns_self(self):
        c = QuantumCircuit(1)
        assert c.h(0) is c

    def test_x_returns_self(self):
        c = QuantumCircuit(1)
        assert c.x(0) is c

    def test_y_returns_self(self):
        c = QuantumCircuit(1)
        assert c.y(0) is c

    def test_z_returns_self(self):
        c = QuantumCircuit(1)
        assert c.z(0) is c

    def test_cnot_returns_self(self):
        c = QuantumCircuit(2)
        assert c.cnot(0, 1) is c

    def test_cz_returns_self(self):
        c = QuantumCircuit(2)
        assert c.cz(0, 1) is c

    def test_rx_returns_self(self):
        c = QuantumCircuit(1)
        assert c.rx(0, 0.5) is c

    def test_ry_returns_self(self):
        c = QuantumCircuit(1)
        assert c.ry(0, 0.5) is c

    def test_rz_returns_self(self):
        c = QuantumCircuit(1)
        assert c.rz(0, 0.5) is c

    def test_measure_returns_self(self):
        c = QuantumCircuit(1)
        assert c.measure(0, 0) is c

    def test_measure_all_returns_self(self):
        c = QuantumCircuit(2)
        assert c.measure_all() is c

    def test_full_chain(self):
        c = QuantumCircuit(2)
        result = c.h(0).cnot(0, 1).measure_all()
        assert result is c
        assert len(c.gates) == 2


@pytest.mark.unit
class TestSimulatorBellState:
    """Bell state simulation must produce only correlated outcomes."""

    def test_bell_state_only_00_and_11(self):
        sim = QuantumSimulator()
        counts = sim.run(bell_state(), shots=1000)
        for key in counts:
            assert key in ("00", "11"), f"Unexpected outcome: {key}"

    def test_bell_state_both_outcomes_present(self):
        sim = QuantumSimulator()
        counts = sim.run(bell_state(), shots=1000)
        assert counts.get("00", 0) > 0, "Expected '00' outcome"
        assert counts.get("11", 0) > 0, "Expected '11' outcome"

    def test_bell_state_no_anticorrelated_outcomes(self):
        sim = QuantumSimulator()
        counts = sim.run(bell_state(), shots=1000)
        assert "01" not in counts, "Bell state should not produce '01'"
        assert "10" not in counts, "Bell state should not produce '10'"

    def test_bell_state_total_shots(self):
        sim = QuantumSimulator()
        shots = 500
        counts = sim.run(bell_state(), shots=shots)
        assert sum(counts.values()) == shots


@pytest.mark.unit
class TestSimulatorXGate:
    """X gate flips |0> to |1>, so all measurements should be '1'."""

    def test_x_gate_all_ones(self):
        circuit = QuantumCircuit(1).x(0).measure_all()
        sim = QuantumSimulator()
        counts = sim.run(circuit, shots=500)
        assert counts == {"1": 500}

    def test_x_gate_no_zeros(self):
        circuit = QuantumCircuit(1).x(0).measure_all()
        sim = QuantumSimulator()
        counts = sim.run(circuit, shots=200)
        assert "0" not in counts

    def test_double_x_gate_returns_to_zero(self):
        circuit = QuantumCircuit(1).x(0).x(0).measure_all()
        sim = QuantumSimulator()
        counts = sim.run(circuit, shots=200)
        assert counts == {"0": 200}


@pytest.mark.unit
class TestSimulatorGHZState:
    """GHZ state for n qubits: only all-zeros and all-ones outcomes."""

    def test_ghz_3_only_000_and_111(self):
        sim = QuantumSimulator()
        counts = sim.run(ghz_state(3), shots=1000)
        for key in counts:
            assert key in ("000", "111"), f"Unexpected GHZ outcome: {key}"

    def test_ghz_3_both_outcomes_present(self):
        sim = QuantumSimulator()
        counts = sim.run(ghz_state(3), shots=1000)
        assert counts.get("000", 0) > 0
        assert counts.get("111", 0) > 0

    def test_ghz_4_only_extreme_outcomes(self):
        sim = QuantumSimulator()
        counts = sim.run(ghz_state(4), shots=1000)
        for key in counts:
            assert key in ("0000", "1111"), f"Unexpected 4-qubit GHZ outcome: {key}"


@pytest.mark.unit
class TestSimulatorHadamard:
    """Hadamard on |0> should give roughly equal 0 and 1."""

    def test_hadamard_produces_both_outcomes(self):
        circuit = QuantumCircuit(1).h(0).measure_all()
        sim = QuantumSimulator()
        counts = sim.run(circuit, shots=1000)
        assert "0" in counts and "1" in counts

    def test_hadamard_roughly_balanced(self):
        circuit = QuantumCircuit(1).h(0).measure_all()
        sim = QuantumSimulator()
        counts = sim.run(circuit, shots=2000)
        ratio = counts.get("0", 0) / 2000
        assert 0.35 < ratio < 0.65, f"H gate output unexpectedly biased: {ratio}"


@pytest.mark.unit
class TestQFTGateCounts:
    """QFT should produce correct number of gates."""

    def test_qft_2_gate_count(self):
        """QFT(2): H on q0, RZ on q1, H on q1 = 3 gates."""
        c = qft(2)
        assert len(c.gates) == 3

    def test_qft_3_gate_count(self):
        """QFT(3): H, RZ, RZ, H, RZ, H = 6 gates."""
        c = qft(3)
        assert len(c.gates) == 6

    def test_qft_contains_hadamard_gates(self):
        c = qft(3)
        h_count = sum(1 for g in c.gates if g.gate_type == GateType.H)
        assert h_count == 3, "QFT(3) should have 3 Hadamard gates"

    def test_qft_contains_rz_gates(self):
        c = qft(3)
        rz_count = sum(1 for g in c.gates if g.gate_type == GateType.RZ)
        assert rz_count == 3, "QFT(3) should have 3 RZ gates"

    def test_qft_n_total_gate_formula(self):
        """QFT(n) has n*(n+1)/2 gates: n Hadamards + n*(n-1)/2 rotations."""
        for n in range(2, 6):
            c = qft(n)
            expected = n * (n + 1) // 2
            assert len(c.gates) == expected, f"QFT({n}) expected {expected} gates, got {len(c.gates)}"


# ---------------------------------------------------------------------------
# NEW: Tests for visualization submodule
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestCircuitToAscii:
    """Tests for circuit_to_ascii rendering."""

    def test_single_h_gate(self):
        c = QuantumCircuit(1).h(0)
        output = circuit_to_ascii(c)
        assert "q0:" in output
        assert "H" in output

    def test_bell_state_ascii(self):
        output = circuit_to_ascii(bell_state())
        lines = output.strip().split("\n")
        assert len(lines) == 2
        assert "q0:" in lines[0]
        assert "q1:" in lines[1]
        # q0 should have H, control (*), M
        assert "H" in lines[0]
        assert "*" in lines[0]
        assert "M" in lines[0]
        # q1 should have target X and M
        assert "X" in lines[1]
        assert "M" in lines[1]

    def test_x_gate_renders(self):
        c = QuantumCircuit(1).x(0).measure_all()
        output = circuit_to_ascii(c)
        assert "X" in output
        assert "M" in output

    def test_multi_qubit_lines(self):
        c = QuantumCircuit(3).h(0).h(1).h(2)
        output = circuit_to_ascii(c)
        lines = output.strip().split("\n")
        assert len(lines) == 3

    def test_empty_circuit_no_crash(self):
        c = QuantumCircuit(2)
        output = circuit_to_ascii(c)
        assert "q0:" in output
        assert "q1:" in output

    def test_measurement_symbols(self):
        c = QuantumCircuit(2).measure_all()
        output = circuit_to_ascii(c)
        assert output.count("M") == 2

    def test_rotation_gate_symbol(self):
        c = QuantumCircuit(1).rx(0, math.pi / 4)
        output = circuit_to_ascii(c)
        assert "Rx" in output


@pytest.mark.unit
class TestCircuitStats:
    """Tests for circuit_stats statistics."""

    def test_bell_state_stats(self):
        stats = circuit_stats(bell_state())
        assert stats["num_qubits"] == 2
        assert stats["num_gates"] == 2  # H + CNOT
        assert stats["has_measurements"] is True

    def test_bell_state_gate_counts(self):
        stats = circuit_stats(bell_state())
        assert stats["gate_counts"]["H"] == 1
        assert stats["gate_counts"]["CNOT"] == 1

    def test_empty_circuit_stats(self):
        stats = circuit_stats(QuantumCircuit(3))
        assert stats["num_qubits"] == 3
        assert stats["num_gates"] == 0
        assert stats["gate_counts"] == {}
        assert stats["depth"] == 0
        assert stats["has_measurements"] is False

    def test_depth_single_qubit(self):
        c = QuantumCircuit(1).h(0).x(0).z(0)
        stats = circuit_stats(c)
        assert stats["depth"] == 3

    def test_depth_parallel_gates(self):
        """Gates on separate qubits don't increase each other's depth."""
        c = QuantumCircuit(2).h(0).x(1)
        stats = circuit_stats(c)
        assert stats["depth"] == 1

    def test_ghz_3_stats(self):
        stats = circuit_stats(ghz_state(3))
        assert stats["num_qubits"] == 3
        # H on q0, CNOT(0,1), CNOT(0,2) = 3 gates
        assert stats["num_gates"] == 3
        assert stats["has_measurements"] is True

    def test_qft_3_stats(self):
        stats = circuit_stats(qft(3))
        assert stats["num_qubits"] == 3
        assert stats["num_gates"] == 6
        assert stats["has_measurements"] is False
        assert stats["gate_counts"]["H"] == 3
        assert stats["gate_counts"]["RZ"] == 3

    def test_cnot_depth_counts_both_qubits(self):
        """CNOT should count toward depth of both control and target qubits."""
        c = QuantumCircuit(2).cnot(0, 1)
        stats = circuit_stats(c)
        # CNOT touches both qubits, so depth is 1
        assert stats["depth"] == 1

    def test_stats_returns_all_keys(self):
        stats = circuit_stats(QuantumCircuit(1))
        expected_keys = {"num_qubits", "num_gates", "gate_counts", "depth", "has_measurements"}
        assert set(stats.keys()) == expected_keys


# ---------------------------------------------------------------------------
# NEW: SWAP gate tests
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestSwapGate:
    """Tests for QuantumCircuit.swap() and simulator SWAP support."""

    def test_swap_adds_gate(self):
        """swap() adds a SWAP gate to the circuit."""
        c = QuantumCircuit(2)
        c.swap(0, 1)
        assert len(c.gates) == 1
        assert c.gates[0].gate_type == GateType.SWAP

    def test_swap_returns_self(self):
        """swap() returns self for fluent chaining."""
        c = QuantumCircuit(2)
        assert c.swap(0, 1) is c

    def test_swap_chaining(self):
        """swap() can chain with other gate methods."""
        c = QuantumCircuit(2)
        result = c.h(0).swap(0, 1).measure_all()
        assert result is c
        assert len(c.gates) == 2
        assert c.gates[1].gate_type == GateType.SWAP

    def test_swap_simulation(self):
        """SWAP after X(0) should move |1> from qubit 0 to qubit 1."""
        c = QuantumCircuit(2).x(0).swap(0, 1).measure_all()
        sim = QuantumSimulator()
        counts = sim.run(c, shots=500)
        # After X on q0: state is |10>. After SWAP: state is |01>.
        # Bitstring is reversed: qubit 0 is rightmost, so |01> -> "10"
        assert "10" in counts, f"Expected '10' in counts, got {counts}"
        assert counts["10"] == 500

    def test_swap_ascii(self):
        """SWAP gate renders 'x' in ASCII output."""
        c = QuantumCircuit(2).swap(0, 1)
        output = circuit_to_ascii(c)
        assert "x" in output
