---
sidebar_label: 'Environment Setup'
title: 'Environment Setup Module'
slug: /modules/environment_setup
---

# Environment Setup for Codomyrmex

This document outlines the steps to set up the development environment for the Codomyrmex project.

## Prerequisites

- Python 3.9 or higher
- `pip` (Python package installer)
- `git`

## Setup Instructions

1.  **Clone the Repository (if you haven't already):**
    ```bash
    git clone <repository_url> # Replace <repository_url> with the actual URL
    cd codomyrmex
    ```

2.  **Create and Activate a Python Virtual Environment:**
    It's highly recommended to use a virtual environment to manage project dependencies.
    ```bash
    python -m venv .venv
    source .venv/bin/activate  # On Windows: .venv\\Scripts\\activate
    ```

3.  **Install Python Dependencies:**
    The project dependencies are listed in the `requirements.txt` file at the root of the project.
    ```bash
    pip install -r requirements.txt
    ```

4.  **Graphviz (Optional for Dependency Visualization):**
    Some modules may require Graphviz for visualizing dependencies.
    -   Install the Graphviz system package. Instructions can be found at [graphviz.org](https://graphviz.org/download/).
    -   Then, install the Python bindings:
        ```bash
        pip install graphviz
        ```

5.  **API Keys (Optional for LLM features):**
    If you plan to use features interacting with Large Language Models, set up API keys for the respective services (OpenAI, Anthropic, Google Cloud) as environment variables:
    ```bash
    export OPENAI_API_KEY="your-openai-api-key"
    export ANTHROPIC_API_KEY="your-anthropic-api-key"
    export GOOGLE_API_KEY="your-google-api-key"
    ```
    Consult the `.env.example` file for more details if available, or store these in a `.env` file at the project root.

## Documentation Site Development (Using Docusaurus)

The main documentation website is built using Docusaurus and is managed within the `documentation` module. To work on or build the documentation site locally:

### Prerequisites for Documentation

- **Node.js**: Version 18.0 or higher is recommended. You can download it from [nodejs.org](https://nodejs.org/) or use a version manager like [nvm](https://github.com/nvm-sh/nvm).
- **npm** (usually comes with Node.js) or **yarn**.

### Setting up the Documentation Environment

1.  **Navigate to the `documentation` module directory:**
    ```bash
    cd documentation  # Assuming you are in the root 'codomyrmex' directory
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

Refer to the [Documentation Module documentation](../documentation/index.md) for more details on the Docusaurus setup and structure.

## Key Components of this Module

- `env_checker.py`: A script to verify that the development environment meets the project's requirements (e.g., Python version, installed dependencies). (Hypothetical, actual implementation may vary).
- This `README.md` (and its Docusaurus counterpart): Provides the primary setup instructions.

## Further Information

- [API Specification](./api_specification.md)
- [MCP Tool Specification](./mcp_tool_specification.md) 
- [Usage Examples](./usage_examples.md)
- [Detailed Documentation for this module](./docs/index.md)
- [Changelog](./changelog.md)
- [Security Policy](./security.md) 