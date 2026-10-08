# workflows

**Version**: v1.3.0 | **Status**: Active | **Last Updated**: August 2026

## Overview

JSON workflow definitions for `codomyrmex.logistics.orchestration.project`.
A `WorkflowManager` loads every `*.json` file in its `config_dir`, which
defaults to `config/workflows/production/` under the current working
directory. `codomyrmex workflow list` and `codomyrmex workflow run <name>` use
that default, and `codomyrmex workflow create <name>` writes
`config/workflows/production/<name>.json` there, so workflows created by one
`codomyrmex` process are seen by later ones started in the same directory.
`examples/` and `tests/` are reference definitions that are only loaded when a
manager is pointed at them (`WorkflowManager(config_dir=...)`).

## Workflow File Format

```json
{
  "name": "basic_analysis",
  "description": "Optional; ignored by the loader.",
  "steps": [
    {
      "name": "check_env",
      "module": "environment_setup",
      "action": "validate_environment",
      "parameters": {},
      "dependencies": [],
      "timeout": 60,
      "max_retries": 0,
      "required": true
    }
  ]
}
```

- `name` defaults to the file stem; `steps` is required.
- Each step needs non-empty `name`, `module` and `action`. The step calls
  `codomyrmex.<module>.<action>(**parameters)` (or an action registered on the
  task orchestrator); an unknown module or action fails the step.
- `parameters` are passed verbatim: there is no `{{step.output}}`
  substitution, so steps cannot consume each other's results.
- `dependencies` lists step names; steps run in dependency order and
  independent steps run concurrently. Missing steps and cycles fail the run
  before anything executes.
- `timeout` and `max_retries` are recorded but not enforced. `required: false`
  lets the workflow succeed when that step fails.
- A step with `run_if` makes the file invalid (conditions are not supported).
  Invalid files are logged and skipped when loading.

## Workflow Templates (`codomyrmex workflow create --template`)

| Template | Steps |
| --- | --- |
| `basic` (default) | `environment_setup.validate_environment` |
| `ai-analysis` | `coding.static_analysis.get_available_tools`, `coding.static_analysis.analyze_project` (`project_root="."`), `security.scan_secrets` (`target_path="."`) |
| `build-and-test` | `environment_setup.validate_environment`, then `ci_cd_automation.build.check_build_environment` and `coding.static_analysis.analyze_project` (`project_root="."`) |

Template steps inspect the directory the workflow runs in without changing
its files (linters run by `analyze_project` may write caches such as
`.ruff_cache`). Underscores are accepted in place of hyphens (`ai_analysis`).

## Directory Contents

- `PAI.md` – File
- `README.md` – File
- `SPEC.md` – File
- `examples/` – Subdirectory
- `production/` – Subdirectory
- `tests/` – Subdirectory

## Navigation

- **Parent Directory**: [config](../README.md)
- **Project Root**: ../../README.md

## Related Documents

- **Agents**: [AGENTS.md](AGENTS.md)
