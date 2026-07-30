# Documentation module usage

Run examples from the repository root.

## Repository validation

```bash
make docs-check
make manuscript-check
```

These are the canonical contributor gates.

## Read-only Python analysis

```python
from pathlib import Path

from codomyrmex.documentation import (
    DocumentationConsistencyChecker,
    DocumentationQualityAnalyzer,
    generate_pai_md,
)

scores = DocumentationQualityAnalyzer().analyze_file(Path("README.md"))
consistency = DocumentationConsistencyChecker().check_directory("docs")
pai_preview = generate_pai_md(
    "documentation",
    Path("src/codomyrmex/documentation"),
)
```

## MCP dry run

```python
from codomyrmex.documentation.mcp_tools import generate_module_docs

receipt = generate_module_docs("documentation")
assert receipt["dry_run"] is True
assert receipt["executed"] is False
```

Set `dry_run=False` only with explicit authority to replace the target PAI
file.

## Optional package-local Docusaurus

The package retains a legacy Docusaurus lifecycle. Check its environment without
installing dependencies:

```bash
uv run --locked python \
  src/codomyrmex/documentation/documentation_website.py checkenv
```

`install`, `start`, `build`, `serve`, `assess`, `aggregate_docs`, and the
no-argument `full_cycle` have filesystem, process, browser, or network side
effects. They are not part of `make docs-check`.

## Navigation

- [Module overview](README.md)
- [API specification](API_SPECIFICATION.md)
- [MCP tools](MCP_TOOL_SPECIFICATION.md)
