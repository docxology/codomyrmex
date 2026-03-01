# Personal AI Infrastructure — Documentation Module

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

The Documentation module handles the **semantics** of technical documentation — quality auditing, RASP compliance, auto-generation of PAI.md files, and root-level doc synchronization. Distinct from the `documents` module which handles document I/O mechanics.

## PAI Capabilities

### Documentation Quality Audit

```python
from codomyrmex.documentation import audit_documentation, audit_rasp, ModuleAudit

# Audit documentation quality across modules
results = audit_documentation(path="src/codomyrmex")

# Check RASP compliance (README, AGENTS, SPEC, PAI)
rasp_results = audit_rasp(module_path="src/codomyrmex/agents")

# Full module audit
audit = ModuleAudit(module_path="src/codomyrmex/llm")
report = audit.run()
```

### PAI Doc Generation

```python
from codomyrmex.documentation import update_pai_docs, generate_pai_md

# Auto-generate PAI.md from module exports and metadata
pai_content = generate_pai_md(module_path="src/codomyrmex/crypto")

# Update all PAI docs across the project
update_pai_docs()
```

### Root Doc Maintenance

```python
from codomyrmex.documentation import update_root_docs, finalize_docs, update_spec

# Synchronize root README, SPEC with module inventory
update_root_docs()
finalize_docs()
update_spec()
```

## Key Exports

| Export | Type | Purpose |
|--------|------|---------|
| `audit_documentation` | Function | Project-wide documentation quality audit |
| `audit_rasp` | Function | RASP compliance check for a module |
| `ModuleAudit` | Class | Comprehensive single-module doc audit |
| `update_pai_docs` | Function | Auto-update all PAI.md files |
| `generate_pai_md` | Function | Generate PAI.md content for a module |
| `update_root_docs` | Function | Sync root-level documentation |
| `finalize_docs` | Function | Final documentation pass |
| `update_spec` | Function | Update SPEC.md |
| `quality` | Module | Documentation quality metrics |

## PAI Algorithm Phase Mapping

| Phase | Documentation Contribution |
|-------|----------------------------|
| **OBSERVE** | Audit RASP compliance and documentation coverage |
| **BUILD** | Generate and update PAI.md, README.md, SPEC.md files |
| **VERIFY** | Validate documentation quality, check for stale references |
| **LEARN** | Record documentation improvements and audit history |

## MCP Tools

Two tools are auto-discovered via `@mcp_tool` and available through the PAI MCP bridge:

| Tool | Description | Trust Level | Category |
|------|-------------|-------------|----------|
| `generate_module_docs` | Generate documentation for a codomyrmex module (README, SPEC, AGENTS) | Safe | documentation |
| `audit_rasp_compliance` | Audit modules for RASP documentation compliance (README/AGENTS/SPEC/PAI.md) | Safe | documentation |

## Architecture Role

**Service Layer** — Consumes `static_analysis/` (import scanning), `system_discovery/` (module listing), `documents/` (file I/O). Consumed by `maintenance/` for automated doc updates.

## Navigation

- **Self**: [PAI.md](PAI.md)
- **Parent**: [../PAI.md](../PAI.md) — Source-level PAI module map
- **Root Bridge**: [../../../PAI.md](../../../PAI.md) — Authoritative PAI system bridge doc
- **Siblings**: [README.md](README.md) | [AGENTS.md](AGENTS.md) | [SPEC.md](SPEC.md) | [API_SPECIFICATION.md](API_SPECIFICATION.md)
