# Security Policy for Code Execution Sandbox

This document outlines security procedures and policies for the Code Execution Sandbox module.

<!-- TODO: CRITICAL SECTION - Expand significantly. 
    This module is highly security-sensitive. This section needs to go beyond reporting.
    It should detail:
    - Core Security Principles: Least privilege, defense in depth, secure defaults.
    - Sandboxing Technology: Briefly mention the chosen technology (e.g., Docker, nsjail) and key security configurations (e.g., no-new-privs, seccomp filters, network policies, resource limits).
    - Threat Model: What are the primary threats? (e.g., sandbox escape, resource exhaustion DOS, data leakage from host, inter-sandbox communication).
    - Key Security Measures: Specific technical measures in place to mitigate these threats.
    - Known Limitations: Any known security limitations or assumptions.
    - Secure Configuration Guide: Pointers to documentation on how to configure the sandbox securely (resource limits, allowed languages, network access etc.).
    - Incident Response Plan: Basic steps if a breach or critical vulnerability is suspected/found.
-->

## Reporting a Vulnerability

If you discover a security vulnerability within this module, please report it to us as soon as possible.
We take all security reports seriously.

**DO NOT report security vulnerabilities through public GitHub issues.**

Instead, please email blanket@activeinference.institute with the subject line: "SECURITY Vulnerability Report: Code Execution Sandbox - [Brief Description]".

Please include the following information in your report:

- A description of the vulnerability and its potential impact.
- Steps to reproduce the vulnerability, including any specific configurations or conditions required.
- Any proof-of-concept code or examples.
- The version(s) of the module affected.
- Your name and contact information (optional).

We aim to acknowledge receipt of your vulnerability report within [Specify Expected Response Time, e.g., 2-3 business days] and will work with you to understand and remediate the issue. We may request additional information if needed.

Public disclosure of the vulnerability will be coordinated with you after the vulnerability has been fixed and an update is available, or after a reasonable period if a fix is not immediately possible.

## Security Updates

Security patches and updates for this module will be documented in the [CHANGELOG.md](./CHANGELOG.md) and released as part of regular version updates. Critical vulnerabilities may warrant out-of-band releases.

## Scope

This security policy applies only to the `Code Execution Sandbox` module within the Codomyrmex project. For project-wide security concerns, please refer to the main project's security policy (if available) or contact the core project maintainers.

## Best Practices for Using This Module

<!-- TODO: Expand this section with concrete advice for users of the sandbox. -->
- Always use the latest stable version of the module.
- Follow the principle of least privilege when configuring access or permissions related to this module and when defining resource limits for code execution.
- **Never run untrusted code from unknown sources without extreme caution and the tightest possible resource limits.**
- **Regularly review and update the sandbox environment images/runtimes to include the latest security patches for the supported languages and their dependencies.**
- **Strictly control network access for sandboxed code. Default to no network access.**
- **Do not pass sensitive data (secrets, PII) into the sandbox environment or code execution requests unless absolutely necessary and the security implications are fully understood and mitigated.**
- Regularly review configurations and logs (from `logging_monitoring`) for suspicious activity or excessive resource consumption.

Thank you for helping keep Codomyrmex and the Code Execution Sandbox module secure. 