# Security Policy for Website

This document outlines security procedures and policies for the Website module.

## Reporting a Vulnerability

If you discover a security vulnerability within this module, please report it to us as soon as possible.
We take all security reports seriously.

**DO NOT report security vulnerabilities through public GitHub issues.**

Instead, contact the Codomyrmex maintainers with the subject line: "SECURITY Vulnerability Report: Website module".

Please include the following information in your report:

- A description of the vulnerability and its potential impact.
- Steps to reproduce the vulnerability, including any specific configurations or conditions required.
- Any proof-of-concept code or examples.
- The version(s) of the module affected.
- Your name and contact information (optional).

We aim to acknowledge receipt of your vulnerability report within [Specify Expected Response Time, e.g., 2-3 business days] and will work with you to understand and remediate the issue. We may request additional information if needed.

Public disclosure of the vulnerability will be coordinated with you after the vulnerability has been fixed and an update is available, or after a reasonable period if a fix is not immediately possible.

## Security Updates

Security patches and updates for this module will be documented in the module changelog and released as part of regular version updates. Critical vulnerabilities may warrant out-of-band releases.

## Scope

This security policy applies only to the `website` module within the Codomyrmex project. For project-wide security concerns, please refer to the main project's security policy (if available) or contact the core project maintainers.

## Best Practices for Using This Module

- Always use the latest stable version of the module.
- Follow the principle of least privilege when configuring access or permissions related to this module.
- Regularly review configurations and logs for suspicious activity.
- Bind the development server to localhost unless an explicit deployment wrapper supplies authentication and transport security.
- Keep script execution constrained to the project `scripts/` directory; path containment is enforced with resolved paths, not string-prefix checks.
- Treat `/api/config` writes as privileged local-development operations and avoid exposing them on untrusted networks.

Thank you for helping keep Codomyrmex and the Website module secure. 
## Navigation Links

- **Parent**: [Project Overview](../README.md)
- **Module Index**: [All Agents](../../AGENTS.md)
- **Documentation**: [Reference Guides](../../../docs/README.md)
- **Home**: [Root README](../../../README.md)
