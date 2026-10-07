"""The digital ComplianceChecker must not report placeholder compliance."""

from __future__ import annotations

import pytest

from codomyrmex.security.digital.compliance_checker import (
    ComplianceChecker,
    ComplianceResult,
    ComplianceStandard,
    check_compliance_standards,
)


@pytest.mark.unit
def test_check_compliance_is_explicitly_unimplemented() -> None:
    with pytest.raises(NotImplementedError, match=r"security\.compliance"):
        ComplianceChecker().check_compliance({}, [ComplianceStandard.OWASP_TOP_10])


@pytest.mark.unit
def test_convenience_function_does_not_fabricate_results() -> None:
    with pytest.raises(NotImplementedError):
        check_compliance_standards({"debug": True}, ["OWASP_TOP_10"])


@pytest.mark.unit
def test_compliance_score_from_real_results() -> None:
    from datetime import datetime

    now = datetime.now()
    results = [
        ComplianceResult("A", "compliant", "checked", now),
        ComplianceResult("B", "non_compliant", "checked", now),
    ]
    checker = ComplianceChecker()
    assert checker.get_compliance_score(results) == 50.0
    assert checker.get_compliance_score([]) == 0.0
