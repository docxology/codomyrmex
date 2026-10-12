# AGENTS.md — `codomyrmex/tests/unit/manuscript`

## Purpose

Unit tests for the `manuscript` module: bibliography handling, figures,
integrity checks, PDF validation, and the variable contract.

## Layout

- `test_bibliography.py`, `test_figures.py`, `test_integrity.py`,
  `test_pdf_validation.py`, `test_variable_contract.py`

## Gotchas

- Zero-mock policy: real files and data only.
- Figure and margin tests run the real variable-generation CLI against copied
  Git-tracked current inputs with temporary output. Untracked configuration and
  Git submodules are excluded. The fixture exercises the documented
  standalone strict successor and records the unchanged template pin plus
  unknown Git identity; it does not inspect or modify a sibling template repo.
- Explicit template checkout failures are checked with real temporary Git repos.
  These local diagnostics do not establish pinned-template publication or
  scientific acceptance.
