"""
Security Compliance Module

Compliance checking and policy enforcement.
"""

__version__ = "0.1.0"

import json
import threading
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Set


class ComplianceFramework(Enum):
    """Compliance frameworks."""
    SOC2 = "soc2"
    HIPAA = "hipaa"
    GDPR = "gdpr"
    PCI_DSS = "pci_dss"
    ISO27001 = "iso27001"
    CUSTOM = "custom"


class ControlStatus(Enum):
    """Status of a control check."""
    PASSED = "passed"
    FAILED = "failed"
    PARTIAL = "partial"
    NOT_APPLICABLE = "not_applicable"
    UNKNOWN = "unknown"


@dataclass
class Control:
    """A compliance control."""
    id: str
    title: str
    description: str
    framework: ComplianceFramework
    category: str = ""
    requirements: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "title": self.title,
            "framework": self.framework.value,
            "category": self.category,
        }


@dataclass
class ControlResult:
    """Result of a control check."""
    control_id: str
    status: ControlStatus
    message: str = ""
    evidence: list[str] = field(default_factory=list)
    remediation: str = ""
    checked_at: datetime = field(default_factory=datetime.now)

    @property
    def passed(self) -> bool:
        """Check if control passed."""
        return self.status == ControlStatus.PASSED

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "control_id": self.control_id,
            "status": self.status.value,
            "message": self.message,
        }


@dataclass
class ComplianceReport:
    """A compliance assessment report."""
    report_id: str
    framework: ComplianceFramework
    results: list[ControlResult] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def total_controls(self) -> int:
        """Get total controls checked."""
        return len(self.results)

    @property
    def passed_controls(self) -> int:
        """Get passed control count."""
        return sum(1 for r in self.results if r.passed)

    @property
    def failed_controls(self) -> int:
        """Get failed control count."""
        return sum(1 for r in self.results if r.status == ControlStatus.FAILED)

    @property
    def compliance_score(self) -> float:
        """Get compliance score (0-100)."""
        if self.total_controls == 0:
            return 0.0
        return (self.passed_controls / self.total_controls) * 100

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "report_id": self.report_id,
            "framework": self.framework.value,
            "total_controls": self.total_controls,
            "passed": self.passed_controls,
            "failed": self.failed_controls,
            "score": self.compliance_score,
        }


class ControlChecker(ABC):
    """Base class for control checkers."""

    @property
    @abstractmethod
    def control_id(self) -> str:
        """Get control ID."""
        pass

    @abstractmethod
    def check(self, context: dict[str, Any]) -> ControlResult:
        """Check the control."""
        pass


class PolicyChecker(ControlChecker):
    """Checker based on policy rules."""

    def __init__(
        self,
        control_id: str,
        check_fn: Any,  # Callable[[Dict], bool]
        pass_message: str = "Control passed",
        fail_message: str = "Control failed",
        remediation: str = "",
    ):
        """Initialize this instance."""
        self._control_id = control_id
        self._check_fn = check_fn
        self._pass_message = pass_message
        self._fail_message = fail_message
        self._remediation = remediation

    @property
    def control_id(self) -> str:
        """control Id ."""
        return self._control_id

    def check(self, context: dict[str, Any]) -> ControlResult:
        """Check the condition and return the result."""
        try:
            passed = self._check_fn(context)
            return ControlResult(
                control_id=self._control_id,
                status=ControlStatus.PASSED if passed else ControlStatus.FAILED,
                message=self._pass_message if passed else self._fail_message,
                remediation="" if passed else self._remediation,
            )
        except Exception as e:
            return ControlResult(
                control_id=self._control_id,
                status=ControlStatus.UNKNOWN,
                message=f"Check error: {e}",
            )


class ComplianceChecker:
    """
    Compliance checking engine.

    Usage:
        checker = ComplianceChecker(ComplianceFramework.SOC2)

        # Add controls
        checker.add_control(Control(
            id="SOC2-CC1.1",
            title="Access Control Policy",
            description="Organization has access control policy",
            framework=ComplianceFramework.SOC2,
        ))

        # Add checker
        checker.add_checker(PolicyChecker(
            control_id="SOC2-CC1.1",
            check_fn=lambda ctx: ctx.get("has_access_policy"),
        ))

        # Run assessment
        report = checker.assess({"has_access_policy": True})
    """

    def __init__(self, framework: ComplianceFramework):
        """Initialize this instance."""
        self.framework = framework
        self._controls: dict[str, Control] = {}
        self._checkers: dict[str, ControlChecker] = {}
        self._counter = 0
        self._lock = threading.Lock()

    def add_control(self, control: Control) -> "ComplianceChecker":
        """Add a control."""
        self._controls[control.id] = control
        return self

    def add_checker(self, checker: ControlChecker) -> "ComplianceChecker":
        """Add a control checker."""
        self._checkers[checker.control_id] = checker
        return self

    def get_control(self, control_id: str) -> Control | None:
        """Get control by ID."""
        return self._controls.get(control_id)

    def list_controls(self) -> list[Control]:
        """List all controls."""
        return list(self._controls.values())

    def _get_report_id(self) -> str:
        """Generate report ID."""
        with self._lock:
            self._counter += 1
            return f"report_{self._counter}"

    def assess(self, context: dict[str, Any]) -> ComplianceReport:
        """
        Run compliance assessment.

        Args:
            context: Context data for checkers

        Returns:
            ComplianceReport with results
        """
        report = ComplianceReport(
            report_id=self._get_report_id(),
            framework=self.framework,
        )

        for control_id, checker in self._checkers.items():
            result = checker.check(context)
            report.results.append(result)

        return report

    def check_control(self, control_id: str, context: dict[str, Any]) -> ControlResult | None:
        """Check a single control."""
        checker = self._checkers.get(control_id)
        if not checker:
            return None
        return checker.check(context)


# Pre-built SOC2 controls
SOC2_CONTROLS = [
    Control(
        id="CC1.1",
        title="Access Control Policy",
        description="The organization has defined access control policies",
        framework=ComplianceFramework.SOC2,
        category="Common Criteria",
    ),
    Control(
        id="CC6.1",
        title="Encryption at Rest",
        description="Sensitive data is encrypted at rest",
        framework=ComplianceFramework.SOC2,
        category="Common Criteria",
    ),
    Control(
        id="CC6.7",
        title="Encryption in Transit",
        description="Data is encrypted during transmission",
        framework=ComplianceFramework.SOC2,
        category="Common Criteria",
    ),
]


__all__ = [
    # Enums
    "ComplianceFramework",
    "ControlStatus",
    # Data classes
    "Control",
    "ControlResult",
    "ComplianceReport",
    # Checkers
    "ControlChecker",
    "PolicyChecker",
    # Core
    "ComplianceChecker",
    # Pre-built
    "SOC2_CONTROLS",
]
