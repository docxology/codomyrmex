"""Evolution submodule integration bridge.

Exercises ``EvolutionConfig``, ``ConstraintValidator``, ``FitnessScore``,
and skill module data models from the ``evolution/`` git submodule —
without requiring DSPy API keys or LLM calls.

Usage::

    python -m codomyrmex.agents.hermes.scripts.run_evolution_bridge
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any


def run_evolution_bridge() -> dict[str, Any]:
    """Validate evolution submodule integration.

    Exercises core data structures: ``EvolutionConfig``,
    ``ConstraintValidator``, ``ConstraintResult``, ``FitnessScore``,
    ``EvalExample``, ``EvalDataset``, and ``SkillModule`` helpers.

    Returns:
        Dict with test results for each component.
    """
    results: dict[str, Any] = {"components": {}}

    # ── 1. EvolutionConfig ───────────────────────────────────────────
    try:
        from evolution.core.config import EvolutionConfig

        config = EvolutionConfig(
            iterations=5,
            population_size=3,
            max_skill_size=10_000,
            run_pytest=False,
        )
        results["components"]["config"] = {
            "status": "ok",
            "iterations": config.iterations,
            "population_size": config.population_size,
            "max_skill_size": config.max_skill_size,
            "optimizer_model": config.optimizer_model,
        }
    except Exception as exc:
        results["components"]["config"] = {"status": "error", "error": str(exc)}

    # ── 2. ConstraintValidator ───────────────────────────────────────
    try:
        from evolution.core.constraints import ConstraintResult, ConstraintValidator

        config_for_cv = EvolutionConfig(
            max_skill_size=100,
            max_prompt_growth=0.2,
        )
        validator = ConstraintValidator(config_for_cv)

        # Test size check — passing
        small_text = "A short skill description."
        results_pass = validator.validate_all(small_text, "skill")
        all_passed = all(r.passed for r in results_pass)

        # Test size check — failing
        huge_text = "x" * 200
        results_fail = validator.validate_all(huge_text, "skill")
        has_failure = any(not r.passed for r in results_fail)

        # Test growth check
        baseline = "short"
        grown = "short" + " extra" * 20
        growth_results = validator.validate_all(grown, "skill", baseline_text=baseline)
        growth_blocked = any(
            not r.passed and r.constraint_name == "growth_limit" for r in growth_results
        )

        # Test skill structure check
        valid_skill = "---\nname: test\ndescription: demo\n---\n\n# Body\nContent here."
        struct_results = validator.validate_all(valid_skill, "skill")
        struct_ok = any(
            r.passed and r.constraint_name == "skill_structure" for r in struct_results
        )

        results["components"]["constraints"] = {
            "status": "ok",
            "size_pass": all_passed,
            "size_fail_detected": has_failure,
            "growth_blocked": growth_blocked,
            "structure_valid": struct_ok,
            "total_checks": len(results_pass),
        }
    except Exception as exc:
        results["components"]["constraints"] = {"status": "error", "error": str(exc)}

    # ── 3. FitnessScore ──────────────────────────────────────────────
    try:
        from evolution.core.fitness import FitnessScore, _parse_score

        score = FitnessScore(
            correctness=0.8,
            procedure_following=0.7,
            conciseness=0.9,
            length_penalty=0.05,
            feedback="Good but slightly verbose.",
        )
        composite = score.composite

        # Verify composite calculation
        expected = max(0.0, 0.5 * 0.8 + 0.3 * 0.7 + 0.2 * 0.9 - 0.05)
        composite_ok = abs(composite - expected) < 1e-6

        # Test _parse_score with various inputs
        parse_ok = (
            _parse_score(0.5) == 0.5
            and _parse_score("0.75") == 0.75
            and _parse_score(1.5) == 1.0  # Clamped
            and _parse_score(-0.5) == 0.0  # Clamped
            and _parse_score("invalid") == 0.5  # Default
        )

        results["components"]["fitness"] = {
            "status": "ok",
            "composite": round(composite, 4),
            "composite_formula_ok": composite_ok,
            "parse_score_ok": parse_ok,
        }
    except Exception as exc:
        results["components"]["fitness"] = {"status": "error", "error": str(exc)}

    # ── 4. EvalExample + EvalDataset ─────────────────────────────────
    try:
        from evolution.core.dataset_builder import EvalDataset, EvalExample

        ex = EvalExample(
            task_input="Review this PR",
            expected_behavior="Check for security issues",
            difficulty="medium",
            category="security",
            source="synthetic",
        )
        # Round-trip serialization
        as_dict = ex.to_dict()
        restored = EvalExample.from_dict(as_dict)
        roundtrip_ok = (
            restored.task_input == ex.task_input
            and restored.expected_behavior == ex.expected_behavior
            and restored.difficulty == ex.difficulty
        )

        # Dataset creation and split
        dataset = EvalDataset(
            train=[ex],
            val=[EvalExample(task_input="t2", expected_behavior="e2")],
            holdout=[EvalExample(task_input="t3", expected_behavior="e3")],
        )
        all_examples = dataset.all_examples
        dataset_ok = len(all_examples) == 3

        results["components"]["dataset"] = {
            "status": "ok",
            "roundtrip_ok": roundtrip_ok,
            "dataset_size": len(all_examples),
            "dataset_split_ok": dataset_ok,
        }
    except Exception as exc:
        results["components"]["dataset"] = {"status": "error", "error": str(exc)}

    # ── 5. Skill helpers ─────────────────────────────────────────────
    try:
        from evolution.skills.skill_module import load_skill, reassemble_skill

        # Test reassemble
        frontmatter = "name: test-skill\ndescription: A demo skill"
        body = "# Instructions\n\n1. Do the thing\n2. Report results"
        assembled = reassemble_skill(frontmatter, body)
        has_frontmatter = assembled.startswith("---")
        has_body = "Do the thing" in assembled

        results["components"]["skill_helpers"] = {
            "status": "ok",
            "reassemble_has_frontmatter": has_frontmatter,
            "reassemble_has_body": has_body,
            "assembled_length": len(assembled),
        }
    except Exception as exc:
        results["components"]["skill_helpers"] = {"status": "error", "error": str(exc)}

    # ── Summary ──────────────────────────────────────────────────────
    ok_count = sum(1 for c in results["components"].values() if c.get("status") == "ok")
    total = len(results["components"])
    results["status"] = "success" if ok_count == total else "partial"
    results["components_ok"] = f"{ok_count}/{total}"

    return results


def main() -> None:
    """CLI entry point."""
    # Add evolution submodule to sys.path for imports
    evo_path = Path(__file__).resolve().parent.parent / "evolution"
    if evo_path.exists():
        sys.path.insert(0, str(evo_path))

    result = run_evolution_bridge()
    print(json.dumps(result, indent=2, default=str))
    sys.exit(0 if result["status"] == "success" else 1)


if __name__ == "__main__":
    main()
