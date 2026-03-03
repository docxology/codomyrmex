# Model Ops

**Version**: v1.0.8 | **Status**: Active | **Last Updated**: March 2026

## Overview

Model Operations module for Codomyrmex.

## Architecture Overview

```
model_ops/
    __init__.py              # Public API exports
    mcp_tools.py             # MCP tool definitions
```

## Key Exports

- **`optimization`**
- **`registry`**
- **`cli_commands`**
- **`evaluation`**
- **`training`**
- **`Dataset`**
- **`DatasetSanitizer`**
- **`FineTuningJob`**
- **`Evaluator`**
- **`Scorer`**
- **`ExactMatchScorer`**
- **`ContainsScorer`**
- **`LengthScorer`**
- **`RegexScorer`**
- **`CompositeScorer`**

## MCP Tools Reference

| Tool | Trust Level |
|------|-------------|
| `model_ops_list_scorers` | Safe |

## Related Modules

See [All Modules](../README.md) for the complete module listing.

## Navigation

- **Source**: [src/codomyrmex/model_ops/](../../../../src/codomyrmex/model_ops/)
- **Parent**: [All Modules](../README.md)
