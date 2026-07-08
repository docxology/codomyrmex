"""Attack-vector check: check no test value."""

from __future__ import annotations

import re
from typing import Any

from codomyrmex.colony_kernel.falsification.models import AttackVector
from codomyrmex.colony_kernel.models import FalsificationFinding, FalsificationSeverity


def check_no_test_value(plan: dict[str, Any]) -> FalsificationFinding | None:
    """Attack: plan adds no verifiable test coverage.

    Returns a HIGH finding when ``tests`` is absent, empty, or describes
    only manual verification steps.
    """
    tests = plan.get("tests")

    if tests is None:
        return FalsificationFinding(
            claim="The plan includes automated test coverage.",
            attack_vector=AttackVector.NO_TEST_VALUE.value,
            severity=FalsificationSeverity.HIGH,
            evidence={"tests": "<key absent>"},
            remediation=(
                "Add a `tests` key listing the test file paths or test IDs that will "
                "exercise the changed behaviour.  Automated tests are non-negotiable."
            ),
        )

    if isinstance(tests, (list, tuple)):
        if not tests:
            return FalsificationFinding(
                claim="The plan includes automated test coverage.",
                attack_vector=AttackVector.NO_TEST_VALUE.value,
                severity=FalsificationSeverity.HIGH,
                evidence={"tests": []},
                remediation=(
                    "Provide at least one test path in the `tests` list that asserts "
                    "the expected post-change behaviour."
                ),
            )
        tests_str = " ".join(str(t) for t in tests)
    else:
        tests_str = str(tests).strip()

    manual_patterns = [
        r"\bmanual(ly)?\b",
        r"\bsmoke\s+test\b",
        r"\bverify\s+by\s+hand\b",
        r"\bcheck\s+visually\b",
    ]
    if any(re.search(p, tests_str, re.IGNORECASE) for p in manual_patterns):
        return FalsificationFinding(
            claim="Tests rely on automated execution, not manual inspection.",
            attack_vector=AttackVector.NO_TEST_VALUE.value,
            severity=FalsificationSeverity.MEDIUM,
            evidence={"tests": tests_str[:200]},
            remediation=(
                "Replace manual verification steps with automated assertions.  "
                "Manual checks do not scale and are not captured in CI."
            ),
        )

    return None
