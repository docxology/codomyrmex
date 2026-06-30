# Multimodal - API Specification

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## 1. Overview
The `multimodal` module handles various media types with a focus on image generation. Provides a unified interface for generating images from prompts.

## 2. Core Components

### 2.1 Classes

| Class | Description |
|-------|-------------|
| `ImageGenerator` | Generate images from text prompts, supporting multiple backends |

## 3. Related Modules

| Module | Relationship |
|--------|-------------|
| `image` | Reserved namespace for image metadata extraction |
| `vision` | Visual analysis via VLM (Ollama llava/bakllava) |

## 4. Usage Example

```python
from codomyrmex.multimodal import ImageGenerator

gen = ImageGenerator()
result = gen.generate("A futuristic city at sunset")
result.save("output.png")
```

## 5. Navigation

- [README](README.md) | [SPEC](SPEC.md) | [AGENTS](AGENTS.md) | [PAI](PAI.md)
