"""Claude API integration for Codomyrmex agents.

This module provides comprehensive Claude integration including:
- ClaudeClient: Full-featured API client with retry logic, tool use, and sessions
- ClaudeIntegrationAdapter: Bridges Claude with other Codomyrmex modules

Claude Code capabilities (v0.2.0):
- edit_file(): Apply AI-guided edits to files
- create_file(): Generate new files from descriptions
- review_code(): AI-powered code review
- scan_directory(): Project context scanning
- generate_diff(): Unified diff generation

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

    # Claude Code methods
    result = client.edit_file("/path/to/file.py", "Add type hints")
    review = client.review_code("def add(a, b): return a + b")
    structure = client.scan_directory("/path/to/project")
    ```

Version: v0.2.0
"""

from .claude_client import CLAUDE_PRICING, ClaudeClient
from .claude_integration import ClaudeIntegrationAdapter

__all__ = [
    "ClaudeClient",
    "ClaudeIntegrationAdapter",
    "CLAUDE_PRICING",
]

__version__ = "0.2.0"
