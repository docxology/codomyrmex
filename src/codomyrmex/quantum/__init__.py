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

# Shared schemas for cross-module interop
try:
    from codomyrmex.validation.schemas import Result, ResultStatus
except ImportError:
    Result = None
    ResultStatus = None


def cli_commands():
    """Return CLI commands for the quantum module."""

    def _backends():
        """List available simulator backends."""
        print("Quantum Simulator Backends")
        print(f"  Gate Types: {[gt.value for gt in GateType]}")
        print(f"  Available Algorithms: bell_state, ghz_state, qft")
        sim = QuantumSimulator()
        print(f"  Simulator: {sim.__class__.__name__}")

    def _simulate():
        """Run a quantum simulation (Bell state demo)."""
        print("Running Bell State simulation...")
        circuit = bell_state()
        sim = QuantumSimulator()
        result = sim.run(circuit)
        print(f"  Circuit:\n{circuit_to_ascii(circuit)}")
        stats = circuit_stats(circuit)
        for key, val in stats.items():
            print(f"  {key}: {val}")

    return {
        "backends": _backends,
        "simulate": _simulate,
    }


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
    "cli_commands",
]
