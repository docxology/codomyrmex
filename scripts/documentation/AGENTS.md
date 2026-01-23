# Codomyrmex Documentation Agents

**Scope**: `scripts/documentation/`

## Purpose

This directory houses the "librarian" agents of the repository. These scripts ensure that the codebase remains self-documenting and navigable.

## Operating Contracts

### 1. Maintenance

- Run `audit_documentation.py` periodically (or in CI/CD) to detect documentation drift.
- If new modules are added, run `fix_documentation.py` to bootstrap their documentation structure.

### 2. Tooling

- Do not manually edit hundreds of files. Improve `fix_documentation.py` to handle new requirements and apply them en-masse.
- Maintain `ScriptBase` inheritance for all tools here.

## Task Queue

- [ ] Add AI-driven content generation to `fix_documentation.py` (using LLM to read code and write summaries).
- [ ] Add link validation to `audit_documentation.py`.
