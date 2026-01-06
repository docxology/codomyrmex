# Security Policy for Environment Setup

This document outlines security procedures, policies, and key considerations for the Environment Setup module. The primary goal of this module is to facilitate a secure and consistent development environment for the Codomyrmex project.

## 1. Introduction

The Environment Setup module, through its documentation (like `README.md`) and utility scripts (like `env_checker.py`), guides developers in installing prerequisites, configuring dependencies, and managing environment variables (e.g., API keys). While it doesn't typically handle highly sensitive data directly in transit, its guidance and the tools it uses (like `pip`, `npm`, `git`) have security implications.

## 2. Core Security Principles for Environment Setup

-   **Source Integrity**: Obtain software and dependencies from official and trusted sources.
-   **Least Privilege**: Development tools and environments should operate with the minimum necessary permissions.
-   **Configuration Secrecy**: Sensitive configurations, like API keys, must be protected from accidental disclosure.
-   **Reproducibility & Consistency**: A consistent setup process helps reduce the chances of ad-hoc, insecure configurations.

## 3. Threat Model for Development Environment Setup

-   **Compromised Dependencies**: Downloading and installing malicious or compromised packages via `pip install -r requirements.txt` or `npm install`.
    -   Threat: Malicious code execution during package installation (e.g., via `setup.py` or `postinstall` scripts) or at runtime when the package is used.
-   **Insecure API Key Handling**: Accidental commitment of `.env` files containing API keys to version control, or insecure storage/transmission of these keys.
    -   Threat: Unauthorized access to paid services (LLMs, cloud platforms), leading to financial loss or data breaches.
-   **Vulnerable System Prerequisites**: Using outdated or vulnerable versions of Python, Node.js, Git, or the OS itself.
    -   Threat: Exploitation of known vulnerabilities in these tools to compromise the development machine.
-   **Malicious Setup Scripts (Hypothetical)**: If custom setup scripts (e.g., `.sh` or `.bat` files) were introduced that download and execute code from the internet without proper validation (e.g., `curl | bash` anti-pattern).
    -   Threat: Arbitrary code execution on the developer's machine.
-   **Virtual Environment Security**: If the Python virtual environment (`.venv/`) is compromised or tampered with, it could affect all project code run within it.

## 4. Key Security Measures & Mitigations

-   **Dependency Management**:
    -   **Use Pinned Versions**: The root `requirements.txt` and module-specific `requirements.txt` / `package.json` files SHOULD use pinned, exact versions for all dependencies (e.g., `package==1.2.3` not `package>=1.2.0`). This mitigates the risk of inadvertently pulling in a newly compromised version of a sub-dependency.
    -   **Hash-Checking (pip)**: Where feasible and supported by the `requirements.txt` format, include hashes for packages (`pip install --require-hashes ...`). This ensures that downloaded packages match expected checksums. (This is a project-wide goal).
    -   **Source Verification**: Prefer dependencies from well-known, reputable sources (PyPI, npmjs.com main registries). Be cautious with less common or unverified sources.
    -   **Regular Audits**: Periodically review dependencies for known vulnerabilities using tools like `pip-audit`, `npm audit`, or Snyk.
-   **Secure API Key Management (`.env` files)**:
    -   The `env_checker.py` script validates `.env` file existence and provides secure configuration guidance. It never accesses, logs, or exposes actual API key values during environment checks.
    -   The `.env` file **MUST NEVER** be committed to version control. The project's root `.gitignore` includes `.env`.
    -   Store `.env` files securely on the local development machine.
    -   Grant API keys the minimum necessary permissions (Principle of Least Privilege) for their intended use in development.
    -   Consider using environment-specific API keys for development versus production (if applicable to the service).
    -   Regularly review and rotate API keys if supported by the provider, or if a compromise is suspected.
-   **System Prerequisites**: Developers should ensure their underlying OS, Python, Node.js, and Git installations are kept up-to-date with security patches from official sources.
-   **Setup Scripts (if any)**:
    -   Currently, the project primarily relies on `pip` and `npm` with `requirements.txt` / `package.json`. `env_checker.py` is a Python script run directly.
    -   If any shell scripts (`.sh`, `.bat`) are introduced for setup, they should be self-contained or download resources only from trusted, verifiable URLs using secure methods (e.g., `curl -fsSL --tlsv1.2 --proto "=https" ...` with checksum verification if possible). Avoid `curl | bash` patterns.
    -   All scripts should be reviewed for security before adoption.
-   **Virtual Environments**: Protect the `.venv/` directory from unauthorized modification. Ensure it's included in `.gitignore` if not already implicitly covered by project structure.
-   **`env_checker.py` Security**: The script itself should not introduce vulnerabilities. It performs read-only checks or guides user actions. It should not write arbitrary files or execute commands based on untrusted input (it currently does not).

## 5. Reporting a Vulnerability

If you discover a security vulnerability within this module (e.g., in `env_checker.py` or in the documented setup process that leads to a vulnerability), please report it to us as soon as possible.
We take all security reports seriously.

**DO NOT report security vulnerabilities through public GitHub issues.**

Instead, please email **blanket@activeinference.institute** with the subject line: "**SECURITY Vulnerability Report: Environment Setup - Security Issue**".

Please include the following information in your report:

-   A description of the vulnerability and its potential impact.
-   Steps to reproduce the vulnerability, including any specific configurations or conditions required.
-   Any proof-of-concept code or examples.
-   The version(s) of the module or specific scripts affected.
-   Your name and contact information (optional).

We aim to acknowledge receipt of your vulnerability report within **1-2 business days** and will work with you to understand and remediate the issue. We may request additional information if needed.

Public disclosure of the vulnerability will be coordinated with you after the vulnerability has been fixed and an update is available, or after a reasonable period if a fix is not immediately possible.

## 6. Security Updates

Security patches and updates for this module (e.g., to `env_checker.py` or setup documentation) will be documented in the module changelog and released as part of regular version updates.

## 7. Scope

This security policy applies only to the `Environment Setup` module itself and the documented processes it promotes within the Codomyrmex project. For project-wide security concerns, or vulnerabilities in other modules, please refer to their respective security policies or the main project's security policy.

## 8. Best Practices for Users of this Module

-   **Follow Instructions Carefully**: Adhere to the setup instructions in the `environment_setup/README.md` and the root project `README.md`.
-   **Use Virtual Environments**: Always use a Python virtual environment for the project.
-   **Verify Sources**: When manually installing tools or dependencies not covered by the main `requirements.txt`, ensure they are from trusted sources.
-   **Keep `.env` Secure**: Protect your `.env` file and never commit it.
-   **Update Regularly**: Keep your local development tools (Python, pip, Node, Git, OS) updated.

Thank you for helping keep Codomyrmex and the Environment Setup module secure. 
## Navigation Links

- **Parent**: [Project Overview](../README.md)
- **Module Index**: [All Agents](../../AGENTS.md)
- **Documentation**: [Reference Guides](../../docs/README.md)
- **Home**: [Root README](../../../README.md)
