# Specification — Ars Contexta

Formal specification for the Ars Contexta skills submodule.

## Module Identity

- **Package**: `codomyrmex.skills.arscontexta`
- **Version**: 1.0.0
- **Type**: Skills submodule
- **Category**: Reasoning / Knowledge Management

## Three-Space Architecture

| Space | Purpose | Path |
|-------|---------|------|
| `self/` | Personal identity, preferences, goals | `{vault}/self/` |
| `notes/` | Knowledge notes, references, insights | `{vault}/notes/` |
| `ops/` | Templates, automation configs, logs | `{vault}/ops/` |

## Kernel Primitives (15)

### Foundation Layer (5)
1. `atomic-note` — Single-concept note
2. `unique-id` — Stable unique identifier per note
3. `timestamping` — Creation and modification timestamps
4. `plain-text` — Plain text as canonical storage format
5. `link-syntax` — Bidirectional wikilink syntax

### Convention Layer (5)
6. `naming-convention` — Consistent file naming scheme
7. `front-matter` — YAML front-matter metadata block
8. `folder-structure` — Three-space directory layout
9. `tag-taxonomy` — Hierarchical tagging taxonomy
10. `template-set` — Reusable note templates

### Automation Layer (5)
11. `auto-backlink` — Automatic backlink generation
12. `auto-tag` — Automatic tag suggestion
13. `orphan-detection` — Detect unlinked orphan notes
14. `pipeline-hook` — 6R pipeline stage hooks
15. `health-check` — Vault health diagnostics

## 6R Processing Pipeline

```
Record → Reduce → Reflect → Reweave → Verify → Rethink
```

Each stage accepts `(content: str, context: dict) → str` handlers.

## Derivation Engine Dimensions (8)

1. **domain** — Subject area (software, research, design, business, science)
2. **methodology** — Note-taking method (zettelkasten, gtd, para, agile, kanban)
3. **abstraction_level** — Detail granularity (low, high)
4. **temporal_scope** — Time horizon (daily, weekly, project, long-term, archive)
5. **collaboration_mode** — Sharing model (solo, team, public, shared)
6. **output_format** — Delivery format (markdown, pdf, html, plain-text)
7. **toolchain** — Editor/tool (obsidian, vim, vscode, logseq, notion)
8. **learning_style** — Cognitive preference (visual, textual, kinesthetic, auditory)

## Methodology Graph

- **Capacity**: 249 research claims
- **Structure**: Adjacency-list with bidirectional edges
- **Attributes**: claim_id, statement, source, domain, connected_primitives, confidence

## Error Hierarchy

```
ArsContextaError (base)
├── VaultNotFoundError
├── PrimitiveValidationError
└── PipelineError
```

## Dependencies

- Python >= 3.10
- stdlib only (pathlib, dataclasses, enum, typing, json, time, re, hashlib, shutil, logging)
- Optional: pyyaml (already a core codomyrmex dependency)
