"""PRISM Engine — Universal Coordinate System for Information.

Reimplements the core PRISM algebra from UOR Foundation using only stdlib.
Operates over the modular ring Z/(2^(8*(quantum+1)))Z with triadic
coordinates (datum, stratum, spectrum).

Critical Identity: neg(bnot(x)) = x + 1 mod 2^n

References:
    - https://github.com/UOR-Foundation/prism
    - https://github.com/UOR-Foundation/UOR-Framework
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class TriadicCoordinate:
    """The three coordinates of any datum in PRISM space.

    Attributes:
        datum: The identity — value as a tuple of bytes (big-endian).
        stratum: The magnitude — popcount (Hamming weight) per byte.
        spectrum: The structure — active bit positions per byte.
    """

    datum: tuple[int, ...]
    stratum: tuple[int, ...]
    spectrum: tuple[tuple[int, ...], ...]

    @property
    def total_stratum(self) -> int:
        """Total Hamming weight across all bytes."""
        return sum(self.stratum)

    @property
    def width(self) -> int:
        """Number of bytes in the datum."""
        return len(self.datum)


class PrismEngine:
    """Computation engine for the PRISM universal coordinate system.

    Operates over Z/(2^bits)Z where bits = 8 * (quantum + 1).

    Quantum levels:
        Q0: 8-bit   (256 states)
        Q1: 16-bit  (65,536 states)
        Q2: 24-bit  (16,777,216 states)
        Q3: 32-bit  (4,294,967,296 states)

    Signature Σ = {neg, bnot, xor, band, bor}
    Derived: succ = neg ∘ bnot, pred = bnot ∘ neg

    Args:
        quantum: Non-negative integer specifying the quantum level.
    """

    BYTE_BITS = 8
    BYTE_CYCLE = 256

    def __init__(self, quantum: int = 0) -> None:
        if quantum < 0:
            raise ValueError("Quantum must be non-negative")
        self.quantum = quantum
        self.width = quantum + 1
        self.bits = self.BYTE_BITS * self.width
        self.cycle = self.BYTE_CYCLE ** self.width
        self._mask = self.cycle - 1
        self._coherent = False

    # ═══════════════════════════════════════════════════════════════════════
    # REPRESENTATION
    # ═══════════════════════════════════════════════════════════════════════

    def _to_bytes(self, n: int) -> tuple[int, ...]:
        """Convert integer to byte tuple (big-endian), reduced mod cycle."""
        n &= self._mask
        return tuple(n.to_bytes(self.width, byteorder="big", signed=False))

    def _from_bytes(self, b: tuple[int, ...]) -> int:
        """Convert byte tuple to integer (big-endian)."""
        return int.from_bytes(b, byteorder="big")

    def _normalize(self, n: int | tuple[int, ...]) -> tuple[int, ...]:
        """Normalize input to validated byte tuple."""
        if isinstance(n, int):
            return self._to_bytes(n)
        b = tuple(n)
        if len(b) != self.width:
            raise ValueError(f"Expected {self.width} bytes, got {len(b)}")
        for i, x in enumerate(b):
            if not isinstance(x, int) or not (0 <= x <= 0xFF):
                raise ValueError(f"Byte {i} out of range: {x}")
        return b

    # ═══════════════════════════════════════════════════════════════════════
    # PRIMITIVE OPERATIONS
    # ═══════════════════════════════════════════════════════════════════════

    def neg(self, n: int | tuple[int, ...]) -> tuple[int, ...]:
        """Additive inverse (two's complement). Primitive involution.

        neg(neg(x)) = x for all x.
        """
        b = self._normalize(n)
        val = self._from_bytes(b)
        return self._to_bytes((-val) & self._mask)

    def bnot(self, n: int | tuple[int, ...]) -> tuple[int, ...]:
        """Bitwise complement (per byte). Primitive involution.

        bnot(bnot(x)) = x for all x.
        """
        b = self._normalize(n)
        return tuple(byte ^ 0xFF for byte in b)

    def xor(self, a: int | tuple[int, ...], b: int | tuple[int, ...]) -> tuple[int, ...]:
        """Bitwise XOR (per byte). Commutative, associative."""
        ba = self._normalize(a)
        bb = self._normalize(b)
        return tuple(x ^ y for x, y in zip(ba, bb, strict=False))

    def band(self, a: int | tuple[int, ...], b: int | tuple[int, ...]) -> tuple[int, ...]:
        """Bitwise AND (per byte). Commutative, associative."""
        ba = self._normalize(a)
        bb = self._normalize(b)
        return tuple(x & y for x, y in zip(ba, bb, strict=False))

    def bor(self, a: int | tuple[int, ...], b: int | tuple[int, ...]) -> tuple[int, ...]:
        """Bitwise OR (per byte). Commutative, associative."""
        ba = self._normalize(a)
        bb = self._normalize(b)
        return tuple(x | y for x, y in zip(ba, bb, strict=False))

    # ═══════════════════════════════════════════════════════════════════════
    # DERIVED OPERATIONS
    # ═══════════════════════════════════════════════════════════════════════

    def succ(self, n: int | tuple[int, ...]) -> tuple[int, ...]:
        """Increment. Derived: succ = neg ∘ bnot (CRITICAL IDENTITY)."""
        return self.neg(self.bnot(n))

    def pred(self, n: int | tuple[int, ...]) -> tuple[int, ...]:
        """Decrement. Derived: pred = bnot ∘ neg."""
        return self.bnot(self.neg(n))

    # ═══════════════════════════════════════════════════════════════════════
    # TRIADIC COORDINATES
    # ═══════════════════════════════════════════════════════════════════════

    @staticmethod
    def _byte_popcnt(n: int) -> int:
        """Population count (Hamming weight) of a single byte."""
        return n.bit_count()

    @staticmethod
    def _byte_basis(n: int) -> tuple[int, ...]:
        """Active bit positions in a single byte."""
        return tuple(i for i in range(8) if n & (1 << i))

    def stratum(self, n: int | tuple[int, ...]) -> tuple[int, ...]:
        """Compute stratum vector (popcount per byte)."""
        b = self._normalize(n)
        return tuple(self._byte_popcnt(byte) for byte in b)

    def spectrum(self, n: int | tuple[int, ...]) -> tuple[tuple[int, ...], ...]:
        """Compute spectrum (active bit positions per byte)."""
        b = self._normalize(n)
        return tuple(self._byte_basis(byte) for byte in b)

    def triad(self, n: int | tuple[int, ...]) -> TriadicCoordinate:
        """Compute complete triadic coordinates for a value.

        Args:
            n: Integer or byte tuple to compute coordinates for.

        Returns:
            TriadicCoordinate with datum, stratum, and spectrum.
        """
        b = self._normalize(n)
        return TriadicCoordinate(
            datum=b,
            stratum=self.stratum(b),
            spectrum=self.spectrum(b),
        )

    # ═══════════════════════════════════════════════════════════════════════
    # CORRELATION
    # ═══════════════════════════════════════════════════════════════════════

    def correlate(
        self,
        a: int | tuple[int, ...],
        b: int | tuple[int, ...],
    ) -> dict[str, Any]:
        """Measure correlation between two values via XOR-stratum (Hamming distance).

        Fidelity is 1.0 when values are identical, 0.0 when maximally different.

        Args:
            a: First value (integer or byte tuple).
            b: Second value (integer or byte tuple).

        Returns:
            Dict with keys: difference_stratum, total_difference,
            max_difference, fidelity.
        """
        ba = self._normalize(a)
        bb = self._normalize(b)
        na = self._from_bytes(ba)
        nb = self._from_bytes(bb)

        diff_int = (na ^ nb) & self._mask
        total_diff = diff_int.bit_count()
        max_stratum = self.bits
        fidelity = 1.0 - (total_diff / max_stratum)

        diff_bytes = self._to_bytes(diff_int)
        diff_stratum = tuple(byte.bit_count() for byte in diff_bytes)

        return {
            "a_datum": ba,
            "b_datum": bb,
            "difference_stratum": diff_stratum,
            "total_difference": total_diff,
            "max_difference": max_stratum,
            "fidelity": fidelity,
        }

    def fidelity(
        self,
        a: int | tuple[int, ...],
        b: int | tuple[int, ...],
    ) -> float:
        """Shorthand: return just the fidelity score between two values.

        Returns:
            Float in [0.0, 1.0] where 1.0 means identical.
        """
        return self.correlate(a, b)["fidelity"]

    # ═══════════════════════════════════════════════════════════════════════
    # COHERENCE VERIFICATION
    # ═══════════════════════════════════════════════════════════════════════

    def verify(self) -> bool:
        """Verify algebraic coherence at this quantum level.

        For Q0 (8-bit), performs exhaustive verification of all 256 states.
        For higher quantum levels, verifies composition laws on sampled values.

        Returns:
            True if all coherence checks pass.

        Raises:
            RuntimeError: If any algebraic law is violated.
        """
        self._verify_q0_exhaustive()

        if self.quantum > 0:
            self._verify_composition_laws()

        self._coherent = True
        return True

    def _verify_q0_exhaustive(self) -> bool:
        """Exhaustively verify all 256 states at Quantum 0."""
        from math import comb

        q0 = PrismEngine(quantum=0)

        for n in range(256):
            b = (n,)

            # Involution checks
            if q0.bnot(q0.bnot(b)) != b:
                raise RuntimeError(f"bnot not involution at {n}")
            if q0.neg(q0.neg(b)) != b:
                raise RuntimeError(f"neg not involution at {n}")

            # Critical identity: neg(bnot(x)) = x + 1
            expected_succ = q0._to_bytes((n + 1) & 0xFF)
            if q0.neg(q0.bnot(b)) != expected_succ:
                raise RuntimeError(f"Critical identity failed at {n}")

            # Derived ops
            expected_pred = q0._to_bytes((n - 1) & 0xFF)
            if q0.bnot(q0.neg(b)) != expected_pred:
                raise RuntimeError(f"pred identity failed at {n}")

            # Inverse roundtrips
            if q0.succ(q0.pred(b)) != b:
                raise RuntimeError(f"succ(pred({n})) != {n}")
            if q0.pred(q0.succ(b)) != b:
                raise RuntimeError(f"pred(succ({n})) != {n}")

            # XOR properties
            if q0.xor(b, q0.bnot(b)) != (0xFF,):
                raise RuntimeError(f"XOR complement failed at {n}")
            if q0.xor(b, b) != (0,):
                raise RuntimeError(f"XOR self-annihilation failed at {n}")

            # Additive inverse
            neg_n = q0.neg(b)
            total = (n + q0._from_bytes(neg_n)) & 0xFF
            if total != 0:
                raise RuntimeError(f"Additive inverse failed at {n}")

            # Stratum symmetry: popcount(x) + popcount(~x) = 8
            if q0._byte_popcnt(n) + q0._byte_popcnt(n ^ 0xFF) != 8:
                raise RuntimeError(f"Stratum symmetry failed at {n}")

            # Basis recomposition
            recomposed = 0
            for bit in q0._byte_basis(n):
                recomposed |= 1 << bit
            if recomposed != n:
                raise RuntimeError(f"Basis recomposition failed at {n}")

        # Full cycle check: succ generates the entire ring
        visited: set[tuple[int, ...]] = set()
        current = (0,)
        for _ in range(256):
            if current in visited:
                raise RuntimeError("Q0 cycle collapsed")
            visited.add(current)
            current = q0.succ(current)
        if current != (0,):
            raise RuntimeError("Q0 cycle did not return to origin")

        # Stratum distribution: C(8, k) values at each weight k
        counts = [0] * 9
        for n in range(256):
            counts[q0._byte_popcnt(n)] += 1
        for k in range(9):
            if counts[k] != comb(8, k):
                raise RuntimeError("Q0 stratum distribution failed")

        return True

    def _verify_composition_laws(self) -> bool:
        """Verify composition laws on sampled values for quantum > 0."""
        zero = tuple([0] * self.width)
        ones = tuple([0xFF] * self.width)
        mid = tuple([0x55] * self.width)
        alt = tuple([0xAA] * self.width)

        test_values = [zero, ones, mid, alt]

        for i in range(min(16, self.cycle)):
            test_values.append(self._to_bytes(i))
            test_values.append(self._to_bytes(self.cycle - 1 - i))

        for b in test_values:
            if self.bnot(self.bnot(b)) != b:
                raise RuntimeError(f"bnot not involution at {b}")
            if self.neg(self.neg(b)) != b:
                raise RuntimeError(f"neg not involution at {b}")
            if self.succ(self.pred(b)) != b:
                raise RuntimeError(f"succ(pred({b})) != {b}")
            if self.pred(self.succ(b)) != b:
                raise RuntimeError(f"pred(succ({b})) != {b}")
            if self.xor(b, self.bnot(b)) != ones:
                raise RuntimeError(f"XOR complement failed at {b}")
            if self.xor(b, b) != zero:
                raise RuntimeError(f"XOR self-annihilation failed at {b}")

            # Stratum symmetry
            s1 = sum(self.stratum(b))
            s2 = sum(self.stratum(self.bnot(b)))
            if s1 + s2 != 8 * self.width:
                raise RuntimeError(f"Stratum symmetry failed at {b}")

        # Boundary: carry/borrow propagation
        if self.succ(ones) != zero:
            raise RuntimeError("Carry propagation failed at max")
        if self.pred(zero) != ones:
            raise RuntimeError("Borrow propagation failed at zero")

        # Additive inverse
        for b in test_values:
            neg_b = self.neg(b)
            if (self._from_bytes(b) + self._from_bytes(neg_b)) & self._mask != 0:
                raise RuntimeError(f"Additive inverse failed at {b}")

        # Critical identity on sampled values
        for b in test_values:
            n = self._from_bytes(b)
            if self.neg(self.bnot(b)) != self._to_bytes((n + 1) & self._mask):
                raise RuntimeError(f"Critical identity (succ) failed at {b}")
            if self.bnot(self.neg(b)) != self._to_bytes((n - 1) & self._mask):
                raise RuntimeError(f"Critical identity (pred) failed at {b}")

        return True

    @property
    def is_coherent(self) -> bool:
        """Whether verify() has been called and passed."""
        return self._coherent

    def __repr__(self) -> str:
        """repr ."""
        status = "verified" if self._coherent else "unverified"
        return f"PrismEngine(quantum={self.quantum}, bits={self.bits}, {status})"

    def __eq__(self, other: object) -> bool:
        """eq ."""
        if not isinstance(other, PrismEngine):
            return NotImplemented
        return self.quantum == other.quantum

    def __hash__(self) -> int:
        """hash ."""
        return hash(self.quantum)
