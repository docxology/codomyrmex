---
sidebar_label: 'Security'
title: 'Git Operations - Security Policy'
---

# Security Policy for Git Operations Module

This document outlines security procedures and policies for the Git Operations module.

## Reporting a Vulnerability

If you discover a security vulnerability within this module, please report it to us as soon as possible.
We take all security reports seriously.

**DO NOT report security vulnerabilities through public GitHub issues.**

Instead, please email `blanket@activeinference.institute` with the subject line: "SECURITY Vulnerability Report: Git Operations - [Brief Description]".

Please include the following information in your report:

- A description of the vulnerability and its potential impact.
- Steps to reproduce the vulnerability, including any specific configurations or conditions required.
- Any proof-of-concept code or examples.
- The version(s) of the module affected.
- Your name and contact information (optional).

We aim to acknowledge receipt of your vulnerability report within 48 hours and will work with you to understand and remediate the issue. We may request additional information if needed.

Public disclosure of the vulnerability will be coordinated with you after the vulnerability has been fixed and an update is available, or after a reasonable period if a fix is not immediately possible.

## Security Updates

Security patches and updates for this module will be documented in the [CHANGELOG.md](./changelog.md) and released as part of regular version updates. Critical vulnerabilities may warrant out-of-band releases.

## Scope

This security policy applies only to the `Git Operations` module within the Codomyrmex project. For project-wide security concerns, please refer to the main project's security policy or contact the core project maintainers.

## Best Practices for Using This Module

- Always use the latest stable version of the module.
- Follow the principle of least privilege when configuring access or permissions related to this module (e.g., ensuring that any scripts or tools from this module run with only the necessary filesystem and network permissions).
- Ensure that Git itself is kept up-to-date on the system where this module is used.
- Be cautious with repository URLs from untrusted sources if using functions like `git_clone`.
- Regularly review configurations and logs for suspicious activity if this module is used in an automated fashion.

Thank you for helping keep Codomyrmex and the Git Operations module secure. 