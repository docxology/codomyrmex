# Docker Submodule

Docker container and image management for containerization.

## Components

- `docker_manager.py` - Docker daemon interaction
- `build_generator.py` - Dockerfile generation
- `image_optimizer.py` - Image size optimization

## Usage

```python
from codomyrmex.containerization.docker import DockerManager
manager = DockerManager()
manager.build_image("./", "myapp:latest")
```
