# PAI Integration — Ars Contexta

Maps the PAI Algorithm phases to Ars Contexta capabilities.

## Phase Mapping

| PAI Phase | Ars Contexta Capability | How It Helps |
|-----------|------------------------|--------------|
| **OBSERVE** | `DerivationEngine.ingest_from_text()` | Extract knowledge management preferences from user request |
| **THINK** | `MethodologyGraph.get_related()` | Ground ISC in cognitive science research claims |
| **PLAN** | `KernelPrimitiveRegistry.to_kernel_config()` | Select primitives for vault configuration |
| **BUILD** | `ArsContextaManager.setup()` | Create vault with Three-Space directories |
| **EXECUTE** | `ProcessingPipeline.process()` | Run 6R pipeline on captured content |
| **VERIFY** | `VaultHealthChecker.check()` | Validate vault structure and note integrity |
| **LEARN** | `MethodologyGraph.add_claim()` | Record new research insights for future runs |

## MCP Tools Available

All 6 registered skills are accessible via MCP tool calling:

- `arscontexta_setup` — PLAN/BUILD phases
- `arscontexta_health` — VERIFY phase
- `arscontexta_process` — EXECUTE phase
- `arscontexta_derive` — OBSERVE phase
- `arscontexta_primitives` — PLAN phase
- `arscontexta_stats` — LEARN phase

## ISC Generation Support

The Derivation Engine's 8 configuration dimensions map naturally to ISC criteria
for knowledge management tasks:

- **Domain** dimension → ISC about content scope
- **Methodology** dimension → ISC about note-taking approach
- **Output Format** dimension → ISC about deliverable format
- **Toolchain** dimension → ISC about tool compatibility

## Effort Level Guidance

| Effort | Ars Contexta Usage |
|--------|-------------------|
| Fast | `arscontexta_primitives` for quick vault audit |
| Standard | `setup` + `health` for vault creation and validation |
| Extended+ | Full pipeline: derive → setup → process → health cycle |
