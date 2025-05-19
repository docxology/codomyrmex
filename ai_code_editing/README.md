# Ai Code Editing

## Overview

The AI Code Editing module is a core component of the Codomyrmex project, designed to provide intelligent capabilities for understanding, generating, and modifying source code. It leverages artificial intelligence models and techniques to assist developers with tasks such as code completion, refactoring, bug detection, code summarization, and automated generation of code snippets or entire functions. This module aims to enhance developer productivity and improve code quality through AI-powered assistance.

## Key Components

- **Large Language Model (LLM) Connectors**: Interfaces to various LLMs (e.g., OpenAI GPT models, Anthropic Claude models) for code generation, understanding, and modification tasks.
- **Prompt Engineering & Management**: Utilities and templates for crafting effective prompts to guide LLM behavior for specific code editing tasks (e.g., refactoring, summarization, generation).
- **Code Parsing and Representation**: Tools or libraries (potentially leveraging `cased/kit` or tree-sitter) to parse source code into abstract syntax trees (ASTs) or other structured representations for analysis and manipulation.
- **Context Retrieval Mechanisms**: Systems to gather relevant code context (e.g., surrounding code, definitions, documentation) to provide to LLMs, improving the quality and relevance of their outputs.
- **Code Transformation Engine**: Logic for applying AI-suggested changes back to the source code, potentially including formatting and validation steps.
- **MCP Tool Implementations**: Specific implementations of tools exposed via the Model Context Protocol, such as `generate_code_snippet` and `refactor_code_snippet`, which orchestrate the above components.
- **Reference Implementations/Examples**: Links to or simplified versions of integrations like `claude_task_master.py` or `openai_codex.py` (as mentioned in TO-DO, these are currently reference links).

## Integration Points

This module is central to AI-assisted development and interacts extensively:

- **Provides:**
    - **Generated Code Snippets/Functions**: Produces new code based on prompts or specifications.
    - **Refactored Code**: Modifies existing code to improve clarity, performance, or to address issues.
    - **Code Summaries & Explanations**: Generates natural language descriptions of code functionality.
    - **Bug Detection/Suggestions**: Identifies potential bugs and may suggest fixes.
    - **MCP Tools**: Exposes functionalities like `generate_code_snippet` and `refactor_code_snippet` through the Model Context Protocol (see `MCP_TOOL_SPECIFICATION.md`).

- **Consumes:**
    - **Source Code**: Takes existing source code from the project or specific files as input for analysis, refactoring, or as context for generation.
    - **User Prompts/Instructions**: Natural language or structured requests from users or other systems detailing the desired code editing task.
    - **LLM Services**: Interfaces with external Large Language Model APIs (e.g., OpenAI, Anthropic) as the core engine for its intelligent capabilities.
    - **`pattern_matching` module / `cased/kit`**: May use these to retrieve relevant code context, find symbol definitions, or understand codebase structure to inform AI tasks.
    - **`code_execution_sandbox` module**: Potentially submits generated or refactored code to the sandbox for validation, testing, or to ensure it runs correctly before finalizing changes.
    - **`logging_monitoring` module**: For logging AI interactions, prompt details (anonymized if necessary), generated outputs, and errors.
    - **`model_context_protocol` module**: Adheres to MCP for defining its exposed tools and for potentially consuming tools from other modules.
    - **`environment_setup` module**: To ensure API keys for LLM services are properly configured.

- Refer to the [API Specification](API_SPECIFICATION.md) and [MCP Tool Specification](MCP_TOOL_SPECIFICATION.md) for detailed programmatic interfaces.)

## Getting Started

To use the AI Code Editing module, ensure that the Codomyrmex development environment is set up according to the instructions in the main project `README.md` and the `environment_setup` module. This module's functionalities are primarily accessed through its MCP tools or potentially direct API calls if exposed.

### Prerequisites

- **Python Environment**: Python 3.8+ (as per general project guidelines, confirm with root `requirements.txt` or `environment_setup`).
- **LLM API Keys**: Valid API keys for the desired Large Language Model providers (e.g., OpenAI, Anthropic) must be configured as environment variables. Refer to the `environment_setup` module for guidance on managing environment variables (e.g., via a `.env` file).
- **Dependencies**: This module relies on dependencies listed in `requirements.txt` (and potentially the root `requirements.txt`). Ensure these are installed. Key conceptual dependencies include:
    - An LLM provider SDK (e.g., `openai`, `anthropic`).
    - Libraries for code parsing/analysis if used (e.g., `tree-sitter` or `cased/kit` if integrated).
- **MCP Integration**: Understanding of the Model Context Protocol (MCP) is necessary if interacting with its exposed tools (`generate_code_snippet`, `refactor_code_snippet`).

### Installation

This module is part of the Codomyrmex project. Clone the main repository to get this module.

1.  **Clone the Repository**:
    ```bash
    git clone https://github.com/your-org/codomyrmex.git
    cd codomyrmex
    ```
2.  **Set up Environment**: Follow instructions in `environment_setup/README.md` to prepare your Python environment and install dependencies from `requirements.txt` (root and module-specific if any).
    ```bash
    # Example commands (adapt based on environment_setup)
    python -m venv .venv
    source .venv/bin/activate
    pip install -r requirements.txt
    pip install -r ai_code_editing/requirements.txt # If it has specific deps
    ```
3.  **Configure API Keys**: Ensure your LLM API keys (e.g., `OPENAI_API_KEY`) are set in your environment (e.g., in a `.env` file at the project root).

### Configuration

- **LLM Provider and Model**: The choice of LLM provider (e.g., "openai", "anthropic") and specific model (e.g., "gpt-4", "claude-2") can often be specified when calling MCP tools like `generate_code_snippet` or `refactor_code_snippet`. If not specified, defaults configured within the module's implementation will be used.
- **Environment Variables**: Key configurations, especially sensitive ones like API keys, are managed through environment variables. Refer to `environment_setup/README.md` and `MCP_TOOL_SPECIFICATION.md` for details on required variables.

## Development

Developers contributing to this module should familiarize themselves with its architecture, dependencies, and the overall Codomyrmex project structure.

### Code Structure

The `ai_code_editing` module's primary logic is expected to reside within its source directory (e.g., Python files directly under `ai_code_editing/` or in a nested `src/` or `ai_code_editing_src/` subdirectory if established).
Key files and directories include:
- `README.md`: This file.
- `API_SPECIFICATION.md`: Describes any direct APIs. Currently a template.
- `MCP_TOOL_SPECIFICATION.md`: Details the `generate_code_snippet` and `refactor_code_snippet` tools.
- `requirements.txt`: Module-specific Python dependencies.
- `docs/`: Contains detailed documentation, including:
    - `technical_overview.md`: Architectural details of the module.
    - `tutorials/`: How-to guides for using module features.
- `tests/`: Contains unit and integration tests.
- `__init__.py`: Makes the directory a Python package.
- Reference files like `claude_task_master.py` and `openai_codex.py` are currently external links, indicating potential integration patterns or inspirations.

For a more detailed architectural view, see the [Technical Overview](./docs/technical_overview.md).

### Building & Testing

This module, being primarily Python-based, does not have a separate "build" step in the traditional compilation sense. Testing is crucial.

1.  **Install Dependencies**: Ensure all development dependencies are installed (including those in the root `requirements.txt` and this module's `ai_code_editing/requirements.txt`).
2.  **Run Tests**: Execute tests using the project's preferred test runner (e.g., `pytest`). Refer to `ai_code_editing/tests/README.md` for specific instructions.
    ```bash
    # Example using pytest (adapt as needed)
    pytest ai_code_editing/tests/unit
    pytest ai_code_editing/tests/integration
    ```
    - Unit tests (`tests/unit`) should mock external LLM calls to ensure deterministic behavior.
    - Integration tests (`tests/integration`) might involve actual (sandboxed or limited) calls to LLM APIs, requiring API key configuration.

Ensure that any contributions pass all relevant tests and adhere to the coding standards outlined in `.cursorrules` files and the project's `CONTRIBUTING.md`.

## Further Information

- [API Specification](API_SPECIFICATION.md)
- [MCP Tool Specification](MCP_TOOL_SPECIFICATION.md) (If this module exposes tools via MCP)
- [Usage Examples](USAGE_EXAMPLES.md)
- [Detailed Documentation](./docs/index.md)
- [Changelog](CHANGELOG.md)
- [Security Policy](SECURITY.md) 