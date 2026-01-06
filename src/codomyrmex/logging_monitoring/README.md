# src/codomyrmex/logging_monitoring

## Signposting
- **Parent**: [Parent](../README.md)
- **Children**:
    - [docs](docs/README.md)
    - [tests](tests/README.md)
- **Key Artifacts**:
    - [Agent Guide](AGENTS.md)
    - [Functional Spec](SPEC.md)

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: December 2025

## Overview

Foundation module providing centralized logging infrastructure for the Codomyrmex platform. This module implements a unified logging system that ensures consistent log formatting, configurable output destinations, and proper log level management across all platform components.

The logging_monitoring module serves as the backbone for observability, enabling debugging, monitoring, and troubleshooting throughout the entire Codomyrmex ecosystem.

## Directory Contents
- `.cursor/` – Subdirectory
- `.gitignore` – File
- `API_SPECIFICATION.md` – File
- `CHANGELOG.md` – File
- `MCP_TOOL_SPECIFICATION.md` – File
- `SECURITY.md` – File
- `USAGE_EXAMPLES.md` – File
- `__init__.py` – File
- `docs/` – Subdirectory
- `logger_config.py` – File
- `requirements.txt` – File
- `tests/` – Subdirectory

## Architecture

### Logging System Architecture

```mermaid
graph TB
    subgraph "Configuration Layer"
        EnvVars["Environment Variables<br/>CODOMYRMEX_LOG_*"]
        ConfigFile["Configuration File<br/>(Optional)"]
    end

    subgraph "Core Logging System"
        SetupFunc["setup_logging()<br/>Initialization"]
        LoggerFactory["get_logger(name)<br/>Factory Function"]
        LogContext["LogContext<br/>Structured Context"]
    end

    subgraph "Output Layer"
        ConsoleHandler["Console Handler<br/>Terminal Output"]
        FileHandler["File Handler<br/>Persistent Logs"]
        JSONFormatter["JSON Formatter<br/>Structured Data"]
        TextFormatter["Text Formatter<br/>Human Readable"]
    end

    subgraph "Integration Layer"
        Modules["Codomyrmex Modules<br/>Consistent Logging"]
        Monitoring["Monitoring Systems<br/>Log Aggregation"]
        Debugging["Debug & Troubleshooting<br/>Contextual Info"]
    end

    %% Configuration flow
    EnvVars --> SetupFunc
    ConfigFile --> SetupFunc

    %% Core system flow
    SetupFunc --> LoggerFactory
    LoggerFactory --> LogContext

    %% Output configuration
    SetupFunc --> ConsoleHandler
    SetupFunc --> FileHandler

    ConsoleHandler --> JSONFormatter
    ConsoleHandler --> TextFormatter
    FileHandler --> JSONFormatter
    FileHandler --> TextFormatter

    %% Integration
    LogContext --> Modules
    JSONFormatter --> Monitoring
    TextFormatter --> Debugging
```

### Logger Hierarchy and Flow

```mermaid
graph TD
    RootLogger["Root Logger<br/>(codomyrmex)"] --> FoundationLogger["Foundation Layer<br/>logging_monitoring<br/>environment_setup<br/>model_context_protocol<br/>terminal_interface"]

    RootLogger --> CoreLogger["Core Layer<br/>ai_code_editing<br/>static_analysis<br/>code_execution_sandbox<br/>data_visualization<br/>pattern_matching<br/>git_operations"]

    FoundationLogger --> CoreLogger

    CoreLogger --> ServiceLogger["Service Layer<br/>build_synthesis<br/>documentation<br/>ci_cd_automation<br/>containerization<br/>project_orchestration"]

    ServiceLogger --> SpecializedLogger["Specialized Layer<br/>system_discovery<br/>module_template<br/>modeling_3d"]

    %% Log levels
    subgraph "Log Levels"
        DEBUG["DEBUG<br/>Detailed debugging"]
        INFO["INFO<br/>General information"]
        WARNING["WARNING<br/>Potential issues"]
        ERROR["ERROR<br/>Errors occurred"]
        CRITICAL["CRITICAL<br/>System failures"]
    end

    %% Formatters
    subgraph "Output Formats"
        JSONFmt["JSON Format<br/>Machine readable<br/>Structured data"]
        TextFmt["Text Format<br/>Human readable<br/>Contextual info"]
    end

    CoreLogger -.-> DEBUG
    CoreLogger -.-> INFO
    CoreLogger -.-> WARNING
    CoreLogger -.-> ERROR
    CoreLogger -.-> CRITICAL

    DEBUG -.-> JSONFmt
    INFO -.-> JSONFmt
    WARNING -.-> TextFmt
    ERROR -.-> TextFmt
    CRITICAL -.-> TextFmt
```

## Navigation
- **Project Root**: [README](../../../README.md)
- **Parent Directory**: [codomyrmex](../README.md)
- **Src Hub**: [src](../../../src/README.md)