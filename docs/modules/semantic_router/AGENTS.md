# Semantic Router -- Agent Coordination

**Version**: v1.1.4 | **Status**: Active | **Last Updated**: March 2026

## Overview

Provides embedding-based intent routing for natural language inputs. Routes text to predefined semantic categories using vector similarity matching against example utterances.

## MCP Tools

| Tool | Description | Trust Level | Category |
|------|-------------|-------------|----------|
| `semantic_router_route` | Route input text to the best matching semantic route | Standard | semantic_router |


## PAI Integration

| Algorithm Phase | Agent Role | Primary Operations |
|----------------|-----------|-------------------|
| EXECUTE | Engineer Agent | Route natural language inputs to appropriate handlers |
| BUILD | Architect Agent | Define semantic routes with example utterances for intent classification |


## Agent Instructions

1. Define routes with name, utterances list, and optional similarity threshold (default 0.7)
2. Default routes include weather, greeting, and help categories


## Navigation

- [Source README](../../src/codomyrmex/semantic_router/README.md) | [SPEC.md](SPEC.md)
