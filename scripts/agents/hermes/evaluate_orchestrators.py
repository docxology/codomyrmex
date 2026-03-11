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
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

try:
    from codomyrmex.agents.core.config import get_config
except ImportError:
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent.parent / "src"))
    from codomyrmex.agents.core.config import get_config
from codomyrmex.utils.cli_helpers import (
    print_error,
    print_info,
    print_success,
    setup_logging,
)

# Repo root, resolved once
_REPO_ROOT: Path = Path(__file__).resolve().parent.parent.parent.parent


def _resolve_evaluator_config() -> dict:
    """Load hermes.yaml evaluator section, returning defaults on failure."""
    try:
        config = get_config()
        hermes_cfg = config.get("hermes", {}) if isinstance(config, dict) else {}
        return hermes_cfg.get("evaluator", {})
    except Exception:
        return {}


def _resolve_assessment_timeout(evaluator_cfg: dict) -> int:
    """Return the Hermes assessment timeout from config with a safe fallback.

    Uses evaluator.assessment_timeout first, then hermes.timeout, then 600s.
    """
    if evaluator_cfg.get("assessment_timeout"):
        return int(evaluator_cfg["assessment_timeout"])
    try:
        config = get_config()
        hermes_cfg = config.get("hermes", {}) if isinstance(config, dict) else {}
        return int(hermes_cfg.get("timeout", 600))
    except Exception:
        return 600


def run_script(script_path: Path, timeout: int = 30) -> dict:
    """Run a script and return its return code, stdout, and stderr.

    Args:
        script_path: Path to the Python script to execute.
        timeout: Maximum seconds to wait for the script. Configurable via
            evaluator.script_timeout in hermes.yaml (default: 30).
    """
    print_info(f"  Running: {script_path.name}...")
    try:
        # Run it with the current python interpreter
        result = subprocess.run(
            [sys.executable, str(script_path)],
            capture_output=True,
            text=True,
            timeout=timeout,
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


def _extract_json_object(text: str) -> Optional[str]:
    """Extract the first complete JSON object from *text* using brace-matching.

    Handles the case where Hermes returns a JSON object embedded in prose
    without code fences — e.g. "Here is my assessment:\n{\n  ...json...\n}".

    Args:
        text: Raw string that may contain a JSON object anywhere.

    Returns:
        The matched JSON substring, or None if no balanced object was found.
    """
    start = text.find("{")
    if start == -1:
        return None
    depth = 0
    for i, ch in enumerate(text[start:], start):
        if ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                return text[start : i + 1]
    return None


def _sanitize_json_candidate(text: str) -> str:
    """Escape literal control characters inside JSON string values.

    Hermes sometimes produces JSON where string values contain literal
    newlines/tabs (e.g. multi-line reasoning fields) instead of \\n/\\t
    escape sequences, causing json.loads() to fail with
    "Invalid control character" errors.

    This function does a lightweight state-machine pass over the text,
    only escaping control characters that appear inside quoted strings
    (not in structural characters or already-escaped sequences).

    Args:
        text: Raw candidate JSON string to sanitize.

    Returns:
        Sanitized version with control characters properly escaped.
    """
    _CTRL = {
        "\n": "\\n",
        "\r": "\\r",
        "\t": "\\t",
        "\b": "\\b",
        "\f": "\\f",
    }
    result: list[str] = []
    in_string = False
    i = 0
    while i < len(text):
        ch = text[i]
        if in_string:
            if ch == "\\" and i + 1 < len(text):
                # Pass through existing escape sequences unchanged
                result.append(ch)
                result.append(text[i + 1])
                i += 2
                continue
            if ch == '"':
                in_string = False
                result.append(ch)
            elif ch in _CTRL:
                result.append(_CTRL[ch])
            else:
                result.append(ch)
        else:
            if ch == '"':
                in_string = True
            result.append(ch)
        i += 1
    return "".join(result)


def extract_json_from_response(content: str) -> dict:
    """Parse JSON from the LLM response with 3-layer extraction + sanitization.

    Extraction order:
    1. Markdown code block (```json ... ``` or ``` ... ```)
    2. First balanced JSON object found anywhere in the prose text
    3. Whole content treated as raw JSON
    Each candidate is control-character-sanitized before parsing.

    Args:
        content: Raw text response from Hermes/Ollama.

    Returns:
        Parsed dict matching the evaluation schema, or a diagnostic fallback.
    """
    # Guard: empty or whitespace-only response
    if not content or not content.strip():
        return {
            "adherence_assessment": {
                "adheres": False,
                "reasoning": "Empty response from Hermes — backend may have timed out or returned nothing.",
            },
            "technical_debt": ["Empty LLM response"],
            "underlying_improvements": [],
        }

    candidates: list[str] = []

    # Layer 1 — markdown code block
    match = re.search(r"```(?:json)?\s*(.*?)\s*```", content, re.DOTALL)
    if match:
        candidates.append(match.group(1).strip())

    # Layer 2 — brace-matched JSON object embedded in prose
    embedded = _extract_json_object(content)
    if embedded:
        candidates.append(embedded)

    # Layer 3 — whole content (covers responses that ARE valid JSON)
    candidates.append(content.strip())

    last_exc: Optional[Exception] = None
    for raw_candidate in candidates:
        for candidate in (raw_candidate, _sanitize_json_candidate(raw_candidate)):
            try:
                result = json.loads(candidate)
                if isinstance(result, dict):
                    return result
            except json.JSONDecodeError as exc:
                last_exc = exc

    # Layer 4 — prose-verdict extraction for responses with no JSON structure.
    # Ollama sometimes returns pure text analysis (no {}) for longer prompts.
    # Heuristically determine compliance from signal words in the prose.
    prose = content.strip()
    if prose:
        lowered = prose.lower()
        # Look for positive compliance signals first
        adheres_signals = (
            "adheres to the thin orchestrator" in lowered
            or "follows the codomyrmex" in lowered
            or "meets all" in lowered
            or "complies with" in lowered
        )
        non_adheres_signals = (
            "does not adhere" in lowered
            or "fails to adhere" in lowered
            or "non-compliant" in lowered
            or "does not follow" in lowered
        )
        if adheres_signals and not non_adheres_signals:
            return {
                "adherence_assessment": {
                    "adheres": True,
                    "reasoning": f"[Prose-extracted verdict] {prose[:800]}",
                },
                "technical_debt": [],
                "underlying_improvements": [],
            }
        if non_adheres_signals:
            return {
                "adherence_assessment": {
                    "adheres": False,
                    "reasoning": f"[Prose-extracted verdict] {prose[:800]}",
                },
                "technical_debt": [prose[:300]],
                "underlying_improvements": [],
            }

    return {
        "adherence_assessment": {
            "adheres": False,
            "reasoning": f"Failed to parse JSON response (last error: {last_exc})",
        },
        "technical_debt": ["Malformed response from Hermes"],
        "underlying_improvements": [content[:500]],
    }



def assess_script(client, script_info: dict, source_code: str) -> dict:
    """Use Hermes to assess a script based on stdout, stderr, and source code."""
    script_name = script_info["path"].name

    prompt = f"""You are a senior principal engineer performing a code review and architectural assessment.

Evaluate the following Python orchestration script based on the Codomyrmex "Thin Orchestrator" pattern.
A thin orchestrator MUST:
1. Accept configuration transparently.
2. Formulate dependencies cleanly (no heavy business logic/transformations in the script itself).
3. Execute the core method.
4. Log and format the output beautifully.
5. Exit cleanly.

Script Name: {script_name}
Exit Code: {script_info['returncode']}

--- SCRIPT SOURCE CODE ---
{source_code}
--------------------------

--- STDOUT ---
{script_info['stdout']}
--------------

--- STDERR ---
{script_info['stderr']}
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
            print_info(f"  Adheres to pattern: {eval_data.get('adherence_assessment', {}).get('adheres', False)}")
            print_success("=" * 60)
            return eval_data
        print_error(f"  Hermes failed to assess {script_name}: {response.error}")
        return None
    except Exception as e:
        print_error(f"  Hermes evaluation error: {e}")
        return None


def main() -> int:
    evaluator_cfg = _resolve_evaluator_config()

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
    args = parser.parse_args()

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
    trace_file_rel: Optional[str] = _hermes_cfg.get("observability", {}).get("trace_file")
    trace_path: Optional[Path] = (_REPO_ROOT / trace_file_rel) if trace_file_rel else None
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
        print_info(f"  Assessment timeout: {assessment_timeout}s (full source code included)")
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
        evaluator_cfg.get("excluded_dirs", ["evaluations", "output", "__pycache__", "dispatches"])
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
            print_info(f"  Source-only: {script_path.name} (skipping subprocess execution)")
        else:
            script_info = run_script(
                script_path,
                timeout=evaluator_cfg.get("script_timeout", 30),
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

        eval_data = assess_script(client, script_info, source_code)

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
                            "adheres": eval_data.get("adherence_assessment", {}).get("adheres"),
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
                pass_fail = "✅ STRICT ADHERENCE" if adherence.get("adheres", False) else "❌ NON-COMPLIANT"
                f.write(f"**Pattern Adherence**: {pass_fail}\n\n")
                f.write(f"> {adherence.get('reasoning', 'No reasoning provided.')}\n\n")

                f.write("### Technical Debt Identified:\n")
                f.writelines(f"- {debt}\n" for debt in data.get("technical_debt", []))

                f.write("\n### Underlying Method Improvements Required:\n")
                f.writelines(f"- {imp}\n" for imp in data.get("underlying_improvements", []))

                f.write("\n---\n\n")

        print_success(f"Successfully compiled overall markdown report to: {report_file_path}")
    except Exception as e:
        print_error(f"Failed to save overall evaluation report: {e}")

    print_info("─" * 60)
    print_success("Evaluator run complete.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
