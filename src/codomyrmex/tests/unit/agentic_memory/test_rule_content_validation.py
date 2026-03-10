"""Validation tests for cursorrules content — strictly zero-mock."""

from pathlib import Path

import pytest

from codomyrmex.agentic_memory.rules.registry import RuleRegistry


@pytest.mark.unit
def test_all_cursorrules_have_sections_0_to_7() -> None:
    """Verify that all .cursorrules files have sections 0-7."""
    rules_root = Path(__file__).parents[3] / "agentic_memory" / "rules"
    registry = RuleRegistry(rules_root=rules_root)
    # The registry doesn't have a discover() method according to registry.py
    rules = registry.list_all_rules()

    assert len(rules) > 0, "Expected to find some .cursorrules files"

    violations = []

    for rule in rules:
        expected_sections = set(range(8))  # 0 to 7
        actual_sections = {section.number for section in rule.sections}

        missing = expected_sections - actual_sections
        if missing:
            violations.append(
                f"{rule.file_path.name} is missing sections: {sorted(missing)}"
            )

    if violations:
        pytest.fail(
            "The following .cursorrules files are missing required sections:\n"
            + "\n".join(violations)
        )
