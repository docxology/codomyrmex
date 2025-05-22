# Codomyrmex: A Modular, Extensible Coding Workspace

This design outlines a modular, extensible coding workspace that integrates open-source tools for building, documenting, analyzing, executing, and visualizing code.

## Core Functional Modules

| Module                                       | Description                                                                 | Key Tools/Technologies                                         | Directory Path                               |
| :------------------------------------------- | :-------------------------------------------------------------------------- | :------------------------------------------------------------- | :------------------------------------------- |
| **Build & Code Synthesis**                   | Manages build processes and AI-powered code generation.                     | build2, OpenAI Codex                                           | [`build_synthesis/`](./build_synthesis/)     |
| **Documentation Website**                  | Generates rich, versioned documentation.                                    | Docusaurus, Material for MkDocs, Sphinx, Read the Docs         | [`documentation/`](./documentation/)         |
| **Static Analysis & Code Checking**        | Centralizes linting, security scanning, and quality metrics.                | analysis-tools.dev, SonarQube, ESLint, CodeQL                  | [`static_analysis/`](./static_analysis/)     |
| **Pattern Matching & Generation**            | Enables exhaustive, type-safe pattern matching (e.g., in TypeScript).     | ts-pattern                                                     | [`pattern_matching/`](./pattern_matching/)   |
| **Logging & Monitoring**                   | Supports structured logging across various languages.                       | SLF4J + Log4j 2 (Java), Zap (Go), Loguru (Python)              | [`logging_monitoring/`](./logging_monitoring/) |
| **Data Visualization**                     | Offers static and interactive plotting capabilities.                        | Matplotlib, Bokeh, Altair, Plotly.py                           | [`data_visualization/`](./data_visualization/) |
| **Code Execution & Sandbox**               | Provides safe, scalable online code execution for multi-language support. | Judge0                                                         | [`code_execution_sandbox/`](./code_execution_sandbox/) |
| **AI-Enhanced Code Editing**               | Embeds AI assistance directly into the developer workflow.                  | VS Code + GitHub Copilot, Cursor, Tabnine                      | [`ai_code_editing/`](./ai_code_editing/)     |

## Core Project Structure & Conventions

| Directory                                    | Purpose                                                                                                |
| :------------------------------------------- | :----------------------------------------------------------------------------------------------------- |
| [`template/`](./template/)                   | Contains templates for modules and common file formats (e.g., README, API specs).                      |
| [`git_operations/`](./git_operations/)       | Houses scripts, configurations, and documentation related to Git workflows and repository management.    |
| [`model_context_protocol/`](./model_context_protocol/) | Defines the schema and protocols for interacting with Large Language Models (LLMs).                |
| [`environment_setup/`](./environment_setup/) | Provides scripts and documentation for setting up local and CI/CD development environments.          |

## Getting Started: Development Environment Setup

This section outlines the general steps to set up the development environment for the **entire Codomyrmex project**.

### Prerequisites

- Python 3.9 or higher
- `pip` (Python package installer)
- `git`
- Node.js (Version 18.0 or higher, for `documentation` module)
- npm or yarn (for `documentation` module)

### Setup Instructions

1.  **Clone the Repository (if you haven't already):**
    ```bash
    git clone <repository_url> # Replace <repository_url> with the actual URL
    cd codomyrmex
    ```

2.  **Create and Activate a Python Virtual Environment:**
    It's highly recommended to use a virtual environment to manage project dependencies.
    ```bash
    python -m venv .venv
    source .venv/bin/activate  # On Windows: .venv\Scripts\activate
    ```

3.  **Install Python Dependencies:**
    The project dependencies, including the `cased/kit` toolkit and `python-dotenv`, are listed in the `requirements.txt` file at the root of the project.
    ```bash
    pip install -r requirements.txt
    ```

4.  **Set Up API Keys (for LLM features):**
    If you plan to use features interacting with Large Language Models (e.g., via `ai_code_editing` or `cased/kit`), you will need API keys for services like OpenAI, Anthropic, or Google Cloud.
    Create a `.env` file in the project root (`codomyrmex/.env`) and add your keys:
    ```env
    OPENAI_API_KEY="sk-..."
    ANTHROPIC_API_KEY="sk-ant-..."
    GOOGLE_API_KEY="AIzaSy..."
    # Add other environment-specific variables here
    ```
    The `python-dotenv` library (installed via `requirements.txt`) will load these variables. The `env_checker.py` script in the `environment_setup` module can help verify this setup.

5.  **Graphviz (Optional for Dependency Visualization):**
    Some modules or tools (like `cased/kit` for dependency graphs) may require Graphviz.
    -   Install the Graphviz system package: [graphviz.org/download/](https://graphviz.org/download/).
    -   Install the Python bindings: `pip install graphviz` (ensure it's in the root `requirements.txt` if widely used).

6.  **Setup for the `documentation` Module (Docusaurus):**
    The project documentation website is built using Docusaurus.
    -   Navigate to the `documentation` directory: `cd documentation`
    -   Install Node.js dependencies: `npm install` (or `yarn install`)
    -   Refer to `documentation/README.md` for commands to run the dev server or build the site.

7.  **Helper Scripts (Optional from `environment_setup` module):**
    The [`environment_setup/scripts/`](./environment_setup/scripts/) directory contains helper scripts:
    -   `setup_dev_env.sh`: Automates several initial setup steps like Python version check, virtual environment creation, and dependency installation. Run it from the project root: `bash environment_setup/scripts/setup_dev_env.sh`.
    -   `install_hooks.sh`: Sets up Git hooks (e.g., pre-commit) by symlinking them from `scripts/git-hooks/` to your local `.git/hooks/` directory. Run it from the project root: `bash environment_setup/scripts/install_hooks.sh`. Customize the hooks in `scripts/git-hooks/` as needed.
    For more details on these scripts and other environment checks, see the [`environment_setup/README.md`](./environment_setup/README.md).

8.  **Running Linters and Tests (General Project):**
    To ensure code quality and correctness across the project:
    - **Linters**: Specific linting commands (e.g., for Pylint, Flake8, ESLint) might be defined per module or run via a project-wide script if available. Generally, you would run linters from the root directory or specific module directories. Example (Python):
        ```bash
        # From project root, linting a specific module
        pylint ai_code_editing/
        flake8 ai_code_editing/
        # Or for the entire project, if configured
        pylint **/*.py
        flake8 .
        ```
    - **Tests**: The project uses `pytest` for Python tests. Run tests from the project root:
        ```bash
        # Run all tests
        pytest
        # Run tests for a specific module
        pytest ai_code_editing/tests/
        # Run tests for a specific file
        pytest ai_code_editing/tests/unit/test_example.py
        ```
    - Refer to individual module `README.md` files or their `tests/README.md` for module-specific testing or linting instructions.

## Project Governance & Contribution

This project is governed by the following documents:

- **[LICENSE](./LICENSE)**: Defines the legal terms under which the project is distributed.
- **[CONTRIBUTING.md](./CONTRIBUTING.md)**: Outlines how to contribute to the project, including setup, PR guidelines, and issue reporting.
- **[CODE_OF_CONDUCT.md](./CODE_OF_CONDUCT.md)**: Sets the standards for behavior within the community to ensure a welcoming and inclusive environment.

We encourage all contributors and users to familiarize themselves with these documents.

This modular framework aims to unify these functions into a cohesive package, leveraging proven GitHub-backed projects to enable extensibility, maintainability, and support for polyglot development workflows. 