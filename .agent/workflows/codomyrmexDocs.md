---
description: Retrieve README or SPEC documentation for any Codomyrmex module
---

# /codomyrmexDocs [module]

Retrieves the official documentation (README.md or SPEC.md) for a specific Codomyrmex module.

## Steps

// turbo

1. Fetch documentation:

```bash
cd /Users/mini/Documents/GitHub/codomyrmex && uv run python -c "
from codomyrmex.agents.pai.mcp_bridge import _tool_get_module_readme
import sys
import json
module = sys.argv[1] if len(sys.argv) > 1 else ''
if not module:
    print('Error: Module name is required.')
    sys.exit(1)
result = _tool_get_module_readme(module=module)
print(result.get('content', result.get('error', 'Unknown error')))
" "{{module}}"
```
