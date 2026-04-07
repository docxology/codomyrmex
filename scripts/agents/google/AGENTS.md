# Codomyrmex Scripts Agents Google Coordination

**Parent**: [`scripts/agents/AGENTS.md`](../AGENTS.md)
**Focus**: Google AI Integration Scripts

## Purpose

Thin orchestration scripts for Google AI (unified `google-genai` SDK, optional Vertex AI). See [README.md](README.md) for invocation examples.

## Key Files

| File | Role |
|:---|:---|
| [README.md](README.md) | Flags, env vars, usage |
| `google_batch_processor.py` | Batch / embedding style workflows |
| `google_reason_stream.py` | Streaming reasoning helpers |
| `google_repo_indexer.py` | Repo indexing |
| `google_vision_analyzer.py` | Vision analysis |

## Dependencies

- `google-genai` (`from google import genai`); avoid legacy `google-generativeai`.
- Optional Vertex: `GOOGLE_CLOUD_PROJECT`, `GOOGLE_CLOUD_LOCATION`, ADC via `gcloud auth application-default`.
- Parent hub: [scripts/agents/AGENTS.md](../AGENTS.md).

## Protocol Directives

1. **SDK Preference**: All scripts MUST rely on the unified `google-genai` SDK (`from google import genai`) rather than the legacy `google-generativeai` SDK.
2. **Vertex AI Interop**: Scripts MUST support seamless fallback/promotion to Vertex AI (`genai.Client(vertexai=True)`) if environment variables (`GOOGLE_CLOUD_PROJECT`, `GOOGLE_CLOUD_LOCATION`) or `gcloud auth application-default` are available. This is crucial for enabling 1M+ token scaling and enterprise quotas.
3. **Modularity**: Avoid pulling excessive business logic into these scripts. They are intended as *thin orchestration layers* (e.g. chunking files to invoke batch embeddings, streaming JSON outputs).
4. **Data Privacy**: Scripts must honor the data boundary. Never log model context keys or user credentials in the outputs. Use `codomyrmex.logging_monitoring`.

## Cross-Referencing
Refer to the `Personal AI Infrastructure (PAI)` standards for the exact CLI wrapping expectations for tools executed by agent orchestration arrays.
