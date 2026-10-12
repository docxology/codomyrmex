# AI Code Editing - MCP Tool Specification

## Current Status: No MCP Tools Defined

The AI Code Editing module does not define `@mcp_tool` functions, so the PAI MCP bridge exposes no tools for it. Its LLM-backed code generation and refactoring helpers are available from the Python API:

| Function | Signature (abridged) | Returns |
| :--- | :--- | :--- |
| `generate_code_snippet` | `(prompt, language, provider=DEFAULT_LLM_PROVIDER, model_name=None, context=None, max_length=None, temperature=0.7, **kwargs)` | Dictionary with the generated code and metadata |
| `refactor_code_snippet` | `(code, refactoring_type, language, provider=DEFAULT_LLM_PROVIDER, model_name=None, context=None, preserve_functionality=True, **kwargs)` | Dictionary with the refactored code and metadata |

```python
from codomyrmex.agents.ai_code_editing import generate_code_snippet

result = generate_code_snippet("Write a recursive factorial function.", "python")
```

## General Considerations

- **LLM Dependency**: The helpers call external LLM providers (e.g., OpenAI, Anthropic). API keys and configurations for these services must be set up in the environment.
- **Determinism**: LLM outputs can be non-deterministic. Multiple calls with the same input may yield different results.

If MCP tools are added to this module, document them here with their real `@mcp_tool` names and parameters. See [API_SPECIFICATION.md](API_SPECIFICATION.md) for the full Python API.

---

## Navigation Links

- **Parent**: [Project Overview](../README.md)
- **Module Index**: [All Agents](../../AGENTS.md)
- **Documentation**: [Reference Guides](../../../../docs/README.md)
- **Home**: [Root README](../../../README.md)
