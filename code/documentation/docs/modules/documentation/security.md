---
sidebar_label: 'Security'
title: 'Documentation Module - Security Policy'
---

# Security Policy for the Documentation Module

This document outlines security procedures and policies specifically for the `documentation` module, which manages the Docusaurus website for the Codomyrmex project.

## Reporting a Vulnerability

If you discover a security vulnerability within this module (e.g., related to the Docusaurus build process, its dependencies, or custom components used in the documentation site), please report it to us as soon as possible.
We take all security reports seriously.

**DO NOT report security vulnerabilities through public GitHub issues.**

Instead, please email `blanket@activeinference.institute` with the subject line: "SECURITY Vulnerability Report: Documentation Module - [Brief Description]".

Please include the following information in your report:

- A description of the vulnerability and its potential impact (e.g., XSS in rendered docs, build system compromise).
- Steps to reproduce the vulnerability, including any specific configurations or conditions required.
- Any proof-of-concept code or examples.
- The version(s) of Docusaurus or related dependencies affected (if known).
- Your name and contact information (optional).

We aim to acknowledge receipt of your vulnerability report within 48 hours and will work with you to understand and remediate the issue. We may request additional information if needed.

Public disclosure of the vulnerability will be coordinated with you after the vulnerability has been fixed and an update is available, or after a reasonable period if a fix is not immediately possible.

## Security Updates

Security patches and updates for Docusaurus and its core dependencies are typically managed by updating the versions in `package.json` and will be documented in this module's [CHANGELOG.md](./changelog.md).

## Scope

This security policy applies only to the `documentation` module itself. For vulnerabilities in the *content* of other modules' documentation, please refer to the security policy of that specific module or report it to the project-wide contact if it implies a broader issue.

## Best Practices for This Module

- Keep Docusaurus and its dependencies (`@docusaurus/core`, `@docusaurus/preset-classic`, `react`, etc.) up to date by regularly reviewing and applying updates from `npm outdated` or similar commands.
- Be cautious when adding custom scripts or third-party plugins to Docusaurus, ensuring they are from trusted sources.
- If any user-generated content is ever incorporated directly into the documentation site (beyond standard Markdown features), ensure proper sanitization to prevent XSS attacks.

Thank you for helping keep Codomyrmex and the Documentation module secure. 