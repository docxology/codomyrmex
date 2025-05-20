# Codomyrmex Project TO-DO List

This document outlines the tasks required to complete the Codomyrmex project. It is organized into general project-wide tasks and module-specific tasks.

## I. General Project-Wide Tasks

- [~] **Overall Architecture Review**: Ensure a clear and consistent architecture across all modules. (Initial review suggests a modular architecture. Deeper consistency to be verified during module-specific reviews.)
- [ ] **Dependency Management**: Enforce version pinning in all `requirements.txt` files.
    - [ ] Update root `requirements.txt` to use exact versions for all dependencies (e.g., `openai==X.Y.Z` instead of `openai>=X.Y.Z`).
    - [ ] Review and update all module-specific `requirements.txt` files to use exact versions for their dependencies.
    - [ ] Ensure module `requirements.txt` files correctly state reliance on the root file or list only truly specific dependencies with pinned versions.
- [ ] **Testing Strategy**: 
    - [ ] Define and document a project-wide testing strategy (unit, integration, E2E).
    - [x] Ensure all modules have a `tests/README.md` with clear instructions.
    - [ ] Strive for high test coverage across all modules.
- [~] **Documentation Consistency**:
    - [ ] Ensure all modules have complete and consistent documentation (`README.md`, `API_SPECIFICATION.md`, `MCP_TOOL_SPECIFICATION.md`, `CHANGELOG.md`, `SECURITY.md`, `USAGE_EXAMPLES.md`, `docs/`). (File existence verified for all modules; content and consistency handled by module-specific tasks).
    - [~] Remove all placeholder content (e.g., "(Provide a concise overview...)", "`[Tool Name]`"). (Standardized "[e.g., 48 hours]" in all SECURITY.md files; `template/module_template/MCP_TOOL_SPECIFICATION.md` updated with instructive placeholders; further placeholder removal tracked in module-specific tasks).
    - [~] Ensure all links in documentation are correct and functional. (Fixed inconsistent file naming pattern in sidebars.js to match actual files; updated cross-module links to use correct paths).
- [ ] **`.cursorrules` Adherence**: 
    - [x] Root `general.cursorrules` exists.
    - [ ] Ensure each module has its own `[module_name]/.cursor/.cursorrules` file, based on `template/module_template/.cursor/.cursorrules`.
    - [ ] Clean up `ai_code_editing/.cursor/` directory: it contains copies of rules for many other modules, which is incorrect. It should only contain its own `.cursorrules`.
    - [ ] Verify other modules for correct `.cursor/.cursorrules` placement.
    - [ ] Ensure development activity respects these guidelines (ongoing).
- [~] **CI/CD Pipeline**: Plan and implement a CI/CD pipeline for automated testing, building, and potentially deployment. (Consider integration with `build_synthesis` and `static_analysis`).
- [ ] **Error Handling and Logging**: Ensure consistent error handling and structured logging (via `logging_monitoring`) across all modules.
    - [ ] Audit all relevant Python-based modules to ensure they use `get_logger` from the `logging_monitoring` module.
    - [ ] Define and document project-wide best practices for error handling (e.g., when to raise exceptions, how to format error messages for logs).
- [ ] **Security Review**: Conduct a project-wide security review.
    - [~] All modules have a `SECURITY.md` file. (Verified)
    - [~] Contact email and response time placeholders standardized in all `SECURITY.md` files. (As per previous notes)
    - [ ] Ensure each module's `SECURITY.md` accurately reflects its specific threats, mitigation strategies, and responsible disclosure process, replacing template content where necessary.
    - [ ] Implement security policies outlined in `SECURITY.md` files across modules (ongoing).
- [ ] **Update Project URLs**:
    - [x] Update placeholder URLs (YOUR_USERNAME) in `CONTRIBUTING.md`. (Replaced with `codomyrmex-project-org` as a placeholder, confirm if a specific org/user is intended).
    - [x] Update placeholder URLs (yourusername) and empty `author` field in `package.json`. (Replaced `yourusername` with `codomyrmex-project-org` and author with `Codomyrmex Team`. Confirm if specific values are intended).

## II. Module-Specific Tasks

### 1. AI Code Editing (`ai_code_editing`)

- [x] **`README.md`**: (Content largely complete; updated placeholder URL)
    - [x] Finalize "Overview", "Key Components", and "Integration Points". (Content reviewed and seems comprehensive)
    - [x] Detail "Getting Started" (Prerequisites, Installation, Configuration). (Content reviewed, seems comprehensive, placeholder URL updated)
    - [x] Elaborate on "Development" (Code Structure, Building & Testing). (Content reviewed and seems comprehensive)
- [x] **`API_SPECIFICATION.md`**: (Functions `generate_code_snippet`, `refactor_code_snippet` are defined; Auth, Rate Limiting, Versioning sections are present and specific)
    - [x] Define the actual API for this module, replacing `example_function()`. (Actual functions are documented)
    - [x] Specify "Authentication & Authorization", "Rate Limiting", and "Versioning". (Sections are present and contain specific information)
- [x] **`MCP_TOOL_SPECIFICATION.md`**:
    - [x] Replace `[Tool Name]` with actual tool specifications for AI code editing. (Defined `generate_code_snippet` and `refactor_code_snippet` tools; needs alignment with actual implementation.)
    - [x] Define Input/Output Schemas, Error Handling, Idempotency, and Security Considerations for each tool. (Initial definitions provided for the new tools.)
- [x] **`CHANGELOG.md`**: Populate the "Unreleased" section with initial development tasks.
- [~] **`SECURITY.md`**: Confirm the contact email (`blanket@activeinference.institute`) and response time. (Email confirmed, response time placeholder standardized to "[Specify Expected Response Time, e.g., 2-3 business days]")
- [x] **`USAGE_EXAMPLES.md`**: Provide concrete examples for the module's features. (Examples are comprehensive; minor TODOs remain for "Common Pitfalls" section).
- [x] **`requirements.txt`**: Clarify Python dependencies. If it relies on a root `requirements.txt`, state this clearly. Add any specific dependencies (e.g., `specific-ai-library==1.2.3`). (File states reliance on root and lists `tiktoken`. Version pinning is a general task.)
- [x] **`claude_task_master.py`**: Implement functionality or clarify if it's just a reference link. (Confirmed as a reference link)
- [x] **`openai_codex.py`**: Implement functionality or clarify if it's just a reference link. (Confirmed as a reference link)
- [ ] **`docs/`**:
    - [ ] Complete `technical_overview.md` with actual architecture and design decisions. (Placeholder content present, needs filling)
    - [ ] Create meaningful tutorials in `docs/tutorials/` (e.g., for `generate_code_snippet` and `refactor_code_snippet`), replacing or augmenting `example_tutorial.md`.
- [~] **Core Logic**: Implement the core AI code editing functionalities. (Initial implementation for `generate_code_snippet` and `refactor_code_snippet` exists in `ai_code_helpers.py`; further enhancements and features may be needed.)
- [ ] **Tests**:
    - [ ] Write unit and integration tests for all features. (Some unit tests exist in `test_ai_code_helpers.py`)
    - [x] Update `tests/README.md` with specific instructions. (File is comprehensive and provides good instructions)
- [~] **Adherence to `ai_code_editing.cursorrules`**: Ensure all development follows module-specific rules. (Module-specific .cursorrules file exists at `ai_code_editing/.cursor/ai_code_editing.cursorrules`. Adherence is ongoing.)

### 2. Build Synthesis (`build_synthesis`)

- [x] **`README.md`**: (Content largely complete; updated placeholder URL)
    - [x] Finalize "Overview", "Key Components", and "Integration Points". (Content reviewed and seems comprehensive)
    - [x] Detail "Getting Started" and "Development". (Content reviewed, seems comprehensive, placeholder URL updated)
- [ ] **`API_SPECIFICATION.md`**:
    - [ ] Define actual APIs for build and synthesis tasks, replacing `example_function()`. (`example_function()` and placeholders present)
- [x] **`MCP_TOOL_SPECIFICATION.md`**:
    - [x] Specify actual MCP tools for build/synthesis automation. (Defined speculative `trigger_build` and `synthesize_code_component` tools; needs alignment with actual implementation.)
- [x] **`CHANGELOG.md`**: Populate "Unreleased" section.
- [~] **`SECURITY.md`**: Confirm contact details and security policies for build scripts and generated code. (Email confirmed, response time placeholder standardized to "[Specify Expected Response Time, e.g., 2-3 business days]", policies are generic)
- [x] **`USAGE_EXAMPLES.md`**: Provide examples for triggering builds or code synthesis. (File contains good conceptual examples for `trigger_build` and `synthesize_code_component` MCP tools; minor TODOs for path/name realism remain.)
- [x] **`requirements.txt`**: List dependencies for the build synthesis tools themselves. (File states reliance on root `requirements.txt` and explicitly notes no additional specific dependencies currently. Version pinning is a general task.)
- [ ] **`docs/`**:
    - [ ] Complete `technical_overview.md`. (Placeholder content present, needs filling)
    - [ ] Create meaningful tutorials in `docs/tutorials/` (e.g., for common build targets like Python wheels/Docker, and for code synthesis using `synthesize_code_component`), replacing or augmenting `example_tutorial.md`.
- [ ] **Core Logic**: Implement build orchestration and code generation logic.
- [ ] **Tests**:
    - [ ] Test build scripts, synthesis logic, and reproducibility.
    - [x] Update `tests/README.md` with specific instructions. (File updated with more specific guidance)
- [ ] **Adherence to `build_synthesis.cursorrules`**: Ensure all development follows module-specific rules.
    - [ ] Create `build_synthesis/.cursor/.cursorrules` file from `template/module_template/.cursor/.cursorrules`.
    - [ ] Ensure development activity respects these guidelines (ongoing).

### 3. Code Execution Sandbox (`code_execution_sandbox`)

- [x] **`README.md`**: (Content largely complete and specific; updated placeholder URL)
    - [x] Finalize "Overview", "Key Components", and "Integration Points". (Content reviewed and seems comprehensive and specific to the module)
    - [x] Detail "Getting Started" and "Development". (Content reviewed, seems comprehensive and specific, placeholder URL updated)
- [x] **`API_SPECIFICATION.md`**: (Detailed `execute_code` function and supporting details are well-defined, not a template.)
    - [x] Define the API for submitting code for execution, replacing `example_function()`. (Actual `execute_code` function is documented in detail.)
- [x] **`MCP_TOOL_SPECIFICATION.md`**:
    - [x] Specify MCP tools for code execution. (Tool `execute_code` is comprehensively specified; alignment with implementation is an ongoing concern for any spec.)
- [x] **`CHANGELOG.md`**: Populate "Unreleased" section. (Populated with initial setup based on documentation state)
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
    - [ ] Ensure development activity respects these guidelines (ongoing).

### 4. Data Visualization (`