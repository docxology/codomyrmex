"""Authorization-bound execution for declared Colony actions.

The adapter deliberately has no implicit execution path: a caller must provide
the serialized capability returned by an ``EXECUTE`` gate decision, and the
action must have been registered by the service owner.  Handlers are ordinary
real-component callables so deployments can bind their own filesystem,
test-runner, or module-maintenance implementations without widening the kernel
contract.
"""

from __future__ import annotations

import hashlib
import time
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from codomyrmex.colony_kernel.authorization import (
    AuthorizationError,
    AuthorizationLedger,
    Ed25519Authority,
    _receipt_payload,
    canonical_json,
    deserialize_authorization,
    digest,
    serialize_receipt,
    target_in_scope,
)
from codomyrmex.colony_kernel.models import ExecutionAuthorization, ExecutionReceipt

ActionHandler = Callable[[str, dict[str, Any]], Any]


@dataclass(frozen=True)
class ExecutionRun:
    """The result and signed receipt for one authorization consumption."""

    result: Any
    receipt: ExecutionReceipt


class RegisteredActionExecutor:
    """Execute only action types registered in the governed scope map."""

    def __init__(
        self,
        ledger: AuthorizationLedger,
        *,
        signer: Ed25519Authority,
        executor_id: str,
        action_scope: dict[str, tuple[str, ...]] | None = None,
    ) -> None:
        if not executor_id.strip():
            raise ValueError("executor_id must be non-empty")
        self.ledger = ledger
        self.signer = signer
        self.executor_id = executor_id
        self.action_scope = action_scope or ledger.action_scope
        self._trusted_executor_keys: dict[str, bytes] = {
            signer.key_id: signer.public_key
        }
        self._handlers: dict[str, ActionHandler] = {}

    def register_executor_key(self, key_id: str, public_key: bytes) -> None:
        """Pin a worker public key for receipt verification and rotation."""

        if not key_id or len(public_key) != 32:
            raise ValueError("Ed25519 executor rotation requires a key id and 32-byte key")
        if hashlib.sha256(public_key).hexdigest()[:32] != key_id:
            raise ValueError("executor key id does not match its public key")
        self._trusted_executor_keys[key_id] = public_key

    def revoke_executor_key(self, key_id: str) -> None:
        """Remove a worker public key from the trusted receipt set."""

        self._trusted_executor_keys.pop(key_id, None)

    def register(self, action_type: str, handler: ActionHandler) -> None:
        """Register a real handler for a declared action type."""

        if action_type not in self.action_scope or not self.action_scope[action_type]:
            raise ValueError(
                f"action type is not registered in the scope map: {action_type}"
            )
        if not callable(handler):
            raise TypeError("action handler must be callable")
        self._handlers[action_type] = handler

    def registered_actions(self) -> tuple[str, ...]:
        """Return the action handlers currently bound to this executor."""

        return tuple(sorted(self._handlers))

    def execute(
        self,
        authorization: ExecutionAuthorization | str | dict[str, Any],
        *,
        agent_id: str,
        action_type: str,
        target: str,
        payload: dict[str, Any] | None = None,
    ) -> ExecutionRun:
        """Consume a capability, run its registered handler, and sign a receipt."""

        token = (
            deserialize_authorization(authorization)
            if isinstance(authorization, (str, dict))
            else authorization
        )
        if action_type not in self._handlers:
            raise AuthorizationError(f"no executor handler is registered: {action_type}")
        if not target_in_scope(action_type, target, self.action_scope):
            raise AuthorizationError(f"target is outside the declared action scope: {target}")
        consumed = self.ledger.consume(
            token,
            agent_id=agent_id,
            action_type=action_type,
            target=target,
        )
        arguments = dict(payload or {})
        started_at = time.time()
        action_digest = digest(
            {
                "proposal_id": consumed.proposal_id,
                "action_type": action_type,
                "target": target,
                "payload": arguments,
            }
        )
        exit_code = 0
        status = "completed"
        try:
            result = self._handlers[action_type](target, arguments)
        except Exception as exc:  # the failure itself is captured by the receipt
            result = {"error": str(exc), "error_type": type(exc).__name__}
            exit_code = 1
            status = "failed"
        completed_at = time.time()
        receipt_unsigned = ExecutionReceipt(
            authorization_id=consumed.authorization_id,
            proposal_id=consumed.proposal_id,
            executor_id=self.executor_id,
            action_digest=action_digest,
            result_digest=digest(result),
            started_at=started_at,
            completed_at=completed_at,
            exit_code=exit_code,
            status=status,
            executor_key_id=self.signer.key_id,
            signature="",
        )
        receipt = ExecutionReceipt(
            **{
                **_receipt_payload(receipt_unsigned),
                "signature": self.signer.sign(canonical_json(_receipt_payload(receipt_unsigned))),
            }
        )
        self.ledger.record_receipt(receipt)
        return ExecutionRun(result=result, receipt=receipt)

    def serialize_receipt(self, run: ExecutionRun) -> str:
        """Serialize a run's receipt for an attested outcome call."""

        return serialize_receipt(run.receipt)

    def verify_receipt(self, receipt: ExecutionReceipt) -> bool:
        """Verify a receipt signed by this executor identity."""

        public_key = self._trusted_executor_keys.get(receipt.executor_key_id)
        return public_key is not None and self.signer.verify_with_public_key(
            canonical_json(_receipt_payload(receipt)), receipt.signature, public_key
        )


__all__ = ["ActionHandler", "ExecutionRun", "RegisteredActionExecutor"]
