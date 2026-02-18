# Personal AI Infrastructure - OpenClaw Context

**Module**: openclaw
**Status**: Active

## Context

OpenClaw agent integration for autonomous AI assistance with multi-channel messaging (WhatsApp, Telegram, Slack, Discord, Signal, etc.), Gateway/WebSocket architecture, and LLM-agnostic support.

## AI Strategy

As an AI agent, when working with this module:

1. **Respect Interfaces**: Use the public API defined in `__init__.py`.
2. **Maintain State**: Ensure any stateful operations are documented in `SPEC.md`.
3. **Error Handling**: Wrap external calls in try/except blocks and log using `logging_monitoring`.

## Key Files

- `__init__.py`: Public API export.
- `openclaw_client.py`: CLI client with agent invocation, messaging, and gateway management.
- `openclaw_integration.py`: Integration adapter for code editing, LLM, and execution modules.
- `SPEC.md`: Technical specification.

## Future Considerations

- Modularization: Keep dependencies minimal.
- Telemetry: Ensure operations emit performance metrics.
- Skills: Integration with ClawHub skills ecosystem.
