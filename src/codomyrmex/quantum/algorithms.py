"""Common quantum algorithm circuits."""

import math

from .circuit import QuantumCircuit


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
