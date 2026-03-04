"""Model Context Protocol (MCP) tools for quantum computing."""

from typing import Any

from codomyrmex.model_context_protocol.decorators import mcp_tool

from .algorithms import bell_state
from .circuit import QuantumCircuit
from .models import GateType
from .simulator import QuantumSimulator
from .visualization import circuit_stats, circuit_to_ascii


def _build_circuit_from_json(circuit_data: dict[str, Any]) -> QuantumCircuit:
    """Helper to build a QuantumCircuit from JSON-like dict."""
    num_qubits = circuit_data.get("num_qubits", 1)
    qc = QuantumCircuit(num_qubits)

    gates = circuit_data.get("gates", [])
    for gate_data in gates:
        gtype_str = gate_data.get("gate_type")
        if not gtype_str:
            continue

        try:
            gtype = GateType(gtype_str.upper())
        except ValueError as err:
            raise ValueError(f"Invalid gate type: {gtype_str}") from err

        target = gate_data.get("target")
        if target is None:
            raise ValueError("Gate requires a target qubit")

        control = gate_data.get("control")
        param = gate_data.get("parameter")

        if gtype == GateType.H:
            qc.h(target)
        elif gtype == GateType.X:
            qc.x(target)
        elif gtype == GateType.Y:
            qc.y(target)
        elif gtype == GateType.Z:
            qc.z(target)
        elif gtype == GateType.CNOT:
            if control is None:
                raise ValueError("CNOT gate requires a control qubit")
            qc.cnot(control, target)
        elif gtype == GateType.CZ:
            if control is None:
                raise ValueError("CZ gate requires a control qubit")
            qc.cz(control, target)
        elif gtype == GateType.SWAP:
            if control is None:
                raise ValueError("SWAP gate requires a control qubit")
            qc.swap(control, target)
        elif gtype == GateType.RX:
            if param is None:
                raise ValueError("RX gate requires a parameter")
            qc.rx(target, param)
        elif gtype == GateType.RY:
            if param is None:
                raise ValueError("RY gate requires a parameter")
            qc.ry(target, param)
        elif gtype == GateType.RZ:
            if param is None:
                raise ValueError("RZ gate requires a parameter")
            qc.rz(target, param)

    if circuit_data.get("measure_all", False):
        qc.measure_all()

    return qc


@mcp_tool()
def quantum_run_circuit(
    circuit_data: dict[str, Any], shots: int = 1024
) -> dict[str, int]:
    """Run a quantum circuit simulation.

    Args:
        circuit_data: Dictionary defining the circuit (e.g., {"num_qubits": 2, "gates": [{"gate_type": "H", "target": 0}], "measure_all": True})
        shots: Number of times to run the simulation (default: 1024)

    Returns:
        A dictionary of measurement bitstrings and their counts.
    """
    circuit = _build_circuit_from_json(circuit_data)
    sim = QuantumSimulator()
    return sim.run(circuit, shots=shots)


@mcp_tool()
def quantum_circuit_stats(circuit_data: dict[str, Any]) -> dict[str, Any]:
    """Get statistics for a quantum circuit.

    Args:
        circuit_data: Dictionary defining the circuit.

    Returns:
        A dictionary containing circuit statistics (e.g., depth, gate counts).
    """
    circuit = _build_circuit_from_json(circuit_data)
    return circuit_stats(circuit)


@mcp_tool()
def quantum_bell_state_demo(shots: int = 1024) -> dict[str, Any]:
    """Run a Bell state simulation demonstration.

    Args:
        shots: Number of simulation shots (default: 1024).

    Returns:
        A dictionary containing the simulation counts, circuit ASCII representation, and stats.
    """
    circuit = bell_state()
    sim = QuantumSimulator()
    counts = sim.run(circuit, shots=shots)
    stats = circuit_stats(circuit)
    ascii_art = circuit_to_ascii(circuit)

    return {"counts": counts, "ascii_circuit": ascii_art, "stats": stats}
