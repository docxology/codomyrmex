# src

## Signposting
- **Parent**: [Root](../README.md)
- **Children**:
    - [codomyrmex](codomyrmex/README.md) - Main package
    - [template](template/README.md) - Scaffolding templates
- **Related**:
    - [Tests](../testing/README.md)
    - [Docs](../docs/README.md)

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: December 2025

## Overview

This is the source code coordination document for the core Codomyrmex platform implementation. It defines the modular source code architecture that provides all platform capabilities through independent, well-tested modules.

The src directory contains the Python package implementation with module system, API interfaces, and agent coordination capabilities.

## Package Architecture

```mermaid
graph TB
    subgraph "Source Code Structure"
        SRC[src/]
        CODOMYRMEX[src/codomyrmex/]
        TEMPLATE[src/template/]
    end

    subgraph "Core Package Components"
        INIT[src/__init__.py]
        CLI[src/codomyrmex/cli.py]
        EXCEPTIONS[src/codomyrmex/exceptions.py]
    end

    subgraph "Foundation Layer<br/>(Base Services)"
        LOG[logging_monitoring<br/>Centralized logging]
        ENV[environment_setup<br/>Environment validation]
        MCP[model_context_protocol<br/>AI communication]
        TERM[terminal_interface<br/>Rich terminal UI]
    end

    subgraph "Core Layer<br/>(Primary Capabilities)"
        AI[ai_code_editing<br/>AI code assistance]
        STATIC[static_analysis<br/>Code quality analysis]
        SANDBOX[code_execution_sandbox<br/>Safe code execution]
        VIZ[data_visualization<br/>Charts and plots]
        PATTERN[pattern_matching<br/>Code pattern analysis]
        GIT[git_operations<br/>Version control automation]
    end

    subgraph "Service Layer<br/>(Orchestration & Deployment)"
        BUILD[build_synthesis<br/>Build automation]
        DOCS[documentation<br/>Doc generation]
        API[api_documentation<br/>API specifications]
        CICD[ci_cd_automation<br/>CI/CD pipelines]
        CONTAINER[containerization<br/>Container management]
        DB[database_management<br/>Database operations]
        CONFIG[config_management<br/>Configuration handling]
        ORCHESTRATION[project_orchestration<br/>Workflow orchestration]
    end

    subgraph "Specialized Layer<br/>(Domain-Specific)"
        MODELING[modeling_3d<br/>3D visualization]
        PHYSICAL[physical_management<br/>Hardware management]
        DISCOVERY[system_discovery<br/>Module discovery]
        PERF[performance<br/>Performance monitoring]
        OLLAMA[ollama_integration<br/>Local LLM integration]
        LANG[language_models<br/>LLM infrastructure]
        SECURITY[security_audit<br/>Security scanning]
        REVIEW[code_review<br/>Automated code review]
    end

    SRC --> INIT
    SRC --> CODOMYRMEX
    SRC --> TEMPLATE

    CODOMYRMEX --> CLI
    CODOMYRMEX --> EXCEPTIONS

    CODOMYRMEX --> LOG
    CODOMYRMEX --> ENV
    CODOMYRMEX --> MCP
    CODOMYRMEX --> TERM

    LOG --> AI
    ENV --> AI
    MCP --> AI
    TERM --> AI

    LOG --> STATIC
    LOG --> SANDBOX
    LOG --> VIZ
    LOG --> PATTERN
    LOG --> GIT

    AI --> BUILD
    STATIC --> BUILD
    GIT --> BUILD
    VIZ --> DOCS

    BUILD --> CICD
    DOCS --> CICD
    CONTAINER --> CICD
    CONFIG --> CICD

    AI --> MODELING
    VIZ --> MODELING

    STATIC --> SECURITY
    SECURITY --> REVIEW
```

## Module System Architecture

```mermaid
graph TD
    subgraph "Module Structure"
        MODULE_DIR[module_name/]
        INIT_PY[__init__.py]
        CORE_PY[core.py]
        UTILS_PY[utils.py]
        CONFIG_PY[config.py]
        EXCEPTIONS_PY[exceptions.py]
    end

    subgraph "Module Documentation"
        README_MD[README.md]
        API_SPEC[API_SPECIFICATION.md]
        USAGE_EXAMPLES[USAGE_EXAMPLES.md]
        MCP_SPEC[MCP_TOOL_SPECIFICATION.md]
        SECURITY_MD[SECURITY.md]
        CHANGELOG[CHANGELOG.md]
    end

    subgraph "Module Testing"
        TESTS_DIR[tests/]
        UNIT_TESTS[unit/]
        INTEGRATION_TESTS[integration/]
        REQUIREMENTS[requirements.txt]
    end

    MODULE_DIR --> INIT_PY
    MODULE_DIR --> CORE_PY
    MODULE_DIR --> UTILS_PY
    MODULE_DIR --> CONFIG_PY
    MODULE_DIR --> EXCEPTIONS_PY

    MODULE_DIR --> README_MD
    MODULE_DIR --> API_SPEC
    MODULE_DIR --> USAGE_EXAMPLES
    MODULE_DIR --> MCP_SPEC
    MODULE_DIR --> SECURITY_MD
    MODULE_DIR --> CHANGELOG

    MODULE_DIR --> TESTS_DIR
    TESTS_DIR --> UNIT_TESTS
    TESTS_DIR --> INTEGRATION_TESTS
    MODULE_DIR --> REQUIREMENTS
```

## Module Dependency Flow

```mermaid
graph TD
    subgraph "Foundation Layer"
        LOGGING[logging_monitoring]
        ENV[environment_setup]
        MCP[model_context_protocol]
        TERMINAL[terminal_interface]
    end

    subgraph "Core Layer"
        AI_EDITING[ai_code_editing]
        STATIC_ANALYSIS[static_analysis]
        CODE_EXEC[code_execution_sandbox]
        DATA_VIZ[data_visualization]
        PATTERN_MATCH[pattern_matching]
        GIT_OPS[git_operations]
        CODE_REVIEW[code_review]
        SECURITY_AUDIT[security_audit]
        OLLAMA[ollama_integration]
        LANG_MODELS[language_models]
        PERFORMANCE[performance]
    end

    subgraph "Service Layer"
        BUILD_SYNTHESIS[build_synthesis]
        DOCUMENTATION[documentation]
        API_DOCS[api_documentation]
        CI_CD[ci_cd_automation]
        CONTAINER[containerization]
        DATABASE[database_management]
        CONFIG_MGMT[config_management]
        PROJECT_ORCHESTRATION[project_orchestration]
    end

    subgraph "Specialized Layer"
        MODELING_3D[modeling_3d]
        PHYSICAL_MGMT[physical_management]
        SYSTEM_DISCOVERY[system_discovery]
        MODULE_TEMPLATE[module_template]
    end

    %% Foundation dependencies (all modules depend on foundation)
    AI_EDITING -.-> LOGGING
    STATIC_ANALYSIS -.-> LOGGING
    CODE_EXEC -.-> LOGGING
    DATA_VIZ -.-> LOGGING
    PATTERN_MATCH -.-> LOGGING
    GIT_OPS -.-> LOGGING
    CODE_REVIEW -.-> LOGGING
    SECURITY_AUDIT -.-> LOGGING
    OLLAMA -.-> LOGGING
    LANG_MODELS -.-> LOGGING
    PERFORMANCE -.-> LOGGING
    BUILD_SYNTHESIS -.-> LOGGING
    DOCUMENTATION -.-> LOGGING
    API_DOCS -.-> LOGGING
    CI_CD -.-> LOGGING
    CONTAINER -.-> LOGGING
    DATABASE -.-> LOGGING
    CONFIG_MGMT -.-> LOGGING
    PROJECT_ORCHESTRATION -.-> LOGGING
    MODELING_3D -.-> LOGGING
    PHYSICAL_MGMT -.-> LOGGING
    SYSTEM_DISCOVERY -.-> LOGGING
    MODULE_TEMPLATE -.-> LOGGING

    AI_EDITING -.-> ENV
    STATIC_ANALYSIS -.-> ENV
    CODE_EXEC -.-> ENV
    DATA_VIZ -.-> ENV
    PATTERN_MATCH -.-> ENV
    GIT_OPS -.-> ENV
    CODE_REVIEW -.-> ENV
    SECURITY_AUDIT -.-> ENV
    OLLAMA -.-> ENV
    LANG_MODELS -.-> ENV
    PERFORMANCE -.-> ENV
    BUILD_SYNTHESIS -.-> ENV
    DOCUMENTATION -.-> ENV
    API_DOCS -.-> ENV
    CI_CD -.-> ENV
    CONTAINER -.-> ENV
    DATABASE -.-> ENV
    CONFIG_MGMT -.-> ENV
    PROJECT_ORCHESTRATION -.-> ENV
    MODELING_3D -.-> ENV
    PHYSICAL_MGMT -.-> ENV
    SYSTEM_DISCOVERY -.-> ENV
    MODULE_TEMPLATE -.-> ENV

    AI_EDITING -.-> MCP
    AI_EDITING -.-> TERMINAL

    %% Core layer interconnections
    AI_EDITING --> CODE_EXEC
    AI_EDITING --> PATTERN_MATCH
    STATIC_ANALYSIS --> PATTERN_MATCH
    STATIC_ANALYSIS --> CODE_REVIEW
    BUILD_SYNTHESIS --> STATIC_ANALYSIS
    BUILD_SYNTHESIS --> GIT_OPS
    CODE_REVIEW --> STATIC_ANALYSIS
    CI_CD --> BUILD_SYNTHESIS
    CI_CD --> SECURITY_AUDIT
    CONTAINER --> PHYSICAL_MGMT
    PROJECT_ORCHESTRATION --> BUILD_SYNTHESIS
    PROJECT_ORCHESTRATION --> DOCUMENTATION

    %% Service layer connections
    DATA_VIZ --> MODELING_3D
    DATABASE --> BUILD_SYNTHESIS
    CONFIG_MGMT -.-> ENV
```

## Code Quality Assurance

```mermaid
flowchart TD
    subgraph "Code Quality Pipeline"
        CODE[New Code] --> LINTING[Linting<br/>ruff, pylint]
        LINTING --> TYPE_CHECK[Type Checking<br/>mypy]
        TYPE_CHECK --> UNIT_TESTS[Unit Tests<br/>pytest]
        UNIT_TESTS --> INTEGRATION[Integration Tests<br/>pytest]
        INTEGRATION --> COVERAGE[Coverage Analysis<br/>pytest-cov]
        COVERAGE --> SECURITY[Security Scanning<br/>bandit, safety]
        SECURITY --> PERFORMANCE[Performance Benchmarking<br/>Custom benchmarks]
    end

    subgraph "Quality Gates"
        LINTING -->|Fail| FIX_CODE[Fix Code Issues]
        TYPE_CHECK -->|Fail| FIX_CODE
        UNIT_TESTS -->|Fail| FIX_TESTS[Fix Tests]
        INTEGRATION -->|Fail| FIX_INTEGRATION[Fix Integration]
        COVERAGE -->|Fail| IMPROVE_COVERAGE[Improve Coverage]
        SECURITY -->|Fail| FIX_SECURITY[Fix Security Issues]
        PERFORMANCE -->|Fail| OPTIMIZE[Optimize Performance]
    end

    subgraph "Success Path"
        PERFORMANCE -->|Pass| CODE_REVIEW[Code Review]
        CODE_REVIEW --> MERGE[Merge to Main]
        MERGE --> DEPLOY[Deploy]
    end

    FIX_CODE --> CODE
    FIX_TESTS --> UNIT_TESTS
    FIX_INTEGRATION --> INTEGRATION
    IMPROVE_COVERAGE --> UNIT_TESTS
    FIX_SECURITY --> SECURITY
    OPTIMIZE --> PERFORMANCE
```

## Directory Contents
- `__init__.py` – Package initialization and public API exports
- `codomyrmex/` – Main package with 30+ specialized modules
- `template/` – Code generation templates and scaffolding

## Module Maturity Overview

```mermaid
pie title Module Development Status (December 2025)
    "Production Ready" : 12
    "Beta" : 8
    "Alpha" : 6
    "Planning" : 4
```

| Maturity Level | Description | Module Count | Examples |
|----------------|-------------|--------------|----------|
| **Production Ready** | Fully tested, stable APIs, production use | 12 | logging_monitoring, environment_setup, terminal_interface |
| **Beta** | Core functionality complete, API stabilization | 8 | ai_code_editing, static_analysis, code_execution_sandbox |
| **Alpha** | Basic functionality, APIs may change | 6 | modeling_3d, physical_management, system_discovery |
| **Planning** | Requirements gathering, initial design | 4 | Future specialized modules |

## Testing Architecture

```mermaid
graph TD
    subgraph "Testing Pyramid"
        UNIT[Unit Tests<br/>30+ modules<br/>80%+ coverage]
        INTEGRATION[Integration Tests<br/>Cross-module<br/>End-to-end workflows]
        SYSTEM[System Tests<br/>Full platform<br/>Real deployments]
    end

    subgraph "Test Infrastructure"
        PYTEST[pytest<br/>Test runner]
        COVERAGE[coverage.py<br/>Coverage analysis]
        MOCKS[unittest.mock<br/>Mocking utilities]
        FIXTURES[pytest fixtures<br/>Test data setup]
    end

    subgraph "Test Categories"
        FUNCTIONAL[Functional Tests<br/>API validation]
        PERFORMANCE[Performance Tests<br/>Benchmarking]
        SECURITY[Security Tests<br/>Vulnerability checks]
        REGRESSION[Regression Tests<br/>Bug prevention]
    end

    UNIT --> PYTEST
    INTEGRATION --> PYTEST
    SYSTEM --> PYTEST

    PYTEST --> COVERAGE
    PYTEST --> MOCKS
    PYTEST --> FIXTURES

    UNIT --> FUNCTIONAL
    INTEGRATION --> PERFORMANCE
    SYSTEM --> SECURITY
    ALL_TESTS --> REGRESSION
```

## Package Distribution

```mermaid
graph TD
    subgraph "Development Installation"
        DEV_SETUP[uv sync<br/>Development environment]
        DEV_DEPS[Install dev dependencies<br/>Testing, linting, docs]
        DEV_VERIFY[Verify installation<br/>Import tests, basic functionality]
    end

    subgraph "Production Installation"
        PROD_BUILD[Build distribution<br/>python -m build]
        PROD_UPLOAD[Upload to PyPI<br/>twine upload]
        PROD_INSTALL[pip install codomyrmex<br/>Production deployment]
    end

    subgraph "Optional Dependencies"
        AI_DEPS[AI features<br/>openai, anthropic, ollama]
        VIZ_DEPS[Visualization<br/>matplotlib, plotly, seaborn]
        CLOUD_DEPS[Cloud integration<br/>boto3, google-cloud, azure]
        DEV_DEPS_GROUP[Development tools<br/>black, ruff, mypy]
    end

    DEV_SETUP --> DEV_DEPS
    DEV_DEPS --> DEV_VERIFY

    PROD_BUILD --> PROD_UPLOAD
    PROD_UPLOAD --> PROD_INSTALL

    DEV_DEPS --> AI_DEPS
    DEV_DEPS --> VIZ_DEPS
    DEV_DEPS --> CLOUD_DEPS
    PROD_INSTALL --> AI_DEPS
    PROD_INSTALL --> VIZ_DEPS
    PROD_INSTALL --> CLOUD_DEPS
```

## Navigation
- **Technical Documentation**: [AGENTS.md](AGENTS.md)
- **Functional Specification**: [SPEC.md](SPEC.md)
- **Project Root**: [README](../README.md)
- **Package Documentation**: [src/codomyrmex/README.md](codomyrmex/README.md)
- **API Reference**: [docs/reference/api.md](../docs/reference/api.md)
- **Testing**: [testing/README.md](../testing/README.md)
