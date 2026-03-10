---
description: Get detailed system health and PAI awareness status
---

# /codomyrmexStatus

Provides a comprehensive overview of the Codomyrmex ecosystem and its integration with PAI.

## Steps

// turbo

1. Get status report:

```bash
cd /Users/mini/Documents/GitHub/codomyrmex && uv run python -c "
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

1. Get CLI diagnostic (Git Worktrees, Agentic Memory, System Telemetry):

```bash
cd /Users/mini/Documents/GitHub/codomyrmex && uv run tools/sys_health.py
```

1. Sections:
   - **System Status**: MCP health, module counts, and bridge verification.
   - **PAI Awareness**: Active missions, projects, and TELOS alignment.
