"""Tests for quantum module."""

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
    )
    HAS_MODULE = True
except ImportError:
    HAS_MODULE = False

if not HAS_MODULE:
    pytest.skip("quantum module not available", allow_module_level=True)


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
        import math
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
