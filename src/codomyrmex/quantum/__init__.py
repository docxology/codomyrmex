"""
Quantum Computing Module

Quantum algorithm primitives, simulation, and circuit patterns.
"""

__version__ = "0.1.0"

from .algorithms import bell_state, ghz_state, qft
from .circuit import QuantumCircuit
from .models import Gate, GateType, Qubit
from .simulator import QuantumSimulator
from .visualization import circuit_stats, circuit_to_ascii

# Shared schemas for cross-module interop
try:
    from codomyrmex.validation.schemas import Result, ResultStatus
except ImportError:
    Result = None
    ResultStatus = None


from collections.abc import Callable
from typing import Any


def cli_commands() -> dict[str, Callable[[], None]]:
    """Return CLI commands for the quantum module."""

    def _backends() -> None:
        """List available simulator backends."""
        print("Quantum Simulator Backends")
        print(f"  Gate Types: {[gt.value for gt in GateType]}")
        print("  Available Algorithms: bell_state, ghz_state, qft")
        sim = QuantumSimulator()
        print(f"  Simulator: {sim.__class__.__name__}")

    def _simulate() -> None:
        """Run a quantum simulation (Bell state demo)."""
        print("Running Bell State simulation...")
        circuit = bell_state()
        sim = QuantumSimulator()
        sim.run(circuit)
        print(f"  Circuit:\n{circuit_to_ascii(circuit)}")
        stats = circuit_stats(circuit)
        for key, val in stats.items():
            print(f"  {key}: {val}")

    return {
        "backends": _backends,
        "simulate": _simulate,
    }


__all__ = [
    "Gate",
    "GateType",
    "QuantumCircuit",
    "QuantumSimulator",
    "Qubit",
    "bell_state",
    "circuit_stats",
    "circuit_to_ascii",
    "cli_commands",
    "ghz_state",
    "qft",
]
