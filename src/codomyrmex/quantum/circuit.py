"""Quantum circuit definition and gate operations."""

from .models import Gate, GateType


class QuantumCircuit:
    """A quantum circuit."""

    def __init__(self, num_qubits: int, num_classical_bits: int = 0):
        self.num_qubits = num_qubits
        self.num_classical_bits = num_classical_bits or num_qubits
        self.gates: list[Gate] = []
        self.measurements: dict[int, int] = {}

    def h(self, qubit: int) -> "QuantumCircuit":
        """Add Hadamard gate."""
        self.gates.append(Gate(GateType.H, qubit))
        return self

    def x(self, qubit: int) -> "QuantumCircuit":
        """Add Pauli-X gate."""
        self.gates.append(Gate(GateType.X, qubit))
        return self

    def y(self, qubit: int) -> "QuantumCircuit":
        """Add Pauli-Y gate."""
        self.gates.append(Gate(GateType.Y, qubit))
        return self

    def z(self, qubit: int) -> "QuantumCircuit":
        """Add Pauli-Z gate."""
        self.gates.append(Gate(GateType.Z, qubit))
        return self

    def cnot(self, control: int, target: int) -> "QuantumCircuit":
        """Add CNOT gate."""
        self.gates.append(Gate(GateType.CNOT, target, control))
        return self

    def cz(self, control: int, target: int) -> "QuantumCircuit":
        """Add CZ gate."""
        self.gates.append(Gate(GateType.CZ, target, control))
        return self

    def rx(self, qubit: int, theta: float) -> "QuantumCircuit":
        """Add RX rotation."""
        self.gates.append(Gate(GateType.RX, qubit, parameter=theta))
        return self

    def ry(self, qubit: int, theta: float) -> "QuantumCircuit":
        """Add RY rotation."""
        self.gates.append(Gate(GateType.RY, qubit, parameter=theta))
        return self

    def rz(self, qubit: int, theta: float) -> "QuantumCircuit":
        """Add RZ rotation."""
        self.gates.append(Gate(GateType.RZ, qubit, parameter=theta))
        return self

    def swap(self, qubit1: int, qubit2: int) -> "QuantumCircuit":
        """Add SWAP gate."""
        self.gates.append(Gate(GateType.SWAP, qubit2, qubit1))
        return self

    def measure(self, qubit: int, classical_bit: int) -> "QuantumCircuit":
        """Add measurement."""
        self.measurements[qubit] = classical_bit
        return self

    def measure_all(self) -> "QuantumCircuit":
        """Measure all qubits."""
        for i in range(self.num_qubits):
            self.measurements[i] = i
        return self
