# Codomyrmex Agents — src/codomyrmex/llm/prompt_templates

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: January 2026

## Purpose

Provides reusable prompt templates for LLM interactions. Contains structured markdown templates for system prompts, context injection, and task-specific instructions that can be composed for various use cases.

## Active Components

- `system_template.md` - System prompt templates
- `context_template.md` - Context injection templates
- `task_template.md` - Task-specific instruction templates
- `SPEC.md` - Directory specification
- `README.md` - Directory documentation

## Template Types

### system_template.md
Defines AI persona and behavior:
- Role definitions (assistant, analyst, coder)
- Behavioral constraints
- Output format specifications
- Safety guardrails

Example:
```markdown
You are a helpful coding assistant. You:
- Write clean, well-documented code
- Explain your reasoning
- Ask clarifying questions when needed
- Follow best practices for the language
```

### context_template.md
Injects relevant context:
- Document summaries
- Code snippets
- Previous conversation context
- Environmental information

Example:
```markdown
## Current Context
Project: {{project_name}}
Language: {{language}}
Files in scope:
{{file_list}}
```

### task_template.md
Specifies task instructions:
- Code generation tasks
- Analysis tasks
- Transformation tasks
- Review tasks

Example:
```markdown
## Task: Code Review
Review the following code for:
1. Security vulnerabilities
2. Performance issues
3. Best practice violations

Code to review:
{{code}}
```

## Template Composition

Templates can be combined:
```
{system_template} + {context_template} + {task_template} = complete_prompt
```

## Operating Contracts

- Templates use `{{variable}}` placeholder syntax
- All required variables documented in template header
- Templates are version controlled
- Changes require backward compatibility consideration
- Templates validated for injection safety

## Signposting

- **Consumed By**: `ollama/model_runner.py`, `fabric/fabric_manager.py`
- **Parent Directory**: [llm](../README.md) - Parent module documentation
- **Related Modules**:
  - `ollama/` - Template consumers
  - `fabric/` - Pattern templates
  - `outputs/llm_outputs/` - Sample outputs using templates
- **Project Root**: [../../../../README.md](../../../../README.md) - Main project documentation
