# Codomyrmex Script Reference

Generated on: 2026-01-07 15:56:55

This document contains auto-generated documentation for all scripts in the `scripts/` directory.

## Table of Contents

- [agents](#agents)
- [api](#api)
- [auth](#auth)
- [build_synthesis](#build_synthesis)
- [cache](#cache)
- [cerebrum](#cerebrum)
- [ci_cd_automation](#ci_cd_automation)
- [cloud](#cloud)
- [coding](#coding)
- [compression](#compression)
- [config_management](#config_management)
- [containerization](#containerization)
- [data_visualization](#data_visualization)
- [database_management](#database_management)
- [documentation](#documentation)
- [documents](#documents)
- [encryption](#encryption)
- [environment_setup](#environment_setup)
- [events](#events)
- [fpf](#fpf)
- [git_operations](#git_operations)
- [ide](#ide)
- [llm](#llm)
- [logging_monitoring](#logging_monitoring)
- [logistics](#logistics)
- [metrics](#metrics)
- [model_context_protocol](#model_context_protocol)
- [module_template](#module_template)
- [networking](#networking)
- [pattern_matching](#pattern_matching)
- [performance](#performance)
- [physical_management](#physical_management)
- [plugin_system](#plugin_system)
- [scrape](#scrape)
- [security](#security)
- [serialization](#serialization)
- [skills](#skills)
- [spatial](#spatial)
- [static_analysis](#static_analysis)
- [system_discovery](#system_discovery)
- [templating](#templating)
- [terminal_interface](#terminal_interface)
- [tools](#tools)
- [utils](#utils)
- [validation](#validation)
- [website](#website)

---

## agents

### orchestrate.py

**Path**: `agents/orchestrate.py`

```text
2026-01-07 15:56:57,056 - codomyrmex.logging_monitoring.logger_config - INFO - Logging configured: Level=INFO, OutputType=TEXT, File='Console', Format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
usage: orchestrate.py [-h] [--verbose] [--format {text,json,yaml}]
                      {info,jules,claude,codex,opencode,gemini,droid} ...

Agents Module Orchestrator

positional arguments:
  {info,jules,claude,codex,opencode,gemini,droid}
                        Available commands
    info                Show agents module information
    jules               Jules agent operations
    claude              Claude agent operations
    codex               Codex agent operations
    opencode            OpenCode agent operations
    gemini              Gemini agent operations
    droid               Droid autonomous agent operations

options:
  -h, --help            show this help message and exit
  --verbose, -v         Verbose output
  --format, -f {text,json,yaml}
                        Output format
```

### verify_gemini_real.py

**Path**: `agents/verify_gemini_real.py`

```text
❌ SKIPPING: GEMINI_API_KEY not found in environment.
```

---

## api

### orchestrate.py

**Path**: `api/orchestrate.py`

```text
2026-01-07 15:57:01,450 - codomyrmex.logging_monitoring.logger_config - INFO - Logging configured: Level=INFO, OutputType=TEXT, File='Console', Format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
usage: orchestrate.py [-h] [--verbose]
                      {generate-docs,extract-specs,generate-openapi,validate-openapi} ...

API Documentation operations

positional arguments:
  {generate-docs,extract-specs,generate-openapi,validate-openapi}
                        Available commands
    generate-docs       Generate API documentation
    extract-specs       Extract API specifications
    generate-openapi    Generate OpenAPI specification
    validate-openapi    Validate OpenAPI specification

options:
  -h, --help            show this help message and exit
  --verbose, -v         Verbose output

Examples:
  orchestrate.py generate-docs --source src/ --output docs/api/
  orchestrate.py extract-specs --source src/
  orchestrate.py generate-openapi --source src/ --output openapi.json
  orchestrate.py validate-openapi --spec openapi.json
```

---

## auth

### orchestrate.py

**Path**: `auth/orchestrate.py`

```text
2026-01-07 15:57:01,526 - codomyrmex.logging_monitoring.logger_config - INFO - Logging configured: Level=INFO, OutputType=TEXT, File='Console', Format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
usage: orchestrate.py [-h] [--verbose] {info} ...

Auth operations

positional arguments:
  {info}         Available commands
    info         Get auth module information

options:
  -h, --help     show this help message and exit
  --verbose, -v  Verbose output

Examples:
  orchestrate.py info
```

---

## build_synthesis

### orchestrate.py

**Path**: `build_synthesis/orchestrate.py`

```text
2026-01-07 15:57:01,610 - codomyrmex.logging_monitoring.logger_config - INFO - Logging configured: Level=INFO, OutputType=TEXT, File='Console', Format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
usage: orchestrate.py [-h] [--verbose] [--dry-run]
                      {check-environment,build,trigger-build,list-build-types,list-environments} ...

Build Synthesis operations

positional arguments:
  {check-environment,build,trigger-build,list-build-types,list-environments}
                        Available commands
    check-environment   Check build environment setup
    build               Run build pipeline
    trigger-build       Trigger a specific build target
    list-build-types    List available build types
    list-environments   List available build environments

options:
  -h, --help            show this help message and exit
  --verbose, -v         Verbose output
  --dry-run             Dry run mode (no changes)

Examples:
  orchestrate.py check-environment
  orchestrate.py build --config build_config.json
  orchestrate.py trigger-build --target python --environment production
  orchestrate.py list-build-types
  orchestrate.py list-environments
```

---

## cache

### orchestrate.py

**Path**: `cache/orchestrate.py`

```text
2026-01-07 15:57:01,696 - codomyrmex.logging_monitoring.logger_config - INFO - Logging configured: Level=INFO, OutputType=TEXT, File='Console', Format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
usage: orchestrate.py [-h] [--verbose] {info} ...

Cache operations

positional arguments:
  {info}         Available commands
    info         Get cache module information

options:
  -h, --help     show this help message and exit
  --verbose, -v  Verbose output

Examples:
  orchestrate.py info
```

---

## cerebrum

### orchestrate.py

**Path**: `cerebrum/orchestrate.py`

```text
usage: orchestrate.py [-h] [--dry-run] [--format {json,text}] [--verbose]
                      [--quiet] [--fpf-spec FPF_SPEC]
                      [--output-dir OUTPUT_DIR] [--skip-orchestration]
                      [--skip-combinatorics]

CEREBRUM-FPF orchestration script

options:
  -h, --help            show this help message and exit
  --dry-run             Show what would be executed without actually running
                        commands
  --format {json,text}  Output format (default: text)
  --verbose, -v         Enable verbose output
  --quiet, -q           Suppress non-error output
  --fpf-spec FPF_SPEC   Path to FPF-Spec.md (default: fetch from GitHub)
  --output-dir OUTPUT_DIR
                        Output directory (default: output/cerebrum)
  --skip-orchestration  Skip main orchestration analysis
  --skip-combinatorics  Skip combinatorics analysis
```

---

## ci_cd_automation

### orchestrate.py

**Path**: `ci_cd_automation/orchestrate.py`

```text
2026-01-07 15:57:02,844 - codomyrmex.logging_monitoring.logger_config - INFO - Logging configured: Level=INFO, OutputType=TEXT, File='Console', Format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
usage: orchestrate.py [-h] [--verbose] [--dry-run]
                      {create-pipeline,run-pipeline,monitor-health,generate-reports} ...

CI/CD Automation operations

positional arguments:
  {create-pipeline,run-pipeline,monitor-health,generate-reports}
                        Available commands
    create-pipeline     Create CI/CD pipeline
    run-pipeline        Run CI/CD pipeline
    monitor-health      Monitor pipeline health
    generate-reports    Generate pipeline reports

options:
  -h, --help            show this help message and exit
  --verbose, -v         Verbose output
  --dry-run             Dry run mode (no changes)

Examples:
  orchestrate.py create-pipeline --name my-pipeline
  orchestrate.py run-pipeline --name my-pipeline
  orchestrate.py run-pipeline --name my-pipeline --dry-run
  orchestrate.py monitor-health --name my-pipeline
  orchestrate.py generate-reports --name my-pipeline
  orchestrate.py run-pipeline --name my-pipeline --verbose --dry-run
```

---

## cloud

### orchestrate.py

**Path**: `cloud/orchestrate.py`

```text
Cloud module orchestrator
========================================
Cloud module loaded: codomyrmex.cloud
Available exports: ['CodaClient', 'Doc', 'DocList', 'Page', 'PageList', 'PageReference', 'Table', 'TableList', 'TableReference', 'Column', 'ColumnList', 'Row', 'RowList', 'RowEdit', 'CellEdit', 'Formula', 'FormulaList', 'Control', 'ControlList', 'Permission', 'PermissionList', 'SharingMetadata', 'ACLSettings', 'User', 'WorkspaceReference', 'FolderReference', 'Icon', 'DocSize', 'CodaAPIError', 'CodaAuthenticationError', 'CodaForbiddenError', 'CodaNotFoundError', 'CodaRateLimitError', 'CodaValidationError', 'CodaGoneError']
```

---

## coding

### orchestrate.py

**Path**: `coding/orchestrate.py`

```text
2026-01-07 15:57:03,095 - codomyrmex.logging_monitoring.logger_config - INFO - Logging configured: Level=INFO, OutputType=TEXT, File='Console', Format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
usage: orchestrate.py [-h] [--verbose] [--dry-run]
                      {generate,refactor,analyze,validate-api-keys,list-providers,list-languages,list-models} ...

AI Code Editing operations

positional arguments:
  {generate,refactor,analyze,validate-api-keys,list-providers,list-languages,list-models}
                        Available commands
    generate            Generate code snippet
    refactor            Refactor code
    analyze             Analyze code quality
    validate-api-keys   Validate API keys
    list-providers      List supported providers
    list-languages      List supported languages
    list-models         List available models

options:
  -h, --help            show this help message and exit
  --verbose, -v         Verbose output
  --dry-run             Dry run mode (no changes)

Examples:
  orchestrate.py generate "create a fibonacci function" --language python
  orchestrate.py refactor file.py "optimize for performance"
  orchestrate.py analyze file.py
  orchestrate.py validate-api-keys
  orchestrate.py list-providers
  orchestrate.py list-languages
  orchestrate.py list-models --provider openai
```

---

## compression

### orchestrate.py

**Path**: `compression/orchestrate.py`

```text
2026-01-07 15:57:03,161 - codomyrmex.logging_monitoring.logger_config - INFO - Logging configured: Level=INFO, OutputType=TEXT, File='Console', Format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
usage: orchestrate.py [-h] [--verbose] {basic} ...

Compression operations

positional arguments:
  {basic}        Available commands
    basic        Basic compression operation

options:
  -h, --help     show this help message and exit
  --verbose, -v  Verbose output

Examples:
  orchestrate.py basic
```

---

## config_management

### orchestrate.py

**Path**: `config_management/orchestrate.py`

```text
2026-01-07 15:57:03,329 - codomyrmex.logging_monitoring.logger_config - INFO - Logging configured: Level=INFO, OutputType=TEXT, File='Console', Format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
usage: orchestrate.py [-h] [--verbose] [--dry-run]
                      {load-config,validate-config} ...

Config Management operations

positional arguments:
  {load-config,validate-config}
                        Available commands
    load-config         Load configuration
    validate-config     Validate configuration

options:
  -h, --help            show this help message and exit
  --verbose, -v         Verbose output
  --dry-run             Dry run mode (no changes)

Examples:
  orchestrate.py load-config --path config.json
  orchestrate.py validate-config --path config.json
```

---

## containerization

### orchestrate.py

**Path**: `containerization/orchestrate.py`

```text
2026-01-07 15:57:03,661 - codomyrmex.logging_monitoring.logger_config - INFO - Logging configured: Level=INFO, OutputType=TEXT, File='Console', Format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
usage: orchestrate.py [-h] [--verbose] [--dry-run] {build,scan} ...

Containerization operations

positional arguments:
  {build,scan}   Available commands
    build        Build containers
    scan         Scan container security

options:
  -h, --help     show this help message and exit
  --verbose, -v  Verbose output
  --dry-run      Dry run mode (no changes)

Examples:
  orchestrate.py build --source .
  orchestrate.py scan --container my-container
```

---

## data_visualization

### orchestrate.py

**Path**: `data_visualization/orchestrate.py`

```text
2026-01-07 15:57:05,019 - codomyrmex.logging_monitoring.logger_config - INFO - Logging configured: Level=INFO, OutputType=TEXT, File='Console', Format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
usage: orchestrate.py [-h] [--verbose]
                      {line-plot,scatter-plot,bar-chart,histogram,pie-chart,heatmap,git-visualize} ...

Data Visualization operations

positional arguments:
  {line-plot,scatter-plot,bar-chart,histogram,pie-chart,heatmap,git-visualize}
                        Available commands
    line-plot           Create line plot
    scatter-plot        Create scatter plot
    bar-chart           Create bar chart
    histogram           Create histogram
    pie-chart           Create pie chart
    heatmap             Create heatmap
    git-visualize       Visualize git repository

options:
  -h, --help            show this help message and exit
  --verbose, -v         Verbose output

Examples:
  orchestrate.py line-plot --output output/line.png --title "My Line Plot"
  orchestrate.py scatter-plot --data-file data.json --output output/scatter.png
  orchestrate.py bar-chart --output output/bar.png --title "Bar Chart"
  orchestrate.py histogram --output output/hist.png --title "Distribution"
  orchestrate.py pie-chart --output output/pie.png --title "Pie Chart"
  orchestrate.py heatmap --output output/heat.png --title "Heatmap"
  orchestrate.py git-visualize --repo . --output ./git_analysis
```

---

## database_management

### orchestrate.py

**Path**: `database_management/orchestrate.py`

```text
2026-01-07 15:57:05,290 - codomyrmex.logging_monitoring.logger_config - INFO - Logging configured: Level=INFO, OutputType=TEXT, File='Console', Format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
usage: orchestrate.py [-h] [--verbose] [--dry-run] {backup,migrate} ...

Database Management operations

positional arguments:
  {backup,migrate}  Available commands
    backup          Backup database
    migrate         Run migrations

options:
  -h, --help        show this help message and exit
  --verbose, -v     Verbose output
  --dry-run         Dry run mode (no changes)

Examples:
  orchestrate.py backup --database mydb --output backup.sql
  orchestrate.py migrate --database mydb
```

---

## documentation

### add_missing_navigation_links.py

**Path**: `documentation/add_missing_navigation_links.py`

```text
Failed to get help text (Exit Code: 1)

Stderr:
Traceback (most recent call last):
  File "/Users/mini/Documents/GitHub/codomyrmex/scripts/documentation/add_missing_navigation_links.py", line 19, in <module>
    sys.exit(add_missing_navigation_links.main())
             ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~^^
  File "/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/documentation/scripts/add_missing_navigation_links.py", line 108, in main
    for root, dirs, files in os.walk(base_path):
                             ^^
NameError: name 'os' is not defined. Did you forget to import 'os'?
```

### add_missing_version_status.py

**Path**: `documentation/add_missing_version_status.py`

```text
Failed to get help text (Exit Code: 1)

Stderr:
Traceback (most recent call last):
  File "/Users/mini/Documents/GitHub/codomyrmex/scripts/documentation/add_missing_version_status.py", line 19, in <module>
    sys.exit(add_missing_version_status.main())
             ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~^^
  File "/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/documentation/scripts/add_missing_version_status.py", line 66, in main
    for root, dirs, files in os.walk(base_path):
                             ^^
NameError: name 'os' is not defined. Did you forget to import 'os'?
```

### analyze_content_quality.py

**Path**: `documentation/analyze_content_quality.py`

```text
2026-01-07 15:57:05,481 - codomyrmex.logging_monitoring.logger_config - INFO - Logging configured: Level=INFO, OutputType=TEXT, File='Console', Format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
2026-01-07 15:57:05,481 - codomyrmex.documentation.documentation_website - INFO - Codomyrmex centralized logging initialized successfully via documentation_website.py.
usage: analyze_content_quality.py [-h] [--repo-root REPO_ROOT]
                                  [--output OUTPUT]
                                  [--format {json,html,both}]
                                  [--min-score MIN_SCORE] [--fail-below-min]

Analyze documentation content quality

options:
  -h, --help            show this help message and exit
  --repo-root REPO_ROOT
                        Repository root directory
  --output OUTPUT       Output directory for results
  --format {json,html,both}
                        Output format
  --min-score MIN_SCORE
                        Minimum acceptable quality score
  --fail-below-min      Exit with error if average score below minimum
```

### audit_agents_filepaths.py

**Path**: `documentation/audit_agents_filepaths.py`

```text
Failed to get help text (Exit Code: 1)

Stderr:
{'summary': {'total_files': 279, 'total_issues': 1, 'generic_parent_labels': 1, 'broken_paths': 0, 'files_with_issues': 1}, 'results': [{'file': '@output/AGENTS.md', 'parent': None, 'children': [], 'navigation_links': [], 'key_artifacts': [], 'issues': []}, {'file': '@output/documentation_scan/AGENTS.md', 'parent': None, 'children': [], 'navigation_links': [], 'key_artifacts': [], 'issues': []}, {'file': 'AGENTS.md', 'parent': {'label': 'Parent', 'path': '../AGENTS.md', 'line': 4, 'is_generic': True}, 'children': [{'label': 'agents', 'path': 'agents/AGENTS.md', 'line': 6, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/agents/AGENTS.md'}], 'navigation_links': [{'label': 'Human Documentation', 'text': 'README.md', 'path': 'README.md', 'line': 129, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/README.md'}, {'label': 'Functional Specification', 'text': 'SPEC.md', 'path': 'SPEC.md', 'line': 130, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/SPEC.md'}, {'label': '📁 Parent Directory', 'text': 'src', 'path': '../README.md', 'line': 131, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/README.md'}, {'label': '🏠 Project Root', 'text': 'README', 'path': '../../README.md', 'line': 132, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/README.md'}], 'key_artifacts': [{'label': 'Functional Spec', 'path': 'SPEC.md', 'line': 56, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/SPEC.md'}], 'issues': [{'type': 'generic_parent_label', 'line': 4, 'message': "Parent reference uses generic '[Parent]' label"}]}, {'file': 'agents/AGENTS.md', 'parent': {'label': 'Repository Root', 'path': '../AGENTS.md', 'line': 4, 'is_generic': False}, 'children': [{'label': 'ai_code_editing', 'path': 'ai_code_editing/AGENTS.md', 'line': 6, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/agents/ai_code_editing/AGENTS.md'}], 'navigation_links': [{'label': 'Human Documentation', 'text': 'README.md', 'path': 'README.md', 'line': 54, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/agents/README.md'}, {'label': 'Functional Specification', 'text': 'SPEC.md', 'path': 'SPEC.md', 'line': 55, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/agents/SPEC.md'}, {'label': '📁 Parent Directory', 'text': 'codomyrmex', 'path': '../README.md', 'line': 56, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/README.md'}, {'label': '🏠 Project Root', 'text': 'README', 'path': '../../../README.md', 'line': 57, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/README.md'}], 'key_artifacts': [{'label': 'Functional Spec', 'path': 'SPEC.md', 'line': 18, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/agents/SPEC.md'}], 'issues': []}, {'file': 'agents/ai_code_editing/AGENTS.md', 'parent': {'label': 'Ai Code Editing', 'path': '../AGENTS.md', 'line': 4, 'is_generic': False}, 'children': [], 'navigation_links': [{'label': 'Human Documentation', 'text': 'README.md', 'path': 'README.md', 'line': 40, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/agents/ai_code_editing/README.md'}, {'label': 'Functional Specification', 'text': 'SPEC.md', 'path': 'SPEC.md', 'line': 41, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/agents/ai_code_editing/SPEC.md'}, {'label': '📁 Parent Directory', 'text': 'agents', 'path': '../README.md', 'line': 42, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/agents/README.md'}, {'label': '🏠 Project Root', 'text': 'README', 'path': '../../../../README.md', 'line': 43, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/README.md'}], 'key_artifacts': [{'label': 'Functional Spec', 'path': 'SPEC.md', 'line': 8, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/agents/ai_code_editing/SPEC.md'}], 'issues': []}, {'file': 'agents/claude/AGENTS.md', 'parent': {'label': 'Claude', 'path': '../AGENTS.md', 'line': 4, 'is_generic': False}, 'children': [], 'navigation_links': [{'label': 'Human Documentation', 'text': 'README.md', 'path': 'README.md', 'line': 30, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/agents/claude/README.md'}, {'label': 'Functional Specification', 'text': 'SPEC.md', 'path': 'SPEC.md', 'line': 31, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/agents/claude/SPEC.md'}, {'label': '📁 Parent Directory', 'text': 'agents', 'path': '../README.md', 'line': 32, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/agents/README.md'}, {'label': '🏠 Project Root', 'text': 'README', 'path': '../../../../README.md', 'line': 33, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/README.md'}], 'key_artifacts': [{'label': 'Functional Spec', 'path': 'SPEC.md', 'line': 8, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/agents/claude/SPEC.md'}], 'issues': []}, {'file': 'agents/codex/AGENTS.md', 'parent': {'label': 'Codex', 'path': '../AGENTS.md', 'line': 4, 'is_generic': False}, 'children': [], 'navigation_links': [{'label': 'Human Documentation', 'text': 'README.md', 'path': 'README.md', 'line': 30, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/agents/codex/README.md'}, {'label': 'Functional Specification', 'text': 'SPEC.md', 'path': 'SPEC.md', 'line': 31, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/agents/codex/SPEC.md'}, {'label': '📁 Parent Directory', 'text': 'agents', 'path': '../README.md', 'line': 32, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/agents/README.md'}, {'label': '🏠 Project Root', 'text': 'README', 'path': '../../../../README.md', 'line': 33, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/README.md'}], 'key_artifacts': [{'label': 'Functional Spec', 'path': 'SPEC.md', 'line': 8, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/agents/codex/SPEC.md'}], 'issues': []}, {'file': 'agents/droid/AGENTS.md', 'parent': {'label': 'Droid', 'path': '../AGENTS.md', 'line': 4, 'is_generic': False}, 'children': [{'label': 'handlers', 'path': 'handlers/AGENTS.md', 'line': 6, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/agents/droid/handlers/AGENTS.md'}], 'navigation_links': [{'label': 'Human Documentation', 'text': 'README.md', 'path': 'README.md', 'line': 34, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/agents/droid/README.md'}, {'label': 'Functional Specification', 'text': 'SPEC.md', 'path': 'SPEC.md', 'line': 35, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/agents/droid/SPEC.md'}, {'label': '📁 Parent Directory', 'text': 'agents', 'path': '../README.md', 'line': 36, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/agents/README.md'}, {'label': '🏠 Project Root', 'text': 'README', 'path': '../../../../README.md', 'line': 37, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/README.md'}], 'key_artifacts': [{'label': 'Functional Spec', 'path': 'SPEC.md', 'line': 8, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/agents/droid/SPEC.md'}], 'issues': []}, {'file': 'agents/droid/handlers/AGENTS.md', 'parent': {'label': 'Handlers', 'path': '../AGENTS.md', 'line': 4, 'is_generic': False}, 'children': [], 'navigation_links': [{'label': 'Human Documentation', 'text': 'README.md', 'path': 'README.md', 'line': 26, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/agents/droid/handlers/README.md'}, {'label': 'Functional Specification', 'text': 'SPEC.md', 'path': 'SPEC.md', 'line': 27, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/agents/droid/handlers/SPEC.md'}, {'label': '📁 Parent Directory', 'text': 'droid', 'path': '../README.md', 'line': 28, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/agents/droid/README.md'}, {'label': '🏠 Project Root', 'text': 'README', 'path': '../../../../../README.md', 'line': 29, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/README.md'}], 'key_artifacts': [{'label': 'Functional Spec', 'path': 'SPEC.md', 'line': 8, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/agents/droid/handlers/SPEC.md'}], 'issues': []}, {'file': 'agents/every_code/AGENTS.md', 'parent': {'label': 'Every Code', 'path': '../AGENTS.md', 'line': 4, 'is_generic': False}, 'children': [], 'navigation_links': [{'label': 'Human Documentation', 'text': 'README.md', 'path': 'README.md', 'line': 30, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/agents/every_code/README.md'}, {'label': 'Functional Specification', 'text': 'SPEC.md', 'path': 'SPEC.md', 'line': 31, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/agents/every_code/SPEC.md'}, {'label': '📁 Parent Directory', 'text': 'agents', 'path': '../README.md', 'line': 32, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/agents/README.md'}, {'label': '🏠 Project Root', 'text': 'README', 'path': '../../../../README.md', 'line': 33, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/README.md'}], 'key_artifacts': [{'label': 'Functional Spec', 'path': 'SPEC.md', 'line': 8, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/agents/every_code/SPEC.md'}], 'issues': []}, {'file': 'agents/gemini/AGENTS.md', 'parent': {'label': 'Gemini', 'path': '../AGENTS.md', 'line': 4, 'is_generic': False}, 'children': [], 'navigation_links': [{'label': 'Human Documentation', 'text': 'README.md', 'path': 'README.md', 'line': 30, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/agents/gemini/README.md'}, {'label': 'Functional Specification', 'text': 'SPEC.md', 'path': 'SPEC.md', 'line': 31, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/agents/gemini/SPEC.md'}, {'label': '📁 Parent Directory', 'text': 'agents', 'path': '../README.md', 'line': 32, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/agents/README.md'}, {'label': '🏠 Project Root', 'text': 'README', 'path': '../../../../README.md', 'line': 33, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/README.md'}], 'key_artifacts': [{'label': 'Functional Spec', 'path': 'SPEC.md', 'line': 8, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/agents/gemini/SPEC.md'}], 'issues': []}, {'file': 'agents/generic/AGENTS.md', 'parent': {'label': 'Generic', 'path': '../AGENTS.md', 'line': 4, 'is_generic': False}, 'children': [], 'navigation_links': [{'label': 'Human Documentation', 'text': 'README.md', 'path': 'README.md', 'line': 34, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/agents/generic/README.md'}, {'label': 'Functional Specification', 'text': 'SPEC.md', 'path': 'SPEC.md', 'line': 35, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/agents/generic/SPEC.md'}, {'label': '📁 Parent Directory', 'text': 'agents', 'path': '../README.md', 'line': 36, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/agents/README.md'}, {'label': '🏠 Project Root', 'text': 'README', 'path': '../../../../README.md', 'line': 37, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/README.md'}], 'key_artifacts': [{'label': 'Functional Spec', 'path': 'SPEC.md', 'line': 8, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/agents/generic/SPEC.md'}], 'issues': []}, {'file': 'agents/jules/AGENTS.md', 'parent': {'label': 'Jules', 'path': '../AGENTS.md', 'line': 4, 'is_generic': False}, 'children': [], 'navigation_links': [{'label': 'Human Documentation', 'text': 'README.md', 'path': 'README.md', 'line': 30, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/agents/jules/README.md'}, {'label': 'Functional Specification', 'text': 'SPEC.md', 'path': 'SPEC.md', 'line': 31, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/agents/jules/SPEC.md'}, {'label': '📁 Parent Directory', 'text': 'agents', 'path': '../README.md', 'line': 32, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/agents/README.md'}, {'label': '🏠 Project Root', 'text': 'README', 'path': '../../../../README.md', 'line': 33, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/README.md'}], 'key_artifacts': [{'label': 'Functional Spec', 'path': 'SPEC.md', 'line': 8, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/agents/jules/SPEC.md'}], 'issues': []}, {'file': 'agents/mistral_vibe/AGENTS.md', 'parent': {'label': 'Mistral Vibe', 'path': '../AGENTS.md', 'line': 4, 'is_generic': False}, 'children': [], 'navigation_links': [{'label': 'Human Documentation', 'text': 'README.md', 'path': 'README.md', 'line': 30, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/agents/mistral_vibe/README.md'}, {'label': 'Functional Specification', 'text': 'SPEC.md', 'path': 'SPEC.md', 'line': 31, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/agents/mistral_vibe/SPEC.md'}, {'label': '📁 Parent Directory', 'text': 'agents', 'path': '../README.md', 'line': 32, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/agents/README.md'}, {'label': '🏠 Project Root', 'text': 'README', 'path': '../../../../README.md', 'line': 33, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/README.md'}], 'key_artifacts': [{'label': 'Functional Spec', 'path': 'SPEC.md', 'line': 8, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/agents/mistral_vibe/SPEC.md'}], 'issues': []}, {'file': 'agents/opencode/AGENTS.md', 'parent': {'label': 'Opencode', 'path': '../AGENTS.md', 'line': 4, 'is_generic': False}, 'children': [], 'navigation_links': [{'label': 'Human Documentation', 'text': 'README.md', 'path': 'README.md', 'line': 30, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/agents/opencode/README.md'}, {'label': 'Functional Specification', 'text': 'SPEC.md', 'path': 'SPEC.md', 'line': 31, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/agents/opencode/SPEC.md'}, {'label': '📁 Parent Directory', 'text': 'agents', 'path': '../README.md', 'line': 32, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/agents/README.md'}, {'label': '🏠 Project Root', 'text': 'README', 'path': '../../../../README.md', 'line': 33, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/README.md'}], 'key_artifacts': [{'label': 'Functional Spec', 'path': 'SPEC.md', 'line': 8, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/agents/opencode/SPEC.md'}], 'issues': []}, {'file': 'agents/theory/AGENTS.md', 'parent': {'label': 'Theory', 'path': '../AGENTS.md', 'line': 4, 'is_generic': False}, 'children': [], 'navigation_links': [{'label': 'Human Documentation', 'text': 'README.md', 'path': 'README.md', 'line': 30, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/agents/theory/README.md'}, {'label': 'Functional Specification', 'text': 'SPEC.md', 'path': 'SPEC.md', 'line': 31, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/agents/theory/SPEC.md'}, {'label': '📁 Parent Directory', 'text': 'agents', 'path': '../README.md', 'line': 32, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/agents/README.md'}, {'label': '🏠 Project Root', 'text': 'README', 'path': '../../../../README.md', 'line': 33, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/README.md'}], 'key_artifacts': [{'label': 'Functional Spec', 'path': 'SPEC.md', 'line': 8, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/agents/theory/SPEC.md'}], 'issues': []}, {'file': 'api/AGENTS.md', 'parent': {'label': 'Repository Root', 'path': '../AGENTS.md', 'line': 4, 'is_generic': False}, 'children': [{'label': 'documentation', 'path': 'documentation/AGENTS.md', 'line': 6, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/api/documentation/AGENTS.md'}], 'navigation_links': [{'label': 'Human Documentation', 'text': 'README.md', 'path': 'README.md', 'line': 32, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/api/README.md'}, {'label': 'Functional Specification', 'text': 'SPEC.md', 'path': 'SPEC.md', 'line': 33, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/api/SPEC.md'}, {'label': '📁 Parent Directory', 'text': 'codomyrmex', 'path': '../README.md', 'line': 34, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/README.md'}, {'label': '🏠 Project Root', 'text': 'README', 'path': '../../../README.md', 'line': 35, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/README.md'}], 'key_artifacts': [{'label': 'Functional Spec', 'path': 'SPEC.md', 'line': 9, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/api/SPEC.md'}], 'issues': []}, {'file': 'api/documentation/AGENTS.md', 'parent': {'label': 'Documentation', 'path': '../AGENTS.md', 'line': 4, 'is_generic': False}, 'children': [], 'navigation_links': [{'label': 'Human Documentation', 'text': 'README.md', 'path': 'README.md', 'line': 32, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/api/documentation/README.md'}, {'label': 'Functional Specification', 'text': 'SPEC.md', 'path': 'SPEC.md', 'line': 33, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/api/documentation/SPEC.md'}, {'label': '📁 Parent Directory', 'text': 'api', 'path': '../README.md', 'line': 34, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/api/README.md'}, {'label': '🏠 Project Root', 'text': 'README', 'path': '../../../../README.md', 'line': 35, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/README.md'}], 'key_artifacts': [{'label': 'Functional Spec', 'path': 'SPEC.md', 'line': 8, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/api/documentation/SPEC.md'}], 'issues': []}, {'file': 'api/standardization/AGENTS.md', 'parent': {'label': 'Standardization', 'path': '../AGENTS.md', 'line': 4, 'is_generic': False}, 'children': [], 'navigation_links': [{'label': 'Human Documentation', 'text': 'README.md', 'path': 'README.md', 'line': 33, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/api/standardization/README.md'}, {'label': 'Functional Specification', 'text': 'SPEC.md', 'path': 'SPEC.md', 'line': 34, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/api/standardization/SPEC.md'}, {'label': '📁 Parent Directory', 'text': 'api', 'path': '../README.md', 'line': 35, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/api/README.md'}, {'label': '🏠 Project Root', 'text': 'README', 'path': '../../../../README.md', 'line': 36, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/README.md'}], 'key_artifacts': [{'label': 'Functional Spec', 'path': 'SPEC.md', 'line': 8, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/api/standardization/SPEC.md'}], 'issues': []}, {'file': 'auth/AGENTS.md', 'parent': {'label': 'Repository Root', 'path': '../AGENTS.md', 'line': 4, 'is_generic': False}, 'children': [], 'navigation_links': [{'label': 'Human Documentation', 'text': 'README.md', 'path': 'README.md', 'line': 31, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/auth/README.md'}, {'label': 'Functional Specification', 'text': 'SPEC.md', 'path': 'SPEC.md', 'line': 32, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/auth/SPEC.md'}, {'label': '📁 Parent Directory', 'text': 'codomyrmex', 'path': '../README.md', 'line': 33, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/README.md'}, {'label': '🏠 Project Root', 'text': 'README', 'path': '../../../README.md', 'line': 34, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/README.md'}], 'key_artifacts': [{'label': 'Functional Spec', 'path': 'SPEC.md', 'line': 8, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/auth/SPEC.md'}], 'issues': []}, {'file': 'build_synthesis/AGENTS.md', 'parent': {'label': 'Repository Root', 'path': '../AGENTS.md', 'line': 4, 'is_generic': False}, 'children': [], 'navigation_links': [{'label': 'Human Documentation', 'text': 'README.md', 'path': 'README.md', 'line': 36, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/build_synthesis/README.md'}, {'label': 'Functional Specification', 'text': 'SPEC.md', 'path': 'SPEC.md', 'line': 37, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/build_synthesis/SPEC.md'}, {'label': '📁 Parent Directory', 'text': 'codomyrmex', 'path': '../README.md', 'line': 38, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/README.md'}, {'label': '🏠 Project Root', 'text': 'README', 'path': '../../../README.md', 'line': 39, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/README.md'}], 'key_artifacts': [{'label': 'Functional Spec', 'path': 'SPEC.md', 'line': 8, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/build_synthesis/SPEC.md'}], 'issues': []}, {'file': 'cache/AGENTS.md', 'parent': {'label': 'Repository Root', 'path': '../AGENTS.md', 'line': 4, 'is_generic': False}, 'children': [{'label': 'backends', 'path': 'backends/AGENTS.md', 'line': 6, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/cache/backends/AGENTS.md'}], 'navigation_links': [{'label': 'Human Documentation', 'text': 'README.md', 'path': 'README.md', 'line': 32, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/cache/README.md'}, {'label': 'Functional Specification', 'text': 'SPEC.md', 'path': 'SPEC.md', 'line': 33, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/cache/SPEC.md'}, {'label': '📁 Parent Directory', 'text': 'codomyrmex', 'path': '../README.md', 'line': 34, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/README.md'}, {'label': '🏠 Project Root', 'text': 'README', 'path': '../../../README.md', 'line': 35, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/README.md'}], 'key_artifacts': [{'label': 'Functional Spec', 'path': 'SPEC.md', 'line': 8, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/cache/SPEC.md'}], 'issues': []}, {'file': 'cache/backends/AGENTS.md', 'parent': {'label': 'Backends', 'path': '../AGENTS.md', 'line': 4, 'is_generic': False}, 'children': [], 'navigation_links': [{'label': 'Human Documentation', 'text': 'README.md', 'path': 'README.md', 'line': 31, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/cache/backends/README.md'}, {'label': 'Functional Specification', 'text': 'SPEC.md', 'path': 'SPEC.md', 'line': 32, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/cache/backends/SPEC.md'}, {'label': '📁 Parent Directory', 'text': 'cache', 'path': '../README.md', 'line': 33, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/cache/README.md'}, {'label': '🏠 Project Root', 'text': 'README', 'path': '../../../../README.md', 'line': 34, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/README.md'}], 'key_artifacts': [{'label': 'Functional Spec', 'path': 'SPEC.md', 'line': 8, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/cache/backends/SPEC.md'}], 'issues': []}, {'file': 'cerebrum/AGENTS.md', 'parent': {'label': 'Repository Root', 'path': '../AGENTS.md', 'line': 4, 'is_generic': False}, 'children': [{'label': 'scripts', 'path': 'scripts/AGENTS.md', 'line': 6, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/cerebrum/scripts/AGENTS.md'}], 'navigation_links': [{'label': 'Human Documentation', 'text': 'README.md', 'path': 'README.md', 'line': 51, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/cerebrum/README.md'}, {'label': 'Functional Specification', 'text': 'SPEC.md', 'path': 'SPEC.md', 'line': 52, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/cerebrum/SPEC.md'}, {'label': '📁 Parent Directory', 'text': 'codomyrmex', 'path': '../README.md', 'line': 53, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/README.md'}, {'label': '🏠 Project Root', 'text': 'README', 'path': '../../../README.md', 'line': 54, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/README.md'}], 'key_artifacts': [{'label': 'Functional Spec', 'path': 'SPEC.md', 'line': 8, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/cerebrum/SPEC.md'}], 'issues': []}, {'file': 'cerebrum/scripts/AGENTS.md', 'parent': {'label': 'Scripts Root', 'path': '../AGENTS.md', 'line': 4, 'is_generic': False}, 'children': [], 'navigation_links': [{'label': 'Human Documentation', 'text': 'README.md', 'path': 'README.md', 'line': 28, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/cerebrum/scripts/README.md'}, {'label': 'Functional Specification', 'text': 'SPEC.md', 'path': 'SPEC.md', 'line': 29, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/cerebrum/scripts/SPEC.md'}, {'label': '📁 Parent Directory', 'text': 'cerebrum', 'path': '../README.md', 'line': 30, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/cerebrum/README.md'}, {'label': '🏠 Project Root', 'text': 'README', 'path': '../../../../README.md', 'line': 31, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/README.md'}], 'key_artifacts': [{'label': 'Functional Spec', 'path': 'SPEC.md', 'line': 8, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/cerebrum/scripts/SPEC.md'}], 'issues': []}, {'file': 'ci_cd_automation/AGENTS.md', 'parent': {'label': 'Repository Root', 'path': '../AGENTS.md', 'line': 4, 'is_generic': False}, 'children': [], 'navigation_links': [{'label': 'Human Documentation', 'text': 'README.md', 'path': 'README.md', 'line': 35, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/ci_cd_automation/README.md'}, {'label': 'Functional Specification', 'text': 'SPEC.md', 'path': 'SPEC.md', 'line': 36, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/ci_cd_automation/SPEC.md'}, {'label': '📁 Parent Directory', 'text': 'codomyrmex', 'path': '../README.md', 'line': 37, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/README.md'}, {'label': '🏠 Project Root', 'text': 'README', 'path': '../../../README.md', 'line': 38, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/README.md'}], 'key_artifacts': [{'label': 'Functional Spec', 'path': 'SPEC.md', 'line': 8, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/ci_cd_automation/SPEC.md'}], 'issues': []}, {'file': 'cloud/AGENTS.md', 'parent': {'label': 'Repository Root', 'path': '../AGENTS.md', 'line': 4, 'is_generic': False}, 'children': [{'label': 'coda_io', 'path': 'coda_io/AGENTS.md', 'line': 6, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/cloud/coda_io/AGENTS.md'}], 'navigation_links': [{'label': 'Human Documentation', 'text': 'README.md', 'path': 'README.md', 'line': 29, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/cloud/README.md'}, {'label': 'Functional Specification', 'text': 'SPEC.md', 'path': 'SPEC.md', 'line': 30, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/cloud/SPEC.md'}, {'label': '📁 Parent Directory', 'text': 'codomyrmex', 'path': '../README.md', 'line': 31, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/README.md'}, {'label': '🏠 Project Root', 'text': 'README', 'path': '../../../README.md', 'line': 32, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/README.md'}], 'key_artifacts': [{'label': 'Functional Spec', 'path': 'SPEC.md', 'line': 8, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/cloud/SPEC.md'}], 'issues': []}, {'file': 'cloud/coda_io/AGENTS.md', 'parent': {'label': 'Coda Io', 'path': '../AGENTS.md', 'line': 4, 'is_generic': False}, 'children': [], 'navigation_links': [{'label': 'Human Documentation', 'text': 'README.md', 'path': 'README.md', 'line': 31, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/cloud/coda_io/README.md'}, {'label': 'Functional Specification', 'text': 'SPEC.md', 'path': 'SPEC.md', 'line': 32, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/cloud/coda_io/SPEC.md'}, {'label': '📁 Parent Directory', 'text': 'cloud', 'path': '../README.md', 'line': 33, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/cloud/README.md'}, {'label': '🏠 Project Root', 'text': 'README', 'path': '../../../../README.md', 'line': 34, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/README.md'}], 'key_artifacts': [{'label': 'Functional Spec', 'path': 'SPEC.md', 'line': 8, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/cloud/coda_io/SPEC.md'}], 'issues': []}, {'file': 'coding/AGENTS.md', 'parent': {'label': 'Repository Root', 'path': '../AGENTS.md', 'line': 4, 'is_generic': False}, 'children': [{'label': 'debugging', 'path': 'debugging/AGENTS.md', 'line': 6, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/coding/debugging/AGENTS.md'}], 'navigation_links': [{'label': 'Human Documentation', 'text': 'README.md', 'path': 'README.md', 'line': 39, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/coding/README.md'}, {'label': 'Functional Specification', 'text': 'SPEC.md', 'path': 'SPEC.md', 'line': 40, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/coding/SPEC.md'}, {'label': '📁 Parent Directory', 'text': 'codomyrmex', 'path': '../README.md', 'line': 41, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/README.md'}, {'label': '🏠 Project Root', 'text': 'README', 'path': '../../../README.md', 'line': 42, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/README.md'}], 'key_artifacts': [{'label': 'Functional Spec', 'path': 'SPEC.md', 'line': 12, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/coding/SPEC.md'}], 'issues': []}, {'file': 'coding/debugging/AGENTS.md', 'parent': {'label': 'Debugging', 'path': '../AGENTS.md', 'line': 4, 'is_generic': False}, 'children': [], 'navigation_links': [{'label': 'Human Documentation', 'text': 'README.md', 'path': 'README.md', 'line': 32, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/coding/debugging/README.md'}, {'label': 'Functional Specification', 'text': 'SPEC.md', 'path': 'SPEC.md', 'line': 33, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/coding/debugging/SPEC.md'}, {'label': '📁 Parent Directory', 'text': 'coding', 'path': '../README.md', 'line': 34, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/coding/README.md'}, {'label': '🏠 Project Root', 'text': 'README', 'path': '../../../../README.md', 'line': 35, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/README.md'}], 'key_artifacts': [{'label': 'Functional Spec', 'path': 'SPEC.md', 'line': 8, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/coding/debugging/SPEC.md'}], 'issues': []}, {'file': 'coding/execution/AGENTS.md', 'parent': {'label': 'Execution', 'path': '../AGENTS.md', 'line': 4, 'is_generic': False}, 'children': [], 'navigation_links': [{'label': 'Human Documentation', 'text': 'README.md', 'path': 'README.md', 'line': 31, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/coding/execution/README.md'}, {'label': 'Functional Specification', 'text': 'SPEC.md', 'path': 'SPEC.md', 'line': 32, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/coding/execution/SPEC.md'}, {'label': '📁 Parent Directory', 'text': 'coding', 'path': '../README.md', 'line': 33, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/coding/README.md'}, {'label': '🏠 Project Root', 'text': 'README', 'path': '../../../../README.md', 'line': 34, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/README.md'}], 'key_artifacts': [{'label': 'Functional Spec', 'path': 'SPEC.md', 'line': 8, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/coding/execution/SPEC.md'}], 'issues': []}, {'file': 'coding/monitoring/AGENTS.md', 'parent': {'label': 'Monitoring', 'path': '../AGENTS.md', 'line': 4, 'is_generic': False}, 'children': [], 'navigation_links': [{'label': 'Human Documentation', 'text': 'README.md', 'path': 'README.md', 'line': 31, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/coding/monitoring/README.md'}, {'label': 'Functional Specification', 'text': 'SPEC.md', 'path': 'SPEC.md', 'line': 32, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/coding/monitoring/SPEC.md'}, {'label': '📁 Parent Directory', 'text': 'coding', 'path': '../README.md', 'line': 33, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/coding/README.md'}, {'label': '🏠 Project Root', 'text': 'README', 'path': '../../../../README.md', 'line': 34, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/README.md'}], 'key_artifacts': [{'label': 'Functional Spec', 'path': 'SPEC.md', 'line': 8, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/coding/monitoring/SPEC.md'}], 'issues': []}, {'file': 'coding/review/AGENTS.md', 'parent': {'label': 'Review', 'path': '../AGENTS.md', 'line': 4, 'is_generic': False}, 'children': [], 'navigation_links': [{'label': 'Human Documentation', 'text': 'README.md', 'path': 'README.md', 'line': 32, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/coding/review/README.md'}, {'label': 'Functional Specification', 'text': 'SPEC.md', 'path': 'SPEC.md', 'line': 33, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/coding/review/SPEC.md'}, {'label': '📁 Parent Directory', 'text': 'coding', 'path': '../README.md', 'line': 34, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/coding/README.md'}, {'label': '🏠 Project Root', 'text': 'README', 'path': '../../../../README.md', 'line': 35, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/README.md'}], 'key_artifacts': [{'label': 'Functional Spec', 'path': 'SPEC.md', 'line': 8, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/coding/review/SPEC.md'}], 'issues': []}, {'file': 'coding/sandbox/AGENTS.md', 'parent': {'label': 'Sandbox', 'path': '../AGENTS.md', 'line': 4, 'is_generic': False}, 'children': [], 'navigation_links': [{'label': 'Human Documentation', 'text': 'README.md', 'path': 'README.md', 'line': 32, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/coding/sandbox/README.md'}, {'label': 'Functional Specification', 'text': 'SPEC.md', 'path': 'SPEC.md', 'line': 33, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/coding/sandbox/SPEC.md'}, {'label': '📁 Parent Directory', 'text': 'coding', 'path': '../README.md', 'line': 34, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/coding/README.md'}, {'label': '🏠 Project Root', 'text': 'README', 'path': '../../../../README.md', 'line': 35, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/README.md'}], 'key_artifacts': [{'label': 'Functional Spec', 'path': 'SPEC.md', 'line': 8, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/coding/sandbox/SPEC.md'}], 'issues': []}, {'file': 'compression/AGENTS.md', 'parent': {'label': 'Repository Root', 'path': '../AGENTS.md', 'line': 4, 'is_generic': False}, 'children': [], 'navigation_links': [{'label': 'Human Documentation', 'text': 'README.md', 'path': 'README.md', 'line': 30, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/compression/README.md'}, {'label': 'Functional Specification', 'text': 'SPEC.md', 'path': 'SPEC.md', 'line': 31, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/compression/SPEC.md'}, {'label': '📁 Parent Directory', 'text': 'codomyrmex', 'path': '../README.md', 'line': 32, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/README.md'}, {'label': '🏠 Project Root', 'text': 'README', 'path': '../../../README.md', 'line': 33, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/README.md'}], 'key_artifacts': [{'label': 'Functional Spec', 'path': 'SPEC.md', 'line': 8, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/compression/SPEC.md'}], 'issues': []}, {'file': 'config_management/AGENTS.md', 'parent': {'label': 'Repository Root', 'path': '../AGENTS.md', 'line': 4, 'is_generic': False}, 'children': [], 'navigation_links': [{'label': 'Human Documentation', 'text': 'README.md', 'path': 'README.md', 'line': 36, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/config_management/README.md'}, {'label': 'Functional Specification', 'text': 'SPEC.md', 'path': 'SPEC.md', 'line': 37, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/config_management/SPEC.md'}, {'label': '📁 Parent Directory', 'text': 'codomyrmex', 'path': '../README.md', 'line': 38, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/README.md'}, {'label': '🏠 Project Root', 'text': 'README', 'path': '../../../README.md', 'line': 39, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/README.md'}], 'key_artifacts': [{'label': 'Functional Spec', 'path': 'SPEC.md', 'line': 8, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/config_management/SPEC.md'}], 'issues': []}, {'file': 'containerization/AGENTS.md', 'parent': {'label': 'Repository Root', 'path': '../AGENTS.md', 'line': 4, 'is_generic': False}, 'children': [], 'navigation_links': [{'label': 'Human Documentation', 'text': 'README.md', 'path': 'README.md', 'line': 37, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/containerization/README.md'}, {'label': 'Functional Specification', 'text': 'SPEC.md', 'path': 'SPEC.md', 'line': 38, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/containerization/SPEC.md'}, {'label': '📁 Parent Directory', 'text': 'codomyrmex', 'path': '../README.md', 'line': 39, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/README.md'}, {'label': '🏠 Project Root', 'text': 'README', 'path': '../../../README.md', 'line': 40, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/README.md'}], 'key_artifacts': [{'label': 'Functional Spec', 'path': 'SPEC.md', 'line': 8, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/containerization/SPEC.md'}], 'issues': []}, {'file': 'data_visualization/AGENTS.md', 'parent': {'label': 'Repository Root', 'path': '../AGENTS.md', 'line': 4, 'is_generic': False}, 'children': [], 'navigation_links': [{'label': 'Human Documentation', 'text': 'README.md', 'path': 'README.md', 'line': 44, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/data_visualization/README.md'}, {'label': 'Functional Specification', 'text': 'SPEC.md', 'path': 'SPEC.md', 'line': 45, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/data_visualization/SPEC.md'}, {'label': '📁 Parent Directory', 'text': 'codomyrmex', 'path': '../README.md', 'line': 46, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/README.md'}, {'label': '🏠 Project Root', 'text': 'README', 'path': '../../../README.md', 'line': 47, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/README.md'}], 'key_artifacts': [{'label': 'Functional Spec', 'path': 'SPEC.md', 'line': 8, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/data_visualization/SPEC.md'}], 'issues': []}, {'file': 'database_management/AGENTS.md', 'parent': {'label': 'Repository Root', 'path': '../AGENTS.md', 'line': 4, 'is_generic': False}, 'children': [], 'navigation_links': [{'label': 'Human Documentation', 'text': 'README.md', 'path': 'README.md', 'line': 35, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/database_management/README.md'}, {'label': 'Functional Specification', 'text': 'SPEC.md', 'path': 'SPEC.md', 'line': 36, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/database_management/SPEC.md'}, {'label': '📁 Parent Directory', 'text': 'codomyrmex', 'path': '../README.md', 'line': 37, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/README.md'}, {'label': '🏠 Project Root', 'text': 'README', 'path': '../../../README.md', 'line': 38, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/README.md'}], 'key_artifacts': [{'label': 'Functional Spec', 'path': 'SPEC.md', 'line': 8, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/database_management/SPEC.md'}], 'issues': []}, {'file': 'documentation/AGENTS.md', 'parent': {'label': 'Repository Root', 'path': '../AGENTS.md', 'line': 4, 'is_generic': False}, 'children': [{'label': 'docs', 'path': 'docs/AGENTS.md', 'line': 6, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/documentation/docs/AGENTS.md'}], 'navigation_links': [{'label': 'Human Documentation', 'text': 'README.md', 'path': 'README.md', 'line': 53, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/documentation/README.md'}, {'label': 'Functional Specification', 'text': 'SPEC.md', 'path': 'SPEC.md', 'line': 54, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/documentation/SPEC.md'}, {'label': '📁 Parent Directory', 'text': 'codomyrmex', 'path': '../README.md', 'line': 55, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/README.md'}, {'label': '🏠 Project Root', 'text': 'README', 'path': '../../../README.md', 'line': 56, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/README.md'}], 'key_artifacts': [{'label': 'Functional Spec', 'path': 'SPEC.md', 'line': 11, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/documentation/SPEC.md'}], 'issues': []}, {'file': 'documentation/docs/AGENTS.md', 'parent': {'label': 'Documentation Root', 'path': '../AGENTS.md', 'line': 4, 'is_generic': False}, 'children': [{'label': 'development', 'path': 'development/AGENTS.md', 'line': 6, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/documentation/docs/development/AGENTS.md'}], 'navigation_links': [{'label': 'Human Documentation', 'text': 'README.md', 'path': 'README.md', 'line': 36, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/documentation/docs/README.md'}, {'label': 'Functional Specification', 'text': 'SPEC.md', 'path': 'SPEC.md', 'line': 37, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/documentation/docs/SPEC.md'}, {'label': '📁 Parent Directory', 'text': 'documentation', 'path': '../README.md', 'line': 38, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/documentation/README.md'}, {'label': '🏠 Project Root', 'text': 'README', 'path': '../../../../README.md', 'line': 39, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/README.md'}], 'key_artifacts': [{'label': 'Functional Spec', 'path': 'SPEC.md', 'line': 11, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/documentation/docs/SPEC.md'}], 'issues': []}, {'file': 'documentation/docs/development/AGENTS.md', 'parent': {'label': 'Development', 'path': '../AGENTS.md', 'line': 4, 'is_generic': False}, 'children': [], 'navigation_links': [{'label': 'Human Documentation', 'text': 'README.md', 'path': 'README.md', 'line': 30, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/documentation/docs/development/README.md'}, {'label': 'Functional Specification', 'text': 'SPEC.md', 'path': 'SPEC.md', 'line': 31, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/documentation/docs/development/SPEC.md'}, {'label': '📁 Parent Directory', 'text': 'docs', 'path': '../README.md', 'line': 32, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/documentation/docs/README.md'}, {'label': '🏠 Project Root', 'text': 'README', 'path': '../../../../../README.md', 'line': 33, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/README.md'}], 'key_artifacts': [{'label': 'Functional Spec', 'path': 'SPEC.md', 'line': 8, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/documentation/docs/development/SPEC.md'}], 'issues': []}, {'file': 'documentation/docs/modules/AGENTS.md', 'parent': {'label': 'Modules', 'path': '../AGENTS.md', 'line': 4, 'is_generic': False}, 'children': [{'label': 'ai_code_editing', 'path': 'ai_code_editing/AGENTS.md', 'line': 6, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/documentation/docs/modules/ai_code_editing/AGENTS.md'}], 'navigation_links': [{'label': 'Human Documentation', 'text': 'README.md', 'path': 'README.md', 'line': 47, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/documentation/docs/modules/README.md'}, {'label': 'Functional Specification', 'text': 'SPEC.md', 'path': 'SPEC.md', 'line': 48, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/documentation/docs/modules/SPEC.md'}, {'label': '📁 Parent Directory', 'text': 'docs', 'path': '../README.md', 'line': 49, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/documentation/docs/README.md'}, {'label': '🏠 Project Root', 'text': 'README', 'path': '../../../../../README.md', 'line': 50, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/README.md'}], 'key_artifacts': [{'label': 'Functional Spec', 'path': 'SPEC.md', 'line': 18, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/documentation/docs/modules/SPEC.md'}], 'issues': []}, {'file': 'documentation/docs/modules/ai_code_editing/AGENTS.md', 'parent': {'label': 'Ai Code Editing', 'path': '../AGENTS.md', 'line': 4, 'is_generic': False}, 'children': [{'label': 'docs', 'path': 'docs/AGENTS.md', 'line': 6, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/documentation/docs/modules/ai_code_editing/docs/AGENTS.md'}], 'navigation_links': [{'label': 'Human Documentation', 'text': 'README.md', 'path': 'README.md', 'line': 33, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/documentation/docs/modules/ai_code_editing/README.md'}, {'label': 'Functional Specification', 'text': 'SPEC.md', 'path': 'SPEC.md', 'line': 34, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/documentation/docs/modules/ai_code_editing/SPEC.md'}, {'label': '📁 Parent Directory', 'text': 'modules', 'path': '../README.md', 'line': 35, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/documentation/docs/modules/README.md'}, {'label': '🏠 Project Root', 'text': 'README', 'path': '../../../../../../README.md', 'line': 36, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/README.md'}], 'key_artifacts': [{'label': 'Functional Spec', 'path': 'SPEC.md', 'line': 8, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/documentation/docs/modules/ai_code_editing/SPEC.md'}], 'issues': []}, {'file': 'documentation/docs/modules/ai_code_editing/docs/AGENTS.md', 'parent': {'label': 'Documentation Root', 'path': '../AGENTS.md', 'line': 4, 'is_generic': False}, 'children': [{'label': 'tutorials', 'path': 'tutorials/AGENTS.md', 'line': 6, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/documentation/docs/modules/ai_code_editing/docs/tutorials/AGENTS.md'}], 'navigation_links': [{'label': 'Human Documentation', 'text': 'README.md', 'path': 'README.md', 'line': 29, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/documentation/docs/modules/ai_code_editing/docs/README.md'}, {'label': 'Functional Specification', 'text': 'SPEC.md', 'path': 'SPEC.md', 'line': 30, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/documentation/docs/modules/ai_code_editing/docs/SPEC.md'}, {'label': '📁 Parent Directory', 'text': 'ai_code_editing', 'path': '../README.md', 'line': 31, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/documentation/docs/modules/ai_code_editing/README.md'}, {'label': '🏠 Project Root', 'text': 'README', 'path': '../../../../../../../README.md', 'line': 32, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/README.md'}], 'key_artifacts': [{'label': 'Functional Spec', 'path': 'SPEC.md', 'line': 8, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/documentation/docs/modules/ai_code_editing/docs/SPEC.md'}], 'issues': []}, {'file': 'documentation/docs/modules/ai_code_editing/docs/tutorials/AGENTS.md', 'parent': {'label': 'Tutorials', 'path': '../AGENTS.md', 'line': 4, 'is_generic': False}, 'children': [], 'navigation_links': [{'label': 'Human Documentation', 'text': 'README.md', 'path': 'README.md', 'line': 28, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/documentation/docs/modules/ai_code_editing/docs/tutorials/README.md'}, {'label': 'Functional Specification', 'text': 'SPEC.md', 'path': 'SPEC.md', 'line': 29, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/documentation/docs/modules/ai_code_editing/docs/tutorials/SPEC.md'}, {'label': '📁 Parent Directory', 'text': 'docs', 'path': '../README.md', 'line': 30, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/documentation/docs/modules/ai_code_editing/docs/README.md'}, {'label': '🏠 Project Root', 'text': 'README', 'path': '../../../../../../../../README.md', 'line': 31, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/README.md'}], 'key_artifacts': [{'label': 'Functional Spec', 'path': 'SPEC.md', 'line': 8, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/documentation/docs/modules/ai_code_editing/docs/tutorials/SPEC.md'}], 'issues': []}, {'file': 'documentation/docs/modules/build_synthesis/AGENTS.md', 'parent': {'label': 'Build Synthesis', 'path': '../AGENTS.md', 'line': 4, 'is_generic': False}, 'children': [{'label': 'docs', 'path': 'docs/AGENTS.md', 'line': 6, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/documentation/docs/modules/build_synthesis/docs/AGENTS.md'}], 'navigation_links': [{'label': 'Human Documentation', 'text': 'README.md', 'path': 'README.md', 'line': 33, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/documentation/docs/modules/build_synthesis/README.md'}, {'label': 'Functional Specification', 'text': 'SPEC.md', 'path': 'SPEC.md', 'line': 34, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/documentation/docs/modules/build_synthesis/SPEC.md'}, {'label': '📁 Parent Directory', 'text': 'modules', 'path': '../README.md', 'line': 35, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/documentation/docs/modules/README.md'}, {'label': '🏠 Project Root', 'text': 'README', 'path': '../../../../../../README.md', 'line': 36, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/README.md'}], 'key_artifacts': [{'label': 'Functional Spec', 'path': 'SPEC.md', 'line': 8, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/documentation/docs/modules/build_synthesis/SPEC.md'}], 'issues': []}, {'file': 'documentation/docs/modules/build_synthesis/docs/AGENTS.md', 'parent': {'label': 'Documentation Root', 'path': '../AGENTS.md', 'line': 4, 'is_generic': False}, 'children': [{'label': 'tutorials', 'path': 'tutorials/AGENTS.md', 'line': 6, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/documentation/docs/modules/build_synthesis/docs/tutorials/AGENTS.md'}], 'navigation_links': [{'label': 'Human Documentation', 'text': 'README.md', 'path': 'README.md', 'line': 29, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/documentation/docs/modules/build_synthesis/docs/README.md'}, {'label': 'Functional Specification', 'text': 'SPEC.md', 'path': 'SPEC.md', 'line': 30, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/documentation/docs/modules/build_synthesis/docs/SPEC.md'}, {'label': '📁 Parent Directory', 'text': 'build_synthesis', 'path': '../README.md', 'line': 31, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/documentation/docs/modules/build_synthesis/README.md'}, {'label': '🏠 Project Root', 'text': 'README', 'path': '../../../../../../../README.md', 'line': 32, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/README.md'}], 'key_artifacts': [{'label': 'Functional Spec', 'path': 'SPEC.md', 'line': 8, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/documentation/docs/modules/build_synthesis/docs/SPEC.md'}], 'issues': []}, {'file': 'documentation/docs/modules/build_synthesis/docs/tutorials/AGENTS.md', 'parent': {'label': 'Tutorials', 'path': '../AGENTS.md', 'line': 4, 'is_generic': False}, 'children': [], 'navigation_links': [{'label': 'Human Documentation', 'text': 'README.md', 'path': 'README.md', 'line': 28, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/documentation/docs/modules/build_synthesis/docs/tutorials/README.md'}, {'label': 'Functional Specification', 'text': 'SPEC.md', 'path': 'SPEC.md', 'line': 29, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/documentation/docs/modules/build_synthesis/docs/tutorials/SPEC.md'}, {'label': '📁 Parent Directory', 'text': 'docs', 'path': '../README.md', 'line': 30, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/documentation/docs/modules/build_synthesis/docs/README.md'}, {'label': '🏠 Project Root', 'text': 'README', 'path': '../../../../../../../../README.md', 'line': 31, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/README.md'}], 'key_artifacts': [{'label': 'Functional Spec', 'path': 'SPEC.md', 'line': 8, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/documentation/docs/modules/build_synthesis/docs/tutorials/SPEC.md'}], 'issues': []}, {'file': 'documentation/docs/modules/data_visualization/AGENTS.md', 'parent': {'label': 'Data Visualization', 'path': '../AGENTS.md', 'line': 4, 'is_generic': False}, 'children': [{'label': 'docs', 'path': 'docs/AGENTS.md', 'line': 6, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/documentation/docs/modules/data_visualization/docs/AGENTS.md'}], 'navigation_links': [{'label': 'Human Documentation', 'text': 'README.md', 'path': 'README.md', 'line': 33, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/documentation/docs/modules/data_visualization/README.md'}, {'label': 'Functional Specification', 'text': 'SPEC.md', 'path': 'SPEC.md', 'line': 34, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/documentation/docs/modules/data_visualization/SPEC.md'}, {'label': '📁 Parent Directory', 'text': 'modules', 'path': '../README.md', 'line': 35, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/documentation/docs/modules/README.md'}, {'label': '🏠 Project Root', 'text': 'README', 'path': '../../../../../../README.md', 'line': 36, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/README.md'}], 'key_artifacts': [{'label': 'Functional Spec', 'path': 'SPEC.md', 'line': 8, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/documentation/docs/modules/data_visualization/SPEC.md'}], 'issues': []}, {'file': 'documentation/docs/modules/data_visualization/docs/AGENTS.md', 'parent': {'label': 'Documentation Root', 'path': '../AGENTS.md', 'line': 4, 'is_generic': False}, 'children': [{'label': 'tutorials', 'path': 'tutorials/AGENTS.md', 'line': 6, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/documentation/docs/modules/data_visualization/docs/tutorials/AGENTS.md'}], 'navigation_links': [{'label': 'Human Documentation', 'text': 'README.md', 'path': 'README.md', 'line': 29, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/documentation/docs/modules/data_visualization/docs/README.md'}, {'label': 'Functional Specification', 'text': 'SPEC.md', 'path': 'SPEC.md', 'line': 30, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/documentation/docs/modules/data_visualization/docs/SPEC.md'}, {'label': '📁 Parent Directory', 'text': 'data_visualization', 'path': '../README.md', 'line': 31, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/documentation/docs/modules/data_visualization/README.md'}, {'label': '🏠 Project Root', 'text': 'README', 'path': '../../../../../../../README.md', 'line': 32, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/README.md'}], 'key_artifacts': [{'label': 'Functional Spec', 'path': 'SPEC.md', 'line': 8, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/documentation/docs/modules/data_visualization/docs/SPEC.md'}], 'issues': []}, {'file': 'documentation/docs/modules/data_visualization/docs/tutorials/AGENTS.md', 'parent': {'label': 'Tutorials', 'path': '../AGENTS.md', 'line': 4, 'is_generic': False}, 'children': [], 'navigation_links': [{'label': 'Human Documentation', 'text': 'README.md', 'path': 'README.md', 'line': 32, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/documentation/docs/modules/data_visualization/docs/tutorials/README.md'}, {'label': 'Functional Specification', 'text': 'SPEC.md', 'path': 'SPEC.md', 'line': 33, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/documentation/docs/modules/data_visualization/docs/tutorials/SPEC.md'}, {'label': '📁 Parent Directory', 'text': 'docs', 'path': '../README.md', 'line': 34, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/documentation/docs/modules/data_visualization/docs/README.md'}, {'label': '🏠 Project Root', 'text': 'README', 'path': '../../../../../../../../README.md', 'line': 35, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/README.md'}], 'key_artifacts': [{'label': 'Functional Spec', 'path': 'SPEC.md', 'line': 8, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/documentation/docs/modules/data_visualization/docs/tutorials/SPEC.md'}], 'issues': []}, {'file': 'documentation/docs/modules/environment_setup/AGENTS.md', 'parent': {'label': 'Environment Setup', 'path': '../AGENTS.md', 'line': 4, 'is_generic': False}, 'children': [{'label': 'docs', 'path': 'docs/AGENTS.md', 'line': 6, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/documentation/docs/modules/environment_setup/docs/AGENTS.md'}], 'navigation_links': [{'label': 'Human Documentation', 'text': 'README.md', 'path': 'README.md', 'line': 33, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/documentation/docs/modules/environment_setup/README.md'}, {'label': 'Functional Specification', 'text': 'SPEC.md', 'path': 'SPEC.md', 'line': 34, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/documentation/docs/modules/environment_setup/SPEC.md'}, {'label': '📁 Parent Directory', 'text': 'modules', 'path': '../README.md', 'line': 35, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/documentation/docs/modules/README.md'}, {'label': '🏠 Project Root', 'text': 'README', 'path': '../../../../../../README.md', 'line': 36, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/README.md'}], 'key_artifacts': [{'label': 'Functional Spec', 'path': 'SPEC.md', 'line': 8, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/documentation/docs/modules/environment_setup/SPEC.md'}], 'issues': []}, {'file': 'documentation/docs/modules/environment_setup/docs/AGENTS.md', 'parent': {'label': 'Documentation Root', 'path': '../AGENTS.md', 'line': 4, 'is_generic': False}, 'children': [{'label': 'tutorials', 'path': 'tutorials/AGENTS.md', 'line': 6, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/documentation/docs/modules/environment_setup/docs/tutorials/AGENTS.md'}], 'navigation_links': [{'label': 'Human Documentation', 'text': 'README.md', 'path': 'README.md', 'line': 29, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/documentation/docs/modules/environment_setup/docs/README.md'}, {'label': 'Functional Specification', 'text': 'SPEC.md', 'path': 'SPEC.md', 'line': 30, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/documentation/docs/modules/environment_setup/docs/SPEC.md'}, {'label': '📁 Parent Directory', 'text': 'environment_setup', 'path': '../README.md', 'line': 31, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/documentation/docs/modules/environment_setup/README.md'}, {'label': '🏠 Project Root', 'text': 'README', 'path': '../../../../../../../README.md', 'line': 32, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/README.md'}], 'key_artifacts': [{'label': 'Functional Spec', 'path': 'SPEC.md', 'line': 8, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/documentation/docs/modules/environment_setup/docs/SPEC.md'}], 'issues': []}, {'file': 'documentation/docs/modules/environment_setup/docs/tutorials/AGENTS.md', 'parent': {'label': 'Tutorials', 'path': '../AGENTS.md', 'line': 4, 'is_generic': False}, 'children': [], 'navigation_links': [{'label': 'Human Documentation', 'text': 'README.md', 'path': 'README.md', 'line': 26, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/documentation/docs/modules/environment_setup/docs/tutorials/README.md'}, {'label': 'Functional Specification', 'text': 'SPEC.md', 'path': 'SPEC.md', 'line': 27, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/documentation/docs/modules/environment_setup/docs/tutorials/SPEC.md'}, {'label': '📁 Parent Directory', 'text': 'docs', 'path': '../README.md', 'line': 28, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/documentation/docs/modules/environment_setup/docs/README.md'}, {'label': '🏠 Project Root', 'text': 'README', 'path': '../../../../../../../../README.md', 'line': 29, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/README.md'}], 'key_artifacts': [{'label': 'Functional Spec', 'path': 'SPEC.md', 'line': 8, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/documentation/docs/modules/environment_setup/docs/tutorials/SPEC.md'}], 'issues': []}, {'file': 'documentation/docs/modules/git_operations/AGENTS.md', 'parent': {'label': 'Git Operations', 'path': '../AGENTS.md', 'line': 4, 'is_generic': False}, 'children': [{'label': 'docs', 'path': 'docs/AGENTS.md', 'line': 6, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/documentation/docs/modules/git_operations/docs/AGENTS.md'}], 'navigation_links': [{'label': 'Human Documentation', 'text': 'README.md', 'path': 'README.md', 'line': 33, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/documentation/docs/modules/git_operations/README.md'}, {'label': 'Functional Specification', 'text': 'SPEC.md', 'path': 'SPEC.md', 'line': 34, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/documentation/docs/modules/git_operations/SPEC.md'}, {'label': '📁 Parent Directory', 'text': 'modules', 'path': '../README.md', 'line': 35, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/documentation/docs/modules/README.md'}, {'label': '🏠 Project Root', 'text': 'README', 'path': '../../../../../../README.md', 'line': 36, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/README.md'}], 'key_artifacts': [{'label': 'Functional Spec', 'path': 'SPEC.md', 'line': 8, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/documentation/docs/modules/git_operations/SPEC.md'}], 'issues': []}, {'file': 'documentation/docs/modules/git_operations/docs/AGENTS.md', 'parent': {'label': 'Documentation Root', 'path': '../AGENTS.md', 'line': 4, 'is_generic': False}, 'children': [{'label': 'tutorials', 'path': 'tutorials/AGENTS.md', 'line': 6, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/documentation/docs/modules/git_operations/docs/tutorials/AGENTS.md'}], 'navigation_links': [{'label': 'Human Documentation', 'text': 'README.md', 'path': 'README.md', 'line': 29, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/documentation/docs/modules/git_operations/docs/README.md'}, {'label': 'Functional Specification', 'text': 'SPEC.md', 'path': 'SPEC.md', 'line': 30, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/documentation/docs/modules/git_operations/docs/SPEC.md'}, {'label': '📁 Parent Directory', 'text': 'git_operations', 'path': '../README.md', 'line': 31, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/documentation/docs/modules/git_operations/README.md'}, {'label': '🏠 Project Root', 'text': 'README', 'path': '../../../../../../../README.md', 'line': 32, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/README.md'}], 'key_artifacts': [{'label': 'Functional Spec', 'path': 'SPEC.md', 'line': 8, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/documentation/docs/modules/git_operations/docs/SPEC.md'}], 'issues': []}, {'file': 'documentation/docs/modules/git_operations/docs/tutorials/AGENTS.md', 'parent': {'label': 'Tutorials', 'path': '../AGENTS.md', 'line': 4, 'is_generic': False}, 'children': [], 'navigation_links': [{'label': 'Human Documentation', 'text': 'README.md', 'path': 'README.md', 'line': 27, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/documentation/docs/modules/git_operations/docs/tutorials/README.md'}, {'label': 'Functional Specification', 'text': 'SPEC.md', 'path': 'SPEC.md', 'line': 28, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/documentation/docs/modules/git_operations/docs/tutorials/SPEC.md'}, {'label': '📁 Parent Directory', 'text': 'docs', 'path': '../README.md', 'line': 29, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/documentation/docs/modules/git_operations/docs/README.md'}, {'label': '🏠 Project Root', 'text': 'README', 'path': '../../../../../../../../README.md', 'line': 30, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/README.md'}], 'key_artifacts': [{'label': 'Functional Spec', 'path': 'SPEC.md', 'line': 8, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/documentation/docs/modules/git_operations/docs/tutorials/SPEC.md'}], 'issues': []}, {'file': 'documentation/docs/modules/logging_monitoring/AGENTS.md', 'parent': {'label': 'Logging Monitoring', 'path': '../AGENTS.md', 'line': 4, 'is_generic': False}, 'children': [{'label': 'docs', 'path': 'docs/AGENTS.md', 'line': 6, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/documentation/docs/modules/logging_monitoring/docs/AGENTS.md'}], 'navigation_links': [{'label': 'Human Documentation', 'text': 'README.md', 'path': 'README.md', 'line': 33, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/documentation/docs/modules/logging_monitoring/README.md'}, {'label': 'Functional Specification', 'text': 'SPEC.md', 'path': 'SPEC.md', 'line': 34, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/documentation/docs/modules/logging_monitoring/SPEC.md'}, {'label': '📁 Parent Directory', 'text': 'modules', 'path': '../README.md', 'line': 35, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/documentation/docs/modules/README.md'}, {'label': '🏠 Project Root', 'text': 'README', 'path': '../../../../../../README.md', 'line': 36, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/README.md'}], 'key_artifacts': [{'label': 'Functional Spec', 'path': 'SPEC.md', 'line': 8, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/documentation/docs/modules/logging_monitoring/SPEC.md'}], 'issues': []}, {'file': 'documentation/docs/modules/logging_monitoring/docs/AGENTS.md', 'parent': {'label': 'Documentation Root', 'path': '../AGENTS.md', 'line': 4, 'is_generic': False}, 'children': [{'label': 'tutorials', 'path': 'tutorials/AGENTS.md', 'line': 6, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/documentation/docs/modules/logging_monitoring/docs/tutorials/AGENTS.md'}], 'navigation_links': [{'label': 'Human Documentation', 'text': 'README.md', 'path': 'README.md', 'line': 29, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/documentation/docs/modules/logging_monitoring/docs/README.md'}, {'label': 'Functional Specification', 'text': 'SPEC.md', 'path': 'SPEC.md', 'line': 30, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/documentation/docs/modules/logging_monitoring/docs/SPEC.md'}, {'label': '📁 Parent Directory', 'text': 'logging_monitoring', 'path': '../README.md', 'line': 31, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/documentation/docs/modules/logging_monitoring/README.md'}, {'label': '🏠 Project Root', 'text': 'README', 'path': '../../../../../../../README.md', 'line': 32, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/README.md'}], 'key_artifacts': [{'label': 'Functional Spec', 'path': 'SPEC.md', 'line': 8, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/documentation/docs/modules/logging_monitoring/docs/SPEC.md'}], 'issues': []}, {'file': 'documentation/docs/modules/logging_monitoring/docs/tutorials/AGENTS.md', 'parent': {'label': 'Tutorials', 'path': '../AGENTS.md', 'line': 4, 'is_generic': False}, 'children': [], 'navigation_links': [{'label': 'Human Documentation', 'text': 'README.md', 'path': 'README.md', 'line': 26, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/documentation/docs/modules/logging_monitoring/docs/tutorials/README.md'}, {'label': 'Functional Specification', 'text': 'SPEC.md', 'path': 'SPEC.md', 'line': 27, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/documentation/docs/modules/logging_monitoring/docs/tutorials/SPEC.md'}, {'label': '📁 Parent Directory', 'text': 'docs', 'path': '../README.md', 'line': 28, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/documentation/docs/modules/logging_monitoring/docs/README.md'}, {'label': '🏠 Project Root', 'text': 'README', 'path': '../../../../../../../../README.md', 'line': 29, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/README.md'}], 'key_artifacts': [{'label': 'Functional Spec', 'path': 'SPEC.md', 'line': 8, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/documentation/docs/modules/logging_monitoring/docs/tutorials/SPEC.md'}], 'issues': []}, {'file': 'documentation/docs/modules/model_context_protocol/AGENTS.md', 'parent': {'label': 'Model Context Protocol', 'path': '../AGENTS.md', 'line': 4, 'is_generic': False}, 'children': [{'label': 'docs', 'path': 'docs/AGENTS.md', 'line': 6, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/documentation/docs/modules/model_context_protocol/docs/AGENTS.md'}], 'navigation_links': [{'label': 'Human Documentation', 'text': 'README.md', 'path': 'README.md', 'line': 33, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/documentation/docs/modules/model_context_protocol/README.md'}, {'label': 'Functional Specification', 'text': 'SPEC.md', 'path': 'SPEC.md', 'line': 34, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/documentation/docs/modules/model_context_protocol/SPEC.md'}, {'label': '📁 Parent Directory', 'text': 'modules', 'path': '../README.md', 'line': 35, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/documentation/docs/modules/README.md'}, {'label': '🏠 Project Root', 'text': 'README', 'path': '../../../../../../README.md', 'line': 36, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/README.md'}], 'key_artifacts': [{'label': 'Functional Spec', 'path': 'SPEC.md', 'line': 8, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/documentation/docs/modules/model_context_protocol/SPEC.md'}], 'issues': []}, {'file': 'documentation/docs/modules/model_context_protocol/docs/AGENTS.md', 'parent': {'label': 'Documentation Root', 'path': '../AGENTS.md', 'line': 4, 'is_generic': False}, 'children': [{'label': 'tutorials', 'path': 'tutorials/AGENTS.md', 'line': 6, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/documentation/docs/modules/model_context_protocol/docs/tutorials/AGENTS.md'}], 'navigation_links': [{'label': 'Human Documentation', 'text': 'README.md', 'path': 'README.md', 'line': 29, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/documentation/docs/modules/model_context_protocol/docs/README.md'}, {'label': 'Functional Specification', 'text': 'SPEC.md', 'path': 'SPEC.md', 'line': 30, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/documentation/docs/modules/model_context_protocol/docs/SPEC.md'}, {'label': '📁 Parent Directory', 'text': 'model_context_protocol', 'path': '../README.md', 'line': 31, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/documentation/docs/modules/model_context_protocol/README.md'}, {'label': '🏠 Project Root', 'text': 'README', 'path': '../../../../../../../README.md', 'line': 32, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/README.md'}], 'key_artifacts': [{'label': 'Functional Spec', 'path': 'SPEC.md', 'line': 8, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/documentation/docs/modules/model_context_protocol/docs/SPEC.md'}], 'issues': []}, {'file': 'documentation/docs/modules/model_context_protocol/docs/tutorials/AGENTS.md', 'parent': {'label': 'Tutorials', 'path': '../AGENTS.md', 'line': 4, 'is_generic': False}, 'children': [], 'navigation_links': [{'label': 'Human Documentation', 'text': 'README.md', 'path': 'README.md', 'line': 27, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/documentation/docs/modules/model_context_protocol/docs/tutorials/README.md'}, {'label': 'Functional Specification', 'text': 'SPEC.md', 'path': 'SPEC.md', 'line': 28, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/documentation/docs/modules/model_context_protocol/docs/tutorials/SPEC.md'}, {'label': '📁 Parent Directory', 'text': 'docs', 'path': '../README.md', 'line': 29, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/documentation/docs/modules/model_context_protocol/docs/README.md'}, {'label': '🏠 Project Root', 'text': 'README', 'path': '../../../../../../../../README.md', 'line': 30, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/README.md'}], 'key_artifacts': [{'label': 'Functional Spec', 'path': 'SPEC.md', 'line': 8, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/documentation/docs/modules/model_context_protocol/docs/tutorials/SPEC.md'}], 'issues': []}, {'file': 'documentation/docs/modules/module_template/AGENTS.md', 'parent': {'label': 'Module Template', 'path': '../AGENTS.md', 'line': 4, 'is_generic': False}, 'children': [{'label': 'docs', 'path': 'docs/AGENTS.md', 'line': 6, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/documentation/docs/modules/module_template/docs/AGENTS.md'}], 'navigation_links': [{'label': 'Human Documentation', 'text': 'README.md', 'path': 'README.md', 'line': 32, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/documentation/docs/modules/module_template/README.md'}, {'label': 'Functional Specification', 'text': 'SPEC.md', 'path': 'SPEC.md', 'line': 33, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/documentation/docs/modules/module_template/SPEC.md'}, {'label': '📁 Parent Directory', 'text': 'modules', 'path': '../README.md', 'line': 34, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/documentation/docs/modules/README.md'}, {'label': '🏠 Project Root', 'text': 'README', 'path': '../../../../../../README.md', 'line': 35, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/README.md'}], 'key_artifacts': [{'label': 'Functional Spec', 'path': 'SPEC.md', 'line': 8, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/documentation/docs/modules/module_template/SPEC.md'}], 'issues': []}, {'file': 'documentation/docs/modules/module_template/docs/AGENTS.md', 'parent': {'label': 'Documentation Root', 'path': '../AGENTS.md', 'line': 4, 'is_generic': False}, 'children': [{'label': 'tutorials', 'path': 'tutorials/AGENTS.md', 'line': 6, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/documentation/docs/modules/module_template/docs/tutorials/AGENTS.md'}], 'navigation_links': [{'label': 'Human Documentation', 'text': 'README.md', 'path': 'README.md', 'line': 29, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/documentation/docs/modules/module_template/docs/README.md'}, {'label': 'Functional Specification', 'text': 'SPEC.md', 'path': 'SPEC.md', 'line': 30, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/documentation/docs/modules/module_template/docs/SPEC.md'}, {'label': '📁 Parent Directory', 'text': 'module_template', 'path': '../README.md', 'line': 31, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/documentation/docs/modules/module_template/README.md'}, {'label': '🏠 Project Root', 'text': 'README', 'path': '../../../../../../../README.md', 'line': 32, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/README.md'}], 'key_artifacts': [{'label': 'Functional Spec', 'path': 'SPEC.md', 'line': 8, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/documentation/docs/modules/module_template/docs/SPEC.md'}], 'issues': []}, {'file': 'documentation/docs/modules/module_template/docs/tutorials/AGENTS.md', 'parent': {'label': 'Tutorials', 'path': '../AGENTS.md', 'line': 4, 'is_generic': False}, 'children': [], 'navigation_links': [{'label': 'Human Documentation', 'text': 'README.md', 'path': 'README.md', 'line': 26, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/documentation/docs/modules/module_template/docs/tutorials/README.md'}, {'label': 'Functional Specification', 'text': 'SPEC.md', 'path': 'SPEC.md', 'line': 27, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/documentation/docs/modules/module_template/docs/tutorials/SPEC.md'}, {'label': '📁 Parent Directory', 'text': 'docs', 'path': '../README.md', 'line': 28, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/documentation/docs/modules/module_template/docs/README.md'}, {'label': '🏠 Project Root', 'text': 'README', 'path': '../../../../../../../../README.md', 'line': 29, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/README.md'}], 'key_artifacts': [{'label': 'Functional Spec', 'path': 'SPEC.md', 'line': 8, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/documentation/docs/modules/module_template/docs/tutorials/SPEC.md'}], 'issues': []}, {'file': 'documentation/docs/modules/pattern_matching/AGENTS.md', 'parent': {'label': 'Pattern Matching', 'path': '../AGENTS.md', 'line': 4, 'is_generic': False}, 'children': [{'label': 'docs', 'path': 'docs/AGENTS.md', 'line': 6, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/documentation/docs/modules/pattern_matching/docs/AGENTS.md'}], 'navigation_links': [{'label': 'Human Documentation', 'text': 'README.md', 'path': 'README.md', 'line': 40, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/documentation/docs/modules/pattern_matching/README.md'}, {'label': 'Functional Specification', 'text': 'SPEC.md', 'path': 'SPEC.md', 'line': 41, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/documentation/docs/modules/pattern_matching/SPEC.md'}, {'label': '📁 Parent Directory', 'text': 'modules', 'path': '../README.md', 'line': 42, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/documentation/docs/modules/README.md'}, {'label': '🏠 Project Root', 'text': 'README', 'path': '../../../../../../README.md', 'line': 43, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/README.md'}], 'key_artifacts': [{'label': 'Functional Spec', 'path': 'SPEC.md', 'line': 8, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/documentation/docs/modules/pattern_matching/SPEC.md'}], 'issues': []}, {'file': 'documentation/docs/modules/pattern_matching/docs/AGENTS.md', 'parent': {'label': 'Documentation Root', 'path': '../AGENTS.md', 'line': 4, 'is_generic': False}, 'children': [{'label': 'tutorials', 'path': 'tutorials/AGENTS.md', 'line': 6, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/documentation/docs/modules/pattern_matching/docs/tutorials/AGENTS.md'}], 'navigation_links': [{'label': 'Human Documentation', 'text': 'README.md', 'path': 'README.md', 'line': 29, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/documentation/docs/modules/pattern_matching/docs/README.md'}, {'label': 'Functional Specification', 'text': 'SPEC.md', 'path': 'SPEC.md', 'line': 30, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/documentation/docs/modules/pattern_matching/docs/SPEC.md'}, {'label': '📁 Parent Directory', 'text': 'pattern_matching', 'path': '../README.md', 'line': 31, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/documentation/docs/modules/pattern_matching/README.md'}, {'label': '🏠 Project Root', 'text': 'README', 'path': '../../../../../../../README.md', 'line': 32, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/README.md'}], 'key_artifacts': [{'label': 'Functional Spec', 'path': 'SPEC.md', 'line': 8, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/documentation/docs/modules/pattern_matching/docs/SPEC.md'}], 'issues': []}, {'file': 'documentation/docs/modules/pattern_matching/docs/tutorials/AGENTS.md', 'parent': {'label': 'Tutorials', 'path': '../AGENTS.md', 'line': 4, 'is_generic': False}, 'children': [], 'navigation_links': [{'label': 'Human Documentation', 'text': 'README.md', 'path': 'README.md', 'line': 26, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/documentation/docs/modules/pattern_matching/docs/tutorials/README.md'}, {'label': 'Functional Specification', 'text': 'SPEC.md', 'path': 'SPEC.md', 'line': 27, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/documentation/docs/modules/pattern_matching/docs/tutorials/SPEC.md'}, {'label': '📁 Parent Directory', 'text': 'docs', 'path': '../README.md', 'line': 28, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/documentation/docs/modules/pattern_matching/docs/README.md'}, {'label': '🏠 Project Root', 'text': 'README', 'path': '../../../../../../../../README.md', 'line': 29, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/README.md'}], 'key_artifacts': [{'label': 'Functional Spec', 'path': 'SPEC.md', 'line': 8, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/documentation/docs/modules/pattern_matching/docs/tutorials/SPEC.md'}], 'issues': []}, {'file': 'documentation/docs/modules/static_analysis/AGENTS.md', 'parent': {'label': 'Static Analysis', 'path': '../AGENTS.md', 'line': 4, 'is_generic': False}, 'children': [{'label': 'docs', 'path': 'docs/AGENTS.md', 'line': 6, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/documentation/docs/modules/static_analysis/docs/AGENTS.md'}], 'navigation_links': [{'label': 'Human Documentation', 'text': 'README.md', 'path': 'README.md', 'line': 33, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/documentation/docs/modules/static_analysis/README.md'}, {'label': 'Functional Specification', 'text': 'SPEC.md', 'path': 'SPEC.md', 'line': 34, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/documentation/docs/modules/static_analysis/SPEC.md'}, {'label': '📁 Parent Directory', 'text': 'modules', 'path': '../README.md', 'line': 35, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/documentation/docs/modules/README.md'}, {'label': '🏠 Project Root', 'text': 'README', 'path': '../../../../../../README.md', 'line': 36, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/README.md'}], 'key_artifacts': [{'label': 'Functional Spec', 'path': 'SPEC.md', 'line': 8, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/documentation/docs/modules/static_analysis/SPEC.md'}], 'issues': []}, {'file': 'documentation/docs/modules/static_analysis/docs/AGENTS.md', 'parent': {'label': 'Documentation Root', 'path': '../AGENTS.md', 'line': 4, 'is_generic': False}, 'children': [{'label': 'tutorials', 'path': 'tutorials/AGENTS.md', 'line': 6, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/documentation/docs/modules/static_analysis/docs/tutorials/AGENTS.md'}], 'navigation_links': [{'label': 'Human Documentation', 'text': 'README.md', 'path': 'README.md', 'line': 29, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/documentation/docs/modules/static_analysis/docs/README.md'}, {'label': 'Functional Specification', 'text': 'SPEC.md', 'path': 'SPEC.md', 'line': 30, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/documentation/docs/modules/static_analysis/docs/SPEC.md'}, {'label': '📁 Parent Directory', 'text': 'static_analysis', 'path': '../README.md', 'line': 31, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/documentation/docs/modules/static_analysis/README.md'}, {'label': '🏠 Project Root', 'text': 'README', 'path': '../../../../../../../README.md', 'line': 32, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/README.md'}], 'key_artifacts': [{'label': 'Functional Spec', 'path': 'SPEC.md', 'line': 8, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/documentation/docs/modules/static_analysis/docs/SPEC.md'}], 'issues': []}, {'file': 'documentation/docs/modules/static_analysis/docs/tutorials/AGENTS.md', 'parent': {'label': 'Tutorials', 'path': '../AGENTS.md', 'line': 4, 'is_generic': False}, 'children': [], 'navigation_links': [{'label': 'Human Documentation', 'text': 'README.md', 'path': 'README.md', 'line': 26, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/documentation/docs/modules/static_analysis/docs/tutorials/README.md'}, {'label': 'Functional Specification', 'text': 'SPEC.md', 'path': 'SPEC.md', 'line': 27, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/documentation/docs/modules/static_analysis/docs/tutorials/SPEC.md'}, {'label': '📁 Parent Directory', 'text': 'docs', 'path': '../README.md', 'line': 28, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/documentation/docs/modules/static_analysis/docs/README.md'}, {'label': '🏠 Project Root', 'text': 'README', 'path': '../../../../../../../../README.md', 'line': 29, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/README.md'}], 'key_artifacts': [{'label': 'Functional Spec', 'path': 'SPEC.md', 'line': 8, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/documentation/docs/modules/static_analysis/docs/tutorials/SPEC.md'}], 'issues': []}, {'file': 'documentation/docs/modules/template/AGENTS.md', 'parent': {'label': 'Template', 'path': '../AGENTS.md', 'line': 4, 'is_generic': False}, 'children': [{'label': 'docs', 'path': 'docs/AGENTS.md', 'line': 6, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/documentation/docs/modules/template/docs/AGENTS.md'}], 'navigation_links': [{'label': 'Human Documentation', 'text': 'README.md', 'path': 'README.md', 'line': 32, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/documentation/docs/modules/template/README.md'}, {'label': 'Functional Specification', 'text': 'SPEC.md', 'path': 'SPEC.md', 'line': 33, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/documentation/docs/modules/template/SPEC.md'}, {'label': '📁 Parent Directory', 'text': 'modules', 'path': '../README.md', 'line': 34, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/documentation/docs/modules/README.md'}, {'label': '🏠 Project Root', 'text': 'README', 'path': '../../../../../../README.md', 'line': 35, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/README.md'}], 'key_artifacts': [{'label': 'Functional Spec', 'path': 'SPEC.md', 'line': 8, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/documentation/docs/modules/template/SPEC.md'}], 'issues': []}, {'file': 'documentation/docs/modules/template/docs/AGENTS.md', 'parent': {'label': 'Documentation Root', 'path': '../AGENTS.md', 'line': 4, 'is_generic': False}, 'children': [{'label': 'tutorials', 'path': 'tutorials/AGENTS.md', 'line': 6, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/documentation/docs/modules/template/docs/tutorials/AGENTS.md'}], 'navigation_links': [{'label': 'Human Documentation', 'text': 'README.md', 'path': 'README.md', 'line': 29, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/documentation/docs/modules/template/docs/README.md'}, {'label': 'Functional Specification', 'text': 'SPEC.md', 'path': 'SPEC.md', 'line': 30, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/documentation/docs/modules/template/docs/SPEC.md'}, {'label': '📁 Parent Directory', 'text': 'template', 'path': '../README.md', 'line': 31, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/documentation/docs/modules/template/README.md'}, {'label': '🏠 Project Root', 'text': 'README', 'path': '../../../../../../../README.md', 'line': 32, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/README.md'}], 'key_artifacts': [{'label': 'Functional Spec', 'path': 'SPEC.md', 'line': 8, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/documentation/docs/modules/template/docs/SPEC.md'}], 'issues': []}, {'file': 'documentation/docs/modules/template/docs/tutorials/AGENTS.md', 'parent': {'label': 'Tutorials', 'path': '../AGENTS.md', 'line': 4, 'is_generic': False}, 'children': [], 'navigation_links': [{'label': 'Human Documentation', 'text': 'README.md', 'path': 'README.md', 'line': 26, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/documentation/docs/modules/template/docs/tutorials/README.md'}, {'label': 'Functional Specification', 'text': 'SPEC.md', 'path': 'SPEC.md', 'line': 27, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/documentation/docs/modules/template/docs/tutorials/SPEC.md'}, {'label': '📁 Parent Directory', 'text': 'docs', 'path': '../README.md', 'line': 28, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/documentation/docs/modules/template/docs/README.md'}, {'label': '🏠 Project Root', 'text': 'README', 'path': '../../../../../../../../README.md', 'line': 29, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/README.md'}], 'key_artifacts': [{'label': 'Functional Spec', 'path': 'SPEC.md', 'line': 8, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/documentation/docs/modules/template/docs/tutorials/SPEC.md'}], 'issues': []}, {'file': 'documentation/docs/project/AGENTS.md', 'parent': {'label': 'Project', 'path': '../AGENTS.md', 'line': 4, 'is_generic': False}, 'children': [], 'navigation_links': [{'label': 'Human Documentation', 'text': 'README.md', 'path': 'README.md', 'line': 33, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/documentation/docs/project/README.md'}, {'label': 'Functional Specification', 'text': 'SPEC.md', 'path': 'SPEC.md', 'line': 34, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/documentation/docs/project/SPEC.md'}, {'label': '📁 Parent Directory', 'text': 'docs', 'path': '../README.md', 'line': 35, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/documentation/docs/README.md'}, {'label': '🏠 Project Root', 'text': 'README', 'path': '../../../../../README.md', 'line': 36, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/README.md'}], 'key_artifacts': [{'label': 'Functional Spec', 'path': 'SPEC.md', 'line': 8, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/documentation/docs/project/SPEC.md'}], 'issues': []}, {'file': 'documentation/docs/tutorials/AGENTS.md', 'parent': {'label': 'Tutorials', 'path': '../AGENTS.md', 'line': 4, 'is_generic': False}, 'children': [], 'navigation_links': [{'label': 'Human Documentation', 'text': 'README.md', 'path': 'README.md', 'line': 26, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/documentation/docs/tutorials/README.md'}, {'label': 'Functional Specification', 'text': 'SPEC.md', 'path': 'SPEC.md', 'line': 27, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/documentation/docs/tutorials/SPEC.md'}, {'label': '📁 Parent Directory', 'text': 'docs', 'path': '../README.md', 'line': 28, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/documentation/docs/README.md'}, {'label': '🏠 Project Root', 'text': 'README', 'path': '../../../../../README.md', 'line': 29, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/README.md'}], 'key_artifacts': [{'label': 'Functional Spec', 'path': 'SPEC.md', 'line': 8, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/documentation/docs/tutorials/SPEC.md'}], 'issues': []}, {'file': 'documentation/scripts/AGENTS.md', 'parent': {'label': 'Scripts Root', 'path': '../AGENTS.md', 'line': 4, 'is_generic': False}, 'children': [], 'navigation_links': [{'label': 'Human Documentation', 'text': 'README.md', 'path': 'README.md', 'line': 120, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/documentation/scripts/README.md'}, {'label': 'Functional Specification', 'text': 'SPEC.md', 'path': 'SPEC.md', 'line': 121, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/documentation/scripts/SPEC.md'}, {'label': '📁 Parent Directory', 'text': 'documentation', 'path': '../README.md', 'line': 122, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/documentation/README.md'}, {'label': '🏠 Project Root', 'text': 'README', 'path': '../../../../README.md', 'line': 123, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/README.md'}], 'key_artifacts': [{'label': 'Functional Spec', 'path': 'SPEC.md', 'line': 8, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/documentation/scripts/SPEC.md'}], 'issues': []}, {'file': 'documentation/src/AGENTS.md', 'parent': {'label': 'Source Root', 'path': '../AGENTS.md', 'line': 4, 'is_generic': False}, 'children': [{'label': 'css', 'path': 'css/AGENTS.md', 'line': 6, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/documentation/src/css/AGENTS.md'}], 'navigation_links': [{'label': 'Human Documentation', 'text': 'README.md', 'path': 'README.md', 'line': 27, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/documentation/src/README.md'}, {'label': 'Functional Specification', 'text': 'SPEC.md', 'path': 'SPEC.md', 'line': 28, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/documentation/src/SPEC.md'}, {'label': '📁 Parent Directory', 'text': 'documentation', 'path': '../README.md', 'line': 29, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/documentation/README.md'}, {'label': '🏠 Project Root', 'text': 'README', 'path': '../../../../README.md', 'line': 30, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/README.md'}], 'key_artifacts': [{'label': 'Functional Spec', 'path': 'SPEC.md', 'line': 8, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/documentation/src/SPEC.md'}], 'issues': []}, {'file': 'documentation/src/css/AGENTS.md', 'parent': {'label': 'Css', 'path': '../AGENTS.md', 'line': 4, 'is_generic': False}, 'children': [], 'navigation_links': [{'label': 'Human Documentation', 'text': 'README.md', 'path': 'README.md', 'line': 27, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/documentation/src/css/README.md'}, {'label': 'Functional Specification', 'text': 'SPEC.md', 'path': 'SPEC.md', 'line': 28, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/documentation/src/css/SPEC.md'}, {'label': '📁 Parent Directory', 'text': 'src', 'path': '../README.md', 'line': 29, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/documentation/src/README.md'}, {'label': '🏠 Project Root', 'text': 'README', 'path': '../../../../../README.md', 'line': 30, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/README.md'}], 'key_artifacts': [{'label': 'Functional Spec', 'path': 'SPEC.md', 'line': 8, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/documentation/src/css/SPEC.md'}], 'issues': []}, {'file': 'documentation/static/AGENTS.md', 'parent': {'label': 'Static', 'path': '../AGENTS.md', 'line': 4, 'is_generic': False}, 'children': [{'label': 'img', 'path': 'img/AGENTS.md', 'line': 6, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/documentation/static/img/AGENTS.md'}], 'navigation_links': [{'label': 'Human Documentation', 'text': 'README.md', 'path': 'README.md', 'line': 27, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/documentation/static/README.md'}, {'label': 'Functional Specification', 'text': 'SPEC.md', 'path': 'SPEC.md', 'line': 28, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/documentation/static/SPEC.md'}, {'label': '📁 Parent Directory', 'text': 'documentation', 'path': '../README.md', 'line': 29, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/documentation/README.md'}, {'label': '🏠 Project Root', 'text': 'README', 'path': '../../../../README.md', 'line': 30, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/README.md'}], 'key_artifacts': [{'label': 'Functional Spec', 'path': 'SPEC.md', 'line': 8, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/documentation/static/SPEC.md'}], 'issues': []}, {'file': 'documentation/static/img/AGENTS.md', 'parent': {'label': 'Img', 'path': '../AGENTS.md', 'line': 4, 'is_generic': False}, 'children': [], 'navigation_links': [{'label': 'Human Documentation', 'text': 'README.md', 'path': 'README.md', 'line': 29, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/documentation/static/img/README.md'}, {'label': 'Functional Specification', 'text': 'SPEC.md', 'path': 'SPEC.md', 'line': 30, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/documentation/static/img/SPEC.md'}, {'label': '📁 Parent Directory', 'text': 'static', 'path': '../README.md', 'line': 31, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/documentation/static/README.md'}, {'label': '🏠 Project Root', 'text': 'README', 'path': '../../../../../README.md', 'line': 32, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/README.md'}], 'key_artifacts': [{'label': 'Functional Spec', 'path': 'SPEC.md', 'line': 8, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/documentation/static/img/SPEC.md'}], 'issues': []}, {'file': 'documents/AGENTS.md', 'parent': {'label': 'Repository Root', 'path': '../AGENTS.md', 'line': 4, 'is_generic': False}, 'children': [{'label': 'core', 'path': 'core/AGENTS.md', 'line': 6, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/documents/core/AGENTS.md'}], 'navigation_links': [{'label': 'Human Documentation', 'text': 'README.md', 'path': 'README.md', 'line': 48, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/documents/README.md'}, {'label': 'Functional Specification', 'text': 'SPEC.md', 'path': 'SPEC.md', 'line': 49, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/documents/SPEC.md'}, {'label': '📁 Parent Directory', 'text': 'codomyrmex', 'path': '../README.md', 'line': 50, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/README.md'}, {'label': '🏠 Project Root', 'text': 'README', 'path': '../../../README.md', 'line': 51, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/README.md'}], 'key_artifacts': [{'label': 'Functional Spec', 'path': 'SPEC.md', 'line': 15, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/documents/SPEC.md'}], 'issues': []}, {'file': 'documents/core/AGENTS.md', 'parent': {'label': 'Core', 'path': '../AGENTS.md', 'line': 4, 'is_generic': False}, 'children': [], 'navigation_links': [{'label': 'Human Documentation', 'text': 'README.md', 'path': 'README.md', 'line': 32, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/documents/core/README.md'}, {'label': 'Functional Specification', 'text': 'SPEC.md', 'path': 'SPEC.md', 'line': 33, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/documents/core/SPEC.md'}, {'label': '📁 Parent Directory', 'text': 'documents', 'path': '../README.md', 'line': 34, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/documents/README.md'}, {'label': '🏠 Project Root', 'text': 'README', 'path': '../../../../README.md', 'line': 35, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/README.md'}], 'key_artifacts': [{'label': 'Functional Spec', 'path': 'SPEC.md', 'line': 8, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/documents/core/SPEC.md'}], 'issues': []}, {'file': 'documents/formats/AGENTS.md', 'parent': {'label': 'Formats', 'path': '../AGENTS.md', 'line': 4, 'is_generic': False}, 'children': [], 'navigation_links': [{'label': 'Human Documentation', 'text': 'README.md', 'path': 'README.md', 'line': 33, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/documents/formats/README.md'}, {'label': 'Functional Specification', 'text': 'SPEC.md', 'path': 'SPEC.md', 'line': 34, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/documents/formats/SPEC.md'}, {'label': '📁 Parent Directory', 'text': 'documents', 'path': '../README.md', 'line': 35, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/documents/README.md'}, {'label': '🏠 Project Root', 'text': 'README', 'path': '../../../../README.md', 'line': 36, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/README.md'}], 'key_artifacts': [{'label': 'Functional Spec', 'path': 'SPEC.md', 'line': 8, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/documents/formats/SPEC.md'}], 'issues': []}, {'file': 'documents/metadata/AGENTS.md', 'parent': {'label': 'Metadata', 'path': '../AGENTS.md', 'line': 4, 'is_generic': False}, 'children': [], 'navigation_links': [{'label': 'Human Documentation', 'text': 'README.md', 'path': 'README.md', 'line': 31, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/documents/metadata/README.md'}, {'label': 'Functional Specification', 'text': 'SPEC.md', 'path': 'SPEC.md', 'line': 32, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/documents/metadata/SPEC.md'}, {'label': '📁 Parent Directory', 'text': 'documents', 'path': '../README.md', 'line': 33, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/documents/README.md'}, {'label': '🏠 Project Root', 'text': 'README', 'path': '../../../../README.md', 'line': 34, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/README.md'}], 'key_artifacts': [{'label': 'Functional Spec', 'path': 'SPEC.md', 'line': 8, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/documents/metadata/SPEC.md'}], 'issues': []}, {'file': 'documents/models/AGENTS.md', 'parent': {'label': 'Models', 'path': '../AGENTS.md', 'line': 4, 'is_generic': False}, 'children': [], 'navigation_links': [{'label': 'Human Documentation', 'text': 'README.md', 'path': 'README.md', 'line': 30, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/documents/models/README.md'}, {'label': 'Functional Specification', 'text': 'SPEC.md', 'path': 'SPEC.md', 'line': 31, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/documents/models/SPEC.md'}, {'label': '📁 Parent Directory', 'text': 'documents', 'path': '../README.md', 'line': 32, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/documents/README.md'}, {'label': '🏠 Project Root', 'text': 'README', 'path': '../../../../README.md', 'line': 33, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/README.md'}], 'key_artifacts': [{'label': 'Functional Spec', 'path': 'SPEC.md', 'line': 8, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/documents/models/SPEC.md'}], 'issues': []}, {'file': 'documents/search/AGENTS.md', 'parent': {'label': 'Search', 'path': '../AGENTS.md', 'line': 4, 'is_generic': False}, 'children': [], 'navigation_links': [{'label': 'Human Documentation', 'text': 'README.md', 'path': 'README.md', 'line': 31, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/documents/search/README.md'}, {'label': 'Functional Specification', 'text': 'SPEC.md', 'path': 'SPEC.md', 'line': 32, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/documents/search/SPEC.md'}, {'label': '📁 Parent Directory', 'text': 'documents', 'path': '../README.md', 'line': 33, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/documents/README.md'}, {'label': '🏠 Project Root', 'text': 'README', 'path': '../../../../README.md', 'line': 34, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/README.md'}], 'key_artifacts': [{'label': 'Functional Spec', 'path': 'SPEC.md', 'line': 8, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/documents/search/SPEC.md'}], 'issues': []}, {'file': 'documents/templates/AGENTS.md', 'parent': {'label': 'Templates', 'path': '../AGENTS.md', 'line': 4, 'is_generic': False}, 'children': [], 'navigation_links': [{'label': 'Human Documentation', 'text': 'README.md', 'path': 'README.md', 'line': 26, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/documents/templates/README.md'}, {'label': 'Functional Specification', 'text': 'SPEC.md', 'path': 'SPEC.md', 'line': 27, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/documents/templates/SPEC.md'}, {'label': '📁 Parent Directory', 'text': 'documents', 'path': '../README.md', 'line': 28, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/documents/README.md'}, {'label': '🏠 Project Root', 'text': 'README', 'path': '../../../../README.md', 'line': 29, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/README.md'}], 'key_artifacts': [{'label': 'Functional Spec', 'path': 'SPEC.md', 'line': 8, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/documents/templates/SPEC.md'}], 'issues': []}, {'file': 'documents/transformation/AGENTS.md', 'parent': {'label': 'Transformation', 'path': '../AGENTS.md', 'line': 4, 'is_generic': False}, 'children': [], 'navigation_links': [{'label': 'Human Documentation', 'text': 'README.md', 'path': 'README.md', 'line': 32, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/documents/transformation/README.md'}, {'label': 'Functional Specification', 'text': 'SPEC.md', 'path': 'SPEC.md', 'line': 33, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/documents/transformation/SPEC.md'}, {'label': '📁 Parent Directory', 'text': 'documents', 'path': '../README.md', 'line': 34, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/documents/README.md'}, {'label': '🏠 Project Root', 'text': 'README', 'path': '../../../../README.md', 'line': 35, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/README.md'}], 'key_artifacts': [{'label': 'Functional Spec', 'path': 'SPEC.md', 'line': 8, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/documents/transformation/SPEC.md'}], 'issues': []}, {'file': 'documents/utils/AGENTS.md', 'parent': {'label': 'Utils', 'path': '../AGENTS.md', 'line': 4, 'is_generic': False}, 'children': [], 'navigation_links': [{'label': 'Human Documentation', 'text': 'README.md', 'path': 'README.md', 'line': 31, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/documents/utils/README.md'}, {'label': 'Functional Specification', 'text': 'SPEC.md', 'path': 'SPEC.md', 'line': 32, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/documents/utils/SPEC.md'}, {'label': '📁 Parent Directory', 'text': 'documents', 'path': '../README.md', 'line': 33, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/documents/README.md'}, {'label': '🏠 Project Root', 'text': 'README', 'path': '../../../../README.md', 'line': 34, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/README.md'}], 'key_artifacts': [{'label': 'Functional Spec', 'path': 'SPEC.md', 'line': 8, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/documents/utils/SPEC.md'}], 'issues': []}, {'file': 'encryption/AGENTS.md', 'parent': {'label': 'Repository Root', 'path': '../AGENTS.md', 'line': 4, 'is_generic': False}, 'children': [], 'navigation_links': [{'label': 'Human Documentation', 'text': 'README.md', 'path': 'README.md', 'line': 30, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/encryption/README.md'}, {'label': 'Functional Specification', 'text': 'SPEC.md', 'path': 'SPEC.md', 'line': 31, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/encryption/SPEC.md'}, {'label': '📁 Parent Directory', 'text': 'codomyrmex', 'path': '../README.md', 'line': 32, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/README.md'}, {'label': '🏠 Project Root', 'text': 'README', 'path': '../../../README.md', 'line': 33, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/README.md'}], 'key_artifacts': [{'label': 'Functional Spec', 'path': 'SPEC.md', 'line': 8, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/encryption/SPEC.md'}], 'issues': []}, {'file': 'environment_setup/AGENTS.md', 'parent': {'label': 'Repository Root', 'path': '../AGENTS.md', 'line': 4, 'is_generic': False}, 'children': [{'label': 'scripts', 'path': 'scripts/AGENTS.md', 'line': 6, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/environment_setup/scripts/AGENTS.md'}], 'navigation_links': [{'label': 'Human Documentation', 'text': 'README.md', 'path': 'README.md', 'line': 37, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/environment_setup/README.md'}, {'label': 'Functional Specification', 'text': 'SPEC.md', 'path': 'SPEC.md', 'line': 38, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/environment_setup/SPEC.md'}, {'label': '📁 Parent Directory', 'text': 'codomyrmex', 'path': '../README.md', 'line': 39, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/README.md'}, {'label': '🏠 Project Root', 'text': 'README', 'path': '../../../README.md', 'line': 40, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/README.md'}], 'key_artifacts': [{'label': 'Functional Spec', 'path': 'SPEC.md', 'line': 8, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/environment_setup/SPEC.md'}], 'issues': []}, {'file': 'environment_setup/scripts/AGENTS.md', 'parent': {'label': 'Scripts Root', 'path': '../AGENTS.md', 'line': 4, 'is_generic': False}, 'children': [], 'navigation_links': [{'label': 'Human Documentation', 'text': 'README.md', 'path': 'README.md', 'line': 29, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/environment_setup/scripts/README.md'}, {'label': 'Functional Specification', 'text': 'SPEC.md', 'path': 'SPEC.md', 'line': 30, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/environment_setup/scripts/SPEC.md'}, {'label': '📁 Parent Directory', 'text': 'environment_setup', 'path': '../README.md', 'line': 31, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/environment_setup/README.md'}, {'label': '🏠 Project Root', 'text': 'README', 'path': '../../../../README.md', 'line': 32, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/README.md'}], 'key_artifacts': [{'label': 'Functional Spec', 'path': 'SPEC.md', 'line': 8, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/environment_setup/scripts/SPEC.md'}], 'issues': []}, {'file': 'events/AGENTS.md', 'parent': {'label': 'Repository Root', 'path': '../AGENTS.md', 'line': 4, 'is_generic': False}, 'children': [], 'navigation_links': [{'label': 'Human Documentation', 'text': 'README.md', 'path': 'README.md', 'line': 33, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/events/README.md'}, {'label': 'Functional Specification', 'text': 'SPEC.md', 'path': 'SPEC.md', 'line': 34, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/events/SPEC.md'}, {'label': '📁 Parent Directory', 'text': 'codomyrmex', 'path': '../README.md', 'line': 35, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/README.md'}, {'label': '🏠 Project Root', 'text': 'README', 'path': '../../../README.md', 'line': 36, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/README.md'}], 'key_artifacts': [{'label': 'Functional Spec', 'path': 'SPEC.md', 'line': 8, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/events/SPEC.md'}], 'issues': []}, {'file': 'examples/AGENTS.md', 'parent': {'label': 'Repository Root', 'path': '../AGENTS.md', 'line': 4, 'is_generic': False}, 'children': [], 'navigation_links': [{'label': 'Human Documentation', 'text': 'README.md', 'path': 'README.md', 'line': 28, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/examples/README.md'}, {'label': 'Functional Specification', 'text': 'SPEC.md', 'path': 'SPEC.md', 'line': 29, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/examples/SPEC.md'}, {'label': '📁 Parent Directory', 'text': 'codomyrmex', 'path': '../README.md', 'line': 30, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/README.md'}, {'label': '🏠 Project Root', 'text': 'README', 'path': '../../../README.md', 'line': 31, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/README.md'}], 'key_artifacts': [{'label': 'Functional Spec', 'path': 'SPEC.md', 'line': 8, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/examples/SPEC.md'}], 'issues': []}, {'file': 'fpf/AGENTS.md', 'parent': {'label': 'Repository Root', 'path': '../AGENTS.md', 'line': 4, 'is_generic': False}, 'children': [], 'navigation_links': [{'label': 'Human Documentation', 'text': 'README.md', 'path': 'README.md', 'line': 48, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/fpf/README.md'}, {'label': 'Functional Specification', 'text': 'SPEC.md', 'path': 'SPEC.md', 'line': 49, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/fpf/SPEC.md'}, {'label': '📁 Parent Directory', 'text': 'codomyrmex', 'path': '../README.md', 'line': 50, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/README.md'}, {'label': '🏠 Project Root', 'text': 'README', 'path': '../../../README.md', 'line': 51, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/README.md'}], 'key_artifacts': [{'label': 'Functional Spec', 'path': 'SPEC.md', 'line': 8, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/fpf/SPEC.md'}], 'issues': []}, {'file': 'git_operations/AGENTS.md', 'parent': {'label': 'Repository Root', 'path': '../AGENTS.md', 'line': 4, 'is_generic': False}, 'children': [], 'navigation_links': [{'label': 'Human Documentation', 'text': 'README.md', 'path': 'README.md', 'line': 50, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/git_operations/README.md'}, {'label': 'Functional Specification', 'text': 'SPEC.md', 'path': 'SPEC.md', 'line': 51, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/git_operations/SPEC.md'}, {'label': '📁 Parent Directory', 'text': 'codomyrmex', 'path': '../README.md', 'line': 52, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/README.md'}, {'label': '🏠 Project Root', 'text': 'README', 'path': '../../../README.md', 'line': 53, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/README.md'}], 'key_artifacts': [{'label': 'Functional Spec', 'path': 'SPEC.md', 'line': 8, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/git_operations/SPEC.md'}], 'issues': []}, {'file': 'ide/AGENTS.md', 'parent': {'label': 'Repository Root', 'path': '../AGENTS.md', 'line': 4, 'is_generic': False}, 'children': [{'label': 'antigravity', 'path': 'antigravity/AGENTS.md', 'line': 6, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/ide/antigravity/AGENTS.md'}], 'navigation_links': [{'label': 'Human Documentation', 'text': 'README.md', 'path': 'README.md', 'line': 33, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/ide/README.md'}, {'label': 'Functional Specification', 'text': 'SPEC.md', 'path': 'SPEC.md', 'line': 34, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/ide/SPEC.md'}, {'label': '📁 Parent Directory', 'text': 'codomyrmex', 'path': '../README.md', 'line': 35, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/README.md'}, {'label': '🏠 Project Root', 'text': 'README', 'path': '../../../README.md', 'line': 36, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/README.md'}], 'key_artifacts': [{'label': 'Functional Spec', 'path': 'SPEC.md', 'line': 10, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/ide/SPEC.md'}], 'issues': []}, {'file': 'ide/antigravity/AGENTS.md', 'parent': {'label': 'Antigravity', 'path': '../AGENTS.md', 'line': 4, 'is_generic': False}, 'children': [], 'navigation_links': [{'label': 'Human Documentation', 'text': 'README.md', 'path': 'README.md', 'line': 28, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/ide/antigravity/README.md'}, {'label': 'Functional Specification', 'text': 'SPEC.md', 'path': 'SPEC.md', 'line': 29, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/ide/antigravity/SPEC.md'}, {'label': '📁 Parent Directory', 'text': 'ide', 'path': '../README.md', 'line': 30, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/ide/README.md'}, {'label': '🏠 Project Root', 'text': 'README', 'path': '../../../../README.md', 'line': 31, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/README.md'}], 'key_artifacts': [{'label': 'Functional Spec', 'path': 'SPEC.md', 'line': 8, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/ide/antigravity/SPEC.md'}], 'issues': []}, {'file': 'ide/cursor/AGENTS.md', 'parent': {'label': 'Cursor', 'path': '../AGENTS.md', 'line': 4, 'is_generic': False}, 'children': [], 'navigation_links': [{'label': 'Human Documentation', 'text': 'README.md', 'path': 'README.md', 'line': 28, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/ide/cursor/README.md'}, {'label': 'Functional Specification', 'text': 'SPEC.md', 'path': 'SPEC.md', 'line': 29, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/ide/cursor/SPEC.md'}, {'label': '📁 Parent Directory', 'text': 'ide', 'path': '../README.md', 'line': 30, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/ide/README.md'}, {'label': '🏠 Project Root', 'text': 'README', 'path': '../../../../README.md', 'line': 31, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/README.md'}], 'key_artifacts': [{'label': 'Functional Spec', 'path': 'SPEC.md', 'line': 8, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/ide/cursor/SPEC.md'}], 'issues': []}, {'file': 'ide/vscode/AGENTS.md', 'parent': {'label': 'Vscode', 'path': '../AGENTS.md', 'line': 4, 'is_generic': False}, 'children': [], 'navigation_links': [{'label': 'Human Documentation', 'text': 'README.md', 'path': 'README.md', 'line': 28, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/ide/vscode/README.md'}, {'label': 'Functional Specification', 'text': 'SPEC.md', 'path': 'SPEC.md', 'line': 29, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/ide/vscode/SPEC.md'}, {'label': '📁 Parent Directory', 'text': 'ide', 'path': '../README.md', 'line': 30, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/ide/README.md'}, {'label': '🏠 Project Root', 'text': 'README', 'path': '../../../../README.md', 'line': 31, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/README.md'}], 'key_artifacts': [{'label': 'Functional Spec', 'path': 'SPEC.md', 'line': 8, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/ide/vscode/SPEC.md'}], 'issues': []}, {'file': 'llm/AGENTS.md', 'parent': {'label': 'Repository Root', 'path': '../AGENTS.md', 'line': 4, 'is_generic': False}, 'children': [{'label': 'fabric', 'path': 'fabric/AGENTS.md', 'line': 6, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/llm/fabric/AGENTS.md'}], 'navigation_links': [{'label': 'Human Documentation', 'text': 'README.md', 'path': 'README.md', 'line': 36, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/llm/README.md'}, {'label': 'Functional Specification', 'text': 'SPEC.md', 'path': 'SPEC.md', 'line': 37, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/llm/SPEC.md'}, {'label': '📁 Parent Directory', 'text': 'codomyrmex', 'path': '../README.md', 'line': 38, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/README.md'}, {'label': '🏠 Project Root', 'text': 'README', 'path': '../../../README.md', 'line': 39, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/README.md'}], 'key_artifacts': [{'label': 'Functional Spec', 'path': 'SPEC.md', 'line': 11, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/llm/SPEC.md'}], 'issues': []}, {'file': 'llm/fabric/AGENTS.md', 'parent': {'label': 'Fabric', 'path': '../AGENTS.md', 'line': 4, 'is_generic': False}, 'children': [], 'navigation_links': [{'label': 'Human Documentation', 'text': 'README.md', 'path': 'README.md', 'line': 31, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/llm/fabric/README.md'}, {'label': 'Functional Specification', 'text': 'SPEC.md', 'path': 'SPEC.md', 'line': 32, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/llm/fabric/SPEC.md'}, {'label': '📁 Parent Directory', 'text': 'llm', 'path': '../README.md', 'line': 33, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/llm/README.md'}, {'label': '🏠 Project Root', 'text': 'README', 'path': '../../../../README.md', 'line': 34, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/README.md'}], 'key_artifacts': [{'label': 'Functional Spec', 'path': 'SPEC.md', 'line': 8, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/llm/fabric/SPEC.md'}], 'issues': []}, {'file': 'llm/ollama/AGENTS.md', 'parent': {'label': 'Ollama', 'path': '../AGENTS.md', 'line': 4, 'is_generic': False}, 'children': [], 'navigation_links': [{'label': 'Human Documentation', 'text': 'README.md', 'path': 'README.md', 'line': 37, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/llm/ollama/README.md'}, {'label': 'Functional Specification', 'text': 'SPEC.md', 'path': 'SPEC.md', 'line': 38, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/llm/ollama/SPEC.md'}, {'label': '📁 Parent Directory', 'text': 'llm', 'path': '../README.md', 'line': 39, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/llm/README.md'}, {'label': '🏠 Project Root', 'text': 'README', 'path': '../../../../README.md', 'line': 40, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/README.md'}], 'key_artifacts': [{'label': 'Functional Spec', 'path': 'SPEC.md', 'line': 8, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/llm/ollama/SPEC.md'}], 'issues': []}, {'file': 'llm/outputs/AGENTS.md', 'parent': {'label': 'Outputs', 'path': '../AGENTS.md', 'line': 4, 'is_generic': False}, 'children': [{'label': 'integration', 'path': 'integration/AGENTS.md', 'line': 6, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/llm/outputs/integration/AGENTS.md'}], 'navigation_links': [{'label': 'Human Documentation', 'text': 'README.md', 'path': 'README.md', 'line': 38, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/llm/outputs/README.md'}, {'label': 'Functional Specification', 'text': 'SPEC.md', 'path': 'SPEC.md', 'line': 39, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/llm/outputs/SPEC.md'}, {'label': '📁 Parent Directory', 'text': 'llm', 'path': '../README.md', 'line': 40, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/llm/README.md'}, {'label': '🏠 Project Root', 'text': 'README', 'path': '../../../../README.md', 'line': 41, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/README.md'}], 'key_artifacts': [{'label': 'Functional Spec', 'path': 'SPEC.md', 'line': 12, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/llm/outputs/SPEC.md'}], 'issues': []}, {'file': 'llm/outputs/integration/AGENTS.md', 'parent': {'label': 'Integration', 'path': '../AGENTS.md', 'line': 4, 'is_generic': False}, 'children': [], 'navigation_links': [{'label': 'Human Documentation', 'text': 'README.md', 'path': 'README.md', 'line': 28, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/llm/outputs/integration/README.md'}, {'label': 'Functional Specification', 'text': 'SPEC.md', 'path': 'SPEC.md', 'line': 29, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/llm/outputs/integration/SPEC.md'}, {'label': '📁 Parent Directory', 'text': 'outputs', 'path': '../README.md', 'line': 30, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/llm/outputs/README.md'}, {'label': '🏠 Project Root', 'text': 'README', 'path': '../../../../../README.md', 'line': 31, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/README.md'}], 'key_artifacts': [{'label': 'Functional Spec', 'path': 'SPEC.md', 'line': 8, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/llm/outputs/integration/SPEC.md'}], 'issues': []}, {'file': 'llm/outputs/llm_outputs/AGENTS.md', 'parent': {'label': 'Llm Outputs', 'path': '../AGENTS.md', 'line': 4, 'is_generic': False}, 'children': [], 'navigation_links': [{'label': 'Human Documentation', 'text': 'README.md', 'path': 'README.md', 'line': 32, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/llm/outputs/llm_outputs/README.md'}, {'label': 'Functional Specification', 'text': 'SPEC.md', 'path': 'SPEC.md', 'line': 33, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/llm/outputs/llm_outputs/SPEC.md'}, {'label': '📁 Parent Directory', 'text': 'outputs', 'path': '../README.md', 'line': 34, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/llm/outputs/README.md'}, {'label': '🏠 Project Root', 'text': 'README', 'path': '../../../../../README.md', 'line': 35, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/README.md'}], 'key_artifacts': [{'label': 'Functional Spec', 'path': 'SPEC.md', 'line': 8, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/llm/outputs/llm_outputs/SPEC.md'}], 'issues': []}, {'file': 'llm/outputs/performance/AGENTS.md', 'parent': {'label': 'Performance', 'path': '../AGENTS.md', 'line': 4, 'is_generic': False}, 'children': [], 'navigation_links': [{'label': 'Human Documentation', 'text': 'README.md', 'path': 'README.md', 'line': 32, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/llm/outputs/performance/README.md'}, {'label': 'Functional Specification', 'text': 'SPEC.md', 'path': 'SPEC.md', 'line': 33, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/llm/outputs/performance/SPEC.md'}, {'label': '📁 Parent Directory', 'text': 'outputs', 'path': '../README.md', 'line': 34, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/llm/outputs/README.md'}, {'label': '🏠 Project Root', 'text': 'README', 'path': '../../../../../README.md', 'line': 35, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/README.md'}], 'key_artifacts': [{'label': 'Functional Spec', 'path': 'SPEC.md', 'line': 8, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/llm/outputs/performance/SPEC.md'}], 'issues': []}, {'file': 'llm/outputs/reports/AGENTS.md', 'parent': {'label': 'Reports', 'path': '../AGENTS.md', 'line': 4, 'is_generic': False}, 'children': [], 'navigation_links': [{'label': 'Human Documentation', 'text': 'README.md', 'path': 'README.md', 'line': 27, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/llm/outputs/reports/README.md'}, {'label': 'Functional Specification', 'text': 'SPEC.md', 'path': 'SPEC.md', 'line': 28, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/llm/outputs/reports/SPEC.md'}, {'label': '📁 Parent Directory', 'text': 'outputs', 'path': '../README.md', 'line': 29, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/llm/outputs/README.md'}, {'label': '🏠 Project Root', 'text': 'README', 'path': '../../../../../README.md', 'line': 30, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/README.md'}], 'key_artifacts': [{'label': 'Functional Spec', 'path': 'SPEC.md', 'line': 8, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/llm/outputs/reports/SPEC.md'}], 'issues': []}, {'file': 'llm/outputs/test_results/AGENTS.md', 'parent': {'label': 'Test Results', 'path': '../AGENTS.md', 'line': 4, 'is_generic': False}, 'children': [], 'navigation_links': [{'label': 'Human Documentation', 'text': 'README.md', 'path': 'README.md', 'line': 28, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/llm/outputs/test_results/README.md'}, {'label': 'Functional Specification', 'text': 'SPEC.md', 'path': 'SPEC.md', 'line': 29, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/llm/outputs/test_results/SPEC.md'}, {'label': '📁 Parent Directory', 'text': 'outputs', 'path': '../README.md', 'line': 30, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/llm/outputs/README.md'}, {'label': '🏠 Project Root', 'text': 'README', 'path': '../../../../../README.md', 'line': 31, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/README.md'}], 'key_artifacts': [{'label': 'Functional Spec', 'path': 'SPEC.md', 'line': 8, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/llm/outputs/test_results/SPEC.md'}], 'issues': []}, {'file': 'llm/prompt_templates/AGENTS.md', 'parent': {'label': 'Prompt Templates', 'path': '../AGENTS.md', 'line': 4, 'is_generic': False}, 'children': [], 'navigation_links': [{'label': 'Human Documentation', 'text': 'README.md', 'path': 'README.md', 'line': 29, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/llm/prompt_templates/README.md'}, {'label': 'Functional Specification', 'text': 'SPEC.md', 'path': 'SPEC.md', 'line': 30, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/llm/prompt_templates/SPEC.md'}, {'label': '📁 Parent Directory', 'text': 'llm', 'path': '../README.md', 'line': 31, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/llm/README.md'}, {'label': '🏠 Project Root', 'text': 'README', 'path': '../../../../README.md', 'line': 32, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/README.md'}], 'key_artifacts': [{'label': 'Functional Spec', 'path': 'SPEC.md', 'line': 8, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/llm/prompt_templates/SPEC.md'}], 'issues': []}, {'file': 'logging_monitoring/AGENTS.md', 'parent': {'label': 'Repository Root', 'path': '../AGENTS.md', 'line': 4, 'is_generic': False}, 'children': [], 'navigation_links': [{'label': 'Human Documentation', 'text': 'README.md', 'path': 'README.md', 'line': 36, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/logging_monitoring/README.md'}, {'label': 'Functional Specification', 'text': 'SPEC.md', 'path': 'SPEC.md', 'line': 37, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/logging_monitoring/SPEC.md'}, {'label': '📁 Parent Directory', 'text': 'codomyrmex', 'path': '../README.md', 'line': 38, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/README.md'}, {'label': '🏠 Project Root', 'text': 'README', 'path': '../../../README.md', 'line': 39, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/README.md'}], 'key_artifacts': [{'label': 'Functional Spec', 'path': 'SPEC.md', 'line': 8, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/logging_monitoring/SPEC.md'}], 'issues': []}, {'file': 'logistics/AGENTS.md', 'parent': {'label': 'Repository Root', 'path': '../AGENTS.md', 'line': 4, 'is_generic': False}, 'children': [{'label': 'orchestration', 'path': 'orchestration/AGENTS.md', 'line': 6, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/logistics/orchestration/AGENTS.md'}], 'navigation_links': [{'label': 'Human Documentation', 'text': 'README.md', 'path': 'README.md', 'line': 33, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/logistics/README.md'}, {'label': 'Functional Specification', 'text': 'SPEC.md', 'path': 'SPEC.md', 'line': 34, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/logistics/SPEC.md'}, {'label': '📁 Parent Directory', 'text': 'codomyrmex', 'path': '../README.md', 'line': 35, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/README.md'}, {'label': '🏠 Project Root', 'text': 'README', 'path': '../../../README.md', 'line': 36, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/README.md'}], 'key_artifacts': [{'label': 'Functional Spec', 'path': 'SPEC.md', 'line': 10, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/logistics/SPEC.md'}], 'issues': []}, {'file': 'logistics/orchestration/AGENTS.md', 'parent': {'label': 'Orchestration', 'path': '../AGENTS.md', 'line': 4, 'is_generic': False}, 'children': [{'label': 'project', 'path': 'project/AGENTS.md', 'line': 6, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/logistics/orchestration/project/AGENTS.md'}], 'navigation_links': [{'label': 'Human Documentation', 'text': 'README.md', 'path': 'README.md', 'line': 29, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/logistics/orchestration/README.md'}, {'label': 'Functional Specification', 'text': 'SPEC.md', 'path': 'SPEC.md', 'line': 30, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/logistics/orchestration/SPEC.md'}, {'label': '📁 Parent Directory', 'text': 'logistics', 'path': '../README.md', 'line': 31, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/logistics/README.md'}, {'label': '🏠 Project Root', 'text': 'README', 'path': '../../../../README.md', 'line': 32, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/README.md'}], 'key_artifacts': [{'label': 'Functional Spec', 'path': 'SPEC.md', 'line': 8, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/logistics/orchestration/SPEC.md'}], 'issues': []}, {'file': 'logistics/orchestration/project/AGENTS.md', 'parent': {'label': 'Project', 'path': '../AGENTS.md', 'line': 4, 'is_generic': False}, 'children': [{'label': 'templates', 'path': 'templates/AGENTS.md', 'line': 6, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/logistics/orchestration/project/templates/AGENTS.md'}], 'navigation_links': [{'label': 'Human Documentation', 'text': 'README.md', 'path': 'README.md', 'line': 45, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/logistics/orchestration/project/README.md'}, {'label': 'Functional Specification', 'text': 'SPEC.md', 'path': 'SPEC.md', 'line': 46, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/logistics/orchestration/project/SPEC.md'}, {'label': '📁 Parent Directory', 'text': 'orchestration', 'path': '../README.md', 'line': 47, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/logistics/orchestration/README.md'}, {'label': '🏠 Project Root', 'text': 'README', 'path': '../../../../../README.md', 'line': 48, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/README.md'}], 'key_artifacts': [{'label': 'Functional Spec', 'path': 'SPEC.md', 'line': 8, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/logistics/orchestration/project/SPEC.md'}], 'issues': []}, {'file': 'logistics/orchestration/project/templates/AGENTS.md', 'parent': {'label': 'Templates', 'path': '../AGENTS.md', 'line': 4, 'is_generic': False}, 'children': [{'label': 'doc_templates', 'path': 'doc_templates/AGENTS.md', 'line': 6, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/logistics/orchestration/project/templates/doc_templates/AGENTS.md'}], 'navigation_links': [{'label': 'Human Documentation', 'text': 'README.md', 'path': 'README.md', 'line': 30, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/logistics/orchestration/project/templates/README.md'}, {'label': 'Functional Specification', 'text': 'SPEC.md', 'path': 'SPEC.md', 'line': 31, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/logistics/orchestration/project/templates/SPEC.md'}, {'label': '📁 Parent Directory', 'text': 'project', 'path': '../README.md', 'line': 32, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/logistics/orchestration/project/README.md'}, {'label': '🏠 Project Root', 'text': 'README', 'path': '../../../../../../README.md', 'line': 33, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/README.md'}], 'key_artifacts': [{'label': 'Functional Spec', 'path': 'SPEC.md', 'line': 8, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/logistics/orchestration/project/templates/SPEC.md'}], 'issues': []}, {'file': 'logistics/orchestration/project/templates/doc_templates/AGENTS.md', 'parent': {'label': 'Doc Templates', 'path': '../AGENTS.md', 'line': 4, 'is_generic': False}, 'children': [], 'navigation_links': [{'label': 'Human Documentation', 'text': 'README.md', 'path': 'README.md', 'line': 30, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/logistics/orchestration/project/templates/doc_templates/README.md'}, {'label': 'Functional Specification', 'text': 'SPEC.md', 'path': 'SPEC.md', 'line': 31, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/logistics/orchestration/project/templates/doc_templates/SPEC.md'}, {'label': '📁 Parent Directory', 'text': 'templates', 'path': '../README.md', 'line': 32, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/logistics/orchestration/project/templates/README.md'}, {'label': '🏠 Project Root', 'text': 'README', 'path': '../../../../../../../README.md', 'line': 33, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/README.md'}], 'key_artifacts': [{'label': 'Functional Spec', 'path': 'SPEC.md', 'line': 8, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/logistics/orchestration/project/templates/doc_templates/SPEC.md'}], 'issues': []}, {'file': 'logistics/schedule/AGENTS.md', 'parent': {'label': 'Schedule', 'path': '../AGENTS.md', 'line': 4, 'is_generic': False}, 'children': [], 'navigation_links': [{'label': 'Human Documentation', 'text': 'README.md', 'path': 'README.md', 'line': 32, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/logistics/schedule/README.md'}, {'label': 'Functional Specification', 'text': 'SPEC.md', 'path': 'SPEC.md', 'line': 33, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/logistics/schedule/SPEC.md'}, {'label': '📁 Parent Directory', 'text': 'logistics', 'path': '../README.md', 'line': 34, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/logistics/README.md'}, {'label': '🏠 Project Root', 'text': 'README', 'path': '../../../../README.md', 'line': 35, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/README.md'}], 'key_artifacts': [{'label': 'Functional Spec', 'path': 'SPEC.md', 'line': 8, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/logistics/schedule/SPEC.md'}], 'issues': []}, {'file': 'logistics/task/AGENTS.md', 'parent': {'label': 'Task', 'path': '../AGENTS.md', 'line': 4, 'is_generic': False}, 'children': [{'label': 'backends', 'path': 'backends/AGENTS.md', 'line': 6, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/logistics/task/backends/AGENTS.md'}], 'navigation_links': [{'label': 'Human Documentation', 'text': 'README.md', 'path': 'README.md', 'line': 32, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/logistics/task/README.md'}, {'label': 'Functional Specification', 'text': 'SPEC.md', 'path': 'SPEC.md', 'line': 33, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/logistics/task/SPEC.md'}, {'label': '📁 Parent Directory', 'text': 'logistics', 'path': '../README.md', 'line': 34, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/logistics/README.md'}, {'label': '🏠 Project Root', 'text': 'README', 'path': '../../../../README.md', 'line': 35, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/README.md'}], 'key_artifacts': [{'label': 'Functional Spec', 'path': 'SPEC.md', 'line': 8, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/logistics/task/SPEC.md'}], 'issues': []}, {'file': 'logistics/task/backends/AGENTS.md', 'parent': {'label': 'Backends', 'path': '../AGENTS.md', 'line': 4, 'is_generic': False}, 'children': [], 'navigation_links': [{'label': 'Human Documentation', 'text': 'README.md', 'path': 'README.md', 'line': 29, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/logistics/task/backends/README.md'}, {'label': 'Functional Specification', 'text': 'SPEC.md', 'path': 'SPEC.md', 'line': 30, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/logistics/task/backends/SPEC.md'}, {'label': '📁 Parent Directory', 'text': 'task', 'path': '../README.md', 'line': 31, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/logistics/task/README.md'}, {'label': '🏠 Project Root', 'text': 'README', 'path': '../../../../../README.md', 'line': 32, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/README.md'}], 'key_artifacts': [{'label': 'Functional Spec', 'path': 'SPEC.md', 'line': 8, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/logistics/task/backends/SPEC.md'}], 'issues': []}, {'file': 'metrics/AGENTS.md', 'parent': {'label': 'Repository Root', 'path': '../AGENTS.md', 'line': 4, 'is_generic': False}, 'children': [], 'navigation_links': [{'label': 'Human Documentation', 'text': 'README.md', 'path': 'README.md', 'line': 29, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/metrics/README.md'}, {'label': 'Functional Specification', 'text': 'SPEC.md', 'path': 'SPEC.md', 'line': 30, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/metrics/SPEC.md'}, {'label': '📁 Parent Directory', 'text': 'codomyrmex', 'path': '../README.md', 'line': 31, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/README.md'}, {'label': '🏠 Project Root', 'text': 'README', 'path': '../../../README.md', 'line': 32, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/README.md'}], 'key_artifacts': [{'label': 'Functional Spec', 'path': 'SPEC.md', 'line': 8, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/metrics/SPEC.md'}], 'issues': []}, {'file': 'model_context_protocol/AGENTS.md', 'parent': {'label': 'Repository Root', 'path': '../AGENTS.md', 'line': 4, 'is_generic': False}, 'children': [], 'navigation_links': [{'label': 'Human Documentation', 'text': 'README.md', 'path': 'README.md', 'line': 36, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/model_context_protocol/README.md'}, {'label': 'Functional Specification', 'text': 'SPEC.md', 'path': 'SPEC.md', 'line': 37, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/model_context_protocol/SPEC.md'}, {'label': '📁 Parent Directory', 'text': 'codomyrmex', 'path': '../README.md', 'line': 38, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/README.md'}, {'label': '🏠 Project Root', 'text': 'README', 'path': '../../../README.md', 'line': 39, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/README.md'}], 'key_artifacts': [{'label': 'Functional Spec', 'path': 'SPEC.md', 'line': 8, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/model_context_protocol/SPEC.md'}], 'issues': []}, {'file': 'module_template/AGENTS.md', 'parent': {'label': 'Repository Root', 'path': '../AGENTS.md', 'line': 4, 'is_generic': False}, 'children': [], 'navigation_links': [{'label': 'Human Documentation', 'text': 'README.md', 'path': 'README.md', 'line': 34, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/module_template/README.md'}, {'label': 'Functional Specification', 'text': 'SPEC.md', 'path': 'SPEC.md', 'line': 35, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/module_template/SPEC.md'}, {'label': '📁 Parent Directory', 'text': 'codomyrmex', 'path': '../README.md', 'line': 36, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/README.md'}, {'label': '🏠 Project Root', 'text': 'README', 'path': '../../../README.md', 'line': 37, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/README.md'}], 'key_artifacts': [{'label': 'Functional Spec', 'path': 'SPEC.md', 'line': 8, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/module_template/SPEC.md'}], 'issues': []}, {'file': 'networking/AGENTS.md', 'parent': {'label': 'Repository Root', 'path': '../AGENTS.md', 'line': 4, 'is_generic': False}, 'children': [], 'navigation_links': [{'label': 'Human Documentation', 'text': 'README.md', 'path': 'README.md', 'line': 30, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/networking/README.md'}, {'label': 'Functional Specification', 'text': 'SPEC.md', 'path': 'SPEC.md', 'line': 31, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/networking/SPEC.md'}, {'label': '📁 Parent Directory', 'text': 'codomyrmex', 'path': '../README.md', 'line': 32, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/README.md'}, {'label': '🏠 Project Root', 'text': 'README', 'path': '../../../README.md', 'line': 33, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/README.md'}], 'key_artifacts': [{'label': 'Functional Spec', 'path': 'SPEC.md', 'line': 8, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/networking/SPEC.md'}], 'issues': []}, {'file': 'output/AGENTS.md', 'parent': {'label': 'Repository Root', 'path': '../AGENTS.md', 'line': 4, 'is_generic': False}, 'children': [], 'navigation_links': [], 'key_artifacts': [{'label': 'Functional Spec', 'path': 'SPEC.md', 'line': 8, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/output/SPEC.md'}], 'issues': []}, {'file': 'pattern_matching/AGENTS.md', 'parent': {'label': 'Repository Root', 'path': '../AGENTS.md', 'line': 4, 'is_generic': False}, 'children': [], 'navigation_links': [{'label': 'Human Documentation', 'text': 'README.md', 'path': 'README.md', 'line': 34, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/pattern_matching/README.md'}, {'label': 'Functional Specification', 'text': 'SPEC.md', 'path': 'SPEC.md', 'line': 35, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/pattern_matching/SPEC.md'}, {'label': '📁 Parent Directory', 'text': 'codomyrmex', 'path': '../README.md', 'line': 36, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/README.md'}, {'label': '🏠 Project Root', 'text': 'README', 'path': '../../../README.md', 'line': 37, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/README.md'}], 'key_artifacts': [{'label': 'Functional Spec', 'path': 'SPEC.md', 'line': 8, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/pattern_matching/SPEC.md'}], 'issues': []}, {'file': 'performance/AGENTS.md', 'parent': {'label': 'Repository Root', 'path': '../AGENTS.md', 'line': 4, 'is_generic': False}, 'children': [], 'navigation_links': [{'label': 'Human Documentation', 'text': 'README.md', 'path': 'README.md', 'line': 36, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/performance/README.md'}, {'label': 'Functional Specification', 'text': 'SPEC.md', 'path': 'SPEC.md', 'line': 37, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/performance/SPEC.md'}, {'label': '📁 Parent Directory', 'text': 'codomyrmex', 'path': '../README.md', 'line': 38, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/README.md'}, {'label': '🏠 Project Root', 'text': 'README', 'path': '../../../README.md', 'line': 39, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/README.md'}], 'key_artifacts': [{'label': 'Functional Spec', 'path': 'SPEC.md', 'line': 8, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/performance/SPEC.md'}], 'issues': []}, {'file': 'physical_management/AGENTS.md', 'parent': {'label': 'Repository Root', 'path': '../AGENTS.md', 'line': 4, 'is_generic': False}, 'children': [{'label': 'examples', 'path': 'examples/AGENTS.md', 'line': 6, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/physical_management/examples/AGENTS.md'}], 'navigation_links': [{'label': 'Human Documentation', 'text': 'README.md', 'path': 'README.md', 'line': 35, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/physical_management/README.md'}, {'label': 'Functional Specification', 'text': 'SPEC.md', 'path': 'SPEC.md', 'line': 36, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/physical_management/SPEC.md'}, {'label': '📁 Parent Directory', 'text': 'codomyrmex', 'path': '../README.md', 'line': 37, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/README.md'}, {'label': '🏠 Project Root', 'text': 'README', 'path': '../../../README.md', 'line': 38, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/README.md'}], 'key_artifacts': [{'label': 'Functional Spec', 'path': 'SPEC.md', 'line': 8, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/physical_management/SPEC.md'}], 'issues': []}, {'file': 'physical_management/examples/AGENTS.md', 'parent': {'label': 'Examples Root', 'path': '../AGENTS.md', 'line': 4, 'is_generic': False}, 'children': [], 'navigation_links': [{'label': 'Human Documentation', 'text': 'README.md', 'path': 'README.md', 'line': 28, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/physical_management/examples/README.md'}, {'label': 'Functional Specification', 'text': 'SPEC.md', 'path': 'SPEC.md', 'line': 29, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/physical_management/examples/SPEC.md'}, {'label': '📁 Parent Directory', 'text': 'physical_management', 'path': '../README.md', 'line': 30, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/physical_management/README.md'}, {'label': '🏠 Project Root', 'text': 'README', 'path': '../../../../README.md', 'line': 31, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/README.md'}], 'key_artifacts': [{'label': 'Functional Spec', 'path': 'SPEC.md', 'line': 8, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/physical_management/examples/SPEC.md'}], 'issues': []}, {'file': 'plugin_system/AGENTS.md', 'parent': {'label': 'Repository Root', 'path': '../AGENTS.md', 'line': 4, 'is_generic': False}, 'children': [], 'navigation_links': [{'label': 'Human Documentation', 'text': 'README.md', 'path': 'README.md', 'line': 31, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/plugin_system/README.md'}, {'label': 'Functional Specification', 'text': 'SPEC.md', 'path': 'SPEC.md', 'line': 32, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/plugin_system/SPEC.md'}, {'label': '📁 Parent Directory', 'text': 'codomyrmex', 'path': '../README.md', 'line': 33, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/README.md'}, {'label': '🏠 Project Root', 'text': 'README', 'path': '../../../README.md', 'line': 34, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/README.md'}], 'key_artifacts': [{'label': 'Functional Spec', 'path': 'SPEC.md', 'line': 8, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/plugin_system/SPEC.md'}], 'issues': []}, {'file': 'scrape/AGENTS.md', 'parent': {'label': 'Repository Root', 'path': '../AGENTS.md', 'line': 4, 'is_generic': False}, 'children': [{'label': 'firecrawl', 'path': 'firecrawl/AGENTS.md', 'line': 6, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/scrape/firecrawl/AGENTS.md'}], 'navigation_links': [{'label': 'Human Documentation', 'text': 'README.md', 'path': 'README.md', 'line': 37, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/scrape/README.md'}, {'label': 'Functional Specification', 'text': 'SPEC.md', 'path': 'SPEC.md', 'line': 38, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/scrape/SPEC.md'}, {'label': '📁 Parent Directory', 'text': 'codomyrmex', 'path': '../README.md', 'line': 39, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/README.md'}, {'label': '🏠 Project Root', 'text': 'README', 'path': '../../../README.md', 'line': 40, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/README.md'}], 'key_artifacts': [{'label': 'Functional Spec', 'path': 'SPEC.md', 'line': 8, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/scrape/SPEC.md'}], 'issues': []}, {'file': 'scrape/firecrawl/AGENTS.md', 'parent': {'label': 'Firecrawl', 'path': '../AGENTS.md', 'line': 4, 'is_generic': False}, 'children': [], 'navigation_links': [{'label': 'Human Documentation', 'text': 'README.md', 'path': 'README.md', 'line': 30, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/scrape/firecrawl/README.md'}, {'label': 'Functional Specification', 'text': 'SPEC.md', 'path': 'SPEC.md', 'line': 31, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/scrape/firecrawl/SPEC.md'}, {'label': '📁 Parent Directory', 'text': 'scrape', 'path': '../README.md', 'line': 32, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/scrape/README.md'}, {'label': '🏠 Project Root', 'text': 'README', 'path': '../../../../README.md', 'line': 33, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/README.md'}], 'key_artifacts': [{'label': 'Functional Spec', 'path': 'SPEC.md', 'line': 8, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/scrape/firecrawl/SPEC.md'}], 'issues': []}, {'file': 'security/AGENTS.md', 'parent': {'label': 'Repository Root', 'path': '../AGENTS.md', 'line': 4, 'is_generic': False}, 'children': [{'label': 'cognitive', 'path': 'cognitive/AGENTS.md', 'line': 6, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/security/cognitive/AGENTS.md'}], 'navigation_links': [{'label': 'Human Documentation', 'text': 'README.md', 'path': 'README.md', 'line': 37, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/security/README.md'}, {'label': 'Functional Specification', 'text': 'SPEC.md', 'path': 'SPEC.md', 'line': 38, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/security/SPEC.md'}, {'label': '📁 Parent Directory', 'text': 'codomyrmex', 'path': '../README.md', 'line': 39, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/README.md'}, {'label': '🏠 Project Root', 'text': 'README', 'path': '../../../README.md', 'line': 40, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/README.md'}], 'key_artifacts': [{'label': 'Functional Spec', 'path': 'SPEC.md', 'line': 12, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/security/SPEC.md'}], 'issues': []}, {'file': 'security/cognitive/AGENTS.md', 'parent': {'label': 'Cognitive', 'path': '../AGENTS.md', 'line': 4, 'is_generic': False}, 'children': [], 'navigation_links': [{'label': 'Human Documentation', 'text': 'README.md', 'path': 'README.md', 'line': 33, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/security/cognitive/README.md'}, {'label': 'Functional Specification', 'text': 'SPEC.md', 'path': 'SPEC.md', 'line': 34, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/security/cognitive/SPEC.md'}, {'label': '📁 Parent Directory', 'text': 'security', 'path': '../README.md', 'line': 35, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/security/README.md'}, {'label': '🏠 Project Root', 'text': 'README', 'path': '../../../../README.md', 'line': 36, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/README.md'}], 'key_artifacts': [{'label': 'Functional Spec', 'path': 'SPEC.md', 'line': 8, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/security/cognitive/SPEC.md'}], 'issues': []}, {'file': 'security/digital/AGENTS.md', 'parent': {'label': 'Digital', 'path': '../AGENTS.md', 'line': 4, 'is_generic': False}, 'children': [], 'navigation_links': [{'label': 'Human Documentation', 'text': 'README.md', 'path': 'README.md', 'line': 40, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/security/digital/README.md'}, {'label': 'Functional Specification', 'text': 'SPEC.md', 'path': 'SPEC.md', 'line': 41, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/security/digital/SPEC.md'}, {'label': '📁 Parent Directory', 'text': 'security', 'path': '../README.md', 'line': 42, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/security/README.md'}, {'label': '🏠 Project Root', 'text': 'README', 'path': '../../../../README.md', 'line': 43, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/README.md'}], 'key_artifacts': [{'label': 'Functional Spec', 'path': 'SPEC.md', 'line': 8, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/security/digital/SPEC.md'}], 'issues': []}, {'file': 'security/physical/AGENTS.md', 'parent': {'label': 'Physical', 'path': '../AGENTS.md', 'line': 4, 'is_generic': False}, 'children': [], 'navigation_links': [{'label': 'Human Documentation', 'text': 'README.md', 'path': 'README.md', 'line': 33, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/security/physical/README.md'}, {'label': 'Functional Specification', 'text': 'SPEC.md', 'path': 'SPEC.md', 'line': 34, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/security/physical/SPEC.md'}, {'label': '📁 Parent Directory', 'text': 'security', 'path': '../README.md', 'line': 35, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/security/README.md'}, {'label': '🏠 Project Root', 'text': 'README', 'path': '../../../../README.md', 'line': 36, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/README.md'}], 'key_artifacts': [{'label': 'Functional Spec', 'path': 'SPEC.md', 'line': 8, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/security/physical/SPEC.md'}], 'issues': []}, {'file': 'security/security_theory/AGENTS.md', 'parent': {'label': 'Security Theory', 'path': '../AGENTS.md', 'line': 4, 'is_generic': False}, 'children': [], 'navigation_links': [{'label': 'Human Documentation', 'text': 'README.md', 'path': 'README.md', 'line': 33, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/security/security_theory/README.md'}, {'label': 'Functional Specification', 'text': 'SPEC.md', 'path': 'SPEC.md', 'line': 34, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/security/security_theory/SPEC.md'}, {'label': '📁 Parent Directory', 'text': 'security', 'path': '../README.md', 'line': 35, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/security/README.md'}, {'label': '🏠 Project Root', 'text': 'README', 'path': '../../../../README.md', 'line': 36, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/README.md'}], 'key_artifacts': [{'label': 'Functional Spec', 'path': 'SPEC.md', 'line': 8, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/security/security_theory/SPEC.md'}], 'issues': []}, {'file': 'security/theory/AGENTS.md', 'parent': {'label': 'Theory', 'path': '../AGENTS.md', 'line': 4, 'is_generic': False}, 'children': [], 'navigation_links': [{'label': 'Human Documentation', 'text': 'README.md', 'path': 'README.md', 'line': 34, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/security/theory/README.md'}, {'label': 'Functional Specification', 'text': 'SPEC.md', 'path': 'SPEC.md', 'line': 35, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/security/theory/SPEC.md'}, {'label': '📁 Parent Directory', 'text': 'security', 'path': '../README.md', 'line': 36, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/security/README.md'}, {'label': '🏠 Project Root', 'text': 'README', 'path': '../../../../README.md', 'line': 37, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/README.md'}], 'key_artifacts': [{'label': 'Functional Spec', 'path': 'SPEC.md', 'line': 8, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/security/theory/SPEC.md'}], 'issues': []}, {'file': 'serialization/AGENTS.md', 'parent': {'label': 'Repository Root', 'path': '../AGENTS.md', 'line': 4, 'is_generic': False}, 'children': [], 'navigation_links': [{'label': 'Human Documentation', 'text': 'README.md', 'path': 'README.md', 'line': 30, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/serialization/README.md'}, {'label': 'Functional Specification', 'text': 'SPEC.md', 'path': 'SPEC.md', 'line': 31, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/serialization/SPEC.md'}, {'label': '📁 Parent Directory', 'text': 'codomyrmex', 'path': '../README.md', 'line': 32, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/README.md'}, {'label': '🏠 Project Root', 'text': 'README', 'path': '../../../README.md', 'line': 33, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/README.md'}], 'key_artifacts': [{'label': 'Functional Spec', 'path': 'SPEC.md', 'line': 8, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/serialization/SPEC.md'}], 'issues': []}, {'file': 'skills/AGENTS.md', 'parent': {'label': 'Repository Root', 'path': '../AGENTS.md', 'line': 4, 'is_generic': False}, 'children': [], 'navigation_links': [{'label': 'Human Documentation', 'text': 'README.md', 'path': 'README.md', 'line': 34, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/skills/README.md'}, {'label': 'Functional Specification', 'text': 'SPEC.md', 'path': 'SPEC.md', 'line': 35, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/skills/SPEC.md'}, {'label': '📁 Parent Directory', 'text': 'codomyrmex', 'path': '../README.md', 'line': 36, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/README.md'}, {'label': '🏠 Project Root', 'text': 'README', 'path': '../../../README.md', 'line': 37, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/README.md'}], 'key_artifacts': [{'label': 'Functional Spec', 'path': 'SPEC.md', 'line': 8, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/skills/SPEC.md'}], 'issues': []}, {'file': 'spatial/AGENTS.md', 'parent': {'label': 'Repository Root', 'path': '../AGENTS.md', 'line': 4, 'is_generic': False}, 'children': [{'label': 'four_d', 'path': 'four_d/AGENTS.md', 'line': 6, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/spatial/four_d/AGENTS.md'}], 'navigation_links': [{'label': 'Human Documentation', 'text': 'README.md', 'path': 'README.md', 'line': 32, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/spatial/README.md'}, {'label': 'Functional Specification', 'text': 'SPEC.md', 'path': 'SPEC.md', 'line': 33, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/spatial/SPEC.md'}, {'label': '📁 Parent Directory', 'text': 'codomyrmex', 'path': '../README.md', 'line': 34, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/README.md'}, {'label': '🏠 Project Root', 'text': 'README', 'path': '../../../README.md', 'line': 35, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/README.md'}], 'key_artifacts': [{'label': 'Functional Spec', 'path': 'SPEC.md', 'line': 10, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/spatial/SPEC.md'}], 'issues': []}, {'file': 'spatial/four_d/AGENTS.md', 'parent': {'label': 'Four D', 'path': '../AGENTS.md', 'line': 4, 'is_generic': False}, 'children': [], 'navigation_links': [{'label': 'Human Documentation', 'text': 'README.md', 'path': 'README.md', 'line': 27, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/spatial/four_d/README.md'}, {'label': 'Functional Specification', 'text': 'SPEC.md', 'path': 'SPEC.md', 'line': 28, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/spatial/four_d/SPEC.md'}, {'label': '📁 Parent Directory', 'text': 'spatial', 'path': '../README.md', 'line': 29, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/spatial/README.md'}, {'label': '🏠 Project Root', 'text': 'README', 'path': '../../../../README.md', 'line': 30, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/README.md'}], 'key_artifacts': [{'label': 'Functional Spec', 'path': 'SPEC.md', 'line': 8, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/spatial/four_d/SPEC.md'}], 'issues': []}, {'file': 'spatial/three_d/AGENTS.md', 'parent': {'label': 'Three D', 'path': '../AGENTS.md', 'line': 4, 'is_generic': False}, 'children': [{'label': 'examples', 'path': 'examples/AGENTS.md', 'line': 6, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/spatial/three_d/examples/AGENTS.md'}], 'navigation_links': [{'label': 'Human Documentation', 'text': 'README.md', 'path': 'README.md', 'line': 34, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/spatial/three_d/README.md'}, {'label': 'Functional Specification', 'text': 'SPEC.md', 'path': 'SPEC.md', 'line': 35, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/spatial/three_d/SPEC.md'}, {'label': '📁 Parent Directory', 'text': 'spatial', 'path': '../README.md', 'line': 36, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/spatial/README.md'}, {'label': '🏠 Project Root', 'text': 'README', 'path': '../../../../README.md', 'line': 37, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/README.md'}], 'key_artifacts': [{'label': 'Functional Spec', 'path': 'SPEC.md', 'line': 8, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/spatial/three_d/SPEC.md'}], 'issues': []}, {'file': 'spatial/three_d/examples/AGENTS.md', 'parent': {'label': 'Examples Root', 'path': '../AGENTS.md', 'line': 4, 'is_generic': False}, 'children': [], 'navigation_links': [{'label': 'Human Documentation', 'text': 'README.md', 'path': 'README.md', 'line': 27, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/spatial/three_d/examples/README.md'}, {'label': 'Functional Specification', 'text': 'SPEC.md', 'path': 'SPEC.md', 'line': 28, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/spatial/three_d/examples/SPEC.md'}, {'label': '📁 Parent Directory', 'text': 'three_d', 'path': '../README.md', 'line': 29, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/spatial/three_d/README.md'}, {'label': '🏠 Project Root', 'text': 'README', 'path': '../../../../../README.md', 'line': 30, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/README.md'}], 'key_artifacts': [{'label': 'Functional Spec', 'path': 'SPEC.md', 'line': 8, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/spatial/three_d/examples/SPEC.md'}], 'issues': []}, {'file': 'spatial/world_models/AGENTS.md', 'parent': {'label': 'World Models', 'path': '../AGENTS.md', 'line': 4, 'is_generic': False}, 'children': [], 'navigation_links': [{'label': 'Human Documentation', 'text': 'README.md', 'path': 'README.md', 'line': 27, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/spatial/world_models/README.md'}, {'label': 'Functional Specification', 'text': 'SPEC.md', 'path': 'SPEC.md', 'line': 28, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/spatial/world_models/SPEC.md'}, {'label': '📁 Parent Directory', 'text': 'spatial', 'path': '../README.md', 'line': 29, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/spatial/README.md'}, {'label': '🏠 Project Root', 'text': 'README', 'path': '../../../../README.md', 'line': 30, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/README.md'}], 'key_artifacts': [{'label': 'Functional Spec', 'path': 'SPEC.md', 'line': 8, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/spatial/world_models/SPEC.md'}], 'issues': []}, {'file': 'static_analysis/AGENTS.md', 'parent': {'label': 'Repository Root', 'path': '../AGENTS.md', 'line': 4, 'is_generic': False}, 'children': [], 'navigation_links': [{'label': 'Human Documentation', 'text': 'README.md', 'path': 'README.md', 'line': 35, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/static_analysis/README.md'}, {'label': 'Functional Specification', 'text': 'SPEC.md', 'path': 'SPEC.md', 'line': 36, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/static_analysis/SPEC.md'}, {'label': '📁 Parent Directory', 'text': 'codomyrmex', 'path': '../README.md', 'line': 37, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/README.md'}, {'label': '🏠 Project Root', 'text': 'README', 'path': '../../../README.md', 'line': 38, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/README.md'}], 'key_artifacts': [{'label': 'Functional Spec', 'path': 'SPEC.md', 'line': 8, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/static_analysis/SPEC.md'}], 'issues': []}, {'file': 'system_discovery/AGENTS.md', 'parent': {'label': 'Repository Root', 'path': '../AGENTS.md', 'line': 4, 'is_generic': False}, 'children': [], 'navigation_links': [{'label': 'Human Documentation', 'text': 'README.md', 'path': 'README.md', 'line': 36, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/system_discovery/README.md'}, {'label': 'Functional Specification', 'text': 'SPEC.md', 'path': 'SPEC.md', 'line': 37, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/system_discovery/SPEC.md'}, {'label': '📁 Parent Directory', 'text': 'codomyrmex', 'path': '../README.md', 'line': 38, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/README.md'}, {'label': '🏠 Project Root', 'text': 'README', 'path': '../../../README.md', 'line': 39, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/README.md'}], 'key_artifacts': [{'label': 'Functional Spec', 'path': 'SPEC.md', 'line': 8, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/system_discovery/SPEC.md'}], 'issues': []}, {'file': 'templating/AGENTS.md', 'parent': {'label': 'Repository Root', 'path': '../AGENTS.md', 'line': 4, 'is_generic': False}, 'children': [], 'navigation_links': [{'label': 'Human Documentation', 'text': 'README.md', 'path': 'README.md', 'line': 29, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/templating/README.md'}, {'label': 'Functional Specification', 'text': 'SPEC.md', 'path': 'SPEC.md', 'line': 30, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/templating/SPEC.md'}, {'label': '📁 Parent Directory', 'text': 'codomyrmex', 'path': '../README.md', 'line': 31, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/README.md'}, {'label': '🏠 Project Root', 'text': 'README', 'path': '../../../README.md', 'line': 32, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/README.md'}], 'key_artifacts': [{'label': 'Functional Spec', 'path': 'SPEC.md', 'line': 8, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/templating/SPEC.md'}], 'issues': []}, {'file': 'terminal_interface/AGENTS.md', 'parent': {'label': 'Repository Root', 'path': '../AGENTS.md', 'line': 4, 'is_generic': False}, 'children': [], 'navigation_links': [{'label': 'Human Documentation', 'text': 'README.md', 'path': 'README.md', 'line': 33, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/terminal_interface/README.md'}, {'label': 'Functional Specification', 'text': 'SPEC.md', 'path': 'SPEC.md', 'line': 34, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/terminal_interface/SPEC.md'}, {'label': '📁 Parent Directory', 'text': 'codomyrmex', 'path': '../README.md', 'line': 35, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/README.md'}, {'label': '🏠 Project Root', 'text': 'README', 'path': '../../../README.md', 'line': 36, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/README.md'}], 'key_artifacts': [{'label': 'Functional Spec', 'path': 'SPEC.md', 'line': 8, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/terminal_interface/SPEC.md'}], 'issues': []}, {'file': 'tests/AGENTS.md', 'parent': {'label': 'Repository Root', 'path': '../AGENTS.md', 'line': 4, 'is_generic': False}, 'children': [{'label': 'examples', 'path': 'examples/AGENTS.md', 'line': 6, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/examples/AGENTS.md'}], 'navigation_links': [{'label': 'Human Documentation', 'text': 'README.md', 'path': 'README.md', 'line': 41, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/README.md'}, {'label': 'Functional Specification', 'text': 'SPEC.md', 'path': 'SPEC.md', 'line': 42, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/SPEC.md'}, {'label': '📁 Parent Directory', 'text': 'codomyrmex', 'path': '../README.md', 'line': 43, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/README.md'}, {'label': '🏠 Project Root', 'text': 'README', 'path': '../../../README.md', 'line': 44, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/README.md'}], 'key_artifacts': [{'label': 'Functional Spec', 'path': 'SPEC.md', 'line': 13, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/SPEC.md'}], 'issues': []}, {'file': 'tests/examples/AGENTS.md', 'parent': {'label': 'Examples Root', 'path': '../AGENTS.md', 'line': 4, 'is_generic': False}, 'children': [], 'navigation_links': [{'label': 'Human Documentation', 'text': 'README.md', 'path': 'README.md', 'line': 31, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/examples/README.md'}, {'label': 'Functional Specification', 'text': 'SPEC.md', 'path': 'SPEC.md', 'line': 32, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/examples/SPEC.md'}, {'label': '📁 Parent Directory', 'text': 'tests', 'path': '../README.md', 'line': 33, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/README.md'}, {'label': '🏠 Project Root', 'text': 'README', 'path': '../../../../README.md', 'line': 34, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/README.md'}], 'key_artifacts': [{'label': 'Functional Spec', 'path': 'SPEC.md', 'line': 8, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/examples/SPEC.md'}], 'issues': []}, {'file': 'tests/fixtures/AGENTS.md', 'parent': {'label': 'Fixtures', 'path': '../AGENTS.md', 'line': 4, 'is_generic': False}, 'children': [], 'navigation_links': [{'label': 'Human Documentation', 'text': 'README.md', 'path': 'README.md', 'line': 27, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/fixtures/README.md'}, {'label': 'Functional Specification', 'text': 'SPEC.md', 'path': 'SPEC.md', 'line': 28, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/fixtures/SPEC.md'}, {'label': '📁 Parent Directory', 'text': 'tests', 'path': '../README.md', 'line': 29, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/README.md'}, {'label': '🏠 Project Root', 'text': 'README', 'path': '../../../../README.md', 'line': 30, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/README.md'}], 'key_artifacts': [{'label': 'Functional Spec', 'path': 'SPEC.md', 'line': 8, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/fixtures/SPEC.md'}], 'issues': []}, {'file': 'tests/integration/AGENTS.md', 'parent': {'label': 'Integration', 'path': '../AGENTS.md', 'line': 4, 'is_generic': False}, 'children': [{'label': 'ai_code_editing', 'path': 'ai_code_editing/AGENTS.md', 'line': 6, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/integration/ai_code_editing/AGENTS.md'}], 'navigation_links': [{'label': 'Human Documentation', 'text': 'README.md', 'path': 'README.md', 'line': 40, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/integration/README.md'}, {'label': 'Functional Specification', 'text': 'SPEC.md', 'path': 'SPEC.md', 'line': 41, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/integration/SPEC.md'}, {'label': '📁 Parent Directory', 'text': 'tests', 'path': '../README.md', 'line': 42, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/README.md'}, {'label': '🏠 Project Root', 'text': 'README', 'path': '../../../../README.md', 'line': 43, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/README.md'}], 'key_artifacts': [{'label': 'Functional Spec', 'path': 'SPEC.md', 'line': 13, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/integration/SPEC.md'}], 'issues': []}, {'file': 'tests/integration/ai_code_editing/AGENTS.md', 'parent': {'label': 'Ai Code Editing', 'path': '../AGENTS.md', 'line': 4, 'is_generic': False}, 'children': [], 'navigation_links': [{'label': 'Human Documentation', 'text': 'README.md', 'path': 'README.md', 'line': 27, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/integration/ai_code_editing/README.md'}, {'label': 'Functional Specification', 'text': 'SPEC.md', 'path': 'SPEC.md', 'line': 28, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/integration/ai_code_editing/SPEC.md'}, {'label': '📁 Parent Directory', 'text': 'integration', 'path': '../README.md', 'line': 29, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/integration/README.md'}, {'label': '🏠 Project Root', 'text': 'README', 'path': '../../../../../README.md', 'line': 30, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/README.md'}], 'key_artifacts': [{'label': 'Functional Spec', 'path': 'SPEC.md', 'line': 8, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/integration/ai_code_editing/SPEC.md'}], 'issues': []}, {'file': 'tests/integration/data_visualization/AGENTS.md', 'parent': {'label': 'Data Visualization', 'path': '../AGENTS.md', 'line': 4, 'is_generic': False}, 'children': [], 'navigation_links': [{'label': 'Human Documentation', 'text': 'README.md', 'path': 'README.md', 'line': 27, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/integration/data_visualization/README.md'}, {'label': 'Functional Specification', 'text': 'SPEC.md', 'path': 'SPEC.md', 'line': 28, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/integration/data_visualization/SPEC.md'}, {'label': '📁 Parent Directory', 'text': 'integration', 'path': '../README.md', 'line': 29, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/integration/README.md'}, {'label': '🏠 Project Root', 'text': 'README', 'path': '../../../../../README.md', 'line': 30, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/README.md'}], 'key_artifacts': [{'label': 'Functional Spec', 'path': 'SPEC.md', 'line': 8, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/integration/data_visualization/SPEC.md'}], 'issues': []}, {'file': 'tests/integration/documentation/AGENTS.md', 'parent': {'label': 'Documentation', 'path': '../AGENTS.md', 'line': 4, 'is_generic': False}, 'children': [], 'navigation_links': [{'label': 'Human Documentation', 'text': 'README.md', 'path': 'README.md', 'line': 27, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/integration/documentation/README.md'}, {'label': 'Functional Specification', 'text': 'SPEC.md', 'path': 'SPEC.md', 'line': 28, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/integration/documentation/SPEC.md'}, {'label': '📁 Parent Directory', 'text': 'integration', 'path': '../README.md', 'line': 29, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/integration/README.md'}, {'label': '🏠 Project Root', 'text': 'README', 'path': '../../../../../README.md', 'line': 30, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/README.md'}], 'key_artifacts': [{'label': 'Functional Spec', 'path': 'SPEC.md', 'line': 8, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/integration/documentation/SPEC.md'}], 'issues': []}, {'file': 'tests/integration/documents/AGENTS.md', 'parent': {'label': 'Documents', 'path': '../AGENTS.md', 'line': 4, 'is_generic': False}, 'children': [], 'navigation_links': [{'label': 'Human Documentation', 'text': 'README.md', 'path': 'README.md', 'line': 27, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/integration/documents/README.md'}, {'label': 'Functional Specification', 'text': 'SPEC.md', 'path': 'SPEC.md', 'line': 28, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/integration/documents/SPEC.md'}, {'label': '📁 Parent Directory', 'text': 'integration', 'path': '../README.md', 'line': 29, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/integration/README.md'}, {'label': '🏠 Project Root', 'text': 'README', 'path': '../../../../../README.md', 'line': 30, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/README.md'}], 'key_artifacts': [{'label': 'Functional Spec', 'path': 'SPEC.md', 'line': 8, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/integration/documents/SPEC.md'}], 'issues': []}, {'file': 'tests/integration/git_operations/AGENTS.md', 'parent': {'label': 'Git Operations', 'path': '../AGENTS.md', 'line': 4, 'is_generic': False}, 'children': [], 'navigation_links': [{'label': 'Human Documentation', 'text': 'README.md', 'path': 'README.md', 'line': 30, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/integration/git_operations/README.md'}, {'label': 'Functional Specification', 'text': 'SPEC.md', 'path': 'SPEC.md', 'line': 31, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/integration/git_operations/SPEC.md'}, {'label': '📁 Parent Directory', 'text': 'integration', 'path': '../README.md', 'line': 32, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/integration/README.md'}, {'label': '🏠 Project Root', 'text': 'README', 'path': '../../../../../README.md', 'line': 33, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/README.md'}], 'key_artifacts': [{'label': 'Functional Spec', 'path': 'SPEC.md', 'line': 8, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/integration/git_operations/SPEC.md'}], 'issues': []}, {'file': 'tests/integration/security/AGENTS.md', 'parent': {'label': 'Security', 'path': '../AGENTS.md', 'line': 4, 'is_generic': False}, 'children': [], 'navigation_links': [{'label': 'Human Documentation', 'text': 'README.md', 'path': 'README.md', 'line': 28, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/integration/security/README.md'}, {'label': 'Functional Specification', 'text': 'SPEC.md', 'path': 'SPEC.md', 'line': 29, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/integration/security/SPEC.md'}, {'label': '📁 Parent Directory', 'text': 'integration', 'path': '../README.md', 'line': 30, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/integration/README.md'}, {'label': '🏠 Project Root', 'text': 'README', 'path': '../../../../../README.md', 'line': 31, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/README.md'}], 'key_artifacts': [{'label': 'Functional Spec', 'path': 'SPEC.md', 'line': 8, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/integration/security/SPEC.md'}], 'issues': []}, {'file': 'tests/output/AGENTS.md', 'parent': {'label': 'Tests', 'path': '../AGENTS.md', 'line': 5, 'is_generic': False}, 'children': [], 'navigation_links': [], 'key_artifacts': [{'label': 'Functional Spec', 'path': 'SPEC.md', 'line': 9, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/output/SPEC.md'}], 'issues': []}, {'file': 'tests/performance/AGENTS.md', 'parent': {'label': 'Performance', 'path': '../AGENTS.md', 'line': 4, 'is_generic': False}, 'children': [], 'navigation_links': [{'label': 'Human Documentation', 'text': 'README.md', 'path': 'README.md', 'line': 29, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/performance/README.md'}, {'label': 'Functional Specification', 'text': 'SPEC.md', 'path': 'SPEC.md', 'line': 30, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/performance/SPEC.md'}, {'label': '📁 Parent Directory', 'text': 'tests', 'path': '../README.md', 'line': 31, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/README.md'}, {'label': '🏠 Project Root', 'text': 'README', 'path': '../../../../README.md', 'line': 32, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/README.md'}], 'key_artifacts': [{'label': 'Functional Spec', 'path': 'SPEC.md', 'line': 8, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/performance/SPEC.md'}], 'issues': []}, {'file': 'tests/unit/AGENTS.md', 'parent': {'label': 'Unit', 'path': '../AGENTS.md', 'line': 4, 'is_generic': False}, 'children': [{'label': 'agents', 'path': 'agents/AGENTS.md', 'line': 6, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/agents/AGENTS.md'}], 'navigation_links': [{'label': 'Human Documentation', 'text': 'README.md', 'path': 'README.md', 'line': 124, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/README.md'}, {'label': 'Functional Specification', 'text': 'SPEC.md', 'path': 'SPEC.md', 'line': 125, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/SPEC.md'}, {'label': '📁 Parent Directory', 'text': 'tests', 'path': '../README.md', 'line': 126, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/README.md'}, {'label': '🏠 Project Root', 'text': 'README', 'path': '../../../../README.md', 'line': 127, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/README.md'}], 'key_artifacts': [{'label': 'Functional Spec', 'path': 'SPEC.md', 'line': 54, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/SPEC.md'}], 'issues': []}, {'file': 'tests/unit/agents/AGENTS.md', 'parent': {'label': 'Agents', 'path': '../AGENTS.md', 'line': 4, 'is_generic': False}, 'children': [{'label': 'ai_code_editing', 'path': 'ai_code_editing/AGENTS.md', 'line': 6, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/agents/ai_code_editing/AGENTS.md'}], 'navigation_links': [{'label': 'Human Documentation', 'text': 'README.md', 'path': 'README.md', 'line': 50, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/agents/README.md'}, {'label': 'Functional Specification', 'text': 'SPEC.md', 'path': 'SPEC.md', 'line': 51, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/agents/SPEC.md'}, {'label': '📁 Parent Directory', 'text': 'unit', 'path': '../README.md', 'line': 52, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/README.md'}, {'label': '🏠 Project Root', 'text': 'README', 'path': '../../../../../README.md', 'line': 53, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/README.md'}], 'key_artifacts': [{'label': 'Functional Spec', 'path': 'SPEC.md', 'line': 12, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/agents/SPEC.md'}], 'issues': []}, {'file': 'tests/unit/agents/ai_code_editing/AGENTS.md', 'parent': {'label': 'Ai Code Editing', 'path': '../AGENTS.md', 'line': 4, 'is_generic': False}, 'children': [{'label': 'integration', 'path': 'integration/AGENTS.md', 'line': 6, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/agents/ai_code_editing/integration/AGENTS.md'}], 'navigation_links': [{'label': 'Human Documentation', 'text': 'README.md', 'path': 'README.md', 'line': 29, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/agents/ai_code_editing/README.md'}, {'label': 'Functional Specification', 'text': 'SPEC.md', 'path': 'SPEC.md', 'line': 30, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/agents/ai_code_editing/SPEC.md'}, {'label': '📁 Parent Directory', 'text': 'agents', 'path': '../README.md', 'line': 31, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/agents/README.md'}, {'label': '🏠 Project Root', 'text': 'README', 'path': '../../../../../../README.md', 'line': 32, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/README.md'}], 'key_artifacts': [{'label': 'Functional Spec', 'path': 'SPEC.md', 'line': 9, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/agents/ai_code_editing/SPEC.md'}], 'issues': []}, {'file': 'tests/unit/agents/ai_code_editing/integration/AGENTS.md', 'parent': {'label': 'Integration', 'path': '../AGENTS.md', 'line': 4, 'is_generic': False}, 'children': [], 'navigation_links': [{'label': 'Human Documentation', 'text': 'README.md', 'path': 'README.md', 'line': 27, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/agents/ai_code_editing/integration/README.md'}, {'label': 'Functional Specification', 'text': 'SPEC.md', 'path': 'SPEC.md', 'line': 28, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/agents/ai_code_editing/integration/SPEC.md'}, {'label': '📁 Parent Directory', 'text': 'ai_code_editing', 'path': '../README.md', 'line': 29, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/agents/ai_code_editing/README.md'}, {'label': '🏠 Project Root', 'text': 'README', 'path': '../../../../../../../README.md', 'line': 30, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/README.md'}], 'key_artifacts': [{'label': 'Functional Spec', 'path': 'SPEC.md', 'line': 8, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/agents/ai_code_editing/integration/SPEC.md'}], 'issues': []}, {'file': 'tests/unit/agents/ai_code_editing/unit/AGENTS.md', 'parent': {'label': 'Unit', 'path': '../AGENTS.md', 'line': 4, 'is_generic': False}, 'children': [{'label': 'droid', 'path': 'droid/AGENTS.md', 'line': 6, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/agents/ai_code_editing/unit/droid/AGENTS.md'}], 'navigation_links': [{'label': 'Human Documentation', 'text': 'README.md', 'path': 'README.md', 'line': 28, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/agents/ai_code_editing/unit/README.md'}, {'label': 'Functional Specification', 'text': 'SPEC.md', 'path': 'SPEC.md', 'line': 29, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/agents/ai_code_editing/unit/SPEC.md'}, {'label': '📁 Parent Directory', 'text': 'ai_code_editing', 'path': '../README.md', 'line': 30, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/agents/ai_code_editing/README.md'}, {'label': '🏠 Project Root', 'text': 'README', 'path': '../../../../../../../README.md', 'line': 31, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/README.md'}], 'key_artifacts': [{'label': 'Functional Spec', 'path': 'SPEC.md', 'line': 8, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/agents/ai_code_editing/unit/SPEC.md'}], 'issues': []}, {'file': 'tests/unit/agents/ai_code_editing/unit/droid/AGENTS.md', 'parent': {'label': 'Droid', 'path': '../AGENTS.md', 'line': 4, 'is_generic': False}, 'children': [], 'navigation_links': [{'label': 'Human Documentation', 'text': 'README.md', 'path': 'README.md', 'line': 26, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/agents/ai_code_editing/unit/droid/README.md'}, {'label': 'Functional Specification', 'text': 'SPEC.md', 'path': 'SPEC.md', 'line': 27, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/agents/ai_code_editing/unit/droid/SPEC.md'}, {'label': '📁 Parent Directory', 'text': 'unit', 'path': '../README.md', 'line': 28, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/agents/ai_code_editing/unit/README.md'}, {'label': '🏠 Project Root', 'text': 'README', 'path': '../../../../../../../../README.md', 'line': 29, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/README.md'}], 'key_artifacts': [{'label': 'Functional Spec', 'path': 'SPEC.md', 'line': 8, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/agents/ai_code_editing/unit/droid/SPEC.md'}], 'issues': []}, {'file': 'tests/unit/agents/every_code/AGENTS.md', 'parent': {'label': 'Every Code', 'path': '../AGENTS.md', 'line': 4, 'is_generic': False}, 'children': [], 'navigation_links': [{'label': 'Human Documentation', 'text': 'README.md', 'path': 'README.md', 'line': 30, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/agents/every_code/README.md'}, {'label': 'Functional Specification', 'text': 'SPEC.md', 'path': 'SPEC.md', 'line': 31, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/agents/every_code/SPEC.md'}, {'label': '📁 Parent Directory', 'text': 'agents', 'path': '../README.md', 'line': 32, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/agents/README.md'}, {'label': '🏠 Project Root', 'text': 'README', 'path': '../../../../../../README.md', 'line': 33, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/README.md'}], 'key_artifacts': [{'label': 'Functional Spec', 'path': 'SPEC.md', 'line': 8, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/agents/every_code/SPEC.md'}], 'issues': []}, {'file': 'tests/unit/agents/gemini/AGENTS.md', 'parent': {'label': 'Gemini', 'path': '../AGENTS.md', 'line': 4, 'is_generic': False}, 'children': [], 'navigation_links': [{'label': 'Human Documentation', 'text': 'README.md', 'path': 'README.md', 'line': 31, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/agents/gemini/README.md'}, {'label': 'Functional Specification', 'text': 'SPEC.md', 'path': 'SPEC.md', 'line': 32, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/agents/gemini/SPEC.md'}, {'label': '📁 Parent Directory', 'text': 'agents', 'path': '../README.md', 'line': 33, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/agents/README.md'}, {'label': '🏠 Project Root', 'text': 'README', 'path': '../../../../../../README.md', 'line': 34, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/README.md'}], 'key_artifacts': [{'label': 'Functional Spec', 'path': 'SPEC.md', 'line': 8, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/agents/gemini/SPEC.md'}], 'issues': []}, {'file': 'tests/unit/agents/generic/AGENTS.md', 'parent': {'label': 'Generic', 'path': '../AGENTS.md', 'line': 4, 'is_generic': False}, 'children': [], 'navigation_links': [{'label': 'Human Documentation', 'text': 'README.md', 'path': 'README.md', 'line': 28, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/agents/generic/README.md'}, {'label': 'Functional Specification', 'text': 'SPEC.md', 'path': 'SPEC.md', 'line': 29, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/agents/generic/SPEC.md'}, {'label': '📁 Parent Directory', 'text': 'agents', 'path': '../README.md', 'line': 30, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/agents/README.md'}, {'label': '🏠 Project Root', 'text': 'README', 'path': '../../../../../../README.md', 'line': 31, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/README.md'}], 'key_artifacts': [{'label': 'Functional Spec', 'path': 'SPEC.md', 'line': 8, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/agents/generic/SPEC.md'}], 'issues': []}, {'file': 'tests/unit/agents/mistral_vibe/AGENTS.md', 'parent': {'label': 'Mistral Vibe', 'path': '../AGENTS.md', 'line': 4, 'is_generic': False}, 'children': [], 'navigation_links': [{'label': 'Human Documentation', 'text': 'README.md', 'path': 'README.md', 'line': 30, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/agents/mistral_vibe/README.md'}, {'label': 'Functional Specification', 'text': 'SPEC.md', 'path': 'SPEC.md', 'line': 31, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/agents/mistral_vibe/SPEC.md'}, {'label': '📁 Parent Directory', 'text': 'agents', 'path': '../README.md', 'line': 32, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/agents/README.md'}, {'label': '🏠 Project Root', 'text': 'README', 'path': '../../../../../../README.md', 'line': 33, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/README.md'}], 'key_artifacts': [{'label': 'Functional Spec', 'path': 'SPEC.md', 'line': 8, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/agents/mistral_vibe/SPEC.md'}], 'issues': []}, {'file': 'tests/unit/ai_code_editing/AGENTS.md', 'parent': {'label': 'Ai Code Editing', 'path': '../AGENTS.md', 'line': 4, 'is_generic': False}, 'children': [], 'navigation_links': [{'label': 'Human Documentation', 'text': 'README.md', 'path': 'README.md', 'line': 28, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/ai_code_editing/README.md'}, {'label': 'Functional Specification', 'text': 'SPEC.md', 'path': 'SPEC.md', 'line': 29, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/ai_code_editing/SPEC.md'}, {'label': '📁 Parent Directory', 'text': 'unit', 'path': '../README.md', 'line': 30, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/README.md'}, {'label': '🏠 Project Root', 'text': 'README', 'path': '../../../../../README.md', 'line': 31, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/README.md'}], 'key_artifacts': [{'label': 'Functional Spec', 'path': 'SPEC.md', 'line': 8, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/ai_code_editing/SPEC.md'}], 'issues': []}, {'file': 'tests/unit/api_documentation/AGENTS.md', 'parent': {'label': 'Api Documentation', 'path': '../AGENTS.md', 'line': 4, 'is_generic': False}, 'children': [], 'navigation_links': [{'label': 'Human Documentation', 'text': 'README.md', 'path': 'README.md', 'line': 28, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/api_documentation/README.md'}, {'label': 'Functional Specification', 'text': 'SPEC.md', 'path': 'SPEC.md', 'line': 29, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/api_documentation/SPEC.md'}, {'label': '📁 Parent Directory', 'text': 'unit', 'path': '../README.md', 'line': 30, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/README.md'}, {'label': '🏠 Project Root', 'text': 'README', 'path': '../../../../../README.md', 'line': 31, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/README.md'}], 'key_artifacts': [{'label': 'Functional Spec', 'path': 'SPEC.md', 'line': 8, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/api_documentation/SPEC.md'}], 'issues': []}, {'file': 'tests/unit/api_standardization/AGENTS.md', 'parent': {'label': 'Api Standardization', 'path': '../AGENTS.md', 'line': 4, 'is_generic': False}, 'children': [], 'navigation_links': [{'label': 'Human Documentation', 'text': 'README.md', 'path': 'README.md', 'line': 28, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/api_standardization/README.md'}, {'label': 'Functional Specification', 'text': 'SPEC.md', 'path': 'SPEC.md', 'line': 29, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/api_standardization/SPEC.md'}, {'label': '📁 Parent Directory', 'text': 'unit', 'path': '../README.md', 'line': 30, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/README.md'}, {'label': '🏠 Project Root', 'text': 'README', 'path': '../../../../../README.md', 'line': 31, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/README.md'}], 'key_artifacts': [{'label': 'Functional Spec', 'path': 'SPEC.md', 'line': 8, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/api_standardization/SPEC.md'}], 'issues': []}, {'file': 'tests/unit/auth/AGENTS.md', 'parent': {'label': 'Auth', 'path': '../AGENTS.md', 'line': 4, 'is_generic': False}, 'children': [], 'navigation_links': [{'label': 'Human Documentation', 'text': 'README.md', 'path': 'README.md', 'line': 28, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/auth/README.md'}, {'label': 'Functional Specification', 'text': 'SPEC.md', 'path': 'SPEC.md', 'line': 29, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/auth/SPEC.md'}, {'label': '📁 Parent Directory', 'text': 'unit', 'path': '../README.md', 'line': 30, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/README.md'}, {'label': '🏠 Project Root', 'text': 'README', 'path': '../../../../../README.md', 'line': 31, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/README.md'}], 'key_artifacts': [{'label': 'Functional Spec', 'path': 'SPEC.md', 'line': 8, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/auth/SPEC.md'}], 'issues': []}, {'file': 'tests/unit/build_synthesis/AGENTS.md', 'parent': {'label': 'Build Synthesis', 'path': '../AGENTS.md', 'line': 4, 'is_generic': False}, 'children': [{'label': 'integration', 'path': 'integration/AGENTS.md', 'line': 6, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/build_synthesis/integration/AGENTS.md'}], 'navigation_links': [{'label': 'Human Documentation', 'text': 'README.md', 'path': 'README.md', 'line': 31, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/build_synthesis/README.md'}, {'label': 'Functional Specification', 'text': 'SPEC.md', 'path': 'SPEC.md', 'line': 32, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/build_synthesis/SPEC.md'}, {'label': '📁 Parent Directory', 'text': 'unit', 'path': '../README.md', 'line': 33, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/README.md'}, {'label': '🏠 Project Root', 'text': 'README', 'path': '../../../../../README.md', 'line': 34, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/README.md'}], 'key_artifacts': [{'label': 'Functional Spec', 'path': 'SPEC.md', 'line': 9, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/build_synthesis/SPEC.md'}], 'issues': []}, {'file': 'tests/unit/build_synthesis/integration/AGENTS.md', 'parent': {'label': 'Integration', 'path': '../AGENTS.md', 'line': 4, 'is_generic': False}, 'children': [], 'navigation_links': [{'label': 'Human Documentation', 'text': 'README.md', 'path': 'README.md', 'line': 27, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/build_synthesis/integration/README.md'}, {'label': 'Functional Specification', 'text': 'SPEC.md', 'path': 'SPEC.md', 'line': 28, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/build_synthesis/integration/SPEC.md'}, {'label': '📁 Parent Directory', 'text': 'build_synthesis', 'path': '../README.md', 'line': 29, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/build_synthesis/README.md'}, {'label': '🏠 Project Root', 'text': 'README', 'path': '../../../../../../README.md', 'line': 30, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/README.md'}], 'key_artifacts': [{'label': 'Functional Spec', 'path': 'SPEC.md', 'line': 8, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/build_synthesis/integration/SPEC.md'}], 'issues': []}, {'file': 'tests/unit/build_synthesis/unit/AGENTS.md', 'parent': {'label': 'Unit', 'path': '../AGENTS.md', 'line': 4, 'is_generic': False}, 'children': [], 'navigation_links': [{'label': 'Human Documentation', 'text': 'README.md', 'path': 'README.md', 'line': 27, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/build_synthesis/unit/README.md'}, {'label': 'Functional Specification', 'text': 'SPEC.md', 'path': 'SPEC.md', 'line': 28, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/build_synthesis/unit/SPEC.md'}, {'label': '📁 Parent Directory', 'text': 'build_synthesis', 'path': '../README.md', 'line': 29, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/build_synthesis/README.md'}, {'label': '🏠 Project Root', 'text': 'README', 'path': '../../../../../../README.md', 'line': 30, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/README.md'}], 'key_artifacts': [{'label': 'Functional Spec', 'path': 'SPEC.md', 'line': 8, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/build_synthesis/unit/SPEC.md'}], 'issues': []}, {'file': 'tests/unit/cache/AGENTS.md', 'parent': {'label': 'Cache', 'path': '../AGENTS.md', 'line': 4, 'is_generic': False}, 'children': [], 'navigation_links': [{'label': 'Human Documentation', 'text': 'README.md', 'path': 'README.md', 'line': 28, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/cache/README.md'}, {'label': 'Functional Specification', 'text': 'SPEC.md', 'path': 'SPEC.md', 'line': 29, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/cache/SPEC.md'}, {'label': '📁 Parent Directory', 'text': 'unit', 'path': '../README.md', 'line': 30, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/README.md'}, {'label': '🏠 Project Root', 'text': 'README', 'path': '../../../../../README.md', 'line': 31, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/README.md'}], 'key_artifacts': [{'label': 'Functional Spec', 'path': 'SPEC.md', 'line': 8, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/cache/SPEC.md'}], 'issues': []}, {'file': 'tests/unit/cerebrum/AGENTS.md', 'parent': {'label': 'Cerebrum', 'path': '../AGENTS.md', 'line': 4, 'is_generic': False}, 'children': [{'label': 'integration', 'path': 'integration/AGENTS.md', 'line': 6, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/cerebrum/integration/AGENTS.md'}], 'navigation_links': [{'label': 'Human Documentation', 'text': 'README.md', 'path': 'README.md', 'line': 32, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/cerebrum/README.md'}, {'label': 'Functional Specification', 'text': 'SPEC.md', 'path': 'SPEC.md', 'line': 33, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/cerebrum/SPEC.md'}, {'label': '📁 Parent Directory', 'text': 'unit', 'path': '../README.md', 'line': 34, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/README.md'}, {'label': '🏠 Project Root', 'text': 'README', 'path': '../../../../../README.md', 'line': 35, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/README.md'}], 'key_artifacts': [{'label': 'Functional Spec', 'path': 'SPEC.md', 'line': 9, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/cerebrum/SPEC.md'}], 'issues': []}, {'file': 'tests/unit/cerebrum/integration/AGENTS.md', 'parent': {'label': 'Integration', 'path': '../AGENTS.md', 'line': 4, 'is_generic': False}, 'children': [], 'navigation_links': [{'label': 'Human Documentation', 'text': 'README.md', 'path': 'README.md', 'line': 29, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/cerebrum/integration/README.md'}, {'label': 'Functional Specification', 'text': 'SPEC.md', 'path': 'SPEC.md', 'line': 30, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/cerebrum/integration/SPEC.md'}, {'label': '📁 Parent Directory', 'text': 'cerebrum', 'path': '../README.md', 'line': 31, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/cerebrum/README.md'}, {'label': '🏠 Project Root', 'text': 'README', 'path': '../../../../../../README.md', 'line': 32, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/README.md'}], 'key_artifacts': [{'label': 'Functional Spec', 'path': 'SPEC.md', 'line': 8, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/cerebrum/integration/SPEC.md'}], 'issues': []}, {'file': 'tests/unit/cerebrum/unit/AGENTS.md', 'parent': {'label': 'Unit', 'path': '../AGENTS.md', 'line': 4, 'is_generic': False}, 'children': [], 'navigation_links': [{'label': 'Human Documentation', 'text': 'README.md', 'path': 'README.md', 'line': 31, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/cerebrum/unit/README.md'}, {'label': 'Functional Specification', 'text': 'SPEC.md', 'path': 'SPEC.md', 'line': 32, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/cerebrum/unit/SPEC.md'}, {'label': '📁 Parent Directory', 'text': 'cerebrum', 'path': '../README.md', 'line': 33, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/cerebrum/README.md'}, {'label': '🏠 Project Root', 'text': 'README', 'path': '../../../../../../README.md', 'line': 34, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/README.md'}], 'key_artifacts': [{'label': 'Functional Spec', 'path': 'SPEC.md', 'line': 8, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/cerebrum/unit/SPEC.md'}], 'issues': []}, {'file': 'tests/unit/ci_cd_automation/AGENTS.md', 'parent': {'label': 'Ci Cd Automation', 'path': '../AGENTS.md', 'line': 4, 'is_generic': False}, 'children': [], 'navigation_links': [{'label': 'Human Documentation', 'text': 'README.md', 'path': 'README.md', 'line': 28, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/ci_cd_automation/README.md'}, {'label': 'Functional Specification', 'text': 'SPEC.md', 'path': 'SPEC.md', 'line': 29, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/ci_cd_automation/SPEC.md'}, {'label': '📁 Parent Directory', 'text': 'unit', 'path': '../README.md', 'line': 30, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/README.md'}, {'label': '🏠 Project Root', 'text': 'README', 'path': '../../../../../README.md', 'line': 31, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/README.md'}], 'key_artifacts': [{'label': 'Functional Spec', 'path': 'SPEC.md', 'line': 8, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/ci_cd_automation/SPEC.md'}], 'issues': []}, {'file': 'tests/unit/cli/AGENTS.md', 'parent': {'label': 'Cli', 'path': '../AGENTS.md', 'line': 4, 'is_generic': False}, 'children': [], 'navigation_links': [{'label': 'Human Documentation', 'text': 'README.md', 'path': 'README.md', 'line': 29, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/cli/README.md'}, {'label': 'Functional Specification', 'text': 'SPEC.md', 'path': 'SPEC.md', 'line': 30, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/cli/SPEC.md'}, {'label': '📁 Parent Directory', 'text': 'unit', 'path': '../README.md', 'line': 31, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/README.md'}, {'label': '🏠 Project Root', 'text': 'README', 'path': '../../../../../README.md', 'line': 32, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/README.md'}], 'key_artifacts': [{'label': 'Functional Spec', 'path': 'SPEC.md', 'line': 8, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/cli/SPEC.md'}], 'issues': []}, {'file': 'tests/unit/cloud/AGENTS.md', 'parent': {'label': 'Cloud', 'path': '../AGENTS.md', 'line': 4, 'is_generic': False}, 'children': [], 'navigation_links': [{'label': 'Human Documentation', 'text': 'README.md', 'path': 'README.md', 'line': 30, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/cloud/README.md'}, {'label': 'Functional Specification', 'text': 'SPEC.md', 'path': 'SPEC.md', 'line': 31, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/cloud/SPEC.md'}, {'label': '📁 Parent Directory', 'text': 'unit', 'path': '../README.md', 'line': 32, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/README.md'}, {'label': '🏠 Project Root', 'text': 'README', 'path': '../../../../../README.md', 'line': 33, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/README.md'}], 'key_artifacts': [{'label': 'Functional Spec', 'path': 'SPEC.md', 'line': 8, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/cloud/SPEC.md'}], 'issues': []}, {'file': 'tests/unit/coding/AGENTS.md', 'parent': {'label': 'Coding', 'path': '../AGENTS.md', 'line': 4, 'is_generic': False}, 'children': [{'label': 'execution', 'path': 'execution/AGENTS.md', 'line': 6, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/coding/execution/AGENTS.md'}], 'navigation_links': [{'label': 'Human Documentation', 'text': 'README.md', 'path': 'README.md', 'line': 35, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/coding/README.md'}, {'label': 'Functional Specification', 'text': 'SPEC.md', 'path': 'SPEC.md', 'line': 36, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/coding/SPEC.md'}, {'label': '📁 Parent Directory', 'text': 'unit', 'path': '../README.md', 'line': 37, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/README.md'}, {'label': '🏠 Project Root', 'text': 'README', 'path': '../../../../../README.md', 'line': 38, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/README.md'}], 'key_artifacts': [{'label': 'Functional Spec', 'path': 'SPEC.md', 'line': 11, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/coding/SPEC.md'}], 'issues': []}, {'file': 'tests/unit/coding/execution/AGENTS.md', 'parent': {'label': 'Execution', 'path': '../AGENTS.md', 'line': 4, 'is_generic': False}, 'children': [{'label': 'integration', 'path': 'integration/AGENTS.md', 'line': 6, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/coding/execution/integration/AGENTS.md'}], 'navigation_links': [{'label': 'Human Documentation', 'text': 'README.md', 'path': 'README.md', 'line': 32, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/coding/execution/README.md'}, {'label': 'Functional Specification', 'text': 'SPEC.md', 'path': 'SPEC.md', 'line': 33, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/coding/execution/SPEC.md'}, {'label': '📁 Parent Directory', 'text': 'coding', 'path': '../README.md', 'line': 34, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/coding/README.md'}, {'label': '🏠 Project Root', 'text': 'README', 'path': '../../../../../../README.md', 'line': 35, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/README.md'}], 'key_artifacts': [{'label': 'Functional Spec', 'path': 'SPEC.md', 'line': 9, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/coding/execution/SPEC.md'}], 'issues': []}, {'file': 'tests/unit/coding/execution/integration/AGENTS.md', 'parent': {'label': 'Integration', 'path': '../AGENTS.md', 'line': 4, 'is_generic': False}, 'children': [], 'navigation_links': [{'label': 'Human Documentation', 'text': 'README.md', 'path': 'README.md', 'line': 27, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/coding/execution/integration/README.md'}, {'label': 'Functional Specification', 'text': 'SPEC.md', 'path': 'SPEC.md', 'line': 28, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/coding/execution/integration/SPEC.md'}, {'label': '📁 Parent Directory', 'text': 'execution', 'path': '../README.md', 'line': 29, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/coding/execution/README.md'}, {'label': '🏠 Project Root', 'text': 'README', 'path': '../../../../../../../README.md', 'line': 30, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/README.md'}], 'key_artifacts': [{'label': 'Functional Spec', 'path': 'SPEC.md', 'line': 8, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/coding/execution/integration/SPEC.md'}], 'issues': []}, {'file': 'tests/unit/coding/execution/unit/AGENTS.md', 'parent': {'label': 'Unit', 'path': '../AGENTS.md', 'line': 4, 'is_generic': False}, 'children': [], 'navigation_links': [{'label': 'Human Documentation', 'text': 'README.md', 'path': 'README.md', 'line': 27, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/coding/execution/unit/README.md'}, {'label': 'Functional Specification', 'text': 'SPEC.md', 'path': 'SPEC.md', 'line': 28, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/coding/execution/unit/SPEC.md'}, {'label': '📁 Parent Directory', 'text': 'execution', 'path': '../README.md', 'line': 29, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/coding/execution/README.md'}, {'label': '🏠 Project Root', 'text': 'README', 'path': '../../../../../../../README.md', 'line': 30, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/README.md'}], 'key_artifacts': [{'label': 'Functional Spec', 'path': 'SPEC.md', 'line': 8, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/coding/execution/unit/SPEC.md'}], 'issues': []}, {'file': 'tests/unit/coding/monitoring/AGENTS.md', 'parent': {'label': 'Monitoring', 'path': '../AGENTS.md', 'line': 4, 'is_generic': False}, 'children': [], 'navigation_links': [{'label': 'Human Documentation', 'text': 'README.md', 'path': 'README.md', 'line': 26, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/coding/monitoring/README.md'}, {'label': 'Functional Specification', 'text': 'SPEC.md', 'path': 'SPEC.md', 'line': 27, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/coding/monitoring/SPEC.md'}, {'label': '📁 Parent Directory', 'text': 'coding', 'path': '../README.md', 'line': 28, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/coding/README.md'}, {'label': '🏠 Project Root', 'text': 'README', 'path': '../../../../../../README.md', 'line': 29, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/README.md'}], 'key_artifacts': [{'label': 'Functional Spec', 'path': 'SPEC.md', 'line': 8, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/coding/monitoring/SPEC.md'}], 'issues': []}, {'file': 'tests/unit/coding/review/AGENTS.md', 'parent': {'label': 'Review', 'path': '../AGENTS.md', 'line': 4, 'is_generic': False}, 'children': [{'label': 'e2e', 'path': 'e2e/AGENTS.md', 'line': 6, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/coding/review/e2e/AGENTS.md'}], 'navigation_links': [{'label': 'Human Documentation', 'text': 'README.md', 'path': 'README.md', 'line': 37, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/coding/review/README.md'}, {'label': 'Functional Specification', 'text': 'SPEC.md', 'path': 'SPEC.md', 'line': 38, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/coding/review/SPEC.md'}, {'label': '📁 Parent Directory', 'text': 'coding', 'path': '../README.md', 'line': 39, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/coding/README.md'}, {'label': '🏠 Project Root', 'text': 'README', 'path': '../../../../../../README.md', 'line': 40, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/README.md'}], 'key_artifacts': [{'label': 'Functional Spec', 'path': 'SPEC.md', 'line': 12, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/coding/review/SPEC.md'}], 'issues': []}, {'file': 'tests/unit/coding/review/e2e/AGENTS.md', 'parent': {'label': 'E2E', 'path': '../AGENTS.md', 'line': 4, 'is_generic': False}, 'children': [], 'navigation_links': [{'label': 'Human Documentation', 'text': 'README.md', 'path': 'README.md', 'line': 26, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/coding/review/e2e/README.md'}, {'label': 'Functional Specification', 'text': 'SPEC.md', 'path': 'SPEC.md', 'line': 27, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/coding/review/e2e/SPEC.md'}, {'label': '📁 Parent Directory', 'text': 'review', 'path': '../README.md', 'line': 28, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/coding/review/README.md'}, {'label': '🏠 Project Root', 'text': 'README', 'path': '../../../../../../../README.md', 'line': 29, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/README.md'}], 'key_artifacts': [{'label': 'Functional Spec', 'path': 'SPEC.md', 'line': 8, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/coding/review/e2e/SPEC.md'}], 'issues': []}, {'file': 'tests/unit/coding/review/fixtures/AGENTS.md', 'parent': {'label': 'Fixtures', 'path': '../AGENTS.md', 'line': 4, 'is_generic': False}, 'children': [{'label': 'python', 'path': 'python/AGENTS.md', 'line': 6, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/coding/review/fixtures/python/AGENTS.md'}], 'navigation_links': [{'label': 'Human Documentation', 'text': 'README.md', 'path': 'README.md', 'line': 27, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/coding/review/fixtures/README.md'}, {'label': 'Functional Specification', 'text': 'SPEC.md', 'path': 'SPEC.md', 'line': 28, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/coding/review/fixtures/SPEC.md'}, {'label': '📁 Parent Directory', 'text': 'review', 'path': '../README.md', 'line': 29, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/coding/review/README.md'}, {'label': '🏠 Project Root', 'text': 'README', 'path': '../../../../../../../README.md', 'line': 30, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/README.md'}], 'key_artifacts': [{'label': 'Functional Spec', 'path': 'SPEC.md', 'line': 8, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/coding/review/fixtures/SPEC.md'}], 'issues': []}, {'file': 'tests/unit/coding/review/fixtures/python/AGENTS.md', 'parent': {'label': 'Python', 'path': '../AGENTS.md', 'line': 4, 'is_generic': False}, 'children': [], 'navigation_links': [{'label': 'Human Documentation', 'text': 'README.md', 'path': 'README.md', 'line': 30, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/coding/review/fixtures/python/README.md'}, {'label': 'Functional Specification', 'text': 'SPEC.md', 'path': 'SPEC.md', 'line': 31, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/coding/review/fixtures/python/SPEC.md'}, {'label': '📁 Parent Directory', 'text': 'fixtures', 'path': '../README.md', 'line': 32, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/coding/review/fixtures/README.md'}, {'label': '🏠 Project Root', 'text': 'README', 'path': '../../../../../../../../README.md', 'line': 33, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/README.md'}], 'key_artifacts': [{'label': 'Functional Spec', 'path': 'SPEC.md', 'line': 8, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/coding/review/fixtures/python/SPEC.md'}], 'issues': []}, {'file': 'tests/unit/coding/review/integration/AGENTS.md', 'parent': {'label': 'Integration', 'path': '../AGENTS.md', 'line': 4, 'is_generic': False}, 'children': [], 'navigation_links': [{'label': 'Human Documentation', 'text': 'README.md', 'path': 'README.md', 'line': 26, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/coding/review/integration/README.md'}, {'label': 'Functional Specification', 'text': 'SPEC.md', 'path': 'SPEC.md', 'line': 27, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/coding/review/integration/SPEC.md'}, {'label': '📁 Parent Directory', 'text': 'review', 'path': '../README.md', 'line': 28, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/coding/review/README.md'}, {'label': '🏠 Project Root', 'text': 'README', 'path': '../../../../../../../README.md', 'line': 29, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/README.md'}], 'key_artifacts': [{'label': 'Functional Spec', 'path': 'SPEC.md', 'line': 8, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/coding/review/integration/SPEC.md'}], 'issues': []}, {'file': 'tests/unit/coding/review/performance/AGENTS.md', 'parent': {'label': 'Performance', 'path': '../AGENTS.md', 'line': 4, 'is_generic': False}, 'children': [], 'navigation_links': [{'label': 'Human Documentation', 'text': 'README.md', 'path': 'README.md', 'line': 26, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/coding/review/performance/README.md'}, {'label': 'Functional Specification', 'text': 'SPEC.md', 'path': 'SPEC.md', 'line': 27, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/coding/review/performance/SPEC.md'}, {'label': '📁 Parent Directory', 'text': 'review', 'path': '../README.md', 'line': 28, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/coding/review/README.md'}, {'label': '🏠 Project Root', 'text': 'README', 'path': '../../../../../../../README.md', 'line': 29, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/README.md'}], 'key_artifacts': [{'label': 'Functional Spec', 'path': 'SPEC.md', 'line': 8, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/coding/review/performance/SPEC.md'}], 'issues': []}, {'file': 'tests/unit/coding/review/unit/AGENTS.md', 'parent': {'label': 'Unit', 'path': '../AGENTS.md', 'line': 4, 'is_generic': False}, 'children': [], 'navigation_links': [{'label': 'Human Documentation', 'text': 'README.md', 'path': 'README.md', 'line': 26, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/coding/review/unit/README.md'}, {'label': 'Functional Specification', 'text': 'SPEC.md', 'path': 'SPEC.md', 'line': 27, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/coding/review/unit/SPEC.md'}, {'label': '📁 Parent Directory', 'text': 'review', 'path': '../README.md', 'line': 28, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/coding/review/README.md'}, {'label': '🏠 Project Root', 'text': 'README', 'path': '../../../../../../../README.md', 'line': 29, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/README.md'}], 'key_artifacts': [{'label': 'Functional Spec', 'path': 'SPEC.md', 'line': 8, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/coding/review/unit/SPEC.md'}], 'issues': []}, {'file': 'tests/unit/coding/sandbox/AGENTS.md', 'parent': {'label': 'Sandbox', 'path': '../AGENTS.md', 'line': 4, 'is_generic': False}, 'children': [{'label': 'integration', 'path': 'integration/AGENTS.md', 'line': 6, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/coding/sandbox/integration/AGENTS.md'}], 'navigation_links': [{'label': 'Human Documentation', 'text': 'README.md', 'path': 'README.md', 'line': 29, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/coding/sandbox/README.md'}, {'label': 'Functional Specification', 'text': 'SPEC.md', 'path': 'SPEC.md', 'line': 30, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/coding/sandbox/SPEC.md'}, {'label': '📁 Parent Directory', 'text': 'coding', 'path': '../README.md', 'line': 31, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/coding/README.md'}, {'label': '🏠 Project Root', 'text': 'README', 'path': '../../../../../../README.md', 'line': 32, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/README.md'}], 'key_artifacts': [{'label': 'Functional Spec', 'path': 'SPEC.md', 'line': 9, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/coding/sandbox/SPEC.md'}], 'issues': []}, {'file': 'tests/unit/coding/sandbox/integration/AGENTS.md', 'parent': {'label': 'Integration', 'path': '../AGENTS.md', 'line': 4, 'is_generic': False}, 'children': [], 'navigation_links': [{'label': 'Human Documentation', 'text': 'README.md', 'path': 'README.md', 'line': 27, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/coding/sandbox/integration/README.md'}, {'label': 'Functional Specification', 'text': 'SPEC.md', 'path': 'SPEC.md', 'line': 28, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/coding/sandbox/integration/SPEC.md'}, {'label': '📁 Parent Directory', 'text': 'sandbox', 'path': '../README.md', 'line': 29, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/coding/sandbox/README.md'}, {'label': '🏠 Project Root', 'text': 'README', 'path': '../../../../../../../README.md', 'line': 30, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/README.md'}], 'key_artifacts': [{'label': 'Functional Spec', 'path': 'SPEC.md', 'line': 8, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/coding/sandbox/integration/SPEC.md'}], 'issues': []}, {'file': 'tests/unit/coding/sandbox/unit/AGENTS.md', 'parent': {'label': 'Unit', 'path': '../AGENTS.md', 'line': 4, 'is_generic': False}, 'children': [], 'navigation_links': [{'label': 'Human Documentation', 'text': 'README.md', 'path': 'README.md', 'line': 27, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/coding/sandbox/unit/README.md'}, {'label': 'Functional Specification', 'text': 'SPEC.md', 'path': 'SPEC.md', 'line': 28, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/coding/sandbox/unit/SPEC.md'}, {'label': '📁 Parent Directory', 'text': 'sandbox', 'path': '../README.md', 'line': 29, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/coding/sandbox/README.md'}, {'label': '🏠 Project Root', 'text': 'README', 'path': '../../../../../../../README.md', 'line': 30, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/README.md'}], 'key_artifacts': [{'label': 'Functional Spec', 'path': 'SPEC.md', 'line': 8, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/coding/sandbox/unit/SPEC.md'}], 'issues': []}, {'file': 'tests/unit/config_management/AGENTS.md', 'parent': {'label': 'Config Management', 'path': '../AGENTS.md', 'line': 4, 'is_generic': False}, 'children': [], 'navigation_links': [{'label': 'Human Documentation', 'text': 'README.md', 'path': 'README.md', 'line': 29, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/config_management/README.md'}, {'label': 'Functional Specification', 'text': 'SPEC.md', 'path': 'SPEC.md', 'line': 30, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/config_management/SPEC.md'}, {'label': '📁 Parent Directory', 'text': 'unit', 'path': '../README.md', 'line': 31, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/README.md'}, {'label': '🏠 Project Root', 'text': 'README', 'path': '../../../../../README.md', 'line': 32, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/README.md'}], 'key_artifacts': [{'label': 'Functional Spec', 'path': 'SPEC.md', 'line': 8, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/config_management/SPEC.md'}], 'issues': []}, {'file': 'tests/unit/containerization/AGENTS.md', 'parent': {'label': 'Containerization', 'path': '../AGENTS.md', 'line': 4, 'is_generic': False}, 'children': [], 'navigation_links': [{'label': 'Human Documentation', 'text': 'README.md', 'path': 'README.md', 'line': 29, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/containerization/README.md'}, {'label': 'Functional Specification', 'text': 'SPEC.md', 'path': 'SPEC.md', 'line': 30, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/containerization/SPEC.md'}, {'label': '📁 Parent Directory', 'text': 'unit', 'path': '../README.md', 'line': 31, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/README.md'}, {'label': '🏠 Project Root', 'text': 'README', 'path': '../../../../../README.md', 'line': 32, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/README.md'}], 'key_artifacts': [{'label': 'Functional Spec', 'path': 'SPEC.md', 'line': 8, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/containerization/SPEC.md'}], 'issues': []}, {'file': 'tests/unit/data_visualization/AGENTS.md', 'parent': {'label': 'Data Visualization', 'path': '../AGENTS.md', 'line': 4, 'is_generic': False}, 'children': [{'label': 'integration', 'path': 'integration/AGENTS.md', 'line': 6, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/data_visualization/integration/AGENTS.md'}], 'navigation_links': [{'label': 'Human Documentation', 'text': 'README.md', 'path': 'README.md', 'line': 31, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/data_visualization/README.md'}, {'label': 'Functional Specification', 'text': 'SPEC.md', 'path': 'SPEC.md', 'line': 32, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/data_visualization/SPEC.md'}, {'label': '📁 Parent Directory', 'text': 'unit', 'path': '../README.md', 'line': 33, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/README.md'}, {'label': '🏠 Project Root', 'text': 'README', 'path': '../../../../../README.md', 'line': 34, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/README.md'}], 'key_artifacts': [{'label': 'Functional Spec', 'path': 'SPEC.md', 'line': 9, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/data_visualization/SPEC.md'}], 'issues': []}, {'file': 'tests/unit/data_visualization/integration/AGENTS.md', 'parent': {'label': 'Integration', 'path': '../AGENTS.md', 'line': 4, 'is_generic': False}, 'children': [], 'navigation_links': [{'label': 'Human Documentation', 'text': 'README.md', 'path': 'README.md', 'line': 27, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/data_visualization/integration/README.md'}, {'label': 'Functional Specification', 'text': 'SPEC.md', 'path': 'SPEC.md', 'line': 28, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/data_visualization/integration/SPEC.md'}, {'label': '📁 Parent Directory', 'text': 'data_visualization', 'path': '../README.md', 'line': 29, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/data_visualization/README.md'}, {'label': '🏠 Project Root', 'text': 'README', 'path': '../../../../../../README.md', 'line': 30, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/README.md'}], 'key_artifacts': [{'label': 'Functional Spec', 'path': 'SPEC.md', 'line': 8, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/data_visualization/integration/SPEC.md'}], 'issues': []}, {'file': 'tests/unit/data_visualization/unit/AGENTS.md', 'parent': {'label': 'Unit', 'path': '../AGENTS.md', 'line': 4, 'is_generic': False}, 'children': [], 'navigation_links': [{'label': 'Human Documentation', 'text': 'README.md', 'path': 'README.md', 'line': 27, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/data_visualization/unit/README.md'}, {'label': 'Functional Specification', 'text': 'SPEC.md', 'path': 'SPEC.md', 'line': 28, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/data_visualization/unit/SPEC.md'}, {'label': '📁 Parent Directory', 'text': 'data_visualization', 'path': '../README.md', 'line': 29, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/data_visualization/README.md'}, {'label': '🏠 Project Root', 'text': 'README', 'path': '../../../../../../README.md', 'line': 30, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/README.md'}], 'key_artifacts': [{'label': 'Functional Spec', 'path': 'SPEC.md', 'line': 8, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/data_visualization/unit/SPEC.md'}], 'issues': []}, {'file': 'tests/unit/database_management/AGENTS.md', 'parent': {'label': 'Database Management', 'path': '../AGENTS.md', 'line': 4, 'is_generic': False}, 'children': [], 'navigation_links': [{'label': 'Human Documentation', 'text': 'README.md', 'path': 'README.md', 'line': 28, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/database_management/README.md'}, {'label': 'Functional Specification', 'text': 'SPEC.md', 'path': 'SPEC.md', 'line': 29, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/database_management/SPEC.md'}, {'label': '📁 Parent Directory', 'text': 'unit', 'path': '../README.md', 'line': 30, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/README.md'}, {'label': '🏠 Project Root', 'text': 'README', 'path': '../../../../../README.md', 'line': 31, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/README.md'}], 'key_artifacts': [{'label': 'Functional Spec', 'path': 'SPEC.md', 'line': 8, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/database_management/SPEC.md'}], 'issues': []}, {'file': 'tests/unit/documentation/AGENTS.md', 'parent': {'label': 'Documentation', 'path': '../AGENTS.md', 'line': 4, 'is_generic': False}, 'children': [{'label': 'integration', 'path': 'integration/AGENTS.md', 'line': 6, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/documentation/integration/AGENTS.md'}], 'navigation_links': [{'label': 'Human Documentation', 'text': 'README.md', 'path': 'README.md', 'line': 32, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/documentation/README.md'}, {'label': 'Functional Specification', 'text': 'SPEC.md', 'path': 'SPEC.md', 'line': 33, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/documentation/SPEC.md'}, {'label': '📁 Parent Directory', 'text': 'unit', 'path': '../README.md', 'line': 34, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/README.md'}, {'label': '🏠 Project Root', 'text': 'README', 'path': '../../../../../README.md', 'line': 35, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/README.md'}], 'key_artifacts': [{'label': 'Functional Spec', 'path': 'SPEC.md', 'line': 9, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/documentation/SPEC.md'}], 'issues': []}, {'file': 'tests/unit/documentation/integration/AGENTS.md', 'parent': {'label': 'Integration', 'path': '../AGENTS.md', 'line': 4, 'is_generic': False}, 'children': [], 'navigation_links': [{'label': 'Human Documentation', 'text': 'README.md', 'path': 'README.md', 'line': 27, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/documentation/integration/README.md'}, {'label': 'Functional Specification', 'text': 'SPEC.md', 'path': 'SPEC.md', 'line': 28, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/documentation/integration/SPEC.md'}, {'label': '📁 Parent Directory', 'text': 'documentation', 'path': '../README.md', 'line': 29, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/documentation/README.md'}, {'label': '🏠 Project Root', 'text': 'README', 'path': '../../../../../../README.md', 'line': 30, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/README.md'}], 'key_artifacts': [{'label': 'Functional Spec', 'path': 'SPEC.md', 'line': 8, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/documentation/integration/SPEC.md'}], 'issues': []}, {'file': 'tests/unit/documentation/unit/AGENTS.md', 'parent': {'label': 'Unit', 'path': '../AGENTS.md', 'line': 4, 'is_generic': False}, 'children': [], 'navigation_links': [{'label': 'Human Documentation', 'text': 'README.md', 'path': 'README.md', 'line': 27, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/documentation/unit/README.md'}, {'label': 'Functional Specification', 'text': 'SPEC.md', 'path': 'SPEC.md', 'line': 28, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/documentation/unit/SPEC.md'}, {'label': '📁 Parent Directory', 'text': 'documentation', 'path': '../README.md', 'line': 29, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/documentation/README.md'}, {'label': '🏠 Project Root', 'text': 'README', 'path': '../../../../../../README.md', 'line': 30, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/README.md'}], 'key_artifacts': [{'label': 'Functional Spec', 'path': 'SPEC.md', 'line': 8, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/documentation/unit/SPEC.md'}], 'issues': []}, {'file': 'tests/unit/documents/AGENTS.md', 'parent': {'label': 'Documents', 'path': '../AGENTS.md', 'line': 4, 'is_generic': False}, 'children': [{'label': 'integration', 'path': 'integration/AGENTS.md', 'line': 6, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/documents/integration/AGENTS.md'}], 'navigation_links': [{'label': 'Human Documentation', 'text': 'README.md', 'path': 'README.md', 'line': 31, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/documents/README.md'}, {'label': 'Functional Specification', 'text': 'SPEC.md', 'path': 'SPEC.md', 'line': 32, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/documents/SPEC.md'}, {'label': '📁 Parent Directory', 'text': 'unit', 'path': '../README.md', 'line': 33, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/README.md'}, {'label': '🏠 Project Root', 'text': 'README', 'path': '../../../../../README.md', 'line': 34, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/README.md'}], 'key_artifacts': [{'label': 'Functional Spec', 'path': 'SPEC.md', 'line': 9, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/documents/SPEC.md'}], 'issues': []}, {'file': 'tests/unit/documents/integration/AGENTS.md', 'parent': {'label': 'Integration', 'path': '../AGENTS.md', 'line': 4, 'is_generic': False}, 'children': [], 'navigation_links': [{'label': 'Human Documentation', 'text': 'README.md', 'path': 'README.md', 'line': 26, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/documents/integration/README.md'}, {'label': 'Functional Specification', 'text': 'SPEC.md', 'path': 'SPEC.md', 'line': 27, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/documents/integration/SPEC.md'}, {'label': '📁 Parent Directory', 'text': 'documents', 'path': '../README.md', 'line': 28, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/documents/README.md'}, {'label': '🏠 Project Root', 'text': 'README', 'path': '../../../../../../README.md', 'line': 29, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/README.md'}], 'key_artifacts': [{'label': 'Functional Spec', 'path': 'SPEC.md', 'line': 8, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/documents/integration/SPEC.md'}], 'issues': []}, {'file': 'tests/unit/documents/unit/AGENTS.md', 'parent': {'label': 'Unit', 'path': '../AGENTS.md', 'line': 4, 'is_generic': False}, 'children': [{'label': 'core', 'path': 'core/AGENTS.md', 'line': 6, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/documents/unit/core/AGENTS.md'}], 'navigation_links': [{'label': 'Human Documentation', 'text': 'README.md', 'path': 'README.md', 'line': 33, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/documents/unit/README.md'}, {'label': 'Functional Specification', 'text': 'SPEC.md', 'path': 'SPEC.md', 'line': 34, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/documents/unit/SPEC.md'}, {'label': '📁 Parent Directory', 'text': 'documents', 'path': '../README.md', 'line': 35, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/documents/README.md'}, {'label': '🏠 Project Root', 'text': 'README', 'path': '../../../../../../README.md', 'line': 36, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/README.md'}], 'key_artifacts': [{'label': 'Functional Spec', 'path': 'SPEC.md', 'line': 11, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/documents/unit/SPEC.md'}], 'issues': []}, {'file': 'tests/unit/documents/unit/core/AGENTS.md', 'parent': {'label': 'Core', 'path': '../AGENTS.md', 'line': 4, 'is_generic': False}, 'children': [], 'navigation_links': [{'label': 'Human Documentation', 'text': 'README.md', 'path': 'README.md', 'line': 31, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/documents/unit/core/README.md'}, {'label': 'Functional Specification', 'text': 'SPEC.md', 'path': 'SPEC.md', 'line': 32, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/documents/unit/core/SPEC.md'}, {'label': '📁 Parent Directory', 'text': 'unit', 'path': '../README.md', 'line': 33, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/documents/unit/README.md'}, {'label': '🏠 Project Root', 'text': 'README', 'path': '../../../../../../../README.md', 'line': 34, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/README.md'}], 'key_artifacts': [{'label': 'Functional Spec', 'path': 'SPEC.md', 'line': 8, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/documents/unit/core/SPEC.md'}], 'issues': []}, {'file': 'tests/unit/documents/unit/formats/AGENTS.md', 'parent': {'label': 'Formats', 'path': '../AGENTS.md', 'line': 4, 'is_generic': False}, 'children': [], 'navigation_links': [{'label': 'Human Documentation', 'text': 'README.md', 'path': 'README.md', 'line': 31, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/documents/unit/formats/README.md'}, {'label': 'Functional Specification', 'text': 'SPEC.md', 'path': 'SPEC.md', 'line': 32, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/documents/unit/formats/SPEC.md'}, {'label': '📁 Parent Directory', 'text': 'unit', 'path': '../README.md', 'line': 33, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/documents/unit/README.md'}, {'label': '🏠 Project Root', 'text': 'README', 'path': '../../../../../../../README.md', 'line': 34, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/README.md'}], 'key_artifacts': [{'label': 'Functional Spec', 'path': 'SPEC.md', 'line': 8, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/documents/unit/formats/SPEC.md'}], 'issues': []}, {'file': 'tests/unit/documents/unit/models/AGENTS.md', 'parent': {'label': 'Models', 'path': '../AGENTS.md', 'line': 4, 'is_generic': False}, 'children': [], 'navigation_links': [{'label': 'Human Documentation', 'text': 'README.md', 'path': 'README.md', 'line': 28, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/documents/unit/models/README.md'}, {'label': 'Functional Specification', 'text': 'SPEC.md', 'path': 'SPEC.md', 'line': 29, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/documents/unit/models/SPEC.md'}, {'label': '📁 Parent Directory', 'text': 'unit', 'path': '../README.md', 'line': 30, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/documents/unit/README.md'}, {'label': '🏠 Project Root', 'text': 'README', 'path': '../../../../../../../README.md', 'line': 31, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/README.md'}], 'key_artifacts': [{'label': 'Functional Spec', 'path': 'SPEC.md', 'line': 8, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/documents/unit/models/SPEC.md'}], 'issues': []}, {'file': 'tests/unit/documents/unit/utils/AGENTS.md', 'parent': {'label': 'Utils', 'path': '../AGENTS.md', 'line': 4, 'is_generic': False}, 'children': [], 'navigation_links': [{'label': 'Human Documentation', 'text': 'README.md', 'path': 'README.md', 'line': 28, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/documents/unit/utils/README.md'}, {'label': 'Functional Specification', 'text': 'SPEC.md', 'path': 'SPEC.md', 'line': 29, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/documents/unit/utils/SPEC.md'}, {'label': '📁 Parent Directory', 'text': 'unit', 'path': '../README.md', 'line': 30, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/documents/unit/README.md'}, {'label': '🏠 Project Root', 'text': 'README', 'path': '../../../../../../../README.md', 'line': 31, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/README.md'}], 'key_artifacts': [{'label': 'Functional Spec', 'path': 'SPEC.md', 'line': 8, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/documents/unit/utils/SPEC.md'}], 'issues': []}, {'file': 'tests/unit/environment_setup/AGENTS.md', 'parent': {'label': 'Environment Setup', 'path': '../AGENTS.md', 'line': 4, 'is_generic': False}, 'children': [{'label': 'integration', 'path': 'integration/AGENTS.md', 'line': 6, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/environment_setup/integration/AGENTS.md'}], 'navigation_links': [{'label': 'Human Documentation', 'text': 'README.md', 'path': 'README.md', 'line': 32, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/environment_setup/README.md'}, {'label': 'Functional Specification', 'text': 'SPEC.md', 'path': 'SPEC.md', 'line': 33, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/environment_setup/SPEC.md'}, {'label': '📁 Parent Directory', 'text': 'unit', 'path': '../README.md', 'line': 34, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/README.md'}, {'label': '🏠 Project Root', 'text': 'README', 'path': '../../../../../README.md', 'line': 35, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/README.md'}], 'key_artifacts': [{'label': 'Functional Spec', 'path': 'SPEC.md', 'line': 9, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/environment_setup/SPEC.md'}], 'issues': []}, {'file': 'tests/unit/environment_setup/integration/AGENTS.md', 'parent': {'label': 'Integration', 'path': '../AGENTS.md', 'line': 4, 'is_generic': False}, 'children': [], 'navigation_links': [{'label': 'Human Documentation', 'text': 'README.md', 'path': 'README.md', 'line': 27, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/environment_setup/integration/README.md'}, {'label': 'Functional Specification', 'text': 'SPEC.md', 'path': 'SPEC.md', 'line': 28, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/environment_setup/integration/SPEC.md'}, {'label': '📁 Parent Directory', 'text': 'environment_setup', 'path': '../README.md', 'line': 29, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/environment_setup/README.md'}, {'label': '🏠 Project Root', 'text': 'README', 'path': '../../../../../../README.md', 'line': 30, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/README.md'}], 'key_artifacts': [{'label': 'Functional Spec', 'path': 'SPEC.md', 'line': 8, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/environment_setup/integration/SPEC.md'}], 'issues': []}, {'file': 'tests/unit/environment_setup/unit/AGENTS.md', 'parent': {'label': 'Unit', 'path': '../AGENTS.md', 'line': 4, 'is_generic': False}, 'children': [], 'navigation_links': [{'label': 'Human Documentation', 'text': 'README.md', 'path': 'README.md', 'line': 27, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/environment_setup/unit/README.md'}, {'label': 'Functional Specification', 'text': 'SPEC.md', 'path': 'SPEC.md', 'line': 28, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/environment_setup/unit/SPEC.md'}, {'label': '📁 Parent Directory', 'text': 'environment_setup', 'path': '../README.md', 'line': 29, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/environment_setup/README.md'}, {'label': '🏠 Project Root', 'text': 'README', 'path': '../../../../../../README.md', 'line': 30, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/README.md'}], 'key_artifacts': [{'label': 'Functional Spec', 'path': 'SPEC.md', 'line': 8, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/environment_setup/unit/SPEC.md'}], 'issues': []}, {'file': 'tests/unit/events/AGENTS.md', 'parent': {'label': 'Events', 'path': '../AGENTS.md', 'line': 4, 'is_generic': False}, 'children': [], 'navigation_links': [{'label': 'Human Documentation', 'text': 'README.md', 'path': 'README.md', 'line': 28, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/events/README.md'}, {'label': 'Functional Specification', 'text': 'SPEC.md', 'path': 'SPEC.md', 'line': 29, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/events/SPEC.md'}, {'label': '📁 Parent Directory', 'text': 'unit', 'path': '../README.md', 'line': 30, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/README.md'}, {'label': '🏠 Project Root', 'text': 'README', 'path': '../../../../../README.md', 'line': 31, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/README.md'}], 'key_artifacts': [{'label': 'Functional Spec', 'path': 'SPEC.md', 'line': 8, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/events/SPEC.md'}], 'issues': []}, {'file': 'tests/unit/exceptions/AGENTS.md', 'parent': {'label': 'Exceptions', 'path': '../AGENTS.md', 'line': 4, 'is_generic': False}, 'children': [], 'navigation_links': [{'label': 'Human Documentation', 'text': 'README.md', 'path': 'README.md', 'line': 28, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/exceptions/README.md'}, {'label': 'Functional Specification', 'text': 'SPEC.md', 'path': 'SPEC.md', 'line': 29, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/exceptions/SPEC.md'}, {'label': '📁 Parent Directory', 'text': 'unit', 'path': '../README.md', 'line': 30, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/README.md'}, {'label': '🏠 Project Root', 'text': 'README', 'path': '../../../../../README.md', 'line': 31, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/README.md'}], 'key_artifacts': [{'label': 'Functional Spec', 'path': 'SPEC.md', 'line': 8, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/exceptions/SPEC.md'}], 'issues': []}, {'file': 'tests/unit/fpf/AGENTS.md', 'parent': {'label': 'Fpf', 'path': '../AGENTS.md', 'line': 4, 'is_generic': False}, 'children': [], 'navigation_links': [{'label': 'Human Documentation', 'text': 'README.md', 'path': 'README.md', 'line': 38, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/fpf/README.md'}, {'label': 'Functional Specification', 'text': 'SPEC.md', 'path': 'SPEC.md', 'line': 39, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/fpf/SPEC.md'}, {'label': '📁 Parent Directory', 'text': 'unit', 'path': '../README.md', 'line': 40, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/README.md'}, {'label': '🏠 Project Root', 'text': 'README', 'path': '../../../../../README.md', 'line': 41, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/README.md'}], 'key_artifacts': [{'label': 'Functional Spec', 'path': 'SPEC.md', 'line': 8, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/fpf/SPEC.md'}], 'issues': []}, {'file': 'tests/unit/git_operations/AGENTS.md', 'parent': {'label': 'Git Operations', 'path': '../AGENTS.md', 'line': 4, 'is_generic': False}, 'children': [{'label': 'integration', 'path': 'integration/AGENTS.md', 'line': 6, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/git_operations/integration/AGENTS.md'}], 'navigation_links': [{'label': 'Human Documentation', 'text': 'README.md', 'path': 'README.md', 'line': 36, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/git_operations/README.md'}, {'label': 'Functional Specification', 'text': 'SPEC.md', 'path': 'SPEC.md', 'line': 37, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/git_operations/SPEC.md'}, {'label': '📁 Parent Directory', 'text': 'unit', 'path': '../README.md', 'line': 38, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/README.md'}, {'label': '🏠 Project Root', 'text': 'README', 'path': '../../../../../README.md', 'line': 39, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/README.md'}], 'key_artifacts': [{'label': 'Functional Spec', 'path': 'SPEC.md', 'line': 9, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/git_operations/SPEC.md'}], 'issues': []}, {'file': 'tests/unit/git_operations/integration/AGENTS.md', 'parent': {'label': 'Integration', 'path': '../AGENTS.md', 'line': 4, 'is_generic': False}, 'children': [], 'navigation_links': [{'label': 'Human Documentation', 'text': 'README.md', 'path': 'README.md', 'line': 29, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/git_operations/integration/README.md'}, {'label': 'Functional Specification', 'text': 'SPEC.md', 'path': 'SPEC.md', 'line': 30, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/git_operations/integration/SPEC.md'}, {'label': '📁 Parent Directory', 'text': 'git_operations', 'path': '../README.md', 'line': 31, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/git_operations/README.md'}, {'label': '🏠 Project Root', 'text': 'README', 'path': '../../../../../../README.md', 'line': 32, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/README.md'}], 'key_artifacts': [{'label': 'Functional Spec', 'path': 'SPEC.md', 'line': 8, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/git_operations/integration/SPEC.md'}], 'issues': []}, {'file': 'tests/unit/git_operations/unit/AGENTS.md', 'parent': {'label': 'Unit', 'path': '../AGENTS.md', 'line': 4, 'is_generic': False}, 'children': [], 'navigation_links': [{'label': 'Human Documentation', 'text': 'README.md', 'path': 'README.md', 'line': 29, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/git_operations/unit/README.md'}, {'label': 'Functional Specification', 'text': 'SPEC.md', 'path': 'SPEC.md', 'line': 30, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/git_operations/unit/SPEC.md'}, {'label': '📁 Parent Directory', 'text': 'git_operations', 'path': '../README.md', 'line': 31, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/git_operations/README.md'}, {'label': '🏠 Project Root', 'text': 'README', 'path': '../../../../../../README.md', 'line': 32, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/README.md'}], 'key_artifacts': [{'label': 'Functional Spec', 'path': 'SPEC.md', 'line': 8, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/git_operations/unit/SPEC.md'}], 'issues': []}, {'file': 'tests/unit/ide/AGENTS.md', 'parent': {'label': 'Ide', 'path': '../AGENTS.md', 'line': 4, 'is_generic': False}, 'children': [], 'navigation_links': [{'label': 'Human Documentation', 'text': 'README.md', 'path': 'README.md', 'line': 28, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/ide/README.md'}, {'label': 'Functional Specification', 'text': 'SPEC.md', 'path': 'SPEC.md', 'line': 29, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/ide/SPEC.md'}, {'label': '📁 Parent Directory', 'text': 'unit', 'path': '../README.md', 'line': 30, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/README.md'}, {'label': '🏠 Project Root', 'text': 'README', 'path': '../../../../../README.md', 'line': 31, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/README.md'}], 'key_artifacts': [{'label': 'Functional Spec', 'path': 'SPEC.md', 'line': 8, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/ide/SPEC.md'}], 'issues': []}, {'file': 'tests/unit/llm/AGENTS.md', 'parent': {'label': 'Llm', 'path': '../AGENTS.md', 'line': 4, 'is_generic': False}, 'children': [], 'navigation_links': [{'label': 'Human Documentation', 'text': 'README.md', 'path': 'README.md', 'line': 28, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/llm/README.md'}, {'label': 'Functional Specification', 'text': 'SPEC.md', 'path': 'SPEC.md', 'line': 29, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/llm/SPEC.md'}, {'label': '📁 Parent Directory', 'text': 'unit', 'path': '../README.md', 'line': 30, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/README.md'}, {'label': '🏠 Project Root', 'text': 'README', 'path': '../../../../../README.md', 'line': 31, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/README.md'}], 'key_artifacts': [{'label': 'Functional Spec', 'path': 'SPEC.md', 'line': 8, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/llm/SPEC.md'}], 'issues': []}, {'file': 'tests/unit/logging_monitoring/AGENTS.md', 'parent': {'label': 'Logging Monitoring', 'path': '../AGENTS.md', 'line': 4, 'is_generic': False}, 'children': [{'label': 'integration', 'path': 'integration/AGENTS.md', 'line': 6, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/logging_monitoring/integration/AGENTS.md'}], 'navigation_links': [{'label': 'Human Documentation', 'text': 'README.md', 'path': 'README.md', 'line': 31, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/logging_monitoring/README.md'}, {'label': 'Functional Specification', 'text': 'SPEC.md', 'path': 'SPEC.md', 'line': 32, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/logging_monitoring/SPEC.md'}, {'label': '📁 Parent Directory', 'text': 'unit', 'path': '../README.md', 'line': 33, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/README.md'}, {'label': '🏠 Project Root', 'text': 'README', 'path': '../../../../../README.md', 'line': 34, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/README.md'}], 'key_artifacts': [{'label': 'Functional Spec', 'path': 'SPEC.md', 'line': 9, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/logging_monitoring/SPEC.md'}], 'issues': []}, {'file': 'tests/unit/logging_monitoring/integration/AGENTS.md', 'parent': {'label': 'Integration', 'path': '../AGENTS.md', 'line': 4, 'is_generic': False}, 'children': [], 'navigation_links': [{'label': 'Human Documentation', 'text': 'README.md', 'path': 'README.md', 'line': 27, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/logging_monitoring/integration/README.md'}, {'label': 'Functional Specification', 'text': 'SPEC.md', 'path': 'SPEC.md', 'line': 28, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/logging_monitoring/integration/SPEC.md'}, {'label': '📁 Parent Directory', 'text': 'logging_monitoring', 'path': '../README.md', 'line': 29, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/logging_monitoring/README.md'}, {'label': '🏠 Project Root', 'text': 'README', 'path': '../../../../../../README.md', 'line': 30, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/README.md'}], 'key_artifacts': [{'label': 'Functional Spec', 'path': 'SPEC.md', 'line': 8, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/logging_monitoring/integration/SPEC.md'}], 'issues': []}, {'file': 'tests/unit/logging_monitoring/unit/AGENTS.md', 'parent': {'label': 'Unit', 'path': '../AGENTS.md', 'line': 4, 'is_generic': False}, 'children': [], 'navigation_links': [{'label': 'Human Documentation', 'text': 'README.md', 'path': 'README.md', 'line': 27, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/logging_monitoring/unit/README.md'}, {'label': 'Functional Specification', 'text': 'SPEC.md', 'path': 'SPEC.md', 'line': 28, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/logging_monitoring/unit/SPEC.md'}, {'label': '📁 Parent Directory', 'text': 'logging_monitoring', 'path': '../README.md', 'line': 29, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/logging_monitoring/README.md'}, {'label': '🏠 Project Root', 'text': 'README', 'path': '../../../../../../README.md', 'line': 30, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/README.md'}], 'key_artifacts': [{'label': 'Functional Spec', 'path': 'SPEC.md', 'line': 8, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/logging_monitoring/unit/SPEC.md'}], 'issues': []}, {'file': 'tests/unit/logistics/AGENTS.md', 'parent': {'label': 'Logistics', 'path': '../AGENTS.md', 'line': 4, 'is_generic': False}, 'children': [{'label': 'orchestration', 'path': 'orchestration/AGENTS.md', 'line': 6, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/logistics/orchestration/AGENTS.md'}], 'navigation_links': [{'label': 'Human Documentation', 'text': 'README.md', 'path': 'README.md', 'line': 29, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/logistics/README.md'}, {'label': 'Functional Specification', 'text': 'SPEC.md', 'path': 'SPEC.md', 'line': 30, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/logistics/SPEC.md'}, {'label': '📁 Parent Directory', 'text': 'unit', 'path': '../README.md', 'line': 31, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/README.md'}, {'label': '🏠 Project Root', 'text': 'README', 'path': '../../../../../README.md', 'line': 32, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/README.md'}], 'key_artifacts': [{'label': 'Functional Spec', 'path': 'SPEC.md', 'line': 9, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/logistics/SPEC.md'}], 'issues': []}, {'file': 'tests/unit/logistics/orchestration/AGENTS.md', 'parent': {'label': 'Orchestration', 'path': '../AGENTS.md', 'line': 4, 'is_generic': False}, 'children': [{'label': 'project', 'path': 'project/AGENTS.md', 'line': 6, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/logistics/orchestration/project/AGENTS.md'}], 'navigation_links': [{'label': 'Human Documentation', 'text': 'README.md', 'path': 'README.md', 'line': 29, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/logistics/orchestration/README.md'}, {'label': 'Functional Specification', 'text': 'SPEC.md', 'path': 'SPEC.md', 'line': 30, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/logistics/orchestration/SPEC.md'}, {'label': '📁 Parent Directory', 'text': 'logistics', 'path': '../README.md', 'line': 31, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/logistics/README.md'}, {'label': '🏠 Project Root', 'text': 'README', 'path': '../../../../../../README.md', 'line': 32, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/README.md'}], 'key_artifacts': [{'label': 'Functional Spec', 'path': 'SPEC.md', 'line': 8, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/logistics/orchestration/SPEC.md'}], 'issues': []}, {'file': 'tests/unit/logistics/orchestration/project/AGENTS.md', 'parent': {'label': 'Project', 'path': '../AGENTS.md', 'line': 4, 'is_generic': False}, 'children': [], 'navigation_links': [{'label': 'Human Documentation', 'text': 'README.md', 'path': 'README.md', 'line': 27, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/logistics/orchestration/project/README.md'}, {'label': 'Functional Specification', 'text': 'SPEC.md', 'path': 'SPEC.md', 'line': 28, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/logistics/orchestration/project/SPEC.md'}, {'label': '📁 Parent Directory', 'text': 'orchestration', 'path': '../README.md', 'line': 29, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/logistics/orchestration/README.md'}, {'label': '🏠 Project Root', 'text': 'README', 'path': '../../../../../../../README.md', 'line': 30, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/README.md'}], 'key_artifacts': [{'label': 'Functional Spec', 'path': 'SPEC.md', 'line': 8, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/logistics/orchestration/project/SPEC.md'}], 'issues': []}, {'file': 'tests/unit/logistics/task/AGENTS.md', 'parent': {'label': 'Task', 'path': '../AGENTS.md', 'line': 4, 'is_generic': False}, 'children': [], 'navigation_links': [{'label': 'Human Documentation', 'text': 'README.md', 'path': 'README.md', 'line': 28, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/logistics/task/README.md'}, {'label': 'Functional Specification', 'text': 'SPEC.md', 'path': 'SPEC.md', 'line': 29, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/logistics/task/SPEC.md'}, {'label': '📁 Parent Directory', 'text': 'logistics', 'path': '../README.md', 'line': 30, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/logistics/README.md'}, {'label': '🏠 Project Root', 'text': 'README', 'path': '../../../../../../README.md', 'line': 31, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/README.md'}], 'key_artifacts': [{'label': 'Functional Spec', 'path': 'SPEC.md', 'line': 8, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/logistics/task/SPEC.md'}], 'issues': []}, {'file': 'tests/unit/metrics/AGENTS.md', 'parent': {'label': 'Metrics', 'path': '../AGENTS.md', 'line': 4, 'is_generic': False}, 'children': [], 'navigation_links': [{'label': 'Human Documentation', 'text': 'README.md', 'path': 'README.md', 'line': 28, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/metrics/README.md'}, {'label': 'Functional Specification', 'text': 'SPEC.md', 'path': 'SPEC.md', 'line': 29, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/metrics/SPEC.md'}, {'label': '📁 Parent Directory', 'text': 'unit', 'path': '../README.md', 'line': 30, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/README.md'}, {'label': '🏠 Project Root', 'text': 'README', 'path': '../../../../../README.md', 'line': 31, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/README.md'}], 'key_artifacts': [{'label': 'Functional Spec', 'path': 'SPEC.md', 'line': 8, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/metrics/SPEC.md'}], 'issues': []}, {'file': 'tests/unit/model_context_protocol/AGENTS.md', 'parent': {'label': 'Model Context Protocol', 'path': '../AGENTS.md', 'line': 4, 'is_generic': False}, 'children': [{'label': 'integration', 'path': 'integration/AGENTS.md', 'line': 6, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/model_context_protocol/integration/AGENTS.md'}], 'navigation_links': [{'label': 'Human Documentation', 'text': 'README.md', 'path': 'README.md', 'line': 31, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/model_context_protocol/README.md'}, {'label': 'Functional Specification', 'text': 'SPEC.md', 'path': 'SPEC.md', 'line': 32, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/model_context_protocol/SPEC.md'}, {'label': '📁 Parent Directory', 'text': 'unit', 'path': '../README.md', 'line': 33, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/README.md'}, {'label': '🏠 Project Root', 'text': 'README', 'path': '../../../../../README.md', 'line': 34, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/README.md'}], 'key_artifacts': [{'label': 'Functional Spec', 'path': 'SPEC.md', 'line': 9, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/model_context_protocol/SPEC.md'}], 'issues': []}, {'file': 'tests/unit/model_context_protocol/integration/AGENTS.md', 'parent': {'label': 'Integration', 'path': '../AGENTS.md', 'line': 4, 'is_generic': False}, 'children': [], 'navigation_links': [{'label': 'Human Documentation', 'text': 'README.md', 'path': 'README.md', 'line': 27, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/model_context_protocol/integration/README.md'}, {'label': 'Functional Specification', 'text': 'SPEC.md', 'path': 'SPEC.md', 'line': 28, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/model_context_protocol/integration/SPEC.md'}, {'label': '📁 Parent Directory', 'text': 'model_context_protocol', 'path': '../README.md', 'line': 29, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/model_context_protocol/README.md'}, {'label': '🏠 Project Root', 'text': 'README', 'path': '../../../../../../README.md', 'line': 30, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/README.md'}], 'key_artifacts': [{'label': 'Functional Spec', 'path': 'SPEC.md', 'line': 8, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/model_context_protocol/integration/SPEC.md'}], 'issues': []}, {'file': 'tests/unit/model_context_protocol/unit/AGENTS.md', 'parent': {'label': 'Unit', 'path': '../AGENTS.md', 'line': 4, 'is_generic': False}, 'children': [], 'navigation_links': [{'label': 'Human Documentation', 'text': 'README.md', 'path': 'README.md', 'line': 27, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/model_context_protocol/unit/README.md'}, {'label': 'Functional Specification', 'text': 'SPEC.md', 'path': 'SPEC.md', 'line': 28, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/model_context_protocol/unit/SPEC.md'}, {'label': '📁 Parent Directory', 'text': 'model_context_protocol', 'path': '../README.md', 'line': 29, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/model_context_protocol/README.md'}, {'label': '🏠 Project Root', 'text': 'README', 'path': '../../../../../../README.md', 'line': 30, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/README.md'}], 'key_artifacts': [{'label': 'Functional Spec', 'path': 'SPEC.md', 'line': 8, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/model_context_protocol/unit/SPEC.md'}], 'issues': []}, {'file': 'tests/unit/module_template/AGENTS.md', 'parent': {'label': 'Module Template', 'path': '../AGENTS.md', 'line': 4, 'is_generic': False}, 'children': [{'label': 'integration', 'path': 'integration/AGENTS.md', 'line': 6, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/module_template/integration/AGENTS.md'}], 'navigation_links': [{'label': 'Human Documentation', 'text': 'README.md', 'path': 'README.md', 'line': 31, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/module_template/README.md'}, {'label': 'Functional Specification', 'text': 'SPEC.md', 'path': 'SPEC.md', 'line': 32, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/module_template/SPEC.md'}, {'label': '📁 Parent Directory', 'text': 'unit', 'path': '../README.md', 'line': 33, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/README.md'}, {'label': '🏠 Project Root', 'text': 'README', 'path': '../../../../../README.md', 'line': 34, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/README.md'}], 'key_artifacts': [{'label': 'Functional Spec', 'path': 'SPEC.md', 'line': 9, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/module_template/SPEC.md'}], 'issues': []}, {'file': 'tests/unit/module_template/integration/AGENTS.md', 'parent': {'label': 'Integration', 'path': '../AGENTS.md', 'line': 4, 'is_generic': False}, 'children': [], 'navigation_links': [{'label': 'Human Documentation', 'text': 'README.md', 'path': 'README.md', 'line': 27, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/module_template/integration/README.md'}, {'label': 'Functional Specification', 'text': 'SPEC.md', 'path': 'SPEC.md', 'line': 28, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/module_template/integration/SPEC.md'}, {'label': '📁 Parent Directory', 'text': 'module_template', 'path': '../README.md', 'line': 29, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/module_template/README.md'}, {'label': '🏠 Project Root', 'text': 'README', 'path': '../../../../../../README.md', 'line': 30, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/README.md'}], 'key_artifacts': [{'label': 'Functional Spec', 'path': 'SPEC.md', 'line': 8, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/module_template/integration/SPEC.md'}], 'issues': []}, {'file': 'tests/unit/module_template/unit/AGENTS.md', 'parent': {'label': 'Unit', 'path': '../AGENTS.md', 'line': 4, 'is_generic': False}, 'children': [], 'navigation_links': [{'label': 'Human Documentation', 'text': 'README.md', 'path': 'README.md', 'line': 27, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/module_template/unit/README.md'}, {'label': 'Functional Specification', 'text': 'SPEC.md', 'path': 'SPEC.md', 'line': 28, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/module_template/unit/SPEC.md'}, {'label': '📁 Parent Directory', 'text': 'module_template', 'path': '../README.md', 'line': 29, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/module_template/README.md'}, {'label': '🏠 Project Root', 'text': 'README', 'path': '../../../../../../README.md', 'line': 30, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/README.md'}], 'key_artifacts': [{'label': 'Functional Spec', 'path': 'SPEC.md', 'line': 8, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/module_template/unit/SPEC.md'}], 'issues': []}, {'file': 'tests/unit/networking/AGENTS.md', 'parent': {'label': 'Networking', 'path': '../AGENTS.md', 'line': 4, 'is_generic': False}, 'children': [], 'navigation_links': [{'label': 'Human Documentation', 'text': 'README.md', 'path': 'README.md', 'line': 28, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/networking/README.md'}, {'label': 'Functional Specification', 'text': 'SPEC.md', 'path': 'SPEC.md', 'line': 29, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/networking/SPEC.md'}, {'label': '📁 Parent Directory', 'text': 'unit', 'path': '../README.md', 'line': 30, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/README.md'}, {'label': '🏠 Project Root', 'text': 'README', 'path': '../../../../../README.md', 'line': 31, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/README.md'}], 'key_artifacts': [{'label': 'Functional Spec', 'path': 'SPEC.md', 'line': 8, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/networking/SPEC.md'}], 'issues': []}, {'file': 'tests/unit/pattern_matching/AGENTS.md', 'parent': {'label': 'Pattern Matching', 'path': '../AGENTS.md', 'line': 4, 'is_generic': False}, 'children': [{'label': 'integration', 'path': 'integration/AGENTS.md', 'line': 6, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/pattern_matching/integration/AGENTS.md'}], 'navigation_links': [{'label': 'Human Documentation', 'text': 'README.md', 'path': 'README.md', 'line': 31, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/pattern_matching/README.md'}, {'label': 'Functional Specification', 'text': 'SPEC.md', 'path': 'SPEC.md', 'line': 32, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/pattern_matching/SPEC.md'}, {'label': '📁 Parent Directory', 'text': 'unit', 'path': '../README.md', 'line': 33, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/README.md'}, {'label': '🏠 Project Root', 'text': 'README', 'path': '../../../../../README.md', 'line': 34, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/README.md'}], 'key_artifacts': [{'label': 'Functional Spec', 'path': 'SPEC.md', 'line': 9, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/pattern_matching/SPEC.md'}], 'issues': []}, {'file': 'tests/unit/pattern_matching/integration/AGENTS.md', 'parent': {'label': 'Integration', 'path': '../AGENTS.md', 'line': 4, 'is_generic': False}, 'children': [], 'navigation_links': [{'label': 'Human Documentation', 'text': 'README.md', 'path': 'README.md', 'line': 27, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/pattern_matching/integration/README.md'}, {'label': 'Functional Specification', 'text': 'SPEC.md', 'path': 'SPEC.md', 'line': 28, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/pattern_matching/integration/SPEC.md'}, {'label': '📁 Parent Directory', 'text': 'pattern_matching', 'path': '../README.md', 'line': 29, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/pattern_matching/README.md'}, {'label': '🏠 Project Root', 'text': 'README', 'path': '../../../../../../README.md', 'line': 30, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/README.md'}], 'key_artifacts': [{'label': 'Functional Spec', 'path': 'SPEC.md', 'line': 8, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/pattern_matching/integration/SPEC.md'}], 'issues': []}, {'file': 'tests/unit/pattern_matching/unit/AGENTS.md', 'parent': {'label': 'Unit', 'path': '../AGENTS.md', 'line': 4, 'is_generic': False}, 'children': [], 'navigation_links': [{'label': 'Human Documentation', 'text': 'README.md', 'path': 'README.md', 'line': 27, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/pattern_matching/unit/README.md'}, {'label': 'Functional Specification', 'text': 'SPEC.md', 'path': 'SPEC.md', 'line': 28, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/pattern_matching/unit/SPEC.md'}, {'label': '📁 Parent Directory', 'text': 'pattern_matching', 'path': '../README.md', 'line': 29, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/pattern_matching/README.md'}, {'label': '🏠 Project Root', 'text': 'README', 'path': '../../../../../../README.md', 'line': 30, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/README.md'}], 'key_artifacts': [{'label': 'Functional Spec', 'path': 'SPEC.md', 'line': 8, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/pattern_matching/unit/SPEC.md'}], 'issues': []}, {'file': 'tests/unit/performance/AGENTS.md', 'parent': {'label': 'Performance', 'path': '../AGENTS.md', 'line': 4, 'is_generic': False}, 'children': [], 'navigation_links': [{'label': 'Human Documentation', 'text': 'README.md', 'path': 'README.md', 'line': 29, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/performance/README.md'}, {'label': 'Functional Specification', 'text': 'SPEC.md', 'path': 'SPEC.md', 'line': 30, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/performance/SPEC.md'}, {'label': '📁 Parent Directory', 'text': 'unit', 'path': '../README.md', 'line': 31, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/README.md'}, {'label': '🏠 Project Root', 'text': 'README', 'path': '../../../../../README.md', 'line': 32, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/README.md'}], 'key_artifacts': [{'label': 'Functional Spec', 'path': 'SPEC.md', 'line': 8, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/performance/SPEC.md'}], 'issues': []}, {'file': 'tests/unit/physical_management/AGENTS.md', 'parent': {'label': 'Physical Management', 'path': '../AGENTS.md', 'line': 4, 'is_generic': False}, 'children': [], 'navigation_links': [{'label': 'Human Documentation', 'text': 'README.md', 'path': 'README.md', 'line': 28, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/physical_management/README.md'}, {'label': 'Functional Specification', 'text': 'SPEC.md', 'path': 'SPEC.md', 'line': 29, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/physical_management/SPEC.md'}, {'label': '📁 Parent Directory', 'text': 'unit', 'path': '../README.md', 'line': 30, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/README.md'}, {'label': '🏠 Project Root', 'text': 'README', 'path': '../../../../../README.md', 'line': 31, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/README.md'}], 'key_artifacts': [{'label': 'Functional Spec', 'path': 'SPEC.md', 'line': 8, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/physical_management/SPEC.md'}], 'issues': []}, {'file': 'tests/unit/plugin_system/AGENTS.md', 'parent': {'label': 'Plugin System', 'path': '../AGENTS.md', 'line': 4, 'is_generic': False}, 'children': [], 'navigation_links': [{'label': 'Human Documentation', 'text': 'README.md', 'path': 'README.md', 'line': 28, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/plugin_system/README.md'}, {'label': 'Functional Specification', 'text': 'SPEC.md', 'path': 'SPEC.md', 'line': 29, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/plugin_system/SPEC.md'}, {'label': '📁 Parent Directory', 'text': 'unit', 'path': '../README.md', 'line': 30, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/README.md'}, {'label': '🏠 Project Root', 'text': 'README', 'path': '../../../../../README.md', 'line': 31, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/README.md'}], 'key_artifacts': [{'label': 'Functional Spec', 'path': 'SPEC.md', 'line': 8, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/plugin_system/SPEC.md'}], 'issues': []}, {'file': 'tests/unit/scrape/AGENTS.md', 'parent': {'label': 'Scrape', 'path': '../AGENTS.md', 'line': 4, 'is_generic': False}, 'children': [{'label': 'integration', 'path': 'integration/AGENTS.md', 'line': 6, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/scrape/integration/AGENTS.md'}], 'navigation_links': [{'label': 'Human Documentation', 'text': 'README.md', 'path': 'README.md', 'line': 32, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/scrape/README.md'}, {'label': 'Functional Specification', 'text': 'SPEC.md', 'path': 'SPEC.md', 'line': 33, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/scrape/SPEC.md'}, {'label': '📁 Parent Directory', 'text': 'unit', 'path': '../README.md', 'line': 34, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/README.md'}, {'label': '🏠 Project Root', 'text': 'README', 'path': '../../../../../README.md', 'line': 35, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/README.md'}], 'key_artifacts': [{'label': 'Functional Spec', 'path': 'SPEC.md', 'line': 9, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/scrape/SPEC.md'}], 'issues': []}, {'file': 'tests/unit/scrape/integration/AGENTS.md', 'parent': {'label': 'Integration', 'path': '../AGENTS.md', 'line': 4, 'is_generic': False}, 'children': [], 'navigation_links': [{'label': 'Human Documentation', 'text': 'README.md', 'path': 'README.md', 'line': 29, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/scrape/integration/README.md'}, {'label': 'Functional Specification', 'text': 'SPEC.md', 'path': 'SPEC.md', 'line': 30, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/scrape/integration/SPEC.md'}, {'label': '📁 Parent Directory', 'text': 'scrape', 'path': '../README.md', 'line': 31, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/scrape/README.md'}, {'label': '🏠 Project Root', 'text': 'README', 'path': '../../../../../../README.md', 'line': 32, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/README.md'}], 'key_artifacts': [{'label': 'Functional Spec', 'path': 'SPEC.md', 'line': 8, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/scrape/integration/SPEC.md'}], 'issues': []}, {'file': 'tests/unit/scrape/unit/AGENTS.md', 'parent': {'label': 'Unit', 'path': '../AGENTS.md', 'line': 4, 'is_generic': False}, 'children': [], 'navigation_links': [{'label': 'Human Documentation', 'text': 'README.md', 'path': 'README.md', 'line': 32, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/scrape/unit/README.md'}, {'label': 'Functional Specification', 'text': 'SPEC.md', 'path': 'SPEC.md', 'line': 33, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/scrape/unit/SPEC.md'}, {'label': '📁 Parent Directory', 'text': 'scrape', 'path': '../README.md', 'line': 34, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/scrape/README.md'}, {'label': '🏠 Project Root', 'text': 'README', 'path': '../../../../../../README.md', 'line': 35, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/README.md'}], 'key_artifacts': [{'label': 'Functional Spec', 'path': 'SPEC.md', 'line': 8, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/scrape/unit/SPEC.md'}], 'issues': []}, {'file': 'tests/unit/security/AGENTS.md', 'parent': {'label': 'Security', 'path': '../AGENTS.md', 'line': 4, 'is_generic': False}, 'children': [{'label': 'integration', 'path': 'integration/AGENTS.md', 'line': 6, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/security/integration/AGENTS.md'}], 'navigation_links': [{'label': 'Human Documentation', 'text': 'README.md', 'path': 'README.md', 'line': 36, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/security/README.md'}, {'label': 'Functional Specification', 'text': 'SPEC.md', 'path': 'SPEC.md', 'line': 37, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/security/SPEC.md'}, {'label': '📁 Parent Directory', 'text': 'unit', 'path': '../README.md', 'line': 38, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/README.md'}, {'label': '🏠 Project Root', 'text': 'README', 'path': '../../../../../README.md', 'line': 39, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/README.md'}], 'key_artifacts': [{'label': 'Functional Spec', 'path': 'SPEC.md', 'line': 9, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/security/SPEC.md'}], 'issues': []}, {'file': 'tests/unit/security/integration/AGENTS.md', 'parent': {'label': 'Integration', 'path': '../AGENTS.md', 'line': 4, 'is_generic': False}, 'children': [], 'navigation_links': [{'label': 'Human Documentation', 'text': 'README.md', 'path': 'README.md', 'line': 26, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/security/integration/README.md'}, {'label': 'Functional Specification', 'text': 'SPEC.md', 'path': 'SPEC.md', 'line': 27, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/security/integration/SPEC.md'}, {'label': '📁 Parent Directory', 'text': 'security', 'path': '../README.md', 'line': 28, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/security/README.md'}, {'label': '🏠 Project Root', 'text': 'README', 'path': '../../../../../../README.md', 'line': 29, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/README.md'}], 'key_artifacts': [{'label': 'Functional Spec', 'path': 'SPEC.md', 'line': 8, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/security/integration/SPEC.md'}], 'issues': []}, {'file': 'tests/unit/security/unit/AGENTS.md', 'parent': {'label': 'Unit', 'path': '../AGENTS.md', 'line': 4, 'is_generic': False}, 'children': [], 'navigation_links': [{'label': 'Human Documentation', 'text': 'README.md', 'path': 'README.md', 'line': 26, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/security/unit/README.md'}, {'label': 'Functional Specification', 'text': 'SPEC.md', 'path': 'SPEC.md', 'line': 27, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/security/unit/SPEC.md'}, {'label': '📁 Parent Directory', 'text': 'security', 'path': '../README.md', 'line': 28, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/security/README.md'}, {'label': '🏠 Project Root', 'text': 'README', 'path': '../../../../../../README.md', 'line': 29, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/README.md'}], 'key_artifacts': [{'label': 'Functional Spec', 'path': 'SPEC.md', 'line': 8, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/security/unit/SPEC.md'}], 'issues': []}, {'file': 'tests/unit/serialization/AGENTS.md', 'parent': {'label': 'Serialization', 'path': '../AGENTS.md', 'line': 4, 'is_generic': False}, 'children': [], 'navigation_links': [{'label': 'Human Documentation', 'text': 'README.md', 'path': 'README.md', 'line': 28, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/serialization/README.md'}, {'label': 'Functional Specification', 'text': 'SPEC.md', 'path': 'SPEC.md', 'line': 29, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/serialization/SPEC.md'}, {'label': '📁 Parent Directory', 'text': 'unit', 'path': '../README.md', 'line': 30, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/README.md'}, {'label': '🏠 Project Root', 'text': 'README', 'path': '../../../../../README.md', 'line': 31, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/README.md'}], 'key_artifacts': [{'label': 'Functional Spec', 'path': 'SPEC.md', 'line': 8, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/serialization/SPEC.md'}], 'issues': []}, {'file': 'tests/unit/skills/AGENTS.md', 'parent': {'label': 'Skills', 'path': '../AGENTS.md', 'line': 4, 'is_generic': False}, 'children': [], 'navigation_links': [{'label': 'Human Documentation', 'text': 'README.md', 'path': 'README.md', 'line': 31, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/skills/README.md'}, {'label': 'Functional Specification', 'text': 'SPEC.md', 'path': 'SPEC.md', 'line': 32, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/skills/SPEC.md'}, {'label': '📁 Parent Directory', 'text': 'unit', 'path': '../README.md', 'line': 33, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/README.md'}, {'label': '🏠 Project Root', 'text': 'README', 'path': '../../../../../README.md', 'line': 34, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/README.md'}], 'key_artifacts': [{'label': 'Functional Spec', 'path': 'SPEC.md', 'line': 8, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/skills/SPEC.md'}], 'issues': []}, {'file': 'tests/unit/spatial/AGENTS.md', 'parent': {'label': 'Spatial', 'path': '../AGENTS.md', 'line': 4, 'is_generic': False}, 'children': [{'label': 'three_d', 'path': 'three_d/AGENTS.md', 'line': 6, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/spatial/three_d/AGENTS.md'}], 'navigation_links': [{'label': 'Human Documentation', 'text': 'README.md', 'path': 'README.md', 'line': 27, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/spatial/README.md'}, {'label': 'Functional Specification', 'text': 'SPEC.md', 'path': 'SPEC.md', 'line': 28, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/spatial/SPEC.md'}, {'label': '📁 Parent Directory', 'text': 'unit', 'path': '../README.md', 'line': 29, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/README.md'}, {'label': '🏠 Project Root', 'text': 'README', 'path': '../../../../../README.md', 'line': 30, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/README.md'}], 'key_artifacts': [{'label': 'Functional Spec', 'path': 'SPEC.md', 'line': 8, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/spatial/SPEC.md'}], 'issues': []}, {'file': 'tests/unit/spatial/three_d/AGENTS.md', 'parent': {'label': 'Three D', 'path': '../AGENTS.md', 'line': 4, 'is_generic': False}, 'children': [], 'navigation_links': [{'label': 'Human Documentation', 'text': 'README.md', 'path': 'README.md', 'line': 28, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/spatial/three_d/README.md'}, {'label': 'Functional Specification', 'text': 'SPEC.md', 'path': 'SPEC.md', 'line': 29, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/spatial/three_d/SPEC.md'}, {'label': '📁 Parent Directory', 'text': 'spatial', 'path': '../README.md', 'line': 30, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/spatial/README.md'}, {'label': '🏠 Project Root', 'text': 'README', 'path': '../../../../../../README.md', 'line': 31, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/README.md'}], 'key_artifacts': [{'label': 'Functional Spec', 'path': 'SPEC.md', 'line': 8, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/spatial/three_d/SPEC.md'}], 'issues': []}, {'file': 'tests/unit/static_analysis/AGENTS.md', 'parent': {'label': 'Static Analysis', 'path': '../AGENTS.md', 'line': 4, 'is_generic': False}, 'children': [{'label': 'integration', 'path': 'integration/AGENTS.md', 'line': 6, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/static_analysis/integration/AGENTS.md'}], 'navigation_links': [{'label': 'Human Documentation', 'text': 'README.md', 'path': 'README.md', 'line': 32, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/static_analysis/README.md'}, {'label': 'Functional Specification', 'text': 'SPEC.md', 'path': 'SPEC.md', 'line': 33, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/static_analysis/SPEC.md'}, {'label': '📁 Parent Directory', 'text': 'unit', 'path': '../README.md', 'line': 34, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/README.md'}, {'label': '🏠 Project Root', 'text': 'README', 'path': '../../../../../README.md', 'line': 35, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/README.md'}], 'key_artifacts': [{'label': 'Functional Spec', 'path': 'SPEC.md', 'line': 9, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/static_analysis/SPEC.md'}], 'issues': []}, {'file': 'tests/unit/static_analysis/integration/AGENTS.md', 'parent': {'label': 'Integration', 'path': '../AGENTS.md', 'line': 4, 'is_generic': False}, 'children': [], 'navigation_links': [{'label': 'Human Documentation', 'text': 'README.md', 'path': 'README.md', 'line': 27, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/static_analysis/integration/README.md'}, {'label': 'Functional Specification', 'text': 'SPEC.md', 'path': 'SPEC.md', 'line': 28, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/static_analysis/integration/SPEC.md'}, {'label': '📁 Parent Directory', 'text': 'static_analysis', 'path': '../README.md', 'line': 29, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/static_analysis/README.md'}, {'label': '🏠 Project Root', 'text': 'README', 'path': '../../../../../../README.md', 'line': 30, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/README.md'}], 'key_artifacts': [{'label': 'Functional Spec', 'path': 'SPEC.md', 'line': 8, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/static_analysis/integration/SPEC.md'}], 'issues': []}, {'file': 'tests/unit/static_analysis/unit/AGENTS.md', 'parent': {'label': 'Unit', 'path': '../AGENTS.md', 'line': 4, 'is_generic': False}, 'children': [], 'navigation_links': [{'label': 'Human Documentation', 'text': 'README.md', 'path': 'README.md', 'line': 27, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/static_analysis/unit/README.md'}, {'label': 'Functional Specification', 'text': 'SPEC.md', 'path': 'SPEC.md', 'line': 28, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/static_analysis/unit/SPEC.md'}, {'label': '📁 Parent Directory', 'text': 'static_analysis', 'path': '../README.md', 'line': 29, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/static_analysis/README.md'}, {'label': '🏠 Project Root', 'text': 'README', 'path': '../../../../../../README.md', 'line': 30, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/README.md'}], 'key_artifacts': [{'label': 'Functional Spec', 'path': 'SPEC.md', 'line': 8, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/static_analysis/unit/SPEC.md'}], 'issues': []}, {'file': 'tests/unit/system_discovery/AGENTS.md', 'parent': {'label': 'System Discovery', 'path': '../AGENTS.md', 'line': 4, 'is_generic': False}, 'children': [], 'navigation_links': [{'label': 'Human Documentation', 'text': 'README.md', 'path': 'README.md', 'line': 29, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/system_discovery/README.md'}, {'label': 'Functional Specification', 'text': 'SPEC.md', 'path': 'SPEC.md', 'line': 30, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/system_discovery/SPEC.md'}, {'label': '📁 Parent Directory', 'text': 'unit', 'path': '../README.md', 'line': 31, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/README.md'}, {'label': '🏠 Project Root', 'text': 'README', 'path': '../../../../../README.md', 'line': 32, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/README.md'}], 'key_artifacts': [{'label': 'Functional Spec', 'path': 'SPEC.md', 'line': 8, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/system_discovery/SPEC.md'}], 'issues': []}, {'file': 'tests/unit/template/AGENTS.md', 'parent': {'label': 'Template', 'path': '../AGENTS.md', 'line': 4, 'is_generic': False}, 'children': [], 'navigation_links': [{'label': 'Human Documentation', 'text': 'README.md', 'path': 'README.md', 'line': 28, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/template/README.md'}, {'label': 'Functional Specification', 'text': 'SPEC.md', 'path': 'SPEC.md', 'line': 29, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/template/SPEC.md'}, {'label': '📁 Parent Directory', 'text': 'unit', 'path': '../README.md', 'line': 30, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/README.md'}, {'label': '🏠 Project Root', 'text': 'README', 'path': '../../../../../README.md', 'line': 31, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/README.md'}], 'key_artifacts': [{'label': 'Functional Spec', 'path': 'SPEC.md', 'line': 8, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/template/SPEC.md'}], 'issues': []}, {'file': 'tests/unit/terminal_interface/AGENTS.md', 'parent': {'label': 'Terminal Interface', 'path': '../AGENTS.md', 'line': 4, 'is_generic': False}, 'children': [], 'navigation_links': [{'label': 'Human Documentation', 'text': 'README.md', 'path': 'README.md', 'line': 29, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/terminal_interface/README.md'}, {'label': 'Functional Specification', 'text': 'SPEC.md', 'path': 'SPEC.md', 'line': 30, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/terminal_interface/SPEC.md'}, {'label': '📁 Parent Directory', 'text': 'unit', 'path': '../README.md', 'line': 31, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/README.md'}, {'label': '🏠 Project Root', 'text': 'README', 'path': '../../../../../README.md', 'line': 32, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/README.md'}], 'key_artifacts': [{'label': 'Functional Spec', 'path': 'SPEC.md', 'line': 8, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/terminal_interface/SPEC.md'}], 'issues': []}, {'file': 'tests/unit/tools/AGENTS.md', 'parent': {'label': 'Tools', 'path': '../AGENTS.md', 'line': 4, 'is_generic': False}, 'children': [], 'navigation_links': [{'label': 'Human Documentation', 'text': 'README.md', 'path': 'README.md', 'line': 28, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/tools/README.md'}, {'label': 'Functional Specification', 'text': 'SPEC.md', 'path': 'SPEC.md', 'line': 29, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/tools/SPEC.md'}, {'label': '📁 Parent Directory', 'text': 'unit', 'path': '../README.md', 'line': 30, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/README.md'}, {'label': '🏠 Project Root', 'text': 'README', 'path': '../../../../../README.md', 'line': 31, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/README.md'}], 'key_artifacts': [{'label': 'Functional Spec', 'path': 'SPEC.md', 'line': 8, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/tools/SPEC.md'}], 'issues': []}, {'file': 'tests/unit/validation/AGENTS.md', 'parent': {'label': 'Validation', 'path': '../AGENTS.md', 'line': 4, 'is_generic': False}, 'children': [], 'navigation_links': [{'label': 'Human Documentation', 'text': 'README.md', 'path': 'README.md', 'line': 28, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/validation/README.md'}, {'label': 'Functional Specification', 'text': 'SPEC.md', 'path': 'SPEC.md', 'line': 29, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/validation/SPEC.md'}, {'label': '📁 Parent Directory', 'text': 'unit', 'path': '../README.md', 'line': 30, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/README.md'}, {'label': '🏠 Project Root', 'text': 'README', 'path': '../../../../../README.md', 'line': 31, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/README.md'}], 'key_artifacts': [{'label': 'Functional Spec', 'path': 'SPEC.md', 'line': 8, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/validation/SPEC.md'}], 'issues': []}, {'file': 'tests/unit/website/AGENTS.md', 'parent': {'label': 'Website', 'path': '../AGENTS.md', 'line': 4, 'is_generic': False}, 'children': [{'label': 'integration', 'path': 'integration/AGENTS.md', 'line': 6, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/website/integration/AGENTS.md'}], 'navigation_links': [{'label': 'Human Documentation', 'text': 'README.md', 'path': 'README.md', 'line': 32, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/website/README.md'}, {'label': 'Functional Specification', 'text': 'SPEC.md', 'path': 'SPEC.md', 'line': 33, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/website/SPEC.md'}, {'label': '📁 Parent Directory', 'text': 'unit', 'path': '../README.md', 'line': 34, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/README.md'}, {'label': '🏠 Project Root', 'text': 'README', 'path': '../../../../../README.md', 'line': 35, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/README.md'}], 'key_artifacts': [{'label': 'Functional Spec', 'path': 'SPEC.md', 'line': 9, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/website/SPEC.md'}], 'issues': []}, {'file': 'tests/unit/website/integration/AGENTS.md', 'parent': {'label': 'Integration', 'path': '../AGENTS.md', 'line': 4, 'is_generic': False}, 'children': [], 'navigation_links': [{'label': 'Human Documentation', 'text': 'README.md', 'path': 'README.md', 'line': 29, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/website/integration/README.md'}, {'label': 'Functional Specification', 'text': 'SPEC.md', 'path': 'SPEC.md', 'line': 30, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/website/integration/SPEC.md'}, {'label': '📁 Parent Directory', 'text': 'website', 'path': '../README.md', 'line': 31, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/website/README.md'}, {'label': '🏠 Project Root', 'text': 'README', 'path': '../../../../../../README.md', 'line': 32, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/README.md'}], 'key_artifacts': [{'label': 'Functional Spec', 'path': 'SPEC.md', 'line': 8, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/website/integration/SPEC.md'}], 'issues': []}, {'file': 'tests/unit/website/unit/AGENTS.md', 'parent': {'label': 'Unit', 'path': '../AGENTS.md', 'line': 4, 'is_generic': False}, 'children': [], 'navigation_links': [{'label': 'Human Documentation', 'text': 'README.md', 'path': 'README.md', 'line': 31, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/website/unit/README.md'}, {'label': 'Functional Specification', 'text': 'SPEC.md', 'path': 'SPEC.md', 'line': 32, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/website/unit/SPEC.md'}, {'label': '📁 Parent Directory', 'text': 'website', 'path': '../README.md', 'line': 33, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/website/README.md'}, {'label': '🏠 Project Root', 'text': 'README', 'path': '../../../../../../README.md', 'line': 34, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/README.md'}], 'key_artifacts': [{'label': 'Functional Spec', 'path': 'SPEC.md', 'line': 8, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tests/unit/website/unit/SPEC.md'}], 'issues': []}, {'file': 'tools/AGENTS.md', 'parent': {'label': 'Repository Root', 'path': '../AGENTS.md', 'line': 4, 'is_generic': False}, 'children': [], 'navigation_links': [{'label': 'Human Documentation', 'text': 'README.md', 'path': 'README.md', 'line': 35, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tools/README.md'}, {'label': 'Functional Specification', 'text': 'SPEC.md', 'path': 'SPEC.md', 'line': 36, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tools/SPEC.md'}, {'label': '📁 Parent Directory', 'text': 'codomyrmex', 'path': '../README.md', 'line': 37, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/README.md'}, {'label': '🏠 Project Root', 'text': 'README', 'path': '../../../README.md', 'line': 38, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/README.md'}], 'key_artifacts': [{'label': 'Functional Spec', 'path': 'SPEC.md', 'line': 8, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/tools/SPEC.md'}], 'issues': []}, {'file': 'utils/AGENTS.md', 'parent': {'label': 'Repository Root', 'path': '../AGENTS.md', 'line': 4, 'is_generic': False}, 'children': [], 'navigation_links': [{'label': 'Human Documentation', 'text': 'README.md', 'path': 'README.md', 'line': 29, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/utils/README.md'}, {'label': 'Functional Specification', 'text': 'SPEC.md', 'path': 'SPEC.md', 'line': 30, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/utils/SPEC.md'}, {'label': '📁 Parent Directory', 'text': 'codomyrmex', 'path': '../README.md', 'line': 31, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/README.md'}, {'label': '🏠 Project Root', 'text': 'README', 'path': '../../../README.md', 'line': 32, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/README.md'}], 'key_artifacts': [{'label': 'Functional Spec', 'path': 'SPEC.md', 'line': 8, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/utils/SPEC.md'}], 'issues': []}, {'file': 'validation/AGENTS.md', 'parent': {'label': 'Repository Root', 'path': '../AGENTS.md', 'line': 4, 'is_generic': False}, 'children': [], 'navigation_links': [{'label': 'Human Documentation', 'text': 'README.md', 'path': 'README.md', 'line': 31, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/validation/README.md'}, {'label': 'Functional Specification', 'text': 'SPEC.md', 'path': 'SPEC.md', 'line': 32, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/validation/SPEC.md'}, {'label': '📁 Parent Directory', 'text': 'codomyrmex', 'path': '../README.md', 'line': 33, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/README.md'}, {'label': '🏠 Project Root', 'text': 'README', 'path': '../../../README.md', 'line': 34, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/README.md'}], 'key_artifacts': [{'label': 'Functional Spec', 'path': 'SPEC.md', 'line': 8, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/validation/SPEC.md'}], 'issues': []}, {'file': 'website/AGENTS.md', 'parent': {'label': 'Repository Root', 'path': '../AGENTS.md', 'line': 4, 'is_generic': False}, 'children': [{'label': 'assets', 'path': 'assets/AGENTS.md', 'line': 6, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/website/assets/AGENTS.md'}], 'navigation_links': [{'label': 'Human Documentation', 'text': 'README.md', 'path': 'README.md', 'line': 41, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/website/README.md'}, {'label': 'Functional Specification', 'text': 'SPEC.md', 'path': 'SPEC.md', 'line': 42, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/website/SPEC.md'}, {'label': '📁 Parent Directory', 'text': 'codomyrmex', 'path': '../README.md', 'line': 43, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/README.md'}, {'label': '🏠 Project Root', 'text': 'README', 'path': '../../../README.md', 'line': 44, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/README.md'}], 'key_artifacts': [{'label': 'Functional Spec', 'path': 'SPEC.md', 'line': 9, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/website/SPEC.md'}], 'issues': []}, {'file': 'website/assets/AGENTS.md', 'parent': {'label': 'Assets', 'path': '../AGENTS.md', 'line': 4, 'is_generic': False}, 'children': [{'label': 'css', 'path': 'css/AGENTS.md', 'line': 6, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/website/assets/css/AGENTS.md'}], 'navigation_links': [{'label': 'Human Documentation', 'text': 'README.md', 'path': 'README.md', 'line': 30, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/website/assets/README.md'}, {'label': 'Functional Specification', 'text': 'SPEC.md', 'path': 'SPEC.md', 'line': 31, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/website/assets/SPEC.md'}, {'label': '📁 Parent Directory', 'text': 'website', 'path': '../README.md', 'line': 32, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/website/README.md'}, {'label': '🏠 Project Root', 'text': 'README', 'path': '../../../../README.md', 'line': 33, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/README.md'}], 'key_artifacts': [{'label': 'Functional Spec', 'path': 'SPEC.md', 'line': 9, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/website/assets/SPEC.md'}], 'issues': []}, {'file': 'website/assets/css/AGENTS.md', 'parent': {'label': 'Css', 'path': '../AGENTS.md', 'line': 4, 'is_generic': False}, 'children': [], 'navigation_links': [{'label': 'Human Documentation', 'text': 'README.md', 'path': 'README.md', 'line': 27, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/website/assets/css/README.md'}, {'label': 'Functional Specification', 'text': 'SPEC.md', 'path': 'SPEC.md', 'line': 28, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/website/assets/css/SPEC.md'}, {'label': '📁 Parent Directory', 'text': 'assets', 'path': '../README.md', 'line': 29, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/website/assets/README.md'}, {'label': '🏠 Project Root', 'text': 'README', 'path': '../../../../../README.md', 'line': 30, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/README.md'}], 'key_artifacts': [{'label': 'Functional Spec', 'path': 'SPEC.md', 'line': 8, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/website/assets/css/SPEC.md'}], 'issues': []}, {'file': 'website/assets/js/AGENTS.md', 'parent': {'label': 'Js', 'path': '../AGENTS.md', 'line': 4, 'is_generic': False}, 'children': [], 'navigation_links': [{'label': 'Human Documentation', 'text': 'README.md', 'path': 'README.md', 'line': 27, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/website/assets/js/README.md'}, {'label': 'Functional Specification', 'text': 'SPEC.md', 'path': 'SPEC.md', 'line': 28, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/website/assets/js/SPEC.md'}, {'label': '📁 Parent Directory', 'text': 'assets', 'path': '../README.md', 'line': 29, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/website/assets/README.md'}, {'label': '🏠 Project Root', 'text': 'README', 'path': '../../../../../README.md', 'line': 30, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/README.md'}], 'key_artifacts': [{'label': 'Functional Spec', 'path': 'SPEC.md', 'line': 8, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/website/assets/js/SPEC.md'}], 'issues': []}, {'file': 'website/templates/AGENTS.md', 'parent': {'label': 'Templates', 'path': '../AGENTS.md', 'line': 4, 'is_generic': False}, 'children': [], 'navigation_links': [{'label': 'Human Documentation', 'text': 'README.md', 'path': 'README.md', 'line': 35, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/website/templates/README.md'}, {'label': 'Functional Specification', 'text': 'SPEC.md', 'path': 'SPEC.md', 'line': 36, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/website/templates/SPEC.md'}, {'label': '📁 Parent Directory', 'text': 'website', 'path': '../README.md', 'line': 37, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/website/README.md'}, {'label': '🏠 Project Root', 'text': 'README', 'path': '../../../../README.md', 'line': 38, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/README.md'}], 'key_artifacts': [{'label': 'Functional Spec', 'path': 'SPEC.md', 'line': 8, 'exists': True, 'resolved': '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/website/templates/SPEC.md'}], 'issues': []}]}
```

### audit_documentation_inventory.py

**Path**: `documentation/audit_documentation_inventory.py`

```text
2026-01-07 15:57:06,334 - codomyrmex.logging_monitoring.logger_config - INFO - Logging configured: Level=INFO, OutputType=TEXT, File='Console', Format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
2026-01-07 15:57:06,334 - codomyrmex.documentation.documentation_website - INFO - Codomyrmex centralized logging initialized successfully via documentation_website.py.
```

### audit_module_docs.py

**Path**: `documentation/audit_module_docs.py`

```text
2026-01-07 15:57:06,372 - codomyrmex.logging_monitoring.logger_config - INFO - Logging configured: Level=INFO, OutputType=TEXT, File='Console', Format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
2026-01-07 15:57:06,372 - codomyrmex.documentation.documentation_website - INFO - Codomyrmex centralized logging initialized successfully via documentation_website.py.
```

### audit_structure.py

**Path**: `documentation/audit_structure.py`

```text
2026-01-07 15:57:06,419 - codomyrmex.logging_monitoring.logger_config - INFO - Logging configured: Level=INFO, OutputType=TEXT, File='Console', Format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
2026-01-07 15:57:06,419 - codomyrmex.documentation.documentation_website - INFO - Codomyrmex centralized logging initialized successfully via documentation_website.py.
```

### auto_generate_docs.py

**Path**: `documentation/auto_generate_docs.py`

```text
2026-01-07 15:57:06,464 - codomyrmex.logging_monitoring.logger_config - INFO - Logging configured: Level=INFO, OutputType=TEXT, File='Console', Format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
2026-01-07 15:57:06,464 - codomyrmex.documentation.documentation_website - INFO - Codomyrmex centralized logging initialized successfully via documentation_website.py.
usage: auto_generate_docs.py [-h] [--repo-root REPO_ROOT] [--module MODULE]
                             [--dry-run] [--all]

Automatically generate module documentation

options:
  -h, --help            show this help message and exit
  --repo-root REPO_ROOT
                        Repository root directory
  --module MODULE       Specific module to document (default: all modules)
  --dry-run             Preview changes without writing files
  --all                 Generate documentation for all modules
```

### boost_quality_score.py

**Path**: `documentation/boost_quality_score.py`

```text
2026-01-07 15:57:06,530 - codomyrmex.logging_monitoring.logger_config - INFO - Logging configured: Level=INFO, OutputType=TEXT, File='Console', Format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
2026-01-07 15:57:06,530 - codomyrmex.documentation.documentation_website - INFO - Codomyrmex centralized logging initialized successfully via documentation_website.py.
Boosted 17 files.
```

### bootstrap_agents_readmes.py

**Path**: `documentation/bootstrap_agents_readmes.py`

```text
2026-01-07 15:57:06,597 - codomyrmex.logging_monitoring.logger_config - INFO - Logging configured: Level=INFO, OutputType=TEXT, File='Console', Format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
2026-01-07 15:57:06,597 - codomyrmex.documentation.documentation_website - INFO - Codomyrmex centralized logging initialized successfully via documentation_website.py.
usage: bootstrap_agents_readmes.py [-h] [--repo-root REPO_ROOT] [--dry-run]

Bootstrap AGENTS.md and README.md files across the repository

options:
  -h, --help            show this help message and exit
  --repo-root REPO_ROOT
                        Repository root directory
  --dry-run             Preview changes without creating files
```

### check_completeness.py

**Path**: `documentation/check_completeness.py`

```text
Failed to get help text (Exit Code: 1)

Stderr:
Traceback (most recent call last):
  File "/Users/mini/Documents/GitHub/codomyrmex/scripts/documentation/check_completeness.py", line 19, in <module>
    sys.exit(check_completeness.main())
             ~~~~~~~~~~~~~~~~~~~~~~~^^
  File "/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/documentation/scripts/check_completeness.py", line 315, in main
    status_content = checker.generate_implementation_status(results)
  File "/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/documentation/scripts/check_completeness.py", line 219, in generate_implementation_status
    f"- **Complete**: {complete_modules} ({complete_modules/total_modules*100:.1f}%)",
                                           ~~~~~~~~~~~~~~~~^~~~~~~~~~~~~~
ZeroDivisionError: division by zero
```

### check_doc_links.py

**Path**: `documentation/check_doc_links.py`

```text
Failed to get help text (Exit Code: 1)

Stderr:
```

### check_docs_status.py

**Path**: `documentation/check_docs_status.py`

```text
2026-01-07 15:57:06,794 - codomyrmex.logging_monitoring.logger_config - INFO - Logging configured: Level=INFO, OutputType=TEXT, File='Console', Format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
2026-01-07 15:57:06,794 - codomyrmex.documentation.documentation_website - INFO - Codomyrmex centralized logging initialized successfully via documentation_website.py.
```

### check_documentation_completeness.py

**Path**: `documentation/check_documentation_completeness.py`

```text
Failed to get help text (Exit Code: 1)

Stderr:
Traceback (most recent call last):
  File "/Users/mini/Documents/GitHub/codomyrmex/scripts/documentation/check_documentation_completeness.py", line 17, in <module>
    from codomyrmex.documentation.scripts import check_documentation_completeness
  File "/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/documentation/scripts/check_documentation_completeness.py", line 58, in <module>
    class CompletenessReport:
    ...<20 lines>...
            }
  File "/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/documentation/scripts/check_documentation_completeness.py", line 69, in CompletenessReport
    def to_dict(self) -> Dict[str, Any]:
                                   ^^^
NameError: name 'Any' is not defined. Did you mean: 'any'?
```

### check_example_coverage.py

**Path**: `documentation/check_example_coverage.py`

```text
Failed to get help text (Exit Code: 1)

Stderr:
Traceback (most recent call last):
  File "/Users/mini/Documents/GitHub/codomyrmex/scripts/documentation/check_example_coverage.py", line 19, in <module>
    sys.exit(check_example_coverage.main())
             ~~~~~~~~~~~~~~~~~~~~~~~~~~~^^
  File "/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/documentation/scripts/check_example_coverage.py", line 349, in main
    checker.print_report(report)
    ~~~~~~~~~~~~~~~~~~~~^^^^^^^^
  File "/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/documentation/scripts/check_example_coverage.py", line 294, in print_report
    print(f"   Complete Examples: {summary['complete_examples']}/{summary['total_examples']}")
                                                                  ~~~~~~~^^^^^^^^^^^^^^^^^^
KeyError: 'total_examples'
```

### check_example_links.py

**Path**: `documentation/check_example_links.py`

```text
2026-01-07 15:57:06,981 - codomyrmex.logging_monitoring.logger_config - INFO - Logging configured: Level=INFO, OutputType=TEXT, File='Console', Format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
2026-01-07 15:57:06,981 - codomyrmex.documentation.documentation_website - INFO - Codomyrmex centralized logging initialized successfully via documentation_website.py.
usage: check_example_links.py [-h] [--check-external] [--verbose] [--fix]
                              [--output OUTPUT]

Check links in Codomyrmex examples documentation

options:
  -h, --help           show this help message and exit
  --check-external     Also check external URLs
  --verbose, -v        Show detailed checking progress
  --fix                Attempt to fix broken internal links automatically
  --output, -o OUTPUT  Output file for link check report
```

### check_links.py

**Path**: `documentation/check_links.py`

```text
2026-01-07 15:57:07,101 - codomyrmex.logging_monitoring.logger_config - INFO - Logging configured: Level=INFO, OutputType=TEXT, File='Console', Format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
2026-01-07 15:57:07,101 - codomyrmex.documentation.documentation_website - INFO - Codomyrmex centralized logging initialized successfully via documentation_website.py.
```

### clean_agents_files.py

**Path**: `documentation/clean_agents_files.py`

```text
2026-01-07 15:57:07,150 - codomyrmex.logging_monitoring.logger_config - INFO - Logging configured: Level=INFO, OutputType=TEXT, File='Console', Format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
2026-01-07 15:57:07,150 - codomyrmex.documentation.documentation_website - INFO - Codomyrmex centralized logging initialized successfully via documentation_website.py.
usage: clean_agents_files.py [-h] [--repo-root REPO_ROOT] [--dry-run]
                             [--clean]

Clean AGENTS.md files by removing conceptual items

options:
  -h, --help            show this help message and exit
  --repo-root REPO_ROOT
                        Repository root directory
  --dry-run             Show what would be cleaned without making changes
  --clean               Actually clean the files
```

### cleanup_operating_contracts.py

**Path**: `documentation/cleanup_operating_contracts.py`

```text
2026-01-07 15:57:07,190 - codomyrmex.logging_monitoring.logger_config - INFO - Logging configured: Level=INFO, OutputType=TEXT, File='Console', Format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
2026-01-07 15:57:07,190 - codomyrmex.documentation.documentation_website - INFO - Codomyrmex centralized logging initialized successfully via documentation_website.py.
Cleaned AGENTS.md
Cleaned examples/AGENTS.md
Cleaned examples/output/AGENTS.md
Cleaned examples/output/analysis/AGENTS.md
Cleaned 4 AGENTS.md files
```

### complete_placeholders.py

**Path**: `documentation/complete_placeholders.py`

```text
2026-01-07 15:57:07,235 - codomyrmex.logging_monitoring.logger_config - INFO - Logging configured: Level=INFO, OutputType=TEXT, File='Console', Format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
2026-01-07 15:57:07,235 - codomyrmex.documentation.documentation_website - INFO - Codomyrmex centralized logging initialized successfully via documentation_website.py.
usage: complete_placeholders.py [-h] [--repo-root REPO_ROOT] [--output OUTPUT]
                                [--dry-run] [--apply]

Complete placeholder content in documentation

options:
  -h, --help            show this help message and exit
  --repo-root REPO_ROOT
                        Repository root directory
  --output OUTPUT       Output directory for reports
  --dry-run             Preview changes without applying (default)
  --apply               Apply changes to files
```

### comprehensive_audit.py

**Path**: `documentation/comprehensive_audit.py`

```text
Failed to get help text (Exit Code: 1)

Stderr:
Traceback (most recent call last):
  File "/Users/mini/Documents/GitHub/codomyrmex/scripts/documentation/comprehensive_audit.py", line 19, in <module>
    sys.exit(comprehensive_audit.main())
             ~~~~~~~~~~~~~~~~~~~~~~~~^^
  File "/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/documentation/scripts/comprehensive_audit.py", line 633, in main
    report_path.write_text(report, encoding='utf-8')
    ~~~~~~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/Users/mini/.local/share/uv/python/cpython-3.13.11-macos-aarch64-none/lib/python3.13/pathlib/_local.py", line 555, in write_text
    return PathBase.write_text(self, data, encoding, errors, newline)
           ~~~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/Users/mini/.local/share/uv/python/cpython-3.13.11-macos-aarch64-none/lib/python3.13/pathlib/_abc.py", line 651, in write_text
    with self.open(mode='w', encoding=encoding, errors=errors, newline=newline) as f:
         ~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/Users/mini/.local/share/uv/python/cpython-3.13.11-macos-aarch64-none/lib/python3.13/pathlib/_local.py", line 537, in open
    return io.open(self, mode, buffering, encoding, errors, newline)
           ~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
FileNotFoundError: [Errno 2] No such file or directory: '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/docs/project/documentation-audit-report.md'
```

### comprehensive_doc_check.py

**Path**: `documentation/comprehensive_doc_check.py`

```text
2026-01-07 15:57:09,295 - codomyrmex.logging_monitoring.logger_config - INFO - Logging configured: Level=INFO, OutputType=TEXT, File='Console', Format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
2026-01-07 15:57:09,295 - codomyrmex.documentation.documentation_website - INFO - Codomyrmex centralized logging initialized successfully via documentation_website.py.
Checking 1763 documentation files...


=== SUMMARY ===
Files with issues: 508
Total broken links: 2
Files with placeholder content: 0
Files with navigation issues: 10
Files with structure issues: 994

=== TOP ISSUES ===

src/codomyrmex/website/SPEC.md:
  Broken links: 1
    - Reference Guides -> ../../docs/README.md

src/codomyrmex/agents/gemini/SPEC.md:
  Broken links: 1
    - Reference Guides -> ../../docs/README.md
  Structure issues: ['Missing version information', 'Missing status information']

config/database/examples/SPEC.md:
  Structure issues: ['Missing version information', 'Missing status information']

config/llm/examples/SPEC.md:
  Structure issues: ['Missing version information', 'Missing status information']

config/cache/examples/SPEC.md:
  Structure issues: ['Missing version information', 'Missing status information']

config/security/examples/SPEC.md:
  Structure issues: ['Missing version information', 'Missing status information']

config/workflows/SPEC.md:
  Structure issues: ['Missing version information', 'Missing status information']

config/workflows/tests/SPEC.md:
  Structure issues: ['Missing version information', 'Missing status information']

config/workflows/examples/SPEC.md:
  Structure issues: ['Missing version information', 'Missing status information']

config/workflows/production/SPEC.md:
  Structure issues: ['Missing version information', 'Missing status information']

config/api/examples/SPEC.md:
  Structure issues: ['Missing version information', 'Missing status information']

config/monitoring/examples/SPEC.md:
  Structure issues: ['Missing version information', 'Missing status information']

output/README.md:
  Navigation issues: ['Missing reference to SPEC.md']

output/SPEC.md:
  Structure issues: ['Missing version information', 'Missing status information']

output/gemini_docs/README.md:
  Structure issues: ['Missing version information', 'Missing status information']

output/gemini_docs/SPEC.md:
  Structure issues: ['Missing version information', 'Missing status information']

output/gemini_docs/AGENTS.md:
  Structure issues: ['Missing version information', 'Missing status information']

output/gemini_docs/function-calling/README.md:
  Structure issues: ['Missing version information', 'Missing status information']

output/gemini_docs/function-calling/SPEC.md:
  Structure issues: ['Missing version information', 'Missing status information']

output/gemini_docs/function-calling/AGENTS.md:
  Structure issues: ['Missing version information', 'Missing status information']
```

### comprehensive_filepath_audit.py

**Path**: `documentation/comprehensive_filepath_audit.py`

```text
2026-01-07 15:57:09,637 - codomyrmex.logging_monitoring.logger_config - INFO - Logging configured: Level=INFO, OutputType=TEXT, File='Console', Format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
2026-01-07 15:57:09,637 - codomyrmex.documentation.documentation_website - INFO - Codomyrmex centralized logging initialized successfully via documentation_website.py.
usage: comprehensive_filepath_audit.py [-h] [--repo-root REPO_ROOT]
                                       [--output OUTPUT]
                                       [--format {json,html,both}]
                                       [--fail-on-issues]

Comprehensive filepath and signpost audit for Codomyrmex repository

options:
  -h, --help            show this help message and exit
  --repo-root REPO_ROOT
                        Repository root directory
  --output OUTPUT       Output directory for results
  --format {json,html,both}
                        Output format
  --fail-on-issues      Exit with error code if issues found
```

### comprehensive_fix.py

**Path**: `documentation/comprehensive_fix.py`

```text
2026-01-07 15:57:09,684 - codomyrmex.logging_monitoring.logger_config - INFO - Logging configured: Level=INFO, OutputType=TEXT, File='Console', Format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
2026-01-07 15:57:09,684 - codomyrmex.documentation.documentation_website - INFO - Codomyrmex centralized logging initialized successfully via documentation_website.py.
================================================================================
Comprehensive Documentation Fixer
================================================================================

Fixing 0 example_tutorial.md files...


✅ Fixed 0 tutorial files

Fixing 0 docs/index.md files...


✅ Fixed 0 index files

================================================================================
Summary: Fixed 0 files
================================================================================
```

### comprehensive_placeholder_check.py

**Path**: `documentation/comprehensive_placeholder_check.py`

```text
2026-01-07 15:57:09,736 - codomyrmex.logging_monitoring.logger_config - INFO - Logging configured: Level=INFO, OutputType=TEXT, File='Console', Format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
2026-01-07 15:57:09,736 - codomyrmex.documentation.documentation_website - INFO - Codomyrmex centralized logging initialized successfully via documentation_website.py.
Checking 1764 files for placeholders...


config/workflows/tests/README.md: 1 placeholder(s)
  - Generic test placeholder: Test files and validation suites.

config/workflows/tests/AGENTS.md: 1 placeholder(s)
  - Generic test placeholder: Test files and validation suites.

projects/test_project/README.md: 1 placeholder(s)
  - Generic test placeholder: Test files and validation suites.

projects/test_project/AGENTS.md: 1 placeholder(s)
  - Generic test placeholder: Test files and validation suites.

projects/test_project/SPEC.md: 1 placeholder(s)
  - Generic test placeholder: Test files and validation suites.

scripts/tests/README.md: 1 placeholder(s)
  - Generic test placeholder: Test files and validation suites.

scripts/tests/AGENTS.md: 1 placeholder(s)
  - Generic test placeholder: Test files and validation suites.

scripts/docs/README.md: 1 placeholder(s)
  - Generic documentation placeholder: Documentation files and guides.

scripts/docs/AGENTS.md: 1 placeholder(s)
  - Generic documentation placeholder: Documentation files and guides.

scripts/docs/SPEC.md: 3 placeholder(s)
  - Module name variable placeholder: [module_name]
  - Module name variable placeholder: [module_name]
  - Module name variable placeholder: [module_name]

src/codomyrmex/documentation/docs/README.md: 1 placeholder(s)
  - Generic documentation placeholder: Documentation files and guides.

src/codomyrmex/documentation/docs/AGENTS.md: 1 placeholder(s)
  - Generic documentation placeholder: Documentation files and guides.

src/codomyrmex/documentation/docs/modules/pattern_matching/docs/README.md: 1 placeholder(s)
  - Generic documentation placeholder: Documentation files and guides.

src/codomyrmex/documentation/docs/modules/pattern_matching/docs/AGENTS.md: 1 placeholder(s)
  - Generic documentation placeholder: Documentation files and guides.

src/codomyrmex/documentation/docs/modules/static_analysis/docs/README.md: 1 placeholder(s)
  - Generic documentation placeholder: Documentation files and guides.

src/codomyrmex/documentation/docs/modules/static_analysis/docs/AGENTS.md: 1 placeholder(s)
  - Generic documentation placeholder: Documentation files and guides.

src/codomyrmex/documentation/docs/modules/ai_code_editing/docs/README.md: 1 placeholder(s)
  - Generic documentation placeholder: Documentation files and guides.

src/codomyrmex/documentation/docs/modules/ai_code_editing/docs/AGENTS.md: 1 placeholder(s)
  - Generic documentation placeholder: Documentation files and guides.

src/codomyrmex/documentation/docs/modules/template/docs/README.md: 1 placeholder(s)
  - Generic documentation placeholder: Documentation files and guides.

src/codomyrmex/documentation/docs/modules/template/docs/AGENTS.md: 1 placeholder(s)
  - Generic documentation placeholder: Documentation files and guides.

src/codomyrmex/documentation/docs/modules/environment_setup/docs/README.md: 1 placeholder(s)
  - Generic documentation placeholder: Documentation files and guides.

src/codomyrmex/documentation/docs/modules/environment_setup/docs/AGENTS.md: 1 placeholder(s)
  - Generic documentation placeholder: Documentation files and guides.

src/codomyrmex/documentation/docs/modules/module_template/docs/README.md: 1 placeholder(s)
  - Generic documentation placeholder: Documentation files and guides.

src/codomyrmex/documentation/docs/modules/module_template/docs/AGENTS.md: 1 placeholder(s)
  - Generic documentation placeholder: Documentation files and guides.

src/codomyrmex/documentation/docs/modules/data_visualization/docs/README.md: 1 placeholder(s)
  - Generic documentation placeholder: Documentation files and guides.

src/codomyrmex/documentation/docs/modules/data_visualization/docs/AGENTS.md: 1 placeholder(s)
  - Generic documentation placeholder: Documentation files and guides.

src/codomyrmex/documentation/docs/modules/logging_monitoring/docs/README.md: 1 placeholder(s)
  - Generic documentation placeholder: Documentation files and guides.

src/codomyrmex/documentation/docs/modules/logging_monitoring/docs/AGENTS.md: 1 placeholder(s)
  - Generic documentation placeholder: Documentation files and guides.

src/codomyrmex/documentation/docs/modules/model_context_protocol/docs/README.md: 1 placeholder(s)
  - Generic documentation placeholder: Documentation files and guides.

src/codomyrmex/documentation/docs/modules/model_context_protocol/docs/AGENTS.md: 1 placeholder(s)
  - Generic documentation placeholder: Documentation files and guides.

src/codomyrmex/documentation/docs/modules/build_synthesis/docs/README.md: 1 placeholder(s)
  - Generic documentation placeholder: Documentation files and guides.

src/codomyrmex/documentation/docs/modules/build_synthesis/docs/AGENTS.md: 1 placeholder(s)
  - Generic documentation placeholder: Documentation files and guides.

src/codomyrmex/documentation/docs/modules/git_operations/docs/README.md: 1 placeholder(s)
  - Generic documentation placeholder: Documentation files and guides.

src/codomyrmex/documentation/docs/modules/git_operations/docs/AGENTS.md: 1 placeholder(s)
  - Generic documentation placeholder: Documentation files and guides.

src/codomyrmex/llm/outputs/test_results/README.md: 1 placeholder(s)
  - Generic test placeholder: Test files and validation suites.

src/codomyrmex/llm/outputs/test_results/AGENTS.md: 1 placeholder(s)
  - Generic test placeholder: Test files and validation suites.

src/codomyrmex/tests/README.md: 1 placeholder(s)
  - Generic test placeholder: Test files and validation suites.

src/codomyrmex/tests/AGENTS.md: 1 placeholder(s)
  - Generic test placeholder: Test files and validation suites.

=== SUMMARY ===
Total placeholder issues found: 40
Files with generic placeholders fixed: 0
```

### comprehensive_triple_check.py

**Path**: `documentation/comprehensive_triple_check.py`

```text
2026-01-07 15:57:09,954 - codomyrmex.logging_monitoring.logger_config - INFO - Logging configured: Level=INFO, OutputType=TEXT, File='Console', Format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
2026-01-07 15:57:09,954 - codomyrmex.documentation.documentation_website - INFO - Codomyrmex centralized logging initialized successfully via documentation_website.py.
Triple-checking 1764 documentation files...


=== TRIPLE-CHECK SUMMARY ===
Total files checked: 1764
Files with issues: 988
Total placeholders: 508
Total broken links: 2
Total completeness issues: 1021

=== FILES WITH PLACEHOLDERS (472) ===

scripts/agents/SPEC.md: 31 placeholder(s)
  Line 329: TODO marker - todo
  Line 330: TODO marker - TODO
  Line 334: TODO marker - todo

scripts/docs/SPEC.md: 3 placeholder(s)
  Line 21: Module name variable placeholder - [module_name]
  Line 22: Module name variable placeholder - [module_name]
  Line 23: Module name variable placeholder - [module_name]

docs/project/AGENTS.md: 2 placeholder(s)
  Line 33: TODO marker - todo
  Line 38: TODO marker - TODO

docs/modules/SPEC.md: 2 placeholder(s)
  Line 75: TODO marker - TODO
  Line 75: PLACEHOLDER marker - placeholder

src/codomyrmex/documentation/docs/modules/pattern_matching/AGENTS.md: 2 placeholder(s)
  Line 38: TODO marker - TODO
  Line 35: PLACEHOLDER marker - placeholder

src/codomyrmex/agents/droid/AGENTS.md: 2 placeholder(s)
  Line 25: TODO marker - todo
  Line 32: TODO marker - TODO

config/AGENTS.md: 1 placeholder(s)
  Line 42: TODO marker - TODO

config/database/AGENTS.md: 1 placeholder(s)
  Line 29: TODO marker - TODO

config/database/examples/AGENTS.md: 1 placeholder(s)
  Line 27: TODO marker - TODO

config/llm/AGENTS.md: 1 placeholder(s)
  Line 28: TODO marker - TODO

=== FILES WITH BROKEN LINKS (2) ===

src/codomyrmex/website/SPEC.md: 1 broken link(s)
  Line 49: [Reference Guides](../docs/README.md) - Path does not exist: /Users/mini/Documents/GitHub/codomyrmex/src/docs/README.md

src/codomyrmex/agents/gemini/SPEC.md: 1 broken link(s)
  Line 49: [Reference Guides](../docs/README.md) - Path does not exist: /Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/docs/README.md

=== FILES WITH COMPLETENESS ISSUES (515) ===

config/database/examples/SPEC.md:
  - Missing version information
  - Missing status information

config/llm/examples/SPEC.md:
  - Missing version information
  - Missing status information

config/cache/examples/SPEC.md:
  - Missing version information
  - Missing status information

config/security/examples/SPEC.md:
  - Missing version information
  - Missing status information

config/workflows/SPEC.md:
  - Missing version information
  - Missing status information

config/workflows/tests/SPEC.md:
  - Missing version information
  - Missing status information

config/workflows/examples/SPEC.md:
  - Missing version information
  - Missing status information

config/workflows/production/SPEC.md:
  - Missing version information
  - Missing status information

config/api/examples/SPEC.md:
  - Missing version information
  - Missing status information

config/monitoring/examples/SPEC.md:
  - Missing version information
  - Missing status information

Detailed report: /Users/mini/Documents/GitHub/codomyrmex/output/triple_check_report.md
```

### create_example_tutorials.py

**Path**: `documentation/create_example_tutorials.py`

```text
2026-01-07 15:57:10,786 - codomyrmex.logging_monitoring.logger_config - INFO - Logging configured: Level=INFO, OutputType=TEXT, File='Console', Format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
2026-01-07 15:57:10,786 - codomyrmex.documentation.documentation_website - INFO - Codomyrmex centralized logging initialized successfully via documentation_website.py.
```

### create_missing_doc_files.py

**Path**: `documentation/create_missing_doc_files.py`

```text
2026-01-07 15:57:10,842 - codomyrmex.logging_monitoring.logger_config - INFO - Logging configured: Level=INFO, OutputType=TEXT, File='Console', Format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
2026-01-07 15:57:10,842 - codomyrmex.documentation.documentation_website - INFO - Codomyrmex centralized logging initialized successfully via documentation_website.py.
```

### doc_auditor.py

**Path**: `documentation/doc_auditor.py`

```text
2026-01-07 15:57:10,914 - codomyrmex.logging_monitoring.logger_config - INFO - Logging configured: Level=INFO, OutputType=TEXT, File='Console', Format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
2026-01-07 15:57:10,914 - codomyrmex.documentation.documentation_website - INFO - Codomyrmex centralized logging initialized successfully via documentation_website.py.
```

### doc_scaffolder.py

**Path**: `documentation/doc_scaffolder.py`

```text
2026-01-07 15:57:10,959 - codomyrmex.logging_monitoring.logger_config - INFO - Logging configured: Level=INFO, OutputType=TEXT, File='Console', Format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
2026-01-07 15:57:10,959 - codomyrmex.documentation.documentation_website - INFO - Codomyrmex centralized logging initialized successfully via documentation_website.py.
```

### documentation_scan_report.py

**Path**: `documentation/documentation_scan_report.py`

```text
2026-01-07 15:57:11,015 - codomyrmex.logging_monitoring.logger_config - INFO - Logging configured: Level=INFO, OutputType=TEXT, File='Console', Format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
2026-01-07 15:57:11,015 - codomyrmex.documentation.documentation_website - INFO - Codomyrmex centralized logging initialized successfully via documentation_website.py.
================================================================================
PHASE 1: DISCOVERY AND INVENTORY
================================================================================

1.1 Scanning all markdown files...
  ✓ Found 2818 markdown files
  ✓ Found 279 AGENTS.md files
  ✓ Found 1560 README.md files

1.1 Identifying configuration files...
  ✓ Found 2118 configuration files

1.2 Mapping documentation structure...
  ✓ Mapped 5 documentation categories

1.3 Cataloging existing validation tools...
  ✓ Found 0 existing validation tools

✓ Phase 1 complete!

================================================================================
PHASE 2: ACCURACY VERIFICATION
================================================================================

2.1 Checking content accuracy...
  ✓ Found 0 content accuracy issues

2.2 Validating references...
  ✓ Found 0 reference issues

2.3 Checking terminology consistency...
  ✓ Found 2 terminology issues

✓ Phase 2 complete!

================================================================================
PHASE 3: COMPLETENESS ANALYSIS
================================================================================

3.1 Checking coverage completeness...
  ✓ Found 0 coverage gaps

3.2 Checking audience completeness...
  ✓ Found 2 audience gaps

3.3 Checking cross-reference completeness...
  ✓ Found 3 cross-reference gaps

✓ Phase 3 complete!

================================================================================
PHASE 4: QUALITY ASSESSMENT
================================================================================

4.1 Assessing clarity and readability...
  ✓ Found 20 quality issues

4.2 Assessing actionability...
  ✓ Found 20 actionability issues

4.3 Assessing maintainability...
  ✓ Found 0 maintainability issues

✓ Phase 4 complete!

================================================================================
PHASE 5: INTELLIGENT IMPROVEMENTS
================================================================================

5.1 Analyzing structural improvements needed...
5.2 Analyzing content improvements needed...
5.3 Analyzing UX improvements needed...
5.4 Analyzing technical improvements needed...
  ✓ Identified 0 improvement opportunities

✓ Phase 5 complete!

================================================================================
PHASE 6: VERIFICATION AND VALIDATION
================================================================================

6.1 Running automated validation tools...
  ✓ Completed automated checks

6.2 Manual review checklist...
  ✓ Generated manual review checklist

✓ Phase 6 complete!

================================================================================
PHASE 7: REPORTING
================================================================================

7.1 Generating summary statistics...
  ✓ Generated summary statistics

7.2 Compiling issue catalog...
  ✓ Compiled issue catalog

7.3 Generating recommendations...
  ✓ Generated recommendations

✓ Phase 7 complete!

# Documentation Scan and Improvement Report

Generated: 2026-01-07T15:57:12.675546

Repository: /Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex

================================================================================

## Phase 1: Discovery and Inventory

- Total Markdown Files: 2818
- AGENTS.md Files: 279
- README.md Files: 1560
- Configuration Files: 2118
- Documentation Categories: 5
- Validation Tools Found: 0


## Phase 2: Accuracy Verification

- Content Issues: 0
- Reference Issues: 0
- Terminology Issues: 2


## Phase 3: Completeness Analysis

- Coverage Gaps: 0
- Audience Gaps: 2
- Cross-Reference Gaps: 3


## Phase 4: Quality Assessment

- Quality Issues: 20
- Actionability Issues: 20
- Maintainability Issues: 0


## Phase 5: Intelligent Improvements

- Improvements Identified: 0
- Files Updated: 0


## Phase 6: Verification and Validation

- Validation Tools Run: 3
- Manual Review Items: 8


## Phase 7: Reporting

### Summary Statistics

- Total Files Scanned: 2818
- Issues by Category:
  - broken_links: 0
  - missing_documentation: 0
  - outdated_information: 0
  - inconsistencies: 2
  - quality_issues: 20
- Improvements Identified: 0

### Recommendations

- **Process Improvement** (medium): Set up automated documentation validation in CI/CD pipeline



✓ Results saved to /Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/@output/documentation_scan
```

### documentation_status_summary.py

**Path**: `documentation/documentation_status_summary.py`

```text
2026-01-07 15:57:12,725 - codomyrmex.logging_monitoring.logger_config - INFO - Logging configured: Level=INFO, OutputType=TEXT, File='Console', Format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
2026-01-07 15:57:12,726 - codomyrmex.documentation.documentation_website - INFO - Codomyrmex centralized logging initialized successfully via documentation_website.py.
```

### enforce_quality_gate.py

**Path**: `documentation/enforce_quality_gate.py`

```text
2026-01-07 15:57:12,775 - codomyrmex.logging_monitoring.logger_config - INFO - Logging configured: Level=INFO, OutputType=TEXT, File='Console', Format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
2026-01-07 15:57:12,775 - codomyrmex.documentation.documentation_website - INFO - Codomyrmex centralized logging initialized successfully via documentation_website.py.
usage: enforce_quality_gate.py [-h] [--repo-root REPO_ROOT] [--output OUTPUT]
                               [--min-quality-score MIN_QUALITY_SCORE]
                               [--max-broken-links MAX_BROKEN_LINKS]
                               [--max-placeholders MAX_PLACEHOLDERS]
                               [--min-agents-valid-rate MIN_AGENTS_VALID_RATE]
                               [--fail-on-any] [--allow-warnings]

Enforce documentation quality gates

options:
  -h, --help            show this help message and exit
  --repo-root REPO_ROOT
                        Repository root directory
  --output OUTPUT       Output directory with validation results
  --min-quality-score MIN_QUALITY_SCORE
                        Minimum average quality score
  --max-broken-links MAX_BROKEN_LINKS
                        Maximum number of broken links allowed
  --max-placeholders MAX_PLACEHOLDERS
                        Maximum number of placeholders allowed
  --min-agents-valid-rate MIN_AGENTS_VALID_RATE
                        Minimum AGENTS.md validation rate percentage
  --fail-on-any         Fail if any check fails (vs warnings)
  --allow-warnings      Allow warnings without failing
```

### enhance_stubs.py

**Path**: `documentation/enhance_stubs.py`

```text
2026-01-07 15:57:12,821 - codomyrmex.logging_monitoring.logger_config - INFO - Logging configured: Level=INFO, OutputType=TEXT, File='Console', Format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
2026-01-07 15:57:12,821 - codomyrmex.documentation.documentation_website - INFO - Codomyrmex centralized logging initialized successfully via documentation_website.py.
```

### fix_agents_completeness.py

**Path**: `documentation/fix_agents_completeness.py`

```text
2026-01-07 15:57:12,866 - codomyrmex.logging_monitoring.logger_config - INFO - Logging configured: Level=INFO, OutputType=TEXT, File='Console', Format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
2026-01-07 15:57:12,866 - codomyrmex.documentation.documentation_website - INFO - Codomyrmex centralized logging initialized successfully via documentation_website.py.
usage: fix_agents_completeness.py [-h] [--report REPORT]
                                  [--repo-root REPO_ROOT]

Fix AGENTS.md completeness issues

options:
  -h, --help            show this help message and exit
  --report REPORT       Path to validation report JSON
  --repo-root REPO_ROOT
                        Repository root directory
```

### fix_agents_files.py

**Path**: `documentation/fix_agents_files.py`

```text
2026-01-07 15:57:12,917 - codomyrmex.logging_monitoring.logger_config - INFO - Logging configured: Level=INFO, OutputType=TEXT, File='Console', Format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
2026-01-07 15:57:12,917 - codomyrmex.documentation.documentation_website - INFO - Codomyrmex centralized logging initialized successfully via documentation_website.py.
usage: fix_agents_files.py [-h] [--repo-root REPO_ROOT] [--dry-run] [--fix]

Fix AGENTS.md files throughout repository

options:
  -h, --help            show this help message and exit
  --repo-root REPO_ROOT
                        Repository root directory
  --dry-run             Show what would be fixed without making changes
  --fix                 Actually apply fixes
```

### fix_agents_structure.py

**Path**: `documentation/fix_agents_structure.py`

```text
2026-01-07 15:57:12,968 - codomyrmex.logging_monitoring.logger_config - INFO - Logging configured: Level=INFO, OutputType=TEXT, File='Console', Format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
2026-01-07 15:57:12,968 - codomyrmex.documentation.documentation_website - INFO - Codomyrmex centralized logging initialized successfully via documentation_website.py.
Scanning /Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex for AGENTS.md files...
Fixed 0 AGENTS.md files.
```

### fix_all_module_src_links.py

**Path**: `documentation/fix_all_module_src_links.py`

```text
2026-01-07 15:57:13,185 - codomyrmex.logging_monitoring.logger_config - INFO - Logging configured: Level=INFO, OutputType=TEXT, File='Console', Format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
2026-01-07 15:57:13,185 - codomyrmex.documentation.documentation_website - INFO - Codomyrmex centralized logging initialized successfully via documentation_website.py.

Completed: Fixed 0 files
```

### fix_all_tutorial_references.py

**Path**: `documentation/fix_all_tutorial_references.py`

```text
2026-01-07 15:57:14,519 - codomyrmex.logging_monitoring.logger_config - INFO - Logging configured: Level=INFO, OutputType=TEXT, File='Console', Format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
2026-01-07 15:57:14,520 - codomyrmex.documentation.documentation_website - INFO - Codomyrmex centralized logging initialized successfully via documentation_website.py.
```

### fix_broken_links.py

**Path**: `documentation/fix_broken_links.py`

```text
Failed to get help text (Exit Code: 1)

Stderr:
```

### fix_bulk_placeholders.py

**Path**: `documentation/fix_bulk_placeholders.py`

```text
2026-01-07 15:57:14,670 - codomyrmex.logging_monitoring.logger_config - INFO - Logging configured: Level=INFO, OutputType=TEXT, File='Console', Format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
2026-01-07 15:57:14,670 - codomyrmex.documentation.documentation_website - INFO - Codomyrmex centralized logging initialized successfully via documentation_website.py.
```

### fix_common_doc_issues.py

**Path**: `documentation/fix_common_doc_issues.py`

```text
2026-01-07 15:57:14,749 - codomyrmex.logging_monitoring.logger_config - INFO - Logging configured: Level=INFO, OutputType=TEXT, File='Console', Format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
2026-01-07 15:57:14,749 - codomyrmex.documentation.documentation_website - INFO - Codomyrmex centralized logging initialized successfully via documentation_website.py.

Completed: Fixed 0 documentation files
```

### fix_contributing_refs.py

**Path**: `documentation/fix_contributing_refs.py`

```text
2026-01-07 15:57:15,613 - codomyrmex.logging_monitoring.logger_config - INFO - Logging configured: Level=INFO, OutputType=TEXT, File='Console', Format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
2026-01-07 15:57:15,613 - codomyrmex.documentation.documentation_website - INFO - Codomyrmex centralized logging initialized successfully via documentation_website.py.
```

### fix_deep_nested_src_links.py

**Path**: `documentation/fix_deep_nested_src_links.py`

```text
2026-01-07 15:57:15,674 - codomyrmex.logging_monitoring.logger_config - INFO - Logging configured: Level=INFO, OutputType=TEXT, File='Console', Format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
2026-01-07 15:57:15,674 - codomyrmex.documentation.documentation_website - INFO - Codomyrmex centralized logging initialized successfully via documentation_website.py.

Completed: Fixed 0 files
```

### fix_documentation_spec_links.py

**Path**: `documentation/fix_documentation_spec_links.py`

```text
2026-01-07 15:57:16,413 - codomyrmex.logging_monitoring.logger_config - INFO - Logging configured: Level=INFO, OutputType=TEXT, File='Console', Format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
2026-01-07 15:57:16,413 - codomyrmex.documentation.documentation_website - INFO - Codomyrmex centralized logging initialized successfully via documentation_website.py.

Completed: Fixed 0 files
```

### fix_documentation_src_links.py

**Path**: `documentation/fix_documentation_src_links.py`

```text
2026-01-07 15:57:16,490 - codomyrmex.logging_monitoring.logger_config - INFO - Logging configured: Level=INFO, OutputType=TEXT, File='Console', Format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
2026-01-07 15:57:16,490 - codomyrmex.documentation.documentation_website - INFO - Codomyrmex centralized logging initialized successfully via documentation_website.py.

Completed: Fixed 0 files
```

### fix_duplicate_navigation_labels.py

**Path**: `documentation/fix_duplicate_navigation_labels.py`

```text
2026-01-07 15:57:17,561 - codomyrmex.logging_monitoring.logger_config - INFO - Logging configured: Level=INFO, OutputType=TEXT, File='Console', Format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
2026-01-07 15:57:17,561 - codomyrmex.documentation.documentation_website - INFO - Codomyrmex centralized logging initialized successfully via documentation_website.py.

Completed: Fixed 0 files
```

### fix_examples_module_readmes.py

**Path**: `documentation/fix_examples_module_readmes.py`

```text
2026-01-07 15:57:20,156 - codomyrmex.logging_monitoring.logger_config - INFO - Logging configured: Level=INFO, OutputType=TEXT, File='Console', Format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
2026-01-07 15:57:20,156 - codomyrmex.documentation.documentation_website - INFO - Codomyrmex centralized logging initialized successfully via documentation_website.py.

Completed: Fixed 0 examples module README files
```

### fix_links.py

**Path**: `documentation/fix_links.py`

```text
2026-01-07 15:57:20,224 - codomyrmex.logging_monitoring.logger_config - INFO - Logging configured: Level=INFO, OutputType=TEXT, File='Console', Format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
2026-01-07 15:57:20,224 - codomyrmex.documentation.documentation_website - INFO - Codomyrmex centralized logging initialized successfully via documentation_website.py.
```

### fix_markdown_newlines.py

**Path**: `documentation/fix_markdown_newlines.py`

```text
2026-01-07 15:57:20,293 - codomyrmex.logging_monitoring.logger_config - INFO - Logging configured: Level=INFO, OutputType=TEXT, File='Console', Format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
2026-01-07 15:57:20,293 - codomyrmex.documentation.documentation_website - INFO - Codomyrmex centralized logging initialized successfully via documentation_website.py.
```

### fix_missing_api_links.py

**Path**: `documentation/fix_missing_api_links.py`

```text
2026-01-07 15:57:20,355 - codomyrmex.logging_monitoring.logger_config - INFO - Logging configured: Level=INFO, OutputType=TEXT, File='Console', Format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
2026-01-07 15:57:20,355 - codomyrmex.documentation.documentation_website - INFO - Codomyrmex centralized logging initialized successfully via documentation_website.py.

Completed: Fixed 0 files
```

### fix_navigation_links.py

**Path**: `documentation/fix_navigation_links.py`

```text
2026-01-07 15:57:21,596 - codomyrmex.logging_monitoring.logger_config - INFO - Logging configured: Level=INFO, OutputType=TEXT, File='Console', Format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
2026-01-07 15:57:21,596 - codomyrmex.documentation.documentation_website - INFO - Codomyrmex centralized logging initialized successfully via documentation_website.py.
usage: fix_navigation_links.py [-h] [--repo-root REPO_ROOT] [--dry-run]
                               [--fix]

Fix navigation links in AGENTS.md files

options:
  -h, --help            show this help message and exit
  --repo-root REPO_ROOT
                        Repository root directory
  --dry-run             Show what would be fixed without making changes
  --fix                 Actually fix the navigation links
```

### fix_orchestrator_commands.py

**Path**: `documentation/fix_orchestrator_commands.py`

```text
2026-01-07 15:57:21,670 - codomyrmex.logging_monitoring.logger_config - INFO - Logging configured: Level=INFO, OutputType=TEXT, File='Console', Format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
2026-01-07 15:57:21,670 - codomyrmex.documentation.documentation_website - INFO - Codomyrmex centralized logging initialized successfully via documentation_website.py.
usage: fix_orchestrator_commands.py [-h] [--repo-root REPO_ROOT] [--dry-run]
                                    [--fix]

Fix orchestrator commands in AGENTS.md files

options:
  -h, --help            show this help message and exit
  --repo-root REPO_ROOT
                        Repository root directory
  --dry-run             Show what would be fixed without making changes
  --fix                 Actually fix the orchestrator commands
```

### fix_parent_references.py

**Path**: `documentation/fix_parent_references.py`

```text
2026-01-07 15:57:21,759 - codomyrmex.logging_monitoring.logger_config - INFO - Logging configured: Level=INFO, OutputType=TEXT, File='Console', Format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
2026-01-07 15:57:21,759 - codomyrmex.documentation.documentation_website - INFO - Codomyrmex centralized logging initialized successfully via documentation_website.py.
Found 279 AGENTS.md files

Fixed 0 files
```

### fix_placeholders.py

**Path**: `documentation/fix_placeholders.py`

```text
2026-01-07 15:57:22,296 - codomyrmex.logging_monitoring.logger_config - INFO - Logging configured: Level=INFO, OutputType=TEXT, File='Console', Format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
2026-01-07 15:57:22,296 - codomyrmex.documentation.documentation_website - INFO - Codomyrmex centralized logging initialized successfully via documentation_website.py.
```

### fix_remaining_links.py

**Path**: `documentation/fix_remaining_links.py`

```text
2026-01-07 15:57:22,372 - codomyrmex.logging_monitoring.logger_config - INFO - Logging configured: Level=INFO, OutputType=TEXT, File='Console', Format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
2026-01-07 15:57:22,372 - codomyrmex.documentation.documentation_website - INFO - Codomyrmex centralized logging initialized successfully via documentation_website.py.

Completed: Fixed 0 files
```

### fix_script_specs.py

**Path**: `documentation/fix_script_specs.py`

```text
2026-01-07 15:57:22,810 - codomyrmex.logging_monitoring.logger_config - INFO - Logging configured: Level=INFO, OutputType=TEXT, File='Console', Format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
2026-01-07 15:57:22,810 - codomyrmex.documentation.documentation_website - INFO - Codomyrmex centralized logging initialized successfully via documentation_website.py.
```

### fix_scripts_subdirs.py

**Path**: `documentation/fix_scripts_subdirs.py`

```text
2026-01-07 15:57:22,902 - codomyrmex.logging_monitoring.logger_config - INFO - Logging configured: Level=INFO, OutputType=TEXT, File='Console', Format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
2026-01-07 15:57:22,902 - codomyrmex.documentation.documentation_website - INFO - Codomyrmex centralized logging initialized successfully via documentation_website.py.

Completed: Fixed 0 scripts subdirectory README files
```

### fix_security_digital_readme.py

**Path**: `documentation/fix_security_digital_readme.py`

```text
2026-01-07 15:57:22,969 - codomyrmex.logging_monitoring.logger_config - INFO - Logging configured: Level=INFO, OutputType=TEXT, File='Console', Format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
2026-01-07 15:57:22,969 - codomyrmex.documentation.documentation_website - INFO - Codomyrmex centralized logging initialized successfully via documentation_website.py.
Fixed: /Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/security/digital/README.md
```

### fix_security_digital_readme_nav.py

**Path**: `documentation/fix_security_digital_readme_nav.py`

```text
2026-01-07 15:57:23,044 - codomyrmex.logging_monitoring.logger_config - INFO - Logging configured: Level=INFO, OutputType=TEXT, File='Console', Format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
2026-01-07 15:57:23,044 - codomyrmex.documentation.documentation_website - INFO - Codomyrmex centralized logging initialized successfully via documentation_website.py.
Fixed: /Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/security/digital/README.md
```

### fix_spec_links.py

**Path**: `documentation/fix_spec_links.py`

```text
2026-01-07 15:57:23,183 - codomyrmex.logging_monitoring.logger_config - INFO - Logging configured: Level=INFO, OutputType=TEXT, File='Console', Format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
2026-01-07 15:57:23,183 - codomyrmex.documentation.documentation_website - INFO - Codomyrmex centralized logging initialized successfully via documentation_website.py.

Completed: Fixed 0 SPEC.md files
```

### fix_src_doubling.py

**Path**: `documentation/fix_src_doubling.py`

```text
2026-01-07 15:57:23,513 - codomyrmex.logging_monitoring.logger_config - INFO - Logging configured: Level=INFO, OutputType=TEXT, File='Console', Format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
2026-01-07 15:57:23,513 - codomyrmex.documentation.documentation_website - INFO - Codomyrmex centralized logging initialized successfully via documentation_website.py.
```

### fix_template_paths.py

**Path**: `documentation/fix_template_paths.py`

```text
2026-01-07 15:57:23,600 - codomyrmex.logging_monitoring.logger_config - INFO - Logging configured: Level=INFO, OutputType=TEXT, File='Console', Format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
2026-01-07 15:57:23,600 - codomyrmex.documentation.documentation_website - INFO - Codomyrmex centralized logging initialized successfully via documentation_website.py.
```

### fix_tutorial_references.py

**Path**: `documentation/fix_tutorial_references.py`

```text
2026-01-07 15:57:23,672 - codomyrmex.logging_monitoring.logger_config - INFO - Logging configured: Level=INFO, OutputType=TEXT, File='Console', Format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
2026-01-07 15:57:23,672 - codomyrmex.documentation.documentation_website - INFO - Codomyrmex centralized logging initialized successfully via documentation_website.py.
```

### generate_architecture_diagrams.py

**Path**: `documentation/generate_architecture_diagrams.py`

```text
2026-01-07 15:57:23,760 - codomyrmex.logging_monitoring.logger_config - INFO - Logging configured: Level=INFO, OutputType=TEXT, File='Console', Format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
2026-01-07 15:57:23,760 - codomyrmex.documentation.documentation_website - INFO - Codomyrmex centralized logging initialized successfully via documentation_website.py.
usage: generate_architecture_diagrams.py [-h] [--module MODULE]
                                         [--dependency-graph]
                                         [--system-architecture]
                                         [--workflow WORKFLOW]
                                         [--add-to-readme ADD_TO_README]
                                         [--output OUTPUT]

Generate architecture diagrams

options:
  -h, --help            show this help message and exit
  --module, -m MODULE   Generate diagram for a specific module
  --dependency-graph    Generate module dependency graph
  --system-architecture
                        Generate system architecture diagram
  --workflow WORKFLOW   Path to workflow JSON file to diagram
  --add-to-readme ADD_TO_README
                        Add generated diagrams to specified README file
  --output, -o OUTPUT   Output file for diagram (default: stdout)

Examples:
  generate_architecture_diagrams.py --module logging_monitoring
  generate_architecture_diagrams.py --dependency-graph
  generate_architecture_diagrams.py --system-architecture
  generate_architecture_diagrams.py --workflow workflow.json
  generate_architecture_diagrams.py --add-to-readme docs/README.md
```

### generate_dashboard.py

**Path**: `documentation/generate_dashboard.py`

```text
2026-01-07 15:57:23,839 - codomyrmex.logging_monitoring.logger_config - INFO - Logging configured: Level=INFO, OutputType=TEXT, File='Console', Format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
2026-01-07 15:57:23,839 - codomyrmex.documentation.documentation_website - INFO - Codomyrmex centralized logging initialized successfully via documentation_website.py.
usage: generate_dashboard.py [-h] [--repo-root REPO_ROOT] [--output OUTPUT]

Generate documentation quality dashboard

options:
  -h, --help            show this help message and exit
  --repo-root REPO_ROOT
                        Repository root directory
  --output OUTPUT       Output directory for dashboard
```

### generate_doc_verification_report.py

**Path**: `documentation/generate_doc_verification_report.py`

```text
2026-01-07 15:57:23,956 - codomyrmex.logging_monitoring.logger_config - INFO - Logging configured: Level=INFO, OutputType=TEXT, File='Console', Format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
2026-01-07 15:57:23,957 - codomyrmex.documentation.documentation_website - INFO - Codomyrmex centralized logging initialized successfully via documentation_website.py.
Report generated: /Users/mini/Documents/GitHub/codomyrmex/output/documentation_verification_report.md

=== VERIFICATION SUMMARY ===
Total files: 1763
Broken links: 2
Missing navigation: 0
Missing version: 497
Missing status: 497
Placeholder content: 0
```

### generate_missing_docs.py

**Path**: `documentation/generate_missing_docs.py`

```text
2026-01-07 15:57:24,900 - codomyrmex.logging_monitoring.logger_config - INFO - Logging configured: Level=INFO, OutputType=TEXT, File='Console', Format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
2026-01-07 15:57:24,900 - codomyrmex.documentation.documentation_website - INFO - Codomyrmex centralized logging initialized successfully via documentation_website.py.

Completed: 9 README.md files created, 9 AGENTS.md files created
```

### generate_missing_readmes.py

**Path**: `documentation/generate_missing_readmes.py`

```text
2026-01-07 15:57:25,577 - codomyrmex.logging_monitoring.logger_config - INFO - Logging configured: Level=INFO, OutputType=TEXT, File='Console', Format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
2026-01-07 15:57:25,577 - codomyrmex.documentation.documentation_website - INFO - Codomyrmex centralized logging initialized successfully via documentation_website.py.
usage: generate_missing_readmes.py [-h] [--repo-root REPO_ROOT] [--force]

Generate README.md files for directories with AGENTS.md

options:
  -h, --help            show this help message and exit
  --repo-root REPO_ROOT
                        Repository root directory
  --force               Overwrite existing README.md files
```

### generate_spec_files.py

**Path**: `documentation/generate_spec_files.py`

```text
2026-01-07 15:57:25,664 - codomyrmex.logging_monitoring.logger_config - INFO - Logging configured: Level=INFO, OutputType=TEXT, File='Console', Format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
2026-01-07 15:57:25,664 - codomyrmex.documentation.documentation_website - INFO - Codomyrmex centralized logging initialized successfully via documentation_website.py.

Completed: 9 SPEC.md files created, 593 already existed
```

### global_doc_auditor.py

**Path**: `documentation/global_doc_auditor.py`

```text
2026-01-07 15:57:25,771 - codomyrmex.logging_monitoring.logger_config - INFO - Logging configured: Level=INFO, OutputType=TEXT, File='Console', Format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
2026-01-07 15:57:25,771 - codomyrmex.documentation.documentation_website - INFO - Codomyrmex centralized logging initialized successfully via documentation_website.py.
```

### identify_docs_needing_work.py

**Path**: `documentation/identify_docs_needing_work.py`

```text
2026-01-07 15:57:25,839 - codomyrmex.logging_monitoring.logger_config - INFO - Logging configured: Level=INFO, OutputType=TEXT, File='Console', Format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
2026-01-07 15:57:25,839 - codomyrmex.documentation.documentation_website - INFO - Codomyrmex centralized logging initialized successfully via documentation_website.py.
Found 11 directories with documentation issues

SPEC.md with placeholder content: 9
Files with broken links: 2

Sample directories needing work:

output/script_logs/20260107_155204/ide:
  SPEC: Has placeholder content

output/script_logs/20260107_155204/encryption:
  SPEC: Has placeholder content

output/script_logs/20260107_155204/environment_setup:
  SPEC: Has placeholder content

output/script_logs/20260107_155204/fabric:
  SPEC: Has placeholder content

output/script_logs/20260107_155204/documents:
  SPEC: Has placeholder content

output/script_logs/20260107_155204/events:
  SPEC: Has placeholder content

output/script_logs/20260107_155204/ollama:
  SPEC: Has placeholder content

output/script_logs/20260107_155204/fpf:
  SPEC: Has placeholder content

output/script_logs/20260107_155204/git_operations:
  SPEC: Has placeholder content

src/codomyrmex/website:
  SPEC: Broken links: Reference Guides -> ../../docs/README.md

src/codomyrmex/agents/gemini:
  SPEC: Broken links: Reference Guides -> ../../docs/README.md
```

### module_docs_auditor.py

**Path**: `documentation/module_docs_auditor.py`

```text
Failed to get help text (Exit Code: 1)

Stderr:
Traceback (most recent call last):
  File "/Users/mini/Documents/GitHub/codomyrmex/scripts/documentation/module_docs_auditor.py", line 19, in <module>
    sys.exit(module_docs_auditor.main())
             ~~~~~~~~~~~~~~~~~~~~~~~~^^
  File "/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/documentation/scripts/module_docs_auditor.py", line 376, in main
    report_path.write_text(report, encoding='utf-8')
    ~~~~~~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/Users/mini/.local/share/uv/python/cpython-3.13.11-macos-aarch64-none/lib/python3.13/pathlib/_local.py", line 555, in write_text
    return PathBase.write_text(self, data, encoding, errors, newline)
           ~~~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/Users/mini/.local/share/uv/python/cpython-3.13.11-macos-aarch64-none/lib/python3.13/pathlib/_abc.py", line 651, in write_text
    with self.open(mode='w', encoding=encoding, errors=errors, newline=newline) as f:
         ~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/Users/mini/.local/share/uv/python/cpython-3.13.11-macos-aarch64-none/lib/python3.13/pathlib/_local.py", line 537, in open
    return io.open(self, mode, buffering, encoding, errors, newline)
           ~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
FileNotFoundError: [Errno 2] No such file or directory: '/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/docs/project/module-documentation-audit.md'
```

### monitor_health.py

**Path**: `documentation/monitor_health.py`

```text
2026-01-07 15:57:26,999 - codomyrmex.logging_monitoring.logger_config - INFO - Logging configured: Level=INFO, OutputType=TEXT, File='Console', Format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
2026-01-07 15:57:26,999 - codomyrmex.documentation.documentation_website - INFO - Codomyrmex centralized logging initialized successfully via documentation_website.py.
usage: monitor_health.py [-h] [--repo-root REPO_ROOT] [--output OUTPUT]

Monitor documentation health

options:
  -h, --help            show this help message and exit
  --repo-root REPO_ROOT
                        Repository root directory
  --output OUTPUT       Output directory
```

### orchestrate.py

**Path**: `documentation/orchestrate.py`

```text
2026-01-07 15:57:27,102 - codomyrmex.logging_monitoring.logger_config - INFO - Logging configured: Level=INFO, OutputType=TEXT, File='Console', Format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
2026-01-07 15:57:27,102 - codomyrmex.documentation.documentation_website - INFO - Codomyrmex centralized logging initialized successfully via documentation_website.py.
usage: orchestrate.py [-h] [--verbose]
                      {check-environment,build,dev-server,aggregate,assess} ...

Documentation Module operations

positional arguments:
  {check-environment,build,dev-server,aggregate,assess}
                        Available commands
    check-environment   Check documentation environment
    build               Build static documentation site
    dev-server          Start development server
    aggregate           Aggregate documentation
    assess              Assess documentation site

options:
  -h, --help            show this help message and exit
  --verbose, -v         Verbose output

Examples:
  orchestrate.py check-environment
  orchestrate.py build --output docs/build/
  orchestrate.py dev-server --port 3000
  orchestrate.py aggregate --source docs/ --output docs/aggregated/
  orchestrate.py assess --path docs/build/
```

### refine_generic_descriptions.py

**Path**: `documentation/refine_generic_descriptions.py`

```text
2026-01-07 15:57:27,158 - codomyrmex.logging_monitoring.logger_config - INFO - Logging configured: Level=INFO, OutputType=TEXT, File='Console', Format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
2026-01-07 15:57:27,158 - codomyrmex.documentation.documentation_website - INFO - Codomyrmex centralized logging initialized successfully via documentation_website.py.
```

### remove_missing_file_links.py

**Path**: `documentation/remove_missing_file_links.py`

```text
2026-01-07 15:57:27,216 - codomyrmex.logging_monitoring.logger_config - INFO - Logging configured: Level=INFO, OutputType=TEXT, File='Console', Format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
2026-01-07 15:57:27,216 - codomyrmex.documentation.documentation_website - INFO - Codomyrmex centralized logging initialized successfully via documentation_website.py.

Completed: Fixed 0 files with missing file links
```

### remove_nonexistent_spec_links.py

**Path**: `documentation/remove_nonexistent_spec_links.py`

```text
2026-01-07 15:57:27,292 - codomyrmex.logging_monitoring.logger_config - INFO - Logging configured: Level=INFO, OutputType=TEXT, File='Console', Format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
2026-01-07 15:57:27,292 - codomyrmex.documentation.documentation_website - INFO - Codomyrmex centralized logging initialized successfully via documentation_website.py.

Completed: Fixed 0 SPEC.md files
```

### remove_placeholders.py

**Path**: `documentation/remove_placeholders.py`

```text
2026-01-07 15:57:27,387 - codomyrmex.logging_monitoring.logger_config - INFO - Logging configured: Level=INFO, OutputType=TEXT, File='Console', Format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
2026-01-07 15:57:27,387 - codomyrmex.documentation.documentation_website - INFO - Codomyrmex centralized logging initialized successfully via documentation_website.py.

Updated 0 files
```

### smart_template_engine.py

**Path**: `documentation/smart_template_engine.py`

```text
2026-01-07 15:57:27,693 - codomyrmex.logging_monitoring.logger_config - INFO - Logging configured: Level=INFO, OutputType=TEXT, File='Console', Format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
2026-01-07 15:57:27,693 - codomyrmex.documentation.documentation_website - INFO - Codomyrmex centralized logging initialized successfully via documentation_website.py.
usage: smart_template_engine.py [-h] [--repo-root REPO_ROOT] --module MODULE
                                [--output OUTPUT] [--export-json]

Smart documentation template engine

options:
  -h, --help            show this help message and exit
  --repo-root REPO_ROOT
                        Repository root directory
  --module MODULE       Module file to analyze
  --output OUTPUT       Output directory for analysis
  --export-json         Export analysis as JSON
```

### validate_agents_structure.py

**Path**: `documentation/validate_agents_structure.py`

```text
2026-01-07 15:57:27,772 - codomyrmex.logging_monitoring.logger_config - INFO - Logging configured: Level=INFO, OutputType=TEXT, File='Console', Format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
2026-01-07 15:57:27,772 - codomyrmex.documentation.documentation_website - INFO - Codomyrmex centralized logging initialized successfully via documentation_website.py.
usage: validate_agents_structure.py [-h] [--repo-root REPO_ROOT]
                                    [--output OUTPUT]
                                    [--format {json,html,both}]
                                    [--fail-on-invalid]
                                    [--fix-script-orchestrators]

Validate AGENTS.md file structure

options:
  -h, --help            show this help message and exit
  --repo-root REPO_ROOT
                        Repository root directory
  --output OUTPUT       Output directory for results
  --format {json,html,both}
                        Output format
  --fail-on-invalid     Exit with error if any files are invalid
  --fix-script-orchestrators
                        Automatically fix AGENTS.md files for script
                        orchestrators
```

### validate_child_references.py

**Path**: `documentation/validate_child_references.py`

```text
2026-01-07 15:57:27,852 - codomyrmex.logging_monitoring.logger_config - INFO - Logging configured: Level=INFO, OutputType=TEXT, File='Console', Format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
2026-01-07 15:57:27,852 - codomyrmex.documentation.documentation_website - INFO - Codomyrmex centralized logging initialized successfully via documentation_website.py.
Validating 279 AGENTS.md files...

Validation complete!
  Total files: 279
  Files with issues: 0
  Total issues: 0

Results saved to: /Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/output/child_references_validation.json
```

### validate_code_examples.py

**Path**: `documentation/validate_code_examples.py`

```text
2026-01-07 15:57:28,155 - codomyrmex.logging_monitoring.logger_config - INFO - Logging configured: Level=INFO, OutputType=TEXT, File='Console', Format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
2026-01-07 15:57:28,155 - codomyrmex.documentation.documentation_website - INFO - Codomyrmex centralized logging initialized successfully via documentation_website.py.
Extracting and validating code examples from documentation...
================================================================================

Found 0 code examples
Valid syntax: 0
Invalid syntax: 0

Report saved to: /Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/@output/code_examples_validation_report.json
```

### validate_configs.py

**Path**: `documentation/validate_configs.py`

```text
2026-01-07 15:57:28,245 - codomyrmex.logging_monitoring.logger_config - INFO - Logging configured: Level=INFO, OutputType=TEXT, File='Console', Format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
2026-01-07 15:57:28,245 - codomyrmex.documentation.documentation_website - INFO - Codomyrmex centralized logging initialized successfully via documentation_website.py.
usage: validate_configs.py [-h] [--fix] [--verbose] [--output OUTPUT]

Validate Codomyrmex example configurations

options:
  -h, --help           show this help message and exit
  --fix                Attempt to fix common issues automatically
  --verbose, -v        Show detailed validation results
  --output, -o OUTPUT  Output file for validation report
```

### validate_documentation_links.py

**Path**: `documentation/validate_documentation_links.py`

```text
Failed to get help text (Exit Code: 1)

Stderr:
Traceback (most recent call last):
  File "/Users/mini/Documents/GitHub/codomyrmex/scripts/documentation/validate_documentation_links.py", line 19, in <module>
    sys.exit(validate_documentation_links.main())
             ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~^^
  File "/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/documentation/scripts/validate_documentation_links.py", line 57, in main
    for root, dirs, files in os.walk(base_path):
                             ^^
NameError: name 'os' is not defined. Did you forget to import 'os'?
```

### validate_links.py

**Path**: `documentation/validate_links.py`

```text
2026-01-07 15:57:28,455 - codomyrmex.logging_monitoring.logger_config - INFO - Logging configured: Level=INFO, OutputType=TEXT, File='Console', Format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
2026-01-07 15:57:28,455 - codomyrmex.documentation.documentation_website - INFO - Codomyrmex centralized logging initialized successfully via documentation_website.py.
Found 566 broken links in 558 files:

README.md:
  - [Parent](../README.md)
  - [src](../README.md)
  - [README](../../README.md)
ide/README.md:
  - [README](../../../README.md)
encryption/README.md:
  - [README](../../../README.md)
metrics/README.md:
  - [README](../../../README.md)
documentation/README.md:
  - [README](../../../README.md)
tools/README.md:
  - [README](../../../README.md)
llm/README.md:
  - [README](../../../README.md)
terminal_interface/README.md:
  - [README](../../../README.md)
pattern_matching/README.md:
  - [README](../../../README.md)
cache/README.md:
  - [README](../../../README.md)
security/README.md:
  - [README](../../../README.md)
auth/README.md:
  - [README](../../../README.md)
static_analysis/README.md:
  - [README](../../../README.md)
networking/README.md:
  - [README](../../../README.md)
serialization/README.md:
  - [README](../../../README.md)
website/README.md:
  - [README](../../../README.md)
tests/README.md:
  - [README](../../../README.md)
output/README.md:
  - [../../../README.md](../../../README.md)
  - [../../../SPEC.md](../../../SPEC.md)
containerization/README.md:
  - [README](../../../README.md)
environment_setup/README.md:
  - [README](../../../README.md)

... and 538 more files
```

### validate_links_comprehensive.py

**Path**: `documentation/validate_links_comprehensive.py`

```text
2026-01-07 15:57:29,697 - codomyrmex.logging_monitoring.logger_config - INFO - Logging configured: Level=INFO, OutputType=TEXT, File='Console', Format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
2026-01-07 15:57:29,697 - codomyrmex.documentation.documentation_website - INFO - Codomyrmex centralized logging initialized successfully via documentation_website.py.
usage: validate_links_comprehensive.py [-h] [--repo-root REPO_ROOT]
                                       [--output OUTPUT]
                                       [--format {json,html,both}]
                                       [--fail-on-broken]

Comprehensive link validation for documentation

options:
  -h, --help            show this help message and exit
  --repo-root REPO_ROOT
                        Repository root directory
  --output OUTPUT       Output directory for results
  --format {json,html,both}
                        Output format
  --fail-on-broken      Exit with error code if broken links found
```

### validate_module_docs.py

**Path**: `documentation/validate_module_docs.py`

```text
2026-01-07 15:57:30,065 - codomyrmex.logging_monitoring.logger_config - INFO - Logging configured: Level=INFO, OutputType=TEXT, File='Console', Format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
2026-01-07 15:57:30,066 - codomyrmex.documentation.documentation_website - INFO - Codomyrmex centralized logging initialized successfully via documentation_website.py.
================================================================================
Module Documentation Validator
================================================================================

Validating 0 modules...

✅ All modules pass validation!

================================================================================
Summary: 0 errors, 0 warnings
================================================================================
```

### verify_api_specs.py

**Path**: `documentation/verify_api_specs.py`

```text
Failed to get help text (Exit Code: 1)

Stderr:
Traceback (most recent call last):
  File "/Users/mini/Documents/GitHub/codomyrmex/scripts/documentation/verify_api_specs.py", line 19, in <module>
    sys.exit(verify_api_specs.main())
             ~~~~~~~~~~~~~~~~~~~~~^^
  File "/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/documentation/scripts/verify_api_specs.py", line 300, in main
    print(f"\nModules checked: {results['summary']['total_modules']}")
                                ~~~~~~~^^^^^^^^^^^
KeyError: 'summary'
```

### verify_module_docs.py

**Path**: `documentation/verify_module_docs.py`

```text
2026-01-07 15:57:30,329 - codomyrmex.logging_monitoring.logger_config - INFO - Logging configured: Level=INFO, OutputType=TEXT, File='Console', Format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
2026-01-07 15:57:30,330 - codomyrmex.documentation.documentation_website - INFO - Codomyrmex centralized logging initialized successfully via documentation_website.py.
```

---

## documents

### orchestrate.py

**Path**: `documents/orchestrate.py`

```text
2026-01-07 15:57:30,444 - codomyrmex.logging_monitoring.logger_config - INFO - Logging configured: Level=INFO, OutputType=TEXT, File='Console', Format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
usage: orchestrate.py [-h] [--verbose] {read,info} ...

Documents operations

positional arguments:
  {read,info}    Available commands
    read         Read a document
    info         Get module information

options:
  -h, --help     show this help message and exit
  --verbose, -v  Verbose output

Examples:
  orchestrate.py read --file document.md
  orchestrate.py info
```

---

## encryption

### orchestrate.py

**Path**: `encryption/orchestrate.py`

```text
2026-01-07 15:57:30,524 - codomyrmex.logging_monitoring.logger_config - INFO - Logging configured: Level=INFO, OutputType=TEXT, File='Console', Format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
usage: orchestrate.py [-h] [--verbose] {basic} ...

Encryption operations

positional arguments:
  {basic}        Available commands
    basic        Basic encryption operation

options:
  -h, --help     show this help message and exit
  --verbose, -v  Verbose output

Examples:
  orchestrate.py basic
```

---

## environment_setup

### orchestrate.py

**Path**: `environment_setup/orchestrate.py`

```text
2026-01-07 15:57:30,625 - codomyrmex.logging_monitoring.logger_config - INFO - Logging configured: Level=INFO, OutputType=TEXT, File='Console', Format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
usage: orchestrate.py [-h] [--verbose]
                      {check-dependencies,setup-env-vars,check-uv} ...

Environment Setup operations

positional arguments:
  {check-dependencies,setup-env-vars,check-uv}
                        Available commands
    check-dependencies  Check if all dependencies are installed
    setup-env-vars      Check and setup required environment variables
    check-uv            Check UV availability and environment

options:
  -h, --help            show this help message and exit
  --verbose, -v         Verbose output

Examples:
  orchestrate.py check-dependencies
  orchestrate.py setup-env-vars
  orchestrate.py check-uv
```

---

## events

### orchestrate.py

**Path**: `events/orchestrate.py`

```text
2026-01-07 15:57:30,804 - codomyrmex.logging_monitoring.logger_config - INFO - Logging configured: Level=INFO, OutputType=TEXT, File='Console', Format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
usage: orchestrate.py [-h] [--verbose] {publish} ...

Events operations

positional arguments:
  {publish}      Available commands
    publish      Publish an event

options:
  -h, --help     show this help message and exit
  --verbose, -v  Verbose output

Examples:
  orchestrate.py publish --event-type test.event --data '{"key": "value"}'
```

---

## fpf

### orchestrate.py

**Path**: `fpf/orchestrate.py`

```text
2026-01-07 15:57:31,989 - codomyrmex.logging_monitoring.logger_config - INFO - Logging configured: Level=INFO, OutputType=TEXT, File='Console', Format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
usage: orchestrate.py [-h] [--verbose] [--output OUTPUT] {info,pipeline} ...

FPF Orchestration operations

positional arguments:
  {info,pipeline}      Available commands
    info               Show FPF integration information
    pipeline           Run FPF processing pipeline

options:
  -h, --help           show this help message and exit
  --verbose, -v        Verbose output
  --output, -o OUTPUT  Output file path for JSON results

Examples:
  orchestrate.py info
  orchestrate.py pipeline FPF-Spec.md
  orchestrate.py pipeline ailev/FPF --fetch --output-dir ./fpf_output
```

---

## git_operations

### orchestrate.py

**Path**: `git_operations/orchestrate.py`

```text
2026-01-07 15:57:35,189 - codomyrmex.logging_monitoring.logger_config - INFO - Logging configured: Level=INFO, OutputType=TEXT, File='Console', Format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
usage: orchestrate.py [-h] [--verbose] [--dry-run]
                      {status,branch,add,commit,push,pull,clone,init,history,fetch,remote,config,cherry-pick,amend,check} ...

Git Operations

positional arguments:
  {status,branch,add,commit,push,pull,clone,init,history,fetch,remote,config,cherry-pick,amend,check}
                        Available commands
    status              Show git status
    branch              Branch operations
    add                 Add files to staging
    commit              Commit changes
    push                Push changes
    pull                Pull changes
    clone               Clone repository
    init                Initialize git repository
    history             Show commit history
    fetch               Fetch changes from remote
    remote              Remote operations
    config              Config operations
    cherry-pick         Cherry-pick a commit
    amend               Amend last commit
    check               Check git availability

options:
  -h, --help            show this help message and exit
  --verbose, -v         Verbose output
  --dry-run             Dry run mode (no changes)

Examples:
  orchestrate.py status
  orchestrate.py branch current
  orchestrate.py branch create feature/new-feature
  orchestrate.py branch switch main
  orchestrate.py add file1.py file2.py
  orchestrate.py commit -m "Add new feature"
  orchestrate.py push --branch main --remote origin
  orchestrate.py pull --remote origin --branch main
  orchestrate.py clone https://github.com/user/repo.git --destination ./repo
  orchestrate.py init --path .
  orchestrate.py history --limit 10
  orchestrate.py check
```

### visualization_demo.py

**Path**: `git_operations/visualization_demo.py`

```text
2026-01-07 15:57:37,232 - codomyrmex.logging_monitoring.logger_config - INFO - Logging configured: Level=INFO, OutputType=TEXT, File='Console', Format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
usage: visualization_demo.py [-h] [--output-dir OUTPUT_DIR] [--skip-sample]
                             [--skip-workflows]
                             [repository_path]

Comprehensive Git Visualization Demo

positional arguments:
  repository_path       Path to Git repository to analyze

options:
  -h, --help            show this help message and exit
  --output-dir OUTPUT_DIR
                        Output directory for demo files
  --skip-sample         Skip sample data demonstrations
  --skip-workflows      Skip workflow diagram demonstrations
```

---

## ide

### antigravity_session.py

**Path**: `ide/antigravity_session.py`

```text
usage: antigravity_session.py [-h] [--list-conversations] [--list-artifacts]
                              [--get-artifact NAME] [--stats] [--tools]
                              [--invoke TOOL] [--params PARAMS] [--json]
                              [--limit LIMIT]

Manage Antigravity IDE sessions

options:
  -h, --help            show this help message and exit
  --list-conversations, -lc
                        List recent conversations
  --list-artifacts, -la
                        List artifacts in current conversation
  --get-artifact, -ga NAME
                        Get a specific artifact by name
  --stats, -s           Show session statistics
  --tools, -t           Show available tools
  --invoke, -i TOOL     Invoke a specific tool
  --params, -p PARAMS   JSON parameters for tool invocation
  --json, -j            Output as JSON
  --limit LIMIT         Limit for list operations
```

### ide_status.py

**Path**: `ide/ide_status.py`

```text
usage: ide_status.py [-h] [-v] [-j]

Check IDE connection status

options:
  -h, --help     show this help message and exit
  -v, --verbose  Include detailed capability information
  -j, --json     Output as JSON
```

### orchestrate.py

**Path**: `ide/orchestrate.py`

```text
usage: orchestrate.py [-h] {status,antigravity,ag,cursor,vscode,vsc} ...

IDE Integration Orchestrator

positional arguments:
  {status,antigravity,ag,cursor,vscode,vsc}
                        Command
    status              Show all IDE status
    antigravity (ag)    Antigravity commands
    cursor              Cursor commands
    vscode (vsc)        VS Code commands

options:
  -h, --help            show this help message and exit
```

---

## llm

### code_improvement_workflow.py

**Path**: `llm/fabric/code_improvement_workflow.py`

```text
🔧 Code Improvement Workflow Starting...

🔍 Analyzing code quality...

👃 Finding code smells...

📊 Workflow Results: 0/2 patterns successful
```

### content_analysis_workflow.py

**Path**: `llm/fabric/content_analysis_workflow.py`

```text
📄 Content Analysis Workflow Starting...

🔍 Extracting key insights...

📋 Creating summary...

📊 Workflow Results: 0/2 patterns successful
```

### demo_env_setup.py

**Path**: `llm/fabric/demo_env_setup.py`

```text
🎯 FABRIC ENVIRONMENT SETUP DEMO
========================================

The setup_fabric_env.py script provides interactive configuration for:
  🔑 API Keys (OpenAI, Anthropic, OpenRouter, Google)
  🤖 Model selection and vendor preferences
  ⚙️ Fabric configuration settings
  🌐 OpenRouter integration (multi-model access)
  🧪 Automatic testing with real API calls

Features:
  • Interactive prompts with sensible defaults
  • Secure password masking for API keys
  • Automatic .env file creation in correct location
  • Real-time testing and validation
  • OpenRouter integration for cost-effective access

📭 No existing Fabric environment found
   Will create: /Users/mini/.config/fabric/.env
🌐 OPENROUTER INTEGRATION BENEFITS
-----------------------------------

OpenRouter provides unified access to multiple AI providers:
  • 💰 Cost-effective access to premium models
  • 🔄 Automatic fallback between providers
  • 📊 Usage tracking and cost monitoring
  • 🚀 Access to latest models from multiple providers
  • 🔑 Single API key for multiple AI services

Popular OpenRouter models for code analysis:
  • openai/gpt-4o-mini (fast, cost-effective)
  • anthropic/claude-3-haiku (excellent for code)
  • google/gemini-1.5-flash (multimodal capabilities)
  • meta-llama/llama-3.1-8b-instruct (open source)


📖 USAGE EXAMPLES AFTER SETUP
-----------------------------------

1. 🚀 Run the interactive setup:
   python3 setup_fabric_env.py

2. 🧪 Test Fabric with simple commands:
   echo 'Hello world' | fabric --pattern summarize
   echo 'Python is great' | fabric --pattern extract_wisdom

3. 📋 List available patterns:
   fabric --listpatterns

4. 🤖 Use with orchestrator:
   python3 fabric_orchestrator.py
   python3 content_analysis_workflow.py

5. 💡 Advanced usage with OpenRouter:
   # Access multiple models through OpenRouter
   fabric --model openai/gpt-4o-mini --pattern analyze_code < myfile.py
   fabric --model anthropic/claude-3-haiku --pattern summarize < article.txt

🎬 DEMO SUMMARY
---------------
✅ Interactive environment setup script created
✅ OpenRouter integration included
✅ Automatic testing and validation
✅ Secure API key handling
✅ Integration with existing Fabric orchestrators

🚀 Ready to run: python3 setup_fabric_env.py
```

### fabric_config_manager.py

**Path**: `llm/fabric/fabric_config_manager.py`

```text
Failed to get help text (Exit Code: 1)

Stderr:
  File "/Users/mini/Documents/GitHub/codomyrmex/scripts/llm/fabric/fabric_config_manager.py", line 26
    """Manages Fabric configuration and integration settings."""
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
IndentationError: expected an indented block after class definition on line 25
```

### fabric_orchestrator.py

**Path**: `llm/fabric/fabric_orchestrator.py`

```text
Failed to get help text (Exit Code: 1)

Stderr:
```

### orchestrate.py

**Path**: `llm/fabric/orchestrate.py`

```text
2026-01-07 15:57:39,247 - codomyrmex.logging_monitoring.logger_config - INFO - Logging configured: Level=INFO, OutputType=TEXT, File='Console', Format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
usage: orchestrate.py [-h] [--verbose] [--output OUTPUT] {info} ...

Fabric Integration operations

positional arguments:
  {info}               Available commands
    info               Show integration information

options:
  -h, --help           show this help message and exit
  --verbose, -v        Verbose output
  --output, -o OUTPUT  Output file path for JSON results

Examples:
  orchestrate.py info
  orchestrate.py info --output info.json --verbose
```

### setup_fabric_env.py

**Path**: `llm/fabric/setup_fabric_env.py`

```text
============================================================
🔧 FABRIC ENVIRONMENT INTERACTIVE SETUP
============================================================
This script will help you configure Fabric with your API keys
and demonstrate functionality with a real API call.

⚠️  Non-interactive environment detected. Skipping interactive setup.
   Set FABRIC_FORCE_INTERACTIVE=1 to force interactive mode.
```

### analyze_model_tracking.py

**Path**: `llm/ollama/analyze_model_tracking.py`

```text
Analyzing output/ollama_verification...
Analyzing examples/output/ollama/outputs...

================================================================================
OLLAMA MODEL TRACKING VERIFICATION REPORT
================================================================================
Generated: 2026-01-07 15:57:39

SUMMARY
--------------------------------------------------------------------------------
Total output files analyzed: 0
Total mismatches found: 0
Tracking accuracy: 0.0%

================================================================================
DIRECTORY: output/ollama_verification
================================================================================
Files found: 0
Mismatches: 0

MODELS USED:
--------------------------------------------------------------------------------

✅ All files have matching model names in filename and content

================================================================================
DIRECTORY: examples/output/ollama/outputs
================================================================================
Files found: 0
Mismatches: 0

MODELS USED:
--------------------------------------------------------------------------------

✅ All files have matching model names in filename and content

================================================================================
VERIFICATION SCRIPT RESULTS
================================================================================
Model used in verification: smollm2:135m-instruct-q4_K_S
All tests passed successfully
Output saved to: output/ollama_verification/

================================================================================
MODEL-TO-OUTPUT MAPPING
================================================================================

================================================================================
END OF REPORT
================================================================================

✅ Report saved to: /Users/mini/Documents/GitHub/codomyrmex/output/ollama/ollama_model_tracking_report.txt
✅ JSON data saved to: /Users/mini/Documents/GitHub/codomyrmex/output/ollama/ollama_model_tracking_report.json
```

### basic_usage.py

**Path**: `llm/ollama/basic_usage.py`

```text
Timed out getting help text
```

### integration_demo.py

**Path**: `llm/ollama/integration_demo.py`

```text
Timed out getting help text
```

### model_management.py

**Path**: `llm/ollama/model_management.py`

```text
Timed out getting help text
```

### orchestrate.py

**Path**: `llm/ollama/orchestrate.py`

```text
2026-01-07 15:57:54,605 - codomyrmex.logging_monitoring.logger_config - INFO - Logging configured: Level=INFO, OutputType=TEXT, File='Console', Format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
usage: orchestrate.py [-h] [--verbose] [--output OUTPUT] {info} ...

Ollama Integration operations

positional arguments:
  {info}               Available commands
    info               Show integration information

options:
  -h, --help           show this help message and exit
  --verbose, -v        Verbose output
  --output, -o OUTPUT  Output file path for JSON results

Examples:
  orchestrate.py info
  orchestrate.py info --output info.json --verbose
```

### test_all_parameters_rnj.py

**Path**: `llm/ollama/test_all_parameters_rnj.py`

```text
Timed out getting help text
```

### test_configuration_patterns.py

**Path**: `llm/ollama/test_configuration_patterns.py`

```text
Timed out getting help text
```

### test_error_scenarios.py

**Path**: `llm/ollama/test_error_scenarios.py`

```text
Timed out getting help text
```

### test_nemotron.py

**Path**: `llm/ollama/test_nemotron.py`

```text
Timed out getting help text
```

### test_usage_patterns.py

**Path**: `llm/ollama/test_usage_patterns.py`

```text
Timed out getting help text
```

### verify_integration.py

**Path**: `llm/ollama/verify_integration.py`

```text
Timed out getting help text
```

---

## logging_monitoring

### orchestrate.py

**Path**: `logging_monitoring/orchestrate.py`

```text
2026-01-07 15:58:26,278 - codomyrmex.logging_monitoring.logger_config - INFO - Logging configured: Level=INFO, OutputType=TEXT, File='Console', Format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
usage: orchestrate.py [-h] [--verbose] {test-logging,info} ...

Logging Monitoring operations

positional arguments:
  {test-logging,info}  Available commands
    test-logging       Test logging functionality
    info               Show module information

options:
  -h, --help           show this help message and exit
  --verbose, -v        Verbose output

Examples:
  orchestrate.py test-logging
  orchestrate.py info
```

---

## logistics

### orchestrate.py

**Path**: `logistics/orchestrate.py`

```text
Timed out getting help text
```

---

## metrics

### orchestrate.py

**Path**: `metrics/orchestrate.py`

```text
2026-01-07 15:58:32,799 - codomyrmex.logging_monitoring.logger_config - INFO - Logging configured: Level=INFO, OutputType=TEXT, File='Console', Format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
usage: orchestrate.py [-h] [--verbose] {info} ...

Metrics operations

positional arguments:
  {info}         Available commands
    info         Get metrics module information

options:
  -h, --help     show this help message and exit
  --verbose, -v  Verbose output

Examples:
  orchestrate.py info
```

---

## model_context_protocol

### orchestrate.py

**Path**: `model_context_protocol/orchestrate.py`

```text
2026-01-07 15:58:34,664 - codomyrmex.logging_monitoring.logger_config - INFO - Logging configured: Level=INFO, OutputType=TEXT, File='Console', Format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
usage: orchestrate.py [-h] [--verbose] [--output OUTPUT] {info,list-tools} ...

Model Context Protocol operations

positional arguments:
  {info,list-tools}    Available commands
    info               Show module information
    list-tools         List available MCP tools

options:
  -h, --help           show this help message and exit
  --verbose, -v        Verbose output
  --output, -o OUTPUT  Output file path for JSON results

Examples:
  orchestrate.py info
  orchestrate.py list-tools --output tools.json --verbose
```

---

## module_template

### async_template.py

**Path**: `module_template/_templates/async_template.py`

```text
Failed to get help text (Exit Code: 1)

Stderr:
  File "/Users/mini/Documents/GitHub/codomyrmex/scripts/module_template/_templates/async_template.py", line 31
    from codomyrmex.{module} import (
                    ^
SyntaxError: invalid syntax
```

### basic_template.py

**Path**: `module_template/_templates/basic_template.py`

```text
Failed to get help text (Exit Code: 1)

Stderr:
  File "/Users/mini/Documents/GitHub/codomyrmex/scripts/module_template/_templates/basic_template.py", line 26
    from codomyrmex.{module} import (
                    ^
SyntaxError: invalid syntax
```

### integration_template.py

**Path**: `module_template/_templates/integration_template.py`

```text
Failed to get help text (Exit Code: 1)

Stderr:
  File "/Users/mini/Documents/GitHub/codomyrmex/scripts/module_template/_templates/integration_template.py", line 31
    from codomyrmex.{module1} import (
                    ^
SyntaxError: invalid syntax
```

### tutorial_template.py

**Path**: `module_template/_templates/tutorial_template.py`

```text
Failed to get help text (Exit Code: 1)

Stderr:
  File "/Users/mini/Documents/GitHub/codomyrmex/scripts/module_template/_templates/tutorial_template.py", line 27
    from codomyrmex.{module} import {TestedFunction}
                    ^
SyntaxError: invalid syntax
```

### orchestrate.py

**Path**: `module_template/orchestrate.py`

```text
2026-01-07 15:58:36,356 - codomyrmex.logging_monitoring.logger_config - INFO - Logging configured: Level=INFO, OutputType=TEXT, File='Console', Format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
usage: orchestrate.py [-h] [--verbose] {info} ...

Template operations

positional arguments:
  {info}         Available commands
    info         Get template module information

options:
  -h, --help     show this help message and exit
  --verbose, -v  Verbose output

Examples:
  orchestrate.py info
```

---

## networking

### orchestrate.py

**Path**: `networking/orchestrate.py`

```text
2026-01-07 15:58:37,729 - codomyrmex.logging_monitoring.logger_config - INFO - Logging configured: Level=INFO, OutputType=TEXT, File='Console', Format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
usage: orchestrate.py [-h] [--verbose] {info} ...

Networking operations

positional arguments:
  {info}         Available commands
    info         Get networking module information

options:
  -h, --help     show this help message and exit
  --verbose, -v  Verbose output

Examples:
  orchestrate.py info
```

---

## pattern_matching

### orchestrate.py

**Path**: `pattern_matching/orchestrate.py`

```text
Timed out getting help text
```

---

## performance

### orchestrate.py

**Path**: `performance/orchestrate.py`

```text
2026-01-07 15:58:43,429 - codomyrmex.logging_monitoring.logger_config - INFO - Logging configured: Level=INFO, OutputType=TEXT, File='Console', Format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
usage: orchestrate.py [-h] [--verbose] {monitor-stats,cache-info} ...

Performance operations

positional arguments:
  {monitor-stats,cache-info}
                        Available commands
    monitor-stats       Get performance monitor statistics
    cache-info          Get cache manager information

options:
  -h, --help            show this help message and exit
  --verbose, -v         Verbose output

Examples:
  orchestrate.py monitor-stats
  orchestrate.py cache-info
```

---

## physical_management

### orchestrate.py

**Path**: `physical_management/orchestrate.py`

```text
2026-01-07 15:58:43,552 - codomyrmex.logging_monitoring.logger_config - INFO - Logging configured: Level=INFO, OutputType=TEXT, File='Console', Format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
usage: orchestrate.py [-h] [--verbose] [--output OUTPUT] {info} ...

Physical Management operations

positional arguments:
  {info}               Available commands
    info               Show module information

options:
  -h, --help           show this help message and exit
  --verbose, -v        Verbose output
  --output, -o OUTPUT  Output file path for JSON results

Examples:
  orchestrate.py info
  orchestrate.py info --output info.json --verbose
```

---

## plugin_system

### orchestrate.py

**Path**: `plugin_system/orchestrate.py`

```text
2026-01-07 15:58:43,822 - codomyrmex.logging_monitoring.logger_config - INFO - Logging configured: Level=INFO, OutputType=TEXT, File='Console', Format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
usage: orchestrate.py [-h] [--verbose] {load} ...

Plugin System operations

positional arguments:
  {load}         Available commands
    load         Load a plugin

options:
  -h, --help     show this help message and exit
  --verbose, -v  Verbose output

Examples:
  orchestrate.py load --path plugin.py
```

---

## scrape

### orchestrate.py

**Path**: `scrape/orchestrate.py`

```text
2026-01-07 15:58:43,991 - codomyrmex.logging_monitoring.logger_config - INFO - Logging configured: Level=INFO, OutputType=TEXT, File='Console', Format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
usage: orchestrate.py [-h] [--verbose] {info,scrape,crawl} ...

Scrape operations - web scraping with Firecrawl integration

positional arguments:
  {info,scrape,crawl}  Available commands
    info               Get scrape module information
    scrape             Scrape a single URL
    crawl              Crawl a website from a starting URL

options:
  -h, --help           show this help message and exit
  --verbose, -v        Verbose output

Examples:
  orchestrate.py info
  orchestrate.py scrape https://example.com
  orchestrate.py scrape https://example.com --save --output-dir output/scrape
  orchestrate.py scrape https://example.com --format html --save
  orchestrate.py crawl https://example.com --limit 10 --save
```

### scrape_gemini_docs.py

**Path**: `scrape/scrape_gemini_docs.py`

```text
Timed out getting help text
```

---

## security

### orchestrate.py

**Path**: `security/orchestrate.py`

```text
2026-01-07 15:58:51,563 - codomyrmex.logging_monitoring.logger_config - INFO - Logging configured: Level=INFO, OutputType=TEXT, File='Console', Format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
usage: orchestrate.py [-h] [--verbose]
                      {scan-vulnerabilities,audit-code,check-compliance,generate-report} ...

Security operations

positional arguments:
  {scan-vulnerabilities,audit-code,check-compliance,generate-report}
                        Available commands
    scan-vulnerabilities
                        Scan for vulnerabilities
    audit-code          Audit code security
    check-compliance    Check compliance
    generate-report     Generate security report

options:
  -h, --help            show this help message and exit
  --verbose, -v         Verbose output

Examples:
  orchestrate.py scan-vulnerabilities --path src/
  orchestrate.py audit-code --path src/
  orchestrate.py check-compliance --path src/ --standard OWASP
  orchestrate.py generate-report --path src/ --output security_report.json
```

---

## serialization

### orchestrate.py

**Path**: `serialization/orchestrate.py`

```text
2026-01-07 15:58:53,279 - codomyrmex.logging_monitoring.logger_config - INFO - Logging configured: Level=INFO, OutputType=TEXT, File='Console', Format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
usage: orchestrate.py [-h] [--verbose] {info} ...

Serialization operations

positional arguments:
  {info}         Available commands
    info         Get serialization module information

options:
  -h, --help     show this help message and exit
  --verbose, -v  Verbose output

Examples:
  orchestrate.py info
```

---

## skills

### orchestrate.py

**Path**: `skills/orchestrate.py`

```text
Timed out getting help text
```

---

## spatial

### orchestrate.py

**Path**: `spatial/modeling_3d/orchestrate.py`

```text
Failed to get help text (Exit Code: 1)

Stderr:
Traceback (most recent call last):
  File "/Users/mini/Documents/GitHub/codomyrmex/scripts/spatial/modeling_3d/orchestrate.py", line 23, in <module>
    from _orchestrator_utils import (
    ...<6 lines>...
    )
ModuleNotFoundError: No module named '_orchestrator_utils'

During handling of the above exception, another exception occurred:

Traceback (most recent call last):
  File "/Users/mini/Documents/GitHub/codomyrmex/scripts/spatial/modeling_3d/orchestrate.py", line 34, in <module>
    from _orchestrator_utils import (
    ...<6 lines>...
    )
ModuleNotFoundError: No module named '_orchestrator_utils'
```

### orchestrate.py

**Path**: `spatial/orchestrate.py`

```text
2026-01-07 15:58:59,402 - codomyrmex.logging_monitoring.logger_config - INFO - Logging configured: Level=INFO, OutputType=TEXT, File='Console', Format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
usage: orchestrate.py [-h] [--verbose] {info} ...

Spatial modeling and visualization operations

positional arguments:
  {info}         Available commands
    info         Get spatial module information

options:
  -h, --help     show this help message and exit
  --verbose, -v  Verbose output

Examples:
  orchestrate.py info
```

---

## static_analysis

### orchestrate.py

**Path**: `static_analysis/orchestrate.py`

```text
2026-01-07 15:58:59,788 - codomyrmex.logging_monitoring.logger_config - INFO - Logging configured: Level=INFO, OutputType=TEXT, File='Console', Format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
usage: orchestrate.py [-h] [--dry-run] [--format {json,text}] [--verbose]
                      [--quiet]
                      {analyze-file,analyze-project,list-tools} ...

Static Analysis operations

positional arguments:
  {analyze-file,analyze-project,list-tools}
                        Available commands
    analyze-file        Analyze a single file
    analyze-project     Analyze an entire project
    list-tools          List available analysis tools

options:
  -h, --help            show this help message and exit
  --dry-run             Show what would be executed without actually running
                        commands
  --format {json,text}  Output format (default: text)
  --verbose, -v         Enable verbose output
  --quiet, -q           Suppress non-error output

Examples:
  orchestrate.py analyze-file file.py --output results.json
  orchestrate.py analyze-project . --output analysis_report.json --dry-run
  orchestrate.py list-tools --format json
  orchestrate.py analyze-file file.py --verbose
```

---

## system_discovery

### orchestrate.py

**Path**: `system_discovery/orchestrate.py`

```text
2026-01-07 15:58:59,910 - codomyrmex.logging_monitoring.logger_config - INFO - Logging configured: Level=INFO, OutputType=TEXT, File='Console', Format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
usage: orchestrate.py [-h] [--verbose] {status,scan,discover} ...

System Discovery operations

positional arguments:
  {status,scan,discover}
                        Available commands
    status              Generate system status report
    scan                Scan system capabilities
    discover            Discover system components

options:
  -h, --help            show this help message and exit
  --verbose, -v         Verbose output

Examples:
  orchestrate.py status
  orchestrate.py scan
  orchestrate.py discover
```

---

## templating

### orchestrate.py

**Path**: `templating/orchestrate.py`

```text
2026-01-07 15:59:00,038 - codomyrmex.logging_monitoring.logger_config - INFO - Logging configured: Level=INFO, OutputType=TEXT, File='Console', Format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
usage: orchestrate.py [-h] [--verbose] {basic} ...

Templating operations

positional arguments:
  {basic}        Available commands
    basic        Basic templating operation

options:
  -h, --help     show this help message and exit
  --verbose, -v  Verbose output

Examples:
  orchestrate.py basic
```

---

## terminal_interface

### orchestrate.py

**Path**: `terminal_interface/orchestrate.py`

```text
2026-01-07 15:59:00,194 - codomyrmex.logging_monitoring.logger_config - INFO - Logging configured: Level=INFO, OutputType=TEXT, File='Console', Format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
usage: orchestrate.py [-h] [--verbose] {shell,format} ...

Terminal Interface operations

positional arguments:
  {shell,format}  Available commands
    shell         Launch interactive shell
    format        Test terminal formatting

options:
  -h, --help      show this help message and exit
  --verbose, -v   Verbose output

Examples:
  orchestrate.py shell
  orchestrate.py format
  orchestrate.py shell --verbose
  orchestrate.py format --verbose
```

---

## tools

### config_loader.py

**Path**: `tools/_common/config_loader.py`

```text

```

### example_runner.py

**Path**: `tools/_common/example_runner.py`

```text

```

### utils.py

**Path**: `tools/_common/utils.py`

```text

```

### add_logging.py

**Path**: `tools/add_logging.py`

```text
Failed to get help text (Exit Code: 1)

Stderr:
  File "/Users/mini/Documents/GitHub/codomyrmex/scripts/tools/add_logging.py", line 159
    print("
          ^
SyntaxError: unterminated string literal (detected at line 159)
```

### analyze_todos.py

**Path**: `tools/analyze_todos.py`

```text
Timed out getting help text
```

### audit_error_handling.py

**Path**: `tools/audit_error_handling.py`

```text
Auditing error handling patterns across codebase...
================================================================================

Analyzed 663 Python files
Found 0 error handling patterns

Pattern Summary:

Non-standard patterns found: 0

Report saved to: /Users/mini/Documents/GitHub/codomyrmex/@output/error_handling_audit_report.json
```

### audit_methods.py

**Path**: `tools/audit_methods.py`

```text
Total Issues Found: 0
```

### check_dependencies.py

**Path**: `tools/check_dependencies.py`

```text
Failed to get help text (Exit Code: 1)

Stderr:
Traceback (most recent call last):
  File "/Users/mini/Documents/GitHub/codomyrmex/scripts/tools/check_dependencies.py", line 15, in <module>
    from dependency_analyzer import DependencyAnalyzer
ModuleNotFoundError: No module named 'dependency_analyzer'
```

### check_version_pinning.py

**Path**: `tools/check_version_pinning.py`

```text
Failed to get help text (Exit Code: 1)

Stderr:
```

### cleanup_docs.py

**Path**: `tools/cleanup_docs.py`

```text
Updated scripts/AGENTS.md
Updated scripts/README.md
Docs cleanup complete.
```

### doc_maintenance.py

**Path**: `tools/doc_maintenance.py`

```text
Total files updated: 0
```

### doc_maintenance_v3.py

**Path**: `tools/doc_maintenance_v3.py`

```text
Total files updated: 0
```

### enhance_documentation.py

**Path**: `tools/enhance_documentation.py`

```text
usage: enhance_documentation.py [-h] [--path PATH] [--recursive] [--dry-run]
                                [--file FILE]

Enhance Python documentation with docstrings

options:
  -h, --help   show this help message and exit
  --path PATH  Path to process
  --recursive  Process subdirectories
  --dry-run    Show what would be changed
  --file FILE  Process a single file
```

### example_usage.py

**Path**: `tools/example_usage.py`

```text
Timed out getting help text
```

### fix_imports.py

**Path**: `tools/fix_imports.py`

```text
Failed to get help text (Exit Code: 1)

Stderr:
  File "/Users/mini/Documents/GitHub/codomyrmex/scripts/tools/fix_imports.py", line 263
    print("
          ^
SyntaxError: unterminated string literal (detected at line 263)
```

### fix_imports_simple.py

**Path**: `tools/fix_imports_simple.py`

```text
usage: fix_imports_simple.py [-h] [--path PATH] [--recursive] [--dry-run]
                             [--file FILE]

Sort and organize import statements

options:
  -h, --help   show this help message and exit
  --path PATH  Path to process
  --recursive  Process subdirectories
  --dry-run    Show what would be changed
  --file FILE  Process a single file
```

### fix_syntax_errors.py

**Path**: `tools/fix_syntax_errors.py`

```text
usage: fix_syntax_errors.py [-h] [--path PATH] [--recursive] [--dry-run]
                            [--file FILE]

Fix syntax errors in Python files

options:
  -h, --help   show this help message and exit
  --path PATH  Path to process
  --recursive  Process subdirectories
  --dry-run    Show what would be changed
  --file FILE  Process a single file
```

### generate_coverage_report.py

**Path**: `tools/generate_coverage_report.py`

```text
Failed to get help text (Exit Code: 1)

Stderr:
```

### orchestrate.py

**Path**: `tools/orchestrate.py`

```text
2026-01-07 15:59:20,065 - codomyrmex.logging_monitoring.logger_config - INFO - Logging configured: Level=INFO, OutputType=TEXT, File='Console', Format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
usage: orchestrate.py [-h] [--verbose]
                      {analyze-structure,analyze-dependencies} ...

Tools operations

positional arguments:
  {analyze-structure,analyze-dependencies}
                        Available commands
    analyze-structure   Analyze project structure
    analyze-dependencies
                        Analyze project dependencies

options:
  -h, --help            show this help message and exit
  --verbose, -v         Verbose output

Examples:
  orchestrate.py analyze-structure --path src/
  orchestrate.py analyze-dependencies --path src/
```

### pin_dependency_versions.py

**Path**: `tools/pin_dependency_versions.py`

```text
usage: pin_dependency_versions.py [-h] [--dry-run] [--apply] [files ...]

Pin dependency versions in requirements.txt files

positional arguments:
  files       Specific requirements.txt files to process (default: all)

options:
  -h, --help  show this help message and exit
  --dry-run   Show what would be changed without modifying files (default)
  --apply     Actually apply the changes to files
```

### run_quality_checks.py

**Path**: `tools/run_quality_checks.py`

```text
Timed out getting help text
```

### security_audit.py

**Path**: `tools/security_audit.py`

```text
Timed out getting help text
```

---

## utils

### orchestrate.py

**Path**: `utils/orchestrate.py`

```text
Utils module orchestrator
========================================
Utils module loaded: codomyrmex.utils
```

---

## validation

### orchestrate.py

**Path**: `validation/orchestrate.py`

```text
2026-01-07 15:59:33,460 - codomyrmex.logging_monitoring.logger_config - INFO - Logging configured: Level=INFO, OutputType=TEXT, File='Console', Format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
usage: orchestrate.py [-h] [--verbose] {info} ...

Validation operations

positional arguments:
  {info}         Available commands
    info         Get validation module information

options:
  -h, --help     show this help message and exit
  --verbose, -v  Verbose output

Examples:
  orchestrate.py info
```

### validate_examples.py

**Path**: `validation/validate_examples.py`

```text
usage: validate_examples.py [-h] [--parallel PARALLEL]
                            [--output-dir OUTPUT_DIR] [--types TYPES]
                            [--modules MODULES] [--verbose] [--fix]

Comprehensive validation script for Codomyrmex examples

options:
  -h, --help            show this help message and exit
  --parallel, -p PARALLEL
                        Number of parallel processes (default: 4)
  --output-dir, -o OUTPUT_DIR
                        Output directory for reports
  --types, -t TYPES     Comma-separated validation types
  --modules, -m MODULES
                        Specific modules to validate
  --verbose, -v         Enable verbose output
  --fix                 Attempt to fix common issues automatically
```

---

## website

### generate.py

**Path**: `website/generate.py`

```text
usage: generate.py [-h] [--output-dir OUTPUT_DIR] [--serve] [--open]
                   [--port PORT] [--max-port-attempts MAX_PORT_ATTEMPTS]

Generate and optionally serve the Codomyrmex website.

options:
  -h, --help            show this help message and exit
  --output-dir OUTPUT_DIR
                        Directory to write the generated website to.
  --serve               Serve the website after generation.
  --open                Open the website in the default browser (implies
                        --serve).
  --port PORT           Preferred port to serve on (default: 8000). Will auto-
                        discover if in use.
  --max-port-attempts MAX_PORT_ATTEMPTS
                        Maximum number of ports to try if preferred port is in
                        use (default: 10).
```

### serve.py

**Path**: `website/serve.py`

```text
usage: serve.py [-h] [--directory DIRECTORY] [--port PORT]

Serve the Codomyrmex website.

options:
  -h, --help            show this help message and exit
  --directory, -d DIRECTORY
                        Directory containing the website to serve.
  --port, -p PORT       Port to serve on.
```

---


## Navigation Links

- **Parent**: [Project Overview](../README.md)
- **Module Index**: [All Agents](../../AGENTS.md)
- **Documentation**: [Reference Guides](../docs/README.md)
- **Home**: [Root README](../../../README.md)
