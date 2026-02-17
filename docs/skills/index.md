# The Craftsperson's Workshop

The codomyrmex skills module is organized like a craftsperson's workshop.
Every tool has a place, every place has a purpose, and the arrangement itself
teaches you how work flows from raw material to finished product.

## The Workshop Metaphor

| Workshop Concept | Skills Module Equivalent | Purpose |
|---|---|---|
| **Tools** | `Skill`, `FunctionSkill` | Individual capabilities that do one thing well |
| **Tool Catalog** | `SkillDiscoverer`, `SkillRegistry` | Finding what is available and where it lives |
| **Workbench** | `SkillExecutor` | The surface where tools are applied to material |
| **Jigs and Fixtures** | `SkillComposer`, `ComposedSkill` | Pre-built assemblies that hold tools in sequence |
| **Tool Supplier Showroom** | `SkillMarketplace` | Remote sources for acquiring new tools |
| **Lockout Cabinet** | `SkillPermissionManager` | Controlled access for dangerous operations |

## Skill Lifecycle Philosophy

A skill moves through five stages, each mapped to a dedicated subsystem:

1. **Discover** -- Scan modules, decorators, and YAML files to locate available skills.
2. **Validate** -- Confirm metadata, parameters, and structural integrity before use.
3. **Execute** -- Run the skill with timeouts, error handling, and structured logging.
4. **Compose** -- Combine skills into chains, parallel groups, or conditional branches.
5. **Test** -- Verify behavior with test cases, metadata validation, and benchmarks.

Surrounding this lifecycle are two governance systems: the **marketplace** manages
where skills come from, and **permissions** controls what they are allowed to do.

## Reading Guide

This documentation is split into four focused guides. Read them in order for a
complete understanding, or jump to the section relevant to your task.

| Document | Covers |
|---|---|
| [Skill Lifecycle](./skill-lifecycle.md) | Loading, validation, caching, upstream sync |
| [Discovery and Execution](./discovery-and-execution.md) | Finding skills and running them safely |
| [Composition and Testing](./composition-and-testing.md) | Building pipelines and quality control |
| [Marketplace and Governance](./marketplace-and-governance.md) | Remote sources, versions, and permissions |

## Key Entry Points

The top-level module aggregates all subsystems through a single import:

```python
from codomyrmex.skills import (
    SkillsManager,       # High-level orchestration
    SkillLoader,         # YAML loading with merge logic
    SkillSync,           # Upstream repository synchronization
    SkillRegistry,       # Indexing and search
    discovery,           # Skill discovery and the @skill decorator
    execution,           # Runtime execution with timeouts
    composition,         # Chain, parallel, conditional patterns
    testing,             # Test runner and benchmarks
    marketplace,         # Remote skill sources
    permissions,         # Access control
    versioning,          # Semver compatibility checks
)
```

## Cross-References

For the full module specification, source structure, and API details, see the
[Module Documentation](../modules/skills/README.md).

The skills module sits in the **Service Layer** of the codomyrmex architecture.
It depends on `logging_monitoring` from the Foundation Layer and `git_operations`
from the Core Layer (for upstream sync). No circular dependencies exist; all
dependency arrows point downward.
