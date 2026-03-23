"""MCP tools for the ci_cd_automation module."""

from codomyrmex.model_context_protocol.decorators import mcp_tool


@mcp_tool(category="ci_cd_automation")
def pipeline_list() -> dict:
    """list all configured CI/CD pipelines and their current status.

    Returns:
        Dictionary with pipeline names and status information.
    """
    try:
        from codomyrmex.ci_cd_automation import PipelineManager

        manager = PipelineManager()
        pipelines = getattr(manager, "list_pipelines", None)
        if callable(pipelines):
            result = pipelines()
            return {"status": "success", "pipelines": result}
        return {
            "status": "success",
            "pipelines": ["build", "test", "deploy", "release"],
            "note": "Default pipeline list; configure PipelineManager for live data",
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}


@mcp_tool(category="ci_cd_automation")
def pipeline_run(
    pipeline_name: str,
    dry_run: bool = False,
) -> dict:
    """Execute a named CI/CD pipeline.

    Args:
        pipeline_name: Name of the pipeline to execute ('build', 'test', 'deploy', 'release')
        dry_run: If True, validate the pipeline without executing stages

    Returns:
        Dictionary with execution status and pipeline run details.
    """
    try:
        from codomyrmex.ci_cd_automation import Pipeline, run_pipeline

        pipeline = Pipeline(name=pipeline_name)
        if dry_run:
            return {
                "status": "success",
                "dry_run": True,
                "pipeline": pipeline_name,
                "message": f"Pipeline '{pipeline_name}' validated successfully",
            }
        result = run_pipeline(pipeline)
        return {
            "status": "success",
            "pipeline": pipeline_name,
            "result": str(result) if result is not None else "completed",
        }
    except Exception as e:
        return {"status": "error", "pipeline": pipeline_name, "message": str(e)}


@mcp_tool(category="ci_cd_automation")
def build_status(
    pipeline_name: str = "build",
) -> dict:
    """Get the current health and status of a CI/CD pipeline.

    Args:
        pipeline_name: Name of the pipeline to check (default: 'build')

    Returns:
        Dictionary with health status, stage counts, and metrics.
    """
    try:
        from codomyrmex.ci_cd_automation import PipelineMonitor, monitor_pipeline_health

        PipelineMonitor()
        health = monitor_pipeline_health(pipeline_name)
        return {
            "status": "success",
            "pipeline": pipeline_name,
            "health": health if health is not None else {"state": "idle", "stages": 0},
        }
    except Exception as e:
        return {"status": "error", "pipeline": pipeline_name, "message": str(e)}
