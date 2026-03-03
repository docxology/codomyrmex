# Image Module - Agent Guide

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Purpose

Provides Secure Cognitive Agents with visual capabilities including image processing, analysis, and generation.

## Agent Guidelines

1. **Format Safety**: Always validate image headers before processing to prevent format spoofing attacks.
2. **Resource Management**: Large images consume significant memory. Use streaming or chunked processing when possible.
3. **Privacy**: Strip EXIF metadata and hidden data streams from user-provided images before analysis or storage.

## PAI Agent Role Access Matrix

| PAI Agent | Access Level | Primary Capabilities | Trust Level |
|-----------|-------------|---------------------|-------------|
| **Engineer** | Full | Direct Python import, class instantiation, full API access | TRUSTED |
| **Architect** | Read + Design | API review, interface design, dependency analysis | OBSERVED |
| **QATester** | Validation | Integration testing via pytest, output validation | OBSERVED |
