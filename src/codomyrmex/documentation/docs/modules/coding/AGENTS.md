# coding - Agent Coordination

**Version**: v1.1.9 | **Status**: Active | **Last Updated**: March 2026

## Overview

The coding module provides code execution, sandboxing, review, monitoring, and debugging capabilities to PAI agents. It exposes 5 MCP tools for agent consumption and organizes internal functionality across six submodules.

## Key Files

| File | Role |
|------|------|
| `__init__.py` | Package root; re-exports from all submodules |
| `mcp_tools.py` | 5 MCP tool definitions |
| `execution/` | Sandboxed code execution with `SUPPORTED_LANGUAGES` |
| `sandbox/` | Docker isolation, resource limits, temp file management |
| `review/` | CodeReviewer, PyscnAnalyzer, quality gates, reports |
| `monitoring/` | ExecutionMonitor, MetricsCollector, ResourceMonitor |
| `debugging/` | Debugger, ErrorAnalyzer, PatchGenerator, FixVerifier |

## MCP Tools Available

| Tool | Parameters | Returns |
|------|-----------|---------|
| `code_execute` | `language: str, code: str, timeout: int` | Execution result dict |
| `code_list_languages` | none | Sorted list of supported languages |
| `code_review_file` | `path: str` | Analysis results for a single file |
| `code_review_project` | `path: str` | Project-wide quality analysis |
| `code_debug` | `code: str, stdout: str, stderr: str, exit_code: int` | Debug diagnosis and patches |

## Agent Instructions

1. Use `code_execute` for running user-provided code snippets safely within sandbox limits.
2. Use `code_review_file` for single-file quality checks; `code_review_project` for directory-wide analysis.
3. `code_debug` accepts source code along with its output -- provide all four parameters for accurate diagnosis.
4. `code_list_languages` returns the authoritative list of supported execution languages.
5. All tools return `{"status": "ok", ...}` on success or `{"status": "error", "error": "..."}` on failure.

## Operating Contracts

- `code_execute` runs in a sandboxed process with configurable timeout (default 30s).
- Review tools require file/directory paths accessible from the agent's working directory.
- Debug tools do not execute code -- they analyze provided output and suggest patches.
- Trust gateway: `code_execute` requires TRUSTED level (destructive tool).

## PAI Agent Role Access Matrix

| Agent Role | Access Level | Primary Tools |
|-----------|-------------|---------------|
| Engineer | Full | All 5 tools |
| QATester | Read | `code_review_file`, `code_review_project` |
| Architect | Read | `code_review_project`, `code_debug` |

## Navigation

- [Root](../../../../../../README.md)
