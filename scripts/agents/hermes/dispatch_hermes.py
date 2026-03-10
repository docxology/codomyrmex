#!/usr/bin/env python3
"""Hermes Agent — Sweep-and-Dispatch Orchestrator.

Reads pre-generated evaluation JSON files (from evaluate_orchestrators.py),
then dispatches targeted improvement prompts to a configurable agent:

  - hermes : send prompt directly to HermesClient; save guidance markdown
  - jules  : write a 'jules remote send' shell script per file
  - claude : write a 'claude -p' shell script per file

Usage:
    # Dry run — show what would be dispatched
    python scripts/agents/hermes/dispatch_hermes.py --dry-run

    # Dispatch using Hermes (default)
    python scripts/agents/hermes/dispatch_hermes.py --target agents/hermes

    # Dispatch only NON-COMPLIANT scripts via Jules
    python scripts/agents/hermes/dispatch_hermes.py \\
        --dispatch-agent jules --filter-failing

    # Full sweep with Claude Code
    python scripts/agents/hermes/dispatch_hermes.py \\
        --target agents/hermes \\
        --eval-dir evaluations \\
        --dispatch-agent claude \\
        --dispatch-mode issue \\
        --output-dir dispatches/2026-03-10
"""

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

# Bootstrap path only — not needed when package is already installed
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

# ── Module-level constants ───────────────────────────────────────────────
_REPO_ROOT: Path = Path(__file__).resolve().parent.parent.parent.parent
_SCRIPTS_ROOT: Path = _REPO_ROOT / "scripts"
_SUPPORTED_AGENTS: tuple[str, ...] = ("hermes", "jules", "claude")
_SUPPORTED_MODES: tuple[str, ...] = ("prompt", "issue")
_DEFAULT_TARGET: str = "agents/hermes"
_DEFAULT_EVAL_DIR: str = "evaluations"
_DEFAULT_DISPATCH_AGENT: str = "hermes"
_DEFAULT_DISPATCH_MODE: str = "prompt"
_DEFAULT_OUTPUT_DIR: str = "dispatches"
_DEFAULT_TIMEOUT_S: int = 600  # generous default for full-source prompts through Ollama


def _resolve_dispatch_config() -> dict:
    """Load hermes.yaml dispatch section, returning sensible defaults on any error."""
    try:
        config = get_config()
        hermes_cfg: dict = config.get("hermes", {}) if isinstance(config, dict) else {}
        return hermes_cfg.get("dispatch", {})
    except Exception:
        return {}


def _resolve_ollama_timeout() -> int:
    """Read the dispatch-specific Ollama timeout from hermes.yaml.

    Prefers `dispatch_timeout` (for full-source prompts), falls back to
    `timeout`, then to `_DEFAULT_TIMEOUT_S`.
    """
    try:
        config = get_config()
        hermes_cfg: dict = config.get("hermes", {}) if isinstance(config, dict) else {}
        return int(
            hermes_cfg.get("dispatch_timeout", hermes_cfg.get("timeout", _DEFAULT_TIMEOUT_S))
        )
    except Exception:
        return _DEFAULT_TIMEOUT_S


def _validate_args(args: argparse.Namespace) -> Optional[str]:
    """Validate parsed CLI arguments before execution begins.

    Args:
        args: Parsed argument namespace.

    Returns:
        An error message string if any argument is invalid, or None if all are valid.
    """
    if args.dispatch_agent not in _SUPPORTED_AGENTS:
        return f"Invalid --dispatch-agent '{args.dispatch_agent}'. Choose from: {', '.join(_SUPPORTED_AGENTS)}"
    if args.dispatch_mode not in _SUPPORTED_MODES:
        return f"Invalid --dispatch-mode '{args.dispatch_mode}'. Choose from: {', '.join(_SUPPORTED_MODES)}"
    if args.target and ".." in args.target:
        return "--target must not contain '..' path components."
    return None


def _load_eval_results(eval_dir: Path, target_dir: Path) -> dict[str, dict]:
    """Scan eval_dir for *_eval.json files belonging to scripts in target_dir.

    Args:
        eval_dir: Directory containing `<stem>_eval.json` files.
        target_dir: Directory whose scripts produced the evaluations.

    Returns:
        Mapping of script_name → parsed eval data dict.
    """
    results: dict[str, dict] = {}

    if not eval_dir.exists():
        print_error(f"Evaluation directory not found: {eval_dir}")
        return results

    if not eval_dir.is_dir():
        print_error(f"Eval path is not a directory: {eval_dir}")
        return results

    for json_file in sorted(eval_dir.glob("*_eval.json")):
        script_stem = json_file.stem.replace("_eval", "")
        script_path = target_dir / f"{script_stem}.py"
        if not script_path.exists():
            # eval file for a script not in target — silently skip
            continue
        try:
            raw = json_file.read_text(encoding="utf-8")
            data = json.loads(raw)
        except json.JSONDecodeError as exc:
            print_error(f"  Malformed JSON in {json_file.name}: {exc}")
            continue
        except OSError as exc:
            print_error(f"  Could not read {json_file.name}: {exc}")
            continue
        results[f"{script_stem}.py"] = {"data": data, "source_path": script_path}

    return results


def _build_dispatch_prompt(
    script_name: str,
    source_path: Path,
    eval_data: dict,
    include_source: bool = True,
) -> str:
    """Compose a precise improvement prompt from an evaluation result.

    Includes the full script source code by default so Hermes has maximum
    context to generate accurate, targeted improvements.

    Args:
        script_name: Basename of the script (e.g. 'setup_hermes.py').
        source_path: Absolute path to the script source.
        eval_data: Parsed JSON from evaluate_orchestrators.py output.
        include_source: If False, omit source code (useful for debugging only).

    Returns:
        A self-contained prompt string ready to send to any LLM agent.
    """
    if not isinstance(eval_data, dict):
        return f"# Dispatch prompt for {script_name}\n\nNo eval data available.\n"

    technical_debt: list = eval_data.get("technical_debt", [])
    improvements: list = eval_data.get("underlying_improvements", [])
    reasoning: str = eval_data.get("adherence_assessment", {}).get(
        "reasoning", "No reasoning provided."
    )

    debt_items = "\n".join(f"- {d}" for d in technical_debt) or "None identified."
    improvement_items = "\n".join(f"- {i}" for i in improvements) or "None identified."

    source_section = ""
    if include_source:
        try:
            raw_source = source_path.read_text(encoding="utf-8")
        except OSError:
            raw_source = "# [source unavailable — file could not be read]"
        source_section = f"\n--- CURRENT SOURCE CODE ---\n{raw_source}\n----------------------------\n"

    return (
        f"You are a senior Python engineer performing a targeted code improvement task.\n\n"
        f"Script: {script_name}\n"
        f"Evaluator Assessment: {reasoning}\n\n"
        f"Technical Debt to Fix:\n{debt_items}\n\n"
        f"Architectural Improvements Required:\n{improvement_items}\n"
        f"{source_section}\n"
        f"Please implement all of the improvements above directly into the source code.\n"
        f"Return ONLY the improved, complete Python source file. No markdown, no extra text.\n"
    )


def _dispatch_hermes(
    client: object,
    script_name: str,
    prompt: str,
    output_dir: Path,
) -> bool:
    """Send a prompt to Hermes and save the guidance response to markdown.

    Args:
        client: Initialized HermesClient instance.
        script_name: Name of the script being improved.
        prompt: The dispatch prompt built from eval data.
        output_dir: Directory to save the guidance file.

    Returns:
        True on success, False on failure.
    """
    if client is None:
        print_error(f"  Cannot dispatch {script_name}: no Hermes client available.")
        return False

    print_info(f"  Dispatching to Hermes for {script_name}...")
    try:
        response = client.chat_session(prompt=prompt)  # type: ignore[attr-defined]
        if response.is_success():
            stem = script_name.replace(".py", "")
            guidance_path = output_dir / f"{stem}_guidance.md"
            guidance_path.write_text(
                f"# Hermes Improvement Guidance: `{script_name}`\n\n"
                f"_Generated: {datetime.now().isoformat()}_\n\n"
                f"```python\n{response.content}\n```\n",
                encoding="utf-8",
            )
            print_success(f"  ✓ Guidance saved to {guidance_path}")
            return True
        else:
            print_error(f"  Hermes response error for {script_name}: {response.error}")
            return False
    except Exception as exc:
        print_error(f"  Dispatch exception for {script_name}: {exc}")
        return False


def _dispatch_shell(
    agent: str,
    script_name: str,
    prompt: str,
    output_dir: Path,
    source_path: Path,
) -> bool:
    """Write a shell script that dispatches improvements via Jules or Claude Code.

    Args:
        agent: 'jules' or 'claude'.
        script_name: Name of the script being improved.
        prompt: The dispatch prompt built from eval data.
        output_dir: Directory to save the shell script.
        source_path: Absolute path to the source file to edit.

    Returns:
        True on success, False on failure.
    """
    if agent not in ("jules", "claude"):
        print_error(f"  Unsupported shell dispatch agent: '{agent}'. Use 'jules' or 'claude'.")
        return False

    stem = script_name.replace(".py", "")
    # Escape single-quotes for POSIX shell embedding
    escaped_prompt = prompt.replace("'", "'\"'\"'")
    timestamp = datetime.now().isoformat()

    if agent == "jules":
        script_content = (
            f"#!/bin/bash\n"
            f"# Auto-generated by dispatch_hermes.py — {timestamp}\n"
            f"# Dispatches improvement task for: {script_name}\n"
            f"set -e\n\n"
            f"jules remote send \\\n"
            f"  --file \"{source_path}\" \\\n"
            f"  --prompt '{escaped_prompt}'\n"
        )
        out_path = output_dir / f"{stem}_jules.sh"
    else:  # claude
        script_content = (
            f"#!/bin/bash\n"
            f"# Auto-generated by dispatch_hermes.py — {timestamp}\n"
            f"# Dispatches improvement task for: {script_name}\n"
            f"set -e\n\n"
            f"claude -p '{escaped_prompt}' \\\n"
            f"  --file \"{source_path}\" \\\n"
            f"  --output \"{source_path}\"\n"
        )
        out_path = output_dir / f"{stem}_claude.sh"

    try:
        out_path.write_text(script_content, encoding="utf-8")
        out_path.chmod(0o755)
        print_success(f"  ✓ Shell script written to {out_path}")
        return True
    except OSError as exc:
        print_error(f"  Could not write shell script for {script_name}: {exc}")
        return False


def _compile_manifest(
    dispatched: dict[str, dict],
    dispatch_agent: str,
    output_dir: Path,
) -> None:
    """Write a DISPATCH_MANIFEST.md summarising all actions taken.

    Args:
        dispatched: Mapping of script_name → {'status': 'ok'|'fail'|'dry-run', 'artefact': path}.
        dispatch_agent: Agent used (hermes/jules/claude).
        output_dir: Directory where the manifest will be saved.
    """
    manifest_path = output_dir / "DISPATCH_MANIFEST.md"
    lines = [
        "# Dispatch Manifest\n\n",
        f"**Agent**: `{dispatch_agent}`  \n",
        f"**Generated**: {datetime.now().isoformat()}  \n",
        f"**Output dir**: `{output_dir}`  \n\n",
        "| Script | Status | Artefact |\n",
        "| --- | --- | --- |\n",
    ]
    for script_name, info in dispatched.items():
        status = info.get("status", "fail")
        status_icon = "✅" if status == "ok" else ("⏭️" if status == "dry-run" else "❌")
        artefact = str(info.get("artefact") or "—")
        lines.append(f"| `{script_name}` | {status_icon} {status} | `{artefact}` |\n")

    try:
        manifest_path.write_text("".join(lines), encoding="utf-8")
        print_success(f"Manifest written to {manifest_path}")
    except OSError as exc:
        print_error(f"Could not write manifest: {exc}")


def _boot_hermes_client(effective_timeout: int) -> tuple[Optional[object], int]:
    """Import, initialize, and configure a HermesClient for dispatch use.

    Extracted from main() to separate client boot logic from orchestration.

    Args:
        effective_timeout: Ollama subprocess timeout in seconds. Applied to
            client.timeout so full-source dispatch prompts don't time out.

    Returns:
        Tuple of (client, return_code). If return_code is non-zero, client
        is None and the caller should propagate the error code.
    """
    try:
        from codomyrmex.agents.hermes import HermesClient
        client = HermesClient()
    except ImportError as exc:
        print_error(f"Cannot load HermesClient: {exc}")
        return None, 1

    # Always apply the dispatch-specific (generous) timeout
    client.timeout = effective_timeout  # type: ignore[attr-defined]
    print_info(f"  Hermes timeout set to {effective_timeout}s for full-source dispatch prompts.")

    if client.active_backend == "none":  # type: ignore[attr-defined]
        print_error("No Hermes backend available. Install 'hermes' CLI or 'ollama'.")
        return None, 1

    return client, 0


def main() -> int:
    dispatch_cfg = _resolve_dispatch_config()

    parser = argparse.ArgumentParser(
        description="Hermes Sweep-and-Dispatch: read eval JSONs and dispatch improvements.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--target",
        type=str,
        default=_DEFAULT_TARGET,
        help=f"Target subdirectory within scripts/ (default: '{_DEFAULT_TARGET}').",
    )
    parser.add_argument(
        "--eval-dir",
        type=str,
        default=dispatch_cfg.get("eval_dir", _DEFAULT_EVAL_DIR),
        help=f"Repo-root-relative directory containing *_eval.json files (default: '{_DEFAULT_EVAL_DIR}').",
    )
    parser.add_argument(
        "--dispatch-agent",
        type=str,
        choices=list(_SUPPORTED_AGENTS),
        default=dispatch_cfg.get("agent", _DEFAULT_DISPATCH_AGENT),
        help=f"Agent to use for dispatching improvements (default: '{_DEFAULT_DISPATCH_AGENT}').",
    )
    parser.add_argument(
        "--dispatch-mode",
        type=str,
        choices=list(_SUPPORTED_MODES),
        default=dispatch_cfg.get("mode", _DEFAULT_DISPATCH_MODE),
        help=f"'prompt' sends to the agent directly; 'issue' writes shell scripts (default: '{_DEFAULT_DISPATCH_MODE}').",
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default=dispatch_cfg.get("output_dir", _DEFAULT_OUTPUT_DIR),
        help=f"Repo-root-relative directory for dispatch artefacts (default: '{_DEFAULT_OUTPUT_DIR}').",
    )
    parser.add_argument(
        "--filter-failing",
        action="store_true",
        default=dispatch_cfg.get("filter_failing", False),
        help="Only dispatch improvements for NON-COMPLIANT scripts.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        default=False,
        help="Analyse and plan dispatch without writing any artefacts.",
    )
    parser.add_argument(
        "--no-source",
        action="store_true",
        default=False,
        help=(
            "Omit source code from the dispatch prompt. Not recommended — "
            "Hermes produces much better improvements with full source context. "
            "Use only when debugging timeout issues."
        ),
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=None,
        help=(
            "Override Ollama inference timeout in seconds "
            f"(default: dispatch_timeout from hermes.yaml, currently {_resolve_ollama_timeout()}s)."
        ),
    )
    args = parser.parse_args()

    # ── Input validation ──────────────────────────────────────────────
    validation_error = _validate_args(args)
    if validation_error:
        print_error(f"Argument error: {validation_error}")
        return 2

    setup_logging()

    output_dir: Path = _REPO_ROOT / args.output_dir
    if not args.dry_run:
        try:
            output_dir.mkdir(parents=True, exist_ok=True)
        except OSError as exc:
            print_error(f"Cannot create output directory {output_dir}: {exc}")
            return 1

    eval_dir: Path = _REPO_ROOT / args.eval_dir
    target_dir: Path = _SCRIPTS_ROOT / args.target

    if not target_dir.exists():
        print_error(f"Target directory does not exist: {target_dir}")
        return 1

    print_info("═" * 60)
    print_info("  Hermes Sweep-and-Dispatch")
    print_info(f"  Target:     scripts/{args.target}")
    print_info(f"  Eval dir:   {eval_dir}")
    print_info(f"  Agent:      {args.dispatch_agent}")
    print_info(f"  Mode:       {args.dispatch_mode}")
    print_info(f"  Output:     {output_dir}")
    if args.filter_failing:
        print_info("  Filter:     NON-COMPLIANT only")
    if args.dry_run:
        print_info("  [DRY RUN]   No artefacts will be written.")
    print_info("═" * 60)

    # 1. Load evaluation results
    eval_results = _load_eval_results(eval_dir, target_dir)
    if not eval_results:
        print_error(f"No evaluation files found in {eval_dir} matching scripts in {target_dir}.")
        print_info("  Hint: run evaluate_orchestrators.py first to generate eval JSON files.")
        return 1

    # Filter to non-compliant if requested
    if args.filter_failing:
        before = len(eval_results)
        eval_results = {
            name: info
            for name, info in eval_results.items()
            if not info["data"].get("adherence_assessment", {}).get("adheres", True)
        }
        print_info(f"  Filtered {before} → {len(eval_results)} non-compliant scripts.")

    if not eval_results:
        print_success("All evaluated scripts are compliant — nothing to dispatch.")
        return 0

    print_success(f"Found {len(eval_results)} script(s) to dispatch improvements for.")
    print_info("─" * 60)

    # 2. Boot Hermes client only if needed
    hermes_client: Optional[object] = None
    effective_timeout = args.timeout or _resolve_ollama_timeout()
    if args.dispatch_agent == "hermes" and args.dispatch_mode == "prompt" and not args.dry_run:
        hermes_client, rc = _boot_hermes_client(effective_timeout)
        if rc != 0:
            return rc

    # 3. Dispatch loop
    dispatched: dict[str, dict] = {}

    for script_name, info in eval_results.items():
        eval_data: dict = info["data"]
        source_path: Path = info["source_path"]

        print_info(f"\n  Script: {script_name}")
        debt_count = len(eval_data.get("technical_debt", []))
        improvement_count = len(eval_data.get("underlying_improvements", []))
        print_info(f"  Debt items: {debt_count}  |  Improvement items: {improvement_count}")

        # include_source: default True (full context), overridden by --no-source
        # Also honour dispatch.include_source from hermes.yaml if not overridden on CLI
        use_source = not args.no_source
        prompt = _build_dispatch_prompt(
            script_name, source_path, eval_data,
            include_source=use_source,
        )
        prompt_chars = len(prompt)
        print_info(f"  Prompt length: {prompt_chars} chars | include_source: {use_source}")

        if args.dry_run:
            print_info(
                f"  [DRY RUN] Would dispatch to '{args.dispatch_agent}' "
                f"(mode: {args.dispatch_mode}). Prompt length: {len(prompt)} chars."
            )
            dispatched[script_name] = {"status": "dry-run", "artefact": None}
            continue

        success: bool = False
        artefact: Optional[Path] = None

        if args.dispatch_agent == "hermes" and args.dispatch_mode == "prompt":
            success = _dispatch_hermes(hermes_client, script_name, prompt, output_dir)
            stem = script_name.replace(".py", "")
            artefact = output_dir / f"{stem}_guidance.md"

        elif args.dispatch_agent in ("jules", "claude") or args.dispatch_mode == "issue":
            # When dispatch_mode=issue with hermes agent, fall back to claude shell
            agent = args.dispatch_agent if args.dispatch_agent != "hermes" else "claude"
            success = _dispatch_shell(agent, script_name, prompt, output_dir, source_path)
            stem = script_name.replace(".py", "")
            artefact = output_dir / f"{stem}_{agent}.sh"

        dispatched[script_name] = {
            "status": "ok" if success else "fail",
            "artefact": artefact,
        }

    # 4. Compile manifest
    if not args.dry_run and dispatched:
        _compile_manifest(dispatched, args.dispatch_agent, output_dir)

    print_info("─" * 60)
    successes = sum(1 for v in dispatched.values() if v["status"] in ("ok", "dry-run"))
    print_success(f"Dispatch complete. {successes}/{len(dispatched)} succeeded.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
