"""AgentMail integration for Codomyrmex.

This submodule provides the `AgentMailProvider` class, which implements the
`EmailProvider` interface using the AgentMail API (https://agentmail.to).

AgentMail is an API-first email platform purpose-built for AI agents, offering:
- Simple API key authentication (no OAuth flows)
- Inbox management and creation
- Thread-level message organization
- Draft scheduling and management
- Real-time webhooks and WebSocket events
- Pod-based inbox grouping for agent workflows
- Domain management and metrics

Usage::

    import os
    from codomyrmex.email.agentmail import AgentMailProvider

    provider = AgentMailProvider(
        api_key=os.environ["AGENTMAIL_API_KEY"],
        default_inbox_id="fristonblanket@agentmail.to",
    )
    messages = provider.list_messages(max_results=10)
"""

from .provider import AGENTMAIL_AVAILABLE, AgentMailProvider

__all__ = ["AgentMailProvider", "AGENTMAIL_AVAILABLE"]
