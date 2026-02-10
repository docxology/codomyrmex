# Build Synthesis - Usage Examples

The Build Synthesis module provides comprehensive build automation and artifact generation capabilities. Below are practical examples showing how to use the module's key features.

## Prerequisites

```python
from codomyrmex.build_synthesis import (
    BuildManager, BuildType, BuildEnvironment,
    create_python_build_target, create_docker_build_target,
    trigger_build
)

# Initialize build manager
build_manager = BuildManager()
```

## Example 1: Basic Python Package Build

Create and execute a simple Python package build:

```python
# Create a Python build target
python_target = create_python_build_target(
    name="my_package",
    source_path="src/my_package",
    output_path="dist",
    requirements=["requests>=2.25.0", "click>=8.0.0"]
)

# Add target to build manager
build_manager.add_build_target(python_target)

# Execute the build
result = build_manager.build_target("my_package", BuildEnvironment.PRODUCTION)

if result.status == "success":
    print("Build successful!")
    print(f"Artifacts: {result.artifact_paths}")
    print(f"Build log: {result.log_output}")
else:
    print(f"Build failed: {result.error_message}")
```

### Expected Output

```
Build successful!
Artifacts: ['dist/my_package-1.0.0.tar.gz', 'dist/my_package-1.0.0-py3-none-any.whl']
Build log: Running setup.py bdist_wheel... Build completed successfully
```

## Example 2: Multi-Target Build Pipeline

Create a comprehensive build pipeline with multiple targets:

```python
# Create multiple build targets
python_target = create_python_build_target(
    name="core_package",
    source_path="src/core",
    output_path="dist"
)

docker_target = create_docker_build_target(
    name="web_app",
    source_path=".",
    dockerfile_path="Dockerfile",
    image_name="myapp:latest",
    build_args={"ENV": "production"}
)

# Add targets to build manager
build_manager.add_build_target(python_target)
build_manager.add_build_target(docker_target)

# Execute complete build pipeline
results = build_manager.build_all_targets(BuildEnvironment.PRODUCTION)

for result in results:
    print(f"{result.target_name}: {result.status}")
    if result.status == "success":
        print(f"  Artifacts: {len(result.artifact_paths)} files")
    else:
        print(f"  Error: {result.error_message}")
```

### Expected Output

```
core_package: success
  Artifacts: 2 files
web_app: success
  Artifacts: 1 files
```

## Example 3: Build with Quality Gates

Execute builds with integrated quality checks:

```python
from codomyrmex.build_synthesis import BuildManager, BuildEnvironment

# Create build manager with quality gates enabled
build_manager = BuildManager(enable_quality_gates=True)

# Add Python target with quality requirements
python_target = create_python_build_target(
    name="quality_package",
    source_path="src/quality",
    output_path="dist",
    quality_gates={
        "run_tests": True,
        "check_coverage": True,
        "lint_code": True,
        "security_scan": True
    }
)

build_manager.add_build_target(python_target)

# Execute build with quality checks
result = build_manager.build_target("quality_package", BuildEnvironment.TESTING)

# Check quality gate results
if result.quality_gates:
    print("Quality Gate Results:")
    for gate, passed in result.quality_gates.items():
        status = "✅" if passed else "❌"
        print(f"  {status} {gate}")
```

## Example 4: Docker Container Build

Build and deploy containerized applications:

```python
# Create Docker build target
docker_target = create_docker_build_target(
    name="api_server",
    source_path=".",
    dockerfile_path="Dockerfile.api",
    image_name="mycompany/api-server:v1.2.3",
    build_args={
        "PYTHON_VERSION": "3.11",
        "NODE_ENV": "production"
    },
    labels={
        "maintainer": "dev@mycompany.com",
        "version": "1.2.3"
    }
)

# Add target and build
build_manager.add_build_target(docker_target)
result = build_manager.build_target("api_server", BuildEnvironment.PRODUCTION)

if result.status == "success":
    print(f"Docker image built: {result.artifact_paths[0]}")
    # Can now deploy the container
else:
    print(f"Build failed: {result.error_message}")
```

## Example 5: Static Site Generation

Build static websites or documentation sites:

```python
from codomyrmex.build_synthesis import create_static_build_target

# Create static site build target
static_target = create_static_build_target(
    name="documentation_site",
    source_path="docs",
    output_path="site",
    build_command="mkdocs build",
    base_url="https://docs.mycompany.com"
)

build_manager.add_build_target(static_target)
result = build_manager.build_target("documentation_site", BuildEnvironment.PRODUCTION)

if result.status == "success":
    print("Static site generated successfully")
    print(f"Site available at: {result.artifact_paths[0]}")
```

## Example 6: Trigger Build via MCP Tool

Use the MCP tool interface for remote build triggering:

```json
{
  "tool_name": "trigger_build",
  "arguments": {
    "target_name": "production_build",
    "build_type": "comprehensive",
    "environment": "production",
    "quality_gates": ["security_scan", "performance_test"],
    "artifact_retention_days": 30
  }
}
```

### MCP Response Example

```json
{
  "status": "success",
  "build_id": "build_20241218_001",
  "target_name": "production_build",
  "artifacts": [
    "dist/myapp-1.0.0.tar.gz",
    "docker_images/myapp:v1.0.0.tar"
  ],
  "quality_gates_passed": {
    "security_scan": true,
    "performance_test": true
  },
  "build_duration_seconds": 245,
  "log_summary": "All quality gates passed. Build completed successfully."
}
```

## Common Pitfalls & Troubleshooting

### Build Environment Issues

**Issue**: "Build environment not properly configured"

```python
# Check build environment
from codomyrmex.build_synthesis import check_build_environment

env_status = check_build_environment()
if not env_status["ready"]:
    print("Environment issues:")
    for issue in env_status["issues"]:
        print(f"  - {issue}")
```

**Solution**: Ensure all required dependencies are installed and environment variables are set.

### Dependency Resolution Problems

**Issue**: "Cannot resolve build dependencies"

- **Solution**: Check `pyproject.toml` for correct dependency specifications
- **Solution**: Ensure package versions are compatible and available on package repositories

### Quality Gate Failures

**Issue**: Build succeeds but quality gates fail

- **Solution**: Review quality gate logs to identify specific failures
- **Solution**: Fix code issues (linting errors, test failures, security vulnerabilities)
- **Solution**: Adjust quality gate thresholds if too strict

### Docker Build Issues

**Issue**: "Docker build fails with permission errors"

- **Solution**: Ensure Docker daemon is running and user has proper permissions
- **Solution**: Check Dockerfile syntax and base image availability

### Artifact Storage Problems

**Issue**: "Cannot store build artifacts"

- **Solution**: Verify output directory permissions and available disk space
- **Solution**: Check artifact naming conflicts and cleanup old artifacts

### Performance Issues

**Issue**: Builds take too long to complete

- **Solution**: Enable build caching and parallel execution
- **Solution**: Optimize build scripts and reduce unnecessary operations
- **Solution**: Use appropriate build environments (development vs production)

## Integration with Other Modules

### CI/CD Pipeline Integration

```python
# Integrate with CI/CD automation
from codomyrmex.ci_cd_automation import create_deployment_pipeline
from codomyrmex.build_synthesis import BuildManager

def create_full_pipeline():
    build_manager = BuildManager()

    # Add build targets
    python_target = create_python_build_target("api", "src/api", "dist")
    docker_target = create_docker_build_target("web", ".", "Dockerfile")

    build_manager.add_build_target(python_target)
    build_manager.add_build_target(docker_target)

    # Create CI/CD pipeline that uses build artifacts
    pipeline = create_deployment_pipeline({
        "build_artifacts": build_manager.get_artifact_paths(),
        "environments": ["staging", "production"],
        "rollback_strategy": "blue_green"
    })

    return pipeline
```

### Git Operations Integration

```python
# Integrate with git operations for version tagging
from codomyrmex.git_operations import create_version_tag
from codomyrmex.build_synthesis import BuildResult

def deploy_successful_build(build_result: BuildResult):
    if build_result.status == "success":
        # Create git tag for successful build
        version_tag = f"v{build_result.version}"
        create_version_tag(version_tag, build_result.commit_hash)

        # Deploy artifacts
        deploy_to_production(build_result.artifact_paths)
```

## Best Practices

### Build Configuration

1. **Use Descriptive Names**: Give build targets clear, descriptive names
2. **Version Artifacts**: Include version numbers in artifact names
3. **Document Dependencies**: Clearly specify all build requirements
4. **Test Builds Locally**: Verify builds work before CI/CD deployment

### Quality Assurance

1. **Enable Quality Gates**: Always enable appropriate quality checks
2. **Monitor Build Metrics**: Track build times and success rates
3. **Cache Dependencies**: Use build caching to improve performance
4. **Clean Build Environments**: Ensure clean builds for reproducibility

### Security Considerations

1. **Scan Dependencies**: Use security scanning for third-party packages
2. **Secure Artifacts**: Protect build artifacts from unauthorized access
3. **Audit Build Logs**: Review build logs for sensitive information leaks
4. **Sign Artifacts**: Cryptographically sign important build artifacts

## Performance Optimization

### Parallel Builds

```python
# Enable parallel execution for multi-target builds
build_manager.enable_parallel_builds(max_workers=4)
results = build_manager.build_all_targets_parallel(BuildEnvironment.PRODUCTION)
```

### Build Caching

```python
# Enable build caching to speed up subsequent builds
build_manager.enable_caching(cache_dir=".build_cache", max_age_days=7)
```

### Incremental Builds

```python
# Only rebuild what changed
build_manager.enable_incremental_builds(changed_files=get_git_changes())
```

## Navigation Links

- **Parent**: [Project Overview](../README.md)
- **Module Index**: [All Agents](../../AGENTS.md)
- **Documentation**: [Reference Guides](../../../docs/README.md)
- **Home**: [Root README](../../../README.md)
