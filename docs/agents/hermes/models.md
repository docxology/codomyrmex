# Hermes Model Selection & OpenRouter

**Version**: v0.4.0 | **Last Updated**: March 2026 (73-commit update + v0.4.0)

## Overview

Hermes is model-agnostic and routes LLM calls through configurable providers. OpenRouter is the recommended provider for access to many models through a single API key.

## Configuring the Model

```yaml
# config.yaml
model: nvidia/nemotron-3-super-120b-a12b:free
```

The model string follows OpenRouter's `provider/model-name` format.

## Providers

| Provider                  | Config Key              | Notes                               |
| :------------------------ | :---------------------- | :---------------------------------- |
| **OpenRouter**            | `OPENROUTER_API_KEY`    | Recommended — access to 100+ models |
| **Nous Portal**           | Auth via `hermes model` | Native Nous models                  |
| **OpenAI**                | `OPENAI_API_KEY`        | Direct OpenAI access                |
| **Any OpenAI-compatible** | Custom endpoint         | Ollama, vLLM, etc.                  |

### OpenRouter Setup

1. Get an API key at [openrouter.ai/keys](https://openrouter.ai/keys)
2. Add to `.env`:

   ```bash
   OPENROUTER_API_KEY=sk-or-v1-...
   ```

3. Set model in `config.yaml`:

   ```yaml
   model: nvidia/nemotron-3-super-120b-a12b:free
   ```

### Listing Available Models

```bash
hermes model
```

## Model Categories

### Free Models (Good for Testing)

These models receive the `:free` suffix on OpenRouter and cost nothing to run (subject to daily quotas):

```yaml
# Nvidia Nemotron 120B — top free model for tool use and agentic tasks (confirmed March 2026)
model: nvidia/nemotron-3-super-120b-a12b:free

# Qwen 2.5 72B — fast, strong function calling, 128K context
model: qwen/qwen-2.5-72b-instruct

# Google Gemini Flash — ultra-fast, 1M context, supports tool use
model: google/gemini-2.0-flash-001
```

> **Tip**: `nvidia/nemotron-3-super-120b-a12b:free` is the current recommended default — large 120B MoE model, free tier, confirmed tool-use capable. Always probe model IDs with a live test before committing: `hermes chat -q "OK" --model <model_id>`.

### Recommended for Production

```yaml
# High quality reasoning + tool use
model: anthropic/claude-3-haiku

# Fast + capable (sub-$1 per million tokens)
model: google/gemini-2.0-flash-001

# Cost-effective balance
model: qwen/qwen-2.5-72b-instruct
```

### Compression/Summary Models

For context compression, use a fast, inexpensive model:

```yaml
compression:
  summary_model: google/gemini-2.0-flash-001
  # or
  summary_model: anthropic/claude-3-haiku
```

## Reasoning Effort

```yaml
agent:
    reasoning_effort: medium # low | medium | high
```

| Level      | Behavior                                             |
| :--------- | :--------------------------------------------------- |
| **low**    | Quick responses, minimal planning                    |
| **medium** | Balanced reasoning and tool use                      |
| **high**   | Deep reasoning with scratchpads and multi-step plans |

Higher reasoning effort adds structured thinking tags (`<SCRATCHPAD>`, `<PLAN>`) to the prompt, encouraging the model to think more carefully.

## Automated Metadata & Context Windows (v0.4.0)

Hermes automatically resolves context length capacities dynamically via the OpenRouter `models.dev` API (`agent/models_dev.py`).
This means you no longer have to manually track if `qwen/qwen-2.5-72b-instruct` has 128K context limits; Hermes maps it instantly.

When Hermes' `ContextCompressor` experiences context pressure (e.g., >80% capacity), it accurately initiates token eviction based on this dynamic capacity map.
For Codomyrmex swarms depending on prolonged, deep context spanning thousands of lines of code, this automated boundary resolution significantly reduces OOM/token limits from OpenRouter.

## Multi-Model Architecture

Hermes uses different models for different purposes:

```text
Main Model (config.yaml: model)
  └── Primary conversation and tool use

Summary Model (compression.summary_model)
  └── Context compression and memory summarization

Vision Model (if configured)
  └── Image analysis and OCR
```

## Rate Limiting & Upgrading

### Tier Overview

| Tier | Daily Free Req | RPM | Paid Models | Notes |
| :--- | :--- | :--- | :--- | :--- |
| **Free** (< $5) | 50 req/day | 20 rpm | ❌ `:free` only | All `:free` models only; failed reqs count toward limit |
| **Pay-as-you-go** (≥ $5 credits) | 1000 req/day | 200 rpm | ✅ All models | 5.5% surcharge on credit top-ups; BYOK: 1M free req/month |
| **Enterprise** | Custom | Dedicated | ✅ All models | SSO, SLAs, admin controls; invoicing available |

### How to Increase Your Rate Limits

1. **Buy $5 in credits** at [openrouter.ai/settings/credits](https://openrouter.ai/settings/credits) — this is the single most effective action. It unlocks all paid models, raises daily free quota from 50 → 1,000 req/day, and increases RPM from 20 → 200.
2. **Use BYOK** (bring your own key): set `OPENAI_API_KEY` / `ANTHROPIC_API_KEY` directly. OpenRouter routes your requests to the upstream provider, giving you that provider's full rate limits. First 1M req/month free through OpenRouter.
3. **Check current limits** via API:

   ```bash
   curl https://openrouter.ai/api/v1/key \
     -H "Authorization: Bearer $OPENROUTER_API_KEY"
   ```

4. **Distribute across models** — different `:free` variants have separate provider quotas. Rotating between `nvidia/nemotron-3-super-120b-a12b:free` and `qwen/qwen-2.5-72b-instruct` spreads load.
5. **Use smart model routing** — Hermes supports automatic fallback via `smart_model_routing.py` (v73 update). Configure a fallback list:

   ```yaml
   model: nvidia/nemotron-3-super-120b-a12b:free
   fallback_models:
   - google/gemini-2.0-flash-001
   - anthropic/claude-3-haiku
   ```

### Recommended Setup: Free + Cheap Hybrid

```yaml
# Primary — best free agentic model (120B MoE, tool-use confirmed)
model: nvidia/nemotron-3-super-120b-a12b:free

# Fallback stack — activates automatically when primary is rate-limited
fallback_models:
- google/gemini-2.0-flash-001
- anthropic/claude-3-haiku

# Compression — use a fast cheap model
compression:
  summary_model: google/gemini-2.0-flash-001
```

## Cost Optimization

1. **Use free models for testing** — `model:free` suffix models
2. **Use fast models for compression** — saves on token costs
3. **Lower max_turns** — reduce runaway conversations
4. **Enable compression** — reduces token usage in long conversations

## Codomyrmex skill preload

When using **Codomyrmex** `HermesClient`, Hermes **skill packs** (`hermes chat -s`) are applied on the **Hermes CLI** execution path. The **Ollama** fallback does not load those packs. See [skills.md](skills.md).

## Related Documents

- [Configuration](configuration.md) — Full config reference
- [Sessions](sessions.md) — Compression and summary model usage
- [Personalities](personalities.md) — Custom personas
- [Copilot ACP](copilot_acp.md) — Using GitHub Copilot as a Hermes backend (Hermes doc suite v0.4.0)
- [skills.md](skills.md) — Skill registry, merge order, backends

## Navigation

- **Index**: [README.md](README.md)
- **Coordination**: [AGENTS.md](AGENTS.md)
- **Parent**: [docs/agents/AGENTS.md](../AGENTS.md)
- **Source**: [src/codomyrmex/agents/hermes/](../../../src/codomyrmex/agents/hermes/)
