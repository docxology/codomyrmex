"""Unit tests for the quantum module's MCP tools.

Enforces strictly zero-mock policy.
"""

import pytest

from codomyrmex.quantum.mcp_tools import (
    quantum_bell_state_demo,
    quantum_circuit_stats,
    quantum_run_circuit,
)


def test_quantum_run_circuit_valid() -> None:
    """Test quantum_run_circuit with a valid simple circuit."""
    # Simple circuit: apply X to qubit 0 (making it |1>) and measure
    circuit_data = {
        "num_qubits": 1,
        "gates": [{"gate_type": "X", "target": 0}],
        "measure_all": True,
    }
    result = quantum_run_circuit(circuit_data, shots=10)

    # Should always measure "1"
    assert "1" in result
    assert result["1"] == 10
    assert "0" not in result


def test_quantum_run_circuit_bell_state() -> None:
    """Test quantum_run_circuit with a manually constructed Bell state."""
    circuit_data = {
        "num_qubits": 2,
        "gates": [
            {"gate_type": "H", "target": 0},
            {"gate_type": "CNOT", "target": 1, "control": 0},
        ],
        "measure_all": True,
    }
    result = quantum_run_circuit(circuit_data, shots=100)

    # Should only measure "00" and "11"
    assert set(result.keys()) <= {"00", "11"}
    # Very high probability of having both, but to avoid flaky tests, just check one exists
    assert sum(result.values()) == 100


def test_quantum_run_circuit_invalid_gate() -> None:
    """Test quantum_run_circuit with an invalid gate type naturally raising ValueError."""
    circuit_data = {
        "num_qubits": 1,
        "gates": [{"gate_type": "INVALID_GATE", "target": 0}],
    }
    with pytest.raises(ValueError, match="Invalid gate type"):
        quantum_run_circuit(circuit_data)


def test_quantum_run_circuit_missing_target() -> None:
    """Test quantum_run_circuit with a missing target natively raising ValueError."""
    circuit_data = {"num_qubits": 1, "gates": [{"gate_type": "H"}]}  # Missing target
    with pytest.raises(ValueError, match="Gate requires a target qubit"):
        quantum_run_circuit(circuit_data)


def test_quantum_run_circuit_missing_control() -> None:
    """Test quantum_run_circuit with a CNOT gate missing control."""
    circuit_data = {
        "num_qubits": 2,
        "gates": [{"gate_type": "CNOT", "target": 1}],  # Missing control
    }
    with pytest.raises(ValueError, match="CNOT gate requires a control qubit"):
        quantum_run_circuit(circuit_data)


def test_quantum_run_circuit_missing_parameter() -> None:
    """Test quantum_run_circuit with a rotation gate missing parameter."""
    circuit_data = {
        "num_qubits": 1,
        "gates": [{"gate_type": "RX", "target": 0}],  # Missing parameter
    }
    with pytest.raises(ValueError, match="RX gate requires a parameter"):
        quantum_run_circuit(circuit_data)


def test_quantum_circuit_stats() -> None:
    """Test quantum_circuit_stats accurately calculates stats."""
    circuit_data = {
        "num_qubits": 3,
        "gates": [
            {"gate_type": "H", "target": 0},
            {"gate_type": "CNOT", "target": 1, "control": 0},
            {"gate_type": "CNOT", "target": 2, "control": 1},
        ],
        "measure_all": False,
    }
    stats = quantum_circuit_stats(circuit_data)

    assert stats["num_qubits"] == 3
    assert stats["num_gates"] == 3
    assert stats["gate_counts"] == {"H": 1, "CNOT": 2}
    # depth for q0: H (1) + CNOT (1) = 2
    # depth for q1: CNOT (1) + CNOT (1) = 2
    # depth for q2: CNOT (1)
    assert stats["depth"] == 2
    assert stats["has_measurements"] is False


def test_quantum_bell_state_demo() -> None:
    """Test quantum_bell_state_demo returns proper structure and counts."""
    result = quantum_bell_state_demo(shots=50)

    assert "counts" in result
    assert "ascii_circuit" in result
    assert "stats" in result

    counts = result["counts"]
    assert set(counts.keys()) <= {"00", "11"}
    assert sum(counts.values()) == 50

    stats = result["stats"]
    assert stats["num_qubits"] == 2
    assert stats["has_measurements"] is True
