# Orchestration -- Technical Specification

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Overview

Wraps the OpenStack Heat API for Infomaniak Public Cloud, providing infrastructure-as-code stack management. Supports full stack lifecycle (create, update, delete, suspend, resume), resource and event introspection, template validation, and output retrieval.

## Architecture

Single-class design. `InfomaniakHeatClient` extends `InfomaniakOpenStackBase` with `_service_name = "orchestration"`. All operations delegate to `self._conn.orchestration.*` methods from `openstacksdk`.

## Key Methods

### Stack Lifecycle

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `list_stacks` | (none) | `list[dict]` | All stacks (id, name, status, status_reason, creation_time) |
| `get_stack` | `stack_id: str` | `dict or None` | Full stack details with parameters and outputs |
| `create_stack` | `name, template: str, parameters, environment, timeout_mins: int = 60, disable_rollback: bool, **kwargs` | `dict or None` | Create from YAML string |
| `create_stack_from_file` | `name, template_path: str, parameters, **kwargs` | `dict or None` | Read file and delegate to `create_stack` |
| `update_stack` | `stack_id, template, parameters, environment, **kwargs` | `bool` | Update stack |
| `delete_stack` | `stack_id: str` | `bool` | Delete stack |
| `suspend_stack` | `stack_id: str` | `bool` | Suspend stack |
| `resume_stack` | `stack_id: str` | `bool` | Resume suspended stack |

### Resource and Event Operations

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `list_stack_resources` | `stack_id: str` | `list[dict]` | Resources (name, type, status, physical_resource_id) |
| `get_stack_resource` | `stack_id, resource_name` | `dict or None` | Resource with attributes |
| `list_stack_events` | `stack_id, resource_name` | `list[dict]` | Events with status and reason |

### Template and Output Operations

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `validate_template` | `template: str, environment` | `dict` | `{valid, description, parameters}` or `{valid: False, error}` |
| `get_stack_template` | `stack_id: str` | `str or None` | Retrieve template string |
| `get_stack_outputs` | `stack_id: str` | `dict` | `{output_key: output_value}` |

## Dependencies

- **Internal**: `codomyrmex.cloud.infomaniak.base.InfomaniakOpenStackBase`
- **External**: `openstacksdk` (Heat/Orchestration proxy), `logging`

## Constraints

- `create_stack_from_file` reads the entire template file into memory via `open()` and delegates to `create_stack`.
- `validate_template` catches validation errors and returns them as `{"valid": False, "error": str(e)}` rather than raising.
- `get_stack_outputs` transforms the `stack.outputs` list of `{output_key, output_value}` dicts into a flat key-value mapping.
- Default stack creation timeout is 60 minutes (`timeout_mins=60`).
- `list_stack_events` accepts an optional `resource_name` to filter events for a specific resource.

## Error Handling

- All methods catch `Exception`, log via `logger.error`, and return sentinel values.
- `validate_template` returns structured error info rather than raising.
- No exceptions propagate to callers.
