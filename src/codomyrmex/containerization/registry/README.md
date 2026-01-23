# Registry Submodule

Container registry management for pushing and pulling images.

## Usage

```python
from codomyrmex.containerization.registry import ContainerRegistry
registry = ContainerRegistry("docker.io")
registry.push("myapp:latest")
```
