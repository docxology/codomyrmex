# From Raw Material to Finished Tool

Every tool in the workshop starts as raw material -- a YAML file in a
repository or a decorated Python function in a module. This document traces
the lifecycle of a skill from its origin on disk through validation, caching,
and upstream synchronization.

## Two Kinds of Raw Material

### YAML-Based Skills

The primary skill format is a YAML file that declares patterns, anti-patterns,
validations, and sharp edges. These files live in category directories and
follow a standard layout:

```
upstream/
  category_name/
    skill_name/
      skill.yaml        # Skill definition
    another_skill.yaml   # Also valid (flat file)
```

The `SkillLoader` reads these files and produces Python dictionaries suitable
for indexing and search.

### Programmatic (Python) Skills

Python skills extend the `Skill` abstract class or use the `@skill` decorator
to wrap ordinary functions. The `FunctionSkill` class infers metadata from
type hints and docstrings, meaning a well-documented function becomes a
workshop tool with zero additional configuration.

```python
from codomyrmex.skills.discovery import skill, SkillCategory

@skill(category=SkillCategory.CODE, tags=["formatting"])
def format_code(source: str, language: str = "python") -> str:
    """Format source code using standard rules."""
    ...
```

## Loading: Clone, Overlay, Merge, Cache

The loading pipeline in `SkillLoader` follows four steps:

1. **Clone** -- `SkillSync.clone_upstream()` pulls the upstream repository
   into a local directory. This is the workshop's supply shipment.
2. **Overlay** -- Custom skill files in a separate directory can override or
   extend upstream skills. If a custom file exists for the same
   `category/name`, it takes precedence.
3. **Merge** -- `SkillLoader.get_merged_skill()` combines upstream and custom
   data. The merged result carries `_source` metadata indicating its origin.
4. **Cache** -- Merged results are stored in an in-memory dictionary keyed by
   `category/name`. An optional on-disk YAML cache avoids repeated parsing.

```python
loader = SkillLoader(
    upstream_dir=Path("skills/upstream"),
    custom_dir=Path("skills/custom"),
    cache_dir=Path("skills/.cache"),
)
merged = loader.get_merged_skill("code", "format_code")
```

## Validation Pipeline

Before a skill enters the workshop registry, `SkillValidator` inspects it:

- The data must be a non-empty dictionary.
- If `patterns` is present, it must be a list of dictionaries.
- If `anti_patterns` is present, it must be a list of dictionaries.
- If `validations` or `sharp_edges` are present, they must be lists.

Validation produces a tuple of `(is_valid, errors)`. Skills that fail
validation are logged but not loaded into the index.

## Caching Strategy

The skills module uses a two-tier cache:

| Tier | Storage | Lifetime | Purpose |
|---|---|---|---|
| **In-memory** | `SkillLoader._cache` dict | Process lifetime | Fast repeated lookups |
| **On-disk** | `cache_dir/*.yaml` files | Until `clear_cache()` | Survive restarts |

Call `loader.clear_cache()` or `registry.refresh_index()` to invalidate both
tiers and force a fresh load from source files.

## Upstream Sync Workflow

`SkillSync` manages the relationship between the local workshop and the
upstream tool supplier:

1. **Initial clone** -- `clone_upstream()` performs a `git clone` with the
   configured branch.
2. **Incremental update** -- `pull_upstream()` runs `git pull` to fetch the
   latest changes.
3. **Status check** -- `check_upstream_status()` reports the current branch,
   commit hash, and whether local modifications exist.

```python
sync = SkillSync(
    upstream_dir=Path("skills/upstream"),
    upstream_repo="https://github.com/vibeforge1111/vibeship-spawner-skills",
    upstream_branch="main",
)
sync.pull_upstream()
status = sync.check_upstream_status()
```

## Cross-References

- For the complete source structure and API surface, see the
  [Module Documentation](../modules/skills/README.md).
- For how skills are discovered and executed after loading, continue to
  [Discovery and Execution](./discovery-and-execution.md).
- Return to the [Workshop Overview](./index.md) for the full reading guide.
