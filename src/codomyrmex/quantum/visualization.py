"""Quantum circuit visualization and statistics."""

from .models import Gate, GateType
from .circuit import QuantumCircuit


# Gate symbol mapping for ASCII rendering
_GATE_SYMBOLS: dict[GateType, str] = {
    GateType.H: "H",
    GateType.X: "X",
    GateType.Y: "Y",
    GateType.Z: "Z",
    GateType.S: "S",
    GateType.T: "T",
    GateType.RX: "Rx",
    GateType.RY: "Ry",
    GateType.RZ: "Rz",
    GateType.SWAP: "\u00d7",  # multiplication sign
}


def circuit_to_ascii(circuit: QuantumCircuit) -> str:
    """Render circuit as ASCII art.

    Example output for bell_state()::

        q0: -H--*--M-
        q1: ----X--M-

    Gate symbols:
        H=H, X=X, Y=Y, Z=Z, CNOT target=X control=*,
        CZ target=Z control=*, RX/RY/RZ=Rx/Ry/Rz,
        SWAP=x, Measure=M
    """
    n = circuit.num_qubits

    # Build a list of "time-step columns" for each qubit wire.
    # Each column is a dict mapping qubit index -> symbol string.
    columns: list[dict[int, str]] = []

    for gate in circuit.gates:
        col: dict[int, str] = {}

        if gate.gate_type == GateType.CNOT:
            # Control qubit gets a bullet, target gets X
            if gate.control is not None:
                col[gate.control] = "*"
            col[gate.target] = "X"
        elif gate.gate_type == GateType.CZ:
            # Control qubit gets a bullet, target gets Z
            if gate.control is not None:
                col[gate.control] = "*"
            col[gate.target] = "Z"
        elif gate.gate_type == GateType.SWAP:
            # Both qubits get x
            col[gate.target] = "x"
            if gate.control is not None:
                col[gate.control] = "x"
        else:
            symbol = _GATE_SYMBOLS.get(gate.gate_type, gate.gate_type.value)
            col[gate.target] = symbol

        columns.append(col)

    # Add measurement columns
    if circuit.measurements:
        col = {}
        for qubit_idx in sorted(circuit.measurements.keys()):
            col[qubit_idx] = "M"
        columns.append(col)

    # Determine the width of each column (max symbol length in that column)
    col_widths: list[int] = []
    for col in columns:
        max_w = 1
        for symbol in col.values():
            if len(symbol) > max_w:
                max_w = len(symbol)
        col_widths.append(max_w)

    # Build each qubit wire line
    lines: list[str] = []
    for q in range(n):
        parts: list[str] = [f"q{q}: "]
        for ci, col in enumerate(columns):
            w = col_widths[ci]
            if q in col:
                symbol = col[q]
                # Center the symbol in its width, pad with dashes
                left_pad = (w - len(symbol)) // 2
                right_pad = w - len(symbol) - left_pad
                parts.append("-" + "-" * left_pad + symbol + "-" * right_pad + "-")
            else:
                parts.append("-" + "-" * w + "-")
        lines.append("".join(parts))

    return "\n".join(lines)


def circuit_stats(circuit: QuantumCircuit) -> dict:
    """Return circuit statistics.

    Returns a dict with:
        - num_qubits: int -- number of qubits in the circuit
        - num_gates: int -- total number of gates
        - gate_counts: dict[str, int] -- count per gate type name
        - depth: int -- max gates on any single qubit wire
        - has_measurements: bool -- whether the circuit has measurements
    """
    num_qubits = circuit.num_qubits
    num_gates = len(circuit.gates)
    has_measurements = bool(circuit.measurements)

    # Count gates by type
    gate_counts: dict[str, int] = {}
    for gate in circuit.gates:
        name = gate.gate_type.value
        gate_counts[name] = gate_counts.get(name, 0) + 1

    # Calculate depth: max number of gates touching any single qubit
    qubit_depths: dict[int, int] = {}
    for gate in circuit.gates:
        qubit_depths[gate.target] = qubit_depths.get(gate.target, 0) + 1
        if gate.control is not None:
            qubit_depths[gate.control] = qubit_depths.get(gate.control, 0) + 1

    depth = max(qubit_depths.values()) if qubit_depths else 0

    return {
        "num_qubits": num_qubits,
        "num_gates": num_gates,
        "gate_counts": gate_counts,
        "depth": depth,
        "has_measurements": has_measurements,
    }
