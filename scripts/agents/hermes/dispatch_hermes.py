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

try:
    from prompt_context import build_project_context, _EXEMPLAR_SCRIPTS
except ImportError:
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from prompt_context import build_project_context, _EXEMPLAR_SCRIPTS  # type: ignore[no-redef]

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
_MAX_SOURCE_CHARS: int = 12_000  # truncation guard — prevents dispatch timeouts for large scripts


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


# ── Filesystem Checkpoints ───────────────────────────────────────────


def _resolve_checkpoint_config() -> dict:
    """Load checkpoint configuration from hermes.yaml."""
    try:
        config = get_config()
        hermes_cfg: dict = config.get("hermes", {}) if isinstance(config, dict) else {}
        return hermes_cfg.get("checkpoint", {})
    except Exception:
        return {}


def _create_checkpoint(target_dir: Path, output_dir: Path) -> Path | None:
    """Create a filesystem snapshot before destructive --apply operations.

    Snapshots are stored as timestamped tar.gz archives in the configured
    checkpoint directory (default: ``~/.codomyrmex/checkpoints``).

    Args:
        target_dir: Directory being modified by apply operations.
        output_dir: Dispatch output directory (also checkpointed).

    Returns:
        Path to the checkpoint archive, or None on failure.
    """
    import shutil
    import tarfile

    cp_config = _resolve_checkpoint_config()
    if not cp_config.get("enabled", True):
        return None

    cp_dir = Path(cp_config.get("snapshot_dir", "~/.codomyrmex/checkpoints")).expanduser()
    cp_dir.mkdir(parents=True, exist_ok=True)

    # Enforce max_snapshots limit
    max_snapshots = int(cp_config.get("max_snapshots", 10))
    existing = sorted(cp_dir.glob("checkpoint_*.tar.gz"))
    while len(existing) >= max_snapshots:
        oldest = existing.pop(0)
        try:
            oldest.unlink()
        except OSError:
            pass

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    archive_path = cp_dir / f"checkpoint_{timestamp}.tar.gz"

    try:
        with tarfile.open(archive_path, "w:gz") as tar:
            if target_dir.exists():
                tar.add(target_dir, arcname=f"target/{target_dir.name}")
            if output_dir.exists():
                tar.add(output_dir, arcname=f"output/{output_dir.name}")
        print_success(f"  ✓ Checkpoint created: {archive_path}")
        return archive_path
    except Exception as exc:
        print_error(f"  ⚠  Checkpoint failed: {exc}")
        return None


def _rollback_checkpoint(archive_path: Path, restore_to: Path) -> bool:
    """Restore files from a checkpoint archive.

    Args:
        archive_path: Path to the checkpoint tar.gz archive.
        restore_to: Base directory to extract into.

    Returns:
        True if rollback succeeded.
    """
    import tarfile

    if not archive_path.exists():
        print_error(f"  Checkpoint not found: {archive_path}")
        return False

    try:
        with tarfile.open(archive_path, "r:gz") as tar:
            tar.extractall(path=restore_to, filter="data")
        print_success(f"  ✓ Rollback from {archive_path.name} complete")
        return True
    except Exception as exc:
        print_error(f"  ⚠  Rollback failed: {exc}")
        return False


def _validate_args(args: argparse.Namespace) -> str | None:
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
    target_dir: Path | None = None,
) -> str:
    """Compose a precise improvement prompt from an evaluation result.

    Includes the full script source code by default so Hermes has maximum
    context to generate accurate, targeted improvements. Also injects
    project coding standards, local AGENTS.md, and exemplary scripts so
    Hermes writes idiomatic, modern Python 3.11+ output.

    Args:
        script_name: Basename of the script (e.g. 'setup_hermes.py').
        source_path: Absolute path to the script source.
        eval_data: Parsed JSON from evaluate_orchestrators.py output.
        include_source: If False, omit source code (useful for debugging only).
        target_dir: Directory being targeted, used to load local AGENTS.md.

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
        if len(raw_source) > _MAX_SOURCE_CHARS:
            raw_source = (
                raw_source[:_MAX_SOURCE_CHARS]
                + f"\n\n# [TRUNCATED — source exceeds {_MAX_SOURCE_CHARS} chars;\n"
                  f"#  apply improvements to the HEAD section shown above and note\n"
                  f"#  that the full file is longer with the same patterns continuing]\n"
            )
        source_section = f"\n--- CURRENT SOURCE CODE ---\n{raw_source}\n----------------------------\n"

    # Build rich project context: coding standards + AGENTS.md + exemplary scripts
    project_context = build_project_context(
        target_dir=target_dir or source_path.parent,
        repo_root=_REPO_ROOT,
        exemplar_paths=list(_EXEMPLAR_SCRIPTS),
    )

    return (
        f"You are a senior Python engineer performing a targeted code improvement task.\n\n"
        f"{project_context}\n\n"
        f"Script: {script_name}\n"
        f"Evaluator Assessment: {reasoning}\n\n"
        f"Technical Debt to Fix:\n{debt_items}\n\n"
        f"Architectural Improvements Required:\n{improvement_items}\n"
        f"{source_section}\n"
        f"Please implement all of the improvements above directly into the source code.\n"
        f"IMPORTANT: Return ONLY the improved, complete Python source file.\n"
        f"Do NOT include markdown fences, explanations, or any text outside the Python code.\n"
        f"The output will be written directly to disk — start with the shebang or import line.\n"
        f"Follow ALL coding standards listed in the PROJECT CONTEXT above (Python 3.11+, no legacy typing imports).\n"
    )


def _extract_python_from_response(content: str) -> str:
    """Extract clean Python source from a Hermes response.

    Handles three common response formats:
    1. Pure Python (no fences) — returned as-is.
    2. ```python ... ``` fenced block — inner content extracted.
    3. ``` ... ``` generic fenced block — inner content extracted.

    Args:
        content: Raw string returned by Hermes.

    Returns:
        Clean Python source code string, stripped of leading/trailing whitespace.
    """
    import re as _re
    # Try ```python ... ``` or ``` ... ``` fenced blocks first
    fenced = _re.search(r"```(?:python)?\n(.*?)\n```", content, _re.DOTALL)
    if fenced:
        return fenced.group(1).strip()
    # Fallback: strip any leading/trailing non-code prose lines
    lines = content.strip().splitlines()
    # Drop leading lines that are clearly prose (no Python tokens)
    start = 0
    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped.startswith(("#!", "#", "import ", "from ", "def ", "class ", '"""', "'''")):
            start = i
            break
    return "\n".join(lines[start:]).strip()


def _modernize_python(code: str) -> str:
    """Post-process Hermes-generated Python to enforce Python 3.11+ syntax.

    Hermes3/Ollama tends to generate legacy ``typing`` module constructs even
    when told not to. This function runs targeted regex passes to:

    1. Replace ``Optional[X]`` with ``X | None``
    2. Replace generic aliases ``Dict[...] → dict[...]``, ``List[...] → list[...]``,
       ``Tuple[...] → tuple[...]``, ``Set[...] → set[...]``, ``FrozenSet[...] → frozenset[...]``
    3. Remove legacy bare imports of now-builtin typing names (Dict, List, etc.)
       from ``typing`` import lines, leaving only names still needed.
    4. Remove now-empty ``from typing import ...`` lines.

    The transformation is conservative — it only acts on clearly unambiguous
    patterns and leaves complex generics (e.g. nested multi-arg tuples) intact
    for human review.

    Args:
        code: Python source code string.

    Returns:
        Modernized Python source code.
    """
    import re as _re

    # 1. Replace Optional[X] → X | None (handles nested brackets using a simple heuristic)
    def _replace_optional(m: "_re.Match") -> str:
        inner = m.group(1)
        # Avoid double-wrapping if already 'X | None'
        if "| None" in inner or "None |" in inner:
            return m.group(0)
        return f"{inner} | None"

    code = _re.sub(r"Optional\[([^\[\]]+)\]", _replace_optional, code)
    # Second pass: catches Optional[dict[str,int]] after alias substitution
    code = _re.sub(r"Optional\[([^\[\]]+\[[^\]]*\])\]", _replace_optional, code)

    # 2. Replace capitalized generic aliases with lowercase builtins
    _alias_map = {
        "Dict": "dict",
        "List": "list",
        "Tuple": "tuple",
        "Set": "set",
        "FrozenSet": "frozenset",
        "Type": "type",
    }
    for old, new in _alias_map.items():
        # Replace 'OldName[' → 'new[' (only when followed by '[' — i.e. generic use)
        code = _re.sub(rf"\b{old}\[", f"{new}[", code)

    # 3. Remove legacy names from 'from typing import ...' lines
    _legacy_names = {
        "Optional", "Dict", "List", "Tuple", "Set", "FrozenSet",
        "Type", "Union",  # Union stays only if Literal/other types remain
    }
    def _clean_typing_import(m: "_re.Match") -> str:
        prefix = m.group(1)   # 'from typing import ' or 'from typing import ('
        names_raw = m.group(2)  # the names part
        # Split by comma, strip whitespace and parens
        names = [n.strip().strip("()") for n in names_raw.replace("\n", ",").split(",")]
        kept = [n for n in names if n and n not in _legacy_names]
        if not kept:
            return ""  # entire import line removed
        return f"{prefix}{', '.join(kept)}"

    # Handle: from typing import X, Y, Z  (single line)
    code = _re.sub(
        r"(from typing import )([\w, ]+)",
        _clean_typing_import,
        code,
    )
    # Handle: from typing import (X, Y, Z)  (parenthesised, simplified)
    code = _re.sub(
        r"(from typing import \()([\w,\s]+)\)",
        lambda m: _clean_typing_import(m) + (")" if _clean_typing_import(m) else ""),
        code,
    )

    # 4. Drop any now-empty 'from typing import ' or blank lines left by step 3
    result_lines = []
    for line in code.splitlines():
        stripped = line.strip()
        # Drop lines that are just 'from typing import' with nothing after the keyword
        if _re.match(r"^from typing import\s*$", stripped):
            continue
        result_lines.append(line)

    # Collapse multiple consecutive blank lines to max 2
    final: list[str] = []
    blank_count = 0
    for line in result_lines:
        if line.strip() == "":
            blank_count += 1
            if blank_count <= 2:
                final.append(line)
        else:
            blank_count = 0
            final.append(line)

    return "\n".join(final)


def _dispatch_hermes(
    client: object,
    script_name: str,
    prompt: str,
    output_dir: Path,
    apply: bool = False,
    source_path: Path | None = None,
    backup: bool = True,
) -> bool:
    """Send a prompt to Hermes and save the guidance response to markdown.

    When *apply* is True, the improved Python source extracted from Hermes's
    response is also written directly back to *source_path*, with an optional
    ``.bak`` backup of the original created first.

    Args:
        client: Initialized HermesClient instance.
        script_name: Name of the script being improved.
        prompt: The dispatch prompt built from eval data.
        output_dir: Directory to save the guidance file.
        apply: If True, write improved code back to the original source file.
        source_path: Required when apply=True — path to the script to overwrite.
        backup: If True (default), create a .bak copy before overwriting.

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
            # Always save guidance markdown so the improvement is visible
            guidance_path = output_dir / f"{stem}_guidance.md"
            guidance_path.write_text(
                f"# Hermes Improvement Guidance: `{script_name}`\n\n"
                f"_Generated: {datetime.now().isoformat()}_\n\n"
                f"```python\n{response.content}\n```\n",
                encoding="utf-8",
            )
            print_success(f"  ✓ Guidance saved to {guidance_path}")

            # Apply mode: write improved code back to the source file
            if apply and source_path is not None:
                python_code = _extract_python_from_response(response.content)
                if not python_code.strip():
                    print_error(
                        f"  ⚠️  --apply: could not extract valid Python from Hermes response "
                        f"for {script_name}. Guidance file written but source NOT modified."
                    )
                else:
                    # Post-process: modernize to Python 3.11+ syntax
                    modernized = _modernize_python(python_code)
                    if modernized != python_code:
                        delta = abs(len(modernized) - len(python_code))
                        print_info(f"  🔧 Modernized syntax ({delta} chars changed): legacy typing → 3.11+ style")
                    python_code = modernized
                    # Backup original
                    if backup and source_path.exists():
                        bak_path = source_path.with_suffix(".py.bak")
                        bak_path.write_bytes(source_path.read_bytes())
                        print_info(f"  ✓ Backup written to {bak_path.name}")
                    # Write improved + modernized code
                    source_path.write_text(python_code + "\n", encoding="utf-8")
                    print_success(f"  ✅ Applied improvements to {source_path}")

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


def _boot_hermes_client(effective_timeout: int) -> tuple[object | None, int]:
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
        "--apply",
        action="store_true",
        default=dispatch_cfg.get("apply", False),
        help=(
            "After generating guidance, extract the improved Python code from "
            "Hermes's response and write it directly back to the original source file. "
            "Original file is backed up as <script>.py.bak unless --no-backup is set. "
            "Guidance markdown is always saved regardless."
        ),
    )
    parser.add_argument(
        "--no-backup",
        action="store_true",
        default=False,
        help="Skip creating .py.bak backups when --apply overwrites source files.",
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
    if args.apply:
        backup_note = " (with .bak backup)" if not args.no_backup else " (NO backup)"
        print_info(f"  Apply:      ✅ Improved code will be written to source files{backup_note}")
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
    hermes_client: object | None = None
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
            target_dir=target_dir,
        )
        prompt_chars = len(prompt)
        print_info(f"  Prompt length: {prompt_chars} chars | include_source: {use_source}")
        if use_source and prompt_chars > _MAX_SOURCE_CHARS + 500:  # +500 for prompt overhead
            print_info(
                f"  ⚠️  Source was auto-truncated to {_MAX_SOURCE_CHARS} chars "
                f"(dispatch_timeout={effective_timeout}s). Review guidance for completeness."
            )

        if args.dry_run:
            print_info(
                f"  [DRY RUN] Would dispatch to '{args.dispatch_agent}' "
                f"(mode: {args.dispatch_mode}). Prompt length: {len(prompt)} chars."
            )
            dispatched[script_name] = {"status": "dry-run", "artefact": None}
            continue

        success: bool = False
        artefact: Path | None = None

        # Filesystem checkpoint: snapshot before destructive --apply
        if args.apply:
            _create_checkpoint(target_dir, output_dir)

        if args.dispatch_agent == "hermes" and args.dispatch_mode == "prompt":
            success = _dispatch_hermes(
                hermes_client,
                script_name,
                prompt,
                output_dir,
                apply=args.apply,
                source_path=source_path,
                backup=not args.no_backup,
            )
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
