# Education Agents

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

Agents dedicated to teaching, curriculum design, and skill assessment.

## Agents

### `InstructorAgent` (Tutoring)

- **Role**: Explains concepts and answers questions.
- **Capabilities**: `teach_lesson`, `answer_question`, `provide_example`.

### `CurriculumDesigner` (Curriculum)

- **Role**: Creates structured learning paths.
- **Capabilities**: `design_course`, `sequence_topics`.

### `ProctorAgent` (Certification)

- **Role**: Administers exams and verifies skills.
- **Capabilities**: `administer_test`, `grade_submission`.

## Tools

| Tool | Agent | Description |
| :--- | :--- | :--- |
| `explain_concept` | Instructor | Provide explanation |
| `generate_quiz` | Proctor | Create assessment |

## Integration

These agents integrate with `codomyrmex.agents.core` and use the MCP protocol for tool access.

## Navigation

- [README](README.md) | [SPEC](SPEC.md)
