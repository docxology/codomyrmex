# Code Execution Sandbox

## Overview

The Code Execution Sandbox module provides a secure and isolated environment for running untrusted or dynamically generated code. Its primary function is to allow code execution while strictly controlling its access to system resources, network, and file system, thereby preventing malicious actions and ensuring the stability of the host system. This is crucial for features that involve code generation or execution based on external inputs, such as AI-assisted coding or plugin systems.

## Key Components

- **Isolation Mechanism**: The core technology used to create isolated environments (e.g., Docker containers, `nsjail`, `firecracker`, WebAssembly runtimes, or other process/VM-based isolation techniques).
- **Resource Management & Limiting**: Components responsible for defining and enforcing limits on CPU usage, memory allocation, execution time, network access, and file system operations for sandboxed code.
- **Code Submission API**: An interface (likely HTTP-based or via MCP) for submitting code snippets or packages to be executed within the sandbox.
- **Results Retrieval API**: An interface for securely retrieving execution outputs, standard streams (stdout/stderr), and error information from the sandbox.
- **Security Policy Engine**: Mechanisms for defining and enforcing fine-grained security policies, specifying what operations are permitted or denied within the sandbox.
- **Language Runtimes & Environments**: Pre-configured environments within the sandbox supporting one or more programming languages/versions (e.g., Python, JavaScript).
- **Monitoring and Logging**: Secure logging of sandbox activities and resource usage for auditing and debugging, integrated with the `logging_monitoring` module.

## Integration Points

This module is critical for securely running code and interacts as follows:

- **Provides:**
    - **Secure Execution Environment**: Offers an isolated sandbox where untrusted or dynamically generated code can be run with restricted permissions.
    - **Code Execution API**: An interface (e.g., HTTP or through MCP tool `execute_code`) for submitting code, specifying language, and providing inputs.
    - **Execution Results**: Returns outputs from the executed code, including standard output, standard error, return values, and execution status (success, failure, timeout).
    - **MCP Tool (`execute_code`)**: A standardized way for AI agents or other modules to request code execution via the Model Context Protocol (see `MCP_TOOL_SPECIFICATION.md`).

- **Consumes:**
    - **Code Submissions**: Receives code snippets or packages for execution, potentially from modules like `ai_code_editing` (e.g., AI-generated code) or other modules that need to run dynamic scripts.
    - **Security Policies**: Configurations defining resource limits (CPU, memory, time), allowed system calls, network access rules, and file system permissions for the sandboxed environment.
    - **`logging_monitoring` module**: For securely logging sandbox creation, code execution events, resource usage, security alerts, and errors.
    - **`model_context_protocol` module**: Adheres to MCP for defining the `execute_code` tool.
    - **Language Runtimes/Images**: May consume pre-built container images or runtime environments for various supported languages.

- Refer to the [API Specification](API_SPECIFICATION.md) and [MCP Tool Specification](MCP_TOOL_SPECIFICATION.md) for detailed programmatic interfaces.)

## Getting Started

Using the Code Execution Sandbox involves setting up the required sandboxing technology (e.g., Docker) and then interacting with the module, typically via its MCP tool `execute_code`.

**Crucial Security Note**: This module is highly security-sensitive. Extreme care must be taken in its deployment, configuration, and use. Always refer to `SECURITY.md` and `code_execution_sandbox.cursorrules`.

### Prerequisites

- **Codomyrmex Environment**: A fully configured Codomyrmex development environment (see `environment_setup/README.md`).
- **Isolation Technology**: The specific sandboxing technology chosen for implementation must be installed and operational on the host system. For example:
    - If using Docker: Docker daemon must be running.
    - If using `nsjail` or similar: The tool and its dependencies must be installed.
- **Supported Language Runtimes**: The sandbox must be pre-configured with runtimes for the languages it intends to support (e.g., Python, Node.js). This might involve having specific Docker images available or runtime binaries accessible within the sandbox's controlled environment.
- **Dependencies**: This module relies on dependencies listed in `requirements.txt` (and potentially the root `requirements.txt`). Ensure these are installed. Example: `docker` Python library if Docker is the chosen backend.

### Installation

This module is part of the Codomyrmex project. Ensure the main project is cloned and the environment is set up.

1.  **Clone the Repository**: If not already done:
    ```bash
    git clone https://github.com/codomyrmex-project-org/codomyrmex.git
    cd codomyrmex
    ```
2.  **Set up Environment**: Follow instructions in `environment_setup/README.md`.
    ```bash
    # Example commands (adapt based on environment_setup)
    python -m venv .venv
    source .venv/bin/activate
    pip install -r requirements.txt
    pip install -r code_execution_sandbox/requirements.txt # If it has specific deps like 'docker'
    ```
3.  **Configure Sandboxing Backend**: Ensure the chosen sandboxing technology (e.g., Docker) is installed and configured on your system.

### Configuration

- **Resource Limits**: CPU, memory, time, and network access limits are critical configurations. These are typically defined within the module's implementation and may be adjustable via configuration files or environment variables. See `docs/technical_overview.md` for potential configuration points.
- **Supported Languages**: The list of supported languages and their versions within the sandbox is a key configuration, often managed by providing appropriate runtime environments (e.g., Docker images).
- **Network Policies**: Default to NO network access. Any allowed network access must be explicitly configured and justified.
- **Filesystem Access**: Default to NO host filesystem access. Any temporary file storage must be within a jailed, ephemeral directory.
- **MCP Tool Parameters**: The `execute_code` tool has parameters like `timeout` which have default values but can be overridden per request, within global limits set by the module's configuration. Refer to `MCP_TOOL_SPECIFICATION.md`.

## Development

Developers working on this module MUST prioritize security above all else. Every change needs rigorous security review.

### Code Structure

The `code_execution_sandbox` module contains:
- `README.md`: This file.
- `API_SPECIFICATION.md`: Describes direct APIs (currently a template).
- `MCP_TOOL_SPECIFICATION.md`: Defines the critical `execute_code` MCP tool.
- `SECURITY.md`: **Crucial reading for any developer.** Outlines security policies and considerations.
- `requirements.txt`: Module-specific Python dependencies (e.g., `docker` library).
- Source code for managing the chosen isolation mechanism, handling code execution requests, and enforcing resource limits.
- `docs/`: Detailed documentation, including `technical_overview.md` (which should detail the sandboxing mechanism) and `tutorials/`.
- `tests/`: Extensive unit, integration, and **especially security-focused tests**.

For a more detailed architectural view, see the [Technical Overview](./docs/technical_overview.md).

### Building & Testing

- **Building**: If using containerization (like Docker), "building" may involve creating or pulling specific Docker images that provide the sandboxed language runtimes.
- **Testing**: Testing for this module is paramount and must be comprehensive.
    - **Unit Tests (`tests/unit`)**: Test individual components, such as request parsing or result formatting, mocking the actual execution environment.
    - **Integration Tests (`tests/integration`)**: Test the full execution flow with the chosen sandboxing technology. This will involve running benign code snippets in various supported languages and verifying:
        - Correct stdout/stderr/exit_code.
        - Enforcement of resource limits (CPU time, memory).
        - Network isolation (attempts to access external resources should fail by default).
        - Filesystem isolation.
    - **Security Tests**: Design tests specifically to probe for vulnerabilities, such as attempted sandbox escapes or unauthorized resource access. These are often adversarial in nature.
    - Refer to `code_execution_sandbox/tests/README.md` for detailed instructions.
    ```bash
    # Example using pytest (adapt as needed)
    pytest code_execution_sandbox/tests/unit
    pytest code_execution_sandbox/tests/integration
    # Additional commands for security-specific tests might be defined.
    ```

All contributions must pass stringent security reviews and all tests.

## Further Information

- [API Specification](API_SPECIFICATION.md)
- [MCP Tool Specification](MCP_TOOL_SPECIFICATION.md) (If this module exposes tools via MCP)
- [Usage Examples](USAGE_EXAMPLES.md)
- [Detailed Documentation](./docs/index.md)
- [Changelog](CHANGELOG.md)
- [Security Policy](SECURITY.md) 