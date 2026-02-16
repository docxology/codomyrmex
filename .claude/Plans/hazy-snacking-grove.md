# Plan: Move `cursorrules/` into `agentic_memory/rules/` Submodule

## Context

The top-level `cursorrules/` directory (91 files, 75 `.cursorrules` rule files) contains hierarchical coding standards for AI-assisted development. These rules are a form of agentic knowledge — they guide agent behavior during code generation. Currently they sit as a standalone directory with no Python API. Moving them into `src/codomyrmex/agentic_memory/rules/` as a proper submodule makes them programmatically accessible, keeps agent-knowledge collocated, and follows codomyrmex module patterns.

## Approach

### Step 1: Create `rules/` submodule structure

Create `src/codomyrmex/agentic_memory/rules/` with:

```
rules/
├── __init__.py          # Public API exports
├── models.py            # RuleCategory enum, Rule dataclass, RuleSet dataclass
├── loader.py            # Load .cursorrules files from package data dirs
├── resolver.py          # Hierarchical precedence resolution
├── py.typed             # PEP 561 marker
├── README.md            # RASP doc
├── AGENTS.md            # RASP doc
├── SPEC.md              # RASP doc
├── PAI.md               # RASP doc
├── general.cursorrules  # Moved from cursorrules/
├── cross_module/        # Renamed from cross-module/ (Python-safe)
│   └── (8 .cursorrules files)
├── file_specific/       # Renamed from file-specific/ (Python-safe)
│   └── (6 .cursorrules files)
└── modules/
    └── (60 .cursorrules files)
```

Key: Subdirectory names use underscores (not hyphens) for Python compatibility. Only `.cursorrules` data files are moved — old RASP docs from `cursorrules/` subdirs are replaced by new ones at the `rules/` level.

### Step 2: Create Python API (3 files)

**`rules/models.py`** — Data models:
- `RuleCategory` enum: `GENERAL`, `CROSS_MODULE`, `MODULE`, `FILE_SPECIFIC`
- `CATEGORY_PRECEDENCE` dict mapping category to numeric precedence
- `Rule` frozen dataclass: `name`, `category`, `content`, `source_path`, `precedence` property, `sections` property
- `RuleSet` dataclass: `rules` list, `effective_rule` property (highest precedence), `all_content()` method

**`rules/loader.py`** — File-system loading:
- `load_general()` -> `Rule | None`
- `load_cross_module()` -> `list[Rule]`
- `load_modules()` -> `list[Rule]`
- `load_file_specific()` -> `list[Rule]`
- `load_all()` -> `list[Rule]` (all 75)

**`rules/resolver.py`** — Precedence resolution:
- `RuleResolver` class with methods:
  - `for_module(name)` -> `RuleSet` (general + cross-module match + module match)
  - `for_file_type(name)` -> `RuleSet` (general + file-specific match)
  - `for_context(module=, file_type=)` -> `RuleSet` (combined)
  - `list_modules()`, `list_file_types()`, `list_cross_module()`
  - `all_rules()`, `by_category()`

### Step 3: Move the 75 `.cursorrules` files

- `cursorrules/general.cursorrules` -> `rules/general.cursorrules` (update line 49 self-reference)
- `cursorrules/cross-module/*.cursorrules` (8 files) -> `rules/cross_module/`
- `cursorrules/file-specific/*.cursorrules` (6 files) -> `rules/file_specific/`
- `cursorrules/modules/*.cursorrules` (60 files) -> `rules/modules/`

### Step 4: Update `agentic_memory/__init__.py`

- Add import: `from .rules import RuleResolver, Rule, RuleCategory, RuleSet`
- Add `_rules` CLI command to `cli_commands()` dict
- Add rules types to `__all__`

### Step 5: Update documentation (existing agentic_memory docs)

- `agentic_memory/README.md` — Add "Rules Submodule" section
- `agentic_memory/SPEC.md` — Add rules to architecture components
- `agentic_memory/PAI.md` — Add rules exports to Key Exports table
- `agentic_memory/API_SPECIFICATION.md` — Add RuleResolver API

### Step 6: Create new RASP docs for `rules/`

- `rules/README.md` — Adapted from `cursorrules/README.md`
- `rules/AGENTS.md` — Adapted from `cursorrules/AGENTS.md`
- `rules/SPEC.md` — Adapted from `cursorrules/SPEC.md`
- `rules/PAI.md` — Adapted from `cursorrules/PAI.md`

### Step 7: Update ~13 external references

| File | Change |
|------|--------|
| `/README.md` | Update directory tree + links |
| `/AGENTS.md` | Update ~8 path references |
| `/CLAUDE.md` line 49 | `cursorrules/` -> `src/codomyrmex/agentic_memory/rules/` |
| `.github/CODEOWNERS` | Update ownership path |
| `src/codomyrmex/documentation/scripts/fix_parent_references.py` | Update hardcoded `'cursorrules'` |
| `src/codomyrmex/documentation/scripts/global_doc_auditor.py` | Update targets list |
| `src/codomyrmex/documentation/scripts/bootstrap_agents_readmes.py` | Update skip list |
| `src/codomyrmex/documentation/scripts/fix_remaining_links.py` | Update regex |
| `src/codomyrmex/documentation/scripts/fix_scripts_subdirs.py` | Update regex |
| `src/codomyrmex/logistics/orchestration/project/documentation_generator.py` | Update string ref |
| `src/codomyrmex/agents/droid/run_todo_droid.py` | Update string ref |
| `src/codomyrmex/logistics/orchestration/project/templates/doc_templates/README.template.md` | Update template ref |

**NOT changed** (correctly reference `.cursorrules` as an IDE config concept, not our directory): `src/codomyrmex/ide/cursor/`, `src/codomyrmex/website/.cursor/.cursorrules`

### Step 8: Create tests

Create `src/codomyrmex/tests/unit/agentic_memory/test_rules.py` with Zero-Mock tests:
- `TestRuleCategory` — precedence ordering
- `TestLoader` — load counts (1 general, 8 cross-module, 60 modules, 6 file-specific, 75 total)
- `TestRule` — precedence property, sections parsing, source_path existence
- `TestRuleSet` — effective_rule, empty set, all_content ordering
- `TestRuleResolver` — all methods, nonexistent module fallback

### Step 9: Delete top-level `cursorrules/`

Remove the entire directory after migration is verified.

## Critical Files

- `src/codomyrmex/agentic_memory/__init__.py` — Must update imports + exports + CLI
- `src/codomyrmex/agentic_memory/models.py` — Pattern reference for dataclass style
- `cursorrules/general.cursorrules` — Content update before move (line 49)
- `CLAUDE.md` — Update `.cursorrules` reference (line 49)
- `AGENTS.md` — Dense reference updates (8 occurrences)

## Verification

```bash
# 1. File count check
find src/codomyrmex/agentic_memory/rules -name "*.cursorrules" | wc -l
# Expected: 75

# 2. Old directory gone
test -d cursorrules && echo "FAIL" || echo "PASS"

# 3. Python imports work
uv run python -c "from codomyrmex.agentic_memory.rules import RuleResolver; r = RuleResolver(); print(f'Loaded {len(r.all_rules())} rules')"
# Expected: Loaded 75 rules

# 4. Resolver works
uv run python -c "
from codomyrmex.agentic_memory.rules import RuleResolver
r = RuleResolver()
print('Modules:', len(r.list_modules()))      # 60
print('File types:', len(r.list_file_types())) # 6
rs = r.for_module('agents')
print('Agents effective:', rs.effective_rule.name)  # agents
"

# 5. Parent import still works
uv run python -c "from codomyrmex.agentic_memory import AgentMemory, RuleResolver; print('OK')"

# 6. Existing tests pass
uv run pytest src/codomyrmex/tests/unit/agentic_memory/ -v

# 7. New tests pass
uv run pytest src/codomyrmex/tests/unit/agentic_memory/test_rules.py -v

# 8. No stale references (excluding IDE .cursorrules refs)
grep -r "cursorrules/" README.md AGENTS.md CLAUDE.md .github/CODEOWNERS | grep -v "agentic_memory/rules"
# Expected: no output

# 9. RASP compliance
for f in README.md AGENTS.md SPEC.md PAI.md; do
  test -f "src/codomyrmex/agentic_memory/rules/$f" && echo "OK: $f" || echo "MISSING: $f"
done
```
