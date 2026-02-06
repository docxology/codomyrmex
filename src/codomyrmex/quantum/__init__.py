"""
Quantum Computing Module

Quantum algorithm primitives, simulation, and circuit patterns.
"""

__version__ = "0.1.0"

import math
import cmath
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Tuple
import random


class GateType(Enum):
    """Quantum gate types."""
    H = "H"  # Hadamard
    X = "X"  # Pauli-X (NOT)
    Y = "Y"  # Pauli-Y
    Z = "Z"  # Pauli-Z
    CNOT = "CNOT"  # Controlled-NOT
    SWAP = "SWAP"
    T = "T"  # T gate
    S = "S"  # S gate
    RX = "RX"  # Rotation X
    RY = "RY"  # Rotation Y
    RZ = "RZ"  # Rotation Z
    CZ = "CZ"  # Controlled-Z


@dataclass
class Gate:
    """A quantum gate."""
    gate_type: GateType
    target: int
    control: Optional[int] = None
    parameter: Optional[float] = None


@dataclass
class Qubit:
    """A quantum bit state."""
    alpha: complex = 1.0 + 0j  # |0⟩ amplitude
    beta: complex = 0.0 + 0j  # |1⟩ amplitude
    
    @classmethod
    def zero(cls) -> "Qubit":
        return cls(1.0 + 0j, 0.0 + 0j)
    
    @classmethod
    def one(cls) -> "Qubit":
        return cls(0.0 + 0j, 1.0 + 0j)
    
    @classmethod
    def plus(cls) -> "Qubit":
        """|+⟩ state."""
        s = 1 / math.sqrt(2)
        return cls(s + 0j, s + 0j)
    
    @classmethod
    def minus(cls) -> "Qubit":
        """|−⟩ state."""
        s = 1 / math.sqrt(2)
        return cls(s + 0j, -s + 0j)
    
    @property
    def prob_0(self) -> float:
        return abs(self.alpha) ** 2
    
    @property
    def prob_1(self) -> float:
        return abs(self.beta) ** 2
    
    def measure(self) -> int:
        """Measure qubit, collapsing state."""
        if random.random() < self.prob_0:
            self.alpha = 1.0 + 0j
            self.beta = 0.0 + 0j
            return 0
        else:
            self.alpha = 0.0 + 0j
            self.beta = 1.0 + 0j
            return 1


class QuantumCircuit:
    """A quantum circuit."""
    
    def __init__(self, num_qubits: int, num_classical_bits: int = 0):
        self.num_qubits = num_qubits
        self.num_classical_bits = num_classical_bits or num_qubits
        self.gates: List[Gate] = []
        self.measurements: Dict[int, int] = {}
    
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
    
    def measure(self, qubit: int, classical_bit: int) -> "QuantumCircuit":
        """Add measurement."""
        self.measurements[qubit] = classical_bit
        return self
    
    def measure_all(self) -> "QuantumCircuit":
        """Measure all qubits."""
        for i in range(self.num_qubits):
            self.measurements[i] = i
        return self


class QuantumSimulator:
    """Simple statevector quantum simulator."""
    
    def __init__(self):
        self._state: List[complex] = []
    
    def _init_state(self, num_qubits: int):
        """Initialize to |00...0⟩ state."""
        self._state = [0 + 0j] * (2 ** num_qubits)
        self._state[0] = 1 + 0j
    
    def _apply_single_gate(self, gate: GateType, target: int, num_qubits: int, param: Optional[float] = None):
        """Apply single-qubit gate."""
        # Gate matrices
        sqrt2 = math.sqrt(2)
        matrices = {
            GateType.H: [[1/sqrt2, 1/sqrt2], [1/sqrt2, -1/sqrt2]],
            GateType.X: [[0, 1], [1, 0]],
            GateType.Y: [[0, -1j], [1j, 0]],
            GateType.Z: [[1, 0], [0, -1]],
            GateType.S: [[1, 0], [0, 1j]],
            GateType.T: [[1, 0], [0, cmath.exp(1j * math.pi / 4)]],
        }
        
        if gate in matrices:
            matrix = matrices[gate]
        elif gate == GateType.RX and param is not None:
            c, s = math.cos(param/2), math.sin(param/2)
            matrix = [[c, -1j*s], [-1j*s, c]]
        elif gate == GateType.RY and param is not None:
            c, s = math.cos(param/2), math.sin(param/2)
            matrix = [[c, -s], [s, c]]
        elif gate == GateType.RZ and param is not None:
            e = cmath.exp(1j * param / 2)
            matrix = [[1/e, 0], [0, e]]
        else:
            return
        
        new_state = [0 + 0j] * len(self._state)
        for i in range(len(self._state)):
            bit = (i >> target) & 1
            i0 = i & ~(1 << target)
            i1 = i | (1 << target)
            
            if bit == 0:
                new_state[i0] += matrix[0][0] * self._state[i0] + matrix[0][1] * self._state[i1]
                new_state[i1] += matrix[1][0] * self._state[i0] + matrix[1][1] * self._state[i1]
        
        self._state = new_state
    
    def _apply_cnot(self, control: int, target: int):
        """Apply CNOT gate."""
        new_state = list(self._state)
        for i in range(len(self._state)):
            if (i >> control) & 1:
                j = i ^ (1 << target)
                new_state[i] = self._state[j]
                new_state[j] = self._state[i]
        self._state = new_state
    
    def run(self, circuit: QuantumCircuit, shots: int = 1024) -> Dict[str, int]:
        """Run circuit and return measurement counts."""
        counts: Dict[str, int] = {}
        
        for _ in range(shots):
            self._init_state(circuit.num_qubits)
            
            # Apply gates
            for gate in circuit.gates:
                if gate.control is not None:
                    if gate.gate_type == GateType.CNOT:
                        self._apply_cnot(gate.control, gate.target)
                else:
                    self._apply_single_gate(
                        gate.gate_type,
                        gate.target,
                        circuit.num_qubits,
                        gate.parameter,
                    )
            
            # Measure
            result = self._measure()
            bitstring = format(result, f'0{circuit.num_qubits}b')
            counts[bitstring] = counts.get(bitstring, 0) + 1
        
        return counts
    
    def _measure(self) -> int:
        """Measure all qubits."""
        probs = [abs(a) ** 2 for a in self._state]
        r = random.random()
        cumulative = 0.0
        for i, p in enumerate(probs):
            cumulative += p
            if r < cumulative:
                return i
        return len(probs) - 1


# Convenience functions
def bell_state() -> QuantumCircuit:
    """Create Bell state circuit."""
    return QuantumCircuit(2).h(0).cnot(0, 1).measure_all()


def ghz_state(n: int) -> QuantumCircuit:
    """Create GHZ state circuit."""
    circuit = QuantumCircuit(n).h(0)
    for i in range(n - 1):
        circuit.cnot(0, i + 1)
    return circuit.measure_all()


def qft(n: int) -> QuantumCircuit:
    """Quantum Fourier Transform circuit."""
    circuit = QuantumCircuit(n)
    for i in range(n):
        circuit.h(i)
        for j in range(i + 1, n):
            circuit.rz(j, math.pi / (2 ** (j - i)))
    return circuit


__all__ = [
    "QuantumCircuit",
    "QuantumSimulator",
    "Gate",
    "GateType",
    "Qubit",
    "bell_state",
    "ghz_state",
    "qft",
]
