---
description: Audit Codomyrmex module health: RASP compliance, MCP tool correctness, PAI.md accuracy, test coverage. Use at sprint boundaries or before a release.
---

# Module Health Audit

## 1. RASP Compliance

Each module must have: README.md, AGENTS.md, SPEC.md, PAI.md

```bash
for f in README.md AGENTS.md SPEC.md PAI.md; do
  echo "=== Missing $f ==="
  find src/codomyrmex -maxdepth 2 -name "__init__.py" -not -path "*/tests/*" \
    | sed 's|/__init__.py||' | sort \
    | while read dir; do [ ! -f "$dir/$f" ] && echo "$dir"; done
done
```

## 2. MCP Tool Names (verify naming convention)

```bash
find src/codomyrmex -name "mcp_tools.py" | sort | while read f; do
  echo "=== $f ==="
  python3 -c "
import ast
tree = ast.parse(open('$f').read())
for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef):
        for d in node.decorator_list:
            if hasattr(d, 'func') and getattr(d.func, 'id', '') == 'mcp_tool':
                print(f'  {node.name}')
"
done
```

## 3. Phantom Tool Audit

```bash
find src/codomyrmex -name "PAI.md" | while read paifile; do
  module=$(dirname "$paifile" | sed 's|src/codomyrmex/||')
  mcp_file="$(dirname "$paifile")/mcp_tools.py"
  if grep -q "mcp_tool\|MCP Tool" "$paifile" 2>/dev/null; then
    if [ ! -f "$mcp_file" ]; then
      echo "PHANTOM: $module has MCP tools in PAI.md but no mcp_tools.py"
    fi
  fi
done
```

## 4. Coverage by Module

```bash
uv run pytest --cov=src/codomyrmex --cov-report=term-missing -q 2>&1 \
  | grep " 0%" | sort | head -30
```

## 5. Report Format

```
MODULE HEALTH AUDIT -- <date>
RASP: <N> complete, <M> missing files
MCP Tools: <N> modules with mcp_tools.py, <M> phantom refs
Coverage: <N> at 0%, <M> below 30%
Action Items: [prioritized list]
```
