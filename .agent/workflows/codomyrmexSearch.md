---
description: Search for patterns in the codebase using regex
---

# /codomyrmexSearch [pattern] [path]

Performs a high-performance search across the codebase using Codomyrmex's search engine.

## Steps

// turbo

1. Execute the search:

```bash
cd /Users/mini/Documents/GitHub/codomyrmex && uv run python -c "
from codomyrmex.model_context_protocol.tools import search_codebase
import sys
import json
pattern = sys.argv[1] if len(sys.argv) > 1 else ''
path = sys.argv[2] if len(sys.argv) > 2 else '.'
if not pattern:
    print('Error: Search pattern is required.')
    sys.exit(1)
result = search_codebase(pattern=pattern, path=path)
print(json.dumps(result, indent=2, default=str))
" "{{pattern}}" "{{path}}"
```

1. Integration:
   - Supports robust regex patterns.
   - Filters out binary files and git-ignored directories automatically.
