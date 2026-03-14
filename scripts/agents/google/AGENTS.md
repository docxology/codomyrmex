# Codomyrmex Scripts Agents Google Coordination

**Parent**: [`scripts/agents/AGENTS.md`](../AGENTS.md)
**Focus**: Google AI Integration Scripts

## Protocol Directives

1. **SDK Preference**: All scripts MUST rely on the unified `google-genai` SDK (`from google import genai`) rather than the legacy `google-generativeai` SDK.
2. **Vertex AI Interop**: Scripts MUST support seamless fallback/promotion to Vertex AI (`genai.Client(vertexai=True)`) if environment variables (`GOOGLE_CLOUD_PROJECT`, `GOOGLE_CLOUD_LOCATION`) or `gcloud auth application-default` are available. This is crucial for enabling 1M+ token scaling and enterprise quotas.
3. **Modularity**: Avoid pulling excessive business logic into these scripts. They are intended as *thin orchestration layers* (e.g. chunking files to invoke batch embeddings, streaming JSON outputs).
4. **Data Privacy**: Scripts must honor the data boundary. Never log model context keys or user credentials in the outputs. Use `codomyrmex.logging_monitoring`.

## Cross-Referencing
Refer to the `Personal AI Infrastructure (PAI)` standards for the exact CLI wrapping expectations for tools executed by agent orchestration arrays.
