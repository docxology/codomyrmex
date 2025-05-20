# Security Policy for Environment Setup

This document outlines security procedures and policies for the Environment Setup module.

## Reporting a Vulnerability

If you discover a security vulnerability within this module, please report it to us as soon as possible.
We take all security reports seriously.

**DO NOT report security vulnerabilities through public GitHub issues.**

Instead, please email blanket@activeinference.institute with the subject line: "SECURITY Vulnerability Report: Environment Setup - [Brief Description]".

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

This security policy applies only to the `Environment Setup` module within the Codomyrmex project. For project-wide security concerns, please refer to the main project's security policy (if available) or contact the core project maintainers.

## Best Practices for Using This Module

- Always use the latest stable version of the module.
- **Secure API Key Management**: 
    - When creating the `.env` file as guided by this module (e.g., by `env_checker.py`), ensure it is stored securely and **never commit it to version control** (e.g., Git).
    - The project's root `.gitignore` should already list `.env`, but always double-check.
    - Grant API keys the minimum necessary permissions required for their intended use.
    - Regularly review and rotate API keys if supported by the provider, or if a compromise is suspected.
- Follow the principle of least privilege when configuring access or permissions related to any scripts or tools from this module, though they primarily perform local checks.
- Regularly review configurations and any logs (if `env_checker.py` were to produce them) for suspicious activity.

Thank you for helping keep Codomyrmex and the Environment Setup module secure. 