# LLM Examples

**Version**: v0.2.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

Example implementations demonstrating real LLM provider integrations and usage patterns.

## Examples

### Interactive Chat (`openrouter_chat.py`)

**Multi-turn conversations with streaming, batch mode, and conversation export.**

```bash
# Interactive mode
python openrouter_chat.py

# With system prompt personality
python openrouter_chat.py --system "You are a pirate captain"

# Batch mode (non-interactive)
python openrouter_chat.py --batch "Hello" "What is Python?" "Tell me a joke"

# Save conversation
python openrouter_chat.py --save-to conversation.json

# Custom model
python openrouter_chat.py --model "google/gemma-3-12b-it:free"
```

**Commands (interactive mode):** `/quit`, `/save <file>`, `/history`, `/clear`, `/model <name>`

### Long Output Generator (`openrouter_long_output.py`)

**Generate dissertations, essays, stories with configurable length and templates.**

```bash
# 5-page essay
python openrouter_long_output.py --topic "Climate Change" --pages 5

# PhD dissertation (~100 pages)
python openrouter_long_output.py --template dissertation --topic "AI Ethics" --pages 100 --output thesis.md

# 10,000 word creative story
python openrouter_long_output.py --template story --topic "Space Exploration" --words 10000

# List templates
python openrouter_long_output.py --list-templates
```

**Templates:** `essay`, `dissertation`, `story`, `documentation`, `custom`

### OpenRouter Usage (`openrouter_usage.py`)

**Complete OpenRouter example with CLI interface and flexible API key handling.**

```bash
# List available free models
python openrouter_usage.py --list-models

# Simple completion
python openrouter_usage.py --prompt "Explain Python in one sentence"

# Streaming response
python openrouter_usage.py --prompt "Write a haiku" --stream
```

### Basic Usage (`basic_usage.py`)

Core LLM integration patterns with configuration management.

### Advanced Workflow (`advanced_workflow.py`)

Complex multi-step LLM workflows and integration patterns.

## API Key Setup

```bash
# Environment variable (recommended)
export OPENROUTER_API_KEY='your-key-here'

# Config file
mkdir -p ~/.config/openrouter
echo 'your-key-here' > ~/.config/openrouter/api_key
chmod 600 ~/.config/openrouter/api_key
```

**Get your free API key at:** <https://openrouter.ai/keys>

## Free Models

| Model | Description |
|-------|-------------|
| `openrouter/free` | Auto-selects best available |
| `meta-llama/llama-3.3-70b-instruct:free` | Meta Llama 3.3 70B |
| `google/gemma-3-27b-it:free` | Google Gemma 3 27B |
| `mistralai/mistral-small-3.1-24b-instruct:free` | Mistral Small 3.1 |
| `deepseek/deepseek-r1-0528:free` | DeepSeek R1 |

## Navigation

- **Parent Directory**: [scripts/llm](../README.md)
- **Project Root**: [codomyrmex](../../../README.md)
- **LLM Source**: [src/codomyrmex/llm](../../../src/codomyrmex/llm/README.md)
