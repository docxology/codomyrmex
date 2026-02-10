"""
Quantum Computing Module

Quantum algorithm primitives, simulation, and circuit patterns.
"""

__version__ = "0.1.0"

from .models import Gate, GateType, Qubit
from .circuit import QuantumCircuit
from .simulator import QuantumSimulator
from .algorithms import bell_state, ghz_state, qft
from .visualization import circuit_to_ascii, circuit_stats

__all__ = [
    "QuantumCircuit",
    "QuantumSimulator",
    "Gate",
    "GateType",
    "Qubit",
    "bell_state",
    "ghz_state",
    "qft",
    "circuit_to_ascii",
    "circuit_stats",
]
