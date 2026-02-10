# Building Python Wheels with Build Synthesis

This tutorial demonstrates how to use the Build Synthesis module to build Python wheel distributions.

## Overview

Python wheels are the standard distribution format for Python packages. This tutorial shows you how to configure and execute wheel builds using Codomyrmex's Build Synthesis module.

## Prerequisites

- Python 3.7+ with `build` package installed (`uv pip install build`)
- `setuptools` and `wheel` packages
- A Python package with a `setup.py` or `pyproject.toml` file

## Basic Wheel Build

### Step 1: Define Build Configuration

Create a build configuration file or use the BuildManager API:

```python
from codomyrmex.build_synthesis import BuildManager
from codomyrmex.build_synthesis.build_manager import BuildStep

# Initialize build manager
build_manager = BuildManager()

# Define wheel build steps
wheel_build_steps = [
    BuildStep(
        name="clean_previous_builds",
        command="rm -rf dist/ build/ *.egg-info",
        description="Clean previous build artifacts"
    ),
    BuildStep(
        name="install_build_dependencies",
        command="uv pip install build wheel setuptools",
        description="Ensure build tools are available"
    ),
    BuildStep(
        name="build_wheel",
        command="python -m build --wheel",
        description="Build the wheel distribution",
        working_directory="."
    ),
    BuildStep(
        name="verify_wheel",
        command="python -m pip install --dry-run dist/*.whl",
        description="Verify wheel can be installed"
    )
]

# Register the build
build_manager.register_build("python_wheel", wheel_build_steps)
```

### Step 2: Execute the Build

```python
# Execute the build
result = build_manager.execute_build("python_wheel")

if result.success:
    print(f"Build completed successfully!")
    print(f"Wheel file: {result.output.get('wheel_file', 'unknown')}")
else:
    print(f"Build failed: {result.error_message}")
```

## Advanced: Source Distribution + Wheel

To build both source distribution (sdist) and wheel:

```python
build_steps = [
    BuildStep(
        name="clean",
        command="rm -rf dist/ build/ *.egg-info"
    ),
    BuildStep(
        name="build_all",
        command="python -m build",
        description="Build both sdist and wheel"
    ),
    BuildStep(
        name="list_artifacts",
        command="ls -lh dist/",
        description="List generated artifacts"
    )
]

build_manager.register_build("full_distribution", build_steps)
result = build_manager.execute_build("full_distribution")
```

## Configuration via JSON

You can also define builds using JSON configuration:

```json
{
  "builds": {
    "python_wheel": {
      "steps": [
        {
          "name": "clean",
          "command": "rm -rf dist/ build/ *.egg-info",
          "description": "Clean previous builds"
        },
        {
          "name": "build_wheel",
          "command": "python -m build --wheel",
          "working_directory": ".",
          "timeout": 300
        }
      ],
      "dependencies": ["build", "wheel", "setuptools"]
    }
  }
}
```

## Environment Variables

The build manager respects environment variables for configuration:

```bash
export CODOMYRMEX_BUILD_OUTPUT_DIR="./dist"
export CODOMYRMEX_BUILD_LOG_LEVEL="INFO"
export CODOMYRMEX_BUILD_TIMEOUT=600
```

## Error Handling

The build manager provides detailed error information:

```python
result = build_manager.execute_build("python_wheel")

if not result.success:
    print(f"Error: {result.error_message}")
    print(f"Failed step: {result.failed_step}")
    print(f"Exit code: {result.exit_code}")
    print(f"Output: {result.stdout}")
    print(f"Error output: {result.stderr}")
```

## Best Practices

1. **Always clean before building**: Remove previous build artifacts to avoid conflicts
2. **Use virtual environments**: Build in isolated environments to ensure reproducibility
3. **Verify dependencies**: Ensure all build dependencies are specified in `setup.py` or `pyproject.toml`
4. **Test the wheel**: After building, test installing the wheel in a clean environment
5. **Version management**: Use version tags or environment variables for version management

## Integration with CI/CD

Example CI/CD integration:

```python
import os
from codomyrmex.build_synthesis import BuildManager

# CI/CD environment setup
os.environ['CODOMYRMEX_BUILD_OUTPUT_DIR'] = os.environ.get('CI_ARTIFACTS_DIR', './artifacts')

build_manager = BuildManager()
result = build_manager.execute_build("python_wheel")

if result.success:
    # Upload to artifact storage
    upload_to_artifacts(result.output.get('wheel_file'))
else:
    raise Exception(f"Build failed: {result.error_message}")
```

## Troubleshooting

**Issue**: `build` command not found
- **Solution**: Install build tools: `uv pip install build wheel setuptools`

**Issue**: Wheel build fails with metadata errors
- **Solution**: Verify `setup.py` or `pyproject.toml` has correct metadata

**Issue**: Build times out
- **Solution**: Increase timeout in BuildStep or set `CODOMYRMEX_BUILD_TIMEOUT`

**Issue**: Dependencies not found during build
- **Solution**: Ensure all dependencies are specified in build requirements

## Next Steps

- See [Docker Build Tutorial](./docker_build_tutorial.md) for container builds
- Review [Build Orchestration](../technical_overview.md) for advanced usage
- Check [API Specification](../../../../src/codomyrmex/build_synthesis/API_SPECIFICATION.md) for complete API reference


## Navigation Links

- **Parent**: [Project Overview](../README.md)
- **Module Index**: [All Agents](../../AGENTS.md)
- **Documentation**: [Reference Guides](../../README.md)
- **Home**: [Root README](../../README.md)
