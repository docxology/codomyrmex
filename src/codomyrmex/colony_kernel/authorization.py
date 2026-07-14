"""Signed execution capabilities and atomic authorization ledger.

The advisory Colony Kernel can still return a gate decision without an
authorization.  The strict profile uses this module to make an EXECUTE result
necessary but insufficient: an executor must present a valid, scoped,
unexpired, single-use capability and then return a signed receipt.
"""

from __future__ import annotations

import base64
import hashlib
import json
import sqlite3
import time
import uuid
from collections.abc import Callable
from dataclasses import asdict, is_dataclass
from pathlib import Path, PurePosixPath
from typing import Any

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import (
    Ed25519PrivateKey,
    Ed25519PublicKey,
)

from codomyrmex.colony_kernel.models import (
    ActionProposal,
    AuthorizationStatus,
    ExecutionAuthorization,
    ExecutionReceipt,
    GateDecision,
    GateResult,
)


class AuthorizationError(RuntimeError):
    """Raised when a capability cannot be issued, consumed, or verified."""


DEFAULT_ACTION_SCOPE: dict[str, tuple[str, ...]] = {
    "patch_file": ("src/", "tests/", "docs/"),
    "run_tests": ("tests/",),
    "archive_module": ("src/codomyrmex/",),
}


def _json_value(value: Any) -> Any:
    if is_dataclass(value) and not isinstance(value, type):
        return {key: _json_value(item) for key, item in asdict(value).items()}
    if isinstance(value, dict):
        return {str(key): _json_value(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_json_value(item) for item in value]
    if hasattr(value, "value"):
        return value.value
    return value


def canonical_json(value: Any) -> bytes:
    """Serialize a capability/receipt payload deterministically."""

    return json.dumps(
        _json_value(value), sort_keys=True, separators=(",", ":"), ensure_ascii=True
    ).encode("utf-8")


def digest(value: Any) -> str:
    return hashlib.sha256(canonical_json(value)).hexdigest()


def scope_digest(action_type: str, target: str) -> str:
    return digest({"action_type": action_type, "target": target})


def target_in_scope(
    action_type: str,
    target: str,
    action_scope: dict[str, tuple[str, ...]] | None = None,
) -> bool:
    """Return whether an action/target pair is explicitly registered."""

    scope = DEFAULT_ACTION_SCOPE if action_scope is None else action_scope
    normalized = target.replace("\\", "/")
    path = PurePosixPath(normalized)
    # Scope matching is repository-relative.  Reject absolute paths and
    # traversal components before applying the governed prefix map; otherwise
    # ``src/../outside`` could appear to be an in-scope target while resolving
    # outside the declared boundary.
    if path.is_absolute() or ".." in path.parts:
        return False
    return action_type in scope and any(
        normalized.startswith(prefix) for prefix in scope[action_type]
    )


class Ed25519Authority:
    """Small signing authority used by issuers and registered executors.

    Production callers must load the private key from an external secret
    store. ``generate`` is intentionally explicit for tests and local
    development so a deployment cannot silently invent a new identity.
    """

    def __init__(self, private_key: Ed25519PrivateKey) -> None:
        self._private_key = private_key
        public_bytes = private_key.public_key().public_bytes(
            serialization.Encoding.Raw, serialization.PublicFormat.Raw
        )
        self.public_key = public_bytes
        self.key_id = hashlib.sha256(public_bytes).hexdigest()[:32]

    @classmethod
    def generate(cls) -> Ed25519Authority:
        return cls(Ed25519PrivateKey.generate())

    @classmethod
    def from_raw_private_bytes(cls, raw: bytes) -> Ed25519Authority:
        return cls(Ed25519PrivateKey.from_private_bytes(raw))

    @classmethod
    def from_file(cls, path: str | Path) -> Ed25519Authority:
        raw = Path(path).read_bytes()
        try:
            private = serialization.load_pem_private_key(raw, password=None)
        except ValueError:
            private = Ed25519PrivateKey.from_private_bytes(raw)
        if not isinstance(private, Ed25519PrivateKey):
            raise ValueError("authorization key must be an Ed25519 private key")
        return cls(private)

    def sign(self, payload: bytes) -> str:
        return base64.urlsafe_b64encode(self._private_key.sign(payload)).decode("ascii")

    def verify(self, payload: bytes, signature: str) -> bool:
        try:
            self._private_key.public_key().verify(
                base64.urlsafe_b64decode(signature.encode("ascii")), payload
            )
        except Exception:
            return False
        return True

    def verify_with_public_key(
        self, payload: bytes, signature: str, public_key: bytes
    ) -> bool:
        try:
            Ed25519PublicKey.from_public_bytes(public_key).verify(
                base64.urlsafe_b64decode(signature.encode("ascii")), payload
            )
        except Exception:
            return False
        return True


def _receipt_payload(receipt: ExecutionReceipt) -> dict[str, Any]:
    """Return the signed fields of an execution receipt."""

    return {
        "authorization_id": receipt.authorization_id,
        "proposal_id": receipt.proposal_id,
        "executor_id": receipt.executor_id,
        "action_digest": receipt.action_digest,
        "result_digest": receipt.result_digest,
        "started_at": receipt.started_at,
        "completed_at": receipt.completed_at,
        "exit_code": receipt.exit_code,
        "status": receipt.status,
        "executor_key_id": receipt.executor_key_id,
    }


def serialize_receipt(receipt: ExecutionReceipt) -> str:
    """Serialize a receipt for transport or durable evidence storage."""

    return json.dumps(
        {**_receipt_payload(receipt), "signature": receipt.signature},
        sort_keys=True,
        separators=(",", ":"),
    )


def deserialize_receipt(raw: str | dict[str, Any]) -> ExecutionReceipt:
    """Deserialize a receipt without treating it as verified evidence."""

    data = json.loads(raw) if isinstance(raw, str) else dict(raw)
    return ExecutionReceipt(**data)


def _authorization_payload(token: ExecutionAuthorization) -> dict[str, Any]:
    return {
        "authorization_id": token.authorization_id,
        "proposal_id": token.proposal_id,
        "agent_id": token.agent_id,
        "action_type": token.action_type,
        "target": token.target,
        "scope_digest": token.scope_digest,
        "issued_at": token.issued_at,
        "expires_at": token.expires_at,
        "nonce": token.nonce,
        "issuer_key_id": token.issuer_key_id,
    }


def serialize_authorization(token: ExecutionAuthorization) -> str:
    return json.dumps(
        {**_authorization_payload(token), "signature": token.signature, "status": token.status.value},
        sort_keys=True,
        separators=(",", ":"),
    )


def deserialize_authorization(raw: str | dict[str, Any]) -> ExecutionAuthorization:
    data = json.loads(raw) if isinstance(raw, str) else dict(raw)
    data["status"] = AuthorizationStatus(data.get("status", AuthorizationStatus.ISSUED.value))
    return ExecutionAuthorization(**data)


class AuthorizationLedger:
    """SQLite ledger with atomic single-use capability consumption."""

    def __init__(
        self,
        db_path: str = ":memory:",
        *,
        issuer: Ed25519Authority,
        action_scope: dict[str, tuple[str, ...]] | None = None,
        ttl_seconds: float = 60.0,
    ) -> None:
        self.db_path = db_path
        self.issuer = issuer
        self.action_scope = action_scope or DEFAULT_ACTION_SCOPE
        self.ttl_seconds = ttl_seconds
        self._trusted_issuer_keys: dict[str, bytes] = {
            issuer.key_id: issuer.public_key
        }
        self._conn = sqlite3.connect(db_path, check_same_thread=False, timeout=10.0)
        self._conn.execute("PRAGMA busy_timeout=10000")
        if db_path != ":memory:":
            self._conn.execute("PRAGMA journal_mode=WAL")
        self._conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS execution_authorizations (
                authorization_id TEXT PRIMARY KEY,
                proposal_id TEXT NOT NULL UNIQUE,
                nonce TEXT NOT NULL UNIQUE,
                token_json TEXT NOT NULL,
                status TEXT NOT NULL,
                issued_at REAL NOT NULL,
                expires_at REAL NOT NULL,
                consumed_at REAL
            );
            CREATE TABLE IF NOT EXISTS action_proposals (
                proposal_id TEXT PRIMARY KEY,
                agent_id TEXT NOT NULL,
                action_type TEXT NOT NULL,
                target TEXT NOT NULL,
                proposal_json TEXT NOT NULL,
                recorded_at REAL NOT NULL
            );
            CREATE TABLE IF NOT EXISTS execution_receipts (
                authorization_id TEXT PRIMARY KEY,
                proposal_id TEXT NOT NULL UNIQUE,
                receipt_json TEXT NOT NULL,
                recorded_at REAL NOT NULL
            );
            CREATE TABLE IF NOT EXISTS quarantined_reports (
                report_id TEXT PRIMARY KEY,
                agent_id TEXT NOT NULL,
                action_type TEXT NOT NULL,
                target TEXT NOT NULL,
                report_json TEXT NOT NULL,
                recorded_at REAL NOT NULL
            );
            CREATE TABLE IF NOT EXISTS outcome_reports (
                report_id TEXT PRIMARY KEY,
                proposal_id TEXT NOT NULL UNIQUE,
                authorization_id TEXT NOT NULL UNIQUE,
                evidence_grade TEXT NOT NULL,
                report_json TEXT NOT NULL,
                recorded_at REAL NOT NULL
            );
            """
        )
        self._conn.commit()

    def issue(self, proposal: ActionProposal, result: GateResult) -> ExecutionAuthorization:
        if result.decision is not GateDecision.EXECUTE:
            raise AuthorizationError("only EXECUTE decisions receive an authorization")
        if self.issuer.key_id not in self._trusted_issuer_keys:
            raise AuthorizationError("the active issuer key is revoked")
        if not target_in_scope(proposal.action_type, proposal.target, self.action_scope):
            raise AuthorizationError(
                f"action scope is not registered: {proposal.action_type}:{proposal.target}"
            )
        issued_at = time.time()
        token = ExecutionAuthorization(
            authorization_id=str(uuid.uuid4()),
            proposal_id=proposal.proposal_id,
            agent_id=proposal.agent_id,
            action_type=proposal.action_type,
            target=proposal.target,
            scope_digest=scope_digest(proposal.action_type, proposal.target),
            issued_at=issued_at,
            expires_at=issued_at + self.ttl_seconds,
            nonce=uuid.uuid4().hex,
            issuer_key_id=self.issuer.key_id,
            signature="",
        )
        signature = self.issuer.sign(canonical_json(_authorization_payload(token)))
        token = ExecutionAuthorization(**{**_authorization_payload(token), "signature": signature})
        try:
            self._conn.execute("BEGIN IMMEDIATE")
            self._conn.execute(
                "INSERT INTO execution_authorizations "
                "(authorization_id, proposal_id, nonce, token_json, status, issued_at, expires_at) "
                "VALUES (?, ?, ?, ?, ?, ?, ?)",
                (
                    token.authorization_id,
                    token.proposal_id,
                    token.nonce,
                    serialize_authorization(token),
                    token.status.value,
                    token.issued_at,
                    token.expires_at,
                ),
            )
            self._conn.execute(
                "INSERT INTO action_proposals "
                "(proposal_id, agent_id, action_type, target, proposal_json, recorded_at) "
                "VALUES (?, ?, ?, ?, ?, ?)",
                (
                    proposal.proposal_id,
                    proposal.agent_id,
                    proposal.action_type,
                    proposal.target,
                    json.dumps(
                        _json_value(proposal), sort_keys=True, separators=(",", ":")
                    ),
                    time.time(),
                ),
            )
            self._conn.commit()
        except sqlite3.IntegrityError as exc:
            self._conn.rollback()
            raise AuthorizationError("proposal already has an authorization") from exc
        except Exception:
            self._conn.rollback()
            raise
        return token

    def register_issuer_key(self, key_id: str, public_key: bytes) -> None:
        """Trust a new issuer public key for explicit key rotation."""

        if not key_id or len(public_key) != 32:
            raise ValueError("Ed25519 key rotation requires a key id and 32-byte key")
        derived_id = hashlib.sha256(public_key).hexdigest()[:32]
        if derived_id != key_id:
            raise ValueError("issuer key id does not match its public key")
        Ed25519PublicKey.from_public_bytes(public_key)
        self._trusted_issuer_keys[key_id] = public_key

    def revoke_issuer_key(self, key_id: str) -> None:
        """Stop accepting newly presented capabilities from a key ID.

        Existing consumed records remain auditable.  Revocation is deliberately
        explicit so deployments can rotate a trusted issuer without placing
        private key material in repository state.
        """

        self._trusted_issuer_keys.pop(key_id, None)

    def trusted_key_ids(self) -> tuple[str, ...]:
        """Return trusted issuer IDs without exposing private key material."""

        return tuple(sorted(self._trusted_issuer_keys))

    def get_authorization(self, authorization_id: str) -> ExecutionAuthorization | None:
        """Read a persisted authorization by ID."""

        row = self._conn.execute(
            "SELECT token_json, status FROM execution_authorizations "
            "WHERE authorization_id = ?",
            (authorization_id,),
        ).fetchone()
        if row is None:
            return None
        token = deserialize_authorization(row[0])
        return ExecutionAuthorization(
            **{
                **_authorization_payload(token),
                "signature": token.signature,
                "status": AuthorizationStatus(row[1]),
            }
        )

    def consume(
        self,
        token: ExecutionAuthorization,
        *,
        agent_id: str,
        action_type: str,
        target: str,
    ) -> ExecutionAuthorization:
        if token.status is not AuthorizationStatus.ISSUED:
            raise AuthorizationError(f"authorization is not issued: {token.status.value}")
        public_key = self._trusted_issuer_keys.get(token.issuer_key_id)
        if public_key is None:
            raise AuthorizationError("authorization issuer key is not trusted")
        if not self.issuer.verify_with_public_key(
            canonical_json(_authorization_payload(token)), token.signature, public_key
        ):
            raise AuthorizationError("authorization signature is invalid")
        if token.expires_at <= time.time():
            with self._conn:
                self._conn.execute(
                    "UPDATE execution_authorizations SET status = ? "
                    "WHERE authorization_id = ? AND status = ?",
                    (
                        AuthorizationStatus.EXPIRED.value,
                        token.authorization_id,
                        AuthorizationStatus.ISSUED.value,
                    ),
                )
            raise AuthorizationError("authorization has expired")
        if (token.agent_id, token.action_type, token.target) != (
            agent_id,
            action_type,
            target,
        ):
            raise AuthorizationError("authorization scope does not match executor request")
        if token.scope_digest != scope_digest(action_type, target):
            raise AuthorizationError("authorization scope digest does not match request")
        if not target_in_scope(action_type, target, self.action_scope):
            raise AuthorizationError("authorization target is outside the governed scope")
        self._conn.execute("BEGIN IMMEDIATE")
        try:
            row = self._conn.execute(
                "SELECT status FROM execution_authorizations WHERE authorization_id = ?",
                (token.authorization_id,),
            ).fetchone()
            if row is None or row[0] != AuthorizationStatus.ISSUED.value:
                raise AuthorizationError("authorization is unknown or already consumed")
            updated = self._conn.execute(
                "UPDATE execution_authorizations SET status=?, consumed_at=? "
                "WHERE authorization_id=? AND status=?",
                (
                    AuthorizationStatus.CONSUMED.value,
                    time.time(),
                    token.authorization_id,
                    AuthorizationStatus.ISSUED.value,
                ),
            ).rowcount
            if updated != 1:
                raise AuthorizationError("authorization was consumed concurrently")
            self._conn.commit()
        except Exception:
            self._conn.rollback()
            raise
        return ExecutionAuthorization(
            **{**_authorization_payload(token), "signature": token.signature, "status": AuthorizationStatus.CONSUMED}
        )

    def record_receipt(self, receipt: ExecutionReceipt) -> None:
        with self._conn:
            row = self._conn.execute(
                "SELECT status FROM execution_authorizations WHERE authorization_id=?",
                (receipt.authorization_id,),
            ).fetchone()
            if row is None or row[0] != AuthorizationStatus.CONSUMED.value:
                raise AuthorizationError("receipt requires a consumed authorization")
            proposal_row = self._conn.execute(
                "SELECT proposal_id FROM execution_authorizations WHERE authorization_id = ?",
                (receipt.authorization_id,),
            ).fetchone()
            if proposal_row is None or proposal_row[0] != receipt.proposal_id:
                raise AuthorizationError("receipt proposal does not match authorization")
            try:
                self._conn.execute(
                    "INSERT INTO execution_receipts "
                    "(authorization_id, proposal_id, receipt_json, recorded_at) VALUES (?, ?, ?, ?)",
                    (
                        receipt.authorization_id,
                        receipt.proposal_id,
                        serialize_receipt(receipt),
                        time.time(),
                    ),
                )
            except sqlite3.IntegrityError as exc:
                raise AuthorizationError("an execution receipt already exists") from exc

    def has_receipt(self, authorization_id: str) -> bool:
        return self._conn.execute(
            "SELECT 1 FROM execution_receipts WHERE authorization_id=?", (authorization_id,)
        ).fetchone() is not None

    def get_receipt(self, authorization_id: str) -> ExecutionReceipt | None:
        """Read the sole receipt linked to an authorization, if present."""

        row = self._conn.execute(
            "SELECT receipt_json FROM execution_receipts WHERE authorization_id = ?",
            (authorization_id,),
        ).fetchone()
        return None if row is None else deserialize_receipt(row[0])

    def lifecycle_snapshot(self) -> dict[str, int]:
        """Return separate authorization, receipt, and quarantine counts."""

        rows = self._conn.execute(
            "SELECT status, COUNT(*) FROM execution_authorizations GROUP BY status"
        ).fetchall()
        result = {str(status): int(count) for status, count in rows}
        result["receipts"] = int(
            self._conn.execute("SELECT COUNT(*) FROM execution_receipts").fetchone()[0]
        )
        result["quarantined_reports"] = int(
            self._conn.execute("SELECT COUNT(*) FROM quarantined_reports").fetchone()[0]
        )
        result["proposals"] = int(
            self._conn.execute("SELECT COUNT(*) FROM action_proposals").fetchone()[0]
        )
        result["outcome_reports"] = int(
            self._conn.execute("SELECT COUNT(*) FROM outcome_reports").fetchone()[0]
        )
        return result

    def record_outcome_report(
        self,
        *,
        proposal_id: str,
        authorization_id: str,
        evidence_grade: str,
        report: dict[str, Any],
    ) -> str:
        """Persist one receipt-linked outcome report in the audit ledger."""

        if evidence_grade != "attested_execution":
            raise AuthorizationError("authorization ledger accepts only attested outcomes")
        report_id = str(uuid.uuid4())
        try:
            with self._conn:
                self._conn.execute(
                    "INSERT INTO outcome_reports "
                    "(report_id, proposal_id, authorization_id, evidence_grade, report_json, recorded_at) "
                    "VALUES (?, ?, ?, ?, ?, ?)",
                    (
                        report_id,
                        proposal_id,
                        authorization_id,
                        evidence_grade,
                        json.dumps(report, sort_keys=True, default=str),
                        time.time(),
                    ),
                )
        except sqlite3.IntegrityError as exc:
            raise AuthorizationError(
                "an outcome report already exists for this proposal"
            ) from exc
        return report_id

    def quarantine_report(self, report: dict[str, Any]) -> str:
        report_id = str(uuid.uuid4())
        with self._conn:
            self._conn.execute(
                "INSERT INTO quarantined_reports "
                "(report_id, agent_id, action_type, target, report_json, recorded_at) "
                "VALUES (?, ?, ?, ?, ?, ?)",
                (
                    report_id,
                    str(report.get("agent_id", "")),
                    str(report.get("action_type", "")),
                    str(report.get("target", "")),
                    json.dumps(report, sort_keys=True, default=str),
                    time.time(),
                ),
            )
        return report_id

    def close(self) -> None:
        self._conn.close()


__all__ = [
    "DEFAULT_ACTION_SCOPE",
    "AuthorizationError",
    "AuthorizationLedger",
    "Ed25519Authority",
    "canonical_json",
    "deserialize_authorization",
    "deserialize_receipt",
    "digest",
    "scope_digest",
    "serialize_authorization",
    "serialize_receipt",
    "target_in_scope",
]
