# PAI mapping — documentation module

| Phase | Capability | Boundary |
| :--- | :--- | :--- |
| OBSERVE | Read RASP presence, structure, consistency, and heuristic quality | Filesystem snapshot |
| BUILD | Generate PAI content and package-local site artifacts | Writes require explicit authority |
| VERIFY | Run package checks and the external strict documentation gate | Presence is not semantic proof |
| LEARN | Preserve reviewed receipts and changelog evidence | No independent runtime learning state |

## Example

```python
from pathlib import Path

from codomyrmex.documentation import generate_pai_md, audit_rasp

module_dir = Path("src/codomyrmex/documentation")
preview = generate_pai_md("documentation", module_dir)
exit_code = audit_rasp(module_dir)
```

The MCP generation tool defaults to dry-run. The authoritative repository
verification command is `make docs-check`.

## Navigation

- [Module overview](README.md)
- [Source PAI mapping](../../../src/codomyrmex/documentation/PAI.md)
- [Repository PAI bridge](../../../PAI.md)
