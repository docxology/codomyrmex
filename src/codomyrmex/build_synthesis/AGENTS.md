# Agent Guidelines - Build Synthesis

## Module Overview

Build system generation and project scaffolding.

## Key Classes

- **BuildGenerator** — Generate build configurations
- **ProjectScaffold** — Create project structure
- **DependencyResolver** — Resolve dependencies
- **BuildConfig** — Build configuration

## Agent Instructions

1. **Detect tooling** — Auto-detect build system
2. **Template-based** — Use templates for consistency
3. **Validate output** — Check generated files
4. **Include tests** — Generate test configurations
5. **Document builds** — Add build instructions

## Common Patterns

```python
from codomyrmex.build_synthesis import (
    BuildGenerator, ProjectScaffold, DependencyResolver
)

# Generate build config
generator = BuildGenerator()
config = generator.generate(
    project_type="python",
    build_system="pyproject",
    dependencies=["fastapi", "pydantic"]
)
config.write("pyproject.toml")

# Scaffold new project
scaffold = ProjectScaffold("my_project")
scaffold.add_src()
scaffold.add_tests()
scaffold.add_ci()
scaffold.create()

# Resolve dependencies
resolver = DependencyResolver()
resolved = resolver.resolve(requirements)
```

## Testing Patterns

```python
# Verify build generation
generator = BuildGenerator()
config = generator.generate(project_type="python")
assert "pyproject.toml" in config.files

# Verify scaffold
scaffold = ProjectScaffold("test")
files = scaffold.preview()
assert "src/__init__.py" in files
```

## Navigation

- [README](README.md) | [SPEC](SPEC.md) | [PAI](PAI.md)
