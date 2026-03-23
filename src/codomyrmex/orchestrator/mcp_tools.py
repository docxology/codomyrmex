"""MCP tools for the orchestrator module."""

from codomyrmex.logging_monitoring import get_logger
from codomyrmex.model_context_protocol.decorators import mcp_tool

logger = get_logger(__name__)


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
    from codomyrmex.logistics.orchestration.project.task_orchestrator import Task
    from codomyrmex.orchestrator import CycleError, Workflow

    try:
        workflow = Workflow(name="analysis_workflow")
        for t in tasks:
            task_id = t.get("id")
            if not task_id:
                continue
            task = Task(name=task_id, action="", module="")
            workflow.add_task(task)  # type: ignore

        # Add dependencies in a second pass
        for t in tasks:
            task_id = t.get("id")
            deps = t.get("dependencies", [])
            for dep in deps:
                try:
                    workflow.add_dependency(task_id, dep)
                except (
                    ValueError,
                    RuntimeError,
                    AttributeError,
                    OSError,
                    TypeError,
                ) as e:
                    logger.warning(
                        "Failed to add dependency %s -> %s: %s", task_id, dep, e
                    )

        # Verification happens implicitly or through a topological sort check
        # This will raise CycleError if a cycle exists
        execution_order = workflow._get_execution_order()

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
    - ``fn_expr``: Python expression string evaluated to produce the task result
      (e.g. ``"len('hello')"``).  Full callables are supported via ``fn`` key
      that resolves to a dotted import path (``"module.function"``).
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
        import importlib

        from codomyrmex.orchestrator.swarm_topology import (
            SwarmTopology,
            TaskSpec,
            TopologyMode,
        )

        def _resolve_fn(task_dict: dict):
            """Resolve a callable from task dict."""
            if "fn" in task_dict:
                # dotted import path e.g. "os.path.exists"
                parts = task_dict["fn"].rsplit(".", 1)
                if len(parts) == 2:
                    mod = importlib.import_module(parts[0])
                    return getattr(mod, parts[1])
            if "fn_expr" in task_dict:
                expr = task_dict["fn_expr"]
                return lambda *_a, **_kw: eval(expr)
            # Default: identity (return args as-is)
            return lambda *a, **kw: {"args": a, "kwargs": kw}

        specs = [
            TaskSpec(
                task_id=t.get("id", f"task_{i}"),
                fn=_resolve_fn(t),
                args=t.get("args", []),
                kwargs=t.get("kwargs", {}),
                metadata=t.get("metadata", {}),
            )
            for i, t in enumerate(tasks)
        ]

        topo = SwarmTopology(max_workers=max_workers)
        result = topo.run(
            TopologyMode(topology),
            specs,
            broadcast_message=broadcast_message,
        )
        return {"status": "success", "topology": topology, **result}
    except (ValueError, RuntimeError, AttributeError, OSError, TypeError) as e:
        return {"status": "error", "message": f"DAG execution failed: {e}"}
