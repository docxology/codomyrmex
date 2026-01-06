# Security Policy for Git Operations

This document outlines security procedures, policies, and critical considerations for the Git Operations module. This module provides tools to programmatically interact with Git repositories, which has inherent security implications.

## 1. Introduction

The Git Operations module aims to offer a safe and reliable Python API for automating common Git tasks. Security is paramount, especially when dealing with source code repositories, commit history, and authentication credentials for remote Git servers.

## 2. Core Security Principles

-   **Credential Security**: Authentication credentials (SSH keys, Personal Access Tokens) must be handled securely and never hardcoded or logged.
-   **Input Validation**: Inputs to API functions (e.g., repository paths, branch names, commit messages) must be validated to prevent injection attacks or unintended operations.
-   **Least Privilege**: Automated Git operations should run with the minimum necessary permissions on repositories and remote services.
-   **Secure Defaults**: API functions should default to safer behaviors (e.g., not force-pushing unless explicitly specified and confirmed).
-   **Auditability**: Git operations performed by this module should be logged for audit purposes (via `logging_monitoring`).

## 3. Threat Model

-   **Credential Theft/Leakage**: 
    -   Improper handling of SSH private keys or Personal Access Tokens (PATs) by scripts using this module.
    -   Logging of sensitive credentials.
    -   Hardcoding credentials in scripts.
-   **Command Injection (if using raw subprocesses, less likely with a proper API/library like GitPython)**: 
    -   If API functions internally construct Git CLI commands by unsafely concatenating user-supplied input, it could lead to arbitrary command execution.
-   **Repository Corruption/Data Loss**: 
    -   Automated tools performing destructive operations like force pushes, branch deletions, or history rewrites without proper safeguards or user confirmation.
    -   Accidental commitment of unwanted files (e.g., large binaries, sensitive data) if staging is too broad.
-   **Information Disclosure**: 
    -   Accidental commitment and push of files containing secrets (API keys, passwords, sensitive configuration) to a remote repository.
    -   API functions unintentionally exposing sensitive repository details (e.g., internal file structure, full commit messages with sensitive data if not handled carefully by the caller).
-   **Unauthorized Access/Modification**: 
    -   Tools using overly permissive credentials allowing wider access than necessary.
    -   Exploitation of vulnerabilities in the underlying Git client or an intermediate library (e.g., `GitPython`).
-   **Pre-Commit Hook Exploitation**: 
    -   If this module interacts with repositories that have pre-commit hooks, a malicious hook could execute unintended code or leak data during an automated commit operation triggered by this module.
    -   Secrets scanning hooks might inadvertently log found secrets if not configured carefully.

## 4. Key Security Measures & Mitigations

-   **Secure Credential Handling**: 
    -   The module itself (and its Python API) should **not** directly store or manage long-lived credentials like passwords or PATs. It should rely on Git's underlying credential management system (SSH agent, Git Credential Manager, OS keychain integration).
    -   Clear documentation (in `API_SPECIFICATION.md` and `README.md`) must guide users on how to set up their environment for secure Git authentication (e.g., using SSH keys, or HTTPS with a credential helper).
    -   Avoid API patterns that encourage passing raw credentials. If temporary tokens are used (e.g., from a CI/CD environment), they should be handled with extreme care and have short lifespans and minimal scope.
    -   **Never log credentials or sensitive parts of Git commands** that might contain them.
-   **Safe API Design (Defense against Injection)**:
    -   Prefer using established Git libraries like `GitPython` over direct `subprocess` calls to the `git` CLI. `GitPython` generally provides a safer interface.
    -   If `subprocess` must be used for specific commands not covered by a library, ensure all arguments are passed as a list to `subprocess.run()` (or similar) and that user-supplied inputs are never directly interpolated into command strings without rigorous sanitization (parameterization is key).
-   **Preventing Accidental Data Loss/Corruption**: 
    -   Destructive operations (e.g., `force_push`, `delete_branch` if it's not merged, `reset --hard`) exposed via the API should require explicit confirmation flags or be clearly named to indicate their danger (e.g., `force_push_branch`).
    -   Commit functions should provide control over what is staged (e.g., stage specific files, stage all tracked files, stage all files including untracked). Default to safer staging (e.g., only tracked files).
-   **Secrets Management & Pre-Commit Hooks**: 
    -   **Project-Level Responsibility**: The primary defense against committing secrets is at the project/developer level, using tools like `git-secrets`, `trufflehog`, or other pre-commit hooks that scan for secrets *before* a commit is made locally.
    -   This `git_operations` module, when automating commits, will trigger such hooks if they are configured in the repository it's operating on. Users must be aware of this interaction.
    -   Document that automated commits by this module will respect local repository hooks.
    -   If this module itself were to *manage* or *configure* hooks, that would require its own security review.
-   **Dependency Security**: 
    -   Keep any third-party Git libraries (e.g., `GitPython`) updated to their latest secure versions by pinning them in `git_operations/requirements.txt` and monitoring for vulnerabilities.
    -   Ensure the system's `git` client itself is kept updated.
-   **Input Validation**: 
    -   Validate repository paths to ensure they point to valid directories and ideally actual Git repositories before operations.
    -   Sanitize or validate branch names, commit messages, and other string inputs if they are ever used in contexts where special characters could be misinterpreted (though less of a risk with proper library usage).
-   **Logging**: 
    -   Use `logging_monitoring` to log Git operations performed, including target repository, command/action, and outcome (success/failure). 
    -   **Do not log full file diffs or commit messages if they might contain sensitive data.** Log metadata about the operation.

## 5. Reporting a Vulnerability

If you discover a security vulnerability within this module (e.g., in its API design, or if it mishandles Git operations leading to a security risk), please report it to us as soon as possible.

**DO NOT report security vulnerabilities through public GitHub issues.**

Instead, please email **blanket@activeinference.institute** with the subject line: "**SECURITY Vulnerability Report: Git Operations - Security Issue**".

Please include the following information in your report:

-   A description of the vulnerability and its potential impact.
-   Steps to reproduce the vulnerability, including any specific API calls, configurations, or repository states required.
-   Any proof-of-concept code or examples.
-   The version(s) of the module affected.
-   Your name and contact information (optional).

We aim to acknowledge receipt of your vulnerability report within **1-2 business days**.

## 6. Security Updates

Security patches and updates for this module will be documented in the [CHANGELOG.md](./CHANGELOG.md). Critical vulnerabilities may warrant out-of-band releases. Users are strongly encouraged to keep the module updated.

## 7. Scope

This security policy applies to the `Git Operations` module within Codomyrmex. It does not cover the security of Git itself, the remote Git hosting provider, or user-configured pre-commit hooks, though it considers interactions with them.

## 8. Best Practices for Using This Module Securely

-   **Use SSH Keys or Credential Managers**: Configure your environment to use SSH keys or a secure Git credential manager for authenticating to remote repositories. Avoid passing raw credentials to any scripts.
-   **Principle of Least Privilege for Tokens/Keys**: If using PATs or SSH keys for automation, ensure they have the minimum necessary permissions for the repositories and operations required (e.g., read-only if only fetching, or specific write scopes if pushing).
-   **Review Automated Scripts**: Carefully review any scripts that use this module to automate Git operations, especially those performing writes, pushes, or handling potentially sensitive repositories.
-   **Implement Pre-Commit Secret Scanning**: In all repositories, use pre-commit hooks (like `git-secrets` or `trufflehog`) to prevent accidental commitment of secrets. This module's operations will respect these hooks.
-   **Test Automation Thoroughly**: Test automated Git workflows in non-critical repositories first.
-   **Keep Dependencies Updated**: Regularly update this module, `GitPython` (if used), and your local Git client.

Thank you for helping keep Codomyrmex and the Git Operations module secure. 
## Navigation Links

- **Parent**: [Project Overview](../README.md)
- **Module Index**: [All Agents](../../AGENTS.md)
- **Documentation**: [Reference Guides](../../../../../../docs/README.md)
- **Home**: [Root README](../../../README.md)
