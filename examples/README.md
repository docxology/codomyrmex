# Codomyrmex Examples

## Signposting
- **Parent**: [Parent](../README.md)
- **Children**:
    - [_common](_common/README.md)
    - [_configs](_configs/README.md)
    - [_templates](_templates/README.md)
    - [ai_code_editing](ai_code_editing/README.md)
    - [api_documentation](api_documentation/README.md)
    - [api_standardization](api_standardization/README.md)
    - [build_synthesis](build_synthesis/README.md)
    - [ci_cd_automation](ci_cd_automation/README.md)
    - [code_execution_sandbox](code_execution_sandbox/README.md)
    - [code_review](code_review/README.md)
    - [config_management](config_management/README.md)
    - [containerization](containerization/README.md)
    - [data_visualization](data_visualization/README.md)
    - [database_management](database_management/README.md)
    - [documentation](documentation/README.md)
    - [environment_setup](environment_setup/README.md)
    - [events](events/README.md)
    - [git_operations](git_operations/README.md)
    - [language_models](language_models/README.md)
    - [logging_monitoring](logging_monitoring/README.md)
    - [model_context_protocol](model_context_protocol/README.md)
    - [modeling_3d](modeling_3d/README.md)
    - [multi_module](multi_module/README.md)
    - [ollama_integration](ollama_integration/README.md)
    - [output](output/README.md)
    - [pattern_matching](pattern_matching/README.md)
    - [performance](performance/README.md)
    - [physical_management](physical_management/README.md)
    - [plugin_system](plugin_system/README.md)
    - [project_orchestration](project_orchestration/README.md)
    - [security_audit](security_audit/README.md)
    - [static_analysis](static_analysis/README.md)
    - [system_discovery](system_discovery/README.md)
    - [terminal_interface](terminal_interface/README.md)
    - [validation_reports](validation_reports/README.md)
- **Key Artifacts**:
    - [Agent Guide](AGENTS.md)
    - [Functional Spec](SPEC.md)

**Version**: v0.2.0 | **Status**: Active | **Last Updated**: December 2025

## Overview

This directory contains runnable examples demonstrating all Codomyrmex modules and their integration. All examples are config-driven, reference tested methods from unit tests, and follow modular patterns for easy understanding and extension.

## Directory Structure

```
examples/
├── README.md                     # This file
├── AGENTS.md                     # Agent coordination document
├── _common/                      # Shared utilities
│   ├── config_loader.py          # YAML/JSON config loading
│   ├── example_runner.py         # Standardized execution framework
│   └── utils.py                  # Common helper functions
├── {module_name}/                # One folder per module
│   ├── README.md                 # Module-specific documentation
│   ├── example_basic.py          # Basic usage example
│   ├── config.yaml               # YAML configuration
│   └── config.json               # JSON configuration
└── multi_module/                 # Multi-module workflows
    ├── README.md
    ├── example_workflow_*.py     # Integration workflows
    ├── config_workflow_*.yaml    # Workflow configurations
    └── config_workflow_*.json    # Alternative JSON configs
```

## Quick Start

### Running Individual Module Examples

```bash
# Navigate to a module example
cd examples/logging_monitoring

# Run the basic example
python example_basic.py

# With custom configuration
python example_basic.py --config my_config.yaml
```

### Running Multi-Module Workflows

```bash
# Navigate to multi-module examples
cd examples/multi_module

# Run an integration workflow
python example_workflow_analysis.py
```

## Available Examples

### Foundation Layer ✅

Core infrastructure modules used throughout Codomyrmex:

- **[logging_monitoring/](logging_monitoring)** - Centralized logging and monitoring ✅
- **[environment_setup/](environment_setup)** - Environment validation and setup ✅
- **[model_context_protocol/](model_context_protocol)** - AI communication standards ✅
- **[terminal_interface/](terminal_interface)** - Rich terminal UI ✅

### Core Layer ✅

Primary development capabilities:

- **[ai_code_editing/](ai_code_editing)** - AI-powered code generation ✅
- **[static_analysis/](static_analysis)** - Code quality analysis ✅
- **[code_execution_sandbox/](code_execution_sandbox)** - Safe code execution ✅
- **[data_visualization/](data_visualization)** - Charts and visualizations ✅
- **[pattern_matching/](pattern_matching)** - Code pattern analysis ✅
- **[git_operations/](git_operations)** - Version control automation ✅
- **[code_review/](code_review)** - Automated code review ✅
- **[security_audit/](security_audit)** - Security scanning ✅

### Service Layer ✅

Higher-level orchestration and services:

- **[build_synthesis/](build_synthesis)** - Build automation ✅
- **[documentation/](documentation)** - Documentation generation ✅
- **[api_documentation/](api_documentation)** - API docs generation ✅
- **[ci_cd_automation/](ci_cd_automation)** - CI/CD pipelines ✅
- **[database_management/](database_management)** - Database operations ✅
- **[containerization/](containerization)** - Container management ✅
- **[config_management/](config_management)** - Configuration management ✅
- **[project_orchestration/](project_orchestration)** - Workflow orchestration ✅

### Specialized Layer

Domain-specific capabilities:

- **[modeling_3d/](modeling_3d)** - 3D modeling and visualization ✅
- **[physical_management/](physical_management)** - Hardware management ✅
- **[system_discovery/](system_discovery)** - System exploration ✅
- **[performance/](performance)** - Performance monitoring ✅
- **[ollama_integration/](ollama_integration)** - Local LLM integration ✅
- **[language_models/](language_models)** - LLM infrastructure ✅

### New Modules

Recently added modules:

- **[plugin_system/](plugin_system)** - Plugin architecture ✅
- **[events/](events)** - Event-driven communication ✅
- **[api_standardization/](api_standardization)** - API standards ✅

### Multi-Module Workflows ✅

Real-world integration examples:

- **[example_workflow_analysis.py](multi_module/example_workflow_analysis.py)** - Static analysis + security + visualization ✅
- **[example_workflow_development.py](multi_module/example_workflow_development.py)** - AI editing + review + git + analysis ✅
- **[example_workflow_monitoring.py](multi_module/example_workflow_monitoring.py)** - Logging + performance + discovery ✅
- **[example_workflow_build.py](multi_module/example_workflow_build.py)** - Build + CI/CD + containerization ✅
- **[example_workflow_api.py](multi_module/example_workflow_api.py)** - API + docs + database ✅

## Configuration

All examples support both YAML and JSON configuration files:

### YAML Configuration (config.yaml)

```yaml
# Module-specific settings
module:
  setting1: value1
  setting2: value2

# Output settings
output:
  format: json
  file: output/results.json

# Logging
logging:
  level: INFO
  file: logs/example.log
```

### JSON Configuration (config.json)

```json
{
  "module": {
    "setting1": "value1",
    "setting2": "value2"
  },
  "output": {
    "format": "json",
    "file": "output/results.json"
  },
  "logging": {
    "level": "INFO",
    "file": "logs/example.log"
  }
}
```

### Environment Variable Substitution

Configuration files support environment variable substitution:

```yaml
api_key: ${API_KEY}
database_url: ${DATABASE_URL:default_value}
```

## Common Utilities

The `_common/` directory provides shared utilities:

- **config_loader.py** - Load YAML/JSON configs with environment variable substitution
- **example_runner.py** - Standardized example execution with logging and error handling
- **utils.py** - Helper functions for paths, formatting, and validation

Usage in examples:

```python
from examples._common.config_loader import load_config
from examples._common.example_runner import ExampleRunner

config = load_config(Path(__file__).parent / "config.yaml")
runner = ExampleRunner(__file__, config)
```

## Example Template

Each example follows this structure:

```python
#!/usr/bin/env python3
"""
Example: {Module Name} - {Description}

Demonstrates:
- Feature 1
- Feature 2

Tested Methods:
- method_name() - Verified in test_{module}.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from codomyrmex.{module} import {TestedFunction}
from examples._common.config_loader import load_config
from examples._common.example_runner import ExampleRunner

def main():
    config = load_config(Path(__file__).parent / "config.yaml")
    runner = ExampleRunner(__file__, config)
    runner.start()
    
    try:
        # Example implementation
        results = {...}
        
        runner.validate_results(results)
        runner.save_results(results)
        runner.complete()
    except Exception as e:
        runner.error("Example failed", e)
        sys.exit(1)

if __name__ == "__main__":
    main()
```

## Testing Integration

All examples reference tested methods from unit tests:

- Each example documents which test file verifies the methods used
- Method signatures match those in unit tests
- Examples demonstrate the same patterns as tests
- Configuration options align with test parameters

Example reference:

```python
"""
Tested Methods:
- setup_logging() - Verified in test_logging_monitoring.py::TestLoggingMonitoring::test_setup_logging
- get_logger(name) - Verified in test_logging_monitoring.py::TestLoggingMonitoring::test_get_logger
"""
```

## Output

Examples generate consistent output:

- **Results**: JSON files in `output/{module_name}_results.json`
- **Logs**: Log files in `logs/{example_name}.log`
- **Visualizations**: Images in `output/{module_name}/`
- **Reports**: Generated reports in `output/`

## Best Practices

1. **Always use configuration files** - Never hard-code values
2. **Reference tested methods** - Ensure examples use verified code
3. **Include error handling** - All examples should handle failures gracefully
4. **Document clearly** - Explain what the example demonstrates
5. **Keep it modular** - Examples should be self-contained
6. **Follow the template** - Maintain consistency across examples

## Contributing Examples

To add a new example:

1. Create a directory: `examples/{module_name}/`
2. Add files:
   - `example_basic.py` - Basic usage example
   - `config.yaml` - YAML configuration
   - `config.json` - JSON configuration
   - `README.md` - Module-specific documentation
3. Follow the example template structure
4. Reference tested methods from unit tests
5. Test the example thoroughly
6. Update this README

## Related Documentation

- **[Main Documentation](../docs/)** - Complete Codomyrmex documentation
- **[Source Modules](../src/codomyrmex/)** - Module implementations
- **[Unit Tests](../testing/unit/)** - Test suite
- **[Integration Tests](../testing/integration/)** - Integration tests
- **[AGENTS.md](AGENTS.md)** - Agent coordination for examples
- **[COMPLETE_INVENTORY.md](COMPLETE_INVENTORY.md)** - Full inventory of all examples

## Navigation

- **Human Documentation**: [README.md](README.md)
- **Technical Documentation**: [AGENTS.md](AGENTS.md)
- **Functional Specification**: [SPEC.md](SPEC.md)
- **Parent Directory**: [Root](../README.md)
- **Repository Root**: [../README.md](../README.md)
- **Repository SPEC**: [../SPEC.md](../SPEC.md)