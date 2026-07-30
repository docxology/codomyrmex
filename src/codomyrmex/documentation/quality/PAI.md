# PAI mapping — documentation quality

| Phase | Contribution | Boundary |
| :--- | :--- | :--- |
| OBSERVE | Read package files, headings, links, and structure | Filesystem snapshot only |
| VERIFY | Report RASP gaps, consistency issues, and heuristic scores | Not proof of semantic accuracy |
| LEARN | Persist caller-selected Markdown or external validation receipts | No internal durable learning state |

Use the package quality functions for focused diagnosis and `make docs-check`
for the composed repository gate.

## Navigation

- [Quality overview](README.md)
- [Functional specification](SPEC.md)
- [Parent PAI mapping](../PAI.md)
