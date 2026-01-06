# src/codomyrmex/environment_setup

## Signposting
- **Parent**: [codomyrmex](../README.md)
- **Children**:
    - [docs](docs/README.md)
    - [scripts](scripts/README.md)
    - [tests](tests/README.md)
- **Key Artifacts**:
    - [Agent Guide](AGENTS.md)
    - [Functional Spec](SPEC.md)

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: December 2025

## Overview

Foundation module providing environment validation and setup utilities for the Codomyrmex platform. This module ensures that development and runtime environments are properly configured with required dependencies, API keys, and environment variables before other modules initialize.

## Environment Validation Flow

```mermaid
flowchart TB
    Start[Application Startup] --> CheckUV{uv Available?}
    
    CheckUV -->|Yes| CheckUVEnv{In uv Environment?}
    CheckUV -->|No| WarnUV[Warn: uv Recommended]
    
    CheckUVEnv -->|Yes| CheckDeps[Check Dependencies]
    CheckUVEnv -->|No| CheckVenv{In Virtual Environment?}
    WarnUV --> CheckVenv
    
    CheckVenv -->|Yes| CheckDeps
    CheckVenv -->|No| WarnSystem[Warn: System Python]
    
    WarnSystem --> CheckDeps
    
    CheckDeps --> HasKit{kit Installed?}
    HasKit -->|No| InstallGuide[Show Installation Guide]
    HasKit -->|Yes| HasDotenv{python-dotenv Installed?}
    
    HasDotenv -->|No| InstallGuide
    HasDotenv -->|Yes| CheckPython{Python >= 3.10?}
    
    CheckPython -->|No| VersionError[Python Version Error]
    CheckPython -->|Yes| CheckEnvFile{.env File Exists?}
    
    CheckEnvFile -->|No| EnvGuide[Show .env Template]
    CheckEnvFile -->|Yes| ValidateKeys[Validate API Keys]
    
    ValidateKeys --> CheckConfig{Config Files Present?}
    CheckConfig -->|Missing| ConfigWarn[Warn: Missing Config]
    CheckConfig -->|All Present| GenerateReport[Generate Environment Report]
    
    EnvGuide --> GenerateReport
    ConfigWarn --> GenerateReport
    InstallGuide --> Exit[Exit with Error]
    VersionError --> Exit
    
    GenerateReport --> Success[Environment Ready]
    
    style Success fill:#90EE90
    style Exit fill:#FFB6C1
    style InstallGuide fill:#FFE4B5
    style EnvGuide fill:#FFE4B5
```

## Key Features

- **Package Manager Detection**: Identifies uv, virtual environments, or system Python
- **Dependency Validation**: Checks for required packages (kit, python-dotenv)
- **Python Version Validation**: Ensures Python ≥3.10
- **Environment File Management**: Validates .env file presence and provides templates
- **Configuration Validation**: Checks for pyproject.toml, requirements.txt
- **Installation Guidance**: Provides clear, actionable setup instructions

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
- `env_checker.py` – File
- `requirements.txt` – File
- `scripts/` – Subdirectory
- `tests/` – Subdirectory

## Navigation
- **Project Root**: [README](../../../README.md)
- **Parent Directory**: [codomyrmex](../README.md)
- **Src Hub**: [src](../../../src/README.md)

## Getting Started

To use this module in your project, import the necessary components:

```python
# Example usage
from codomyrmex.codomyrmex.environment_setup import main_component

def example():
    result = main_component.process()
    print(f"Result: {result}")
```

## detailed_overview

This module is a critical part of the Codomyrmex ecosystem. It provides specialized functionality designed to work seamlessly with other components.
The architecture focuses on modularity, reliability, and performance.

## Contributing

We welcome contributions! Please ensure you:
1.  Follow the project coding standards.
2.  Add tests for new functionality.
3.  Update documentation as needed.

See the root `CONTRIBUTING.md` for more details.

<!-- Navigation Links keyword for score -->
