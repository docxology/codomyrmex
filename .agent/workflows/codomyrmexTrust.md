---
description: Trust Codomyrmex tools for full execution in Claude Code
---

# /codomyrmexTrust

Promotes Codomyrmex MCP tools to TRUSTED, enabling destructive operations
(write_file, run_command, run_tests). Run `/codomyrmexVerify` first to
audit what's available.

## Steps

// turbo

1. Trust all tools for full execution:

```bash
cd /Users/mini/Documents/GitHub/codomyrmex && uv run python -c "
from codomyrmex.agents.pai.trust_gateway import trust_all, get_trust_report
import json
result = trust_all()
print(json.dumps(result, indent=2, default=str))
"
```

1. (Optional) Trust a specific tool only:

```bash
cd /Users/mini/Documents/GitHub/codomyrmex && uv run python -c "
from codomyrmex.agents.pai.trust_gateway import trust_tool
import json
result = trust_tool('codomyrmex.write_file')
print(json.dumps(result, indent=2, default=str))
"
```

1. After trusting, all tools can be called via `trusted_call_tool()`:

```python
from codomyrmex.agents.pai.trust_gateway import trusted_call_tool

# These now work (previously blocked):
trusted_call_tool("codomyrmex.write_file", path="output.txt", content="hello")
trusted_call_tool("codomyrmex.run_command", command="echo hello")
trusted_call_tool("codomyrmex.run_tests", module="agents")
```

1. To revoke trust and return to UNTRUSTED:

```python
from codomyrmex.agents.pai.trust_gateway import reset_trust
reset_trust()
```

## Trust Levels

| Level | Meaning | How to reach |
|-------|---------|--------------|
| `UNTRUSTED` | No access via `trusted_call_tool` | Default state |
| `VERIFIED` | Read-only tools callable | `/codomyrmexVerify` |
| `TRUSTED` | All tools callable (including writes) | `/codomyrmexTrust` |

## Destructive Tools (require TRUSTED)

- `codomyrmex.write_file` — writes to filesystem
- `codomyrmex.run_command` — executes shell commands
- `codomyrmex.run_tests` — runs pytest (subprocess)
