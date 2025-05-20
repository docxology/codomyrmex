# Security Policy for Documentation

This document outlines security procedures and policies for the Documentation module.

## Reporting a Vulnerability

If you discover a security vulnerability within this module, please report it to us as soon as possible.
We take all security reports seriously.

**DO NOT report security vulnerabilities through public GitHub issues.**

Instead, please email blanket@activeinference.institute with the subject line: "SECURITY Vulnerability Report: Documentation - [Brief Description]".

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

This security policy applies only to the `Documentation` module within the Codomyrmex project. For project-wide security concerns, please refer to the main project's security policy (if available) or contact the core project maintainers.

## Best Practices for Using This Module

- Always use the latest stable version of the module and its dependencies (including Docusaurus and Node.js packages).
- Follow the principle of least privilege when configuring access or permissions related to this module (e.g., file system permissions for the build process or server).
- Regularly review configurations and logs for suspicious activity, especially if the documentation site is publicly hosted.
- <!-- TODO: Consider adding any Docusaurus-specific security best practices. For example:
  - Be cautious when adding custom scripts or third-party plugins to Docusaurus; ensure they are from trusted sources.
  - If the documentation site processes or displays any form of user input (not typical for static sites, but possible with customizations), ensure it is properly sanitized to prevent XSS attacks.
  - Keep Node.js and npm/yarn updated to patch known vulnerabilities in the build toolchain.
-->

Thank you for helping keep Codomyrmex and the Documentation module secure. 