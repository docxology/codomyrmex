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

_DUMMY_PATH = Path("/tmp")


def _check_evolution_config() -> dict[str, Any]:
    """Validate EvolutionConfig instantiation and defaults."""
    try:
        from evolution.core.config import EvolutionConfig

        config = EvolutionConfig(
            iterations=5,
            population_size=3,
            max_skill_size=10_000,
            run_pytest=False,
            hermes_agent_path=_DUMMY_PATH,
        )
        return {
            "status": "ok",
            "iterations": config.iterations,
            "population_size": config.population_size,
            "max_skill_size": config.max_skill_size,
            "optimizer_model": config.optimizer_model,
        }
    except Exception as exc:
        return {"status": "error", "error": str(exc)}


def _check_constraints() -> dict[str, Any]:
    """Validate ConstraintValidator size, growth, and structure checks."""
    try:
        from evolution.core.config import EvolutionConfig
        from evolution.core.constraints import ConstraintValidator

        cfg = EvolutionConfig(
            max_skill_size=100,
            max_prompt_growth=0.2,
            hermes_agent_path=_DUMMY_PATH,
        )
        validator = ConstraintValidator(cfg)

        size_pass = all(r.passed for r in validator.validate_all("short", "skill"))
        size_fail = any(
            not r.passed for r in validator.validate_all("x" * 200, "skill")
        )

        growth_results = validator.validate_all(
            "short" + " extra" * 20, "skill", baseline_text="short"
        )
        growth_blocked = any(
            not r.passed and r.constraint_name == "growth_limit" for r in growth_results
        )

        valid_skill = "---\nname: test\ndescription: demo\n---\n\n# Body\nContent here."
        struct_ok = any(
            r.passed and r.constraint_name == "skill_structure"
            for r in validator.validate_all(valid_skill, "skill")
        )

        return {
            "status": "ok",
            "size_pass": size_pass,
            "size_fail_detected": size_fail,
            "growth_blocked": growth_blocked,
            "structure_valid": struct_ok,
        }
    except Exception as exc:
        return {"status": "error", "error": str(exc)}


def _check_fitness() -> dict[str, Any]:
    """Validate FitnessScore composite calculation and _parse_score."""
    try:
        from evolution.core.fitness import FitnessScore, _parse_score

        score = FitnessScore(
            correctness=0.8,
            procedure_following=0.7,
            conciseness=0.9,
            length_penalty=0.05,
            feedback="Good but slightly verbose.",
        )
        expected = max(0.0, 0.5 * 0.8 + 0.3 * 0.7 + 0.2 * 0.9 - 0.05)
        parse_ok = (
            _parse_score(0.5) == 0.5
            and _parse_score("0.75") == 0.75
            and _parse_score(1.5) == 1.0
            and _parse_score(-0.5) == 0.0
            and _parse_score("invalid") == 0.5
        )
        return {
            "status": "ok",
            "composite": round(score.composite, 4),
            "composite_formula_ok": abs(score.composite - expected) < 1e-6,
            "parse_score_ok": parse_ok,
        }
    except Exception as exc:
        return {"status": "error", "error": str(exc)}


def _check_dataset() -> dict[str, Any]:
    """Validate EvalExample serialization and EvalDataset aggregation."""
    try:
        from evolution.core.dataset_builder import EvalDataset, EvalExample

        ex = EvalExample(
            task_input="Review this PR",
            expected_behavior="Check for security issues",
            difficulty="medium",
            category="security",
            source="synthetic",
        )
        restored = EvalExample.from_dict(ex.to_dict())
        roundtrip_ok = (
            restored.task_input == ex.task_input
            and restored.expected_behavior == ex.expected_behavior
            and restored.difficulty == ex.difficulty
        )
        dataset = EvalDataset(
            train=[ex],
            val=[EvalExample(task_input="t2", expected_behavior="e2")],
            holdout=[EvalExample(task_input="t3", expected_behavior="e3")],
        )
        return {
            "status": "ok",
            "roundtrip_ok": roundtrip_ok,
            "dataset_size": len(dataset.all_examples),
            "dataset_split_ok": len(dataset.all_examples) == 3,
        }
    except Exception as exc:
        return {"status": "error", "error": str(exc)}


def _check_skill_helpers() -> dict[str, Any]:
    """Validate skill reassembly helpers."""
    try:
        from evolution.skills.skill_module import reassemble_skill

        assembled = reassemble_skill(
            "name: test-skill\ndescription: A demo skill",
            "# Instructions\n\n1. Do the thing\n2. Report results",
        )
        return {
            "status": "ok",
            "reassemble_has_frontmatter": assembled.startswith("---"),
            "reassemble_has_body": "Do the thing" in assembled,
            "assembled_length": len(assembled),
        }
    except Exception as exc:
        return {"status": "error", "error": str(exc)}


def run_evolution_bridge() -> dict[str, Any]:
    """Validate evolution submodule integration.

    Returns:
        Dict with ``components`` (per-component results) and overall ``status``.
    """
    components = {
        "config": _check_evolution_config(),
        "constraints": _check_constraints(),
        "fitness": _check_fitness(),
        "dataset": _check_dataset(),
        "skill_helpers": _check_skill_helpers(),
    }
    ok_count = sum(1 for c in components.values() if c.get("status") == "ok")
    total = len(components)
    return {
        "components": components,
        "status": "success" if ok_count == total else "partial",
        "components_ok": f"{ok_count}/{total}",
    }


def main() -> None:
    """CLI entry point."""
    evo_path = Path(__file__).resolve().parent.parent / "evolution"
    if evo_path.exists():
        sys.path.insert(0, str(evo_path))

    result = run_evolution_bridge()
    print(json.dumps(result, indent=2, default=str))
    sys.exit(0 if result["status"] == "success" else 1)


if __name__ == "__main__":
    main()
