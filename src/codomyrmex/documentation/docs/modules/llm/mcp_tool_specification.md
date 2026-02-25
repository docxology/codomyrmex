# LLM Module - MCP Tool Specification

This document defines the Model Context Protocol (MCP) tools for the `llm` module, which provides comprehensive Large Language Model integration including local model management (Ollama), multi-provider support, embeddings, RAG, guardrails, and cost tracking.

## General Considerations for LLM Tools

- **Dependencies**: Requires `logging_monitoring` module. External dependencies vary by provider (openai, anthropic SDKs). Ollama requires local installation.
- **Initialization**: Provider-specific clients initialized on first use. Ollama server may auto-start.
- **Error Handling**: Errors logged via `logging_monitoring`. Provider-specific errors wrapped in standardized format.
- **Security**: API keys read from environment or config. Prompts/responses may be logged (configurable). PII detection available via guardrails.

---

## Tool: `llm_complete`

### 1. Tool Purpose and Description

Generates text completions using configured LLM providers (OpenAI, Anthropic, Ollama, etc.). Supports chat-style multi-turn conversations with system prompts, streaming, and tool calling.

### 2. Invocation Name

`llm_complete`

### 3. Input Schema (Parameters)

| Parameter Name | Type | Required | Description | Example Value |
|:--------------|:-----|:---------|:------------|:--------------|
| `messages` | `array[object]` | Yes | Conversation messages | See below |
| `messages[].role` | `enum["system", "user", "assistant", "tool"]` | Yes | Message role | `"user"` |
| `messages[].content` | `string` | Yes | Message content | `"Explain quantum computing"` |
| `provider` | `enum["openai", "anthropic", "ollama", "google", "mistral"]` | No | LLM provider. Default: "openai" | `"anthropic"` |
| `model` | `string` | No | Specific model. Default: provider default | `"claude-3-5-sonnet-20241022"` |
| `temperature` | `float` | No | Sampling temperature (0-2). Default: 0.7 | `0.5` |
| `max_tokens` | `integer` | No | Maximum response tokens. Default: provider default | `2048` |
| `stream` | `boolean` | No | Enable streaming response. Default: false | `false` |

### 4. Output Schema (Return Value)

| Field Name | Type | Description | Example Value |
|:-----------|:-----|:------------|:--------------|
| `success` | `boolean` | Whether completion succeeded | `true` |
| `content` | `string` | Generated response text | `"Quantum computing uses..."` |
| `model` | `string` | Model used for generation | `"gpt-4o"` |
| `provider` | `string` | Provider used | `"openai"` |
| `finish_reason` | `string` | Why generation stopped | `"stop"` |
| `usage` | `object` | Token usage statistics | See below |
| `usage.prompt_tokens` | `integer` | Input tokens | `125` |
| `usage.completion_tokens` | `integer` | Output tokens | `456` |
| `usage.total_tokens` | `integer` | Total tokens | `581` |
| `tool_calls` | `array[object]` | Tool calls requested (if any) | `null` |

### 5. Error Handling

- `ProviderError`: Provider API unavailable or returned error
- `AuthenticationError`: Invalid or missing API key
- `RateLimitError`: Provider rate limit exceeded
- `ModelNotFoundError`: Specified model not available
- Return Format: `{"success": false, "error": "Completion failed: <details>", "error_type": "rate_limit"}`

### 6. Idempotency

- **Idempotent**: No
- **Explanation**: LLM outputs are stochastic. Temperature=0 increases consistency but does not guarantee identical outputs.

### 7. Usage Examples (for MCP context)

```json
{
  "tool_name": "llm_complete",
  "arguments": {
    "messages": [
      {"role": "system", "content": "You are a helpful coding assistant."},
      {"role": "user", "content": "Write a Python function to calculate Fibonacci numbers"}
    ],
    "provider": "anthropic",
    "model": "claude-3-5-sonnet-20241022",
    "temperature": 0.3,
    "max_tokens": 1024
  }
}
```

### 8. Security Considerations

- **Input Validation**: Messages validated for structure. Content checked via guardrails if enabled.
- **Permissions**: Requires valid API key for chosen provider.
- **Data Handling**: Prompts and responses sent to external providers. Do not include secrets in prompts.
- **Rate Limiting**: Respect provider rate limits; implement exponential backoff.

---

## Tool: `llm_ollama_run`

### 1. Tool Purpose and Description

Runs inference on locally-hosted Ollama models. Provides privacy-preserving local execution with no data sent to external services.

### 2. Invocation Name

`llm_ollama_run`

### 3. Input Schema (Parameters)

| Parameter Name | Type | Required | Description | Example Value |
|:--------------|:-----|:---------|:------------|:--------------|
| `model_name` | `string` | Yes | Ollama model to run | `"llama3:8b"` |
| `prompt` | `string` | Yes | Input prompt | `"Explain neural networks"` |
| `system_prompt` | `string` | No | System instruction | `"You are a teacher"` |
| `options` | `object` | No | Model options | See below |
| `options.temperature` | `float` | No | Sampling temperature. Default: 0.8 | `0.5` |
| `options.top_p` | `float` | No | Top-p sampling. Default: 0.9 | `0.95` |
| `options.num_predict` | `integer` | No | Max tokens to generate. Default: 2048 | `1024` |
| `save_output` | `boolean` | No | Save output to file. Default: false | `true` |
| `output_dir` | `string` | No | Directory for saved outputs | `"./outputs/ollama/"` |

### 4. Output Schema (Return Value)

| Field Name | Type | Description | Example Value |
|:-----------|:-----|:------------|:--------------|
| `success` | `boolean` | Whether execution succeeded | `true` |
| `model_name` | `string` | Model used | `"llama3:8b"` |
| `prompt` | `string` | Input prompt | `"Explain neural networks"` |
| `response` | `string` | Generated response | `"Neural networks are..."` |
| `execution_time` | `float` | Generation time in seconds | `3.45` |
| `tokens_used` | `integer` | Approximate tokens generated | `256` |
| `error_message` | `string` | Error details if failed | `null` |
| `metadata` | `object` | Additional execution metadata | `{"api_method": "http"}` |

### 5. Error Handling

- `ModelNotAvailableError`: Model not downloaded to Ollama
- `ServerNotRunningError`: Ollama server not running
- `TimeoutError`: Generation exceeded timeout
- Return Format: `{"success": false, "error": "Ollama execution failed: <details>"}`

### 6. Idempotency

- **Idempotent**: No
- **Explanation**: LLM outputs are stochastic even with same inputs.

### 7. Usage Examples (for MCP context)

```json
{
  "tool_name": "llm_ollama_run",
  "arguments": {
    "model_name": "codellama:13b",
    "prompt": "Write a Python function to parse JSON safely",
    "system_prompt": "You are an expert Python developer. Write clean, well-documented code.",
    "options": {
      "temperature": 0.3,
      "num_predict": 512
    }
  }
}
```

### 8. Security Considerations

- **Input Validation**: Model name validated against available models.
- **Permissions**: Local execution only; no external API calls.
- **Data Handling**: All data remains local. Output files created in specified directory.
- **File Paths**: Output directory validated and sandboxed.

---

## Tool: `llm_ollama_list_models`

### 1. Tool Purpose and Description

Lists all Ollama models available locally, including model metadata such as size, parameter count, and family.

### 2. Invocation Name

`llm_ollama_list_models`

### 3. Input Schema (Parameters)

| Parameter Name | Type | Required | Description | Example Value |
|:--------------|:-----|:---------|:------------|:--------------|
| `force_refresh` | `boolean` | No | Force refresh of cached model list. Default: false | `true` |

### 4. Output Schema (Return Value)

| Field Name | Type | Description | Example Value |
|:-----------|:-----|:------------|:--------------|
| `success` | `boolean` | Whether listing succeeded | `true` |
| `models` | `array[object]` | Available models | See below |
| `models[].name` | `string` | Model name | `"llama3:8b"` |
| `models[].id` | `string` | Model digest ID | `"abc123def456"` |
| `models[].size` | `integer` | Size in bytes | `4500000000` |
| `models[].size_gb` | `float` | Size in GB | `4.5` |
| `models[].modified` | `string` | Last modified date | `"2026-01-15"` |
| `models[].parameters` | `string` | Parameter size | `"8B"` |
| `models[].family` | `string` | Model family | `"llama"` |
| `total_count` | `integer` | Total models available | `5` |
| `total_size_gb` | `float` | Total storage used | `25.3` |

### 5. Error Handling

- `ServerNotRunningError`: Ollama server not running
- Return Format: `{"success": false, "error": "Failed to list models: <details>"}`

### 6. Idempotency

- **Idempotent**: Yes
- **Explanation**: Read-only query of available models.

### 7. Usage Examples (for MCP context)

```json
{
  "tool_name": "llm_ollama_list_models",
  "arguments": {
    "force_refresh": true
  }
}
```

### 8. Security Considerations

- **Input Validation**: No user-supplied paths or code.
- **Permissions**: Read-only access to Ollama API.
- **Data Handling**: Model metadata only; no sensitive data.

---

## Tool: `llm_ollama_pull_model`

### 1. Tool Purpose and Description

Downloads (pulls) a model from the Ollama library to local storage. Large models may take significant time to download.

### 2. Invocation Name

`llm_ollama_pull_model`

### 3. Input Schema (Parameters)

| Parameter Name | Type | Required | Description | Example Value |
|:--------------|:-----|:---------|:------------|:--------------|
| `model_name` | `string` | Yes | Model to download | `"llama3:70b"` |

### 4. Output Schema (Return Value)

| Field Name | Type | Description | Example Value |
|:-----------|:-----|:------------|:--------------|
| `success` | `boolean` | Whether download completed | `true` |
| `model_name` | `string` | Downloaded model | `"llama3:70b"` |
| `message` | `string` | Status message | `"Model downloaded successfully"` |

### 5. Error Handling

- `ModelNotFoundError`: Model does not exist in Ollama library
- `DiskSpaceError`: Insufficient disk space
- `NetworkError`: Download failed due to network issues
- Return Format: `{"success": false, "error": "Model pull failed: <details>"}`

### 6. Idempotency

- **Idempotent**: Yes
- **Explanation**: Re-downloading an existing model is a no-op (model already present).

### 7. Usage Examples (for MCP context)

```json
{
  "tool_name": "llm_ollama_pull_model",
  "arguments": {
    "model_name": "codellama:34b"
  }
}
```

### 8. Security Considerations

- **Input Validation**: Model name validated against Ollama library format.
- **Permissions**: Requires write access to Ollama model directory.
- **Data Handling**: Model downloaded from Ollama registry (ollama.com).
- **Network**: Requires internet access during download.

---

## Tool: `llm_embed`

### 1. Tool Purpose and Description

Generates text embeddings (vector representations) for semantic search, similarity matching, and RAG applications. Supports multiple embedding providers and models.

### 2. Invocation Name

`llm_embed`

### 3. Input Schema (Parameters)

| Parameter Name | Type | Required | Description | Example Value |
|:--------------|:-----|:---------|:------------|:--------------|
| `text` | `string` | Yes (if texts not provided) | Single text to embed | `"Machine learning is..."` |
| `texts` | `array[string]` | Yes (if text not provided) | Multiple texts to embed | `["text1", "text2"]` |
| `model` | `enum["text-embedding-ada-002", "text-embedding-3-small", "text-embedding-3-large"]` | No | Embedding model. Default: "text-embedding-3-small" | `"text-embedding-3-large"` |
| `use_cache` | `boolean` | No | Use embedding cache. Default: true | `true` |

### 4. Output Schema (Return Value)

| Field Name | Type | Description | Example Value |
|:-----------|:-----|:------------|:--------------|
| `success` | `boolean` | Whether embedding succeeded | `true` |
| `embeddings` | `array[object]` | Generated embeddings | See below |
| `embeddings[].vector` | `array[float]` | Embedding vector | `[0.023, -0.045, ...]` |
| `embeddings[].text` | `string` | Source text | `"Machine learning is..."` |
| `embeddings[].dimensions` | `integer` | Vector dimensions | `1536` |
| `model` | `string` | Model used | `"text-embedding-3-small"` |
| `cache_hits` | `integer` | Embeddings retrieved from cache | `1` |
| `api_calls` | `integer` | New API calls made | `1` |

### 5. Error Handling

- `ProviderError`: Embedding API unavailable
- `InputTooLongError`: Text exceeds model's token limit
- Return Format: `{"success": false, "error": "Embedding failed: <details>"}`

### 6. Idempotency

- **Idempotent**: Yes
- **Explanation**: Same text produces identical embedding vectors.

### 7. Usage Examples (for MCP context)

```json
{
  "tool_name": "llm_embed",
  "arguments": {
    "texts": [
      "Codomyrmex is a modular development platform",
      "Machine learning enables intelligent automation"
    ],
    "model": "text-embedding-3-small",
    "use_cache": true
  }
}
```

### 8. Security Considerations

- **Input Validation**: Text length validated against model limits.
- **Permissions**: Requires API key for embedding provider.
- **Data Handling**: Text sent to external API for embedding.
- **Caching**: Cached embeddings stored locally; clear cache if processing sensitive data.

---

## Tool: `llm_similarity_search`

### 1. Tool Purpose and Description

Performs semantic similarity search against an embedding index. Finds the most similar documents/chunks to a query using cosine similarity.

### 2. Invocation Name

`llm_similarity_search`

### 3. Input Schema (Parameters)

| Parameter Name | Type | Required | Description | Example Value |
|:--------------|:-----|:---------|:------------|:--------------|
| `query` | `string` | Yes | Search query text | `"How do I execute code safely?"` |
| `index_name` | `string` | No | Named index to search. Default: "default" | `"documentation"` |
| `k` | `integer` | No | Number of results. Default: 5 | `10` |
| `threshold` | `float` | No | Minimum similarity score (0-1). Default: none | `0.7` |

### 4. Output Schema (Return Value)

| Field Name | Type | Description | Example Value |
|:-----------|:-----|:------------|:--------------|
| `success` | `boolean` | Whether search succeeded | `true` |
| `results` | `array[object]` | Similar items found | See below |
| `results[].text` | `string` | Matched text content | `"The coding module provides..."` |
| `results[].score` | `float` | Similarity score (0-1) | `0.89` |
| `results[].rank` | `integer` | Result ranking | `1` |
| `results[].metadata` | `object` | Associated metadata | `{"source": "README.md"}` |
| `total_searched` | `integer` | Items in index | `1250` |
| `query_embedding_time_ms` | `float` | Time to embed query | `45.2` |
| `search_time_ms` | `float` | Time to search index | `12.3` |

### 5. Error Handling

- `IndexNotFoundError`: Specified index does not exist
- `EmbeddingError`: Failed to embed query
- Return Format: `{"success": false, "error": "Search failed: <details>"}`

### 6. Idempotency

- **Idempotent**: Yes
- **Explanation**: Same query produces same results (given unchanged index).

### 7. Usage Examples (for MCP context)

```json
{
  "tool_name": "llm_similarity_search",
  "arguments": {
    "query": "How do I run code in a Docker container?",
    "index_name": "codomyrmex-docs",
    "k": 5,
    "threshold": 0.6
  }
}
```

### 8. Security Considerations

- **Input Validation**: Query text validated and embedded securely.
- **Permissions**: Read access to embedding index.
- **Data Handling**: Query sent to embedding provider; results from local index.

---

## Tool: `llm_rag_query`

### 1. Tool Purpose and Description

Performs Retrieval-Augmented Generation (RAG): retrieves relevant context from an index and generates a response grounded in that context. Reduces hallucination by providing factual grounding.

### 2. Invocation Name

`llm_rag_query`

### 3. Input Schema (Parameters)

| Parameter Name | Type | Required | Description | Example Value |
|:--------------|:-----|:---------|:------------|:--------------|
| `query` | `string` | Yes | User question | `"How do I configure Ollama?"` |
| `index_name` | `string` | No | Document index to search. Default: "default" | `"docs"` |
| `k` | `integer` | No | Number of context chunks. Default: 5 | `3` |
| `provider` | `string` | No | LLM provider for generation. Default: "openai" | `"anthropic"` |
| `model` | `string` | No | Model for generation | `"gpt-4o"` |
| `include_sources` | `boolean` | No | Include source references. Default: true | `true` |

### 4. Output Schema (Return Value)

| Field Name | Type | Description | Example Value |
|:-----------|:-----|:------------|:--------------|
| `success` | `boolean` | Whether RAG completed | `true` |
| `answer` | `string` | Generated answer | `"To configure Ollama, you..."` |
| `sources` | `array[object]` | Context chunks used | See below |
| `sources[].text` | `string` | Source text | `"Ollama configuration..."` |
| `sources[].score` | `float` | Relevance score | `0.92` |
| `sources[].document_id` | `string` | Source document | `"ollama-readme"` |
| `context_used` | `string` | Full context provided to LLM | `"Source 1:..."` |
| `retrieval_time_ms` | `float` | Time for retrieval | `89.4` |
| `generation_time_ms` | `float` | Time for generation | `1234.5` |

### 5. Error Handling

- `IndexNotFoundError`: Document index not available
- `GenerationError`: LLM generation failed
- Return Format: `{"success": false, "error": "RAG query failed: <details>"}`

### 6. Idempotency

- **Idempotent**: No
- **Explanation**: LLM generation is stochastic. Retrieval is deterministic.

### 7. Usage Examples (for MCP context)

```json
{
  "tool_name": "llm_rag_query",
  "arguments": {
    "query": "What security measures does the coding module use for code execution?",
    "index_name": "codomyrmex-docs",
    "k": 4,
    "provider": "anthropic",
    "model": "claude-3-5-sonnet-20241022",
    "include_sources": true
  }
}
```

### 8. Security Considerations

- **Input Validation**: Query sanitized before retrieval and generation.
- **Permissions**: Requires access to index and LLM provider.
- **Data Handling**: Retrieved context sent to LLM provider.
- **Grounding**: Responses grounded in retrieved context to reduce hallucination.

---

## Tool: `llm_check_guardrails`

### 1. Tool Purpose and Description

Validates input/output against safety guardrails including prompt injection detection, PII detection, and content filtering. Essential for production LLM applications.

### 2. Invocation Name

`llm_check_guardrails`

### 3. Input Schema (Parameters)

| Parameter Name | Type | Required | Description | Example Value |
|:--------------|:-----|:---------|:------------|:--------------|
| `text` | `string` | Yes | Text to check | `"Ignore previous instructions..."` |
| `check_type` | `enum["input", "output", "both"]` | No | Type of check. Default: "input" | `"input"` |
| `checks` | `array[enum["injection", "pii", "content", "length"]]` | No | Specific checks. Default: all | `["injection", "pii"]` |
| `sanitize` | `boolean` | No | Sanitize PII if detected. Default: false | `true` |

### 4. Output Schema (Return Value)

| Field Name | Type | Description | Example Value |
|:-----------|:-----|:------------|:--------------|
| `success` | `boolean` | Whether checks completed | `true` |
| `passed` | `boolean` | Whether all checks passed | `false` |
| `is_safe` | `boolean` | Whether content is safe to proceed | `false` |
| `threat_level` | `enum["none", "low", "medium", "high", "critical"]` | Detected threat level | `"high"` |
| `action` | `enum["allow", "warn", "block", "sanitize"]` | Recommended action | `"block"` |
| `threats_detected` | `array[string]` | List of detected threats | `["Prompt injection pattern detected"]` |
| `pii_found` | `array[string]` | Types of PII detected | `["email", "phone"]` |
| `sanitized_content` | `string` | PII-sanitized version (if requested) | `"Contact [EMAIL] at [PHONE]"` |

### 5. Error Handling

- `GuardrailError`: Check could not be performed
- Return Format: `{"success": false, "error": "Guardrail check failed: <details>"}`

### 6. Idempotency

- **Idempotent**: Yes
- **Explanation**: Same input produces same guardrail results.

### 7. Usage Examples (for MCP context)

```json
{
  "tool_name": "llm_check_guardrails",
  "arguments": {
    "text": "Please help me understand machine learning. My email is user@example.com",
    "check_type": "input",
    "checks": ["injection", "pii"],
    "sanitize": true
  }
}
```

### 8. Security Considerations

- **Input Validation**: Text analyzed for security threats.
- **Permissions**: No external calls; runs locally.
- **Data Handling**: PII detection is local; text not transmitted.
- **Blocking**: High-threat content should be blocked from LLM processing.

---

## Tool: `llm_estimate_cost`

### 1. Tool Purpose and Description

Estimates the cost of an LLM request before making it. Helps with budget management and cost-aware model selection.

### 2. Invocation Name

`llm_estimate_cost`

### 3. Input Schema (Parameters)

| Parameter Name | Type | Required | Description | Example Value |
|:--------------|:-----|:---------|:------------|:--------------|
| `model_id` | `string` | Yes | Model to estimate cost for | `"gpt-4o"` |
| `input_text` | `string` | Yes | Input prompt text | `"Explain this concept..."` |
| `estimated_output_tokens` | `integer` | No | Expected output tokens. Default: 500 | `1000` |

### 4. Output Schema (Return Value)

| Field Name | Type | Description | Example Value |
|:-----------|:-----|:------------|:--------------|
| `success` | `boolean` | Whether estimation succeeded | `true` |
| `model_id` | `string` | Model priced | `"gpt-4o"` |
| `input_tokens` | `integer` | Estimated input tokens | `125` |
| `output_tokens` | `integer` | Estimated output tokens | `500` |
| `estimated_cost` | `float` | Total estimated cost in USD | `0.0053` |
| `input_cost` | `float` | Input token cost | `0.0003` |
| `output_cost` | `float` | Output token cost | `0.005` |
| `pricing` | `object` | Model pricing info | See below |
| `pricing.input_per_1k` | `float` | Cost per 1K input tokens | `0.0025` |
| `pricing.output_per_1k` | `float` | Cost per 1K output tokens | `0.01` |

### 5. Error Handling

- `ModelNotFoundError`: Pricing not available for model
- Return Format: `{"success": false, "error": "Cost estimation failed: <details>"}`

### 6. Idempotency

- **Idempotent**: Yes
- **Explanation**: Same inputs produce same cost estimate.

### 7. Usage Examples (for MCP context)

```json
{
  "tool_name": "llm_estimate_cost",
  "arguments": {
    "model_id": "claude-3-5-sonnet",
    "input_text": "Analyze this codebase and provide detailed recommendations for improving code quality, performance, and maintainability...",
    "estimated_output_tokens": 2000
  }
}
```

### 8. Security Considerations

- **Input Validation**: Model ID validated against known pricing data.
- **Permissions**: No external calls; uses local pricing data.
- **Data Handling**: No sensitive data processed.

---

## Tool: `llm_track_usage`

### 1. Tool Purpose and Description

Records LLM usage for cost tracking and analytics. Provides usage summaries, budget monitoring, and historical analysis.

### 2. Invocation Name

`llm_track_usage`

### 3. Input Schema (Parameters)

| Parameter Name | Type | Required | Description | Example Value |
|:--------------|:-----|:---------|:------------|:--------------|
| `action` | `enum["record", "summary", "export"]` | Yes | Tracking action | `"record"` |
| `model_id` | `string` | Conditional | Model used (required for "record") | `"gpt-4o"` |
| `input_tokens` | `integer` | Conditional | Input tokens (required for "record") | `500` |
| `output_tokens` | `integer` | Conditional | Output tokens (required for "record") | `200` |
| `latency_ms` | `float` | No | Request latency | `1234.5` |
| `period_days` | `integer` | No | Summary period (for "summary"). Default: 30 | `7` |

### 4. Output Schema (Return Value)

**For action="record":**
| Field Name | Type | Description | Example Value |
|:-----------|:-----|:------------|:--------------|
| `success` | `boolean` | Whether recording succeeded | `true` |
| `record_id` | `string` | Recorded entry ID | `"rec-abc123"` |
| `cost` | `float` | Calculated cost | `0.0045` |

**For action="summary":**
| Field Name | Type | Description | Example Value |
|:-----------|:-----|:------------|:--------------|
| `success` | `boolean` | Whether summary succeeded | `true` |
| `period_start` | `string` | Summary start date | `"2026-01-27"` |
| `period_end` | `string` | Summary end date | `"2026-02-03"` |
| `total_requests` | `integer` | Total API calls | `156` |
| `total_tokens` | `integer` | Total tokens used | `125000` |
| `total_cost` | `float` | Total cost | `12.45` |
| `by_model` | `object` | Breakdown by model | See below |

### 5. Error Handling

- `TrackingError`: Unable to record or retrieve usage
- Return Format: `{"success": false, "error": "Usage tracking failed: <details>"}`

### 6. Idempotency

- **Idempotent**: No for "record" (creates new entry), Yes for "summary"/"export"
- **Explanation**: Recording creates new entries; queries are read-only.

### 7. Usage Examples (for MCP context)

```json
{
  "tool_name": "llm_track_usage",
  "arguments": {
    "action": "summary",
    "period_days": 7
  }
}
```

### 8. Security Considerations

- **Input Validation**: Token counts validated as positive integers.
- **Permissions**: Usage data stored locally.
- **Data Handling**: Usage statistics may reveal API usage patterns.

---

## Tool: `llm_list_providers`

### 1. Tool Purpose and Description

Lists all available LLM providers with their configuration status, available models, and capabilities.

### 2. Invocation Name

`llm_list_providers`

### 3. Input Schema (Parameters)

| Parameter Name | Type | Required | Description | Example Value |
|:--------------|:-----|:---------|:------------|:--------------|
| `include_models` | `boolean` | No | Include available models per provider. Default: true | `true` |
| `check_availability` | `boolean` | No | Test provider connectivity. Default: false | `true` |

### 4. Output Schema (Return Value)

| Field Name | Type | Description | Example Value |
|:-----------|:-----|:------------|:--------------|
| `success` | `boolean` | Whether listing succeeded | `true` |
| `providers` | `array[object]` | Available providers | See below |
| `providers[].name` | `string` | Provider name | `"openai"` |
| `providers[].configured` | `boolean` | API key configured | `true` |
| `providers[].available` | `boolean` | Provider responding (if checked) | `true` |
| `providers[].default_model` | `string` | Default model | `"gpt-4o"` |
| `providers[].models` | `array[string]` | Available models | `["gpt-4o", "gpt-4o-mini"]` |
| `default_provider` | `string` | System default provider | `"openai"` |

### 5. Error Handling

- Return Format: `{"success": false, "error": "Provider listing failed: <details>"}`

### 6. Idempotency

- **Idempotent**: Yes
- **Explanation**: Read-only query of provider configuration.

### 7. Usage Examples (for MCP context)

```json
{
  "tool_name": "llm_list_providers",
  "arguments": {
    "include_models": true,
    "check_availability": true
  }
}
```

### 8. Security Considerations

- **Input Validation**: No user-supplied sensitive data.
- **Permissions**: May make test API calls if `check_availability` is true.
- **Data Handling**: API keys not exposed; only configuration status shown.
