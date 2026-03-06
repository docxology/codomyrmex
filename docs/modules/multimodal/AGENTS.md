# Multimodal -- Agent Coordination

**Version**: v1.1.6 | **Status**: Active | **Last Updated**: March 2026

## Overview

Provides multimodal processing capabilities including image generation via Google AI (Imagen 3). Handles various media types for multi-modal AI workflows.

## MCP Tools

No MCP tools defined for this module.

## PAI Integration

| Algorithm Phase | Agent Role | Primary Operations |
|----------------|-----------|-------------------|
| BUILD | Engineer Agent | Generate images and other media as part of multimodal pipelines |
| EXECUTE | Infrastructure Agent | Process multimodal inputs for AI model consumption |


## Agent Instructions

1. Requires GEMINI_API_KEY environment variable for live image generation
2. Use ImageGenerator for text-to-image generation via Google AI


## Navigation

- [Source README](../../src/codomyrmex/multimodal/README.md) | [SPEC.md](SPEC.md)
