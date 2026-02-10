"""Quantum computing models and data types."""

import math
import random
from dataclasses import dataclass
from enum import Enum


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
    control: int | None = None
    parameter: float | None = None


@dataclass
class Qubit:
    """A quantum bit state."""
    alpha: complex = 1.0 + 0j  # |0> amplitude
    beta: complex = 0.0 + 0j  # |1> amplitude

    @classmethod
    def zero(cls) -> "Qubit":
        return cls(1.0 + 0j, 0.0 + 0j)

    @classmethod
    def one(cls) -> "Qubit":
        return cls(0.0 + 0j, 1.0 + 0j)

    @classmethod
    def plus(cls) -> "Qubit":
        """|+> state."""
        s = 1 / math.sqrt(2)
        return cls(s + 0j, s + 0j)

    @classmethod
    def minus(cls) -> "Qubit":
        """|-> state."""
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
