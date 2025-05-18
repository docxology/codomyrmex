# Environment Setup for Codomyrmex

This document outlines the steps to set up the development environment for the Codomyrmex project.

## Prerequisites

- Python 3.9 or higher
- `pip` (Python package installer)
- `git`

## Setup Instructions

1.  **Clone the Repository (if you haven't already):**
    ```bash
    git clone <repository_url>
    cd codomyrmex
    ```

2.  **Create and Activate a Virtual Environment:**
    It's highly recommended to use a virtual environment to manage project dependencies.
    ```bash
    python -m venv .venv
    source .venv/bin/activate  # On Windows: .venv\Scripts\activate
    ```

3.  **Install Dependencies:**
    The project dependencies, including the `cased/kit` toolkit, are listed in the `requirements.txt` file at the root of the project.
    ```bash
    pip install -r requirements.txt
    ```

4.  **Graphviz (Optional for Dependency Visualization):**
    Some modules, like those for visualizing code dependencies using `cased/kit`, may require Graphviz.
    -   Install the Graphviz system package. Instructions can be found at [graphviz.org](https://graphviz.org/download/).
    -   Then, install the Python bindings (uncomment `graphviz` in `requirements.txt` or install separately):
        ```bash
        pip install graphviz
        ```

5.  **API Keys (Optional for LLM features):**
    If you plan to use features of `cased/kit` that interact with Large Language Models (e.g., code summarization, docstring indexing with LLM-generated summaries), you will need to set up API keys for the respective services (OpenAI, Anthropic, Google Cloud).
    Set these as environment variables:
    ```bash
    export OPENAI_API_KEY="sk-..."
    export ANTHROPIC_API_KEY="sk-ant-..."
    export GOOGLE_API_KEY="AIzaSy..."
    ```

## Documentation Site Development (Using Docusaurus)

The main documentation website is built using Docusaurus and is managed within the `documentation/` module. To work on or build the documentation site locally:

### Prerequisites for Documentation

- **Node.js**: Version 18.0 or higher is recommended. You can download it from [nodejs.org](https://nodejs.org/) or use a version manager like [nvm](https://github.com/nvm-sh/nvm).
- **npm** (usually comes with Node.js) or **yarn**.

### Setting up the Documentation Environment

1.  **Navigate to the `documentation` module directory:**
    ```bash
    cd ../documentation  # Assuming you are in the root 'codomyrmex' directory, or adjust path accordingly
    ```

2.  **Install Docusaurus dependencies:**
    ```bash
    npm install
    # OR if you prefer yarn
    # yarn install
    ```

3.  **Run the Docusaurus development server:**
    ```bash
    npm run start
    # OR
    # yarn start
    ```
    This will typically start the site at `http://localhost:3000`.

4.  **Build the static documentation site:**
    ```bash
    npm run build
    # OR
    # yarn build
    ```
    The output will be in `documentation/build/`.

Refer to the `documentation/README.md` for more details on the Docusaurus setup and structure.

## Using `cased/kit`

The `cased/kit` toolkit is a core component for many modules within this project. It provides functionalities for:
- Codebase mapping and symbol extraction
- Text and semantic code search
- Dependency analysis
- Code summarization
- Building context for LLMs

Refer to the documentation of individual modules for specific examples of how `cased/kit` is utilized. The official `cased/kit` documentation (as provided in our project context) is also a key resource.

## Overview

(Provide a concise overview of this module, its purpose, and its core functionalities within the Codomyrmex ecosystem.)

## Key Components

(List and briefly describe the key sub-components, libraries, or tools utilized or developed within this module.)

- Component A: ...
- Component B: ...
- **`env_checker.py`**: Provides utility functions to check for core dependencies (like `cased/kit`, `python-dotenv`) and to guide users in setting up `.env` files for API keys. These functions are designed to be imported and used by other modules within the Codomyrmex project to ensure a consistent environment.

## Integration Points

(Describe how this module interacts with other parts of the Codomyrmex system or external services.
- **Provides:**
    - From `env_checker.py`:
        - `ensure_dependencies_installed()`: A function to verify that essential project dependencies are available.
        - `check_and_setup_env_vars(repo_root_path: str)`: A function to check for the presence of a `.env` file and provide guidance for creating it, particularly for LLM API keys.
    - General guidance and scripts for setting up the overall Codomyrmex development environment.
- **Consumes:**
    - Python standard library (`os`, `sys`).
    - `cased/kit` (for checking its presence).
    - `python-dotenv` (for checking its presence and for loading `.env` files if this module were to use them directly, though `env_checker.py` primarily guides other modules).
- Refer to the [API Specification](API_SPECIFICATION.md) and [MCP Tool Specification](MCP_TOOL_SPECIFICATION.md) for detailed programmatic interfaces.)

## Getting Started

(Provide instructions on how to set up, configure, and use this module.)

### Prerequisites

(List any dependencies or prerequisites required to use or develop this module.)

### Installation

(Provide installation steps, if applicable.)

### Configuration

(Detail any necessary configuration steps.)

## Development

(Information for developers contributing to this module.)

### Code Structure

(Briefly describe the organization of code within this module. For a more detailed architectural view, see the [Technical Overview](./docs/technical_overview.md).)

### Building & Testing

(Instructions for building and running tests for this module.)

## Further Information

- [API Specification](API_SPECIFICATION.md)
- [MCP Tool Specification](MCP_TOOL_SPECIFICATION.md) (If this module exposes tools via MCP)
- [Usage Examples](USAGE_EXAMPLES.md)
- [Detailed Documentation](./docs/index.md)
- [Changelog](CHANGELOG.md)
- [Security Policy](SECURITY.md) 