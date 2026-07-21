# Personal AI Infrastructure — Build Orchestration

PAI agents may use this package during trusted BUILD and VERIFY workflows.
Prefer `validate_build_config`, `run_build_command`, and
`orchestrate_build_pipeline` with explicit project and output paths. Build
commands must be argument lists; shell operators require an explicit trusted
shell command outside this API.
