# Codomyrmex Project TO-DO List

This document outlines the tasks required to complete the Codomyrmex project. It is organized into general project-wide tasks and module-specific tasks.

## I. General Project-Wide Tasks

- [ ] **Dependency Management**: Enforce version pinning in all `requirements.txt` files.
    - [ ] Update root `requirements.txt` to use exact versions for all dependencies (e.g., `openai==X.Y.Z` instead of `openai>=X.Y.Z`).
    - [ ] Review and update all module-specific `requirements.txt` files to use exact versions for their dependencies.
    - [ ] Ensure module `requirements.txt` files correctly state reliance on the root file or list only truly specific dependencies with pinned versions.
- [ ] **Testing Strategy**: 
    - [x] Define and document a project-wide testing strategy (unit, integration, E2E).
    - [ ] Strive for high test coverage across all modules.
- [ ] **Documentation Consistency**:
    - [x] Ensure all modules have complete and consistent documentation (`README.md`, `API_SPECIFICATION.md`, `MCP_TOOL_SPECIFICATION.md`, `CHANGELOG.md`, `SECURITY.md`, `USAGE_EXAMPLES.md`, `docs/`). (File existence verified for all modules; content and consistency handled by module-specific tasks).
- [ ] **Error Handling and Logging**: Ensure consistent error handling and structured logging (via `logging_monitoring`) across all modules.
    - [x] Audit all relevant Python-based modules to ensure they use `get_logger` from the `logging_monitoring` module.
    - [x] Define and document project-wide best practices for error handling (e.g., when to raise exceptions, how to format error messages for logs).
- [ ] **Security Review**: Conduct a project-wide security review.
    - [x] Ensure each module's `SECURITY.md` accurately reflects its specific threats, mitigation strategies, and responsible disclosure process, replacing template content where necessary.
    - [ ] Implement security policies outlined in `SECURITY.md` files across modules (ongoing).

## II. Module-Specific Tasks

### 1. AI Code Editing (`ai_code_editing`)

- [ ] **`docs/`**:
    - [x] Complete `technical_overview.md` with actual architecture and design decisions. (Placeholder content present, needs filling)
    - [x] Create meaningful tutorials in `docs/tutorials/` (e.g., for `generate_code_snippet` and `refactor_code_snippet`), replacing or augmenting `example_tutorial.md`.
- [ ] **Tests**:
    - [ ] Write unit and integration tests for all features. (Expanded unit tests for `ai_code_helpers.py` error handling; broader coverage still needed for all components and integration aspects).
- [ ] **Adherence to `ai_code_editing.cursorrules`**: Ensure all development follows module-specific rules.
    - [x] Create `ai_code_editing/.cursor/.cursorrules` file from `template/module_template/.cursor/.cursorrules`.
    - [ ] Ensure development activity respects these guidelines (ongoing).

### 2. Build Synthesis (`build_synthesis`)

- [ ] **`API_SPECIFICATION.md`**:
    - [x] Define actual APIs for build and synthesis tasks, replacing `example_function()`. (All sub-tasks defining specific APIs are now addressed in the document)
- [ ] **`MCP_TOOL_SPECIFICATION.md`**:
    - [x] Align MCP tools with the newly defined API functions (`trigger_build`, `get_build_status`, `synthesize_component_from_prompt`, `synthesize_component_from_spec`).
    - [x] Ensure clear mapping between MCP tool parameters and API function arguments.
- [ ] **`docs/`**:
    - [x] Complete `technical_overview.md`. (Placeholder content present, needs filling)
    - [ ] Create meaningful tutorials in `docs/tutorials/` (e.g., for common build targets like Python wheels/Docker, and for code synthesis using `synthesize_code_component`), replacing or augmenting `example_tutorial.md`.
- [ ] **Core Logic**: Implement build orchestration and code generation logic.
- [ ] **Tests**:
    - [ ] Test build scripts, synthesis logic, and reproducibility.
- [ ] **Adherence to `build_synthesis.cursorrules`**: Ensure all development follows module-specific rules.
    - [ ] Create `build_synthesis/.cursor/.cursorrules` file from `template/module_template/.cursor/.cursorrules`.
    - [ ] Ensure development activity respects these guidelines (ongoing).

### 3. Code Execution Sandbox (`code`)

- [ ] **`SECURITY.md`**: This is critical.
    - [ ] Detail security measures, threat model, and responsible disclosure. (Template present, needs specific content for sandbox)
        - [ ] Detail sandbox escape prevention mechanisms.
        - [ ] Detail mitigation strategies for resource exhaustion attacks (CPU, memory, disk, network).
        - [ ] Document secure inter-process communication (IPC) if applicable.
- [ ] **`USAGE_EXAMPLES.md`**: Provide examples for using the sandbox.
    - [ ] Example: Running a simple Python script and capturing its output.
    - [ ] Example: Executing a shell command and handling exit codes.
    - [ ] Example: Demonstrating resource limit enforcement.
- [ ] **`docs/`**:
    - [ ] Complete `technical_overview.md`. (Placeholder content present)
        - [ ] Document the chosen containerization/isolation technology (e.g., Docker, gVisor, systemd-nspawn, Firecracker).
        - [ ] Detail communication protocols between the host and the sandbox.
        - [ ] Describe security layers and hardening techniques applied.
    - [ ] Document supported languages, resource limits, and security configurations. (Placeholder content in `technical_overview.md` and `tutorials/example_tutorial.md`)
- [ ] **Core Logic**: Implement sandbox setup, execution management, and resource limiting.
- [ ] **Tests**:
    - [ ] Include security tests (sandbox escapes), resource limit tests, and functionality tests.
    - [ ] Update `tests/README.md`.
- [ ] **Adherence to `code.cursorrules`**: Ensure all development follows module-specific rules, prioritizing security.
    - [ ] Create `code/.cursor/.cursorrules` file from `template/module_template/.cursor/.cursorrules`.
    - [ ] Ensure development activity respects these guidelines (ongoing).

### 4. Data Visualization (`data_visualization`)

- [ ] **`API_SPECIFICATION.md`**:
    - [ ] Define actual APIs for data visualization tasks, replacing `example_function()`.
        - [ ] Example API: `generate_plot(data: dict, plot_type: str, options: dict) -> str` (returns image path or base64 string).
        - [ ] Example API: `create_dashboard(plot_configs: list) -> str` (returns dashboard URL or HTML content).
- [ ] **`MCP_TOOL_SPECIFICATION.md`**:
    - [ ] Specify MCP tools for data visualization.
        - [ ] Example Tool: `visualize_data_interactive` (for dynamic charts).
        - [ ] Example Tool: `get_chart_as_image(data_source_id, chart_parameters)`.
- [ ] **`SECURITY.md`**: This is critical.
    - [ ] Detail security measures, threat model, and responsible disclosure. (Template present, needs specific content for data visualization, especially if rendering user-provided data).
    - [ ] Update `tests/README.md` (if applicable, or a general guide for testing docs).
- [ ] **`USAGE_EXAMPLES.md`**: Provide examples for generating various chart types or dashboards.
- [ ] **`requirements.txt`**:
    - [ ] List any specific data visualization libraries (e.g., `matplotlib`, `seaborn`, `plotly`).
- [ ] **`docs/`**:
    - [ ] Complete `technical_overview.md` (Placeholder content present).
    - [ ] Create tutorials for different visualization types and integration methods.
- [ ] **Core Logic**: Implement data processing and visualization generation logic.
- [ ] **Tests**:
    - [ ] Test visualization generation, data handling, and error conditions.
    - [ ] Update `tests/README.md`.
- [ ] **Adherence to `data_visualization.cursorrules`**: Ensure all development follows module-specific rules.
    - [ ] Create `data_visualization/.cursor/.cursorrules` file from `template/module_template/.cursor/.cursorrules`.
    - [ ] Ensure development activity respects these guidelines (ongoing).

### 5. Documentation (`documentation`)

- [ ] **`README.md`**: Finalize overall project documentation structure and contribution guidelines.
- [ ] **Docusaurus Configuration (`docusaurus.config.js`, `sidebars.js` etc.):**
    - [ ] Review and optimize Docusaurus configuration.
    - [ ] Ensure all modules are correctly represented in sidebars and navigation.
    - [ ] Verify inter-module linking and external links.
- [ ] **Content Review & Enhancement**: 
    - [ ] Review all `docs/` directories within modules for completeness and consistency.
    - [ ] Standardize terminology and style across all documentation.
    - [ ] Ensure `technical_overview.md` for each module is comprehensive.
    - [ ] Ensure tutorials are clear, accurate, and cover key use cases.
- [ ] **Build and Deployment**: 
    - [ ] Test documentation build process.
    - [ ] Set up automated deployment for documentation (e.g., GitHub Pages).
- [ ] **Tests**:
    - [ ] Check for broken links.
    - [ ] Validate documentation build.
    - [ ] Update `tests/README.md` (if applicable, or a general guide for testing docs).
- [ ] **Adherence to `documentation.cursorrules`**: Ensure all development follows module-specific rules.
    - [ ] Create `documentation/.cursor/.cursorrules` file from `template/module_template/.cursor/.cursorrules`.
    - [ ] Ensure development activity respects these guidelines (ongoing).

### 6. Environment Setup (`environment_setup`)

- [x] **`README.md`**: Provide comprehensive instructions for setting up the development environment for the entire project and for individual modules.
    - [x] Cover prerequisites (Python version, pip, virtual environments, Docker if used, etc.).
    - [x] Detail steps for cloning, installing dependencies (root and module-specific).
    - [x] Instructions for running tests and linters.
- [x] **Scripts (Optional)**:
    - [x] Develop helper scripts for common setup tasks (e.g., `setup_dev_env.sh`, `install_hooks.sh`).
- [x] **`API_SPECIFICATION.md` / `MCP_TOOL_SPECIFICATION.md`**: (Likely N/A, but confirm if any tools are exposed).
- [x] **`SECURITY.md`**: Outline any security considerations for the development environment or setup scripts.
- [x] **`USAGE_EXAMPLES.md`**: Provide examples of setting up for different scenarios (e.g., basic dev, full features with all modules).
- [x] **`requirements.txt`**: List any tools required for environment setup itself (e.g., `virtualenv`, `poetry`).
- [x] **`docs/`**:
    - [x] Complete `technical_overview.md` if there are complex aspects to the setup.
    - [x] Create tutorials for troubleshooting common setup issues.
- [x] **Core Logic**: (Likely focused on scripts and documentation).
- [x] **Tests**: 
    - [ ] Test setup scripts on different platforms (if feasible).
    - [ ] Manually verify setup instructions.
    - [x] Update `tests/README.md`.
- [ ] **Adherence to `environment_setup.cursorrules`**: Ensure all development follows module-specific rules.
    - [x] Create `environment_setup/.cursor/.cursorrules` file from `template/module_template/.cursor/.cursorrules`.
    - [ ] Ensure development activity respects these guidelines (ongoing).

### 7. Git Operations (`git_operations`)

- [ ] **`README.md`**: Document any specific Git workflows, branching strategies, or commit message conventions for the project.
- [ ] **`API_SPECIFICATION.md` / `MCP_TOOL_SPECIFICATION.md`**:
    - [ ] Define any APIs or MCP tools for automating Git operations (e.g., `create_feature_branch`, `submit_pull_request`).
        - [ ] Example API/Tool: `create_branch(branch_name: str, base_branch: str = "main")`.
        - [ ] Example API/Tool: `commit_changes(message: str, files: list[str] = None)`. # if files is None, stage all changes
        - [ ] Example API/Tool: `create_pull_request(title: str, body: str, head_branch: str, base_branch: str = "main")`.
- [ ] **`SECURITY.md`**: Address security aspects of Git usage (e.g., pre-commit hooks for secrets, secure handling of tokens if tools automate Git operations).
- [ ] **`USAGE_EXAMPLES.md`**: Provide examples for using any custom Git tools or following specific workflows.
- [ ] **`requirements.txt`**: List any Python libraries used for Git automation (e.g., `GitPython`).
- [ ] **`docs/`**:
    - [ ] Complete `technical_overview.md` for any complex Git automation logic.
    - [ ] Create tutorials for project-specific Git practices.
- [ ] **Core Logic**: Implement any scripts or Python code for Git automation tools.
- [ ] **Tests**: 
    - [ ] Test any Git automation scripts or tools.
    - [ ] Update `tests/README.md`.
- [ ] **Adherence to `git_operations.cursorrules`**: Ensure all development follows module-specific rules.
    - [ ] Create `git_operations/.cursor/.cursorrules` file from `template/module_template/.cursor/.cursorrules`.
    - [ ] Ensure development activity respects these guidelines (ongoing).

### 8. Logging Monitoring (`logging_monitoring`)

- [ ] **`README.md`**: Detail how to use the logging and monitoring framework provided by this module.
    - [ ] Explain logger configuration, log levels, structured logging format.
    - [ ] Describe integration with monitoring tools (if any planned, e.g., Prometheus, Grafana, Sentry).
- [ ] **`API_SPECIFICATION.md`**: 
    - [ ] Define the API for accessing or configuring logging/monitoring (e.g., `get_logger`, `configure_logging`).
- [ ] **`MCP_TOOL_SPECIFICATION.md`**: (Likely N/A unless tools are exposed for external log management).
- [ ] **`SECURITY.md`**: Address security of log data (e.g., scrubbing sensitive information, log storage security).
- [ ] **`USAGE_EXAMPLES.md`**: Provide code snippets showing how other modules should integrate and use the logging utilities.
- [ ] **`requirements.txt`**: List dependencies for logging (e.g., `structlog`) and any monitoring libraries.
- [ ] **`docs/`**:
    - [ ] Complete `technical_overview.md` explaining the logging architecture and design choices.
    - [ ] Create tutorials on best practices for logging within the project, and how to interpret monitoring dashboards.
- [ ] **Core Logic**: Implement the core logging setup (e.g., `get_logger` function, default configurations) and any monitoring integration points.
- [ ] **Tests**: 
    - [ ] Test logger creation, configuration, and output formatting.
    - [ ] Test integration with monitoring systems (if applicable).
    - [ ] Update `tests/README.md`.
- [ ] **Adherence to `logging_monitoring.cursorrules`**: Ensure all development follows module-specific rules.
    - [ ] Create `logging_monitoring/.cursor/.cursorrules` file from `template/module_template/.cursor/.cursorrules`.
    - [ ] Ensure development activity respects these guidelines (ongoing).

### 9. Model Context Protocol (`model_context_protocol`)

- [ ] **`README.md`**: Clearly define the Model Context Protocol (MCP), its purpose, and how it facilitates communication between modules and AI models.
- [ ] **MCP Specification Document(s)**: (This might be the core of this module, potentially in `docs/` or as a top-level spec file)
    - [ ] Formalize the MCP data structures, message formats, and interaction patterns.
    - [ ] Define standard tool specification format to be used by all modules providing MCP tools.
    - [ ] Versioning strategy for the MCP itself.
    - [ ] Define standard error reporting mechanisms and codes within MCP messages.
- [ ] **`API_SPECIFICATION.md`**: (Likely N/A as MCP is a protocol, but there might be helper/validation APIs).
- [ ] **`MCP_TOOL_SPECIFICATION.md`**: (This module defines the *format* for these, rather than having its own tools, unless there are meta-tools for MCP validation/introspection).
- [ ] **`SECURITY.md`**: Discuss security implications of the MCP, data validation, and authorization for tool usage.
- [ ] **`USAGE_EXAMPLES.md`**: Provide examples of MCP messages and tool specifications from other modules.
- [ ] **`requirements.txt`**: List any libraries for data validation (e.g., `pydantic`) or protocol definition.
- [ ] **`docs/`**:
    - [ ] Complete `technical_overview.md` detailing the design and rationale of MCP.
    - [ ] Create tutorials on how to implement an MCP-compliant tool and how to consume MCP messages.
- [ ] **Core Logic**: Implement any shared libraries, validation logic, or schemas for MCP.
- [ ] **Tests**: 
    - [ ] Test MCP schema validation.
    - [ ] Test examples of MCP interactions.
    - [ ] Update `tests/README.md`.
- [ ] **Adherence to `model_context_protocol.cursorrules`**: Ensure all development follows module-specific rules.
    - [ ] Create `model_context_protocol/.cursor/.cursorrules` file from `template/module_template/.cursor/.cursorrules`.
    - [ ] Ensure development activity respects these guidelines (ongoing).

### 10. Pattern Matching (`pattern_matching`)

- [ ] **`README.md`**: Describe the capabilities of the pattern matching module (e.g., regex, AST-based, semantic).
- [ ] **`API_SPECIFICATION.md`**:
    - [ ] Define APIs for submitting text/code and patterns for matching (e.g., `find_matches`, `extract_data`).
        - [ ] Example API: `find_regex_matches(text: str, pattern: str, flags: int = 0) -> list[dict]`.
        - [ ] Example API: `find_ast_matches(code: str, language: str, ast_query: str) -> list[dict]`.
        - [ ] Example API: `extract_semantic_entities(text: str, entity_types: list[str] = None, model_id: str = "default") -> list[dict]`.
- [ ] **`MCP_TOOL_SPECIFICATION.md`**: 
    - [ ] Specify MCP tools for pattern matching tasks.
- [ ] **`SECURITY.md`**: Address potential for ReDoS (Regular Expression Denial of Service) if using complex regexes, and security of parsing untrusted code if using AST-based matching.
- [ ] **`USAGE_EXAMPLES.md`**: Provide examples of different pattern matching use cases.
- [ ] **`requirements.txt`**: List any libraries for advanced pattern matching or AST parsing.
- [ ] **`docs/`**:
    - [ ] Complete `technical_overview.md` explaining the different matching strategies and their trade-offs.
    - [ ] Create tutorials for common pattern matching tasks.
- [ ] **Core Logic**: Implement the pattern matching algorithms and supporting infrastructure.
- [ ] **Tests**: 
    - [ ] Test various pattern types and edge cases.
    - [ ] Test performance and security (e.g., against ReDoS).
    - [ ] Update `tests/README.md`.
- [ ] **Adherence to `pattern_matching.cursorrules`**: Ensure all development follows module-specific rules.
    - [ ] Create `pattern_matching/.cursor/.cursorrules` file from `template/module_template/.cursor/.cursorrules`.
    - [ ] Ensure development activity respects these guidelines (ongoing).

### 11. Static Analysis (`static_analysis`)

- [ ] **`SECURITY.md`**:
    - [ ] Review and update security considerations for running various analysis tools, including Pyrefly.
- [ ] **`requirements.txt`**:
    - [ ] Ensure all dependencies are pinned to exact versions (general project task).
- [ ] **Pyrefly Integration (`pyrefly_runner.py`)**:
    - [ ] **Refine Pyrefly Output Parser**:
        - [ ] Test `pyrefly_runner.py` with actual Pyrefly execution on type errors.
        - [ ] Analyze Pyrefly's `stdout`/`stderr` for error patterns.
        - [ ] Update `PYREFLY_ERROR_PATTERN` regex in `pyrefly_runner.py` for accuracy.
        - [ ] Ensure correct extraction of file path, line, column, message, and error code (if available).
        - [ ] Implement handling for different Pyrefly output formats (e.g., JSON, plain text) if Pyrefly supports them and they are configurable.
    - [ ] **Integrate `pyrefly_runner.py` into main static analysis orchestrator**:
        - [ ] Ensure the main `run_static_analysis` logic can invoke `pyrefly_runner.run_pyrefly_analysis` when "pyrefly" is in the tools list.
        - [ ] Properly pass `target_paths` and `project_root` to the runner.
        - [ ] Aggregate results from `pyrefly_runner.py` into the overall `tool_results` array.
- [ ] **`docs/`**:
    - [ ] Create meaningful tutorials (e.g., "Using Pyrefly for Type Checking"), replacing or augmenting `example_tutorial.md`.
- [ ] **Core Logic**:
    - [ ] Implement the main orchestrator script for `run_static_analysis` that calls individual tool runners (Pylint, Flake8, Bandit, Pyrefly, etc.).
    - [ ] Ensure robust error handling and aggregation of results from all tools.
- [ ] **Tests**:
    - [ ] Write unit tests for `pyrefly_runner.py` (e.g., mocking `subprocess.run`, testing parser with sample outputs).
    - [ ] Write integration tests for the `run_static_analysis` tool invoking Pyrefly on test projects.
- [ ] **Adherence to `static_analysis.cursorrules`**:
    - [ ] Create `static_analysis/.cursor/.cursorrules`.
    - [ ] Ensure all development follows module-specific rules.
## Navigation Links

- **Parent**: [docs](../README.md)
- **Module Index**: [AGENTS.md](../../AGENTS.md)
- **Home**: [Repository Root](../../README.md)
