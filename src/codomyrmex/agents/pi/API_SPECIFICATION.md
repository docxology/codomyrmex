# Pi Coding Agent — API Specification

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Client API

### Configuration

```python
from codomyrmex.agents.pi import PiClient, PiConfig

# Defaults
client = PiClient()

# Custom config
client = PiClient(PiConfig(
    provider="anthropic",
    model="claude-sonnet-4-20250514",
    thinking="high",
    no_session=True,
    cwd="/path/to/project",
))
```

### Configuration Fields

| Field | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `provider` | `str` | `"google"` | LLM provider name |
| `model` | `str` | `""` | Model pattern or `provider/id` |
| `api_key` | `str` | `""` | API key (overrides env var) |
| `thinking` | `str` | `""` | off, minimal, low, medium, high, xhigh |
| `tools` | `str` | `"read,bash,edit,write"` | Comma-separated tool list |
| `session_dir` | `str` | `""` | Session storage directory |
| `no_session` | `bool` | `False` | Disable session persistence |
| `pi_bin` | `str` | `""` | Override pi binary path |
| `cwd` | `str` | `""` | Working directory |
| `env` | `dict` | `{}` | Extra environment variables |
| `startup_timeout` | `float` | `10.0` | Startup timeout (seconds) |
| `extra_args` | `list` | `[]` | Additional CLI arguments |

### Methods

#### Lifecycle

| Method | Returns | Description |
| :--- | :--- | :--- |
| `start()` | `PiClient` | Launch pi RPC subprocess |
| `stop()` | `dict` | Terminate pi subprocess |
| `is_running` | `bool` | Check if subprocess alive |

#### RPC Commands

| Method | Returns | Description |
| :--- | :--- | :--- |
| `prompt(message, ...)` | `Generator[dict]` | Send prompt, yield events |
| `prompt_sync(message, ...)` | `str` | Blocking prompt → full text |
| `steer(message)` | `None` | Interrupt with new instruction |
| `follow_up(message)` | `None` | Queue message for after completion |
| `abort()` | `None` | Abort current operation |
| `new_session()` | `None` | Start fresh session |
| `set_model(model)` | `None` | Switch model mid-session |
| `set_thinking(level)` | `None` | Set thinking level |
| `get_state()` | `None` | Request state |
| `compact()` | `None` | Trigger compaction |

#### Standalone

| Method | Returns | Description |
| :--- | :--- | :--- |
| `run_print(message, ...)` | `str` | Non-interactive `pi -p` mode |

## Error Hierarchy

| Exception | Description |
| :--- | :--- |
| `PiError` | Base exception |
| `PiStartupError` | Cannot find/start pi binary |
| `PiProtocolError` | JSONL framing/parsing error |
| `PiTimeoutError` | Timeout waiting for response |
