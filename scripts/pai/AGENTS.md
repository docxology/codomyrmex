# Codomyrmex PAI — scripts/pai

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: February 2026

## Purpose

Orchestration scripts for PAI dashboard operations. Provides a clean single entry point for all dashboard lifecycle management: setup, restart, and launch.

## Script Inventory

| File | Lines | Description |
|------|-------|-------------|
| `dashboard.py` | ~200 | PAI dashboard orchestrator (setup + restart + run) |

## Method Inventory

### dashboard.py

| Function | Description |
|----------|-------------|
| `_pids_on_port(port)` | Returns list of PIDs listening on the given port via `lsof` |
| `kill_port(port)` | Sends SIGTERM then SIGKILL to all processes on port; returns True if any killed |
| `phase_setup(project_root)` | Generates dashboard static files via `WebsiteGenerator`; writes root redirect |
| `phase_restart(port)` | Calls `kill_port()` and waits for OS to reclaim the port |
| `phase_run(project_root, port, host, open_browser)` | Initialises `DataProvider`, binds `WebsiteServer`, optionally opens browser |
| `parse_args()` | CLI argument parser: `--port`, `--host`, `--restart`, `--no-open`, `--setup-only`, `--no-setup` |
| `main()` | Entry point — orchestrates phases in order based on flags |

## AI Usage Notes

- `phase_setup` and `phase_run` are safe to call directly from agent code for programmatic dashboard management.
- `kill_port` uses `lsof` (macOS/Linux); will silently no-op on platforms where `lsof` is unavailable.
- The script is designed to be **non-interactive** — all output via `print_info` / `print_error`, no prompts.
- Running `--setup-only` is safe to call repeatedly; `WebsiteGenerator` is idempotent.

## Dependencies

- `codomyrmex.website`: `DataProvider`, `WebsiteGenerator`, `WebsiteServer`
- `codomyrmex.utils.cli_helpers`: `print_info`, `print_success`, `print_error`, `setup_logging`
- stdlib: `argparse`, `signal`, `socketserver`, `subprocess`, `threading`, `time`, `webbrowser`
