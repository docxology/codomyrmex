# Multimodal Module -- Agent Integration Guide

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## What Agents Can Do With This Module

The multimodal module provides image generation capabilities via Google AI's Imagen 3 model. Agents can generate images from text prompts for documentation, reports, data augmentation, and visual content creation workflows.

### Capabilities

| Capability | Class / Function | Description |
|------------|-----------------|-------------|
| Text-to-image generation | `ImageGenerator.generate()` | Generate images from natural language prompts |
| Model selection | `ImageGenerator.generate(model=...)` | Choose specific Imagen model versions |
| Batch generation | `ImageGenerator.generate(number_of_images=N)` | Generate multiple images per prompt |
| Aspect ratio control | `ImageGenerator.generate(aspect_ratio=...)` | Control output image dimensions |

## Available MCP Tools

No MCP tools. This module does not have an `mcp_tools.py` and is not auto-discovered via the MCP bridge. Agents must call `ImageGenerator` directly from Python.

## Agent Workflow Patterns

### Pattern 1: Documentation Illustration

```python
from codomyrmex.multimodal import ImageGenerator

generator = ImageGenerator()
images = generator.generate(
    prompt="Architecture diagram showing microservice communication",
    number_of_images=1,
    aspect_ratio="16:9",
)
```

### Pattern 2: Batch Visual Content

```python
prompts = [
    "A clean terminal interface with syntax highlighting",
    "A network topology diagram with three nodes",
]
for prompt in prompts:
    images = generator.generate(prompt=prompt, number_of_images=2)
```

## PAI Agent Role Access Matrix

| PAI Agent | Access Level | Capabilities | Trust Level |
|-----------|-------------|-------------|-------------|
| **Engineer** | Full | `ImageGenerator.generate()` -- create images for builds, documentation, visual assets | TRUSTED |
| **Architect** | Read + Design | Review image generation parameters, plan visual content strategies | OBSERVED |
| **QATester** | Validation | Verify image generation succeeds with given prompts, validate output format | OBSERVED |
| **Researcher** | Read-only | Inspect available models and parameters | SAFE |

### Engineer Agent
**Access**: Full -- generate images, configure models, set generation parameters.
**Use Cases**: Creating visual assets during BUILD phase, generating documentation illustrations, producing diagrams for technical reports.

### Architect Agent
**Access**: Read + Design -- review generation capabilities, plan visual workflows.
**Use Cases**: Designing content pipelines that include image generation, evaluating Imagen model options for project needs.

### QATester Agent
**Access**: Validation -- test generation with sample prompts, verify output structure.
**Use Cases**: Validating that image generation returns expected dictionary format, testing error handling for invalid prompts or missing API keys.

### Researcher Agent
**Access**: Read-only -- query available models and parameters.
**Use Cases**: Documenting image generation capabilities, cataloging supported aspect ratios and model versions.

## Integration with PAI Algorithm Phases

| Phase | Usage | Description |
|-------|-------|-------------|
| BUILD | `ImageGenerator.generate()` | Create visual content as part of deliverables |
| EXECUTE | `ImageGenerator.generate()` | Run image generation tasks in automated workflows |

## Environment Requirements

| Variable | Required | Description |
|----------|----------|-------------|
| `GEMINI_API_KEY` | Yes | Google AI API key for Imagen 3 access |

## Security Constraints

1. API key must be provided via environment variable, never hardcoded.
2. Generated images are returned as in-memory dictionaries; agents should handle storage explicitly.
3. All generation calls require network access to the Google AI API.

## Navigation Links

- **Parent Directory**: [codomyrmex](../README.md)
- **Project Root**: [README.md](../../../README.md)
- **Module README**: [README.md](README.md)
- **PAI Integration**: [PAI.md](PAI.md)
