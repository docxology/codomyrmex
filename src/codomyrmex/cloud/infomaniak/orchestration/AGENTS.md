# Codomyrmex Agents -- src/codomyrmex/cloud/infomaniak/orchestration

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Purpose

Provides infrastructure-as-code orchestration for Infomaniak Public Cloud via the OpenStack Heat API. Manages Heat stacks (create, update, delete, suspend, resume), stack resources, events, template validation, and stack outputs.

## Key Components

| File | Class / Function | Role |
|------|-----------------|------|
| `client.py` | `InfomaniakHeatClient` | Heat client extending `InfomaniakOpenStackBase`; `_service_name = "orchestration"` |
| `client.py` | `list_stacks()` | List all Heat stacks with status and creation time |
| `client.py` | `get_stack(stack_id)` | Get stack details including parameters and outputs |
| `client.py` | `create_stack(name, template, parameters, ...)` | Create stack from YAML template string |
| `client.py` | `create_stack_from_file(name, template_path, ...)` | Create stack from a template file on disk |
| `client.py` | `update_stack(stack_id, template, parameters, ...)` | Update an existing stack |
| `client.py` | `delete_stack(stack_id)` | Delete a stack |
| `client.py` | `suspend_stack(stack_id)` | Suspend a running stack |
| `client.py` | `resume_stack(stack_id)` | Resume a suspended stack |
| `client.py` | `list_stack_resources(stack_id)` | List resources in a stack (type, status, physical ID) |
| `client.py` | `get_stack_resource(stack_id, resource_name)` | Get specific resource with attributes |
| `client.py` | `list_stack_events(stack_id, resource_name)` | List stack events, optionally filtered by resource |
| `client.py` | `validate_template(template, environment)` | Validate template, returns parameters and description |
| `client.py` | `get_stack_template(stack_id)` | Retrieve template from existing stack |
| `client.py` | `get_stack_outputs(stack_id)` | Get stack output key-value pairs |

## Operating Contracts

- `create_stack` accepts a YAML template as a string; `create_stack_from_file` reads the file and delegates to `create_stack`.
- `validate_template` returns `{"valid": True, ...}` on success or `{"valid": False, "error": ...}` on failure.
- `get_stack_outputs` returns a flat `{output_key: output_value}` dict from the `stack.outputs` list.
- Default `timeout_mins` for `create_stack` is 60 minutes.
- All errors are logged and methods return sentinel values rather than raising.

## Integration Points

- **Depends on**: `codomyrmex.cloud.infomaniak.base.InfomaniakOpenStackBase`, `openstacksdk` (Heat/Orchestration proxy)
- **Used by**: `codomyrmex.cloud.infomaniak` (parent)

## Navigation

- **Parent**: [infomaniak](../AGENTS.md)
- **Root**: [../../../../../README.md](../../../../../README.md)
