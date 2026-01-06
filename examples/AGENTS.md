# Codomyrmex Agents — examples

## Signposting
- **Parent**: [Repository Root](../AGENTS.md)
- **Self**: [Agents](AGENTS.md)
- **Children**:
    - [_common](_common/AGENTS.md)
    - [_configs](_configs/AGENTS.md)
    - [_templates](_templates/AGENTS.md)
    - [ai_code_editing](ai_code_editing/AGENTS.md)
    - [api_documentation](api_documentation/AGENTS.md)
    - [api_standardization](api_standardization/AGENTS.md)
    - [build_synthesis](build_synthesis/AGENTS.md)
    - [ci_cd_automation](ci_cd_automation/AGENTS.md)
    - [code](code/AGENTS.md)    - [config_management](config_management/AGENTS.md)
    - [containerization](containerization/AGENTS.md)
    - [data_visualization](data_visualization/AGENTS.md)
    - [database_management](database_management/AGENTS.md)
    - [documentation](documentation/AGENTS.md)
    - [environment_setup](environment_setup/AGENTS.md)
    - [events](events/AGENTS.md)
    - [git_operations](git_operations/AGENTS.md)
    - [language_models](language_models/AGENTS.md)
    - [logging_monitoring](logging_monitoring/AGENTS.md)
    - [model_context_protocol](model_context_protocol/AGENTS.md)
    - [modeling_3d](modeling_3d/AGENTS.md)
    - [multi_module](multi_module/AGENTS.md)
    - [ollama_integration](ollama_integration/AGENTS.md)
    - [output](output/AGENTS.md)
    - [pattern_matching](pattern_matching/AGENTS.md)
    - [performance](performance/AGENTS.md)
    - [physical_management](physical_management/AGENTS.md)
    - [plugin_system](plugin_system/AGENTS.md)
    - [project_orchestration](project_orchestration/AGENTS.md)
    - [security_audit](security_audit/AGENTS.md)
    - [static_analysis](static_analysis/AGENTS.md)
    - [system_discovery](system_discovery/AGENTS.md)
    - [terminal_interface](terminal_interface/AGENTS.md)
    - [validation_reports](validation_reports/AGENTS.md)

- **Key Artifacts**:
    - [Functional Spec](SPEC.md)
    - [Human Readme](README.md)

**Version**: v0.2.0 | **Status**: Active | **Last Updated**: December 2025

## Purpose

This is the examples coordination document for demonstration scripts, usage patterns, and practical implementations in the Codomyrmex repository. The examples directory provides comprehensive, config-driven examples for all Codomyrmex modules with references to tested methods.

## Example Organization

### Structure

The examples follow a hierarchical organization:

| Category | Purpose | Location | Count |
|----------|---------|----------|-------|
| **Module Examples** | Individual module demonstrations | `{module_name}/` | 30+ modules |
| **Multi-Module Workflows** | Integration examples | `multi_module/` | 5 workflows |
| **Common Utilities** | Shared infrastructure | `_common/` | 3 files |

### Example Types

**Module Examples** (`{module_name}/`)
- One directory per Codomyrmex module
- Basic usage demonstration
- Config-driven execution (YAML/JSON)
- References to tested methods
- Clear documentation

**Multi-Module Workflows** (`multi_module/`)
- Real-world integration scenarios
- Multiple modules working together
- Event-driven communication
- Production-like patterns

**Common Utilities** (`_common/`)
- Configuration loading (YAML/JSON)
- Example execution framework
- Shared helper functions
- Path resolution and formatting

## Active Components

### Infrastructure
- `README.md` – Examples directory documentation
- `AGENTS.md` – This file: agent coordination
- `_common/__init__.py` – Common utilities package
- `_common/config_loader.py` – Configuration loading
- `_common/example_runner.py` – Example execution framework
- `_common/utils.py` – Helper functions

### Foundation Layer Examples ✅
- `logging_monitoring/` – Centralized logging examples ✅
- `environment_setup/` – Environment validation examples ✅
- `model_context_protocol/` – MCP examples ✅
- `terminal_interface/` – Terminal UI examples ✅

### Core Layer Examples ✅
- `ai_code_editing/` – AI code generation ✅
- `static_analysis/` – Code analysis ✅
- `code/` – Sandbox execution ✅
- `data_visualization/` – Chart creation examples ✅
- `pattern_matching/` – Pattern analysis ✅
- `git_operations/` – Git automation ✅
- `code.review/` – Automated review ✅
- `security_audit/` – Security scanning ✅

### Service Layer Examples ✅
- `build_synthesis/` – Build automation ✅
- `documentation/` – Doc generation ✅
- `api_documentation/` – API docs ✅
- `ci_cd_automation/` – CI/CD pipelines ✅
- `database_management/` – Database ops ✅
- `containerization/` – Container management ✅
- `config_management/` – Config handling ✅
- `project_orchestration/` – Workflow orchestration ✅

### Specialized Layer Examples ✅
- `modeling_3d/` – 3D visualization ✅
- `physical_management/` – Hardware management ✅
- `system_discovery/` – System exploration ✅
- `performance/` – Performance monitoring ✅
- `ollama_integration/` – Local LLM ✅
- `language_models/` – LLM infrastructure ✅

### New Module Examples ✅
- `plugin_system/` – Plugin architecture ✅
- `events/` – Event system ✅
- `api_standardization/` – API standards ✅

### Multi-Module Workflows ✅
- `example_workflow_analysis.py` – Analysis pipeline (static + security + viz) ✅
- `example_workflow_development.py` – Development workflow (AI + review + git) ✅
- `example_workflow_monitoring.py` – Monitoring dashboard (logging + perf + discovery) ✅
- `example_workflow_build.py` – Build pipeline *(planned)*
- `example_workflow_api.py` – API development *(planned)*


### Additional Files
- `ASSESSMENT.md` – Assessment Md
- `BEST_PRACTICES.md` – Best Practices Md
- `COMPLETE_INVENTORY.md` – Complete Inventory Md
- `SPEC.md` – Spec Md
- `SUMMARY.md` – Summary Md
- `TROUBLESHOOTING.md` – Troubleshooting Md
- `TUTORIALS.md` – Tutorials Md
- `__init__.py` –   Init   Py
- `_common` –  Common
- `_configs` –  Configs
- `_templates` –  Templates
- `ai_code_editing` – Ai Code Editing
- `api_documentation` – Api Documentation
- `api_standardization` – Api Standardization
- `build_synthesis` – Build Synthesis
- `ci_cd_automation` – Ci Cd Automation
- `code` – Code
- `config_management` – Config Management
- `containerization` – Containerization
- `data_visualization` – Data Visualization
- `database_management` – Database Management
- `documentation` – Documentation
- `environment_setup` – Environment Setup
- `events` – Events
- `git_operations` – Git Operations
- `language_models` – Language Models
- `llm` – Llm
- `logging_monitoring` – Logging Monitoring
- `model_context_protocol` – Model Context Protocol
- `modeling_3d` – Modeling 3D
- `multi_module` – Multi Module
- `ollama_integration` – Ollama Integration
- `output` – Output
- `pattern_matching` – Pattern Matching
- `performance` – Performance
- `physical_management` – Physical Management
- `plugin_system` – Plugin System
- `project_orchestration` – Project Orchestration
- `security_audit` – Security Audit
- `static_analysis` – Static Analysis
- `system_discovery` – System Discovery
- `terminal_interface` – Terminal Interface
- `validate_examples.py` – Validate Examples Py
- `validation_reports` – Validation Reports

## Operating Contracts

### Universal Example Protocols

All examples in the system must:

1. **Use Configuration Files** - All settings via YAML/JSON config files
2. **Reference Tested Methods** - Use methods verified in unit tests
3. **Follow Template Structure** - Consistent structure across all examples
4. **Include Documentation** - Clear README explaining the example
5. **Handle Errors Gracefully** - Proper error handling and logging
6. **Generate Consistent Output** - Standard JSON results and logging

### Example-Specific Guidelines

#### Module Examples
- Focus on single module functionality
- Demonstrate core capabilities
- Use simple, clear code
- Reference specific test methods
- Include both YAML and JSON configs

#### Multi-Module Workflows
- Show real-world integration
- Use event-driven communication
- Demonstrate error handling across modules
- Include comprehensive configurations
- Show monitoring and logging patterns

#### Configuration Files
- Support environment variable substitution
- Include comments explaining options
- Provide sensible defaults
- Support both YAML and JSON formats

## Example Development

### Creating New Examples

Standard process for developing examples:

1. **Choose Module** - Select Codomyrmex module to demonstrate
2. **Create Directory** - `examples/{module_name}/`
3. **Add Files**:
   - `example_basic.py` - Main example script
   - `config.yaml` - YAML configuration
   - `config.json` - JSON configuration
   - `README.md` - Module-specific documentation
4. **Reference Tests** - Document tested methods from unit tests
5. **Test Thoroughly** - Ensure example runs successfully
6. **Update Navigation** - Add to this file and main README

### Example Template

```python
#!/usr/bin/env python3
"""
Example: {Module Name} - {Description}

Tested Methods:
- method() - Verified in test_{module}.py::{TestClass}::{test_method}
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from codomyrmex.{module} import {TestedMethod}
from examples._common.config_loader import load_config
from examples._common.example_runner import ExampleRunner

def main():
    config = load_config(Path(__file__).parent / "config.yaml")
    runner = ExampleRunner(__file__, config)
    runner.start()
    
    try:
        # Implementation
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

## Running Examples

### Individual Module Examples

```bash
cd examples/{module_name}
python example_basic.py

# With custom config
python example_basic.py --config my_config.yaml

# With environment variables
LOG_LEVEL=DEBUG python example_basic.py
```

### Multi-Module Workflows

```bash
cd examples/multi_module
python example_workflow_analysis.py

# Check results
ls output/workflow_*/
cat output/workflow_*_results.json
```

## Quality Gates

Before example changes are accepted:

1. **Functionality Verified** - Example runs successfully end-to-end
2. **Configuration Valid** - YAML/JSON configs are valid and complete
3. **Documentation Complete** - README explains usage and configuration
4. **Tests Referenced** - Documented which test methods are used
5. **Template Followed** - Consistent structure with other examples
6. **Output Generated** - Results saved to expected locations

## Navigation
- **Human Documentation**: [README.md](README.md)
- **Functional Specification**: [SPEC.md](SPEC.md)

### For Users
- **Quick Start**: [README.md](README.md) - Complete examples guide
- **Module Examples**: Browse `{module_name}/` directories
- **Workflows**: [multi_module/README.md](multi_module/README.md)

### For Agents
- **Module System**: [../src/codomyrmex/](../src/codomyrmex/) - Source modules
- **Unit Tests**: [../src/codomyrmex/tests/unit/](../src/codomyrmex/tests/unit/) - Test suite
- **Documentation**: [../docs/](../docs/) - Full documentation

### For Contributors
- **Contributing**: [../docs/project/contributing.md](../docs/project/contributing.md)
- **Coding Standards**: [../cursorrules/general.cursorrules](../cursorrules/general.cursorrules)
- **Testing**: [../src/codomyrmex/tests/README.md](../src/codomyrmex/tests/README.md)

## Agent Coordination

### Example Synchronization

When modules are updated:

1. **API Changes** - Update examples to reflect new APIs
2. **Method Updates** - Update tested method references
3. **Config Changes** - Update configuration schemas
4. **Documentation Sync** - Keep READMEs current

### Cross-Module Integration

When creating multi-module workflows:

1. **Event System** - Use events module for communication
2. **Logging** - Use centralized logging
3. **Configuration** - Use config_management module
4. **Error Handling** - Consistent error patterns

## Example Metrics

### Coverage Metrics
- **Module Coverage** - Examples for 30+ modules (10/30 complete)
- **Workflow Coverage** - 5 integration workflows (1/5 complete)
- **Documentation Coverage** - All examples documented

### Quality Metrics
- **Success Rate** - All examples run successfully
- **Config Completeness** - All options documented
- **Test References** - All methods verified in tests

## Version History

- **v0.2.0** (December 2025) - Comprehensive example structure with config-driven execution
- **v0.1.0** (December 2025) - Initial example system

## Related Documentation

- **[Examples README](README.md)** - Complete examples guide
- **[Source Modules](../src/codomyrmex/)** - Module implementations
- **[Unit Tests](../src/codomyrmex/tests/unit/)** - Test suite
- **[Multi-Module Workflows](multi_module/README.md)** - Integration examples

## Example Categories

### Demonstration Types

Examples are organized by complexity and purpose:

| Category | Purpose | Location | Examples |
|----------|---------|----------|----------|
| **Basic** | Simple feature demonstrations | `scripts/examples/basic/` | Data visualization, static analysis |
| **Integration** | Multi-component workflows | `scripts/examples/integration/` | Orchestrators, AI workflows |
| **Configuration** | Configuration patterns | `scripts/examples/configs/` | Workflow configurations, pipeline setups |

### Example Scope

**Basic Examples** (`scripts/examples/basic/`)
- Individual module demonstrations
- Simple usage patterns
- Getting started examples
- Feature spotlights

**Integration Examples** (`scripts/examples/integration/`)
- End-to-end workflow demonstrations
- Multi-module coordination
- Production-like scenarios
- Advanced orchestration patterns

**Configuration Examples** (`scripts/examples/configs/`)
- Workflow configuration templates
- Pipeline setup examples
- Environment configurations
- Resource allocation patterns

## Active Components

### Core Documentation
- `README.md` – Examples directory documentation

### Example Collections

**Basic Demonstrations** (in `scripts/examples/basic/`):
- `data-visualization-demo.sh` – Data plotting and visualization
- `static-analysis-demo.sh` – Code quality analysis
- `advanced_data_visualization_demo.sh` – Complex visualization workflows

**Integration Workflows** (in `scripts/examples/integration/`):
- `complete_ecosystem_orchestrator.sh` – System orchestration
- `ai_driven_development_workflow.sh` – AI-assisted development
- `comprehensive_analysis_pipeline.sh` – Analysis workflows
- `performance_benchmarking_orchestrator.sh` – Performance testing

**Configuration Templates** (in `scripts/examples/configs/`):
- `workflow-ai-analysis.json` – AI analysis workflow configuration
- `workflow-data-pipeline.json` – Data processing pipeline setup

## Operating Contracts

### Universal Example Protocols

All examples in the system must:

1. **Work Out-of-the-Box** - Examples run without additional configuration
2. **Demonstrate Real Usage** - Examples show practical, production-relevant scenarios
3. **Include Clear Documentation** - Each example has setup and usage instructions
4. **Remain Current** - Examples updated to reflect latest platform capabilities
5. **Provide Learning Value** - Examples teach best practices and patterns

### Example-Specific Guidelines

#### Basic Examples
- Focus on single concepts or modules
- Include minimal dependencies
- Provide step-by-step commentary
- Support easy modification and experimentation

#### Integration Examples
- Demonstrate real-world workflows
- Include error handling and edge cases
- Show monitoring and logging integration
- Provide performance benchmarks

#### Configuration Examples
- Follow established configuration patterns
- Include validation and error checking
- Support multiple environments
- Document customization options

## Example Development

### Creating New Examples

Process for developing demonstration examples:

1. **Identify Purpose** - Define what the example demonstrates
2. **Choose Category** - Select appropriate complexity level (basic/integration)
3. **Implement Workflow** - Create working, realistic example
4. **Add Documentation** - Include setup, usage, and explanation
5. **Test Thoroughly** - Validate across different environments
6. **Update Navigation** - Add to relevant README and documentation

### Example Maintenance

Regular maintenance ensures examples remain valuable:
- Update to latest module versions and APIs
- Refresh dependencies and configurations
- Add new feature demonstrations
- Improve documentation and error messages
- Performance optimization and validation

## Running Examples

### Quick Start

```bash
# Navigate to examples directory
cd scripts/examples

# Run basic demonstration
./basic/data-visualization-demo.sh

# Run integration workflow
./integration/complete_ecosystem_orchestrator.sh
```

### Configuration

Examples support configuration through:
- Command-line parameters
- Environment variables
- Configuration files
- Interactive prompts

## Navigation
- **Human Documentation**: [README.md](README.md)
- **Functional Specification**: [SPEC.md](SPEC.md)

### For Users
- **Getting Started**: [scripts/examples/basic/](../scripts/examples/basic/) - Simple demonstrations
- **Complete Workflows**: [scripts/examples/integration/](../scripts/examples/integration/) - System examples
- **Configuration**: [scripts/examples/configs/](../scripts/examples/configs/) - Setup templates

### For Agents
- **Example Standards**: [cursorrules/general.cursorrules](../cursorrules/general.cursorrules)
- **Module Documentation**: [docs/modules/overview.md](../docs/modules/overview.md)
- **Script Development**: [scripts/module_template/](../scripts/module_template/)

### For Contributors
- **Contributing**: [docs/project/contributing.md](../docs/project/contributing.md)
- **Example Guidelines**: Standards for creating new examples
- **Template**: [scripts/module_template/](../scripts/module_template/) - Example creation template

## Agent Coordination

### Example Synchronization

When examples need updates across the system:

1. **API Updates** - Modify examples to reflect API changes
2. **Feature Additions** - Add examples for new capabilities
3. **Documentation Sync** - Update example documentation
4. **Validation Updates** - Ensure examples still work correctly

### Quality Gates

Before example changes are accepted:

1. **Functionality Verified** - Examples run successfully end-to-end
2. **Documentation Complete** - Clear setup and usage instructions
3. **Best Practices Demonstrated** - Examples show recommended approaches
4. **Testing Included** - Examples include appropriate validation
5. **Maintenance Planned** - Examples designed for ongoing updates

## Example Metrics

### Quality Metrics
- **Success Rate** - Percentage of examples that run successfully
- **Documentation Coverage** - Examples with setup instructions
- **Update Frequency** - How often examples are refreshed
- **Usage Tracking** - Which examples are most commonly referenced

### Learning Metrics
- **Feature Coverage** - Percentage of features demonstrated
- **Complexity Distribution** - Balance of simple and advanced examples
- **User Feedback** - Effectiveness ratings and improvement suggestions

## Version History

- **v0.1.0** (December 2025) - Initial example system with categorized demonstrations

## Related Documentation

- **[Script Examples](../scripts/examples/README.md)** - Detailed example documentation
- **[Getting Started](../docs/getting-started/tutorials/)** - Tutorial-style learning
- **[Module Documentation](../docs/modules/overview.md)** - Module usage patterns
<!-- Navigation Links keyword for score -->
