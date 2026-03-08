# PAI Access Matrix - Hermes Agent

Provides interactive and autonomous task execution via NousResearch Hermes. Supports dual backends: Hermes CLI and Ollama (hermes3).

| PAI Agent | Access Level | Primary Capabilities | Trust Level |
| :--- | :--- | :--- | :--- |
| **Engineer** | Full | `hermes_execute`, `hermes_status`, `hermes_skills_list` | TRUSTED |
| **Architect** | Read + Config | `hermes_status`, `hermes_skills_list` | OBSERVED |
| **QATester** | Tests | `hermes_execute` | OBSERVED |
| **Researcher** | Read-only | `hermes_status`, `hermes_skills_list` | OBSERVED |

## Configuration

| Key | Default | Description |
| :--- | :--- | :--- |
| `hermes_backend` | `auto` | `auto` / `cli` / `ollama` |
| `hermes_model` | `hermes3` | Ollama model name |
| `hermes_timeout` | `120` | Subprocess timeout (s) |

## Use Cases

- Chat completion via Ollama hermes3 (automatic fallback).
- Complex containerized tasks via Hermes CLI (`hermes_execute`).
- Skill administration and querying (`hermes_skills_list`, CLI only).
- Backend diagnostics (`hermes_status`).
