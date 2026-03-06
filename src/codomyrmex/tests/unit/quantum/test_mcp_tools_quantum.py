"""Tests for quantum MCP tools.

Zero-mock tests that exercise the real quantum MCP tool implementations.
"""

from __future__ import annotations

import pytest


class TestQuantumRunCircuit:
    """Tests for quantum_run_circuit MCP tool."""

    def test_run_circuit_success(self):
        from codomyrmex.quantum.mcp_tools import quantum_run_circuit

        circuit_data = {
            "num_qubits": 1,
            "gates": [{"gate_type": "H", "target": 0}],
            "measure_all": True,
        }
        result = quantum_run_circuit(circuit_data=circuit_data, shots=100)
        assert isinstance(result, dict)
        assert sum(result.values()) == 100
        # H gate should produce 0 and 1
        for k in result:
            assert k in ("0", "1")

    def test_invalid_gate_type(self):
        from codomyrmex.quantum.mcp_tools import quantum_run_circuit

        circuit_data = {
            "num_qubits": 1,
            "gates": [{"gate_type": "UNKNOWN", "target": 0}],
        }
        with pytest.raises(ValueError, match="Invalid gate type"):
            quantum_run_circuit(circuit_data=circuit_data)


class TestQuantumCircuitStats:
    """Tests for quantum_circuit_stats MCP tool."""

    def test_circuit_stats_success(self):
        from codomyrmex.quantum.mcp_tools import quantum_circuit_stats

        circuit_data = {
            "num_qubits": 2,
            "gates": [
                {"gate_type": "H", "target": 0},
                {"gate_type": "CNOT", "control": 0, "target": 1},
            ],
            "measure_all": True,
        }
        result = quantum_circuit_stats(circuit_data=circuit_data)
        assert isinstance(result, dict)
        assert result["num_qubits"] == 2
        assert result["num_gates"] == 2
        assert result["has_measurements"] is True

    def test_missing_control_qubit(self):
        from codomyrmex.quantum.mcp_tools import quantum_circuit_stats

        circuit_data = {
            "num_qubits": 2,
            "gates": [{"gate_type": "CNOT", "target": 1}],
        }
        with pytest.raises(ValueError, match="requires a control qubit"):
            quantum_circuit_stats(circuit_data=circuit_data)


class TestQuantumBellStateDemo:
    """Tests for quantum_bell_state_demo MCP tool."""

    def test_bell_state_demo(self):
        from codomyrmex.quantum.mcp_tools import quantum_bell_state_demo

        result = quantum_bell_state_demo(shots=50)
        assert isinstance(result, dict)
        assert "counts" in result
        assert "ascii_circuit" in result
        assert "stats" in result

        counts = result["counts"]
        assert sum(counts.values()) == 50
        for k in counts:
            assert k in ("00", "11")

        assert result["stats"]["num_qubits"] == 2
        assert result["stats"]["num_gates"] == 2
        assert "q0:" in result["ascii_circuit"]
