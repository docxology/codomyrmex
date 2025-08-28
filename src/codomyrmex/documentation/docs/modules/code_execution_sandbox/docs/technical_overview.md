# Code Execution Sandbox - Technical Overview

This document provides a detailed technical overview of the Code Execution Sandbox module. Its primary role is the secure execution of untrusted code, making its architecture and design choices critical for the overall security of the Codomyrmex project.

## 1. Introduction and Purpose

The Code Execution Sandbox module provides a heavily restricted and isolated environment for running arbitrary code snippets, typically received from other modules (like AI Code Editing) or external systems via MCP tool calls. It solves the problem of safely evaluating code whose behavior and intent are unknown or untrusted. Key responsibilities include:

-   **Strong Isolation**: Preventing sandboxed code from accessing or harming the host system, other sandboxed instances, or any unauthorized resources.
-   **Strict Resource Limiting**: Enforcing limits on CPU, memory, execution time, and other resources to prevent Denial of Service (DoS) and ensure fair usage.
-   **Language Agnostic Execution**: Supporting multiple programming languages, each within its own tailored and hardened runtime environment.
-   **Secure Result Reporting**: Safely capturing and returning execution outputs (stdout, stderr), exit codes, and status information.

## 2. Architecture

The architecture is centered around containerization, using **Docker as the reference sandboxing technology**. The module orchestrates Docker containers to execute code snippets.

- **Key Components/Sub-modules**: 
  - **`SandboxManager`**: Responsible for the lifecycle of sandbox instances (Docker containers). This includes:
      - Pulling/managing pre-built, hardened Docker images for each supported language.
      - Creating new containers per execution request with appropriate security configurations (resource limits, network policies, read-only rootfs, seccomp profiles, etc.).
      - Securely destroying containers and their ephemeral storage after execution.
  - **`ExecutionOrchestrator`**: Handles an `execute_code` MCP request. It coordinates with other components to:
      - Select the correct Docker image based on the requested `language`.
      - Prepare the code snippet and any `stdin` for injection into the container.
      - Instruct the `SandboxManager` to create and start the container.
      - Monitor the container for timeout and collect results.
  - **`ResourceLimiter` (Integrated into `SandboxManager` logic)**: Configures Docker to enforce CPU, memory, PID, and execution time limits. Timeouts are typically managed by the `ExecutionOrchestrator` by setting a timer and forcibly stopping the container if it exceeds the allocated time.
  - **`LanguageRuntimeProvider`**: Implicitly, this is the set of versioned, security-hardened Docker images (e.g., `codomyrmex/sandbox-python:3.10-slim`, `codomyrmex/sandbox-node:18-alpine`). Each image contains a specific language runtime and minimal necessary dependencies.
  - **`ResultCollector`**: Gathers stdout, stderr, and the exit code from the Docker container logs and termination status. It also calculates or retrieves execution time.
  - **`McpToolImplementations`**: The Python code that implements the `execute_code` MCP tool, acting as the entry point and using the other components.

- **Data Flow** (for an `execute_code` request):
    1. MCP request (language, code, stdin, timeout) arrives at `McpToolImplementations`.
    2. `ExecutionOrchestrator` validates the request (e.g., supported language, timeout within global max).
    3. `ExecutionOrchestrator` requests a sandbox instance from `SandboxManager` for the specified language.
    4. `SandboxManager` pulls the relevant Docker image (if not cached locally) and starts a new Docker container with strict security options (e.g., `--read-only`, `--network=none`, resource limits, `--no-new-privileges`, custom seccomp profile, unprivileged user).
    5. The `code` snippet is typically written to a file in an ephemeral, mounted volume or passed directly to the container's entrypoint/command. `stdin` is piped to the container.
    6. The container executes the code using the specified language runtime.
    7. `ExecutionOrchestrator` monitors execution time. `ResultCollector` streams/retrieves stdout/stderr from container logs.
    8. Upon completion, timeout, or error, `SandboxManager` stops and removes the container and its ephemeral storage.
    9. `ResultCollector` finalizes results (exit code, actual execution time).
    10. `McpToolImplementations` formats and returns the MCP response.

- **Core Logic**: 
    - Securely constructing `docker run` commands with all necessary security flags.
    - Managing Docker image versions and updates.
    - Implementing a robust timeout mechanism that ensures container termination.
    - Parsing and securely handling outputs from containers.

- **External Dependencies**: 
    - **Docker Engine**: The Docker daemon must be running on the host.
    - **`docker` Python SDK**: For programmatic interaction with the Docker daemon from Python.
    - Pre-built language-specific Docker images.

```mermaid
flowchart TD
    A[MCP Request: execute_code (lang, code, stdin, timeout)] --> McpImpl[McpToolImplementations];
    McpImpl --> Orch[ExecutionOrchestrator];
    Orch -- Validates & Prepares --> Orch;
    Orch -- Requests Sandbox for lang --> Mgr[SandboxManager];
    Mgr -- Pulls/Selects --> Img[Language Docker Image];
    Mgr -- Creates & Configures w/ Security Opts --> Cont[(Docker Container Instance)];
    Orch -- Injects code & stdin --> Cont;
    Cont -- Executes Code --> Cont;
    Orch -- Monitors (Timeout) & Collects Results --> Cont;
    ResColl[ResultCollector] -- Gets stdout/stderr/exit_code from --> Cont;
    Mgr -- Stops & Destroys --> Cont;
    Orch -- Aggregates Results from ResColl --> Orch;
    McpImpl -- Returns Formatted --> Resp[MCP Response: stdout, stderr, exit_code, status, exec_time];
```

## 3. Design Decisions and Rationale

-   **Choice of Docker for Sandboxing**: Docker is widely adopted, well-documented, and provides strong OS-level virtualization capabilities (namespaces, cgroups). While not a perfect security boundary against kernel exploits, its features (`--no-new-privileges`, seccomp, AppArmor, user namespacing, read-only rootfs, resource limits) offer substantial defense in depth when configured correctly. It also simplifies managing different language runtimes via images.
-   **Ephemeral, Single-Use Containers**: Each `execute_code` request ideally spins up a fresh, new container instance. This minimizes the risk of state leakage or interference between executions. Containers are destroyed immediately after use.
-   **Default Deny Network Access**: `--network=none` is the default for containers, as most code execution tasks do not require external connectivity. This drastically reduces the attack surface.
-   **Read-Only Root Filesystem**: `--read-only` for the container's root filesystem prevents the sandboxed code from modifying its own runtime environment, enhancing integrity and consistency.
-   **Unprivileged Execution**: Code within containers runs as a non-root user (e.g., `nobody` or a dedicated `sandbox_user` UID/GID) to limit potential damage even if other layers are bypassed.
-   **Strict Resource Limits by Default**: Default CPU, memory, and timeout limits are conservative to prevent abuse. These are configurable by administrators but capped.
-   **Centralized Image Management**: Language runtimes are provided as specific, versioned Docker images that are built/managed with security in mind (minimal layers, vulnerability scanning, regular updates).

## 4. Supported Languages and Runtimes

The sandbox supports a defined set of programming languages and versions, each provided by a specific, hardened Docker image. Administrators configure this list. Examples:

-   **Python**: 
    -   `python3.10`: Provided by image `codomyrmex/sandbox-python:3.10.12-slim-bullseye` (example name)
    -   `python3.9`: Provided by image `codomyrmex/sandbox-python:3.9.17-slim-bullseye`
-   **JavaScript**: 
    -   `nodejs18`: Provided by image `codomyrmex/sandbox-node:18.17.1-alpine`
-   **Bash (or generic shell script)**:
    -   `bash`: Provided by a minimal image like `codomyrmex/sandbox-bash:5.1-alpine` (based on `alpine` with `bash` installed).

The `execute_code` tool's `language` parameter must match one of the configured and available language runtimes.

## 5. Configuration

Secure configuration is critical. Key configuration options managed by administrators (not typically via MCP tool parameters, which are validated against these global settings):

-   **`SANDBOX_GLOBAL_MAX_TIMEOUT_SECONDS`**: (integer) e.g., `300`. Absolute maximum execution timeout allowed for any request.
-   **`SANDBOX_DEFAULT_TIMEOUT_SECONDS`**: (integer) e.g., `30`. Default timeout if not specified in the request.
-   **`SANDBOX_DEFAULT_MEMORY_LIMIT_MB`**: (integer) e.g., `256`. Default memory limit (e.g. Docker's `--memory`).
-   **`SANDBOX_DEFAULT_CPU_QUOTA_PERCENT`**: (integer) e.g., `50` (for 0.5 CPU core). Docker's `--cpus` or equivalent.
-   **`SANDBOX_PID_LIMIT`**: (integer) e.g., `100`. Docker's `--pids-limit`.
-   **`SANDBOX_LANGUAGE_CONFIG_FILE`**: (string) Path to a JSON/YAML file defining supported languages, their corresponding Docker image tags, and potentially language-specific default resource limits or security profiles (e.g., specific seccomp profile).
    *Example entry in `sandbox_languages.json`*:
    ```json
    {
      "python3.10": {
        "image": "codomyrmex/sandbox-python:3.10.12-slim-bullseye",
        "seccomp_profile": "python3.json", // Path to custom seccomp profile
        "default_memory_mb": 256
      },
      "nodejs18": {
        "image": "codomyrmex/sandbox-node:18.17.1-alpine",
        "seccomp_profile": "default.json",
        "default_memory_mb": 192,
        "allow_network": false // Explicitly state default, or override if a lang needs restricted net
      }
    }
    ```
-   **`DOCKER_SOCKET_PATH`**: (string, if applicable) Path to the Docker daemon socket (e.g., `unix:///var/run/docker.sock`).
-   **`SANDBOX_DEFAULT_USER_UID_GID`**: (string) e.g., `"1000:1000"` or `"nobody"`. User to run code as inside container.

These configurations are detailed further in the module's `SECURITY.md`.

## 6. Scalability and Performance

-   **Concurrency**: The module should be designed to handle multiple concurrent `execute_code` requests. The number of concurrent sandboxes is limited by host resources (CPU, memory) and Docker daemon performance.
-   **Startup Overhead**: Docker container startup introduces latency. For very frequent, short-lived executions, this can be a bottleneck. Strategies like maintaining a small pool of pre-warmed, generic sandbox containers might be considered for future optimization, but this significantly complicates security (state leakage, reuse risks) and is not a default assumption.
-   **Resource Contention**: High load can lead to resource contention on the host. Proper sizing of the host and careful configuration of per-sandbox resource limits are essential.

## 7. Security Aspects (Module Internals)

This section supplements the main `SECURITY.md` with focus on implementation details.

-   **Isolation Guarantees & Limitations (Docker)**: Docker uses Linux namespaces (pid, net, mnt, uts, ipc, user) and cgroups for isolation. This is OS-level virtualization. It protects against most user-space attacks but is vulnerable to kernel exploits. User namespaces (`--userns-remap`) further mitigate this by mapping container root to an unprivileged host user.
-   **Kernel Attack Surface Minimization**: Achieved via:
    -   `--no-new-privileges`: Prevents privilege escalation.
    -   `seccomp`: Custom profiles drastically limit available syscalls.
    -   `--cap-drop=ALL`: Drop all Linux capabilities, adding back only if absolutely essential for a specific runtime (rare).
    -   AppArmor/SELinux profiles for Docker provide an additional layer of mandatory access control.
-   **Secure Image/Runtime Management**: Docker images for languages are built from official minimal bases, have unnecessary tools removed, are regularly scanned for vulnerabilities (e.g., with Trivy, Clair), and version-pinned. Updates are rolled out systematically.
-   **Data Exfiltration Prevention**: Primarily via `--network=none`. If restricted network access is ever enabled for a specific language runtime, it must use strict egress filtering and allow-list specific target IPs/ports. No inbound connections.
-   **Side-channel Attacks**: While sophisticated hardware side-channels (Spectre, Meltdown) are best mitigated at the OS/hypervisor/hardware level, the sandbox design does not introduce obvious software-based timing or cache side-channels in its orchestration logic. The risk primarily lies within the executed code itself or the shared kernel if not fully patched.
-   **Logging & Auditing for Security**: Critical events are logged via `logging_monitoring`:
    -   Every `execute_code` request (caller, language, code hash, resource settings).
    -   Sandbox instance creation/destruction (container ID, image used).
    -   Resource limit enforcement actions (e.g., OOM kills by Docker, timeout terminations by module).
    -   Any errors during sandbox setup or execution.
    -   If kernel logs seccomp violations or AppArmor denials related to sandbox containers, these should be correlated if possible.

## 8. Future Development / Roadmap

-   **Support for More Languages/Runtimes**: Systematically adding new, hardened language images based on demand.
-   **Pluggable Sandboxing Backends**: Abstracting the `SandboxManager` to potentially support other sandboxing technologies beyond Docker (e.g., gVisor, Firecracker, Wasm runtimes) for different security/performance trade-offs.
-   **Finer-Grained Network Policies**: If network access is needed, allowing more declarative, per-execution rule definitions (subject to strict admin approval and overrides).
-   **Filesystem Provisioning**: A secure mechanism to provide read-only input files to the sandbox beyond stdin, or to retrieve larger output files beyond stdout.
-   **Pre-warmed Sandbox Pools (Advanced)**: For very high-throughput, low-latency scenarios, explore secure pooling mechanisms with extreme caution regarding state isolation.
