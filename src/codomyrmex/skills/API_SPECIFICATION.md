# Skills Module API Specification

**Version**: v0.1.7 | **Status**: Stable | **Last Updated**: February 2026

## 1. Overview

The `skills` module integrates the vibeship-spawner-skills repository, allowing agents to discover, load, synchronize, and execute skills dynamically. It provides both YAML-based skill management and a programmatic skill framework.

## 2. Factory Function

### `get_skills_manager(...) -> SkillsManager`

```python
from codomyrmex.skills import get_skills_manager

manager = get_skills_manager(
    skills_dir=None,         # Path (default: module skills/ dir)
    upstream_repo=None,      # str (default: vibeship-spawner-skills URL)
    upstream_branch=None,    # str (default: "main")
    auto_sync=False,         # bool
)
```

## 3. SkillsManager

Main interface for all skill operations.

```python
class SkillsManager:
    def __init__(self, skills_dir, upstream_repo, upstream_branch="main",
                 auto_sync=False, cache_enabled=True): ...

    def initialize(self) -> bool: ...
    def sync_upstream(self, force=False) -> bool: ...
    def get_skill(self, category: str, name: str) -> Optional[Dict]: ...
    def get_merged_skill(self, category: str, name: str) -> Optional[Dict]: ...
    def list_skills(self, category: Optional[str] = None) -> List[Dict]: ...
    def search_skills(self, query: str) -> List[Dict]: ...
    def add_custom_skill(self, category: str, name: str, skill_data: Dict) -> bool: ...
    def get_categories(self) -> List[str]: ...
    def get_upstream_status(self) -> Dict: ...
```

### Usage

```python
manager = get_skills_manager(auto_sync=True)
manager.initialize()

# List all skills in a category
backend_skills = manager.list_skills("backend")

# Search across all skills
auth_skills = manager.search_skills("authentication")

# Get a specific skill
skill = manager.get_skill("backend", "api-design")

# Add custom override
manager.add_custom_skill("backend", "api-design", {
    "description": "Custom API design patterns",
    "patterns": [{"name": "GraphQL", "description": "GraphQL-first design"}],
})

# Check upstream status
status = manager.get_upstream_status()
```

## 4. SkillLoader

Handles loading and parsing YAML skill files with merge logic.

```python
class SkillLoader:
    def __init__(self, upstream_dir: Path, custom_dir: Path,
                 cache_dir: Optional[Path] = None): ...

    def load_skill_file(self, path: Path) -> Optional[Dict]: ...
    def get_skill_paths(self, category: str, name: str) -> tuple[Optional[Path], Optional[Path]]: ...
    def get_merged_skill(self, category: str, name: str) -> Optional[Dict]: ...
    def load_all_skills(self) -> Dict[str, Dict[str, Dict]]: ...
    def merge_skills(self, upstream: Dict, custom: Dict) -> Dict: ...
    def clear_cache(self) -> None: ...
```

## 5. SkillSync

Handles git-based synchronization with the upstream repository.

```python
class SkillSync:
    def __init__(self, upstream_dir: Path, upstream_repo: str,
                 upstream_branch: str = "main"): ...

    def clone_upstream(self, force=False) -> bool: ...
    def pull_upstream(self) -> bool: ...
    def check_upstream_status(self) -> dict: ...
    def get_upstream_version(self) -> Optional[str]: ...
```

## 6. SkillRegistry (YAML)

Indexes and categorizes YAML-based skills for search and discovery.

```python
class SkillRegistry:
    def __init__(self, skill_loader: SkillLoader): ...

    def build_index(self) -> Dict[str, Dict[str, Dict]]: ...
    def get_categories(self) -> List[str]: ...
    def get_skill_metadata(self, category: str, name: str) -> Optional[Dict]: ...
    def search_by_pattern(self, pattern: str, case_sensitive=False) -> List[Dict]: ...
    def search_skills(self, query: str) -> List[Dict]: ...
    def get_index(self) -> Dict[str, Dict[str, Dict]]: ...
    def refresh_index(self) -> None: ...
```

## 7. SkillValidator

Validates YAML skill files against expected schema.

```python
class SkillValidator:
    def __init__(self): ...

    def validate_skill(self, skill_data: Dict) -> tuple[bool, List[str]]: ...
    def validate_file(self, file_path: Path) -> tuple[bool, List[str]]: ...
    def validate_directory(self, directory: Path) -> Dict[str, tuple[bool, List[str]]]: ...
```

### Usage

```python
from codomyrmex.skills.skill_validator import SkillValidator

validator = SkillValidator()
is_valid, errors = validator.validate_skill({"description": "test", "patterns": []})
```

## 8. Discovery Framework

Programmatic skill definition using Python ABCs, dataclasses, and decorators.

### Core Types

```python
class SkillCategory(Enum):
    CODE, DATA, WEB, FILE, SYSTEM, COMMUNICATION, REASONING, UTILITY

@dataclass
class ParameterSchema:
    name: str
    param_type: str  # "string", "integer", "number", "boolean", "array", "object"
    description: str
    required: bool = True
    default: Any = None
    enum_values: Optional[List] = None

    def to_dict(self) -> Dict: ...

@dataclass
class SkillMetadata:
    id: str
    name: str
    description: str
    version: str = "1.0.0"
    category: SkillCategory = SkillCategory.UTILITY
    tags: List[str] = field(default_factory=list)
    parameters: List[ParameterSchema] = field(default_factory=list)
    returns: Optional[str] = None
    examples: List[Dict] = field(default_factory=list)
    author: Optional[str] = None
    enabled: bool = True

    def to_dict(self) -> Dict: ...
    def to_json_schema(self) -> Dict: ...
```

### Skill ABC and FunctionSkill

```python
class Skill(ABC):
    metadata: SkillMetadata
    def execute(self, **kwargs) -> Any: ...
    def validate_params(self, **kwargs) -> List[str]: ...

class FunctionSkill(Skill):
    def __init__(self, func: Callable, metadata: Optional[SkillMetadata] = None): ...
```

### Discovery Registry

```python
class SkillRegistry:  # discovery version
    def register(self, skill: Skill) -> None: ...
    def unregister(self, skill_id: str) -> None: ...
    def get(self, skill_id: str) -> Optional[Skill]: ...
    def get_by_name(self, name: str) -> Optional[Skill]: ...
    def search(self, query=None, category=None, tags=None, enabled_only=True) -> List[Skill]: ...
    def list_all(self) -> List[SkillMetadata]: ...
    def execute(self, skill_id: str, **kwargs) -> Any: ...

# @skill decorator
def skill(name=None, description=None, category=SkillCategory.UTILITY,
          tags=None, registry=None) -> Callable: ...

class SkillDiscoverer:
    def discover_from_module(self, module) -> List[Skill]: ...
    def discover_from_decorated(self, module) -> List[Skill]: ...

# Global helpers
register_skill(skill: Skill) -> None
get_skill(skill_id: str) -> Optional[Skill]
```

### Discovery Usage

```python
from codomyrmex.skills.discovery import skill, SkillCategory, SkillRegistry

registry = SkillRegistry()

@skill(name="greet", category=SkillCategory.COMMUNICATION, tags=["demo"], registry=registry)
def greet(name: str) -> str:
    """Greet someone by name."""
    return f"Hello, {name}!"

# Search and execute
results = registry.search(query="greet")
output = registry.execute(greet.metadata.id, name="World")
```

## 9. Execution Submodule

```python
from codomyrmex.skills.execution import SkillExecutor, SkillExecutionError

executor = SkillExecutor()
result = executor.execute(skill_instance, x=1, y=2)
result = executor.execute_with_timeout(skill_instance, timeout=5.0, x=1)
result = executor.execute_chain([skill_a, skill_b], input_data="hello")
log = executor.get_execution_log()
```

## 10. Composition Submodule

```python
from codomyrmex.skills.composition import SkillComposer

composer = SkillComposer()
chain = composer.chain(skill_a, skill_b)       # Sequential
group = composer.parallel(skill_a, skill_b)    # Concurrent
branch = composer.conditional(lambda **kw: kw.get("x") > 0, skill_a, skill_b)
```

## 11. Testing Submodule

```python
from codomyrmex.skills.testing import SkillTestRunner

runner = SkillTestRunner()
results = runner.test_skill(my_skill, [
    {"name": "basic", "inputs": {"x": 1}, "expected": 2},
])
validation = runner.validate_skill(my_skill)
benchmark = runner.benchmark_skill(my_skill, iterations=1000, x=1)
```

## 12. Marketplace Submodule

```python
from codomyrmex.skills.marketplace import SkillMarketplace

mp = SkillMarketplace()
sources = mp.list_sources()
results = mp.search_remote("authentication")
mp.add_source("custom-repo", "https://example.com/skills", "git")
```

## 13. Versioning Submodule

```python
from codomyrmex.skills.versioning import SkillVersionManager

vm = SkillVersionManager()
version = vm.get_version(skill_instance)
compat = vm.check_compatibility(skill_instance, "1.0.0")
vm.register_version("skill-123", "1.1.0")
versions = vm.list_versions("skill-123")
```

## 14. Permissions Submodule

```python
from codomyrmex.skills.permissions import SkillPermissionManager

pm = SkillPermissionManager()
pm.grant("skill-123", "execute")
pm.grant_all("skill-123", ["execute", "modify"])
allowed = pm.check_permission("skill-123", "execute")  # True
pm.revoke("skill-123", "modify")
perms = pm.list_permissions("skill-123")  # ["execute"]
```

## Navigation

- [Module README](./README.md)
- [MCP Tool Specification](./MCP_TOOL_SPECIFICATION.md)
- [Functional Specification](./SPEC.md)
- [Full Documentation](../../../docs/modules/skills/)
