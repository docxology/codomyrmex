<!-- readme: curated -->

# Documentation quality

This subpackage implements three distinct heuristics:

- `audit.py` checks package documentation presence, placeholder signals,
  `py.typed`, and module docstrings;
- `consistency_checker.py` reports line formatting, local-link, and required
  section findings;
- `quality_assessment.py` calculates heuristic 0–100 content scores.

These checks provide triage evidence. They do not prove that prose, commands,
citations, or scientific claims are correct.

## Examples

```python
from pathlib import Path

from codomyrmex.documentation import (
    DocumentationConsistencyChecker,
    DocumentationQualityAnalyzer,
    audit_rasp,
)

scores = DocumentationQualityAnalyzer().analyze_file(Path("README.md"))
consistency = DocumentationConsistencyChecker().check_directory("docs")
exit_code = audit_rasp(Path("src/codomyrmex/documentation"))
```

`audit_rasp()` prints a report and returns an exit code. Use
`scripts/documentation/audit_readme_agents.py` and `make docs-check` for the
authoritative repository release gate.

## Navigation

- [Agent instructions](AGENTS.md)
- [Functional specification](SPEC.md)
- [PAI integration](PAI.md)
- [Parent documentation package](../README.md)
- [Repository documentation guide](../../../../docs/development/documentation.md)
