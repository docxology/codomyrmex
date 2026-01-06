# Security Policy for Ai Code Editing

This document outlines security procedures and policies for the Ai Code Editing module.

## Reporting a Vulnerability

If you discover a security vulnerability within this module, please report it to us as soon as possible.
We take all security reports seriously.

**DO NOT report security vulnerabilities through public GitHub issues.**

Instead, please email blanket@activeinference.institute with the subject line: "SECURITY Vulnerability Report: Ai Code Editing - Security Issue".

Please include the following information in your report:

- A description of the vulnerability and its potential impact.
- Steps to reproduce the vulnerability, including any specific configurations or conditions required.
- Any proof-of-concept code or examples.
- The version(s) of the module affected.
- Your name and contact information (optional).

We aim to acknowledge receipt of your vulnerability report within 2-3 business days and will work with you to understand and remediate the issue. We may request additional information if needed.

Public disclosure of the vulnerability will be coordinated with you after the vulnerability has been fixed and an update is available, or after a reasonable period if a fix is not immediately possible.

## Security Updates

Security patches and updates for this module will be documented in the module changelog and released as part of regular version updates. Critical vulnerabilities may warrant out-of-band releases.

## Scope

This security policy applies only to the `Ai Code Editing` module within the Codomyrmex project. For project-wide security concerns, please refer to the main project's security policy (if available) or contact the core project maintainers.

## Best Practices for Using This Module

- Always use the latest stable version of the module.
- Follow the principle of least privilege when configuring access or permissions related to this module.
- **Input Sanitization for Prompts**: If prompts provided to AI code editing/generation functions are derived from external or untrusted user input, sanitize them to prevent prompt injection attacks that could cause the LLM to generate malicious code or reveal sensitive information.
- **Review Generated Code**: Treat all code generated or modified by this module as untrusted until reviewed by a human. Automated code generation can introduce vulnerabilities or unwanted behaviors.
- **Secure LLM API Key Handling**: If this module directly interacts with LLM APIs, ensure API keys are handled securely (e.g., via environment variables managed by `environment_setup`) and not hardcoded or logged.
- **Resource Limits**: Be mindful of the complexity and length of code submitted for refactoring or analysis, as complex operations could consume significant resources.
- Regularly review configurations and logs for suspicious activity.

Thank you for helping keep Codomyrmex and the Ai Code Editing module secure. 
## Navigation Links

- **Parent**: [Project Overview](../README.md)
- **Module Index**: [All Agents](../../AGENTS.md)
- **Documentation**: [Reference Guides](../../../../docs/README.md)
- **Home**: [Root README](../../../README.md)
