# Personal AI Infrastructure Context: docs/project_orchestration/

## Purpose

Documentation for project orchestration, automation, and multi-project management.

## AI Agent Guidance

This directory covers cross-project coordination. AI agents should:

1. **Understand orchestration** — How projects are coordinated
2. **Follow workflows** — Use defined automation patterns
3. **Respect boundaries** — Honor project isolation

## Directory Structure

| File | Description |
| --- | --- |
| `task-orchestration-guide.md` | Task creation, execution, and monitoring |
| `dispatch-coordination.md` | Dispatch and coordination patterns |
| `config-driven-operations.md` | Workflow, project, and resource configuration |
| `project-lifecycle-guide.md` | Managing projects through their lifecycle |

## PAI Integration

The orchestration API lives in `codomyrmex.logistics.orchestration.project` (formerly `codomyrmex.project_orchestration`):

```python
from codomyrmex.logistics.orchestration.project import ProjectType, get_orchestration_engine

engine = get_orchestration_engine()

# Create a project and run a task for it. Tasks call codomyrmex.<module>.<action>
# unless an implementation is registered for the module/action pair.
project = engine.project_manager.create_project("demo", ProjectType.CUSTOM)
engine.task_orchestrator.register_action("demo", "echo", lambda message: message)
result = engine.execute_task(
    {"name": "greet", "module": "demo", "action": "echo", "parameters": {"message": "hi"}}
)
print(result["success"], result["result"]["result"])  # True hi

print(engine.health_check()["overall_status"])
```

## Cross-References

- [README.md](README.md) — Overview
- [AGENTS.md](AGENTS.md) — Agent rules
- [SPEC.md](SPEC.md) — Specification
- [../](../) — Parent docs directory
