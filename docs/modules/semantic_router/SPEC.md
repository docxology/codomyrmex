# Semantic Router Specification

**Version**: v1.2.3 | **Status**: Active | **Last Updated**: March 2026

## Overview

Provides embedding-based intent routing for natural language inputs. Routes text to predefined semantic categories using vector similarity matching against example utterances.

## Functional Requirements

1. Route definition with name, example utterances, and configurable similarity threshold
2. Embedding-based semantic matching using vector similarity
3. RouteMatch result with route_name, score, and matched flag


## Interface

```python
from codomyrmex.semantic_router import SemanticRouter, Route, RouteMatch

router = SemanticRouter(embedding_dim=64)
router.add_route(Route(name="help", utterances=["I need help"], threshold=0.7))
result = router.route("Can you help me?")
print(result.route_name, result.score, result.matched)
```

## Exports

SemanticRouter, Route, RouteMatch

## Navigation

- [Source README](../../src/codomyrmex/semantic_router/README.md) | [AGENTS.md](AGENTS.md)
