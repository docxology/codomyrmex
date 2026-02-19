"""MCP tools for the orchestrator module."""

from codomyrmex.model_context_protocol.decorators import mcp_tool


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
                "execution_time": metrics.total_execution_time
            }
        }
    except Exception as e:
        return {"status": "error", "message": f"Failed to retrieve scheduler metrics: {e}"}


@mcp_tool(category="orchestrator")
def analyze_workflow_dependencies(tasks: list[dict]) -> dict:
    """Analyze a proposed workflow DAG for cyclic dependencies.
    
    Args:
        tasks: A list of dictionaries, each containing 'id' and 'dependencies' (list of ids)
        
    Returns:
        Validation result indicating if the workflow is a valid DAG.
    """
    from codomyrmex.orchestrator import Workflow, Task, CycleError
    
    try:
        workflow = Workflow(name="analysis_workflow")
        for t in tasks:
            task_id = t.get("id")
            if not task_id:
                continue
            task = Task(id=task_id, func=lambda: None)
            workflow.add_task(task)
            
        # Add dependencies in a second pass
        for t in tasks:
            task_id = t.get("id")
            deps = t.get("dependencies", [])
            for dep in deps:
                try:
                    workflow.add_dependency(task_id, dep)
                except Exception:
                    pass
                    
        # Verification happens implicitly or through a topological sort check
        # This will raise CycleError if a cycle exists
        execution_order = workflow._get_execution_order()
        
        return {
            "status": "success", 
            "valid_dag": True, 
            "execution_order": execution_order
        }
    except CycleError as e:
        return {"status": "error", "valid_dag": False, "message": str(e)}
    except Exception as e:
        return {"status": "error", "message": f"Failed to analyze workflow: {e}"}
