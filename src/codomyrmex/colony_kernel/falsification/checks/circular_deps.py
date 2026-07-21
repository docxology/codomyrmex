"""Attack-vector check: check circular deps."""

from __future__ import annotations

import os
import re
from typing import Any

from codomyrmex.colony_kernel.falsification.import_graph import (
    _build_import_graph,
    _find_cycle,
    _module_path_to_dir,
)
from codomyrmex.colony_kernel.falsification.models import AttackVector
from codomyrmex.colony_kernel.models import FalsificationFinding, FalsificationSeverity


def check_circular_deps(
    plan: dict[str, Any],
    repo_root: str | None,
) -> FalsificationFinding | None:
    """Attack: proposed changes introduce a circular import dependency.

    When *repo_root* is supplied, walks Python source files under the
    target module path and builds a lightweight import graph using the
    stdlib ``ast`` module.  Detects cycles via DFS.

    When *repo_root* is ``None`` or the target path cannot be resolved,
    the check inspects the ``dependencies`` key in the plan for self-
    referential or obviously circular entries.
    """
    target = str(plan.get("target", "")).strip()
    dependencies: list[str] = []
    raw_deps = plan.get("dependencies", [])
    if isinstance(raw_deps, (list, tuple)):
        dependencies = [str(d) for d in raw_deps]
    elif isinstance(raw_deps, str) and raw_deps:
        dependencies = [
            s.strip() for s in re.split(r"[,\n;]", raw_deps) if s.strip()
        ]

    # Self-modification check — agent targeting itself is always circular
    agent_id = str(plan.get("agent_id", "")).strip()
    if agent_id and target and agent_id == target:
        return FalsificationFinding(
            claim="The agent is not modifying itself (no self-referential proposal).",
            attack_vector=AttackVector.CIRCULAR_ARCHITECTURE.value,
            severity=FalsificationSeverity.HIGH,
            evidence={"agent_id": agent_id, "target": target},
            remediation=(
                f"Agent `{agent_id}` is targeting itself as `{target}`. "
                "Self-modification proposals are inherently circular. "
                "Use a separate agent or a sandboxed test environment."
            ),
        )

    # Static dependency list check — catch obvious self-references
    if target and target in dependencies:
        return FalsificationFinding(
            claim="The plan does not introduce a self-referential dependency.",
            attack_vector=AttackVector.CIRCULAR_ARCHITECTURE.value,
            severity=FalsificationSeverity.HIGH,
            evidence={"target": target, "dependencies": dependencies},
            remediation=(
                f"`{target}` lists itself as a dependency.  Remove the self-reference "
                "and ensure the module interface does not require importing itself."
            ),
        )

    # Mutual pair check in dependencies list
    for i, dep_a in enumerate(dependencies):
        for dep_b in dependencies[i + 1 :]:
            if dep_a.startswith(dep_b + ".") or dep_b.startswith(dep_a + "."):
                return FalsificationFinding(
                    claim="No parent–child circular dependency exists in the dependency list.",
                    attack_vector=AttackVector.CIRCULAR_ARCHITECTURE.value,
                    severity=FalsificationSeverity.MEDIUM,
                    evidence={"dep_a": dep_a, "dep_b": dep_b},
                    remediation=(
                        f"`{dep_a}` and `{dep_b}` appear to be in a parent–child relationship. "
                        "Verify that neither imports from the other."
                    ),
                )

    if not repo_root:
        return None  # Cannot do filesystem analysis without a root.

    # Filesystem AST-based cycle detection
    module_dir = _module_path_to_dir(target, repo_root)
    if module_dir is None or not os.path.isdir(module_dir):
        return None  # Target not found on disk — skip filesystem check.

    try:
        import_graph = _build_import_graph(module_dir)
        cycle = _find_cycle(import_graph)
    except (OSError, SyntaxError, RecursionError):
        return None  # Parse failure is not itself a circular dep finding.

    if cycle:
        return FalsificationFinding(
            claim="The module graph under the target path is acyclic.",
            attack_vector=AttackVector.CIRCULAR_ARCHITECTURE.value,
            severity=FalsificationSeverity.HIGH,
            evidence={"cycle": cycle},
            remediation=(
                f"Circular import detected: {' -> '.join(cycle)}.  "
                "Extract shared types to a lower-level module that neither side imports."
            ),
        )

    return None
