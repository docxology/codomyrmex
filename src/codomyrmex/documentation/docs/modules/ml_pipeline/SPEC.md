# ML Pipeline Documentation Mirror Specification

**Version**: v1.3.0 | **Status**: Stub | **Last Updated**: July 2026

## Purpose

This file records the documentation-site contract for the `ml_pipeline` mirror.
The source specification at `src/codomyrmex/ml_pipeline/SPEC.md` is the
authoritative behavior contract. The module is intentionally a lightweight stub:
it defines and echoes pipeline structures through MCP tools, while production
workflow orchestration belongs in `orchestrator`.

## Mirror Contract

- Keep the stub status explicit; do not claim training, evaluation, persistence,
  scheduling, or real execution support.
- Preserve the documented MCP tool names: `ml_pipeline_create` and
  `ml_pipeline_execute`.
- Keep examples pass-through and deterministic.
- Point production users toward `orchestrator`, `eval_harness`, and
  `model_ops` where appropriate.
- Use lower-case local links for this generated docs tree.

## Validation

After changing this mirror or the source module, run:

```bash
make docs-check
uv run ruff check src/codomyrmex/ml_pipeline
uv run pytest tests/unit/ml_pipeline/ -q
```

## Navigation

- **Module Overview**: README.md is rendered in this mirror as [readme.md](readme.md)
- **Agent Guidance**: [AGENTS.md](AGENTS.md)
- **API Specification**: [api_specification.md](api_specification.md)
- **MCP Tools**: [mcp_tool_specification.md](mcp_tool_specification.md)
- **Source Specification**: [../../../../ml_pipeline/SPEC.md](../../../../ml_pipeline/SPEC.md)
