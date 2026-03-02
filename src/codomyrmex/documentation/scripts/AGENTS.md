# Scripts Module - Agent Coordination

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: March 2026

## Purpose

Contains 32 automation scripts for documentation maintenance across the repository. Scripts fall into four categories: auditing (read-only analysis), fixing (write repairs), validation (compliance checks), and generation (scaffold creation). All scripts are CLI-runnable via `python <script>.py` or direct execution.

## Key Components

### Auditing Scripts (read-only analysis)

| File | Class / Function | Role |
|------|-----------------|------|
| `documentation_scan_report.py` | `DocumentationScanner` | 7-phase documentation audit: discovery, accuracy, completeness, quality, improvements, verification, reporting |
| `global_doc_auditor.py` | `audit_directory` | Checks every directory for required RASP files (README, AGENTS, SPEC); reports compliance rate |
| `audit_structure.py` | (audit functions) | Structural audit of documentation layout |
| `audit_agents_filepaths.py` | (audit functions) | Validates file paths listed in AGENTS.md Active Components |

### Fixing Scripts (write repairs)

| File | Class / Function | Role |
|------|-----------------|------|
| `fix_agents_files.py` | `AgentsFileFixer` | Adds missing files to AGENTS.md Active Components sections; supports dry-run |
| `fix_agents_structure.py` | `fix_agents_file` | Ensures AGENTS.md files have Purpose, Active Components, and Operating Contracts sections |
| `fix_broken_links.py` | `fix_links_in_file` | Repairs broken relative links in markdown (examples/, docs/, reference/ path patterns) |
| `fix_navigation_links.py` | `NavigationLinkFixer` | Validates and removes dead navigation links from AGENTS.md files |
| `fix_orchestrator_commands.py` | `OrchestratorCommandFixer` | Extracts CLI subparser commands and adds them to AGENTS.md |
| `fix_markdown_newlines.py` | `fix_newlines` | Replaces escaped `\\n` with actual newlines (doc_scaffolder bug fix) |
| `fix_placeholders.py` | `fix_placeholders` | Replaces placeholder SPEC.md content with test or doc templates |
| `fix_script_specs.py` | `fix_script_specs` | Generates SPEC.md for script directories using a wrapper template |
| `fix_parent_references.py` | (fix functions) | Repairs parent navigation links |
| `fix_agents_completeness.py` | (fix functions) | Ensures AGENTS.md completeness against directory contents |

### Validation Scripts (compliance checks)

| File | Class / Function | Role |
|------|-----------------|------|
| `validate_code_examples.py` | `CodeExample`, `validate_python_syntax` | Extracts Python code blocks from markdown, validates syntax via `ast.parse`, checks imports |
| `validate_child_references.py` | (validate functions) | Checks child document references resolve correctly |
| `validate_configs.py` | (validate functions) | Validates documentation configuration files |
| `validate_links.py` | (validate functions) | Validates all internal documentation links |
| `check_links.py` | (check functions) | Link checking utility |
| `check_doc_links.py` | (check functions) | Documentation-specific link checker |
| `placeholder_check.py` | (check functions) | Detects remaining placeholder content |
| `triple_check.py` | (check functions) | Multi-pass validation |

### Generation and Cleanup Scripts

| File | Class / Function | Role |
|------|-----------------|------|
| `enhance_stubs.py` | `enhance_stubs` | Appends "Getting Started" and "Contributing" sections to short READMEs |
| `boost_quality_score.py` | `boost_file` | Removes placeholder text and adds navigation/architecture blocks to meet quality thresholds |
| `clean_agents_files.py` | `AgentsCleaner` | Removes conceptual (non-file) items from AGENTS.md Active Components |
| `cleanup_operating_contracts.py` | (cleanup functions) | Normalises Operating Contracts sections |
| `generate_missing_readmes.py` | (generate functions) | Scaffolds README.md for directories missing one |
| `bootstrap_agents_readmes.py` | (bootstrap functions) | Batch-creates initial AGENTS.md and README.md files |
| `auto_generate_docs.py` | (generate functions) | Automated documentation generation |
| `smart_template_engine.py` | (template functions) | Template-based documentation scaffolding |
| `remove_placeholders.py` | (remove functions) | Strips placeholder content from documentation files |

## Operating Contracts

- All fixer scripts support `--dry-run` (default) and `--fix` modes; dry-run is always the default to prevent accidental writes.
- Scripts use `argparse` for CLI; most accept `--repo-root` to specify the repository root.
- Audit/validation scripts are strictly read-only; they never modify files.
- Scripts log via `codomyrmex.logging_monitoring.get_logger`.
- Exit codes: 0 = success/no issues, 1 = issues found or errors.

## Integration Points

- `documentation/quality` -- scripts consume audit and consistency results from the quality module to determine what needs fixing.
- `logging_monitoring` -- all scripts use `get_logger(__name__)` for structured logging.
- CI/CD -- scripts can be invoked in pipeline steps for automated documentation hygiene.

## Navigation

- **Parent**: [../README.md](../README.md)
- **Siblings**: [../education/AGENTS.md](../education/AGENTS.md) | [../quality/AGENTS.md](../quality/AGENTS.md)
- **Root**: [../../../../README.md](../../../../README.md)
