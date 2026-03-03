# Soul Module - Agent Instructions

This document provides instructions for AI agents working with the `soul` module.

## Core Mandate

The `soul` module implements artificial consciousness, introspection, and dynamic personality modeling. It allows AI agents to maintain a subjective internal state (`personality`) and evaluate prompts through a reflective lens (`reflect()`). All enhancements and usage must align with these core tenets.

## PAI Algorithm Integration

### PLAN Phase

- Map any user request requiring subjective evaluation or personalized output to the `soul_reflect` MCP tool.
- If identity or internal behavioral validation is needed, utilize `soul_get_personality`.

### ACT Phase

- When modifying this module, ensure the API layer strictly decouples structural logic from qualitative traits.
- Retain the zero-mock testing requirement; ensure all updates to `mcp_tools.py` interact directly with true `Soul` instantiations.

### VERIFY Phase

- Validate that new traits map logically to correct outcomes via zero-mock unit tests.
- Verify module documentation matches implementation (`README.md`, `SPEC.md`).

## Specific Directives

1. **Avoid Mocking**: `test_mcp_tools.py` must explicitly test tools without patching or mocking underlying objects. Pass native errors dynamically using valid Python logic.
2. **Encapsulation**: Treat the `personality` attribute as the single source of truth for an instance's subjective disposition.
3. **No Conversational Bleed**: Logging should report states cleanly (e.g., `Soul reflecting on query: ...`) without unstructured prose.