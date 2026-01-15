# Building Docker Images with Build Synthesis

This tutorial demonstrates how to use the Build Synthesis module to build Docker container images.

## Overview

Docker builds are essential for containerizing applications. This tutorial shows you how to configure and execute Docker image builds using Codomyrmex's Build Synthesis module.

## Prerequisites

- Docker installed and running (`docker --version`)
- Docker daemon accessible (`docker info`)
- A `Dockerfile` in your project directory
- Appropriate Docker permissions

## Basic Docker Build

### Step 1: Define Build Configuration

```python
from codomyrmex.build_synthesis import BuildManager
from codomyrmex.build_synthesis.build_manager import BuildStep

# Initialize build manager
build_manager = BuildManager()

# Define Docker build steps
docker_build_steps = [
    BuildStep(
        name="validate_dockerfile",
        command="docker buildx du --dry-run .",
        description="Validate Dockerfile syntax",
        working_directory="."
    ),
    BuildStep(
        name="build_image",
        command="docker build -t myapp:latest .",
        description="Build Docker image",
        working_directory=".",
        timeout=600  # 10 minutes
    ),
    BuildStep(
        name="verify_image",
        command="docker images myapp:latest",
        description="Verify image was created"
    )
]

# Register the build
build_manager.register_build("docker_image", docker_build_steps)
```

### Step 2: Execute the Build

```python
# Execute the build
result = build_manager.execute_build("docker_image")

if result.success:
    print(f"Build completed successfully!")
    print(f"Image: {result.output.get('image_name', 'unknown')}")
else:
    print(f"Build failed: {result.error_message}")
```

## Tagged Builds with Version

```python
import os

version = os.environ.get('VERSION', 'latest')

docker_build_steps = [
    BuildStep(
        name="build_tagged",
        command=f"docker build -t myapp:{version} -t myapp:latest .",
        description=f"Build Docker image with version {version}"
    ),
    BuildStep(
        name="tag_stable",
        command=f"docker tag myapp:{version} registry.example.com/myapp:{version}",
        description="Tag for registry"
    )
]

build_manager.register_build("docker_tagged", docker_build_steps)
```

## Multi-stage Builds

For multi-stage Dockerfiles:

```python
docker_build_steps = [
    BuildStep(
        name="build_stage1",
        command="docker build --target builder -t myapp:builder .",
        description="Build builder stage"
    ),
    BuildStep(
        name="build_final",
        command="docker build --target runtime -t myapp:latest .",
        description="Build final runtime stage"
    )
]

build_manager.register_build("docker_multistage", docker_build_steps)
```

## Build with Build Arguments

```python
docker_build_steps = [
    BuildStep(
        name="build_with_args",
        command="docker build --build-arg PYTHON_VERSION=3.11 --build-arg BUILD_DATE=$(date -u +'%Y-%m-%dT%H:%M:%SZ') -t myapp:latest .",
        description="Build with build arguments"
    )
]

build_manager.register_build("docker_with_args", docker_build_steps)
```

## Platform-Specific Builds

For multi-platform builds (e.g., ARM64, AMD64):

```python
docker_build_steps = [
    BuildStep(
        name="buildx_setup",
        command="docker buildx create --use --name multiarch",
        description="Create buildx builder",
        condition_command="docker buildx inspect multiarch || true"
    ),
    BuildStep(
        name="build_multiarch",
        command="docker buildx build --platform linux/amd64,linux/arm64 -t myapp:latest --push .",
        description="Build for multiple platforms"
    )
]

build_manager.register_build("docker_multiarch", docker_build_steps)
```

## Build with Cache Optimization

```python
docker_build_steps = [
    BuildStep(
        name="build_with_cache",
        command="docker build --cache-from myapp:latest -t myapp:latest .",
        description="Build using cache from previous image"
    )
]

build_manager.register_build("docker_cached", docker_build_steps)
```

## Configuration via JSON

```json
{
  "builds": {
    "docker_image": {
      "steps": [
        {
          "name": "validate_dockerfile",
          "command": "docker buildx du --dry-run .",
          "working_directory": "."
        },
        {
          "name": "build_image",
          "command": "docker build -t myapp:{{ version }} .",
          "working_directory": ".",
          "timeout": 600,
          "environment": {
            "DOCKER_BUILDKIT": "1"
          }
        }
      ],
      "dependencies": ["docker"]
    }
  }
}
```

## Environment Variables

```bash
export CODOMYRMEX_BUILD_DOCKER_REGISTRY="registry.example.com"
export CODOMYRMEX_BUILD_DOCKER_NAMESPACE="myorg"
export CODOMYRMEX_BUILD_TIMEOUT=600
export DOCKER_BUILDKIT=1  # Enable BuildKit
```

## Error Handling

```python
result = build_manager.execute_build("docker_image")

if not result.success:
    print(f"Error: {result.error_message}")
    print(f"Failed step: {result.failed_step}")

    # Check Docker-specific errors
    if "Cannot connect to the Docker daemon" in result.stderr:
        print("Docker daemon is not running. Start Docker first.")
    elif "Dockerfile not found" in result.stderr:
        print("Dockerfile not found in working directory.")
```

## Pushing to Registry

After building, push to a registry:

```python
docker_build_steps = [
    BuildStep(
        name="build_image",
        command="docker build -t myapp:latest ."
    ),
    BuildStep(
        name="login_registry",
        command="docker login -u $DOCKER_USER -p $DOCKER_PASSWORD registry.example.com",
        description="Login to Docker registry"
    ),
    BuildStep(
        name="push_image",
        command="docker push registry.example.com/myapp:latest",
        description="Push image to registry"
    )
]
```

## Best Practices

1. **Use .dockerignore**: Create a `.dockerignore` file to exclude unnecessary files
2. **Layer caching**: Order Dockerfile commands to maximize cache hits
3. **Security scanning**: Scan images for vulnerabilities before pushing
4. **Tag management**: Use semantic versioning for image tags
5. **Multi-stage builds**: Use multi-stage builds to reduce final image size
6. **Build context**: Minimize build context size for faster builds

## Integration with CI/CD

```python
import os
from codomyrmex.build_synthesis import BuildManager

# CI/CD environment
os.environ['DOCKER_BUILDKIT'] = '1'
os.environ['VERSION'] = os.environ.get('CI_COMMIT_TAG', 'latest')

build_manager = BuildManager()
result = build_manager.execute_build("docker_image")

if result.success:
    # Push to registry
    push_result = build_manager.execute_build("docker_push")
    if not push_result.success:
        raise Exception(f"Push failed: {push_result.error_message}")
else:
    raise Exception(f"Build failed: {result.error_message}")
```

## Troubleshooting

**Issue**: Cannot connect to Docker daemon
- **Solution**: Ensure Docker daemon is running: `docker info`

**Issue**: Permission denied
- **Solution**: Add user to docker group or use `sudo` (not recommended for automation)

**Issue**: Build context too large
- **Solution**: Use `.dockerignore` to exclude large files/directories

**Issue**: Build times out
- **Solution**: Increase timeout or optimize Dockerfile

**Issue**: Out of disk space
- **Solution**: Clean up unused images: `docker system prune -a`

## Security Considerations

1. **Secrets**: Never hardcode secrets in Dockerfiles or build commands
2. **Base images**: Use official, minimal base images
3. **User permissions**: Run containers as non-root when possible
4. **Scanning**: Regularly scan images for vulnerabilities
5. **Multi-stage**: Use multi-stage builds to reduce attack surface

## Next Steps

- See [Python Wheel Build Tutorial](./python_wheel_build_tutorial.md) for package builds
- Review [Build Orchestration](../technical_overview.md) for advanced usage
- Check [Security Documentation](../../SECURITY.md) for security best practices


## Navigation Links

- **Parent**: [Project Overview](../README.md)
- **Module Index**: [All Agents](../../AGENTS.md)
- **Documentation**: [Reference Guides](../../README.md)
- **Home**: [Root README](../../README.md)
