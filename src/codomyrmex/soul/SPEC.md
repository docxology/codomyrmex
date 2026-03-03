# Technical Specification - Soul Module

This module enables a discrete architecture for integrating reflective subjectivity into systems operating within the `codomyrmex` ecosystem.

## Architectural Design

The Soul module separates core cognitive orchestration from static execution components by providing an explicit locus for dynamic personality parameters.

### Data Models

- **`Soul` Class**: State-manager for self-reflection.
  - `config` (`Dict[str, Any]`): Initialization payload containing all necessary parameters.
  - `personality` (`str`): Single string describing the behavioral lens of the `Soul` instance. Defaults to `"default"`.

### Interfaces

#### API

1. `Soul.reflect(query: str) -> str`
   - Inputs the string `query`. Evaluates context.
   - Outputs a constructed string combining the query with the stored `personality` value.
   - Throws `ValueError` if the given `query` is empty.

2. `Soul.get_personality() -> str`
   - Inputs nothing.
   - Outputs a scalar string representing current `personality`.

#### Model Context Protocol (MCP)

To facilitate system-wide agent integration, the following tools exist in `mcp_tools.py`:
- `soul_reflect`: Accepts a personality trait and a query, instantiating the Soul locally, and generating its reflection via the `reflect` method.
- `soul_get_personality`: Accepts a personality configuration and returns the instantiated object's evaluation of its current personality via `get_personality()`.

## Integration Flow

1. An MCP tool receives a call with an explicit or default personality configuration.
2. The MCP tool resolves `create_soul(config)`.
3. The instance acts upon the user-supplied data (e.g., calling `reflect()`).
4. Resultant data passes upward back to the agentic environment via the standard Model Context Protocol.