# Pi Coding Agent — PAI Access Matrix

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Access Matrix

| Resource | Level | Notes |
| :--- | :--- | :--- |
| Pi CLI (`pi`) | Execute | Subprocess invocation |
| Local filesystem | Read/Write | Via pi's read/write/edit tools |
| Bash commands | Execute | Via pi's bash tool |
| LLM API keys | Read | Environment variables |
| Session data | Read/Write | `~/.pi/agent/sessions/` |
| Pi packages | Install | `pi install <source>` |

## Security Notes

- Pi executes bash commands with the same permissions as the parent process
- API keys are passed via environment variables (never logged)
- Session data may contain sensitive prompts/responses
- The `--no-session` flag prevents persistence
