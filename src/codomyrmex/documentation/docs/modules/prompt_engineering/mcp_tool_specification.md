# Prompt Engineering -- MCP Tool Specification

**Version**: v0.1.7 | **Status**: Active | **Last Updated**: February 2026

## No MCP Tools Defined

The `prompt_engineering` module does not expose any MCP tools directly. It provides programmatic APIs for template management, version tracking, optimization, and evaluation that are consumed by other modules and agent frameworks.

Functionality is accessed through Python imports:

```python
from codomyrmex.prompt_engineering import (
    PromptTemplate, TemplateRegistry, PromptOptimizer, PromptEvaluator
)
```

CLI commands are available for interactive use:

```bash
codomyrmex prompt_engineering templates
codomyrmex prompt_engineering strategies
codomyrmex prompt_engineering evaluate
```

Modules that wish to expose prompt engineering capabilities via MCP should wrap these APIs in tool handlers and register them through the `tool_use` module's `ToolRegistry`.

## Navigation

- **Parent**: [README.md](README.md)
- **API Spec**: [API_SPECIFICATION.md](API_SPECIFICATION.md)
- **PAI Integration**: [PAI.md](PAI.md)
