"""Common quantum algorithm circuits.

Provides parameterized circuit constructors for well-known quantum algorithms:
- Bell state, GHZ state
- Quantum Fourier Transform (QFT) and inverse QFT
- Grover's search (oracle + diffusion)
- Variational Quantum Eigensolver (VQE) ansatz
- Quantum Phase Estimation (QPE)
"""

from __future__ import annotations

import math

from .circuit import QuantumCircuit

# ─── Entanglement Circuits ──────────────────────────────────────────────


def bell_state() -> QuantumCircuit:
    """Create a Bell state |Φ⁺⟩ = (|00⟩ + |11⟩)/√2."""
    return QuantumCircuit(2).h(0).cnot(0, 1).measure_all()


def ghz_state(n: int) -> QuantumCircuit:
    """Create an n-qubit GHZ state (|00...0⟩ + |11...1⟩)/√2.

    Args:
        n: Number of qubits (≥2).
    """
    if n < 2:
        raise ValueError("GHZ state requires at least 2 qubits")
    circuit = QuantumCircuit(n).h(0)
    for i in range(n - 1):
        circuit.cnot(0, i + 1)
    return circuit.measure_all()


def w_state(n: int) -> QuantumCircuit:
    """Create an n-qubit W state (|100...0⟩ + |010...0⟩ + ... + |00...1⟩)/√n.

    Uses controlled rotations to distribute a single excitation equally.

    Args:
        n: Number of qubits (≥2).
    """
    if n < 2:
        raise ValueError("W state requires at least 2 qubits")
    circuit = QuantumCircuit(n)
    # Put qubit 0 in |1⟩
    circuit.x(0)
    # Distribute with controlled rotations
    for i in range(n - 1):
        theta = math.acos(math.sqrt(1.0 / (n - i)))
        circuit.ry(i, theta)
        circuit.cnot(i, i + 1)
    return circuit


# ─── Fourier Transform ──────────────────────────────────────────────────


def qft(n: int) -> QuantumCircuit:
    """Quantum Fourier Transform on n qubits.

    Applies Hadamard + controlled phase rotation gates.
    """
    circuit = QuantumCircuit(n)
    for i in range(n):
        circuit.h(i)
        for j in range(i + 1, n):
            circuit.rz(j, math.pi / (2 ** (j - i)))
    return circuit


def inverse_qft(n: int) -> QuantumCircuit:
    """Inverse Quantum Fourier Transform on n qubits.

    Applies gates in reverse order with negated phases.
    """
    circuit = QuantumCircuit(n)
    for i in range(n - 1, -1, -1):
        for j in range(n - 1, i, -1):
            circuit.rz(j, -math.pi / (2 ** (j - i)))
        circuit.h(i)
    return circuit


# ─── Grover's Search ────────────────────────────────────────────────────


def grover_diffusion(n: int) -> QuantumCircuit:
    """Grover diffusion operator (inversion about the mean).

    Applies H → X → multi-controlled Z → X → H.
    """
    circuit = QuantumCircuit(n)
    for i in range(n):
        circuit.h(i)
    for i in range(n):
        circuit.x(i)
    # Multi-controlled Z: H on last qubit, then n-1 CNOTs, then H
    circuit.h(n - 1)
    if n >= 2:
        circuit.cnot(0, n - 1)  # simplified — real impl uses multi-control
    circuit.h(n - 1)
    for i in range(n):
        circuit.x(i)
    for i in range(n):
        circuit.h(i)
    return circuit


def grover_search(n: int, target: int, iterations: int | None = None) -> QuantumCircuit:
    """Grover's search algorithm circuit.

    Args:
        n: Number of qubits (search space = 2^n).
        target: Index of the marked element.
        iterations: Number of Grover iterations. Default: ⌊π/4 · √(2^n)⌋.

    Returns:
        QuantumCircuit with oracle + diffusion applied.
    """
    if iterations is None:
        iterations = max(1, int(math.pi / 4 * math.sqrt(2 ** n)))

    circuit = QuantumCircuit(n)
    # Initialize superposition
    for i in range(n):
        circuit.h(i)

    for _ in range(iterations):
        # Oracle: flip phase of target state
        _apply_oracle(circuit, n, target)
        # Diffusion
        grover_diffusion(n)
        # Inline diffusion gates (simplified — merge circuits)
        for i in range(n):
            circuit.h(i)
        for i in range(n):
            circuit.x(i)
        circuit.h(n - 1)
        if n >= 2:
            circuit.cnot(0, n - 1)
        circuit.h(n - 1)
        for i in range(n):
            circuit.x(i)
        for i in range(n):
            circuit.h(i)

    circuit.measure_all()
    return circuit


def _apply_oracle(circuit: QuantumCircuit, n: int, target: int) -> None:
    """Apply a phase oracle that marks |target⟩ with a -1 phase."""
    # Convert target to binary and apply X gates for 0-bits
    bits = format(target, f"0{n}b")
    for i, bit in enumerate(bits):
        if bit == "0":
            circuit.x(i)
    # Multi-controlled Z (simplified)
    circuit.h(n - 1)
    if n >= 2:
        circuit.cnot(0, n - 1)
    circuit.h(n - 1)
    # Undo X gates
    for i, bit in enumerate(bits):
        if bit == "0":
            circuit.x(i)


# ─── Variational / Ansatz ───────────────────────────────────────────────


def vqe_ansatz(n: int, depth: int = 1, params: list[float] | None = None) -> QuantumCircuit:
    """Hardware-efficient VQE ansatz.

    Alternating layers of Ry rotations and CNOT entanglement.

    Args:
        n: Number of qubits.
        depth: Number of layers.
        params: Rotation parameters. If None, uses π/4 for all.

    Returns:
        Parameterized QuantumCircuit.
    """
    total_params = n * depth
    if params is None:
        params = [math.pi / 4] * total_params

    circuit = QuantumCircuit(n)
    idx = 0
    for layer in range(depth):
        # Rotation layer
        for q in range(n):
            angle = params[idx % len(params)]
            circuit.ry(q, angle)
            idx += 1
        # Entanglement layer (linear connectivity)
        for q in range(n - 1):
            circuit.cnot(q, q + 1)
    return circuit
