# Ars Contexta — Skills Submodule

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: February 2026

Personalized knowledge management architecture for Codomyrmex, based on
[Ars Contexta](https://github.com/agenticnotetaking/arscontexta).

## Architecture

- **Three-Space Architecture** — `self/`, `notes/`, `ops/` vault directories
- **15 Kernel Primitives** — Foundation, Convention, Automation layers
- **6R Processing Pipeline** — Record, Reduce, Reflect, Reweave, Verify, Rethink
- **Derivation Engine** — Maps user text to 8 configuration dimensions
- **Methodology Graph** — 249 research claims grounding decisions in cognitive science

## Quick Start

```python
from codomyrmex.skills.arscontexta import ArsContextaManager

mgr = ArsContextaManager()
config = mgr.setup("/path/to/vault")
report = mgr.health()
results = mgr.process_content("My note content")
signals = mgr.derive_config("I use obsidian for zettelkasten research notes")
primitives = mgr.get_primitives("foundation")
stats = mgr.get_methodology_stats()
```

## Exports

### Enums

| Enum | Values |
|------|--------|
| `VaultSpace` | self, notes, ops |
| `KernelLayer` | foundation, convention, automation |
| `PipelineStage` | record, reduce, reflect, reweave, verify, rethink |
| `ConfigDimension` | domain, methodology, abstraction_level, temporal_scope, collaboration_mode, output_format, toolchain, learning_style |
| `HealthStatus` | healthy, warning, error, unknown |
| `SkillType` | plugin, generated, hook |

### Dataclasses

`KernelPrimitive`, `ResearchClaim`, `DimensionSignal`, `StageResult`,
`VaultHealthReport`, `KernelConfig`, `VaultConfig`

### Services

| Class | Purpose |
|-------|---------|
| `KernelPrimitiveRegistry` | Holds 15 default kernel primitives |
| `ProcessingPipeline` | 6R pipeline with pluggable handlers |
| `DerivationEngine` | Text-to-dimension signal extraction |
| `MethodologyGraph` | Research claim adjacency graph |
| `VaultHealthChecker` | Vault directory diagnostics |

### Orchestrator

`ArsContextaManager` — main entry point composing all services.

## MCP Tools

Six skills are auto-registered into `discovery.DEFAULT_REGISTRY`:

| Tool | Description |
|------|-------------|
| `arscontexta_setup` | Initialise vault at path |
| `arscontexta_health` | Run vault diagnostics |
| `arscontexta_process` | Run 6R pipeline on content |
| `arscontexta_derive` | Extract config signals from text |
| `arscontexta_primitives` | List kernel primitives |
| `arscontexta_stats` | Get methodology graph statistics |

All registered as `SkillCategory.REASONING` with tags
`["arscontexta", "knowledge-management", "cognitive-architecture"]`.

## Dependencies

No additional dependencies — uses only stdlib and `pyyaml` (existing core dep).
