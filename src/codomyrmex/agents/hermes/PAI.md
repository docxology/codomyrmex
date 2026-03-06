# PAI Access Matrix - Hermes Agent

Provides interactive and autonomous task execution capabilities bridging the Codomyrmex ecosystem to NousResearch's Hermes Agent CLI.

| PAI Agent | Access Level | Primary Capabilities | Trust Level |
| :-------- | :----------- | :------------------- | :---------- |
| **Engineer** | Full | `hermes_execute`, `hermes_status`, `hermes_skills_list` | TRUSTED |
| **Architect** | Read + Config | `hermes_status`, `hermes_skills_list` | OBSERVED |
| **QATester** | Tests | `hermes_execute` | OBSERVED |
| **Researcher** | Read-only | `hermes_status`, `hermes_skills_list` | OBSERVED |

## Use Cases

- Complex containerized tasks (`hermes_execute` via terminal backend).
- Remote sandboxed tool execution.
- Skill administration and querying.
