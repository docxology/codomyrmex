# Google Agents — Codomyrmex Integration

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Purpose

This section of the Codomyrmex workspace contains "thin orchestrated configurable" Python CLI scripts designed to leverage advanced capabilities of the Google GenAI SDK and Vertex AI, integrated securely within the Codomyrmex ecosystem. These tools provide single-call entry points for high-leverage workflows like RAG indexing, batch processing, multimodal analysis, and logic puzzle extraction using specialized Gemini models.

## Scripts Inventory

| Script | Purpose | Model | Key Features |
| :--- | :--- | :--- | :--- |
| `google_vision_analyzer.py` | Multimodal Processing | `gemini-2.5-pro` | Batch ingestion of PDFs/Images for OCR, diagramming, and task-specific reasoning. |
| `google_repo_indexer.py` | Codebase RAG Indexing | `text-embedding-004` | Parses repositories into semantic chunks, piping directly into Vertex Vector Search via High-throughput embeddings. |
| `google_reason_stream.py` | Thinking Budget Planner | `gemini-2.5-pro` | Exposes the `thinking_config` budget with live STDERR output, yielding verifiable constraint optimization and mathematical reasoning. |
| `google_batch_processor.py` | Serverless Batch Orchestrator | `gemini-1.5-pro` | Processes thousands of documents in sequence via asyncio semaphores without rate limiting, converting them structured JSON schemas. |

## Configuration & Usage

These scripts are built primarily to leverage the unified `google-genai` SDK.

**Standard Environment variables:**
```bash
export GEMINI_API_KEY="your-key"
```

**Vertex AI Enterprise (Preferred for large batch/caching):**
Run the interactive setup from repository root:
```bash
./scripts/gcp_vertex_setup.sh
```
This will automatically configure application-default login and prepare Vertex AI.

## Development Guidelines

1. **Zero-Mock Policy:** Follow the rules specified in `/AGENTS.md`. No logic mockups allowed; all dependencies and API calls must resolve to functional components.
2. **Thin Wrappers:** Logic should be contained to the specific orchestration capability (e.g., handling asynchronous semaphores, streaming output correctly from `types.Part.thought`). Business logic should be kept out.
3. **Execution Context:** All run via standard `argparse` from CLI. Compatible with Codomyrmex tools (`run_command`).
