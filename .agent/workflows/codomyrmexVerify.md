---
description: Verify all Codomyrmex capabilities available to Claude Code via MCP
---

# /codomyrmexVerify

Audits all Codomyrmex modules, MCP tools, resources, prompts, server health,
and PAI bridge status. Read-only — no side effects. Safe tools are promoted
to VERIFIED trust level.

## Steps

// turbo

1. Run the verify capabilities audit:

```bash
cd /Users/mini/Documents/GitHub/codomyrmex && uv run python -c "
from codomyrmex.agents.pai.trust_gateway import verify_capabilities
import json
report = verify_capabilities()
print(json.dumps(report, indent=2, default=str))
"
```

1. Review the report output. Key sections:
   - **modules** — all available Codomyrmex modules (expect 100+)
   - **tools** — 50 MCP tools, split into safe and destructive categories
   - **resources** — 2 MCP resources
   - **prompts** — 3 MCP prompts
   - **mcp_server** — server creation health check
   - **pai_bridge** — PAI installation status
   - **skill_manifest** — PAI skill manifest validity
   - **trust** — which tools were promoted to VERIFIED

2. After verification, safe tools can be called via `trusted_call_tool()`:

```python
from codomyrmex.agents.pai.trust_gateway import trusted_call_tool
modules = trusted_call_tool("codomyrmex.list_modules")
info = trusted_call_tool("codomyrmex.module_info", module_name="llm")
```

> **Note**: Destructive tools (`write_file`, `run_command`, `run_tests`)
> remain UNTRUSTED. Use `/codomyrmexTrust` to enable them.
