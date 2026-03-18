# Hermes Personality System

**Version**: v0.3.0 | **Last Updated**: March 2026 (73-commit update)

## Overview

Hermes supports a flexible personality system that lets you define custom personas. Personalities are injected into the system prompt via `prompt_builder.py`, shaping how the agent communicates and reasons.

## Configuration

```yaml
# config.yaml
agent:
    personality: civic_technical_analyst # active personality name
    personalities:
        civic_technical_analyst: |
            You are a technical expert with strong civic awareness
            and intelligence‑analyst skills. Provide detailed, accurate
            technical information while considering societal implications
            and applying analytical rigor.
```

## Built-in Personalities

Hermes ships with several built-in personalities:

| Name          | Style                                    |
| :------------ | :--------------------------------------- |
| `helpful`     | Friendly, general-purpose assistant      |
| `concise`     | Brief, to-the-point responses            |
| `technical`   | Detailed, accurate technical information |
| `creative`    | Innovative, outside-the-box thinking     |
| `teacher`     | Patient explanations with examples       |
| `philosopher` | Contemplative, examining deeper meaning  |
| `noir`        | Hard-boiled detective voice              |
| `pirate`      | Nautical terminology and flair           |
| `shakespeare` | Elizabethan prose and dramatic flair     |
| `surfer`      | Laid-back, California vibes              |
| `hype`        | Maximum enthusiasm and energy            |
| `kawaii`      | Cute expressions with kaomoji            |
| `catgirl`     | Anime catgirl persona (nya~!)            |
| `uwu`         | Soft, playful internet culture           |

## Creating Custom Personalities

### Simple Personality

```yaml
agent:
    personality: researcher
    personalities:
        researcher: You are a meticulous researcher. Cite sources, verify claims, and present findings objectively.
```

### Multi-Line Personality

Use YAML block scalars (`|`) for complex personas:

```yaml
agent:
    personalities:
        civic_technical_analyst: |
            You are a technical expert with strong civic awareness
            and intelligence-analyst skills.

            Core behaviors:
            - Provide detailed, accurate technical information
            - Consider societal implications of technology
            - Apply analytical rigor to all assessments
            - Balance technical depth with accessibility
            - Flag potential risks and ethical concerns
```

### Multiple Personalities

Define several and switch between them by changing the `personality` field:

```yaml
agent:
    personality: morning_briefer # currently active
    personalities:
        morning_briefer: |
            Create concise morning briefings summarizing
            overnight activity, news, and pending tasks.
        deep_researcher: |
            Conduct thorough research with source verification.
            Always provide citations and confidence levels.
        code_reviewer: |
            Review code with focus on security, performance,
            and maintainability. Use a constructive tone.
```

## Per-Instance Personalities

When running [multiple instances](multi_instance.md), each can have its own personality:

```text
~/.hermes/config.yaml
  personality: helpful              # Primary: general assistant

~/hermes-crescent-city/.hermes/config.yaml
  personality: civic_technical_analyst  # Crescent City: civic analyst

~/hermes-research/.hermes/config.yaml
  personality: deep_researcher          # Research: thorough analyst
```

## How Personalities Work Internally

The `prompt_builder.py` module assembles the system prompt by combining:

1. **Base system prompt** — core agent instructions
2. **Personality text** — from the active personality definition
3. **Available tools** — JSON schemas for tool calling
4. **Skills** — any loaded skill prompts
5. **Memory context** — relevant memories from FTS5 recall
6. **Session history** — compressed or full conversation history

The personality text is inserted early in the system prompt, establishing the agent's communication style before any task-specific content.

## Tips

- **Keep personalities focused** — don't try to encode tool instructions in the personality
- **Test with `hermes chat`** — quickly verify personality behavior before deploying to Telegram
- **Use YAML block scalars** — `|` preserves newlines, `>` folds into one line
- **Avoid duplicate `agent:` keys** — see [configuration.md](configuration.md) for YAML pitfalls

## Related Documents

- [Configuration](configuration.md) — Full config reference
- [Models](models.md) — Model selection affects personality expression
- [Multi-Instance](multi_instance.md) — Per-bot personalities
