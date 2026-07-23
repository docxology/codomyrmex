"""Authenticated, append-only execution evidence for the Colony Kernel.

The ordinary kernel API records caller-reported consequences.  This module is
the opt-in evidence boundary for experiments that need to distinguish a gate
verdict from an authorization, an execution receipt, and an observed outcome.

The default signer is HMAC-SHA256 because it is available in the standard
library and matches the repository's existing task-attestation primitive.  An
optional Ed25519 signer is provided when ``cryptography`` is installed.  HMAC
proves integrity to a shared authority; it is not a non-repudiation claim.
"""

from __future__ import annotations

import hashlib
import hmac
import json
import os
import sqlite3
import threading
import time
import uuid
from collections.abc import Callable
from dataclasses import dataclass, field
from enum import StrEnum
from pathlib import Path
from typing import Any, Protocol

LEDGER_SCHEMA_VERSION = "1.0"


class LedgerEventType(StrEnum):
    """Lifecycle events accepted by the authenticated evidence ledger."""

    PROPOSAL = "proposal"
    GATE_VERDICT = "gate_verdict"
    EXECUTION_AUTHORIZATION = "execution_authorization"
    EXECUTION_RECEIPT = "execution_receipt"
    OUTCOME = "outcome"
    REJECTION = "rejection"
    ERROR = "error"


class LedgerValidationStatus(StrEnum):
    """Machine-readable validation outcomes."""

    VALID = "valid"
    EMPTY = "empty"
    BAD_HASH = "bad_hash"
    BAD_SIGNATURE = "bad_signature"
    DUPLICATE = "duplicate"
    REPLAY = "replay"
    MISSING_PARENT = "missing_parent"
    SEQUENCE_GAP = "sequence_gap"
    UNAUTHORIZED_LINK = "unauthorized_link"
    INCOMPLETE_EXECUTION = "incomplete_execution"


class LedgerError(ValueError):
    """Base error for malformed or unauthorised ledger operations."""


class Signer(Protocol):
    """Minimal signer/verifier protocol used by :class:`AttestationLedger`."""

    algorithm: str
    key_id: str

    def sign(self, payload: bytes) -> dict[str, str]: ...

    def verify(self, payload: bytes, signature: dict[str, str]) -> bool: ...


def canonical_json(value: Any) -> bytes:
    """Encode JSON deterministically for hashes and signatures."""

    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
        default=str,
    ).encode("utf-8")


def digest_json(value: Any) -> str:
    """Return a full SHA-256 digest for a JSON-compatible value."""

    return hashlib.sha256(canonical_json(value)).hexdigest()


class HMACSigner:
    """Shared-key HMAC-SHA256 signer for local or controlled experiments."""

    algorithm = "hmac-sha256"

    def __init__(self, secret_key: bytes | str, key_id: str = "default") -> None:
        self._key = (
            secret_key.encode("utf-8") if isinstance(secret_key, str) else secret_key
        )
        if len(self._key) < 16:
            raise ValueError("HMAC attestation keys must contain at least 16 bytes")
        if not key_id:
            raise ValueError("key_id must be non-empty")
        self.key_id = key_id

    def sign(self, payload: bytes) -> dict[str, str]:
        return {
            "algorithm": self.algorithm,
            "key_id": self.key_id,
            "value": hmac.new(self._key, payload, hashlib.sha256).hexdigest(),
        }

    def verify(self, payload: bytes, signature: dict[str, str]) -> bool:
        if signature.get("algorithm") != self.algorithm:
            return False
        if signature.get("key_id") != self.key_id:
            return False
        expected = hmac.new(self._key, payload, hashlib.sha256).hexdigest()
        return hmac.compare_digest(expected, str(signature.get("value", "")))


class Ed25519Signer:
    """Optional independently verifiable signer backed by ``cryptography``.

    The import is delayed so the offline default remains usable without the
    optional dependency.  Private keys are supplied as raw 32-byte material;
    callers are responsible for secure key storage.
    """

    algorithm = "ed25519"

    def __init__(self, private_key: bytes, key_id: str = "default") -> None:
        if len(private_key) != 32:
            raise ValueError("Ed25519 private keys must contain 32 raw bytes")
        try:
            from cryptography.hazmat.primitives.asymmetric.ed25519 import (
                Ed25519PrivateKey,
            )
        except ImportError as exc:  # pragma: no cover - depends on optional extra
            raise RuntimeError(
                "Ed25519 attestation requires the cryptography dependency"
            ) from exc
        self._private = Ed25519PrivateKey.from_private_bytes(private_key)
        self._public = self._private.public_key()
        self.key_id = key_id

    @classmethod
    def generate(cls, key_id: str = "default") -> Ed25519Signer:
        try:
            from cryptography.hazmat.primitives.asymmetric.ed25519 import (
                Ed25519PrivateKey,
            )
        except ImportError as exc:  # pragma: no cover - depends on optional extra
            raise RuntimeError(
                "Ed25519 attestation requires the cryptography dependency"
            ) from exc
        private = Ed25519PrivateKey.generate()
        raw = private.private_bytes_raw()
        return cls(raw, key_id=key_id)

    def public_key_bytes(self) -> bytes:
        from cryptography.hazmat.primitives import serialization

        return self._public.public_bytes(
            encoding=serialization.Encoding.Raw,
            format=serialization.PublicFormat.Raw,
        )

    def sign(self, payload: bytes) -> dict[str, str]:
        return {
            "algorithm": self.algorithm,
            "key_id": self.key_id,
            "value": self._private.sign(payload).hex(),
            "public_key": self.public_key_bytes().hex(),
        }

    def verify(self, payload: bytes, signature: dict[str, str]) -> bool:
        return Ed25519Verifier(self.public_key_bytes(), key_id=self.key_id).verify(
            payload, signature
        )


class Ed25519Verifier:
    """Optional public-key-only verifier for exported ledger artifacts."""

    algorithm = "ed25519"

    def __init__(self, public_key: bytes, key_id: str = "default") -> None:
        if len(public_key) != 32:
            raise ValueError("Ed25519 public keys must contain 32 raw bytes")
        try:
            from cryptography.hazmat.primitives.asymmetric.ed25519 import (
                Ed25519PublicKey,
            )
        except ImportError as exc:  # pragma: no cover - optional dependency
            raise RuntimeError(
                "Ed25519 attestation requires the cryptography dependency"
            ) from exc
        self._public = Ed25519PublicKey.from_public_bytes(public_key)
        self._public_bytes = public_key
        self.key_id = key_id

    def verify(self, payload: bytes, signature: dict[str, str]) -> bool:
        if signature.get("algorithm") != self.algorithm:
            return False
        if signature.get("key_id") != self.key_id:
            return False
        if signature.get("public_key") != self._public_bytes.hex():
            return False
        from cryptography.exceptions import InvalidSignature

        try:
            self._public.verify(bytes.fromhex(str(signature.get("value", ""))), payload)
        except (InvalidSignature, ValueError, TypeError):
            return False
        return True


@dataclass(frozen=True)
class LedgerEvent:
    """Immutable event envelope stored in the append-only ledger."""

    run_id: str
    sequence: int
    event_type: LedgerEventType
    actor_id: str
    nonce: str
    payload: dict[str, Any]
    previous_hash: str = ""
    event_id: str = field(default_factory=lambda: f"evt-{uuid.uuid4().hex}")
    created_at: float | None = None
    event_hash: str = ""
    signature: dict[str, str] = field(default_factory=dict)

    def unsigned_dict(self) -> dict[str, Any]:
        return {
            "schema_version": LEDGER_SCHEMA_VERSION,
            "run_id": self.run_id,
            "sequence": self.sequence,
            "event_type": self.event_type.value,
            "actor_id": self.actor_id,
            "nonce": self.nonce,
            "payload": self.payload,
            "previous_hash": self.previous_hash,
            "event_id": self.event_id,
            "created_at": self.created_at,
        }

    def computed_hash(self) -> str:
        return hashlib.sha256(canonical_json(self.unsigned_dict())).hexdigest()

    def signing_bytes(self) -> bytes:
        return canonical_json(
            {**self.unsigned_dict(), "event_hash": self.computed_hash()}
        )

    def with_signature(self, signer: Signer) -> LedgerEvent:
        event_hash = self.computed_hash()
        signed_payload = canonical_json(
            {**self.unsigned_dict(), "event_hash": event_hash}
        )
        return LedgerEvent(
            **{
                **self.__dict__,
                "event_hash": event_hash,
                "signature": signer.sign(signed_payload),
            }
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            **self.unsigned_dict(),
            "event_hash": self.event_hash,
            "signature": self.signature,
        }

    @classmethod
    def from_dict(cls, value: dict[str, Any]) -> LedgerEvent:
        return cls(
            run_id=str(value["run_id"]),
            sequence=int(value["sequence"]),
            event_type=LedgerEventType(value["event_type"]),
            actor_id=str(value["actor_id"]),
            nonce=str(value["nonce"]),
            payload=dict(value.get("payload", {})),
            previous_hash=str(value.get("previous_hash", "")),
            event_id=str(value["event_id"]),
            created_at=value.get("created_at"),
            event_hash=str(value.get("event_hash", "")),
            signature=dict(value.get("signature", {})),
        )


@dataclass(frozen=True)
class LedgerValidationResult:
    """Validation report with an explicit claim boundary."""

    valid: bool
    status: LedgerValidationStatus
    run_id: str
    event_count: int
    errors: tuple[str, ...] = ()
    last_valid_sequence: int = 0

    def to_dict(self) -> dict[str, Any]:
        return {
            "valid": self.valid,
            "status": self.status.value,
            "run_id": self.run_id,
            "event_count": self.event_count,
            "errors": list(self.errors),
            "last_valid_sequence": self.last_valid_sequence,
        }


_SCHEMA = """
CREATE TABLE IF NOT EXISTS ledger_events (
    event_id TEXT PRIMARY KEY,
    run_id TEXT NOT NULL,
    sequence INTEGER NOT NULL,
    event_type TEXT NOT NULL,
    actor_id TEXT NOT NULL,
    nonce TEXT NOT NULL,
    previous_hash TEXT NOT NULL,
    payload_json TEXT NOT NULL,
    created_at REAL,
    event_hash TEXT NOT NULL UNIQUE,
    signature_json TEXT NOT NULL,
    UNIQUE(run_id, sequence),
    UNIQUE(run_id, nonce)
);
CREATE INDEX IF NOT EXISTS idx_ledger_events_run ON ledger_events(run_id, sequence);
"""


class AttestationLedger:
    """SQLite-backed append-only evidence ledger.

    A ledger never claims that an action was safe or beneficial.  It verifies
    only that the recorded lifecycle is internally linked and authenticated by
    the configured signer.
    """

    def __init__(
        self,
        db_path: str | os.PathLike[str] = ":memory:",
        *,
        signer: Signer | None = None,
        clock: Callable[[], float] | None = None,
    ) -> None:
        self._signer = signer or HMACSigner(os.urandom(32), key_id="ephemeral")
        self._clock = clock or time.time
        self._lock = threading.RLock()
        self._conn = sqlite3.connect(
            os.fspath(db_path), check_same_thread=False, isolation_level=None
        )
        self._conn.execute("PRAGMA journal_mode=WAL")
        self._conn.execute("PRAGMA foreign_keys=ON")
        self._conn.execute("PRAGMA busy_timeout=5000")
        self._conn.executescript(_SCHEMA)

    @property
    def signer(self) -> Signer:
        return self._signer

    def close(self) -> None:
        with self._lock:
            self._conn.close()

    def _next_sequence(self, run_id: str) -> tuple[int, str]:
        row = self._conn.execute(
            "SELECT sequence, event_hash FROM ledger_events WHERE run_id=? ORDER BY sequence DESC LIMIT 1",
            (run_id,),
        ).fetchone()
        return (int(row[0]) + 1, str(row[1])) if row else (1, "")

    def append(self, event: LedgerEvent) -> LedgerEvent:
        """Validate and append one event, or return an identical idempotent retry."""

        if not event.run_id or not event.actor_id or not event.nonce:
            raise LedgerError("run_id, actor_id, and nonce are required")
        if event.event_hash != event.computed_hash():
            raise LedgerError("event hash does not match canonical event payload")
        if not event.signature or not self._signer.verify(
            event.signing_bytes(), event.signature
        ):
            raise LedgerError("event signature is invalid")

        with self._lock:
            try:
                self._conn.execute("BEGIN IMMEDIATE")
                existing = self._conn.execute(
                    "SELECT payload_json, event_hash FROM ledger_events WHERE event_id=?",
                    (event.event_id,),
                ).fetchone()
                if existing:
                    existing_payload = json.loads(existing[0])
                    if (
                        existing[1] == event.event_hash
                        and existing_payload == event.payload
                    ):
                        self._conn.execute("COMMIT")
                        return event
                    raise LedgerError("duplicate event_id with different event content")

                expected_sequence, expected_previous = self._next_sequence(event.run_id)
                if event.sequence != expected_sequence:
                    raise LedgerError(
                        f"sequence gap for {event.run_id}: expected {expected_sequence}, got {event.sequence}"
                    )
                if event.previous_hash != expected_previous:
                    raise LedgerError("previous_hash does not link to the latest event")
                self._conn.execute(
                    "INSERT INTO ledger_events VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                    (
                        event.event_id,
                        event.run_id,
                        event.sequence,
                        event.event_type.value,
                        event.actor_id,
                        event.nonce,
                        event.previous_hash,
                        json.dumps(
                            event.payload,
                            sort_keys=True,
                            separators=(",", ":"),
                            default=str,
                        ),
                        event.created_at,
                        event.event_hash,
                        json.dumps(
                            event.signature, sort_keys=True, separators=(",", ":")
                        ),
                    ),
                )
                self._conn.execute("COMMIT")
                return event
            except sqlite3.IntegrityError as exc:
                self._conn.execute("ROLLBACK")
                raise LedgerError(
                    "duplicate nonce, sequence, event_id, or event hash"
                ) from exc
            except Exception:
                self._conn.execute("ROLLBACK")
                raise

    def create_event(
        self,
        run_id: str,
        event_type: LedgerEventType,
        actor_id: str,
        payload: dict[str, Any],
        *,
        nonce: str | None = None,
        created_at: float | None = None,
    ) -> LedgerEvent:
        with self._lock:
            sequence, previous_hash = self._next_sequence(run_id)
        event = LedgerEvent(
            run_id=run_id,
            sequence=sequence,
            event_type=event_type,
            actor_id=actor_id,
            nonce=nonce or uuid.uuid4().hex,
            payload=dict(payload),
            previous_hash=previous_hash,
            created_at=self._clock() if created_at is None else created_at,
        )
        return event.with_signature(self._signer)

    def append_record(
        self,
        run_id: str,
        event_type: LedgerEventType,
        actor_id: str,
        payload: dict[str, Any],
        *,
        nonce: str | None = None,
        created_at: float | None = None,
    ) -> LedgerEvent:
        return self.append(
            self.create_event(
                run_id,
                event_type,
                actor_id,
                payload,
                nonce=nonce,
                created_at=created_at,
            )
        )

    def events(self, run_id: str) -> list[LedgerEvent]:
        rows = self._conn.execute(
            "SELECT run_id, sequence, event_type, actor_id, nonce, payload_json, previous_hash, event_id, created_at, event_hash, signature_json "
            "FROM ledger_events WHERE run_id=? ORDER BY sequence",
            (run_id,),
        ).fetchall()
        return [
            LedgerEvent(
                run_id=row[0],
                sequence=row[1],
                event_type=LedgerEventType(row[2]),
                actor_id=row[3],
                nonce=row[4],
                payload=json.loads(row[5]),
                previous_hash=row[6],
                event_id=row[7],
                created_at=row[8],
                event_hash=row[9],
                signature=json.loads(row[10]),
            )
            for row in rows
        ]

    def validate(self, run_id: str) -> LedgerValidationResult:
        events = self.events(run_id)
        if not events:
            return LedgerValidationResult(
                False, LedgerValidationStatus.EMPTY, run_id, 0
            )

        errors: list[str] = []
        previous_hash = ""
        expected_sequence = 1
        proposal_ids: set[str] = set()
        proposal_event_ids: set[str] = set()
        verdicts: dict[str, tuple[str, str]] = {}
        authorizations: set[str] = set()
        executions: set[str] = set()
        last_valid = 0

        for event in events:
            if event.sequence != expected_sequence:
                errors.append(f"sequence {event.sequence} expected {expected_sequence}")
                return LedgerValidationResult(
                    False,
                    LedgerValidationStatus.SEQUENCE_GAP,
                    run_id,
                    len(events),
                    tuple(errors),
                    last_valid,
                )
            if event.previous_hash != previous_hash:
                errors.append(f"event {event.event_id} has missing or incorrect parent")
                return LedgerValidationResult(
                    False,
                    LedgerValidationStatus.MISSING_PARENT,
                    run_id,
                    len(events),
                    tuple(errors),
                    last_valid,
                )
            if event.event_hash != event.computed_hash():
                errors.append(f"event {event.event_id} hash mismatch")
                return LedgerValidationResult(
                    False,
                    LedgerValidationStatus.BAD_HASH,
                    run_id,
                    len(events),
                    tuple(errors),
                    last_valid,
                )
            if not self._signer.verify(event.signing_bytes(), event.signature):
                errors.append(f"event {event.event_id} signature mismatch")
                return LedgerValidationResult(
                    False,
                    LedgerValidationStatus.BAD_SIGNATURE,
                    run_id,
                    len(events),
                    tuple(errors),
                    last_valid,
                )

            payload = event.payload
            if event.event_type == LedgerEventType.PROPOSAL:
                proposal_id = str(payload.get("proposal_id", ""))
                if not proposal_id or proposal_id in proposal_ids:
                    return LedgerValidationResult(
                        False,
                        LedgerValidationStatus.REPLAY,
                        run_id,
                        len(events),
                        ("proposal replay or missing proposal_id",),
                        last_valid,
                    )
                proposal_ids.add(proposal_id)
                proposal_event_ids.add(event.event_id)
            elif event.event_type == LedgerEventType.GATE_VERDICT:
                proposal_event = str(payload.get("proposal_event_id", ""))
                decision = str(payload.get("decision", ""))
                if proposal_event not in proposal_event_ids or decision not in {
                    "execute",
                    "hold",
                    "refuse",
                }:
                    return LedgerValidationResult(
                        False,
                        LedgerValidationStatus.UNAUTHORIZED_LINK,
                        run_id,
                        len(events),
                        ("gate verdict is not linked to a proposal",),
                        last_valid,
                    )
                verdicts[event.event_id] = (decision, proposal_event)
            elif event.event_type == LedgerEventType.EXECUTION_AUTHORIZATION:
                verdict_event = str(payload.get("gate_event_id", ""))
                if (
                    verdict_event not in verdicts
                    or verdicts[verdict_event][0] != "execute"
                ):
                    return LedgerValidationResult(
                        False,
                        LedgerValidationStatus.UNAUTHORIZED_LINK,
                        run_id,
                        len(events),
                        ("execution authorization lacks an EXECUTE verdict",),
                        last_valid,
                    )
                authorizations.add(event.event_id)
            elif event.event_type == LedgerEventType.EXECUTION_RECEIPT:
                authorization_event = str(payload.get("authorization_event_id", ""))
                if authorization_event not in authorizations:
                    return LedgerValidationResult(
                        False,
                        LedgerValidationStatus.UNAUTHORIZED_LINK,
                        run_id,
                        len(events),
                        ("execution receipt lacks authorization",),
                        last_valid,
                    )
                executions.add(event.event_id)
            elif event.event_type == LedgerEventType.OUTCOME:
                execution_event = str(payload.get("execution_event_id", ""))
                if execution_event not in executions:
                    return LedgerValidationResult(
                        False,
                        LedgerValidationStatus.INCOMPLETE_EXECUTION,
                        run_id,
                        len(events),
                        ("outcome lacks an execution receipt",),
                        last_valid,
                    )

            previous_hash = event.event_hash
            expected_sequence += 1
            last_valid = event.sequence

        return LedgerValidationResult(
            True,
            LedgerValidationStatus.VALID,
            run_id,
            len(events),
            tuple(errors),
            last_valid,
        )

    def record_proposal(
        self, run_id: str, actor_id: str, proposal: dict[str, Any]
    ) -> LedgerEvent:
        return self.append_record(
            run_id,
            LedgerEventType.PROPOSAL,
            actor_id,
            {
                "proposal_id": str(proposal["proposal_id"]),
                "proposal_digest": digest_json(proposal),
            },
        )

    def record_gate_verdict(
        self,
        run_id: str,
        actor_id: str,
        proposal_event: LedgerEvent,
        decision: str,
        gate: dict[str, Any],
    ) -> LedgerEvent:
        if decision not in {"execute", "hold", "refuse"}:
            raise LedgerError(f"unsupported gate decision: {decision}")
        return self.append_record(
            run_id,
            LedgerEventType.GATE_VERDICT,
            actor_id,
            {
                "proposal_event_id": proposal_event.event_id,
                "proposal_id": proposal_event.payload["proposal_id"],
                "decision": decision,
                "gate_digest": digest_json(gate),
            },
        )

    def authorize_execution(
        self, run_id: str, actor_id: str, gate_event: LedgerEvent
    ) -> LedgerEvent:
        if (
            gate_event.event_type != LedgerEventType.GATE_VERDICT
            or gate_event.payload.get("decision") != "execute"
        ):
            raise LedgerError("only an EXECUTE gate verdict can authorize execution")
        return self.append_record(
            run_id,
            LedgerEventType.EXECUTION_AUTHORIZATION,
            actor_id,
            {
                "gate_event_id": gate_event.event_id,
                "proposal_id": gate_event.payload["proposal_id"],
            },
        )

    def record_execution(
        self,
        run_id: str,
        actor_id: str,
        authorization_event: LedgerEvent,
        receipt: dict[str, Any],
    ) -> LedgerEvent:
        if authorization_event.event_type != LedgerEventType.EXECUTION_AUTHORIZATION:
            raise LedgerError("execution receipt requires an authorization event")
        return self.append_record(
            run_id,
            LedgerEventType.EXECUTION_RECEIPT,
            actor_id,
            {
                "authorization_event_id": authorization_event.event_id,
                "execution_id": str(receipt.get("execution_id", uuid.uuid4().hex)),
                "receipt_digest": digest_json(receipt),
            },
        )

    def record_outcome(
        self,
        run_id: str,
        actor_id: str,
        execution_event: LedgerEvent,
        outcome: dict[str, Any],
    ) -> LedgerEvent:
        if (
            not isinstance(execution_event, LedgerEvent)
            or execution_event.event_type != LedgerEventType.EXECUTION_RECEIPT
        ):
            raise LedgerError("outcome requires an execution receipt")
        return self.append_record(
            run_id,
            LedgerEventType.OUTCOME,
            actor_id,
            {
                "execution_event_id": execution_event.event_id,
                "outcome_digest": digest_json(outcome),
            },
        )

    def record_rejection(
        self,
        run_id: str,
        actor_id: str,
        proposal_event: LedgerEvent,
        reason: str,
    ) -> LedgerEvent:
        """Record a refusal/hold without granting execution authority."""

        if proposal_event.event_type != LedgerEventType.PROPOSAL:
            raise LedgerError("rejection requires a proposal event")
        return self.append_record(
            run_id,
            LedgerEventType.REJECTION,
            actor_id,
            {
                "proposal_event_id": proposal_event.event_id,
                "proposal_id": proposal_event.payload["proposal_id"],
                "reason": reason,
            },
        )

    def record_error(
        self,
        run_id: str,
        actor_id: str,
        parent_event: LedgerEvent | None,
        error: str,
    ) -> LedgerEvent:
        """Record an execution/ledger error as evidence, never as success."""

        if parent_event is not None and parent_event.run_id != run_id:
            raise LedgerError("error parent belongs to a different run")
        return self.append_record(
            run_id,
            LedgerEventType.ERROR,
            actor_id,
            {
                "parent_event_id": parent_event.event_id if parent_event else None,
                "error": error,
            },
        )


__all__ = [
    "LEDGER_SCHEMA_VERSION",
    "AttestationLedger",
    "Ed25519Signer",
    "Ed25519Verifier",
    "HMACSigner",
    "LedgerError",
    "LedgerEvent",
    "LedgerEventType",
    "LedgerValidationResult",
    "LedgerValidationStatus",
    "canonical_json",
    "digest_json",
]
