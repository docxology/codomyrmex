# Release Module — MCP Tool Specification

**Version**: v1.3.0 | **Status**: Active | **Last Updated**: July 2026

## Overview

Three MCP tools expose strict release validation and real local builds. No MCP
tool publishes remotely or prepares a technical-report bundle.

## `release_validate`

Accepts optional evidence fields for tests, coverage, typing, security,
documentation, and artifact verification. Omitted required categories remain
missing and therefore block certification under the default strict policy.

Important response fields are `certified`, `pass_rate`, `blockers`, and the
per-check `category`, `status`, and `value`.

## `release_build`

Parameters:

- `name`
- `version`
- `python_requires`
- `source_dir`
- `output_dir`

Runs a real isolated `uv build`. Each returned artifact includes `filename`,
`path`, `format`, `media_type`, `size_bytes`, complete `sha256`, and complete
`sha512`. `success` is false when the command, count, embedded package metadata,
or archive-member safety inspection is invalid. Unsafe absolute, traversing,
SCM, cache, and private-environment paths are never copied from the isolated
stage; neither are files embedding the active source or user-home path.

## `release_certification_report`

Accepts the same evidence categories as `release_validate` and returns the
fail-closed certification result as Markdown. Missing categories remain visible
as blockers.

## Publication Interface Boundary

Use the direct API or CLI for publication bundles:

```bash
python -m codomyrmex.release publication prepare
python -m codomyrmex.release publication verify BUNDLE
python -m codomyrmex.release publication plan BUNDLE --target github
```

Remote publication execution is intentionally unavailable.
