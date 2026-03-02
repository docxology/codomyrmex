# Semantic Router -- Agent Integration Guide

## Module Purpose

Provides embedding-based intent routing for AI agents that need to classify user inputs into named categories without training a full classifier.

## MCP Tools

| Tool | Description | Inputs | Output |
|------|-------------|--------|--------|
| `semantic_router_route` | Route text to best matching route | `text, routes, embedding_dim` | `{route_name, score, matched, all_routes}` |

## Agent Use Cases

### Intent Classification
An agent can use `semantic_router_route` to classify user queries into predefined categories (weather, help, greeting, etc.).

### Multi-Agent Dispatch
Route incoming requests to specialized agents based on semantic similarity to known intents.

### Fallback Detection
When no route matches above threshold, the agent knows to ask for clarification or use a general-purpose handler.

## Example Agent Workflow

```
1. Agent receives: "What will the temperature be tomorrow?"
2. Agent calls: semantic_router_route(text="What will the temperature be tomorrow?")
3. Response: {"route_name": "weather", "score": 0.92, "matched": true}
4. Agent dispatches to weather-handling sub-agent
```
