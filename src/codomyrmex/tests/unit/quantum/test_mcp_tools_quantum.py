"""Tests for quantum MCP tools.

Zero-mock tests that exercise the real quantum MCP tool implementations.
"""

from __future__ import annotations


class TestQuantumListGates:
    """Tests for quantum_list_gates MCP tool."""

    def test_returns_success_status(self):
        from codomyrmex.quantum.mcp_tools import quantum_list_gates

        result = quantum_list_gates()
        assert result["status"] == "success"

    def test_contains_standard_gates(self):
        from codomyrmex.quantum.mcp_tools import quantum_list_gates

        result = quantum_list_gates()
        gates = result["gate_types"]
        assert "H" in gates
        assert "X" in gates
        assert "CNOT" in gates

    def test_contains_algorithm_names(self):
        from codomyrmex.quantum.mcp_tools import quantum_list_gates

        result = quantum_list_gates()
        algos = result["algorithms"]
        assert "bell_state" in algos
        assert "ghz_state" in algos
        assert "qft" in algos


class TestQuantumSimulate:
    """Tests for quantum_simulate MCP tool."""

    def test_bell_state_simulation(self):
        from codomyrmex.quantum.mcp_tools import quantum_simulate

        result = quantum_simulate(algorithm="bell_state", shots=100)
        assert result["status"] == "success"
        assert result["algorithm"] == "bell_state"
        counts = result["counts"]
        # Bell state produces |00> and |11> only
        for key in counts:
            assert key in ("00", "11")
        assert sum(counts.values()) == 100

    def test_ghz_state_simulation(self):
        from codomyrmex.quantum.mcp_tools import quantum_simulate

        result = quantum_simulate(algorithm="ghz_state", num_qubits=3, shots=50)
        assert result["status"] == "success"
        counts = result["counts"]
        # GHZ state produces |000> and |111> only
        for key in counts:
            assert key in ("000", "111")
        assert sum(counts.values()) == 50

    def test_qft_simulation(self):
        from codomyrmex.quantum.mcp_tools import quantum_simulate

        result = quantum_simulate(algorithm="qft", num_qubits=2, shots=20)
        assert result["status"] == "success"
        assert result["stats"]["num_qubits"] == 2

    def test_unknown_algorithm_returns_error(self):
        from codomyrmex.quantum.mcp_tools import quantum_simulate

        result = quantum_simulate(algorithm="teleportation")
        assert result["status"] == "error"
        assert "Unknown algorithm" in result["message"]

    def test_result_contains_ascii_circuit(self):
        from codomyrmex.quantum.mcp_tools import quantum_simulate

        result = quantum_simulate(algorithm="bell_state", shots=10)
        assert result["status"] == "success"
        assert "ascii_circuit" in result
        assert "q0:" in result["ascii_circuit"]


class TestQuantumCircuitInfo:
    """Tests for quantum_circuit_info MCP tool."""

    def test_bell_state_stats(self):
        from codomyrmex.quantum.mcp_tools import quantum_circuit_info

        result = quantum_circuit_info(algorithm="bell_state")
        assert result["status"] == "success"
        stats = result["stats"]
        assert stats["num_qubits"] == 2
        assert stats["num_gates"] == 2  # H + CNOT
        assert stats["has_measurements"] is True

    def test_ghz_state_stats(self):
        from codomyrmex.quantum.mcp_tools import quantum_circuit_info

        result = quantum_circuit_info(algorithm="ghz_state", num_qubits=4)
        assert result["status"] == "success"
        stats = result["stats"]
        assert stats["num_qubits"] == 4
        assert stats["num_gates"] == 4  # 1 H + 3 CNOTs

    def test_unknown_algorithm_returns_error(self):
        from codomyrmex.quantum.mcp_tools import quantum_circuit_info

        result = quantum_circuit_info(algorithm="shor")
        assert result["status"] == "error"

    def test_ascii_art_present(self):
        from codomyrmex.quantum.mcp_tools import quantum_circuit_info

        result = quantum_circuit_info(algorithm="bell_state")
        assert "ascii_circuit" in result
        assert "q0:" in result["ascii_circuit"]
        assert "q1:" in result["ascii_circuit"]
