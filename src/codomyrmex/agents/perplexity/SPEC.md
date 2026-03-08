# Perplexity Submodule - Functional Specification

**Version**: v1.1.9 | **Status**: Active | **Last Updated**: March 2026

## Purpose

To provide a concrete implementation of `APIAgentBase` targeting the Perplexity Search-Augmented Chat Completions API.

## Design

### Client Architecture

- Extends `APIAgentBase`.
- Standardized to use the `sonar` model series.
- Extracts standard fields (`choices[0].message.content`) alongside custom search `citations` returned in metadata.

### Methods

1. **`execute(request: AgentRequest) -> AgentResponse`**: Full payload POST via `requests`. Passes JSON body `{"messages": [{"role": "user", "content": prompt}], "model": model}`.
2. **`stream(request: AgentRequest) -> Iterator[str]`**: Parses Server-Sent Events (SSE) extracting `"delta"` deltas and handling `[DONE]` terminators according to the standard OpenAI-like streaming envelope used by Perplexity.

### Testing Standard

Zero-Mock. `TestPerplexityClient` verifies request building, connection test behavior missing/present keys, and executes a real query if keys are present globally.
