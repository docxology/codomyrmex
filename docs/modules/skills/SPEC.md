# skills Functional Specification

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: February 2026

## Core Concept

The skills module implements a dual-layer skill management system: **upstream synchronization** (cloning a curated skills repository via git) combined with **custom overrides** (user-defined skills that take precedence). On top of this YAML-based system, a **programmatic discovery framework** allows defining skills as Python classes and functions with rich metadata, parameter validation, and runtime registration.

## Architecture

```mermaid
graph TD
    subgraph "Skills Module"
        SM[SkillsManager]
        SL[SkillLoader]
        SS[SkillSync]
        SR[SkillRegistry]
        SV[SkillValidator]
    end

    subgraph "Discovery Framework"
        ABC[Skill ABC]
        FS[FunctionSkill]
        DR[SkillRegistry - Discovery]
        SD[SkillDiscoverer]
        DEC[@skill decorator]
    end

    subgraph "Submodules"
        EX[execution/]
        CO[composition/]
        TF[testing/]
        MP[marketplace/]
        VR[versioning/]
        PM[permissions/]
    end

    subgraph "External"
        VSR[vibeship-spawner-skills]
    end

    subgraph "Storage"
        US[upstream/]
        CS[custom/]
        MC[.cache/]
    end

    subgraph "Integration"
        GO[git_operations]
        LM[logging_monitoring]
        MCP[model_context_protocol]
    end

    VSR -->|Clone/Pull| SS
    SS --> US
    SM --> SL
    SL --> US
    SL --> CS
    SL --> MC
    SM --> SR
    SM --> SV
    SS --> GO
    SM --> LM
    SM --> MCP

    DEC --> FS
    FS --> ABC
    SD --> DR
    EX --> ABC
    CO --> ABC
    TF --> ABC
```

## Functional Requirements

### 1. Initialization
- Setup `skills/upstream/`, `skills/custom/`, and `skills/.cache/` directory structure
- Clone upstream repository if `upstream/` does not exist
- Build the skill index from all YAML files
- Support auto-sync on initialization via `auto_sync` flag

### 2. Upstream Sync
- Clone the vibeship-spawner-skills repository via git
- Pull latest changes from upstream
- Check upstream status (branch, changes, last commit)
- Get upstream version/commit hash
- Support force re-clone

### 3. Skill Loading
- Load skills from YAML files (`skill.yaml` in directories or flat `.yaml` files)
- Merge custom skills with upstream (custom overrides completely)
- Cache merged results in memory and optionally to `.cache/` directory
- Support both directory-based (`category/name/skill.yaml`) and file-based (`category/name.yaml`) structures

### 4. Skill Discovery and Search
- Index all skills by category and name
- Extract metadata (patterns, anti_patterns, validations, sharp_edges) for search
- Full-text search across descriptions, pattern names, and anti-pattern descriptions
- Regex-based pattern matching with case-sensitivity control
- Get skill metadata without loading full skill data

### 5. Custom Skills
- Add custom skills via API (writes YAML to `custom/` directory)
- Custom skills with same category/name automatically override upstream
- Refresh index after adding custom skills
- Clear cache to force reloads

### 6. Validation
- Validate skill data dictionaries against expected schema
- Validate individual YAML files
- Validate entire directories recursively
- Check patterns, anti_patterns, validations, and sharp_edges types

### 7. Programmatic Discovery Framework
- `Skill` ABC with `execute()` and `validate_params()` methods
- `FunctionSkill` wraps regular functions with auto-inferred metadata
- `SkillMetadata` dataclass with JSON schema generation for LLM tool calling
- `SkillCategory` enum (CODE, DATA, WEB, FILE, SYSTEM, COMMUNICATION, REASONING, UTILITY)
- `@skill` decorator for declarative skill definition with auto-registration
- `SkillDiscoverer` for discovering skills from Python modules
- Global default registry with `register_skill()` and `get_skill()` helpers

### 8. Execution
- Execute skills with error handling and logging
- Timeout-wrapped execution via thread pool
- Sequential chaining (output of one skill becomes input of next)
- Execution logging with timing

### 9. Composition
- Chain skills sequentially
- Execute skills in parallel with concurrent futures
- Conditional branching based on runtime conditions

### 10. Testing
- Run test cases with expected value assertions
- Validate skill metadata completeness
- Benchmark skill performance with timing statistics

## Modularity & Interfaces

### Inputs
- Upstream repository URL and branch
- YAML skill files (category/name structure)
- Skill data dictionaries (for custom skills)
- Python functions/classes (for programmatic skills)
- Search queries, category filters, regex patterns

### Outputs
- Skill data dictionaries (merged from upstream + custom)
- Search results with metadata
- Validation results (is_valid, errors)
- Execution results with timing
- Test results and benchmark statistics

### Dependencies
- `git_operations` -- Repository cloning and pulling
- `logging_monitoring` -- Structured logging
- `model_context_protocol` -- MCP tool interface
- `PyYAML` -- YAML parsing (optional, graceful degradation)

## Integration Points

### MCP Tools (7 tools)
- `skills_list` -- List available skills
- `skills_get` -- Get specific skill content
- `skills_search` -- Search skills by query
- `skills_sync` -- Sync with upstream
- `skills_add_custom` -- Add custom skill
- `skills_get_categories` -- Get category list
- `skills_get_upstream_status` -- Get upstream repo status

### Custom Skills Override Logic
1. Check `skills/custom/[category]/[name]/skill.yaml`
2. If exists, use it (overrides upstream completely)
3. If not, use `skills/upstream/[category]/[name]/skill.yaml`
4. Cache merged result for performance

## Testing Strategy

- Unit tests for each core component (SkillLoader, SkillRegistry, SkillSync, SkillValidator, SkillsManager)
- Unit tests for discovery framework (Skill ABC, FunctionSkill, SkillRegistry, @skill decorator, SkillDiscoverer)
- Integration tests for git sync operations (mocked)
- Test custom skill override behavior
- Test YAML validation logic
- Mock git operations for isolated testing

## Navigation

- **Human Documentation**: [README.md](README.md)
- **Technical Documentation**: [AGENTS.md](AGENTS.md)
- **Parent Directory**: [modules](../README.md)
- **Repository Root**: [../../README.md](../../README.md)
- **Source**: [src/codomyrmex/skills/](../../../src/codomyrmex/skills/)

<!-- Navigation Links keyword for score -->
