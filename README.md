# Codomyrmex: A Modular, Extensible Coding Workspace

**🚀 NOW FULLY FUNCTIONAL!** A complete, modular coding workspace that integrates the latest open-source tools for building, documenting, analyzing, executing, and visualizing code. Uses cutting-edge package versions for optimal performance.

## Quick Start 🚀

**Codomyrmex is now functional!** Here's how to get started in under 5 minutes:

### 1. Automated Setup
```bash
# Clone and setup everything automatically
git clone https://github.com/codomyrmex/codomyrmex.git
cd codomyrmex
bash code/environment_setup/scripts/setup_dev_env.sh
```

### 2. Manual Setup (Alternative)
```bash
# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -e .

# Check setup
codomyrmex check
```

### 3. Verify Installation
```bash
codomyrmex info     # See project overview
codomyrmex check    # Verify environment setup
```

### 4. Start Using Modules
```bash
# Run the example script to see everything working
python example_usage.py
```

Or try individual modules:
```python
# Example: Use data visualization
from codomyrmex.code.data_visualization import create_line_plot
import numpy as np

x = np.linspace(0, 10, 100)
y = np.sin(x)
create_line_plot(x, y, title="Sample Plot", output_path="plot.png")
```

**✅ What's Working Now:**
- Environment setup and dependency management (latest versions)
- Logging and monitoring system
- Data visualization (plots, charts, graphs)
- Static analysis tools (pylint, flake8, bandit)
- CLI interface for quick checks
- Modular architecture with proper imports
- AI/LLM integration (OpenAI, Anthropic, Google)
- Code execution capabilities
- Testing framework
- All with latest package versions!

**🔄 Future Enhancements:**
- Advanced AI code editing workflows
- Build synthesis automation
- Documentation website (Docusaurus)
- Git operations integration
- Additional visualization types

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

## 📚 Documentation & Resources

### **Complete Documentation Suite**
- **[📖 Full Documentation](code/documentation/README.md)** - Comprehensive guides, tutorials, and API references
- **[🏗️ Architecture Overview](code/documentation/docs/project/architecture.md)** - System design and data flow
- **[🧪 Testing Strategy](code/documentation/docs/project/TESTING_STRATEGY.md)** - Quality assurance approach
- **[🤝 Contributing Guide](code/documentation/docs/project/contributing.md)** - How to contribute effectively
- **[🔧 Module Interdependencies](MODULE_RELATIONSHIPS.md)** - How modules work together
- **[🚀 Quick Start Guide](QUICKSTART.md)** - Get running in 3 minutes
- **[🔍 Troubleshooting Guide](TROUBLESHOOTING.md)** - Common issues and solutions

### **Module-Specific Documentation**
| Module | Documentation | API Reference | Tutorials |
|--------|---------------|---------------|-----------|
| **AI Code Editing** | [📚 Docs](code/documentation/docs/modules/ai_code_editing/) | [🔌 API](code/documentation/docs/modules/ai_code_editing/api_specification.md) | [🎓 Tutorials](code/documentation/docs/modules/ai_code_editing/docs/tutorials/) |
| **Data Visualization** | [📚 Docs](code/documentation/docs/modules/data_visualization/) | [🔌 API](code/documentation/docs/modules/data_visualization/api_specification.md) | [🎓 Tutorials](code/documentation/docs/modules/data_visualization/docs/tutorials/) |
| **Code Execution** | [📚 Docs](code/documentation/docs/modules/code_execution_sandbox/) | [🔌 API](code/documentation/docs/modules/code_execution_sandbox/api_specification.md) | [🎓 Tutorials](code/documentation/docs/modules/code_execution_sandbox/docs/tutorials/) |
| **Pattern Matching** | [📚 Docs](code/documentation/docs/modules/pattern_matching/) | [🔌 API](code/documentation/docs/modules/pattern_matching/pattern-matching-api-specification.md) | [🎓 Tutorials](code/documentation/docs/modules/pattern_matching/docs/tutorials/) |
| **Static Analysis** | [📚 Docs](code/documentation/docs/modules/static_analysis/) | [🔌 API](code/documentation/docs/modules/static_analysis/api_specification.md) | [🎓 Tutorials](code/documentation/docs/modules/static_analysis/docs/tutorials/) |

## Getting Started: Development Environment Setup

This section outlines the general steps to set up the development environment for the **entire Codomyrmex project**.

### Prerequisites

- Python 3.10 or higher (uses latest package versions for best performance)
- `pip` (Python package installer) OR `uv` (recommended - faster and more reliable)
- `git`
- Node.js (Version 18.0 or higher, for `documentation` module)
- npm or yarn (for `documentation` module)

**Note:** `uv` is a fast Python package manager that can replace pip and virtualenv. It's highly recommended for this project. Install it from https://github.com/astral-sh/uv

### Setup Instructions

1.  **Clone the Repository (if you haven't already):**
    ```bash
    git clone <repository_url> # Replace <repository_url> with the actual URL
    cd codomyrmex
    ```

2.  **Set up Python Environment:**

    **Option A: Using uv (Recommended - Faster and More Reliable)**
    ```bash
    # Install uv if you haven't already (visit https://github.com/astral-sh/uv)
    # Create and activate virtual environment
    uv venv .venv
    source .venv/bin/activate  # On Windows: .venv\Scripts\activate

    # Install dependencies
    uv pip install -e .
    ```

    **Option B: Using pip (Traditional Method)**
    ```bash
    # Create and activate virtual environment
    python -m venv .venv
    source .venv/bin/activate  # On Windows: .venv\Scripts\activate

    # Install dependencies
    pip install -r requirements.txt
    ```

    **Option C: Automated Setup Script**
    ```bash
    # Run the automated setup script (supports both uv and pip)
    bash environment_setup/scripts/setup_dev_env.sh
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
    - **Tests**: The project uses `pytest` for Python tests with coverage reporting. Run tests from the project root:
    ```bash
    # Run all tests with coverage
    pytest

    # Run tests for a specific module
    pytest testing/unit/test_ai_code_editing.py

    # Run tests for a specific file
    pytest testing/unit/test_ai_code_editing.py::TestAICodeEditing::test_ai_code_helpers_import

    # Run with coverage report
    pytest --cov-report=html
    open testing/htmlcov/index.html  # View coverage report in browser
    ```
- Refer to individual module `README.md` files or their `tests/README.md` for module-specific testing or linting instructions.

## Project Governance & Contribution

This project is governed by the following documents:

- **[LICENSE](./LICENSE)**: Defines the legal terms under which the project is distributed.
- **[CONTRIBUTING.md](./CONTRIBUTING.md)**: Outlines how to contribute to the project, including setup, PR guidelines, and issue reporting.
- **[CODE_OF_CONDUCT.md](./CODE_OF_CONDUCT.md)**: Sets the standards for behavior within the community to ensure a welcoming and inclusive environment.

We encourage all contributors and users to familiarize themselves with these documents.

This modular framework aims to unify these functions into a cohesive package, leveraging proven GitHub-backed projects to enable extensibility, maintainability, and support for polyglot development workflows. 