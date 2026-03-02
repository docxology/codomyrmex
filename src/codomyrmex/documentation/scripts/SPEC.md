# Scripts Module - Functional Specification

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: March 2026

## Overview

32 standalone Python scripts for automated documentation maintenance. Organised into four functional categories: auditing, fixing, validation, and generation. Each script is independently runnable via `python <script>.py` or `python -m` invocation with `argparse`-based CLI.

## Architecture

Scripts are stateless utilities. Each reads documentation files, performs analysis or transformation, and either reports findings (audit/validation) or writes corrections (fixers). No shared state between scripts. Common pattern: class-based fixers with `fix_all_*` methods iterating over `rglob("AGENTS.md")` or `rglob("*.md")` results.

## Key Classes and Functions

### `DocumentationScanner` (documentation_scan_report.py)

| Method | Description |
|--------|-------------|
| `scan()` | Runs 7-phase audit: discovery, accuracy, completeness, quality, improvements, verification, reporting |
| `generate_json_report()` | Outputs structured JSON results |
| `generate_markdown_report()` | Outputs human-readable markdown summary |

### `AgentsFileFixer` (fix_agents_files.py)

| Method | Description |
|--------|-------------|
| `find_agents_files()` | Discovers all AGENTS.md via `rglob` |
| `get_actual_files(directory)` | Lists real files/dirs in a directory (excludes hidden, AGENTS.md itself) |
| `parse_agents_file(path)` | Extracts sections by `## ` headers |
| `extract_active_components(text)` | Parses bullet items from Active Components section |
| `fix_agents_file(path, dry_run)` | Adds missing items; returns `True` if already complete |
| `fix_all_agents_files(dry_run)` | Batch runner; returns results dict |

### `NavigationLinkFixer` (fix_navigation_links.py)

| Method | Description |
|--------|-------------|
| `validate_navigation_link(target, agents_file)` | Resolves relative path and checks file existence |
| `fix_navigation_links(agents_file, dry_run)` | Removes dead navigation links |
| `fix_all_navigation_links(dry_run)` | Batch runner for all AGENTS.md files |

### `OrchestratorCommandFixer` (fix_orchestrator_commands.py)

| Method | Description |
|--------|-------------|
| `extract_commands_from_orchestrator(script_path)` | Finds `subparsers.add_parser` calls via regex |
| `fix_orchestrator_commands(agents_file, dry_run)` | Adds undocumented CLI commands to Active Components |

### `AgentsCleaner` (clean_agents_files.py)

| Method | Description |
|--------|-------------|
| `clean(path)` | Removes entries from Active Components that do not correspond to actual files |

### `CodeExample` (validate_code_examples.py, dataclass)

| Field | Type | Description |
|-------|------|-------------|
| `file_path` | `str` | Source markdown file |
| `line_number` | `int` | Line of code block start |
| `language` | `str` | Language identifier (filtered to `"python"`) |
| `code` | `str` | Extracted code content |
| `syntax_valid` | `bool` | Result of `ast.parse` validation |
| `import_errors` | `list[str]` | Import resolution issues |

### Standalone Functions

| Function | File | Description |
|----------|------|-------------|
| `fix_newlines(directory)` | `fix_markdown_newlines.py` | Replaces escaped `\\n` with real newlines |
| `fix_placeholders(root_dir)` | `fix_placeholders.py` | Replaces placeholder SPEC.md with typed templates |
| `fix_script_specs(root_dir)` | `fix_script_specs.py` | Generates wrapper SPEC.md for script directories |
| `boost_file(path)` | `boost_quality_score.py` | Removes placeholders, adds navigation/architecture blocks |
| `enhance_stubs(path)` | `enhance_stubs.py` | Appends Getting Started and Contributing sections to short READMEs |
| `audit_directory(root_path)` | `global_doc_auditor.py` | Returns `(total, compliant, issues)` tuple for RASP compliance |
| `fix_links_in_file(file_path, repo_root)` | `fix_broken_links.py` | Repairs broken relative markdown links |
| `fix_agents_file(file_path)` | `fix_agents_structure.py` | Ensures Purpose, Active Components, Operating Contracts sections exist |

## Dependencies

- `logging_monitoring` -- `get_logger` for structured logging.
- Standard library: `pathlib`, `argparse`, `re`, `os`, `ast`, `json`, `dataclasses`.

## Constraints

- Fixer scripts default to dry-run; `--fix` flag required for writes.
- Scripts skip hidden directories (`.git`, `.venv`), `__pycache__`, and `node_modules`.
- File encoding assumed UTF-8; `PermissionError` and `UnicodeDecodeError` logged and skipped.
- Scripts are not importable as a library (`__init__.py` is empty); each runs standalone.

## Error Handling

| Scenario | Behaviour |
|----------|-----------|
| Unreadable file | Logged warning; file skipped, processing continues |
| Permission denied on directory | Logged warning; directory skipped |
| Missing target directory | Error printed; exit code 1 |
| Broken regex match | Graceful fallback; link left unchanged |

## Navigation

- **Parent**: [../README.md](../README.md)
- **Siblings**: [../education/SPEC.md](../education/SPEC.md) | [../quality/SPEC.md](../quality/SPEC.md)
- **Root**: [../../../../README.md](../../../../README.md)
