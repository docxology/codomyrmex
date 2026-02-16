---
description: Perform deep analysis of a Codomyrmex project or specific file
---

# /codomyrmexAnalyze [path]

Runs a comprehensive analysis of the specified path using the Codomyrmex coding engine.

## Steps

// turbo

1. Run the analysis:

```bash
cd /Users/mini/Documents/GitHub/codomyrmex && uv run python -c "
from codomyrmex.coding.execution.executor import analyze_project
import json
import sys
path = sys.argv[1] if len(sys.argv) > 1 else '.'
result = analyze_project(path)
print(json.dumps(result, indent=2, default=str))
" "{{path}}"
```

1. Review the analysis results:
   - **Metrics**: Complexity, maintainability, and quality scores.
   - **Structure**: Class and function tree analysis.
   - **Recommendations**: Automated suggestions for improvements.
