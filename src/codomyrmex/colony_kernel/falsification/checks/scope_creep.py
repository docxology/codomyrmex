"""Attack-vector check: check scope creep."""

from __future__ import annotations

import re
from typing import Any

from codomyrmex.colony_kernel.falsification.models import AttackVector
from codomyrmex.colony_kernel.models import FalsificationFinding, FalsificationSeverity


def check_scope_creep(plan: dict[str, Any]) -> FalsificationFinding | None:
    """Attack: plan's scope is broader than its stated target.

    Detects when:
    - the ``action_type`` is a destructive operation (delete, drop, remove, truncate)
      without explicit blast-radius documentation in ``scope``;
    - the ``scope`` description references modules or systems unrelated to ``target``;
    - the scope language is deliberately vague.
    """
    scope = plan.get("scope", "")
    target = plan.get("target", "")
    action_type = str(plan.get("action_type", "")).strip().lower()

    _DESTRUCTIVE_ACTIONS = {"delete", "drop", "remove", "truncate", "purge", "wipe"}
    if action_type in _DESTRUCTIVE_ACTIONS:
        return FalsificationFinding(
            claim="The plan documents the blast radius of its destructive action.",
            attack_vector=AttackVector.SCOPE_CREEP.value,
            severity=FalsificationSeverity.HIGH,
            evidence={
                "action_type": action_type,
                "target": str(target),
                "scope_documented": bool(scope),
            },
            remediation=(
                f"Destructive action '{action_type}' requires a `scope` field "
                "enumerating all affected files, callers, and dependent modules. "
                "Add an explicit blast-radius analysis before submitting."
            ),
        )

    if not scope:
        return None  # Absent scope is handled elsewhere; not a creep signal.

    scope_str = str(scope).strip()
    target_str = str(target).strip()

    # Vagueness indicators
    vague_patterns = [
        r"\bvarious\b",
        r"\bmultiple\s+(systems?|modules?|services?|components?)\b",
        r"\brelated\s+(things?|work|changes?)\b",
        r"\bas\s+needed\b",
        r"\bwherever\s+applicable\b",
        r"\bgeneral\s+(improvements?|refactor(ing)?)\b",
    ]
    vague_hits = [p for p in vague_patterns if re.search(p, scope_str, re.IGNORECASE)]
    if len(vague_hits) >= 2:
        return FalsificationFinding(
            claim="The plan scope is precisely bounded to its stated target.",
            attack_vector=AttackVector.SCOPE_CREEP.value,
            severity=FalsificationSeverity.MEDIUM,
            evidence={
                "scope": scope_str[:300],
                "vague_patterns_matched": vague_hits,
            },
            remediation=(
                "Rewrite the scope to name the specific files, functions, or modules "
                "in scope.  Vague scope language hides unbounded work."
            ),
        )

    # Cross-module boundary detection: scope mentions modules not in target
    if target_str:
        # Extract dotted module names from scope
        module_refs = re.findall(
            r"\b([a-z_][a-z0-9_]*(?:\.[a-z_][a-z0-9_]*)+)\b", scope_str
        )
        target_root = target_str.split(".")[0] if "." in target_str else target_str
        foreign_refs = [m for m in module_refs if not m.startswith(target_root)]
        if len(foreign_refs) >= 3:
            return FalsificationFinding(
                claim="The plan scope does not reach into unrelated modules.",
                attack_vector=AttackVector.SCOPE_CREEP.value,
                severity=FalsificationSeverity.HIGH,
                evidence={
                    "target_root": target_root,
                    "foreign_module_refs": foreign_refs[:10],
                },
                remediation=(
                    f"Scope references {len(foreign_refs)} modules outside `{target_root}`.  "
                    "Split into separate proposals or explicitly justify each cross-module touch."
                ),
            )

    return None
