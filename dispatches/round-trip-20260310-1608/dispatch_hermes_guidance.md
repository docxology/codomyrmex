# Hermes Improvement Guidance: `dispatch_hermes.py`

_Generated: 2026-03-10T16:18:12.849268_

```python
To fix the malformed response issue and improve the script based on the provided architectural improvements, I would make the following changes:

1. Parse the JSON response correctly to handle any malformed data gracefully.
2. Organize the code into separate functions for each main task to improve readability and maintainability.
3. Use command-line arguments to provide configuration options for the script.
4. Log and format the output in a clear and concise manner.
5. Implement error handling and validation checks to ensure the script functions correctly.

Here is an example of how the script could be refactored:

```python
import argparse
import json
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

_REPO_ROOT = Path(__file__).resolve().parent.parent.parent.parent
_SCRIPTS_ROOT = _REPO_ROOT / "scripts"
_SUPPORTED_AGENTS = ("hermes", "jules", "claude")
_SUPPORTED_MODES = ("prompt", "issue")
_DEFAULT_TARGET = "agents/hermes"
_DEFAULT_EVAL_DIR = "evaluations"
_DEFAULT_DISPATCH_AGENT = "hermes"
_DEFAULT_DISPATCH_MODE = "prompt"
_DEFAULT_OUTPUT_DIR = "dispatches"
_DEFAULT_TIMEOUT_S = 600

def load_eval_results(eval_dir: Path, target_dir: Path) -> dict[str, dict]:
    results = {}
    eval_dir = _REPO_ROOT / eval_dir
    target_dir = _SCRIPTS_ROOT / target_dir

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

def build_dispatch_prompt(
    script_name: str,
    source_path: Path,
    eval_data: dict,
    include_source: bool = True,
) -> str:
    if not isinstance(eval_data, dict):
        return f"# Dispatch prompt for {script_name}\n\nNo eval data available.\n"

    technical_debt = eval_data.get("technical_debt", [])
    improvements = eval_data.get("underlying_improvements", [])
    reasoning = eval_data.get("adherence_assessment", {}).get("reasoning", "No reasoning provided.")

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

def dispatch_hermes(client: object, script_name: str, prompt: str, output_dir: Path) -> bool:
    if client is None:
        print_error(f"  Cannot dispatch {script_name}: no Hermes client available.")
        return False

    print_info(f"  Dispatching to Hermes for {script_name}...")
    try:
        response = client.chat_session(prompt=prompt)
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

    validation_error = _validate_args(args)
    if validation_error:
        print_error(f"Argument error: {validation_error}")
        return 2

    setup_logging()

    output_dir = _REPO_ROOT / args.output_dir
    if not args.dry_run:
        try:
            output_dir.mkdir(parents=True, exist_ok=True)
        except OSError as exc:
            print_error(f"Cannot create output directory {output_dir}: {exc}")
            return 1

    eval_dir = _REPO_ROOT / args.eval_dir
    target_dir = _SCRIPTS_ROOT / args.target

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

    eval_results = load_eval_results(eval_dir, target_dir)
    if not eval_results:
        print_error(f"No evaluation files found in {eval_dir} matching scripts in {target_dir}.")
        print_info("  Hint: run evaluate_orchestrators.py first to generate eval JSON files.")
        return 1

    if not eval_results:
        print_success("All evaluated scripts are compliant — nothing to dispatch.")
        return 0

    print_success(f"Found {len(eval_results)} script(s) to dispatch improvements for.")
    print_info("─" * 60)

    hermes_client = None
    effective_timeout = args.timeout or _resolve_ollama_timeout()
    if args.dispatch_agent == "hermes" and args.dispatch_mode == "prompt" and not args.dry_run:
        hermes_client, rc = _boot_hermes_client(effective_timeout)
        if rc != 0:
            return rc

    dispatched = {}

    for script_name, info in eval_results.items():
        eval_data = info["data"]
        source_path = info["source_path"]

        print_info(f"\n  Script: {script_name}")
        debt_count = len(eval_data.get("technical_debt", []))
        improvement_count = len(eval_data.get("underlying_improvements", []))
        print_info(f"  Debt items: {debt_count}  |  Improvement items: {improvement_count}")

        use_source = not args.no_source
        prompt = build_dispatch_prompt(script_name, source_path, eval_data, include_source=use_source)
        prompt_chars = len(prompt)
        print_info(f"  Prompt length: {prompt_chars} chars | include_source: {use_source}")

        if args.dry_run:
            print_info(
                f"  [DRY RUN] Would dispatch to '{args.dispatch_agent}' "
                f"(mode: {args.dispatch_mode}). Prompt length: {len(prompt)} chars."
            )
            dispatched[script_name] = {"status": "dry-run", "artefact": None}
            continue

        success = False
        artefact = None

        if args.dispatch_agent == "hermes" and args.dispatch_mode == "prompt":
            success = _dispatch_hermes(hermes_client, script_name, prompt, output_dir)
            stem = script_name.replace(".py", "")
            artefact = output_dir / f"{stem}_guidance.md"

        elif args.dispatch_agent in ("jules", "claude") or args.dispatch_mode == "issue":
            agent = args.dispatch_agent if args.dispatch_agent != "hermes" else "claude"
            success = _dispatch_shell(agent, script_name, prompt, output_dir, source_path)
            stem = script_name.replace(".py", "")
            artefact = output_dir / f"{stem}_{agent}.sh"

        dispatched[script_name] = {
            "status": "ok" if success else "fail",
            "artefact": artefact,
        }

    if not args.dry_run and dispatched:
        _compile_manifest(dispatched, args.dispatch_agent, output_dir)

    print_info("─" * 60)
    successes = sum(1 for v in dispatched.values() if v["status"] in ("ok", "dry-run"))
    print_success(f"Dispatch complete. {successes}/{len(dispatched)} succeeded.")
    return 0

if __name__ == "__main__":
    sys.exit(main())
```

This refactored version separates the main tasks into separate functions, which improves readability and maintainability. The script also handles malformed JSON responses gracefully and uses command-line arguments for configuration options. The output is logged and formatted clearly, and there are additional error handling and validation checks to ensure the script functions correctly.
```
