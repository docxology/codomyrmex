# Workflow Execution Personal AI Infrastructure

**Status**: Active
**Last Updated**: February 2026

## AI Capabilities

PAI details for Workflow Execution.

Workflow execution is an execution capability, not a sandbox. PAI agents may
invoke it only with a reviewed, trusted workflow. Command steps stop the
workflow after timeout or error unless the step explicitly sets
`continue_on_error: true`; this prevents later actions from running after an
unexpected failure.
