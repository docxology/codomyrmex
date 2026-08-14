"""MCP tools for the orchestrator module.

MCP callers may select only the small, explicitly registered set of pure
callables below.  Import paths are deliberately not treated as capabilities.
"""

from codomyrmex.logging_monitoring import get_logger
from codomyrmex.model_context_protocol.decorators import mcp_tool

logger = get_logger(__name__)

_SAFE_CALLABLES = {
    "builtins.abs": abs,
    "builtins.int": int,
    "builtins.len": len,
    "builtins.max": max,
    "builtins.min": min,
    "builtins.round": round,
    "builtins.str": str,
    "builtins.sum": sum,
}
_MAX_DAG_TASKS = 256
_MAX_WORKERS = 32


@mcp_tool(category="orchestrator")
def get_scheduler_metrics() -> dict:
    """Retrieve the current metrics of the Orchestrator AsyncScheduler.

    Returns:
        A dictionary containing scheduler metrics like active jobs and completion rates.
    """
    from codomyrmex.orchestrator import AsyncScheduler

    try:
        # We instantiate a scheduler to get its metrics layout
        # In a real environment, this might connect to a running daemon
        scheduler = AsyncScheduler()
        metrics = scheduler.metrics

        return {
            "status": "success",
            "metrics": {
                "total_jobs": metrics.jobs_scheduled,
                "completed": metrics.jobs_completed,
                "failed": metrics.jobs_failed,
                "cancelled": metrics.jobs_cancelled,
                "execution_time": metrics.total_execution_time,
            },
        }
    except (ValueError, RuntimeError, AttributeError, OSError, TypeError) as e:
        return {
            "status": "error",
            "message": f"Failed to retrieve scheduler metrics: {e}",
        }


@mcp_tool(category="orchestrator")
def analyze_workflow_dependencies(tasks: list[dict]) -> dict:
    """Analyze a proposed workflow DAG for cyclic dependencies.

    Args:
        tasks: A list of dictionaries, each containing 'id' and 'dependencies' (list of ids)

    Returns:
        Validation result indicating if the workflow is a valid DAG.
    """
    from codomyrmex.orchestrator import CycleError, Workflow

    try:
        if not isinstance(tasks, list) or not tasks:
            raise ValueError("tasks must be a non-empty list")
        if len(tasks) > _MAX_DAG_TASKS:
            raise ValueError(f"tasks must contain at most {_MAX_DAG_TASKS} entries")
        workflow = Workflow(name="analysis_workflow")
        seen: set[str] = set()
        for t in tasks:
            if not isinstance(t, dict) or not isinstance(t.get("id"), str):
                raise ValueError("each task must have a string id")
            task_id = t["id"].strip()
            if not task_id or task_id in seen:
                raise ValueError(f"task ids must be non-empty and unique: {task_id!r}")
            dependencies = t.get("dependencies", [])
            if not isinstance(dependencies, list) or not all(
                isinstance(dep, str) and dep.strip() for dep in dependencies
            ):
                raise ValueError(f"dependencies for {task_id!r} must be a list of ids")
            seen.add(task_id)
            workflow.add_task(task_id, lambda: None, dependencies=dependencies)

        workflow.validate()
        remaining = {
            name: set(task.dependencies) for name, task in workflow.tasks.items()
        }
        execution_order: list[str] = []
        while remaining:
            ready = sorted(name for name, deps in remaining.items() if not deps)
            if not ready:
                raise CycleError("Circular dependency detected")
            execution_order.extend(ready)
            for name in ready:
                remaining.pop(name)
            for deps in remaining.values():
                deps.difference_update(ready)

        return {
            "status": "success",
            "valid_dag": True,
            "execution_order": execution_order,
        }
    except CycleError as e:
        return {"status": "error", "valid_dag": False, "message": str(e)}
    except (ValueError, RuntimeError, AttributeError, OSError, TypeError) as e:
        return {"status": "error", "message": f"Failed to analyze workflow: {e}"}


@mcp_tool(category="orchestrator")
def orchestrator_run_dag(
    topology: str,
    tasks: list[dict],
    broadcast_message: dict | None = None,
    max_workers: int = 8,
) -> dict:
    """Execute tasks using a swarm topology (Fan-Out, Fan-In, Pipeline, or Broadcast).

    Each task dict must include:
    - ``id``: unique task identifier
    - ``fn_expr``: bounded expression using the documented pure builtins
      (e.g. ``"len('hello')"``), or ``fn`` set to a key in the explicit
      callable registry (for example ``"builtins.int"``).
    - Optional ``args``, ``kwargs`` for the callable.

    Args:
        topology: One of ``"fan_out"``, ``"fan_in"``, ``"pipeline"``, ``"broadcast"``.
        tasks: list of task specification dicts.
        broadcast_message: Message payload injected for ``broadcast`` mode.
        max_workers: Maximum parallel workers for concurrent modes.

    Returns:
        Aggregated result dict with per-task outputs, success/error counts.
    """
    try:
        from codomyrmex.orchestrator.swarm_topology import (
            SwarmTopology,
            TaskSpec,
            TopologyMode,
        )

        def _resolve_fn(task_dict: dict):
            """Resolve a callable from task dict."""
            if "fn" in task_dict:
                fn_name = task_dict["fn"]
                if fn_name not in _SAFE_CALLABLES:
                    raise ValueError(
                        f"callable {fn_name!r} is not in the orchestrator registry"
                    )
                return _SAFE_CALLABLES[fn_name]
            if "fn_expr" in task_dict:
                expr = task_dict["fn_expr"]
                if not isinstance(expr, str) or len(expr) > 256:
                    raise ValueError(
                        "fn_expr must be a string of at most 256 characters"
                    )
                if "__" in expr:
                    raise ValueError(
                        "Double underscores are not allowed in fn_expr for security reasons."
                    )

                safe_locals = {
                    "len": len,
                    "sum": sum,
                    "min": min,
                    "max": max,
                    "abs": abs,
                    "round": round,
                }
                return lambda *_a, **_kw: eval(  # nosec B307
                    expr, {"__builtins__": {}}, safe_locals
                )
            # Default: identity (return args as-is)
            return lambda *a, **kw: {"args": a, "kwargs": kw}

        if not isinstance(tasks, list) or not tasks:
            raise ValueError("tasks must be a non-empty list")
        if len(tasks) > _MAX_DAG_TASKS:
            raise ValueError(f"tasks must contain at most {_MAX_DAG_TASKS} entries")
        if not isinstance(max_workers, int) or not 1 <= max_workers <= _MAX_WORKERS:
            raise ValueError(f"max_workers must be between 1 and {_MAX_WORKERS}")
        seen_ids: set[str] = set()
        specs = []
        for i, task in enumerate(tasks):
            if not isinstance(task, dict):
                raise ValueError(f"task {i} must be an object")
            task_id = task.get("id", f"task_{i}")
            if (
                not isinstance(task_id, str)
                or not task_id.strip()
                or task_id in seen_ids
            ):
                raise ValueError(
                    f"task ids must be unique non-empty strings: {task_id!r}"
                )
            args = task.get("args", [])
            kwargs = task.get("kwargs", {})
            if not isinstance(args, list) or not isinstance(kwargs, dict):
                raise ValueError(
                    f"args must be a list and kwargs an object for {task_id!r}"
                )
            seen_ids.add(task_id)
            specs.append(
                TaskSpec(
                    task_id=task_id,
                    fn=_resolve_fn(task),
                    args=args,
                    kwargs=kwargs,
                    metadata=task.get("metadata", {}),
                )
            )

        topo = SwarmTopology(max_workers=max_workers)
        result = topo.run(
            TopologyMode(topology),
            specs,
            broadcast_message=broadcast_message,
        )
        status = "success" if result.get("error_count", 0) == 0 else "failed"
        return {"status": status, "topology": topology, **result}
    except (ValueError, RuntimeError, AttributeError, OSError, TypeError) as e:
        return {"status": "error", "message": f"DAG execution failed: {e}"}
