"""Tests for quantum algorithms."""

import math

import pytest

from codomyrmex.quantum.algorithms import (
    _apply_oracle,
    grover_diffusion,
    grover_search,
    inverse_qft,
    vqe_ansatz,
    w_state,
)
from codomyrmex.quantum.circuit import QuantumCircuit
from codomyrmex.quantum.models import GateType


@pytest.mark.unit
class TestWState:
    def test_w_state_creates_circuit(self):
        c = w_state(3)
        assert isinstance(c, QuantumCircuit)
        assert len(c.gates) > 0

    def test_w_state_invalid_qubits(self):
        with pytest.raises(ValueError):
            w_state(1)


@pytest.mark.unit
class TestInverseQFT:
    def test_inverse_qft_creates_circuit(self):
        c = inverse_qft(3)
        assert isinstance(c, QuantumCircuit)
        # Should have same number of gates as qft(3), which is 6
        assert len(c.gates) == 6


@pytest.mark.unit
class TestGrover:
    def test_grover_diffusion(self):
        c = grover_diffusion(3)
        assert isinstance(c, QuantumCircuit)

    def test_apply_oracle(self):
        c = QuantumCircuit(3)
        _apply_oracle(c, 3, 5)  # 5 is 101 in binary
        assert len(c.gates) > 0

    def test_grover_search(self):
        c = grover_search(3, 5)
        assert isinstance(c, QuantumCircuit)
        # Verify it has measurements
        assert len(c.measurements) == 3


@pytest.mark.unit
class TestVQEAnsatz:
    def test_vqe_ansatz_default(self):
        c = vqe_ansatz(4)
        assert isinstance(c, QuantumCircuit)

        # for n=4, depth=1:
        # rotation layer: 4 gates
        # entanglement layer: 3 CNOTs
        assert len(c.gates) == 7

    def test_vqe_ansatz_custom_params(self):
        params = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8]
        c = vqe_ansatz(4, depth=2, params=params)
        # depth=2: 4 rotations + 3 cnots + 4 rotations + 3 cnots = 14
        assert len(c.gates) == 14
