"""MCP tool integrations for the fractals module."""

import tempfile
from pathlib import Path

from codomyrmex.logging_monitoring import get_logger
from codomyrmex.model_context_protocol.decorators import mcp_tool
from codomyrmex.orchestrator.fractals.executor import execute_leaf_task
from codomyrmex.orchestrator.fractals.models import TaskStatus
from codomyrmex.orchestrator.fractals.planner import build_tree, plan, propagate_status
from codomyrmex.orchestrator.fractals.workspace import WorkspaceManager

logger = get_logger(__name__)


@mcp_tool(category="orchestrator")
def orchestrate_fractal_task(task_description: str, max_depth: int = 3, provider: str = "claude") -> dict:
    """Recursively decompose and execute a complex task using the fractal orchestration pattern.

    This tool breaks down a high-level task into smaller atomic tasks, creates isolated git
    worktrees for each leaf task, and executes them concurrently using the specified agent provider.

    Args:
        task_description: The complex task to execute (e.g. "Build a web app with react and fastapi")
        max_depth: Maximum recursion depth for task decomposition.
        provider: The llm executor provider to use (default "claude").

    Returns:
        A dictionary containing the task execution summary and status.
    """
    logger.info(f"Starting fractal orchestration for: {task_description}")

    try:
        # 1. Initialization and Planning
        root_node = build_tree(task_description)
        logger.info("Decomposing tasks...")

        # Plan synchronously for simplicity in the MCP tool (LLM client blocks)
        planned_tree = plan(root_node, max_depth=max_depth)

        # 2. Workspace Setup
        target_dir = Path(tempfile.gettempdir()) / "fractals_workspace"
        workspace = WorkspaceManager(target_dir)
        workspace.init_workspace()

        # 3. Execution
        leaves = planned_tree.get_leaves()
        logger.info(f"Executing {len(leaves)} atomic tasks in {target_dir}")

        # In this synchronous wrapping, we execute sequentially. Over async boundaries, we could
        # gather them concurrently.
        execution_results = []
        for leaf in leaves:
            try:
                leaf.status = TaskStatus.RUNNING
                propagate_status(planned_tree)

                result = execute_leaf_task(leaf, workspace, provider=provider)

                leaf.status = TaskStatus.DONE
                propagate_status(planned_tree)

                execution_results.append({"task": leaf.description, "status": "success"})

            except Exception as e:
                leaf.status = TaskStatus.FAILED
                propagate_status(planned_tree)
                logger.error(f"Task failed: {leaf.description} - {e!s}")
                execution_results.append({"task": leaf.description, "status": "error", "message": str(e)})

        return {
            "status": "success",
            "task": task_description,
            "workspace_path": str(target_dir),
            "final_tree_status": planned_tree.status.value,
            "subtasks_executed": len(leaves),
            "results": execution_results
        }

    except Exception as e:
        logger.exception("Fractal orchestration failed")
        return {
            "status": "error",
            "message": f"Orchestration failed: {e!s}"
        }
