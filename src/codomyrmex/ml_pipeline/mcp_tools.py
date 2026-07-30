from typing import Any

from codomyrmex.model_context_protocol.decorators import mcp_tool


@mcp_tool()
def ml_pipeline_create(name: str, steps: list[dict[str, Any]]) -> dict[str, Any]:
    """
    Return a stateless receipt for a proposed pipeline definition.

    Args:
        name: The name of the pipeline.
        steps: A list of step definitions, where each step is a dictionary containing step configurations.

    Returns:
        An echo receipt containing ``name`` and ``steps``. No validation or
        persistence is performed.
    """
    return {"status": "success", "pipeline": {"name": name, "steps": steps}}


@mcp_tool()
def ml_pipeline_execute(name: str, inputs: dict[str, Any]) -> dict[str, Any]:
    """
    Return an execution-shaped echo receipt without running a workload.

    Args:
        name: The caller-reported pipeline name.
        inputs: The input mapping to echo in the receipt.

    Returns:
        A receipt containing ``name`` and the unchanged ``inputs`` as
        ``outputs``. No lookup, validation, or ML execution is performed.
    """
    return {"status": "success", "result": {"pipeline": name, "outputs": inputs}}
