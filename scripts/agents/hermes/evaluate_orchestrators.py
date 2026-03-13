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
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path

try:
    import yaml as _yaml
    _YAML_AVAILABLE = True
except ImportError:
    _YAML_AVAILABLE = False

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
from codomyrmex.utils.json_helpers import extract_json_from_response
from codomyrmex.agents.hermes.prompts import build_assessment_prompt

try:
    from prompt_context import build_project_context
except ImportError:
    # Fallback if running from outside scripts/agents/hermes/
    import sys as _sys
    _sys.path.insert(0, str(Path(__file__).resolve().parent))
    from prompt_context import build_project_context

# Find repository root by locating pyproject.toml
def _find_repository_root() -> Path:
    """Find the repository root by searching upward for pyproject.toml."""
    current = Path(__file__).resolve()
    for parent in current.parents:
        if (parent / "pyproject.toml").exists():
            return parent
    # Fallback to git directory if pyproject.toml not found
    if (current / ".git").exists():
        return current
    # Last resort: use parent.parent.parent.parent (original behavior)
    return current.parent.parent.parent.parent

_REPO_ROOT: Path = _find_repository_root()
# Scripts root — direct parent of all target directories
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


def _resolve_evaluator_config(target: str | None = None) -> dict:
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


def run_script(script_path: Path, timeout: int = 30, extra_env: dict | None = None) -> dict:
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


def assess_script(client, script_info: dict, source_code: str, target_dir: Path | None = None) -> dict:
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
    project_context = build_project_context(target_dir) if target_dir else ""
    exemplar_context = ""
    if _EXEMPLAR_SCRIPTS:
        exemplar_snippets = []
        for script in _EXEMPLAR_SCRIPTS[:2]:  # Limit to avoid token overflow
            try:
                exemplar_snippets.append(f"# From {script.relative_to(_REPO_ROOT)}:\n{script.read_text()}")
            except OSError:
                pass
        if exemplar_snippets:
            exemplar_context = "\n\n---\n\nEXEMPLARY SCRIPTS (REFERENCE):\n\n" + "\n\n---\n\n".join(exemplar_snippets)

    # Compose prompt for Hermes
    prompt = build_assessment_prompt(
        script_name=script_name,
        script_info=script_info,
        source_code=source_code,
        project_context=project_context,
        exemplar_context=exemplar_context,
    )

    print_info(f"  Asking Hermes to assess {script_name}...")
    try:
        response = client.chat(prompt)
        content = response.get("content", "") if isinstance(response, dict) else str(response)
    except Exception as e:
        print_error(f"  Hermes assessment failed: {e}")
        return {
            "adherence_assessment": {
                "adheres": False,
                "reasoning": f"Hermes client error: {e}",
            },
            "technical_debt": ["Hermes client error"],

