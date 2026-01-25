"""Claude API integration for Codomyrmex agents.

This module provides comprehensive Claude integration including:
- ClaudeClient: Full-featured API client with retry logic, tool use, and sessions
- ClaudeIntegrationAdapter: Bridges Claude with other Codomyrmex modules

Example:
    ```python
    from codomyrmex.agents.claude import ClaudeClient, ClaudeIntegrationAdapter

    # Basic usage
    client = ClaudeClient()
    response = client.execute(AgentRequest(prompt="Hello, Claude!"))

    # With session management
    session = client.create_session()
    response = client.execute_with_session(request, session=session)

    # With tool use
    client.register_tool(
        name="get_weather",
        description="Get weather for a location",
        input_schema={"type": "object", "properties": {"location": {"type": "string"}}},
        handler=get_weather_fn
    )
    response = client.execute_with_tools(request)
    ```
"""

from .claude_client import ClaudeClient, CLAUDE_PRICING
from .claude_integration import ClaudeIntegrationAdapter

__all__ = [
    "ClaudeClient",
    "ClaudeIntegrationAdapter",
    "CLAUDE_PRICING",
]


