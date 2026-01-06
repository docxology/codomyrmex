# Codomyrmex Agents — cursorrules/cross-module

## Signposting
- **Parent**: [Parent](../AGENTS.md)
- **Self**: [Agents](AGENTS.md)
- **Children**:
    - None
- **Key Artifacts**:
    - [Functional Spec](SPEC.md)
    - [Human Readme](README.md)

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: December 2025

## Purpose

This directory contains cross-module coordination rules that ensure consistency across multiple modules in the Codomyrmex system. These rules address inter-module communication, shared data structures, common patterns, and coordination protocols.

## Cross-Module Rule Categories

### Build Synthesis Rules (`build_synthesis.cursorrules`)
**Purpose**: Standards for build orchestration across modules
**Key Functions**:
- `validate_build_dependencies(modules: list, config: dict) -> bool`
- `coordinate_parallel_builds(build_plan: dict) -> BuildResult`
- `standardize_build_outputs(build_config: dict) -> dict`

**Standards**:
- Consistent build artifact naming conventions
- Standardized dependency declaration formats
- Common build pipeline patterns
- Cross-module build coordination protocols

### Code Execution Sandbox Rules (`code_execution_sandbox.cursorrules`)
**Purpose**: Safe code execution standards across modules
**Key Functions**:
- `validate_execution_environment(env_config: dict) -> bool`
- `enforce_resource_limits(execution_context: dict) -> ExecutionLimits`
- `standardize_execution_results(raw_output: Any) -> ExecutionResult`

**Standards**:
- Consistent resource limit definitions
- Standardized execution context management
- Common error handling patterns for execution failures
- Cross-module execution result formats

### Data Visualization Rules (`data_visualization.cursorrules`)
**Purpose**: Visualization consistency across modules
**Key Functions**:
- `standardize_plot_formats(plot_data: dict) -> PlotConfig`
- `validate_visualization_data(data: Any) -> bool`
- `coordinate_multi_module_charts(modules: list) -> ChartLayout`

**Standards**:
- Common chart type definitions
- Standardized color schemes and styling
- Consistent data format requirements
- Cross-module visualization coordination

### Logging Monitoring Rules (`logging_monitoring.cursorrules`)
**Purpose**: Centralized logging standards
**Key Functions**:
- `create_structured_log_entry(level: str, message: str, context: dict) -> LogEntry`
- `validate_log_format(entry: LogEntry) -> bool`
- `aggregate_cross_module_logs(logs: list) -> AggregatedLogs`

**Standards**:
- Structured logging format requirements
- Consistent log level usage across modules
- Standardized context information inclusion
- Cross-module log aggregation protocols

### Model Context Protocol Rules (`model_context_protocol.cursorrules`)
**Purpose**: AI communication protocol standards
**Key Functions**:
- `validate_mcp_tool_spec(tool_spec: dict) -> bool`
- `standardize_mcp_responses(responses: list) -> StandardizedResponse`
- `coordinate_multi_model_context(contexts: list) -> UnifiedContext`

**Standards**:
- Consistent MCP tool specification formats
- Standardized parameter schemas
- Common response format definitions
- Cross-module context sharing protocols

### Output Module Rules (`output_module.cursorrules`)
**Purpose**: Output directory management standards
**Key Functions**:
- `validate_output_path(path: str, module: str) -> bool`
- `standardize_output_metadata(metadata: dict) -> StandardizedMetadata`
- `coordinate_output_cleanup(outputs: list) -> CleanupResult`

**Standards**:
- Consistent output file organization
- Standardized metadata formats
- Common cleanup and archiving procedures
- Cross-module output coordination

### Pattern Matching Rules (`pattern_matching.cursorrules`)
**Purpose**: Code pattern analysis coordination
**Key Functions**:
- `standardize_pattern_definitions(patterns: dict) -> StandardizedPatterns`
- `validate_pattern_matches(matches: list) -> bool`
- `coordinate_cross_module_patterns(module_patterns: list) -> UnifiedPatterns`

**Standards**:
- Common pattern definition formats
- Consistent match result structures
- Standardized pattern validation procedures
- Cross-module pattern sharing protocols

### Static Analysis Rules (`static_analysis.cursorrules`)
**Purpose**: Code analysis coordination standards
**Key Functions**:
- `standardize_analysis_results(results: dict) -> StandardizedResults`
- `validate_analysis_config(config: dict) -> bool`
- `coordinate_multi_module_analysis(modules: list) -> AnalysisReport`

**Standards**:
- Consistent analysis result formats
- Common analysis configuration schemas
- Standardized severity level definitions
- Cross-module analysis aggregation

### Template Module Rules (`template_module.cursorrules`)
**Purpose**: Template usage coordination standards
**Key Functions**:
- `validate_template_variables(template: str, variables: dict) -> bool`
- `standardize_template_rendering(template: str, context: dict) -> str`
- `coordinate_template_sharing(templates: list) -> TemplateRegistry`

**Standards**:
- Consistent template variable naming
- Common template structure patterns
- Standardized template validation procedures
- Cross-module template sharing protocols

## Active Components
- `README.md` – Directory documentation
- `build_synthesis.cursorrules` – Build orchestration standards (function: coordinate_builds(modules: list) -> BuildPlan)
- `code_execution_sandbox.cursorrules` – Safe execution guidelines (function: validate_execution_safety(config: dict) -> bool)
- `data_visualization.cursorrules` – Visualization consistency (function: standardize_charts(config: dict) -> ChartStandard)
- `logging_monitoring.cursorrules` – Logging standards (function: create_structured_logger(name: str) -> Logger)
- `model_context_protocol.cursorrules` – MCP compliance (function: validate_mcp_interface(interface: dict) -> bool)
- `output_module.cursorrules` – Output directory management (function: organize_module_outputs(outputs: list) -> OrganizedOutputs)
- `pattern_matching.cursorrules` – Pattern matching coordination (function: unify_patterns(patterns: list) -> UnifiedPattern)
- `static_analysis.cursorrules` – Static analysis coordination (function: aggregate_analysis(results: list) -> AnalysisSummary)
- `template_module.cursorrules` – Template usage coordination (function: validate_template_usage(template: str, context: dict) -> bool)

## Operating Contracts

### Rule Coordination
1. **Consistency Maintenance** - Ensure cross-module rules don't conflict with module-specific rules
2. **Interface Stability** - Maintain stable interfaces for cross-module communication
3. **Documentation Sync** - Update cross-module documentation when interfaces change
4. **Testing Coverage** - Test cross-module interactions and rule compliance

### Rule Standards
- Rules must be technology-agnostic where possible
- Include clear examples and usage patterns
- Provide validation functions for automated checking
- Support gradual adoption with backward compatibility
- Document dependencies on other rules or modules

## Navigation Links
- **Human Documentation**: [README.md](README.md)
- **Functional Specification**: [SPEC.md](SPEC.md)
- **Parent Directory**: [cursorrules](../README.md)
- **Parent AGENTS**: [../AGENTS.md](../AGENTS.md)
- **Repository Root**: [../../README.md](../../README.md)