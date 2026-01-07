# Codomyrmex Agents — src/codomyrmex/llm/prompt_templates

## Signposting
- **Parent**: [llm](../AGENTS.md)
- **Self**: [Agents](AGENTS.md)
- **Children**:
    - None
- **Key Artifacts**:
    - [Functional Spec](SPEC.md)
    - [Human Readme](README.md)

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: January 2026

## Purpose
Prompt templates for LLM interactions including system templates, context templates, and task templates. Provides standardized prompt structures for consistent LLM interactions across the Codomyrmex platform.

## Active Components
- `README.md` – Project file
- `SPEC.md` – Project file
- `context_template.md` – Context template for LLM prompts
- `system_template.md` – System template for LLM prompts
- `task_template.md` – Task template for LLM prompts

## Key Templates

### System Template (`system_template.md`)
- System-level prompt template defining LLM persona and behavior

### Context Template (`context_template.md`)
- Context template for providing background information to LLMs

### Task Template (`task_template.md`)
- Task template for structuring task-specific prompts

## Operating Contracts
- Maintain alignment between code, documentation, and configured workflows.
- Ensure Model Context Protocol interfaces remain available for sibling agents.
- Record outcomes in shared telemetry and update TODO queues when necessary.

## Navigation Links
- **Human Documentation**: [README.md](README.md)
- **Functional Specification**: [SPEC.md](SPEC.md)
- **📁 Parent Directory**: [llm](../README.md) - Parent directory documentation
- **🏠 Project Root**: [README](../../../../README.md) - Main project documentation