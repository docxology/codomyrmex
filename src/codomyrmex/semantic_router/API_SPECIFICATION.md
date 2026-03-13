# Semantic Router - API Specification

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## 1. Overview
The `semantic_router` module provides embedding-based intent routing. Maps user queries to predefined routes using semantic similarity, enabling routing decisions without keyword matching.

## 2. Core Components

### 2.1 Classes

| Class | Description |
|-------|-------------|
| `SemanticRouter` | Main router that matches queries against registered routes |
| `Route` | A named route with example utterances and metadata |
| `RouteMatch` | Result of a routing decision (route name, confidence score) |

## 3. Usage Example

```python
from codomyrmex.semantic_router import SemanticRouter, Route

router = SemanticRouter()
router.add_route(Route(
    name="weather",
    utterances=["What's the weather?", "Is it raining?", "Temperature today"],
))
router.add_route(Route(
    name="calendar",
    utterances=["What's on my schedule?", "Book a meeting", "Next appointment"],
))

match = router.route("Will it rain tomorrow?")
print(f"Route: {match.name}, Score: {match.score:.3f}")
```

## 4. Navigation

- [README](README.md) | [SPEC](SPEC.md) | [AGENTS](AGENTS.md) | [PAI](PAI.md)
