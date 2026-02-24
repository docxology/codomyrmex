"""Aggregate security posture dashboard.

Combines permission matrix, compliance summary, CVE status,
and secret scan findings into a unified security view.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from codomyrmex.security.compliance_report import ComplianceReport
from codomyrmex.security.permissions import PermissionModel
from codomyrmex.security.secret_scanner import SecretFinding


@dataclass
class SecurityPosture:
    """Aggregate security posture.

    Attributes:
        permission_matrix: Principal → permission map.
        compliance_pass_rate: Compliance pass percentage.
        secret_findings_count: Number of exposed secrets.
        total_checks: Total compliance checks.
        risk_score: Overall risk score (0-100, lower = better).
    """

    permission_matrix: dict[str, dict[str, bool]] = field(default_factory=dict)
    compliance_pass_rate: float = 0.0
    secret_findings_count: int = 0
    total_checks: int = 0
    risk_score: float = 0.0


class SecurityDashboard:
    """Aggregate security posture view.

    Example::

        dashboard = SecurityDashboard(
            permissions=perm_model,
            compliance=comp_report,
            secrets=findings,
        )
        posture = dashboard.posture()
    """

    def __init__(
        self,
        permissions: PermissionModel | None = None,
        compliance: ComplianceReport | None = None,
        secrets: list[SecretFinding] | None = None,
    ) -> None:
        """Execute   Init   operations natively."""
        self._permissions = permissions or PermissionModel()
        self._compliance = compliance or ComplianceReport()
        self._secrets = secrets or []

    def posture(self) -> SecurityPosture:
        """Compute aggregate security posture."""
        perm_matrix = self._permissions.permission_matrix()
        pass_rate = self._compliance.pass_rate
        secrets_count = len(self._secrets)

        # Risk score: 0-100 (lower = better)
        risk = 0.0
        if self._compliance.total_checks > 0 and pass_rate < 1.0:
            risk += (1.0 - pass_rate) * 50  # Up to 50 from compliance
        risk += min(secrets_count * 10, 50)  # Up to 50 from secrets

        return SecurityPosture(
            permission_matrix=perm_matrix,
            compliance_pass_rate=pass_rate,
            secret_findings_count=secrets_count,
            total_checks=self._compliance.total_checks,
            risk_score=min(risk, 100),
        )

    def to_markdown(self) -> str:
        """Render security posture as markdown."""
        p = self.posture()
        lines = [
            "# Security Dashboard",
            "",
            f"**Risk Score**: {p.risk_score:.0f}/100 | "
            f"**Compliance**: {p.compliance_pass_rate:.0%} | "
            f"**Secrets Found**: {p.secret_findings_count}",
            "",
        ]

        if p.permission_matrix:
            lines.extend(["## Permission Matrix", ""])
            headers = list(next(iter(p.permission_matrix.values())).keys())
            lines.append("| Principal | " + " | ".join(headers) + " |")
            lines.append("|" + "---|" * (len(headers) + 1))
            for principal, perms in p.permission_matrix.items():
                vals = [("✅" if v else "❌") for v in perms.values()]
                lines.append(f"| {principal} | " + " | ".join(vals) + " |")

        return "\n".join(lines)


__all__ = ["SecurityDashboard", "SecurityPosture"]
