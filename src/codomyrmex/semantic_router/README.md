# Semantic Router

Embedding-based intent routing that classifies user inputs to named routes using cosine similarity.

## Overview

The Semantic Router module provides:

- **Route**: Named intent with example utterances and a similarity threshold
- **RouteMatch**: Classification result with score and match status
- **SemanticRouter**: Core router that compares input embeddings against route examples

## Quick Start

```python
from codomyrmex.semantic_router import SemanticRouter, Route

router = SemanticRouter(embedding_dim=64)
router.add_route(Route(
    name="weather",
    utterances=["What is the weather?", "Will it rain?", "Temperature today?"],
    threshold=0.7,
))
router.add_route(Route(
    name="greeting",
    utterances=["Hello", "Hi there", "Good morning"],
    threshold=0.7,
))

result = router.route("How is the weather today?")
print(result.route_name)  # "weather"
print(result.score)       # cosine similarity score
print(result.matched)     # True
```

## Embedding Function

The default embedding uses a simple hash-based approach (deterministic, no external dependencies). For production use, replace `router._embed_fn` with a real embedding model.

## Dependencies

- `numpy` (core dependency)
- No external embedding libraries required (ships with hash-based fallback)
