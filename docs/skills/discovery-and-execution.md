# Finding and Using Your Tools

A well-organized workshop means nothing if you cannot find the right tool
when you need it. Discovery is the process of scanning the workshop shelves,
cataloging what is available, and making every tool retrievable by name,
category, or tag. Execution is the workbench itself -- the controlled
environment where a tool is applied to material with proper safety measures.

## Discovery: Scanning the Shelves

### SkillDiscoverer

`SkillDiscoverer` walks Python modules looking for objects that qualify as
skills. It recognizes two patterns:

- **Class-based skills** -- Any class that is a subclass of `Skill` (but not
  `Skill` itself) is instantiated and registered.
- **Decorated functions** -- Any object that is an instance of `FunctionSkill`
  (created by the `@skill` decorator) is registered directly.

```python
from codomyrmex.skills.discovery import SkillDiscoverer, SkillRegistry

registry = SkillRegistry()
discoverer = SkillDiscoverer(registry)

import my_module
discovered = discoverer.discover_from_module(my_module)
```

The discoverer populates a `SkillRegistry`, which indexes skills by ID,
category, and tag for fast retrieval.

### The @skill Decorator and FunctionSkill

The `@skill` decorator converts an ordinary function into a `FunctionSkill`
with auto-inferred metadata. Type hints map to parameter schemas
(`int` becomes `"integer"`, `bool` becomes `"boolean"`, and so on), and the
first line of the docstring becomes the skill description.

```python
from codomyrmex.skills.discovery import skill, SkillCategory

@skill(
    name="analyze_imports",
    category=SkillCategory.CODE,
    tags=["static-analysis", "imports"],
)
def analyze_imports(file_path: str) -> dict:
    """Analyze Python import statements in a file."""
    ...
```

If no explicit metadata is provided, `FunctionSkill._infer_metadata` generates
an ID from the module path, extracts parameters from `inspect.signature`, and
maps type annotations to JSON schema types.

### SkillRegistry Indexing

The `SkillRegistry` in `discovery/__init__.py` maintains three indexes:

| Index | Key | Value |
|---|---|---|
| `_skills` | Skill ID (md5 hash) | `Skill` instance |
| `_by_category` | `SkillCategory` enum | List of skill IDs |
| `_by_tag` | Tag string | List of skill IDs |

Search supports filtering by query string, category, tags, and enabled state:

```python
results = registry.search(
    query="format",
    category=SkillCategory.CODE,
    tags=["formatting"],
    enabled_only=True,
)
```

The separate `SkillRegistry` in `skill_registry.py` provides YAML-level
indexing with `build_index()`, `search_by_pattern()`, and `search_skills()`
for text-based search across skill descriptions and pattern names.

## Execution: The Workbench

### SkillExecutor

`SkillExecutor` is the controlled surface where skills run. It provides three
execution modes:

**Direct execution** validates parameters and wraps the call in structured
logging:

```python
from codomyrmex.skills.execution import SkillExecutor

executor = SkillExecutor(max_workers=4)
result = executor.execute(my_skill, file_path="/src/main.py")
```

**Timeout execution** uses a thread pool to enforce a maximum duration:

```python
result = executor.execute_with_timeout(my_skill, timeout=30.0, file_path="/src/main.py")
```

**Chain execution** passes the output of each skill as `input` to the next:

```python
result = executor.execute_chain([parse_skill, transform_skill, write_skill], source="raw data")
```

### Error Handling

All execution failures raise `SkillExecutionError`, which wraps the original
exception with the skill name and timing information. The executor maintains
an execution log accessible via `get_execution_log()`:

```python
for entry in executor.get_execution_log():
    print(f"{entry['skill']}: {entry['status']} ({entry['elapsed']:.3f}s)")
```

### Key Source Paths

- `src/codomyrmex/skills/discovery/__init__.py` -- `Skill`, `FunctionSkill`,
  `SkillDiscoverer`, `SkillRegistry`, `@skill` decorator
- `src/codomyrmex/skills/execution/__init__.py` -- `SkillExecutor`,
  `SkillExecutionError`
- `src/codomyrmex/skills/skill_registry.py` -- YAML-level `SkillRegistry`

## Repository `SKILL.md` files and IDE discovery

The `SkillDiscoverer` flow above applies to **Python-registered** skills inside `codomyrmex.skills`. Separately, this repository ships a few **Markdown skill packs** (agentskills-style front matter) for PAI, Cursor, and Claude Code:

| Location | Role |
|----------|------|
| [`SKILL.md`](../../SKILL.md) (repo root) | Canonical Codomyrmex PAI / marketplace narrative; volatile counts point to [`docs/reference/inventory.md`](../reference/inventory.md). |
| [`src/codomyrmex/agents/pai/SKILL.md`](../../src/codomyrmex/agents/pai/SKILL.md) | Same contract as root; kept in-tree for PAI pack resolution next to the MCP bridge. |
| [`src/codomyrmex/orchestrator/fractals/SKILL.md`](../../src/codomyrmex/orchestrator/fractals/SKILL.md) | Fractal orchestration skill (MCP: `orchestrate_fractal_task`). |
| [`.agent/skills/`](../../.agent/skills/) | Canonical workflow skills (e.g. desloppify). |
| [`.cursor/skills/<name>/SKILL.md`](../../.cursor/skills/) | **Cursor** loads skills from here. Use a **stub**: YAML front matter plus links to canonical docs—examples: [desloppify](../../.cursor/skills/desloppify/SKILL.md), [codomyrmex](../../.cursor/skills/codomyrmex/SKILL.md), [fractals](../../.cursor/skills/fractals/SKILL.md). |

Optional **Claude Code** skills under `~/.claude/skills/` (e.g. GitNexus, qmd) are **not** in git; see [CLAUDE.md](../../CLAUDE.md) and [`.agent/SKILL_INDEX.md`](../../.agent/SKILL_INDEX.md) for plugin path maps.

After MCP changes, refresh metrics with `uv run python scripts/doc_inventory.py` (add `--manifest` for runtime `get_skill_manifest()` tool count).

## Cross-References

- For the full API specification, see the
  [Module Documentation](../modules/skills/README.md).
- For combining discovered skills into pipelines, continue to
  [Composition and Testing](./composition-and-testing.md).
- Return to the [Workshop Overview](./index.md) for the full reading guide.
