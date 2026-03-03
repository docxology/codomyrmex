"""Statevector quantum simulator."""

import cmath
import math
import random

from .circuit import QuantumCircuit
from .models import GateType


class QuantumSimulator:
    """Simple statevector quantum simulator."""

    def __init__(self) -> None:
        self._state: list[complex] = []

    def _init_state(self, num_qubits: int) -> None:
        """Initialize to |00...0> state."""
        self._state = [0 + 0j] * (2**num_qubits)
        self._state[0] = 1 + 0j

    def _apply_single_gate(
        self, gate: GateType, target: int, num_qubits: int, param: float | None = None
    ) -> None:
        """Apply a single-qubit gate to the current statevector.

        Args:
            gate: The type of gate to apply.
            target: The index of the target qubit.
            num_qubits: Total number of qubits in the system.
            param: Optional parameter for rotation gates.
        """
        # Gate matrices
        sqrt2 = math.sqrt(2)
        matrices: dict[GateType, list[list[complex]]] = {
            GateType.H: [
                [1 / sqrt2 + 0j, 1 / sqrt2 + 0j],
                [1 / sqrt2 + 0j, -1 / sqrt2 + 0j],
            ],
            GateType.X: [[0j, 1 + 0j], [1 + 0j, 0j]],
            GateType.Y: [[0j, -1j], [1j, 0j]],
            GateType.Z: [[1 + 0j, 0j], [0j, -1 + 0j]],
            GateType.S: [[1 + 0j, 0j], [0j, 1j]],
            GateType.T: [[1 + 0j, 0j], [0j, cmath.exp(1j * math.pi / 4)]],
        }

        if gate in matrices:
            matrix = matrices[gate]
        elif gate == GateType.RX and param is not None:
            c, s = math.cos(param / 2), math.sin(param / 2)
            matrix = [[c + 0j, -1j * s], [-1j * s, c + 0j]]
        elif gate == GateType.RY and param is not None:
            c, s = math.cos(param / 2), math.sin(param / 2)
            matrix = [[c + 0j, -s + 0j], [s + 0j, c + 0j]]
        elif gate == GateType.RZ and param is not None:
            e = cmath.exp(1j * param / 2)
            matrix = [[1 / e, 0j], [0j, e]]
        else:
            return

        new_state = [0 + 0j] * len(self._state)
        for i in range(len(self._state)):
            bit = (i >> target) & 1
            i0 = i & ~(1 << target)
            i1 = i | (1 << target)

            if bit == 0:
                new_state[i0] += (
                    matrix[0][0] * self._state[i0] + matrix[0][1] * self._state[i1]
                )
                new_state[i1] += (
                    matrix[1][0] * self._state[i0] + matrix[1][1] * self._state[i1]
                )

        self._state = new_state

    def _apply_cnot(self, control: int, target: int) -> None:
        """Apply a CNOT (Controlled-NOT) gate to the current statevector.

        Args:
            control: The index of the control qubit.
            target: The index of the target qubit.
        """
        new_state = list(self._state)
        for i in range(len(self._state)):
            if (i >> control) & 1:
                j = i ^ (1 << target)
                new_state[i] = self._state[j]
                new_state[j] = self._state[i]
        self._state = new_state

    def _apply_swap(self, qubit1: int, qubit2: int) -> None:
        """Apply a SWAP gate by exchanging the amplitudes of two qubits.

        Args:
            qubit1: The index of the first qubit to swap.
            qubit2: The index of the second qubit to swap.
        """
        new_state = list(self._state)
        for i in range(len(self._state)):
            bit1 = (i >> qubit1) & 1
            bit2 = (i >> qubit2) & 1
            if bit1 != bit2:
                j = i ^ (1 << qubit1) ^ (1 << qubit2)
                new_state[i] = self._state[j]
                new_state[j] = self._state[i]
        self._state = new_state

    def run(self, circuit: QuantumCircuit, shots: int = 1024) -> dict[str, int]:
        """Run circuit and return measurement counts."""
        counts: dict[str, int] = {}

        for _ in range(shots):
            self._init_state(circuit.num_qubits)

            # Apply gates
            for gate in circuit.gates:
                if gate.control is not None:
                    if gate.gate_type == GateType.CNOT:
                        self._apply_cnot(gate.control, gate.target)
                    elif gate.gate_type == GateType.SWAP:
                        self._apply_swap(gate.control, gate.target)
                else:
                    self._apply_single_gate(
                        gate.gate_type,
                        gate.target,
                        circuit.num_qubits,
                        gate.parameter,
                    )

            # Measure
            result = self._measure()
            bitstring = format(result, f"0{circuit.num_qubits}b")
            counts[bitstring] = counts.get(bitstring, 0) + 1

        return counts

    def _measure(self) -> int:
        """Measure all qubits in the computational basis.

        Returns:
            An integer representing the measured multi-qubit bitstring.
        """
        probs = [abs(a) ** 2 for a in self._state]
        r = random.random()
        cumulative = 0.0
        for i, p in enumerate(probs):
            cumulative += p
            if r < cumulative:
                return i
        return len(probs) - 1
