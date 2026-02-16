---
description: Add a new entry to the Codomyrmex agentic long-term memory
---

# /codomyrmexMemory [content] [importance]

Persists information into the agent's long-term memory for future retrieval and context-awareness.

## Steps

// turbo

1. Save the memory:

```bash
cd /Users/mini/Documents/GitHub/codomyrmex && uv run python -c "
from codomyrmex.agentic_memory.core import add_memory
import sys
content = sys.argv[1] if len(sys.argv) > 1 else ''
importance = int(sys.argv[2]) if len(sys.argv) > 2 else 5
if not content:
    print('Error: Memory content is required.')
    sys.exit(1)
result = add_memory(content=content, importance=importance)
print(result)
" "{{content}}" "{{importance}}"
```

2. Confirmation:
   - The memory is indexed and added to the RAG-enabled vector store.
   - It will be automatically retrieved during future task planning.
