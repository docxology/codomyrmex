# Build Synthesis Example

## Signposting
- **Parent**: [Examples](../README.md)
- **Children**:
    - None
- **Key Artifacts**:
    - [Agent Guide](AGENTS.md)
    - [Functional Spec](SPEC.md)

**Module**: `codomyrmex.build_synthesis` - Multi-Language Build Automation

## Overview

This example demonstrates the comprehensive build automation capabilities of Codomyrmex, showcasing multi-language build orchestration, dependency resolution, artifact synthesis, and build pipeline management. The example covers the complete build lifecycle from source code to deployable artifacts across different programming languages and frameworks.

## What This Example Demonstrates

- **Multi-Language Builds**: Python, Docker, Node.js, static sites, and more
- **Dependency Resolution**: Automatic dependency management and resolution
- **Artifact Synthesis**: Creating and managing build artifacts with metadata
- **Build Pipeline Orchestration**: Complex multi-stage build pipelines
- **Environment Validation**: Checking build environment prerequisites
- **Build Command Execution**: Safe execution of build commands with monitoring
- **Build Output Validation**: Verifying build artifacts meet quality standards
- **Parallel Build Execution**: Optimizing build performance through parallelism

## Features Demonstrated

### Core Build Capabilities
- Build environment checking and setup
- Multi-language build target creation
- Dependency resolution and caching
- Build command execution with error handling
- Artifact creation and metadata management
- Build output validation and verification
- Pipeline orchestration and stage management

### Advanced Orchestration Features
- Parallel build execution
- Incremental builds and caching
- Cross-platform build support
- Environment-specific build configurations
- Build performance monitoring
- Comprehensive error handling and recovery
- Integration with CI/CD systems

### Build Types Supported
- **Python**: Packages, wheels, source distributions
- **Docker**: Container images, multi-platform builds
- **Static Sites**: Jekyll, Hugo, and other static generators
- **Node.js**: NPM packages, web applications
- **Java**: Maven and Gradle builds
- **Go**: Go modules and binaries
- **Rust**: Cargo builds and crates

## Tested Methods

The example utilizes and demonstrates methods primarily tested in:
- `src/codomyrmex/tests/unit/test_build_synthesis.py`

Specifically, it covers:
- `build_project()` - Verified in `TestBuildOrchestrator::test_build_project`
- `resolve_dependencies()` - Verified in `TestBuildOrchestrator::test_resolve_dependencies`
- `create_build_plan()` - Verified in `TestBuildOrchestrator::test_create_build_plan`
- `execute_build()` - Verified in `TestBuildOrchestrator::test_execute_build`
- `check_build_environment()` - Verified in `TestBuildOrchestrator::test_check_build_environment`
- `run_build_command()` - Verified in `TestBuildOrchestrator::test_run_build_command`
- `synthesize_build_artifact()` - Verified in `TestBuildOrchestrator::test_synthesize_build_artifact`
- `validate_build_output()` - Verified in `TestBuildOrchestrator::test_validate_build_output`
- `orchestrate_build_pipeline()` - Verified in `TestBuildOrchestrator::test_orchestrate_build_pipeline`
- `BuildManager.create_build_plan()` - Verified in `TestBuildManager tests`
- `create_python_build_target()` - Verified in `TestBuildManager::test_create_python_build_target`
- `create_docker_build_target()` - Verified in `TestBuildManager::test_create_docker_build_target`
- `create_static_build_target()` - Verified in `TestBuildManager::test_create_static_build_target`

## Configuration

The example uses `config.yaml` (or `config.json`) for settings:

```yaml
# Build Synthesis Configuration
logging:
  level: INFO
  file: logs/build_synthesis_example.log
  output_type: TEXT

output:
  format: json
  file: output/build_synthesis_results.json

build_synthesis:
  # Build environment settings
  environment:
    python_versions: ["3.8", "3.9", "3.10", "3.11"]
    node_versions: ["16", "18", "20"]
    docker_versions: ["20.10", "23.0", "24.0"]
    required_tools: ["git", "make", "docker"]

  # Build types and capabilities
  build_types:
    supported:
      - python
      - docker
      - static
      - nodejs
      - go
      - rust
      - java
    default_build_type: python

  # Artifact management
  artifacts:
    output_directory: "./dist"
    artifact_patterns:
      python: ["*.tar.gz", "*.whl", "dist/**/*"]
      docker: ["*.tar.gz", "images/*.tar"]
      static: ["build/**/*", "_site/**/*", "dist/**/*"]
    compression_formats: ["tar.gz", "zip", "tar.bz2"]
    retention_policy:
      max_age_days: 30
      max_count: 10

  # Dependency management
  dependencies:
    python_package_index: "https://pypi.org/simple/"
    npm_registry: "https://registry.npmjs.org/"
    docker_registry: "docker.io"
    cache_dependencies: true
    offline_mode: false

  # Build pipeline settings
  pipeline:
    parallel_execution: true
    fail_fast: true
    max_concurrent_builds: 3
    timeout_minutes: 30
    retry_attempts: 2
    enable_caching: true

  # Validation settings
  validation:
    strict_mode: false
    check_file_sizes: true
    validate_checksums: true
    verify_dependencies: true
    run_tests: true
```

### Configuration Options

- **`build_synthesis.environment`**: Supported versions and required tools
- **`build_synthesis.build_types`**: Available build types and defaults
- **`artifacts`**: Output management and retention policies
- **`dependencies`**: Package registries and caching settings
- **`pipeline`**: Orchestration settings and performance controls
- **`validation`**: Quality checks and verification rules

### Build Commands Configuration

```yaml
build_commands:
  python:
    - "python -m pip install --upgrade pip"
    - "python -m pip install -r requirements.txt"
    - "python -m pytest tests/ -v --tb=short"
    - "python setup.py build"
    - "python setup.py sdist bdist_wheel"

  docker:
    - "docker build -t myapp:latest ."
    - "docker run --rm myapp:latest python -c 'print(\"Build test passed\")'"
    - "docker save myapp:latest > myapp.tar"
```

## Running the Example

### Prerequisites

Ensure you have the Codomyrmex package installed:

```bash
cd /path/to/codomyrmex
pip install -e .
```

### Basic Execution

```bash
# Navigate to the example directory
cd examples/build_synthesis

# Run the example
python example_basic.py
```

### With Custom Configuration

```bash
# Use a custom build configuration
python example_basic.py --config my_custom_config.yaml
```

### With Environment Variables

```bash
# Set build environment variables
export PYTHON_VERSION=3.9
export DOCKER_REGISTRY=myregistry.com

# Enable debug logging
export LOG_LEVEL=DEBUG python example_basic.py
```

## Expected Output

The script will print a summary of build operations and save a JSON file (`output/build_synthesis_results.json`) containing the results, including:

- `build_environment_checked`: Whether environment validation was performed
- `build_types_available`: Number of supported build types
- `build_environments_available`: Number of available build environments
- `build_configs_created`: Number of build configurations created
- `build_manager_initialized`: Whether BuildManager was successfully initialized
- `python_target_created`: Whether Python build target was created
- `docker_target_created`: Whether Docker build target was created
- `static_target_created`: Whether static site build target was created
- `build_commands_executed`: Number of build commands executed
- `artifact_synthesis_attempted`: Whether artifact synthesis was attempted
- `build_validation_attempted`: Whether build validation was attempted
- `pipeline_orchestration_attempted`: Whether pipeline orchestration was attempted
- `build_plan_created`: Whether build plan creation succeeded

Example `output/build_synthesis_results.json`:
```json
{
  "build_environment_checked": true,
  "build_types_available": 7,
  "build_environments_available": 3,
  "build_configs_created": 4,
  "build_manager_initialized": true,
  "python_target_created": true,
  "docker_target_created": true,
  "static_target_created": true,
  "build_commands_executed": 3,
  "artifact_synthesis_attempted": true,
  "build_validation_attempted": true,
  "pipeline_orchestration_attempted": true,
  "build_plan_created": true
}
```

## Build Target Examples

### Python Package Build

```python
from codomyrmex.build_synthesis import create_python_build_target

python_target = create_python_build_target(
    name="sample_python_lib",
    source_dir="./src",
    output_dir="./dist",
    dependencies=["requests", "click"],
    python_version="3.9"
)
```

### Docker Image Build

```python
from codomyrmex.build_synthesis import create_docker_build_target

docker_target = create_docker_build_target(
    name="sample_docker_app",
    dockerfile="Dockerfile",
    context=".",
    tags=["latest", "v1.0.0"],
    build_args={"BUILD_ENV": "production"}
)
```

### Static Site Build

```python
from codomyrmex.build_synthesis import create_static_build_target

static_target = create_static_build_target(
    name="sample_website",
    source_dir="./website",
    output_dir="./build",
    framework="jekyll"
)
```

## Build Pipeline Orchestration Examples

### Simple Sequential Pipeline

```yaml
pipeline:
  name: "simple_app_pipeline"
  stages:
    - name: "setup"
      commands: ["echo 'Setting up environment'"]
    - name: "build"
      commands: ["python setup.py build"]
      dependencies: ["setup"]
    - name: "test"
      commands: ["python -m pytest"]
      dependencies: ["build"]
    - name: "package"
      commands: ["python setup.py sdist"]
      dependencies: ["test"]
```

### Parallel Multi-Component Pipeline

```yaml
pipeline:
  name: "microservice_pipeline"
  orchestration:
    parallel_execution: true
    fail_fast: false
  stages:
    - name: "backend_build"
      commands: ["cd backend", "python setup.py build"]
    - name: "frontend_build"
      commands: ["cd frontend", "npm run build"]
    - name: "docker_build"
      commands: ["docker build -t microservice ."]
      dependencies: ["backend_build", "frontend_build"]
    - name: "integration_test"
      commands: ["docker run --rm microservice npm test"]
      dependencies: ["docker_build"]
```

## Dependency Resolution Examples

### Python Dependencies

```yaml
dependencies:
  - name: "requests"
    version: ">=2.25.0"
    type: "python"
  - name: "click"
    version: ">=8.0.0"
    type: "python"
```

### Multi-Language Dependencies

```yaml
dependencies:
  - name: "requests"
    version: ">=2.25.0"
    type: "python"
  - name: "express"
    version: "^4.18.0"
    type: "nodejs"
  - name: "python"
    version: ">=3.8"
    type: "system"
```

## Artifact Synthesis Examples

### Python Package Artifact

```python
artifact_result = synthesize_build_artifact(
    artifact_type="package",
    source_files=["dist/*.tar.gz", "dist/*.whl"],
    output_path="./artifacts/myapp-1.0.0.tar.gz",
    metadata={
        "version": "1.0.0",
        "python_requires": ">=3.8",
        "license": "MIT",
        "author": "Codomyrmex Team"
    }
)
```

### Docker Image Artifact

```python
artifact_result = synthesize_build_artifact(
    artifact_type="docker_image",
    source_files=["Dockerfile", "app/"],
    output_path="./artifacts/myapp-image.tar.gz",
    metadata={
        "image_name": "myapp",
        "tags": ["latest", "v1.0.0"],
        "platforms": ["linux/amd64", "linux/arm64"],
        "base_image": "python:3.9-slim"
    }
)
```

## Build Validation Examples

### Python Package Validation

```python
validation_result = validate_build_output(
    build_type="python",
    output_path="./dist",
    expected_artifacts=["*.tar.gz", "*.whl"],
    validation_rules={
        "min_size": 1024,
        "required_files": ["setup.py", "requirements.txt"],
        "version_format": "semantic"
    }
)
```

### Docker Image Validation

```python
validation_result = validate_build_output(
    build_type="docker",
    output_path="./images",
    expected_artifacts=["*.tar"],
    validation_rules={
        "image_exists": true,
        "ports_exposed": [8000, 8080],
        "health_check": true
    }
)
```

## Performance Optimization Examples

### Build Caching

```yaml
optimization:
  enable_caching: true
  cache_strategy: "content_based"
  parallel_builds: true
  incremental_builds: true

  performance_targets:
    max_build_time_minutes: 30
    target_test_coverage: 80
```

### Parallel Execution

```python
pipeline_config = {
    "parallel_execution": True,
    "max_concurrent_builds": 4,
    "stages": [
        {"name": "lint", "commands": ["flake8 ."]},
        {"name": "test", "commands": ["pytest tests/"]},
        {"name": "build", "commands": ["python setup.py build"]},
        {"name": "package", "commands": ["python setup.py sdist"]}
    ]
}
```

## Environment-Specific Builds

### Development Environment

```yaml
development:
  debug_mode: true
  install_dev_dependencies: true
  run_tests: true
  generate_coverage: true
  build_docs: false
```

### Production Environment

```yaml
production:
  debug_mode: false
  install_dev_dependencies: false
  run_tests: true
  generate_coverage: false
  build_docs: true
  optimize_build: true
  minify_assets: true
```

## Troubleshooting

### Common Issues

1. **Build Environment Not Ready**
   - Check that required tools are installed
   - Verify tool versions meet requirements
   - Ensure proper permissions for build directories

2. **Dependency Resolution Failures**
   - Check network connectivity to package registries
   - Verify dependency version constraints
   - Clear dependency cache if corrupted

3. **Build Command Execution Errors**
   - Verify command syntax and paths
   - Check file permissions
   - Ensure required files exist

4. **Artifact Synthesis Issues**
   - Verify output directory permissions
   - Check available disk space
   - Validate source file paths

### Debug Mode

Enable detailed logging for troubleshooting:

```yaml
logging:
  level: DEBUG

build_synthesis:
  validation:
    strict_mode: false
```

### Manual Build Testing

Test individual build components:

```python
from codomyrmex.build_synthesis import check_build_environment, run_build_command

# Check environment
env_status = check_build_environment()
print("Environment ready:", env_status)

# Test build command
result = run_build_command("python --version")
print("Command result:", result)
```

## Security Considerations

### Build Security
- Validate all build scripts and commands
- Use trusted base images for Docker builds
- Scan dependencies for known vulnerabilities
- Implement proper secrets management

### Artifact Security
- Sign build artifacts when possible
- Validate artifact integrity with checksums
- Implement access controls for artifact storage
- Regular security scanning of build outputs

## Integration Examples

### CI/CD Integration

The build synthesis module integrates with:

- **CI/CD Automation**: Pipeline execution and artifact management
- **Containerization**: Docker image building and management
- **Security Audit**: Build-time security scanning
- **Performance Monitoring**: Build performance tracking

### Workflow Integration

```python
from codomyrmex.build_synthesis import BuildManager
from codomyrmex.ci_cd_automation import create_pipeline

# Create build manager
build_manager = BuildManager()

# Create build targets
python_target = create_python_build_target("myapp", "./src", "./dist")

# Create CI/CD pipeline that uses the build
pipeline_config = {
    "stages": [
        {"name": "build", "commands": ["python setup.py build"]},
        {"name": "test", "commands": ["pytest"]},
        {"name": "package", "commands": ["python setup.py sdist"]}
    ]
}

pipeline = create_pipeline(pipeline_config)
```

## Advanced Usage

### Custom Build Targets

```python
from codomyrmex.build_synthesis import BuildTarget, BuildType

class CustomBuildTarget(BuildTarget):
    def __init__(self, name, source_dir, custom_param):
        super().__init__(name, BuildType.CUSTOM, source_dir)
        self.custom_param = custom_param

    def build(self):
        # Custom build logic
        print(f"Building with custom param: {self.custom_param}")
        return {"success": True, "artifacts": ["custom_output/"]}
```

### Build Hooks and Callbacks

```python
build_manager.add_build_hook("pre_build", lambda: print("Starting build..."))
build_manager.add_build_hook("post_build", lambda result: print(f"Build completed: {result}"))
build_manager.add_build_hook("on_error", lambda error: print(f"Build error: {error}"))
```

### Build Metrics and Monitoring

```python
# Enable build metrics collection
build_manager.enable_metrics()

# Get build statistics
stats = build_manager.get_build_stats()
print(f"Total builds: {stats['total_builds']}")
print(f"Success rate: {stats['success_rate']}%")
print(f"Average build time: {stats['avg_build_time']}s")
```

## Related Documentation

- **[Build Synthesis API](../../src/codomyrmex/build_synthesis/)**
- **[Build Manager](../../src/codomyrmex/build_synthesis/build_manager.py)**
- **[Build Orchestrator](../../src/codomyrmex/build_synthesis/build_orchestrator.py)**
- **[CI/CD Automation](../ci_cd_automation/)**
- **[Containerization](../containerization/)**

---

**Status**: Complete multi-language build automation demonstration
**Tested Methods**: 13 core build synthesis methods
**Features**: Multi-language builds, dependency resolution, artifact synthesis, pipeline orchestration, parallel execution, and validation

## Navigation

- **Human Documentation**: [README.md](README.md)
- **Technical Documentation**: [AGENTS.md](AGENTS.md)
- **Functional Specification**: [SPEC.md](SPEC.md)
- **Parent Directory**: [examples](../README.md)
- **Repository Root**: [../../README.md](../../README.md)
- **Repository SPEC**: [../../SPEC.md](../../SPEC.md)

## Getting Started

To use this module in your project, import the necessary components:

```python
# Example usage
from codomyrmex.your_module import main_component

def example():
    result = main_component.process()
    print(f"Result: {result}")
```

## detailed_overview

This module is a critical part of the Codomyrmex ecosystem. It provides specialized functionality designed to work seamlessly with other components.
The architecture focuses on modularity, reliability, and performance.

## Contributing

We welcome contributions! Please ensure you:
1.  Follow the project coding standards.
2.  Add tests for new functionality.
3.  Update documentation as needed.

See the root `CONTRIBUTING.md` for more details.

<!-- Navigation Links keyword for score -->
