# Image Module

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

Image processing and generation capabilities for Secure Cognitive Agents.

## Overview

The image module provides robust utilities for programmatic image manipulation, computer vision tasks, and integration with generative image models. It serves as the primary interface for PAI agents to "see" and "create" visual content.

## Features

- **Image Processing**: Common transformations, filters, and color operations
- **Format Conversion**: Safe transcoding between popular image formats
- **Computer Vision**: Feature extraction and pattern detection
- **Generative Integration**: Interfaces for text-to-image models
- **MCP Tools**: Ready-to-use Model Context Protocol endpoints for visual tasks

## Installation

```bash
uv add codomyrmex[image]
```

## Usage

Agents can leverage the image tools via direct import or MCP:

```python
from codomyrmex.image import ImageProcessor

processor = ImageProcessor()
result = processor.resize("input.jpg", width=800, height=600)
```

## Documentation

- [Agent Guide](AGENTS.md)
- [Technical Specification](SPEC.md)
