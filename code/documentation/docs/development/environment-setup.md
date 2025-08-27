---
id: environment-setup
title: Environment Setup
sidebar_label: Environment Setup
---

# Environment Setup for Codomyrmex

This document outlines the steps to set up the development environment for the Codomyrmex project.

## Core Prerequisites

- Python 3.9 or higher
- `pip` (Python package installer)
- `git`

## Core Project Setup Instructions

1.  **Clone the Repository (if you haven't already):**
    ```bash
    git clone <repository_url> # Replace <repository_url> with the actual URL
    cd codomyrmex
    ```

2.  **Create and Activate a Virtual Environment:**
    It's highly recommended to use a virtual environment to manage project dependencies.
    ```bash
    python -m venv .venv
    source .venv/bin/activate  # On Windows: .venv\Scripts\activate
    ```

3.  **Install Core Dependencies:**
    The project dependencies, including the `cased/kit` toolkit, are listed in the `requirements.txt` file at the root of the project.
    ```bash
    pip install -r requirements.txt
    ```

4.  **Graphviz (Optional for Dependency Visualization):**
    Some modules, like those for visualizing code dependencies using `cased/kit`, may require Graphviz.
    -   Install the Graphviz system package. Instructions can be found at [graphviz.org](https://graphviz.org/download/).
    -   Then, install the Python bindings (uncomment `graphviz` in the root `requirements.txt` or install separately):
        ```bash
        pip install graphviz
        ```

5.  **API Keys (Optional for LLM features):**
    If you plan to use features of `cased/kit` that interact with Large Language Models (e.g., code summarization, docstring indexing with LLM-generated summaries), you will need to set up API keys for the respective services (OpenAI, Anthropic, Google Cloud).
    Set these as environment variables. It is recommended to create a `.env` file in the root of your repository (`codomyrmex/.env`) with the following format:
    ```
    # .env file example
    OPENAI_API_KEY="your_openai_api_key_here"
    ANTHROPIC_API_KEY="your_anthropic_api_key_here"
    GOOGLE_API_KEY="your_google_api_key_here"
    # Add other environment variables as needed
    ```
    The `environment_setup/env_checker.py` script can help guide you on this, and the system will attempt to load these using `python-dotenv`.

## Documentation Site Development (Using Docusaurus)

The main documentation website is built using Docusaurus and is managed within the `documentation/` module. To work on or build the documentation site locally:

### Prerequisites for Documentation

- **Node.js**: Version 18.0 or higher is recommended. You can download it from [nodejs.org](https://nodejs.org/) or use a version manager like [nvm](https://github.com/nvm-sh/nvm).
- **npm** (usually comes with Node.js) or **yarn**.

### Setting up the Documentation Environment

1.  **Navigate to the `documentation` module directory:**
    ```bash
    cd documentation  # From the root 'codomyrmex' directory
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

Refer to the `documentation/README.md` (inside the `documentation` module directory) for more details on the Docusaurus setup and structure.

## Using `cased/kit`

The `cased/kit` toolkit is a core component for many modules within this project. It provides functionalities for:
- Codebase mapping and symbol extraction
- Text and semantic code search
- Dependency analysis
- Code summarization
- Building context for LLMs

Refer to the documentation of individual modules for specific examples of how `cased/kit` is utilized. The official `cased/kit` documentation is also a key resource. 