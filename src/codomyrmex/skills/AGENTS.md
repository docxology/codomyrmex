# Codomyrmex Agents — src/codomyrmex/skills

## Signposting
- **Parent**: [codomyrmex](../AGENTS.md)
- **Self**: [Agents](AGENTS.md)
- **Children**:
    - [docs](docs/AGENTS.md)
    - [tests](tests/AGENTS.md)
- **Key Artifacts**:
    - [Functional Spec](SPEC.md)
    - [Human Readme](README.md)

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: January 2026

## Purpose

Integration with the vibeship-spawner-skills repository, providing access to 462+ specialized skills organized across 35 categories. Enables skill management, syncing with upstream, and support for custom skills that can override upstream skills.

## Active Components
- `__init__.py` – Module exports and public API
- `skills_manager.py` – Main skill management interface
- `skill_loader.py` – YAML skill loading and parsing
- `skill_sync.py` – Git sync with upstream repository
- `skill_registry.py` – Skill discovery and indexing
- `skill_validator.py` – YAML schema validation
- `AGENTS.md` – This file
- `README.md` – Human-readable documentation
- `SPEC.md` – Functional specification
- `tests/` – Test suite
- `docs/` – Additional documentation

## Key Classes and Functions

### SkillsManager (`skills_manager.py`)
- `SkillsManager(skills_dir: Path, upstream_repo: str, upstream_branch: str = "main", auto_sync: bool = False, cache_enabled: bool = True)` – Main skill management interface
- `initialize() -> bool` – Setup skills directory, clone if needed
- `sync_upstream(force: bool = False) -> bool` – Sync with upstream repo
- `get_skill(category: str, name: str) -> Optional[Dict[str, Any]]` – Load specific skill
- `list_skills(category: Optional[str] = None) -> List[Dict[str, Any]]` – List available skills
- `search_skills(query: str) -> List[Dict[str, Any]]` – Search skills by content
- `add_custom_skill(category: str, name: str, skill_data: Dict[str, Any]) -> bool` – Add custom skill
- `get_merged_skill(category: str, name: str) -> Optional[Dict[str, Any]]` – Get skill with custom overrides
- `get_categories() -> List[str]` – Get all available skill categories
- `get_upstream_status() -> Dict[str, Any]` – Get status of upstream repository

### SkillLoader (`skill_loader.py`)
- `SkillLoader(upstream_dir: Path, custom_dir: Path, cache_dir: Optional[Path] = None)` – Load and parse YAML skill files
- `load_skill_file(path: Path) -> Optional[Dict[str, Any]]` – Load a skill file from disk
- `get_skill_paths(category: str, name: str) -> tuple[Optional[Path], Optional[Path]]` – Get paths for upstream and custom skill files
- `get_merged_skill(category: str, name: str) -> Optional[Dict[str, Any]]` – Get skill with custom overrides applied
- `load_all_skills() -> Dict[str, Dict[str, Dict[str, Any]]]` – Load all available skills
- `merge_skills(upstream: Dict[str, Any], custom: Dict[str, Any]) -> Dict[str, Any]` – Merge upstream and custom skills
- `clear_cache() -> None` – Clear the skill cache

### SkillSync (`skill_sync.py`)
- `SkillSync(upstream_dir: Path, upstream_repo: str, upstream_branch: str = "main")` – Git operations for syncing upstream
- `clone_upstream(force: bool = False) -> bool` – Clone the upstream repository
- `pull_upstream() -> bool` – Pull latest changes from upstream repository
- `check_upstream_status() -> Dict[str, Any]` – Check the status of the upstream repository
- `get_upstream_version() -> Optional[str]` – Get the current version/commit of the upstream repository

### SkillRegistry (`skill_registry.py`)
- `SkillRegistry(skill_loader: SkillLoader)` – Index and categorize skills
- `build_index() -> Dict[str, Dict[str, Dict[str, Any]]]` – Build the skill index from all available skills
- `get_categories() -> List[str]` – Get all available skill categories
- `get_skill_metadata(category: str, name: str) -> Optional[Dict[str, Any]]` – Get metadata for a specific skill
- `search_by_pattern(pattern: str, case_sensitive: bool = False) -> List[Dict[str, Any]]` – Search skills by pattern (regex or text)
- `search_skills(query: str) -> List[Dict[str, Any]]` – Search skills by query string
- `get_index() -> Dict[str, Dict[str, Dict[str, Any]]]` – Get the current skill index
- `refresh_index() -> None` – Refresh the skill index by rebuilding it

### SkillValidator (`skill_validator.py`)
- `SkillValidator()` – Validates skill YAML files against expected schema
- `validate_skill(skill_data: Dict[str, Any]) -> tuple[bool, List[str]]` – Validate a skill data dictionary
- `validate_file(file_path: Path) -> tuple[bool, List[str]]` – Validate a skill file
- `validate_directory(directory: Path) -> Dict[str, tuple[bool, List[str]]]` – Validate all skill files in a directory

### Module Functions (`__init__.py`)
- `get_skills_manager(skills_dir: Optional[Path] = None, upstream_repo: Optional[str] = None, upstream_branch: Optional[str] = None, auto_sync: bool = False) -> SkillsManager` – Get a configured SkillsManager instance

## Operating Contracts
- Maintain alignment between code, documentation, and configured workflows.
- Ensure Model Context Protocol interfaces remain available for sibling agents.
- Record outcomes in shared telemetry and update TODO queues when necessary.
- Custom skills override upstream skills with the same category/name.
- Skill loading uses merge logic: custom skills take precedence over upstream.

## Navigation Links
- **Human Documentation**: [README.md](README.md)
- **Functional Specification**: [SPEC.md](SPEC.md)
- **📁 Parent Directory**: [codomyrmex](../README.md) - Parent directory documentation
- **🏠 Project Root**: [README](../../../README.md) - Main project documentation

