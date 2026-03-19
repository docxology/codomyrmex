# Hermes Model Selection & OpenRouter

**Version**: v0.3.0 | **Last Updated**: March 2026 (73-commit update)

## Overview

Hermes is model-agnostic and routes LLM calls through configurable providers. OpenRouter is the recommended provider for access to many models through a single API key.

## Configuring the Model

```yaml
# config.yaml
model: nousresearch/hermes-3-llama-3.1-405b:free
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
   model: nousresearch/hermes-3-llama-3.1-405b
   ```

### Listing Available Models

```bash
hermes model
```

## Model Categories

### Free Models (Good for Testing)

These models receive the `:free` suffix on OpenRouter and cost nothing to run (subject to daily quotas):

```yaml
# Native Hermes model — best tool use + agentic tasks
model: nousresearch/hermes-3-llama-3.1-405b-instruct:free

# Fast, strong function calling — 128K context
model: meta-llama/llama-3.1-70b-instruct:free

# Coding-specialized, 128K context
model: qwen/qwen2.5-coder-32b-instruct:free

# 1M+ context, ultra-fast (Google Gemini)
model: google/gemini-2.0-flash:free

# Lightweight, fastest responses
model: microsoft/phi-3.5-mini-instruct:free
```

> **Tip**: `nousresearch/hermes-3-llama-3.1-405b-instruct:free` is the best default — it is the Hermes-native model and supports structured tool calling natively.

### Recommended for Production

```yaml
# High quality reasoning
model: nousresearch/hermes-3-llama-3.1-405b

# Fast + capable
model: anthropic/claude-3.5-sonnet

# Cost-effective
model: google/gemini-2.0-flash
```

### Compression/Summary Models

For context compression, use a fast, inexpensive model:

```yaml
compression:
  summary_model: google/gemini-3-flash-preview
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
| **Free** (< $10) | 50 req/day | 20 rpm | ❌ `:free` only | All `:free` models only; failed reqs count toward limit |
| **Pay-as-you-go** (≥ $10 credits) | 1000 req/day | 20 rpm | ✅ All models | 5.5% surcharge on credit top-ups ($0.80 min); BYOK: 1M free req/month |
| **Enterprise** | Custom | Dedicated | ✅ All models | SSO, SLAs, admin controls; invoicing available |

### How to Increase Your Rate Limits

1. **Buy $10 in credits** at [openrouter.ai/settings/credits](https://openrouter.ai/settings/credits) — this is the single most effective action. It unlocks all paid models and raises daily free quota from 50 → 1,000 req/day.
2. **Use BYOK** (bring your own key): set `OPENAI_API_KEY` / `ANTHROPIC_API_KEY` directly. OpenRouter routes your requests to the upstream provider, giving you that provider's full rate limits. First 1M req/month free through OpenRouter.
3. **Check current limits** via API:

   ```bash
   curl https://openrouter.ai/api/v1/key \
     -H "Authorization: Bearer $OPENROUTER_API_KEY"
   ```

4. **Distribute across models** — different `:free` variants have separate provider quotas. Rotating between `hermes-3-llama-3.1-405b:free` and `qwen2.5-coder-32b:free` spreads load.
5. **Use smart model routing** — Hermes now supports automatic fallback via `smart_model_routing.py` (v73 update). Configure a fallback model:

   ```yaml
   model: nousresearch/hermes-3-llama-3.1-405b-instruct:free
   fallback_model: qwen/qwen2.5-coder-32b-instruct:free
   ```

### Recommended Setup: Free + Cheap Hybrid

```yaml
# Primary — native Hermes, best agentic quality, free
model: nousresearch/hermes-3-llama-3.1-405b-instruct:free

# Fallback — ultra-cheap when primary hits limit (<$0.30/M tokens paid)
fallback_model: qwen/qwen2.5-coder-32b-instruct

# Compression — use the fastest cheap model
compression:
  summary_model: google/gemini-2.0-flash
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
- [Copilot ACP](copilot_acp.md) — Using GitHub Copilot as a Hermes backend (new v0.3.0)
- [skills.md](skills.md) — Skill registry, merge order, backends
