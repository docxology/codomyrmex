# Codomyrmex Agents -- src/codomyrmex/system_discovery/reporting

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Purpose

Provides system status reporting and environment profiling for the Codomyrmex
ecosystem. `StatusReporter` aggregates Python environment, project structure,
dependency availability, git status, and external tool checks into a
comprehensive report. `HardwareProfiler` and `EnvironmentProfiler` detect
hardware capabilities and execution environment (CI, Docker, Kubernetes, local).

## Key Components

| File | Class / Function | Role |
|------|-----------------|------|
| `status_reporter.py` | `StatusReporter` | Generates comprehensive system status reports with terminal formatting |
| `profilers.py` | `HardwareProfiler` | Detects CPU count, frequency, RAM, OS, and architecture via `psutil` |
| `profilers.py` | `EnvironmentProfiler` | Detects execution environment type (GitHub Actions, Travis, Docker, K8s, local) and Python runtime info |

## Operating Contracts

- `StatusReporter.generate_comprehensive_report()` returns a dict aggregating all sub-checks (Python env, project structure, dependencies, git, external tools).
- `StatusReporter.check_dependencies()` tests importability of 14 key packages grouped into Core, LLM, Data Science, Dev Tools, and Web Framework categories.
- `StatusReporter.check_git_status()` runs `git` subprocess calls with 10-second timeouts; gracefully handles missing git or non-repo scenarios.
- `HardwareProfiler.get_hardware_info()` requires `psutil`; callers should guard with `@pytest.mark.skipif` if the library is unavailable.
- `EnvironmentProfiler.get_environment_type()` inspects environment variables (`GITHUB_ACTIONS`, `TRAVIS`, `KUBERNETES_SERVICE_HOST`) and filesystem markers (`/.dockerenv`).
- `display_status_report()` uses `TerminalFormatter` for coloured output; falls back gracefully if unavailable.
- Errors must be logged via `logging_monitoring` before re-raising.

## Integration Points

- **Depends on**: `logging_monitoring.core.logger_config`, `terminal_interface.utils.terminal_utils.TerminalFormatter`, `psutil`
- **Used by**: `system_discovery` parent module, CLI `codomyrmex status` command, agent diagnostics

## Navigation

- **Parent**: [system_discovery](../AGENTS.md)
- **Root**: [../../../../README.md](../../../../README.md)
