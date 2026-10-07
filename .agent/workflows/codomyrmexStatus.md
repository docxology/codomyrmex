---
description: Get detailed system health and PAI awareness status
---

# /codomyrmexStatus

Provides a comprehensive overview of the Codomyrmex ecosystem and its integration with PAI.

## Steps

// turbo

1. Get status report:

```bash
cd "$(git rev-parse --show-toplevel)" && uv run python -c "
from codomyrmex.agents.pai.mcp_bridge import tool_pai_status, tool_pai_awareness
import json
status = tool_pai_status()
awareness = tool_pai_awareness()
report = {
    'system_status': status,
    'pai_awareness': awareness
}
print(json.dumps(report, indent=2, default=str))
"
```

// turbo

1. Get CLI diagnostics (PAI bridge, MCP tools, RASP docs, workflows, imports, Colony Kernel):

```bash
cd "$(git rev-parse --show-toplevel)" && uv run codomyrmex doctor --all
```

1. Sections:
   - **System Status**: MCP health, module counts, and bridge verification.
   - **PAI Awareness**: Active missions, projects, and TELOS alignment.
