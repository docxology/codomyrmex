#!/usr/bin/env python3
"""Hermes Agent — Evaluator Orchestrator.

Iterates over modules inside `scripts/`, runs the corresponding scripts,
captures their output, reads their source code, and uses Hermes to provide
a technical assessment on whether they follow the "thin orchestrator" pattern,
along with suggested improvements.

Usage:
    python scripts/agents/hermes/evaluate_orchestrators.py --target agents/hermes
    python scripts/agents/hermes/evaluate_orchestrators.py --target all
"""

import argparse
import json
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

try:
    import yaml as _yaml

    _YAML_AVAILABLE = True
except ImportError:
    _YAML_AVAILABLE = False

try:
    from codomyrmex.agents.core.config import get_config
    from codomyrmex.utils.json_helpers import extract_json_from_response
except ImportError:
    sys.path.insert(
        0, str(Path(__file__).resolve().parent.parent.parent.parent / "src")
    )
    from codomyrmex.agents.core.config import get_config
    from codomyrmex.utils.json_helpers import extract_json_from_response
from codomyrmex.utils.cli_helpers import (
    print_error,
    print_info,
    print_success,
    setup_logging,
)

try:
    from prompt_context import build_project_context
except ImportError:
    # Fallback if running from outside scripts/agents/hermes/
    import sys as _sys

    _sys.path.insert(0, str(Path(__file__).resolve().parent))
    from prompt_context import build_project_context


def _find_repository_root() -> Path:
    """Find the repository root by searching upward for pyproject.toml."""
    current = Path(__file__).resolve()
    for parent in current.parents:
        if (parent / "pyproject.toml").exists():
            return parent
    if (current / ".git").exists():
        return current
    return current.parent.parent.parent.parent


_REPO_ROOT: Path = _find_repository_root()
_SCRIPTS_ROOT: Path = _REPO_ROOT / "scripts"

# Exemplary COMPLIANT scripts used as positive-example context in eval prompts.
# These are well-rated hermes orchestrators that demonstrate the pattern.
_EXEMPLAR_SCRIPTS: list[Path] = [
    _REPO_ROOT / "scripts" / "agents" / "hermes" / "observe_hermes.py",
    _REPO_ROOT / "scripts" / "agents" / "hermes" / "setup_hermes.py",
]


_HERMES_YAML: Path = _REPO_ROOT / "config" / "agents" / "hermes.yaml"


def _load_hermes_yaml() -> dict:
    """Read hermes.yaml directly and return its contents as a dict.

    Uses PyYAML when available. Falls back to empty dict on any error.
    hermes.yaml is a flat namespace (not nested under a 'hermes' key).
    """
    if not _YAML_AVAILABLE or not _HERMES_YAML.exists():
        return {}
    try:
        return _yaml.safe_load(_HERMES_YAML.read_text(encoding="utf-8")) or {}
    except Exception:
        return {}


def _resolve_evaluator_config(target: Optional[str] = None) -> dict:
    """Load hermes.yaml evaluator section, merging any target-specific overrides.

    If *target* is given and a matching key exists in hermes.yaml
    ``target_overrides``, those settings are merged on top of the base
    evaluator config, allowing per-directory customisation of output_dir,
    no_exec_scripts, run_env, etc.

    Args:
        target: Value of --target CLI arg (e.g. 'agents/gemini').

    Returns:
        Merged evaluator config dict.
    """
    hermes_cfg = _load_hermes_yaml()
    base: dict = dict(hermes_cfg.get("evaluator", {}))
    if target:
        overrides: dict = hermes_cfg.get("target_overrides", {}).get(target, {})
        if overrides:
            base = {**base, **overrides}
    return base


def _resolve_assessment_timeout(evaluator_cfg: dict) -> int:
    """Return the Hermes assessment timeout from config with a safe fallback.

    Uses evaluator.assessment_timeout first, then hermes.timeout, then 600s.
    """
    if evaluator_cfg.get("assessment_timeout"):
        return int(evaluator_cfg["assessment_timeout"])
    hermes_cfg = _load_hermes_yaml()
    return int(hermes_cfg.get("timeout", 600))


def run_script(
    script_path: Path, timeout: int = 30, extra_env: Optional[dict] = None
) -> dict:
    """Run a script and return its return code, stdout, and stderr.

    Args:
        script_path: Path to the Python script to execute.
        timeout: Maximum seconds to wait for the script. Configurable via
            evaluator.script_timeout in hermes.yaml (default: 30).
        extra_env: Optional dict of environment variables to inject into the
            subprocess environment. Merged on top of the current os.environ.
            Use to pass CODOMYRMEX_TEST_MODE=1 for API-dependent scripts.
    """
    print_info(f"  Running: {script_path.name}...")
    env = {**os.environ}
    if extra_env:
        env.update(extra_env)
        env_keys = ", ".join(f"{k}={v}" for k, v in extra_env.items())
        print_info(f"  Injecting env: {env_keys}")
    try:
        # Run it with the current python interpreter
        result = subprocess.run(
            [sys.executable, str(script_path)],
            capture_output=True,
            text=True,
            timeout=timeout,
            env=env,
        )
        return {
            "path": script_path,
            "returncode": result.returncode,
            "stdout": result.stdout,
            "stderr": result.stderr,
        }
    except subprocess.TimeoutExpired:
        return {
            "path": script_path,
            "returncode": -1,
            "stdout": "",
            "stderr": f"Execution timed out after {timeout} seconds.",
        }
    except Exception as e:
        return {
            "path": script_path,
            "returncode": -1,
            "stdout": "",
            "stderr": f"Failed to execute: {e}",
        }


def assess_script(
    client, script_info: dict, source_code: str, target_dir: Optional[Path] = None
) -> dict:
    """Use Hermes to assess a script based on stdout, stderr, and source code.

    Args:
        client: Initialized Hermes client.
        script_info: Dict with 'path', 'returncode', 'stdout', 'stderr'.
        source_code: Full source code of the script.
        target_dir: Directory containing the scripts being evaluated.
            Used to load local AGENTS.md for richer project context.
    """
    script_name = script_info["path"].name

    # Build rich project context: standards + AGENTS.md + exemplary scripts
    project_context = build_project_context(
        target_dir=target_dir or script_info["path"].parent,
        repo_root=_REPO_ROOT,
        exemplar_paths=_EXEMPLAR_SCRIPTS,
    )

    prompt = f"""You are a senior principal engineer performing a code review and architectural assessment.

{project_context}

Evaluate the following Python orchestration script based on the Codomyrmex "Thin Orchestrator" pattern.
A thin orchestrator MUST:
1. Accept configuration transparently (from config files or env vars — never hardcoded values).
2. Formulate dependencies cleanly — NO heavy business logic or data transformations in the script itself.
3. Execute the core method by delegating to a library/module function.
4. Log and format the output clearly using cli_helpers (print_info/print_success/print_error).
5. Exit cleanly with sys.exit(0) on success, non-zero on failure.

Common anti-patterns to flag:
- Bare `except:` → must specify exception type(s)
- `Optional[X]` / `Dict` / `List` from typing → use `X | None` / `dict` / `list` (Python 3.11+)
- Hardcoded file paths → use Path(__file__).resolve() or env vars
- Business logic in the script body → extract to library module
- Missing sys.exit() → script must exit with explicit code
- Bare `print()` for status → use cli_helpers instead

Script Name: {script_name}
Exit Code: {script_info["returncode"]}

--- SCRIPT SOURCE CODE ---
{source_code}
--------------------------

--- STDOUT ---
{script_info["stdout"]}
--------------

--- STDERR ---
{script_info["stderr"]}
--------------

IMPORTANT: Your entire response MUST be a single valid JSON object and nothing else.
Do NOT include any prose, explanation, markdown formatting, or code fences around the JSON.
Start your response with {{ and end it with }}. No text before or after.

Use exactly this schema:
{{
    "adherence_assessment": {{
        "adheres": true,
        "reasoning": "Detailed justification of why it adheres or does not adhere."
    }},
    "technical_debt": [
        "Sloppy Code: Issue 1",
        "Hardcoded Paths: Issue 2",
        "Heavy Logic: Issue 3"
    ],
    "underlying_improvements": [
        "Architectural Flaw 1",
        "Test/Method downstream fix 1"
    ]
}}"""

    print_info(f"  Requesting assessment for {script_name} from Hermes...")
    try:
        response = client.chat_session(prompt=prompt)
        if response.is_success():
            eval_data = extract_json_from_response(response.content)

            print_success(f"=== Hermes Assessment for {script_name} ===")
            print_info(
                f"  Adheres to pattern: {eval_data.get('adherence_assessment', {}).get('adheres', False)}"
            )
            print_success("=" * 60)
            return eval_data
        print_error(f"  Hermes failed to assess {script_name}: {response.error}")
        return None
    except Exception as e:
        print_error(f"  Hermes evaluation error: {e}")
        return None


def main() -> int:
    # Pre-parse just --target so we can use it when resolving config
    # (target_overrides in hermes.yaml are target-specific; we need target before argparse defaults run)
    _pre = argparse.ArgumentParser(add_help=False)
    _pre.add_argument("--target", default="agents/hermes")
    _pre_args, _ = _pre.parse_known_args()
    evaluator_cfg = _resolve_evaluator_config(target=_pre_args.target)

    parser = argparse.ArgumentParser(description="Hermes Script Evaluator")
    parser.add_argument(
        "--target",
        type=str,
        default="agents/hermes",
        help="Target subdirectory within scripts/ to find python executable scripts (e.g. 'agents/hermes')",
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default=evaluator_cfg.get("output_dir", "evaluations"),
        help="Directory to save the JSON reports and overall markdown evaluation (repo-root relative).",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        default=False,
        help="Discover and execute scripts but skip Hermes assessment. Useful for fast iteration.",
    )
    parser.add_argument(
        "--run-env",
        nargs="*",
        default=[],
        metavar="KEY=VALUE",
        help=(
            "Environment variable(s) to inject when running target scripts. "
            "Example: --run-env CODOMYRMEX_TEST_MODE=1 GEMINI_API_KEY=dummy. "
            "Useful to prevent API-dependent scripts from blocking during eval."
        ),
    )
    args = parser.parse_args()

    # Seed run_env from target_overrides.run_env in hermes.yaml (CLI flags override)
    run_env_dict: dict[str, str] = {}
    cfg_run_env = evaluator_cfg.get("run_env", {})
    if isinstance(cfg_run_env, dict):
        run_env_dict.update({str(k): str(v) for k, v in cfg_run_env.items()})
    # CLI --run-env overrides yaml values
    for item in args.run_env or []:
        if "=" in item:
            k, _, v = item.partition("=")
            run_env_dict[k.strip()] = v.strip()
        else:
            run_env_dict[item.strip()] = "1"
    # Re-resolve config now that we have the real --target (handles case where pre-parse differs)
    evaluator_cfg = _resolve_evaluator_config(target=args.target)

    setup_logging()

    # Ensure output directory exists — relative to repo root, not CWD
    output_path: Path = _REPO_ROOT / args.output_dir
    output_path.mkdir(parents=True, exist_ok=True)

    # Open trace file for appending evaluation events (JSONL)
    _hermes_cfg: dict = {}
    try:
        _cfg = get_config()
        _hermes_cfg = _cfg.get("hermes", {}) if isinstance(_cfg, dict) else {}
    except Exception:
        pass
    trace_file_rel: Optional[str] = _hermes_cfg.get("observability", {}).get(
        "trace_file"
    )
    trace_path: Optional[Path] = (
        (_REPO_ROOT / trace_file_rel) if trace_file_rel else None
    )
    if trace_path:
        trace_path.parent.mkdir(parents=True, exist_ok=True)

    # 1. Boot up Hermes Client
    if not args.dry_run:
        try:
            from codomyrmex.agents.hermes.hermes_client import HermesClient
        except ImportError as e:
            print_error(f"Import failed: {e}")
            return 1
        client = HermesClient()
        # Apply assessment-specific timeout so full-source prompts don't time out
        assessment_timeout = _resolve_assessment_timeout(evaluator_cfg)
        client.timeout = assessment_timeout  # type: ignore[attr-defined]
        print_info(
            f"  Assessment timeout: {assessment_timeout}s (full source code included)"
        )
    else:
        client = None
        print_info("  [DRY RUN] Hermes assessment will be skipped.")

    print_info("═" * 60)
    print_info(f"  Hermes Script Evaluator — Target: scripts/{args.target}")
    print_info(f"  Saving outputs to: {output_path}")
    if args.dry_run:
        print_info("  Mode: DRY RUN")
    print_info("═" * 60)

    if not args.dry_run and client.active_backend == "none":
        print_error("No backend available. Install 'hermes' CLI or 'ollama'.")
        return 1

    # 2. Discover Targets
    scripts_root = Path(__file__).parent.parent.parent
    if args.target == "all":
        target_dir = scripts_root
    else:
        target_dir = scripts_root / args.target

    if not target_dir.exists() or not target_dir.is_dir():
        print_error(f"Target directory {target_dir} does not exist.")
        return 1

    # Scripts that should be assessed from source only, NOT executed as subprocesses.
    # Running these would cause recursion (evaluator) or block on Hermes/Ollama (dispatcher).
    _no_exec_scripts: set[str] = set(
        evaluator_cfg.get(
            "no_exec_scripts",
            ["evaluate_orchestrators.py", "dispatch_hermes.py"],
        )
    )

    # Find python scripts (excluding dunder files and output dirs)
    _excluded_dirs: set = set(
        evaluator_cfg.get(
            "excluded_dirs", ["evaluations", "output", "__pycache__", "dispatches"]
        )
    )
    scripts_to_evaluate: list[Path] = []
    for py_file in target_dir.rglob("*.py"):
        if py_file.name.startswith("__"):
            continue
        # Skip files inside excluded subdirectories
        if any(part in _excluded_dirs for part in py_file.parts):
            continue
        scripts_to_evaluate.append(py_file)

    if not scripts_to_evaluate:
        print_info(f"No valid python scripts found in {target_dir}")
        return 0

    exec_count = sum(1 for p in scripts_to_evaluate if p.name not in _no_exec_scripts)
    no_exec_count = len(scripts_to_evaluate) - exec_count
    print_success(
        f"Found {len(scripts_to_evaluate)} scripts to evaluate. "
        f"({exec_count} will be executed, {no_exec_count} source-only assessment)"
    )
    print_info("─" * 60)

    all_evaluations = {}

    # 3. Execute and Assess Loop
    for script_path in scripts_to_evaluate:
        is_no_exec = script_path.name in _no_exec_scripts

        # Run script (skip for source-only scripts to avoid recursion/side-effects)
        if is_no_exec:
            script_info = {
                "path": script_path,
                "returncode": 0,
                "stdout": "(source-only assessment — script not executed)",
                "stderr": "",
            }
            print_info(
                f"  Source-only: {script_path.name} (skipping subprocess execution)"
            )
        else:
            script_info = run_script(
                script_path,
                timeout=evaluator_cfg.get("script_timeout", 30),
                extra_env=run_env_dict or None,
            )

        # Read source code
        try:
            with open(script_path, encoding="utf-8") as f:
                source_code = f.read()
        except Exception as e:
            print_error(f"  Could not read source code for {script_path.name}: {e}")
            continue

        # Assess (skip in dry-run mode)
        if args.dry_run:
            print_info(f"  [DRY RUN] Would assess {script_path.name} with Hermes.")
            continue

        eval_data = assess_script(
            client, script_info, source_code, target_dir=target_dir
        )

        if eval_data:
            script_name = script_path.name
            all_evaluations[script_name] = eval_data

            # Save individual JSON report
            json_file_path = output_path / f"{script_path.stem}_eval.json"
            try:
                with open(json_file_path, "w", encoding="utf-8") as f:
                    json.dump(eval_data, f, indent=4)
                print_info(f"  Saved JSON report to: {json_file_path}")
            except Exception as e:
                print_error(f"  Failed to save JSON for {script_name}: {e}")

            # Append to JSONL trace file
            if trace_path:
                try:
                    with open(trace_path, "a", encoding="utf-8") as tf:
                        trace_entry = {
                            "ts": datetime.now().isoformat(),
                            "script": script_name,
                            "adheres": eval_data.get("adherence_assessment", {}).get(
                                "adheres"
                            ),
                            "debt_count": len(eval_data.get("technical_debt", [])),
                        }
                        tf.write(json.dumps(trace_entry) + "\n")
                except Exception as e:
                    print_error(f"  Failed to write trace entry: {e}")

    # 4. Compile Overall Markdown Report
    report_file_path = output_path / "overall_evaluation_report.md"
    try:
        with open(report_file_path, "w", encoding="utf-8") as f:
            f.write("# Evaluator Orchestrations Report\n")
            f.write(f"Target: `scripts/{args.target}`\n")
            f.write(f"Generated: {datetime.now().isoformat()}\n\n")

            for script_name, data in all_evaluations.items():
                f.write(f"## Script: `{script_name}`\n")

                adherence = data.get("adherence_assessment", {})
                pass_fail = (
                    "✅ STRICT ADHERENCE"
                    if adherence.get("adheres", False)
                    else "❌ NON-COMPLIANT"
                )
                f.write(f"**Pattern Adherence**: {pass_fail}\n\n")
                f.write(f"> {adherence.get('reasoning', 'No reasoning provided.')}\n\n")

                f.write("### Technical Debt Identified:\n")
                f.writelines(f"- {debt}\n" for debt in data.get("technical_debt", []))

                f.write("\n### Underlying Method Improvements Required:\n")
                f.writelines(f"- {imp}\n" for imp in data.get("underlying_improvements", []))

                f.write("\n---\n\n")

        print_success(
            f"Successfully compiled overall markdown report to: {report_file_path}"
        )
    except Exception as e:
        print_error(f"Failed to save overall evaluation report: {e}")

    print_info("─" * 60)
    print_success("Evaluator run complete.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
