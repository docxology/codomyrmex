"""MCP tools for the agents module."""

from codomyrmex.model_context_protocol.decorators import mcp_tool


@mcp_tool(category="agents")
def execute_agent(agent_name: str, prompt: str) -> dict:
    """Execute an agent conversation with the given prompt.

    Args:
        agent_name: The name of the agent to execute (e.g. 'claude', 'gemini')
        prompt: The user input or instruction for the agent

    Returns:
        A dictionary containing the agent's response and execution metrics.
    """
    from codomyrmex.agents import AgentRequest
    from codomyrmex.agents.agent_setup import AgentRegistry

    # 1. Look up agent in registry
    registry = AgentRegistry()
    descriptor = registry.get_descriptor(agent_name)
    if descriptor is None:
        return {
            "status": "error",
            "error_code": "AGENT_NOT_FOUND",
            "message": f"Agent '{agent_name}' not found.",
        }

    # 2. Instantiate and execute
    try:
        agent = registry.create_agent(agent_name)
        request = AgentRequest(prompt=prompt)
        response = agent.execute(request)
        return {
            "status": "success" if response.is_success() else "error",
            "agent": descriptor.name,
            "content": response.content,
            "error": response.error,
            "metadata": response.metadata or {},
            "execution_time": response.execution_time,
            "tokens_used": response.tokens_used,
            "cost": response.cost,
            "request_id": response.request_id,
            "trace_id": response.trace_id,
        }
    except Exception as e:
        return {
            "status": "error",
            "error_code": "AGENT_EXECUTION_FAILED",
            "agent": descriptor.name,
            "message": f"Failed to execute agent {agent_name}: {e}",
            "error_type": type(e).__name__,
        }


@mcp_tool(category="agents")
def list_agents() -> dict:
    """Return a list of all available AI agents.

    Returns:
        A dictionary mapping agent IDs to their descriptions and capabilities.
    """
    from codomyrmex.agents.agent_setup import AgentRegistry

    registry = AgentRegistry()
    agents = registry.list_agents()
    return {
        "status": "success",
        "agents": [descriptor.to_dict() for descriptor in agents],
        "count": len(agents),
    }


@mcp_tool(category="agents")
def get_agent_memory(session_id: str) -> dict:
    """Retrieve the interaction logs and memory for a specific agent session.

    Args:
        session_id: The ID of the session

    Returns:
        A dictionary containing the agent's memory traces.
    """
    from codomyrmex.agents import SessionManager

    try:
        # Assuming SessionManager can list messages for a session ID
        manager = SessionManager()
        session = manager.get_session(session_id)
        if not session:
            return {"status": "error", "message": f"Session {session_id} not found."}

        logs = [
            {"role": m.role.value, "content": m.content} for m in session.messages[-50:]
        ]
        return {"status": "success", "logs": logs, "session_id": session_id}
    except (ValueError, RuntimeError, AttributeError, OSError, TypeError) as e:
        return {
            "status": "error",
            "message": f"Failed to retrieve memory for {session_id}: {e}",
        }
