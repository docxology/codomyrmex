"""Cloud Security Pipeline for Infomaniak operations.

Composable pre/post security checks that integrate with cognitive security
modules (defense, identity, privacy) when available.
"""

import logging
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any

logger = logging.getLogger(__name__)

# Lazy imports — all cross-module dependencies are optional
try:
    from codomyrmex.security.ai_safety import ActiveDefense
except ImportError:
    ActiveDefense = None

try:
    from codomyrmex.identity import IdentityManager, VerificationLevel
except ImportError:
    IdentityManager = None
    VerificationLevel = None

try:
    from codomyrmex.privacy import CrumbCleaner
except ImportError:
    CrumbCleaner = None


class OperationRisk(Enum):
    """Risk level for cloud operations."""
    READ = auto()
    WRITE = auto()
    DELETE = auto()
    ADMIN = auto()


@dataclass
class SecurityCheckResult:
    """Result of a security pipeline check."""
    allowed: bool = True
    reason: str = ""
    risk_level: OperationRisk = OperationRisk.READ
    checks_passed: list[str] = field(default_factory=list)
    checks_failed: list[str] = field(default_factory=list)


# Prefix-based risk classification
_RISK_PREFIXES = {
    "list_": OperationRisk.READ,
    "get_": OperationRisk.READ,
    "describe_": OperationRisk.READ,
    "create_": OperationRisk.WRITE,
    "update_": OperationRisk.WRITE,
    "add_": OperationRisk.WRITE,
    "set_": OperationRisk.WRITE,
    "upload_": OperationRisk.WRITE,
    "allocate_": OperationRisk.WRITE,
    "associate_": OperationRisk.WRITE,
    "attach_": OperationRisk.WRITE,
    "delete_": OperationRisk.DELETE,
    "remove_": OperationRisk.DELETE,
    "release_": OperationRisk.DELETE,
    "detach_": OperationRisk.DELETE,
    "disassociate_": OperationRisk.DELETE,
    "terminate_": OperationRisk.ADMIN,
    "destroy_": OperationRisk.ADMIN,
    "force_": OperationRisk.ADMIN,
    "reboot_": OperationRisk.ADMIN,
}


def classify_operation_risk(operation_name: str) -> OperationRisk:
    """Map an operation name to its risk level based on prefix."""
    name = operation_name.lower()
    for prefix, risk in _RISK_PREFIXES.items():
        if name.startswith(prefix):
            return risk
    return OperationRisk.READ


# Minimum verification levels for risky operations
_MIN_VERIFICATION = {
    OperationRisk.READ: None,
    OperationRisk.WRITE: "ANON",
    OperationRisk.DELETE: "VERIFIED_ANON",
    OperationRisk.ADMIN: "KYC",
}

# Ordered verification levels for comparison
_VERIFICATION_ORDER = ["UNVERIFIED", "ANON", "VERIFIED_ANON", "KYC"]


class CloudSecurityPipeline:
    """Composable security pipeline for cloud operations.

    Each check is optional — if a module isn't installed, that check
    is silently skipped.
    """

    def __init__(
        self,
        active_defense: Any | None = None,
        identity_manager: Any | None = None,
        crumb_cleaner: Any | None = None,
    ):
        """Initialize this instance."""
        self._defense = active_defense
        if self._defense is None and ActiveDefense is not None:
            self._defense = ActiveDefense()

        self._identity = identity_manager
        if self._identity is None and IdentityManager is not None:
            self._identity = IdentityManager()

        self._cleaner = crumb_cleaner
        if self._cleaner is None and CrumbCleaner is not None:
            self._cleaner = CrumbCleaner()

    def pre_check(
        self,
        operation_name: str,
        parameters: dict[str, Any],
        user_id: str | None = None,
    ) -> SecurityCheckResult:
        """Run pre-execution security checks.

        Checks:
        1. Exploit detection on string parameters (ActiveDefense)
        2. Identity verification level for write/delete/admin ops (IdentityManager)
        """
        risk = classify_operation_risk(operation_name)
        result = SecurityCheckResult(risk_level=risk)

        # Check 1: Exploit detection on string params
        if self._defense is not None:
            for key, value in parameters.items():
                if isinstance(value, str) and self._defense.detect_exploit(value):
                    result.allowed = False
                    result.reason = f"Exploit detected in parameter '{key}'"
                    result.checks_failed.append("exploit_detection")
                    logger.warning(
                        f"Security: blocked {operation_name} — exploit in '{key}'"
                    )
                    return result
            result.checks_passed.append("exploit_detection")

        # Check 2: Identity verification for risky operations
        if self._identity is not None and VerificationLevel is not None:
            min_level_name = _MIN_VERIFICATION.get(risk)
            if min_level_name is not None:
                persona = self._identity.active_persona
                if persona is None:
                    result.allowed = False
                    result.reason = (
                        f"Operation '{operation_name}' requires "
                        f"{min_level_name} verification but no active persona"
                    )
                    result.checks_failed.append("identity_verification")
                    return result

                persona_level_name = persona.level.name
                if (
                    _VERIFICATION_ORDER.index(persona_level_name)
                    < _VERIFICATION_ORDER.index(min_level_name)
                ):
                    result.allowed = False
                    result.reason = (
                        f"Operation '{operation_name}' requires "
                        f"{min_level_name} but persona has {persona_level_name}"
                    )
                    result.checks_failed.append("identity_verification")
                    return result

                result.checks_passed.append("identity_verification")

        return result

    def post_process(
        self,
        operation_name: str,
        result: Any,
    ) -> Any:
        """Post-process operation results to scrub metadata.

        Uses CrumbCleaner if available to remove tracking data.
        """
        if self._cleaner is not None and isinstance(result, (dict, list)):
            return self._cleaner.scrub(result)
        return result
