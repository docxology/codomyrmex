# Model Evaluation -- MCP Tool Specification

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: February 2026

## No MCP Tools Defined

The `model_evaluation` module does not expose any MCP tools directly. It provides programmatic APIs for scoring, benchmarking, and quality analysis that are consumed by other modules and agent frameworks.

Evaluation functionality is accessed through Python imports:

```python
from codomyrmex.model_evaluation import (
    ExactMatchScorer, BenchmarkSuite, analyze_quality
)
```

Modules that wish to expose evaluation capabilities via MCP should wrap these APIs in tool handlers and register them through the `tool_use` module's `ToolRegistry`.

## Navigation

- **Parent**: [README.md](README.md)
- **API Spec**: [API_SPECIFICATION.md](API_SPECIFICATION.md)
- **PAI Integration**: [PAI.md](PAI.md)
