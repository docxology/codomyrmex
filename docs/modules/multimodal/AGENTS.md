# Multimodal Module — Agent Coordination

## Purpose

Vision and audio processing for multimodal AI applications.

## Key Capabilities

- **MediaType**: Types of media.
- **ImageFormat**: Supported image formats.
- **AudioFormat**: Supported audio formats.
- **MediaContent**: Container for media content.
- **ImageContent**: Image-specific content.
- `size_bytes()`: Get content size in bytes.
- `hash()`: Get content hash.
- `to_base64()`: Convert to base64 string.

## Agent Usage Patterns

```python
from codomyrmex.multimodal import MediaType

# Agent initializes multimodal
instance = MediaType()
```

## Integration Points

- **Source**: [src/codomyrmex/multimodal/](../../../src/codomyrmex/multimodal/)
- **Docs**: [Module Documentation](README.md)
- **Spec**: [Technical Specification](SPEC.md)

## Testing Guidelines

```bash
uv run python -m pytest src/codomyrmex/tests/ -k multimodal -v
```

- Run tests before and after making changes.
- Ensure all existing tests pass before submitting.
