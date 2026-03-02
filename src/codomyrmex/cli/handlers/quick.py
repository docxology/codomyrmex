"""Quick orchestration CLI handlers.

Provides thin, composable commands for rapid orchestration tasks:
- run: Execute scripts or workflows quickly
- pipe: Chain commands together
- watch: Monitor and re-run on changes
- batch: Run multiple operations in parallel
"""

import asyncio
import json
from pathlib import Path
from typing import Any

from codomyrmex.logging_monitoring import get_logger

logger = get_logger(__name__)


def handle_quick_run(
    target: str,
    args: list[str] | None = None,
    timeout: int = 60,
    parallel: bool = False,
    verbose: bool = False
) -> bool:
    """Quick run a script, module, or workflow.

    Args:
        target: Script path, module name, or workflow name
        args: Additional arguments
        timeout: Execution timeout
        parallel: Run in parallel if multiple targets
        verbose: Show detailed output

    Returns:
        True if successful
    """
    from codomyrmex.orchestrator.parallel_runner import ParallelRunner

    from codomyrmex.orchestrator import (
        discover_scripts,
        run_script,
    )

    args = args or []
    target_path = Path(target)

    # Progress callback for verbose mode
    def progress(name: str, status: str, details: dict[str, Any]):
        """progress ."""
        if verbose:
            print(f"  [{status.upper()}] {name}", end="")
            if "execution_time" in details:
                print(f" ({details['execution_time']:.1f}s)", end="")
            print()

    try:
        # Case 1: Single script file
        if target_path.is_file() and target_path.suffix == ".py":
            print(f"Running script: {target_path.name}")
            result = run_script(target_path, timeout=timeout)
            _print_result(result, verbose)
            return result["status"] == "passed"

        # Case 2: Directory of scripts
        elif target_path.is_dir():
            scripts = discover_scripts(target_path, max_depth=2)
            if not scripts:
                print(f"No scripts found in {target_path}")
                return False

            print(f"Found {len(scripts)} scripts in {target_path}")

            if parallel:
                runner = ParallelRunner(progress_callback=progress if verbose else None)
                result = runner.run_scripts(scripts, timeout=timeout)
                _print_batch_result(result)
                return result.success
            else:
                success = True
                for script in scripts:
                    print(f"  Running: {script.name}")
                    r = run_script(script, timeout=timeout)
                    if r["status"] != "passed":
                        success = False
                        if not verbose:
                            print(f"    FAILED: {r.get('error', 'Unknown error')}")
                return success

        # Case 3: Module name (try to run module demo)
        elif "." not in target and "/" not in target:
            print(f"Running module: {target}")
            from codomyrmex.cli.handlers import handle_module_demo
            return handle_module_demo(target)

        # Case 4: Glob pattern
        elif "*" in target:
            from glob import glob
            scripts = [Path(p) for p in glob(target) if p.endswith(".py")]
            if not scripts:
                print(f"No scripts matching pattern: {target}")
                return False

            print(f"Running {len(scripts)} scripts matching '{target}'")
            runner = ParallelRunner(progress_callback=progress if verbose else None)
            result = runner.run_scripts(scripts, timeout=timeout)
            _print_batch_result(result)
            return result.success

        else:
            print(f"Unknown target: {target}")
            return False

    except Exception as e:
        print(f"Error: {e}")
        logger.exception("Quick run failed")
        return False


def handle_quick_pipe(commands: list[str], stop_on_error: bool = True) -> bool:
    """Pipe multiple commands together.

    Args:
        commands: List of commands to pipe
        stop_on_error: Stop on first error

    Returns:
        True if all commands succeeded
    """
    from codomyrmex.orchestrator import Workflow

    print(f"Piping {len(commands)} commands")

    # Build workflow from commands
    async def run_command(cmd: str, _task_results: dict = None) -> dict[str, Any]:
        """Run a single command."""
        import subprocess
        result = subprocess.run(
            cmd,
            shell=True,  # SECURITY: Intentional — pipe executor runs CLI command strings
            capture_output=True,
            text=True
        )
        return {
            "command": cmd,
            "returncode": result.returncode,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "success": result.returncode == 0
        }

    # Create tasks for each command
    workflow = Workflow(name="pipe", fail_fast=stop_on_error)

    prev_task = None
    for i, cmd in enumerate(commands):
        task_name = f"step_{i + 1}"
        deps = [prev_task] if prev_task else None

        # Create closure to capture cmd
        def make_action(command):
            """make Action ."""
            async def action(_task_results=None):
                return await run_command(command, _task_results)
            return action

        workflow.add_task(
            name=task_name,
            action=make_action(cmd),
            dependencies=deps
        )
        prev_task = task_name

    # Run workflow
    try:
        results = asyncio.run(workflow.run())
        summary = workflow.get_summary()

        print(f"\nPipeline {'succeeded' if summary['success'] else 'failed'}")
        print(f"  Steps: {summary['completed']}/{summary['total_tasks']} completed")

        for name, task in workflow.tasks.items():
            status_icon = "✓" if task.status.value == "completed" else "✗"
            print(f"  {status_icon} {name}")
            if task.error:
                print(f"    Error: {task.error}")

        return summary["success"]

    except Exception as e:
        print(f"Pipeline failed: {e}")
        return False


def handle_quick_batch(
    targets: list[str],
    workers: int = 4,
    timeout: int = 60,
    verbose: bool = False
) -> bool:
    """Run multiple targets in parallel batches.

    Args:
        targets: List of targets (scripts, modules, patterns)
        workers: Number of parallel workers
        timeout: Timeout per target
        verbose: Show detailed output

    Returns:
        True if all succeeded
    """
    from codomyrmex.orchestrator.parallel_runner import ParallelRunner

    from codomyrmex.orchestrator import discover_scripts

    # Collect all scripts
    all_scripts = []
    for target in targets:
        target_path = Path(target)
        if target_path.is_file():
            all_scripts.append(target_path)
        elif target_path.is_dir():
            all_scripts.extend(discover_scripts(target_path))
        elif "*" in target:
            from glob import glob
            all_scripts.extend(Path(p) for p in glob(target) if p.endswith(".py"))

    if not all_scripts:
        print("No scripts found")
        return False

    print(f"Running {len(all_scripts)} scripts with {workers} workers")

    def progress(name: str, status: str, details: dict[str, Any]):
        """progress ."""
        if verbose:
            print(f"  [{status}] {name}")

    runner = ParallelRunner(
        max_workers=workers,
        progress_callback=progress if verbose else None,
        default_timeout=timeout
    )

    result = runner.run_scripts(all_scripts)
    _print_batch_result(result)

    return result.success


def handle_quick_chain(
    scripts: list[str],
    timeout: int = 60,
    continue_on_error: bool = False
) -> bool:
    """Chain scripts to run sequentially, passing results.

    Args:
        scripts: List of script paths
        timeout: Timeout per script
        continue_on_error: Continue even if a script fails

    Returns:
        True if all succeeded
    """
    from codomyrmex.orchestrator import run_script

    print(f"Chaining {len(scripts)} scripts")

    results = []
    success = True
    prev_result = None

    for i, script_path in enumerate(scripts):
        script = Path(script_path)
        if not script.exists():
            print(f"  ✗ Script not found: {script}")
            if not continue_on_error:
                return False
            continue

        print(f"  [{i + 1}/{len(scripts)}] {script.name}...", end=" ", flush=True)

        # Pass previous result via environment
        env = {}
        if prev_result:
            env["PREV_RESULT"] = json.dumps(prev_result)
            env["PREV_STATUS"] = prev_result.get("status", "unknown")

        result = run_script(script, timeout=timeout, env=env)
        results.append(result)

        if result["status"] == "passed":
            print("✓")
        else:
            print(f"✗ ({result.get('error', result['status'])})")
            success = False
            if not continue_on_error:
                break

        prev_result = result

    print(f"\nChain {'completed' if success else 'failed'}: "
          f"{sum(1 for r in results if r['status'] == 'passed')}/{len(results)} passed")

    return success


def handle_quick_workflow(
    definition_file: str,
    params: str | None = None,
    verbose: bool = False
) -> bool:
    """Execute a workflow from a definition file.

    Args:
        definition_file: Path to workflow YAML/JSON file
        params: JSON parameters string
        verbose: Show detailed output

    Returns:
        True if successful
    """
    import yaml

    definition_path = Path(definition_file)
    if not definition_path.exists():
        print(f"Workflow definition not found: {definition_file}")
        return False

    # Parse parameters
    workflow_params = {}
    if params:
        try:
            workflow_params = json.loads(params)
        except json.JSONDecodeError:
            print(f"Invalid JSON parameters: {params}")
            return False

    # Load definition
    try:
        with open(definition_path) as f:
            if definition_path.suffix in [".yaml", ".yml"]:
                definition = yaml.safe_load(f)
            else:
                definition = json.load(f)
    except Exception as e:
        print(f"Failed to load workflow definition: {e}")
        return False

    # Execute workflow
    from codomyrmex.logistics.orchestration.project.orchestration_engine import (
        get_orchestration_engine,
    )

    try:
        engine = get_orchestration_engine()

        if verbose:
            print(f"Executing workflow: {definition.get('name', 'unnamed')}")
            print(f"Steps: {len(definition.get('steps', []))}")

        result = engine.execute_complex_workflow(definition)

        if result["success"]:
            print("Workflow completed successfully")
            if verbose and "results" in result:
                for step, step_result in result["results"].items():
                    print(f"  ✓ {step}")
            return True
        else:
            print(f"Workflow failed: {result.get('error', 'Unknown error')}")
            return False

    except Exception as e:
        print(f"Workflow execution failed: {e}")
        logger.exception("Workflow execution error")
        return False


def _print_result(result: dict[str, Any], verbose: bool = False):
    """Print single script result."""
    status = result.get("status", "unknown")
    name = result.get("name", "unknown")
    exec_time = result.get("execution_time", 0)

    if status == "passed":
        print(f"  ✓ {name} ({exec_time:.1f}s)")
    else:
        print(f"  ✗ {name} ({status})")
        if verbose and result.get("stderr"):
            lines = result["stderr"].strip().split("\n")
            for line in lines[-3:]:  # Last 3 lines
                print(f"    {line}")


def _print_batch_result(result):
    """Print batch execution result."""
    print("\nResults:")
    print(f"  Total:   {result.total}")
    print(f"  Passed:  {result.passed}")
    print(f"  Failed:  {result.failed}")
    print(f"  Timeout: {result.timeout}")
    print(f"  Time:    {result.execution_time:.1f}s")

    if result.failed > 0:
        print("\nFailed scripts:")
        for r in result.results:
            if r.get("status") != "passed":
                print(f"  ✗ {r.get('name', 'unknown')}: {r.get('error', r.get('status'))}")
