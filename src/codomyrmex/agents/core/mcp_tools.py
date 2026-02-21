"""MCP tools for ThinkingAgent reasoning capabilities.

Exposes Chain-of-Thought reasoning, trace retrieval, and depth
control as MCP-discoverable tools.
"""

from __future__ import annotations

from typing import Any

from codomyrmex.model_context_protocol.decorators import mcp_tool


# Module-level singleton — avoids re-creating on every call
_agent_instance: Any = None


def _get_agent() -> Any:
    """Lazily create a shared ThinkingAgent instance."""
    global _agent_instance
    if _agent_instance is None:
        from codomyrmex.agents.core.thinking_agent import ThinkingAgent
        _agent_instance = ThinkingAgent()
    return _agent_instance


@mcp_tool(category="agents.core")
def think(prompt: str, depth: str = "normal") -> dict:
    """Run Chain-of-Thought reasoning on a prompt.

    Decomposes the prompt into structured reasoning steps and
    synthesizes a conclusion with confidence scoring.

    Args:
        prompt: The question or problem to reason about.
        depth: Thinking depth — 'shallow', 'normal', or 'deep'.

    Returns:
        A dictionary with the reasoning trace summary, conclusion,
        confidence score, and step count.
    """
    from codomyrmex.llm.models.reasoning import ThinkingDepth

    agent = _get_agent()

    depth_map = {
        "shallow": ThinkingDepth.SHALLOW,
        "normal": ThinkingDepth.NORMAL,
        "deep": ThinkingDepth.DEEP,
    }
    td = depth_map.get(depth.lower(), ThinkingDepth.NORMAL)
    agent.thinking_depth = td

    from codomyrmex.agents.core.base import AgentRequest
    response = agent.execute(AgentRequest(prompt=prompt))

    trace = agent.last_trace
    return {
        "status": "success",
        "content": response.content,
        "confidence": trace.total_confidence if trace else 0.0,
        "steps": trace.step_count if trace else 0,
        "depth": td.value,
    }


@mcp_tool(category="agents.core")
def get_thinking_depth() -> dict:
    """Return the current thinking depth of the ThinkingAgent.

    Returns:
        A dictionary with the current depth value.
    """
    agent = _get_agent()
    return {
        "status": "success",
        "depth": agent.thinking_depth.value,
    }


@mcp_tool(category="agents.core")
def set_thinking_depth(depth: str) -> dict:
    """Set the ThinkingAgent's reasoning depth.

    Args:
        depth: One of 'shallow', 'normal', or 'deep'.

    Returns:
        A dictionary confirming the new depth.
    """
    from codomyrmex.llm.models.reasoning import ThinkingDepth

    depth_map = {
        "shallow": ThinkingDepth.SHALLOW,
        "normal": ThinkingDepth.NORMAL,
        "deep": ThinkingDepth.DEEP,
    }
    td = depth_map.get(depth.lower())
    if td is None:
        return {
            "status": "error",
            "message": f"Unknown depth '{depth}'. Use 'shallow', 'normal', or 'deep'.",
        }

    agent = _get_agent()
    agent.thinking_depth = td
    return {
        "status": "success",
        "depth": td.value,
    }


@mcp_tool(category="agents.core")
def get_last_trace() -> dict:
    """Retrieve the most recent reasoning trace.

    Returns:
        A dictionary with the trace summary or an error if no traces exist.
    """
    agent = _get_agent()
    trace = agent.last_trace
    if trace is None:
        return {"status": "error", "message": "No reasoning traces available."}

    return {
        "status": "success",
        "trace_id": trace.trace_id,
        "depth": trace.depth.value,
        "steps": trace.step_count,
        "confidence": trace.total_confidence,
        "is_complete": trace.is_complete,
        "conclusion": {
            "action": trace.conclusion.action if trace.conclusion else None,
            "justification": trace.conclusion.justification if trace.conclusion else None,
            "confidence": trace.conclusion.confidence if trace.conclusion else None,
        },
    }


__all__ = [
    "get_last_trace",
    "get_thinking_depth",
    "set_thinking_depth",
    "think",
]
