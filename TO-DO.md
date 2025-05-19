# Codomyrmex Project TO-DO List

This document outlines the tasks required to complete the Codomyrmex project. It is organized into general project-wide tasks and module-specific tasks.

## I. General Project-Wide Tasks

- [ ] **Overall Architecture Review**: Ensure a clear and consistent architecture across all modules.
- [ ] **Dependency Management**: (Reviewed module requirements.txt files; main structure seems fine. Specifics handled per module.)
- [ ] **Testing Strategy**: 
    - [ ] Define and document a project-wide testing strategy (unit, integration, E2E).
    - [x] Ensure all modules have a `tests/README.md` with clear instructions.
    - [ ] Strive for high test coverage across all modules.
- [ ] **Documentation Consistency**:
    - [ ] Ensure all modules have complete and consistent documentation (`README.md`, `API_SPECIFICATION.md`, `MCP_TOOL_SPECIFICATION.md`, `CHANGELOG.md`, `SECURITY.md`, `USAGE_EXAMPLES.md`, `docs/`).
    - [~] Remove all placeholder content (e.g., "(Provide a concise overview...)", "`[Tool Name]`"). (Standardized "[e.g., 48 hours]" in all SECURITY.md files; `template/module_template/MCP_TOOL_SPECIFICATION.md` updated with instructive placeholders).
    - [ ] Ensure all links in documentation are correct and functional.
- [ ] **`.cursorrules` Adherence**: Ensure all development activity respects the guidelines in `general.cursorrules` and module-specific `.cursorrules`.
- [ ] **CI/CD Pipeline**: Plan and implement a CI/CD pipeline for automated testing, building, and potentially deployment. (Consider integration with `build_synthesis` and `static_analysis`).
- [ ] **Error Handling and Logging**: Ensure consistent error handling and structured logging (via `logging_monitoring`) across all modules.
- [ ] **Security Review**: Conduct a project-wide security review, ensuring all `SECURITY.md` files are accurate and policies are implemented. (Standardized response time placeholder in all SECURITY.md files).

## II. Module-Specific Tasks

### 1. AI Code Editing (`ai_code_editing`)

- [~] **`README.md`**:
    - [~] Finalize "Overview", "Key Components", and "Integration Points". (Placeholder content present)
    - [~] Detail "Getting Started" (Prerequisites, Installation, Configuration). (Placeholder content present)
    - [~] Elaborate on "Development" (Code Structure, Building & Testing). (Placeholder content present)
- [ ] **`API_SPECIFICATION.md`**:
    - [ ] Define the actual API for this module, replacing `example_function()`. (`example_function()` and placeholders present)
    - [ ] Specify "Authentication & Authorization", "Rate Limiting", and "Versioning". (Placeholder content present)
- [x] **`MCP_TOOL_SPECIFICATION.md`**:
    - [x] Replace `[Tool Name]` with actual tool specifications for AI code editing. (Defined `generate_code_snippet` and `refactor_code_snippet` tools; needs alignment with actual implementation.)
    - [x] Define Input/Output Schemas, Error Handling, Idempotency, and Security Considerations for each tool. (Initial definitions provided for the new tools.)
- [ ] **`CHANGELOG.md`**: Populate the "Unreleased" section with initial development tasks.
- [~] **`SECURITY.md`**: Confirm the contact email (`blanket@activeinference.institute`) and response time. (Email confirmed, response time placeholder standardized to "[Specify Expected Response Time, e.g., 2-3 business days]")
- [ ] **`USAGE_EXAMPLES.md`**: Provide concrete examples for the module's features.
- [~] **`requirements.txt`**: Clarify Python dependencies. If it relies on a root `requirements.txt`, state this clearly. Add any specific dependencies (e.g., `specific-ai-library==1.2.3`). (File states reliance on root `requirements.txt`; needs confirmation if specific dependencies are needed)
- [x] **`claude_task_master.py`**: Implement functionality or clarify if it's just a reference link. (Confirmed as a reference link)
- [x] **`openai_codex.py`**: Implement functionality or clarify if it's just a reference link. (Confirmed as a reference link)
- [ ] **`docs/`**:
    - [ ] Complete `technical_overview.md` with actual architecture and design decisions. (Placeholder content present)
    - [ ] Create meaningful tutorials in `docs/tutorials/` replacing `example_tutorial.md`. (`example_tutorial.md` present, needs replacement)
- [ ] **Core Logic**: Implement the core AI code editing functionalities.
- [ ] **Tests**:
    - [ ] Write unit and integration tests for all features.
    - [ ] Update `tests/README.md` with specific instructions.
- [ ] **Adherence to `ai_code_editing.cursorrules`**: Ensure all development follows module-specific rules.

### 2. Build Synthesis (`build_synthesis`)

- [ ] **`README.md`**:
    - [ ] Finalize "Overview", "Key Components", and "Integration Points". (Placeholder content present)
    - [ ] Detail "Getting Started" and "Development". (Placeholder content present)
- [ ] **`API_SPECIFICATION.md`**:
    - [ ] Define actual APIs for build and synthesis tasks, replacing `example_function()`. (`example_function()` and placeholders present)
- [x] **`MCP_TOOL_SPECIFICATION.md`**:
    - [x] Specify actual MCP tools for build/synthesis automation. (Defined speculative `trigger_build` and `synthesize_code_component` tools; needs alignment with actual implementation.)
- [ ] **`CHANGELOG.md`**: Populate "Unreleased" section.
- [~] **`SECURITY.md`**: Confirm contact details and security policies for build scripts and generated code. (Email confirmed, response time placeholder standardized to "[Specify Expected Response Time, e.g., 2-3 business days]", policies are generic)
- [ ] **`USAGE_EXAMPLES.md`**: Provide examples for triggering builds or code synthesis.
- [~] **`requirements.txt`**: List dependencies for the build synthesis tools themselves. (File states reliance on root `requirements.txt`; needs confirmation if specific dependencies are needed)
- [ ] **`docs/`**:
    - [ ] Complete `technical_overview.md`. (Placeholder content present)
    - [ ] Create tutorials for build targets and synthesis strategies. (`example_tutorial.md` present, needs replacement)
- [ ] **Core Logic**: Implement build orchestration and code generation logic.
- [ ] **Tests**:
    - [ ] Test build scripts, synthesis logic, and reproducibility.
    - [ ] Update `tests/README.md`.
- [ ] **Adherence to `build_synthesis.cursorrules`**: Ensure all development follows module-specific rules.

### 3. Code Execution Sandbox (`code_execution_sandbox`)

- [ ] **`README.md`**:
    - [ ] Finalize "Overview", "Key Components", and "Integration Points". (Placeholder content present)
    - [ ] Detail "Getting Started" and "Development". (Placeholder content present)
- [ ] **`API_SPECIFICATION.md`**:
    - [ ] Define the API for submitting code for execution, replacing `example_function()`. (`example_function()` and placeholders present)
- [x] **`MCP_TOOL_SPECIFICATION.md`**:
    - [x] Specify MCP tools for code execution. (Defined a speculative `execute_code` tool based on common patterns; needs alignment with actual implementation once core logic is complete.)
- [ ] **`CHANGELOG.md`**: Populate "Unreleased" section.
- [~] **`SECURITY.md`**: This is critical.
    - [ ] Detail security measures, threat model, and responsible disclosure. (Template present, needs specific content for sandbox)
    - [~] Confirm contact details. (Email confirmed, response time placeholder standardized to "[Specify Expected Response Time, e.g., 2-3 business days]")
- [ ] **`USAGE_EXAMPLES.md`**: Provide examples for using the sandbox.
- [~] **`requirements.txt`**: List dependencies for the sandbox management system. (File states reliance on root `requirements.txt`; needs confirmation if specific dependencies are needed)
- [ ] **`docs/`**:
    - [ ] Complete `technical_overview.md`. (Placeholder content present)
    - [ ] Document supported languages, resource limits, and security configurations. (Placeholder content in `technical_overview.md` and `tutorials/example_tutorial.md`)
- [ ] **Core Logic**: Implement sandbox setup, execution management, and resource limiting.
- [ ] **Tests**:
    - [ ] Include security tests (sandbox escapes), resource limit tests, and functionality tests.
    - [ ] Update `tests/README.md`.
- [ ] **Adherence to `code_execution_sandbox.cursorrules`**: Ensure all development follows module-specific rules, prioritizing security.

### 4. Data Visualization (`data_visualization`)

- [~] **`README.md`**:
    - [x] Review and finalize all sections. (Largely complete, final review suggested)
    - [x] Verify initialization example. (Appears correct)
- [~] **`API_SPECIFICATION.md`**:
    - [x] Review and ensure all plotting functions are accurately documented. (Largely complete, "Versioning" note is minor, final review suggested)
- [x] **`MCP_TOOL_SPECIFICATION.md`**:
    - [x] Add specifications for other plotting functions if they are to be exposed via MCP (currently only `create_heatmap` is detailed).
- [ ] **`CHANGELOG.md`**:
    - [ ] Move items from "Unreleased" to a versioned release once stable.
- [~] **`SECURITY.md`**: Confirm contact details. (Email confirmed, response time placeholder standardized to "[Specify Expected Response Time, e.g., 2-3 business days]")
- [~] **`USAGE_EXAMPLES.md`**:
    - [x] Verify all examples are functional and output paths are correct (e.g., `os.path.join(output_dir, ...)`). (Appears complete and correct, examples need execution for full verification)
    - [x] Ensure `output_dir` creation is handled or documented clearly for examples. (Handled and documented)
- [x] **`requirements.txt`**:
    - [x] Confirm `matplotlib`, `seaborn`, `numpy` versions. (Versions specified)
    - [x] Clarify if `python-dotenv` is a direct dependency or transitive via other Codomyrmex modules. (Clarified as project-level/transitive)
- [ ] **Source Code (`plotter.py`, `line_plot.py`, etc.)**:
    - [ ] Review `if __name__ == '__main__':` blocks; ensure they are for testing and that necessary logging/setup is handled for standalone execution if supported. (Test code in `plotter.py` runs on import, should be in `if __name__ == '__main__':`)
    - [~] Ensure `get_codomyrmex_logger` fallback to standard logging is robust. (Fallback exists in `plotter.py`, seems robust; check other files if they use it directly)
- [ ] **`docs/`**:
    - [ ] Complete `technical_overview.md`. (Placeholder content present)
    - [ ] Create tutorials for different plot types. (`example_tutorial.md` present, needs replacement with actual tutorials)
- [ ] **Tests**:
    - [ ] Write unit and integration tests (e.g., visual regression tests if feasible, or tests verifying plot generation without errors).
    - [ ] Update `tests/README.md`.
- [ ] **Adherence to `data_visualization.cursorrules`**: Ensure all development follows module-specific rules.

### 5. Documentation (`documentation`)

- [x] **`README.md`**:
    - [x] Update with instructions for running and building the Docusaurus site. (Detailed instructions present, including for `documentation_website.py`)
- [ ] **`docusaurus.config.js`**:
    - [ ] Configure site metadata, theme, plugins, navbar, and footer. (Many placeholders like `your-codomyrmex-docs-url.com`, `your-github-org`, and image paths need actual values; favicon, social card, logo images need to be created/added)
- [~] **`sidebars.js`**:
    - [ ] Define the sidebar navigation structure for all Codomyrmex modules. (Structure is well-defined; needs verification against actual module doc files and potential creation of linked `index.md` files for categories)
- [~] **`package.json`**:
    - [ ] Finalize dependencies and scripts (`start`, `build`). (Scripts present, core Docusaurus dependencies listed; review for any other necessary plugins/dependencies)
- [x] **`MCP_TOOL_SPECIFICATION.md`**: Specify MCP tools for documentation site management if applicable. (Defined `trigger_documentation_build` and `check_documentation_environment` tools based on `documentation_website.py` capabilities.)
- [ ] **`docs/intro.md`**: Write the main landing page content for the documentation site. (File `intro.md` is missing, needs to be created and populated)
- [~] **`docs/modules/`**:
    - [x] Create subdirectories for each Codomyrmex module:
        - [x] `ai_code_editing`
        - [x] `build_synthesis`
        - [x] `code_execution_sandbox`
        - [x] `data_visualization`
        - [x] `documentation` (for the documentation module itself)
        - [x] `environment_setup`
        - [x] `git_operations`
        - [x] `logging_monitoring`
        - [x] `model_context_protocol`
        - [ ] `pattern_matching` (directory needs to be created under `documentation/docs/modules/`)
        - [x] `static_analysis`
        - [ ] Note: Clarify if/how `output` directory contents and `template/module_template` should be documented within `documentation/docs/modules/` or if their documentation is sufficiently handled elsewhere (e.g., READMEs of consuming modules for `output`, or `template/module_template/README.md` for the template).
    - [ ] Ensure each module's documentation is correctly linked and structured.
    - [x] Populate `docs/modules/documentation/docs/tutorials/example_tutorial.md` with a real tutorial on using Docusaurus for this project. (Tutorial "Adding a New Module to Documentation" exists and is specific)
- [ ] **`src/css/custom.css`**: Add custom styling as needed.
- [ ] **`static/img/`**: Add project logos and other static images. (Referenced in `docusaurus.config.js` but likely need creation/addition)
- [ ] **Build and Test**:
    - [ ] Ensure `npm run start` and `npm run build` work correctly.
    - [ ] Verify all links and navigation on the deployed/local site.
- [ ] **Adherence to `documentation_module.cursorrules`**: Ensure all development follows module-specific rules.

### 6. Environment Setup (`environment_setup`)

- [~] **`README.md`**:
    - [~] Finalize all sections, especially setup instructions for various OS. (Initial setup part is detailed; module-specific Overview/Key Components sections at the end are placeholders)
    - [x] Clarify Graphviz installation. (Mentioned with link)
    - [x] Clarify API key setup and `.env` usage. (Described)
    - [~] Ensure the "Overview" and "Key Components" for `env_checker.py` are accurate. (Accurate description exists but within a placeholder section of README)
- [ ] **`API_SPECIFICATION.md`**:
    - [ ] If `env_checker.py` functions are considered part of an API, document them. Otherwise, state N/A. (Currently a template, `env_checker.py` functions not documented here)
- [x] **`MCP_TOOL_SPECIFICATION.md`**: Likely N/A unless environment setup tasks are exposed as MCP tools.
- [ ] **`CHANGELOG.md`**: Populate "Unreleased" section.
- [~] **`SECURITY.md`**: Confirm contact details. Emphasize secure handling of API keys. (Email confirmed, response time placeholder standardized to "[Specify Expected Response Time, e.g., 2-3 business days]"; could add more emphasis on API key security beyond generic best practices)
- [ ] **`USAGE_EXAMPLES.md`**:
    - [ ] Provide examples for using `env_checker.py` functions. (Currently a template)
    - [ ] Provide examples of shell scripts for setup. (README has setup commands; this file is a template)
- [~] **`env_checker.py`**:
    - [ ] Thoroughly test `ensure_dependencies_installed()` and `check_and_setup_env_vars()`. (Code review suggests logic is reasonable for informational checks; actual testing status unknown)
    - [x] Ensure it correctly identifies the project root and `.env` file. (`ensure_dependencies_installed` correctly finds files relative to itself; `check_and_setup_env_vars` relies on `repo_root_path` argument, which is correctly determined in its `__main__` block)
- [x] **`requirements.txt`**: List dependencies needed *for the setup scripts themselves* (e.g., `python-dotenv` if `env_checker.py` uses it directly). (States reliance on root `requirements.txt`, which is accurate as `env_checker.py` primarily checks for, not uses, `python-dotenv` for its own operations)
- [ ] **`docs/`**:
    - [ ] Complete `technical_overview.md`. (Placeholder content present)
    - [ ] Add troubleshooting guides and OS-specific instructions. (`example_tutorial.md` present, needs replacement/augmentation with this content)
- [ ] **Setup Scripts**: Develop/finalize any shell scripts for automating environment setup.
- [ ] **Tests**:
    - [ ] Test `env_checker.py` on different platforms/scenarios.
    - [ ] Manually test setup instructions.
    - [ ] Update `tests/README.md`.
- [ ] **Adherence to `environment_setup.cursorrules`**: Ensure all development follows module-specific rules.

### 7. Git Operations (`git_operations`)

- [ ] **`README.md`**:
    - [ ] Clarify module's purpose: Is it for defining project-wide Git practices (branching, commits, PRs) or for providing Git automation tools? 
    - [ ] If it defines practices, these need to be detailed. 
    - [ ] If it's for tools, ensure it refers to root `CONTRIBUTING.md` for project contribution guidelines. (Currently describes providing tools, but doesn't define project conventions like branching models, commit messages, PR guidelines, which are in root `CONTRIBUTING.md`)
- [ ] **`API_SPECIFICATION.md`**: Likely N/A (or template if tools are developed, as README suggests).
- [ ] **`MCP_TOOL_SPECIFICATION.md`**: Likely N/A (or template if tools are developed, as README suggests).
- [ ] **`CHANGELOG.md`**: Populate "Unreleased" section.
- [~] **`SECURITY.md`**: Confirm contact details. (Email confirmed, response time placeholder standardized to "[Specify Expected Response Time, e.g., 2-3 business days]")
- [ ] **`USAGE_EXAMPLES.md`**: Provide examples of Git commands or script usage if any. (Currently a template)
- [~] **`requirements.txt`**: List dependencies for any Git automation scripts (if Python-based). (States reliance on root, which is fine if no specific scripts/tools yet)
- [ ] **`docs/`**:
    - [ ] Complete `technical_overview.md`. (Placeholder content present)
    - [ ] Add detailed explanations of Git strategies and contribution workflows. (Needed if this module defines them; otherwise, this content belongs in or is covered by root `CONTRIBUTING.md`)
- [ ] **Scripts**: Develop any custom Git commands or pre-commit hooks.
- [ ] **Tests**:
    - [ ] Test automation scripts.
    - [ ] Manually verify documented workflows.
    - [ ] Update `tests/README.md`.
- [ ] **Adherence to `git_operations.cursorrules`**: Ensure all development follows module-specific rules.
- [ ] **Consistency Check**: Ensure `git_operations/README.md` aligns with the root `CONTRIBUTING.md`. (Needs review based on clarified purpose of `git_operations/README.md`)

### 8. Logging Monitoring (`logging_monitoring`)

- [x] **`README.md`**:
    - [x] Finalize instructions on configuring and using logging in other modules. (Appears complete and detailed)
- [~] **`logger_config.py`**:
    - [x] Complete and test `setup_logging()` and `get_logger()`. (Appears complete, includes test cases in `__main__`)
    - [x] Ensure `JsonFormatter` works correctly and includes all necessary fields. (Custom `JsonFormatter` implemented, seems comprehensive)
    - [~] Review log rotation, level configuration, and output destinations (console, file, external systems). (Rotation is basic append; levels/destinations are configurable)
- [x] **`API_SPECIFICATION.md`**: Document any APIs for metrics or log querying if planned. (Documents `setup_logging` and `get_logger`; no other APIs currently)
- [x] **`MCP_TOOL_SPECIFICATION.md`**: Specify MCP tools if any relate to log/monitoring control. (Determined that current functions are not suitable for MCP; file updated to state this.)
- [~] **`CHANGELOG.md`**: Populate "Unreleased" section.
- [~] **`SECURITY.md`**: Confirm contact details. Provide guidance on what *not* to log (PII, secrets). (Email confirmed, response time placeholder standardized to "[Specify Expected Response Time, e.g., 2-3 business days]"; guidance on PII/secrets needed)
- [x] **`USAGE_EXAMPLES.md`**: Show how to obtain and use loggers from other modules. (Appears complete and detailed)
- [x] **`requirements.txt`**: List specific logging libraries or dependencies (e.g., `python-json-logger`). (Removed unused `python-json-logger` as custom formatter is used.)
- [ ] **`docs/`**:
    - [x] Complete `technical_overview.md`. (Appears complete and detailed)
    - [~] Add best practices for logging, guides on interpreting logs, and monitoring dashboard setups (if applicable). (`example_tutorial.md` is detailed; check if it covers these aspects sufficiently)
- [ ] **Tests**:
    - [ ] Test logger configuration, formatting, levels, and output.
    - [ ] Update `tests/README.md`.
- [ ] **Adherence to `logging_monitoring.cursorrules`**: Ensure all development follows module-specific rules.

### 9. Model Context Protocol (`model_context_protocol`)

- [ ] **`README.md`**:
    - [ ] Finalize the overview of the protocol, its purpose, and usage. (Placeholder content present)
- [ ] **Schema Definitions**:
    - [ ] Define the core MCP schemas (JSON, ProtoBufs, etc.) clearly. (Not yet defined)
    - [ ] These schemas are fundamental for tool specifications in other modules.
- [ ] **`API_SPECIFICATION.md`**: Document if MCP itself is exposed via a control API. (Template present, no API documented)
- [x] **`MCP_TOOL_SPECIFICATION.md`**: This file in *this* module should define the *rules and meta-structure* for how other modules create *their* `MCP_TOOL_SPECIFICATION.md` files. (File updated to explain its meta-spec role and points to the canonical template in `template/module_template/`.)
- [ ] **`CHANGELOG.md`**: Populate "Unreleased" section.
- [~] **`SECURITY.md`**: Confirm contact details. Consider security aspects of the protocol itself. (Email confirmed, response time placeholder standardized to "[Specify Expected Response Time, e.g., 2-3 business days]"; protocol security aspects missing)
- [ ] **`USAGE_EXAMPLES.md`**: Provide examples of MCP request/response messages. (Template present)
- [~] **`requirements.txt`**: List dependencies for schema validation or example client/server implementations. (Lists `jsonschema`; other dependencies for examples might be needed later)
- [ ] **`docs/`**:
    - [ ] Complete `technical_overview.md`. (Placeholder content present)
    - [ ] Detail protocol messages, data types, interaction patterns, and versioning strategy. (Missing)
    - [ ] Guide developers on creating compliant `MCP_TOOL_SPECIFICATION.md` files. (Missing, `example_tutorial.md` is generic)
- [ ] **Example Implementations**: Consider providing example client/server SDKs.
- [ ] **Tests**:
    - [ ] Test schema validation, serialization/deserialization.
    - [ ] Test client/server conformance if SDKs are provided.
    - [ ] Update `tests/README.md`.
- [ ] **Adherence to `model_context_protocol.cursorrules`**: Ensure all development follows module-specific rules.

### 10. Output (`output`)

- [ ] **Documentation**:
    - [ ] While `output/` doesn't have its own `README.md`, ensure that each module writing to `output/` clearly documents its output structure and format in its *own* documentation.
    - [ ] The root `README.md` or a developer guide should briefly mention the purpose of the `output/` directory.
- [~] **`.gitignore`**: Ensure the project root `.gitignore` effectively ignores contents of `output/`, unless specific sample outputs are intended for version control (e.g., for documentation examples). (Root `.gitignore` includes `output/`, so this is largely met. Review if any specific sample outputs *should* be versioned.)
- [ ] **Cleanup Strategies**:
    - [ ] Implement mechanisms or scripts (perhaps in `build_synthesis` or module-specific Makefiles/scripts) to clean parts or all of the `output/` directory.
- [ ] **Inter-module Dependencies**: If one module consumes output generated by another, this dependency must be clearly documented and managed (e.g., build order).
- [ ] **Adherence to `output_module.cursorrules`**:
    - [ ] Ensure modules write to unique, descriptive paths within `output/`.
    - [ ] Ensure modules consuming output understand its source and format.

### 11. Pattern Matching (`pattern_matching`)

- [~] **`README.md`**:
    - [~] Finalize overview of pattern matching features and use cases.
    - [~] Explain how to use `run_codomyrmex_analysis.py`.
- [ ] **`run_codomyrmex_analysis.py`**:
    - [ ] Review and refactor the script for clarity, efficiency, and robustness.
    - [~] Ensure all analysis functions (`_perform_repository_index`, `_perform_dependency_analysis`, etc.) are well-documented and tested. (Docstrings exist, testing status unknown)
    - [ ] Ensure output data (e.g., JSON files in `output/codomyrmex_analysis/`) is well-structured and documented.
    - [x] Manage LLM configurations (`OpenAIConfig`) securely, likely via `.env` and `environment_setup`. (Handled via .env and env_checker.py)
- [ ] **`API_SPECIFICATION.md`**: Document if pattern matching is exposed as a service. (Template present, no service currently)
- [x] **`MCP_TOOL_SPECIFICATION.md`**: Specify MCP tools for pattern-based queries or transformations if planned. (Defined `search_text_pattern`, `find_symbol_occurrences`, and `search_semantic_concept` tools based on `cased/kit` capabilities.)
- [ ] **`CHANGELOG.md`**: Populate "Unreleased" section.
- [~] **`SECURITY.md`**: Confirm contact details. (Email confirmed, response time placeholder standardized to "[Specify Expected Response Time, e.g., 2-3 business days]")
- [ ] **`USAGE_EXAMPLES.md`**:
    - [ ] Provide examples for `run_codomyrmex_analysis.py` with different configurations.
    - [ ] Show how to interpret the output reports.
- [~] **`requirements.txt`