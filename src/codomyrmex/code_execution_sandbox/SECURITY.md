# Security Policy for Code Execution Sandbox

This document outlines security procedures, policies, and critical considerations for the Code Execution Sandbox module. **This module is highly security-sensitive.** Its primary purpose is to execute untrusted code, and therefore, its design, implementation, configuration, and usage must prioritize security above all else.

## 1. Introduction

The Code Execution Sandbox module is designed to run arbitrary code snippets in an isolated environment. This functionality is inherently risky. This security policy details the measures taken to mitigate these risks and provides guidance for secure operation and development. All users and developers of this module must read and understand this document.

## 2. Core Security Principles

The design and operation of the Code Execution Sandbox adhere to the following core security principles:

-   **Least Privilege**: Sandboxed code runs with the minimum set of permissions and resource access necessary for its intended tasks. By default, permissions are denied.
-   **Defense in Depth**: Multiple layers of security controls are employed. If one layer fails, others should still contain the threat.
-   **Secure Defaults**: Default configurations are the most secure (e.g., no network access, minimal resource limits).
-   **Complete Mediation**: Every attempt by sandboxed code to access resources or perform sensitive operations is validated.
-   **Isolate Components**: The sandbox environment is strongly isolated from the host system and from other sandbox instances.
-   **Minimize Attack Surface**: The sandbox environment and its supporting components expose the smallest possible attack surface.

## 3. Sandboxing Technology & Approach

The primary sandboxing approach assumes the use of **containerization technology, with Docker being a reference implementation.** The principles outlined here apply broadly to any robust sandboxing mechanism (e.g., gVisor, Firecracker, nsjail).

Key security configurations and practices for a Docker-based sandbox include:

-   **Unprivileged Containers**: Containers should run as a non-root user. This can be achieved using the `USER` directive in the Dockerfile or the `--user` flag when running the container. Avoid running the Docker daemon itself as root where possible (rootless Docker).
-   **No New Privileges**: The `--no-new-privileges` Docker option is crucial to prevent sandboxed processes from gaining more privileges than their parent process.
-   **Read-Only Root Filesystem**: Container root filesystems are mounted as read-only (`--read-only`) to prevent modification of the base image contents by the untrusted code.
-   **Minimal & Updated Base Images**: Language runtime images are minimal ("slim" or "alpine" variants where feasible) and are regularly updated to include the latest security patches for the OS and language runtime.
-   **Seccomp Profiles**: Custom, restrictive `seccomp` (secure computing mode) profiles are applied to limit the system calls available to the container to only those absolutely necessary for the supported language runtimes.
-   **AppArmor/SELinux**: Mandatory Access Control systems like AppArmor or SELinux should be configured with profiles to further confine container capabilities, if available on the host.
-   **Strict Resource Limits**: Enforce limits on CPU (e.g., `--cpus`, `--cpu-shares`), memory (`--memory`, `--memory-swap`), Process IDs (`--pids-limit`), and execution time (managed by an external watchdog within the module).
-   **Network Isolation**:
    -   Default: No network access (`--network=none`).
    -   If network access is essential for a specific, trusted use case and language, it must be explicitly enabled and restricted to a dedicated, non-host network with strict egress filtering (allow-listing specific IPs/ports). No inbound connections to the sandbox.
-   **Ephemeral & Isolated Storage**:
    -   Writable storage for the sandboxed code is restricted to an ephemeral, isolated directory (e.g., a `tmpfs` mount within the container at `/sandbox_tmp` or a dedicated working directory).
    -   This storage is size-limited and its contents are destroyed when the sandbox instance terminates.
-   **No Sensitive Volume Mounts**: No host directories containing sensitive information or system files are mounted into the sandbox. Any required input files are securely copied into the ephemeral storage area.

## 4. Threat Model

The threat model considers adversaries attempting to compromise the host system or other services by exploiting the code execution sandbox.

### 4.1. Code-Based Threats (from submitted code)

-   **Sandbox Escape**: Malicious code exploits a vulnerability in the sandboxing technology (e.g., Docker, container runtime, Linux kernel) or its configuration to gain unauthorized access to the host system or other containers.
-   **Resource Exhaustion (Denial of Service - DoS)**: Code consumes excessive CPU, memory, disk space (in its ephemeral storage), PIDs, or network bandwidth, degrading performance or denying service to the host or other sandboxed instances. This includes fork bombs or infinite loops.
-   **Data Exfiltration**: If network access is mistakenly or overly permitted, or if a partial escape occurs, code attempts to send sensitive data (if any were inadvertently made accessible) from the host or its own environment to an external location.
-   **Data Tampering/Destruction**: Code attempts to modify the host filesystem (if escape occurs) or, more likely, interfere with the operation of the sandbox orchestrator if any communication channels are exploitable.
-   **Cryptojacking/Unauthorized Computation**: Code uses allocated CPU/GPU resources for unauthorized purposes like cryptocurrency mining.
-   **Network Attacks**: If network access is enabled, code attempts to scan the internal network, attack other services on the host, or launch attacks against external targets.
-   **Information Gathering**: Code attempts to discover information about the host environment, kernel version, running processes, or network configuration to aid in an escape or further attack.

### 4.2. Infrastructure/Configuration Threats

-   **Misconfiguration of Sandbox**: Weak resource limits, overly permissive seccomp/AppArmor profiles, unnecessary capabilities granted to containers, running containers as root, vulnerabilities in custom entrypoint scripts.
-   **Vulnerabilities in Sandboxing Technology**: Undisclosed (0-day) or unpatched vulnerabilities in Docker, containerd, runc, the Linux kernel, or other underlying virtualization/isolation components.
-   **Vulnerabilities in Language Runtimes**: Exploitable flaws in the Python interpreter, Node.js runtime, or other supported language environments pre-packaged within the sandbox images.
-   **Vulnerabilities in Orchestration Logic**: Flaws in the Code Execution Sandbox module itself (e.g., in how it handles inputs, manages containers, or parses outputs) that could be exploited.

## 5. Key Security Measures & Mitigations

This section details specific technical measures to mitigate the identified threats.

-   **Strong Isolation (Primary Mitigation for Escape)**:
    -   Leverage Linux namespaces (PID, MNT, NET, IPC, UTS, User) and cgroups provided by containerization.
    -   User Namespaces: Map container users to unprivileged users on the host to reduce impact even if an escape to the host kernel occurs.
-   **Strict Resource Limiting (Primary Mitigation for DoS)**:
    -   CPU: Enforce CPU quotas (e.g., `--cpus` in Docker) and shares.
    -   Memory: Hard memory limits (`--memory`) and disabled/limited swap (`--memory-swap`).
    -   Execution Time: An external watchdog implemented by this module terminates code/containers exceeding a configurable timeout.
    -   PID Limits: `--pids-limit` in Docker to prevent fork bombs.
    -   Disk Space: Ephemeral storage (e.g., `tmpfs` mounts) is inherently limited in size.
-   **System Call Filtering (Reduces Attack Surface)**:
    -   Use custom `seccomp` profiles for Docker containers, allowing only the syscalls essential for the specific language runtime and typical benign code execution. Deny dangerous syscalls like `mount`, `reboot`, `kexec_load`, `add_key`, etc.
-   **Filesystem Controls (Prevents Unauthorized Access/Modification)**:
    -   Container root filesystem is `--read-only`.
    -   Code executes in a dedicated, non-persistent working directory (e.g., `/app` or `/sandbox_tmp`) with restricted write access.
    -   No direct mounting of host paths. Data needed by the code is securely copied into the container's ephemeral storage.
-   **Network Controls (Prevents Unauthorized Network Activity)**:
    -   Default to `--network=none` in Docker.
    -   If network access is required for a specific language (e.g., Python with `requests` for a *trusted* external API call defined by the system, not by user code), use a custom, restricted Docker network with strict egress filtering.
    -   Block all inbound connections to the sandbox.
-   **Privilege Reduction (Reduces Impact of Potential Compromise)**:
    -   Containers run with `--no-new-privileges`.
    -   Processes inside the container run as a dedicated, unprivileged user (e.g., `USER nobody` in Dockerfile or `--user <uid>:<gid>`).
    -   Drop all unnecessary Linux capabilities (e.g., `docker run --cap-drop=ALL --cap-add=<minimal_set_if_any>`).
-   **Secure Base Images & Runtimes**:
    -   Use official, minimal base images (e.g., `python:slim-bullseye`, `node:alpine`).
    -   Regularly update base images and language runtimes to patch known vulnerabilities.
    -   Scan images using tools like Trivy or Clair as part of the image build pipeline.
    -   Remove unnecessary packages, compilers, or tools from the final sandbox images.
-   **Input Validation**:
    -   Validate parameters controlling execution, such as language choice, to ensure they match supported and secured runtimes.
    -   Resource limit requests via API/MCP are capped by global maximums defined in the module's secure configuration.
-   **Secure Output Handling**:
    -   Treat stdout/stderr from the sandbox as potentially malicious. Sanitize or escape it before display or further processing, especially if rendered in HTML/JS contexts.
-   **Robust Monitoring & Logging**:
    -   Integrate with the `logging_monitoring` module for comprehensive logging of:
        -   Sandbox creation/deletion events.
        -   Code submission details (language, redacted code/hash).
        -   Resource limit settings per instance.
        -   Actual resource consumption (CPU, memory peak).
        -   Execution success/failure, timeouts.
        -   Any security-relevant events (e.g., seccomp violations if logged by the kernel, AppArmor denials).
    -   Implement alerts for suspicious patterns (e.g., repeated crashes, high resource usage near limits, specific error messages indicating potential attack).

## 6. Supported Languages & Runtimes Security

-   Each supported language (e.g., Python 3.10, Node.js 18) has its own pre-built, hardened sandbox image.
-   Language runtimes are kept updated. The update process for these images includes security scanning.
-   Language-specific execution flags for enhanced security are used where appropriate (e.g., Python's isolated mode `-I` if applicable, though full isolation is primarily by the container).
-   Be aware of language features that are inherently risky (e.g., `pickle` in Python, `eval` in many languages). The sandbox aims to contain these, but code patterns using them are still suspect.

## 7. Known Limitations & Assumptions

-   **Container Escapes / Kernel Exploits**: The security of the sandbox ultimately relies on the strength of the Linux kernel and the containerization technology (e.g., Docker, runc). A zero-day vulnerability in these components could lead to a full sandbox escape. Mitigation: Keep host OS, kernel, and Docker updated.
-   **Sophisticated Side-Channel Attacks**: Attacks exploiting CPU hardware vulnerabilities (e.g., Spectre, Meltdown) or other microarchitectural side channels are generally outside the scope of what this software-based sandbox can prevent. Mitigation: Host-level mitigations for such hardware flaws.
-   **Denial of Service**: While resource limits are strictly enforced, it's theoretically possible for cleverly crafted code to cause performance degradation or hit limits in ways that are disruptive. Continuous monitoring is key.
-   **Complexity of Configuration**: Sandboxing is complex. Misconfiguration (e.g., overly permissive seccomp profiles, incorrect network rules, excessive resource limits) is a significant operational risk. Rigorous review of configurations is required.
-   **Trusted Orchestrator**: This policy assumes that the Code Execution Sandbox module itself, and the host system it runs on, are trusted and secured environments.
-   **Data in Transit/At Rest**: Code snippets and results are handled by the module. If they are sensitive, the broader system context must ensure their secure transmission (TLS) and storage (if persisted).

## 8. Secure Configuration Guide

Secure configuration is paramount. Refer to the `docs/technical_overview.md` and `USAGE_EXAMPLES.md` for specific configuration parameters. Key principles:

-   **Default to Most Restrictive**: Always start with the tightest resource limits (CPU, memory, time), no network access, and the most minimal language runtimes.
-   **Justify Deviations**: Only increase limits or enable capabilities (like network access) if absolutely essential for a well-defined, trusted use case. Document and review such justifications.
-   **Regular Audits**: Periodically review sandbox configurations, runtime images, and resource limits.
-   **Environment Variables**: Use environment variables or a secure configuration service for any sensitive settings (e.g., API keys for an internal artifact registry if images are pulled from there), managed via the `environment_setup` module.
-   **Language Runtimes**: The list of enabled language runtimes and their corresponding images should be explicitly managed and regularly reviewed for security currency.

## 9. Incident Response (High-Level Outline)

If a security breach or critical vulnerability related to the sandbox is suspected or discovered:

1.  **Isolate**: Immediately attempt to stop new sandbox instantiations. If an active breach is suspected in a running sandbox, try to safely terminate the specific instance(s) if possible, or isolate the host running the sandbox service.
2.  **Collect Evidence**: Preserve all relevant logs: from the Code Execution Sandbox module, Docker daemon logs, host system logs (syslog, auth.log, auditd logs), seccomp/AppArmor logs, and if possible, a snapshot of any suspicious container's filesystem (if it wasn't ephemeral or if a copy can be made before termination).
3.  **Analyze**: Review logs and system state to determine the nature, scope, and entry point of the incident. Look for anomalous behavior, unauthorized network connections, unexpected processes, or modifications.
4.  **Notify**: Report the incident immediately to the security contact: `blanket@activeinference.institute` with the subject "URGENT: Sandbox Security Incident".
5.  **Remediate**: Once the vulnerability is understood, apply necessary patches, update configurations, rebuild images, or take other corrective actions.
6.  **Recover**: Safely restore service, ensuring the vulnerability is addressed.
7.  **Learn & Document**: Conduct a post-mortem analysis to understand root causes and improve defenses. Update documentation and security policies.

## 10. Reporting a Vulnerability

If you discover a security vulnerability within this module, please report it to us as soon as possible. We take all security reports seriously.

**DO NOT report security vulnerabilities through public GitHub issues.**

Instead, please email **blanket@activeinference.institute** with the subject line: "**SECURITY Vulnerability Report: Code Execution Sandbox - [Brief Description]**".

Please include the following information in your report:

-   A detailed description of the vulnerability and its potential impact.
-   Clear, step-by-step instructions to reproduce the vulnerability, including any specific code snippets, configurations, or conditions required.
-   Any proof-of-concept (PoC) code, scripts, or examples.
-   The version(s) of the module affected (if known, or commit hash).
-   Your name and contact information (optional, but helpful for follow-up).

We aim to acknowledge receipt of your vulnerability report within **1-2 business days** and will work with you to understand and remediate the issue. We may request additional information if needed. Public disclosure of the vulnerability will be coordinated with you after the vulnerability has been fixed and an update is available, or after a reasonable period if a fix is not immediately possible.

## 11. Security Updates

Security patches and updates for this module will be documented in the [CHANGELOG.md](./CHANGELOG.md) and released as part of regular version updates. Critical vulnerabilities may warrant out-of-band releases. Users are strongly encouraged to keep the module updated to the latest stable version.

## 12. Scope

This security policy applies *only* to the `Code Execution Sandbox` module within the Codomyrmex project. For project-wide security concerns, please refer to the main project's security policy (if one exists) or contact the core project maintainers.

## 13. Best Practices for Using This Module

In addition to the system-level configurations, users submitting code to the sandbox should adhere to these best practices:

-   **Use Latest Version**: Always ensure you are integrating with the latest stable and patched version of this module.
-   **Principle of Least Privilege for Code**: When submitting code, ensure it only attempts to perform actions and use resources absolutely necessary for its task. Do not submit overly broad or exploratory code.
-   **Input Sanitization (Client-Side)**: If the code to be executed in the sandbox itself processes further inputs, the system *calling* the sandbox should sanitize those inputs *before* constructing the code snippet to be executed. Do not rely solely on the sandbox to make unsafe inputs safe.
-   **Output Validation**: Treat any data returned from the sandbox (stdout, stderr, files) as potentially untrusted. Sanitize or validate it appropriately before further use, especially if it will be displayed to users or used in sensitive operations.
-   **Resource Request Accuracy**: If the MCP tool `execute_code` allows specifying resource hints, provide accurate estimates. Do not request excessive resources "just in case."
-   **Network Prudence**: If a use case *requires* network access (and it's enabled by administrators), the submitted code should only contact expected, allow-listed endpoints. Avoid dynamic resolution or redirection to arbitrary hosts.
-   **No Sensitive Data**: **Crucially, do not pass sensitive data (secrets, API keys, PII, proprietary algorithms not meant for execution by third parties) directly into the code to be executed or as easily accessible environment variables within the sandbox.** If such data is needed, consider alternative architectures where the sandbox calls out to a trusted service to handle that data, or use token-based, short-lived, narrowly-scoped credentials if unavoidable.
-   **Monitor and Review**: Regularly review the purpose and behavior of code being submitted to the sandbox. Monitor logs provided by the `logging_monitoring` module for any anomalies related to your sandbox usage.

Thank you for helping keep Codomyrmex and the Code Execution Sandbox module secure. 