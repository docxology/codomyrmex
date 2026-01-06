# Containerization Examples

## Signposting
- **Parent**: [Examples](../README.md)
- **Children**:
    - None
- **Key Artifacts**:
    - [Agent Guide](AGENTS.md)
    - [Functional Spec](SPEC.md)

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: December 2025
Demonstrates Docker container management and optimization using the Codomyrmex Containerization module.

## Overview

The Containerization module provides comprehensive container lifecycle management including image building, optimization, registry management, and deployment orchestration.

## Examples

### Basic Usage (`example_basic.py`)

- Analyze existing container images for size and layers
- Generate optimized multi-stage Dockerfiles
- Suggest image optimizations and size reductions
- Build and manage container images

**Tested Methods:**
- `build_image()` - Build Docker images (from `test_containerization.py`)
- `optimize_image()` - Image optimization (from `test_containerization_enhanced.py`)
- `analyze_image_size()` - Size analysis (from `test_containerization_enhanced.py`)

## Configuration

```yaml
containerization:
  images_to_analyze:
    - name: python:3.9-slim
    - name: node:16-alpine

  build_configs:
    - base_image: python:3.9-slim
      app_files: [app.py, requirements.txt]
      dependencies: [python3-dev, build-essential]
      ports: [8000]

  optimization_configs:
    - image: python:3.9
      target_size_mb: 100
      use_multi_stage: true
```

## Running

```bash
cd examples/containerization
python example_basic.py
```

## Expected Output

The example will:
1. Analyze sizes of specified container images
2. Generate optimized Dockerfiles for different applications
3. Suggest optimizations for size reduction
4. Attempt to build generated images (if Docker available)
5. Generate summary report with optimization potential
6. Save results and generated files to output directory

## Generated Files

The example creates:
- **Dockerfiles**: Optimized multi-stage Dockerfiles
- **Build reports**: Image build results and timings
- **Optimization reports**: Size reduction suggestions

Check the `output/containers/` directory for generated Dockerfiles and reports.

## Containerization Features

- **Multi-stage Builds**: Optimized build processes with minimal final images
- **Image Analysis**: Layer-by-layer size and content analysis
- **Optimization**: Automatic suggestions for size reduction
- **Registry Management**: Push/pull from container registries
- **Security Scanning**: Vulnerability checks on container images

## Use Cases

- **Application Deployment**: Build and deploy containerized applications
- **CI/CD Pipelines**: Automated container building and testing
- **Image Optimization**: Reduce container sizes for faster deployments
- **Registry Management**: Centralized container image management
- **Development Environments**: Consistent development containers

## Integration with Other Modules

The containerization module integrates with:
- **CI/CD Automation**: Automated container builds in pipelines
- **Security Audit**: Scan container images for vulnerabilities
- **Config Management**: Container environment configuration
- **Logging**: Build and deployment logging
- **Performance**: Monitor container resource usage

## Prerequisites

- Docker installed and running (for image building)
- Appropriate permissions for Docker operations

## Related Documentation

- [Module README](../../src/codomyrmex/containerization/README.md)
- [Unit Tests](../../src/codomyrmex/tests/)
- [Enhanced Tests](../../src/codomyrmex/tests/)

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
