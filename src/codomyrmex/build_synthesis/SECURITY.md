# Security Policy for Build Synthesis

This document outlines security procedures and policies for the Build Synthesis module.

## Reporting a Vulnerability

If you discover a security vulnerability within this module, please report it to us as soon as possible.
We take all security reports seriously.

**DO NOT report security vulnerabilities through public GitHub issues.**

Instead, please email blanket@activeinference.institute with the subject line: "SECURITY Vulnerability Report: Build Synthesis - [Brief Description]".

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

This security policy applies only to the `Build Synthesis` module within the Codomyrmex project. For project-wide security concerns, please refer to the main project's security policy (if available) or contact the core project maintainers.

## Best Practices for Using This Module

- Always use the latest stable version of the module.
- **Dependency Security**: If the build process involves fetching dependencies (e.g., from PyPI, npm, Maven), ensure sources are trusted and consider using lockfiles and checksum verification to mitigate supply chain risks. Regularly audit dependencies for known vulnerabilities.
- **Build Environment Security**: Ensure the environment where builds are performed is secure and isolated, especially if building code from untrusted sources or with untrusted build scripts.
- **Artifact Security**: Securely store and distribute build artifacts. Implement signing and verification if artifacts are consumed by other critical systems.
- **Code Synthesis Risks**: If this module synthesizes code (e.g., from prompts or specifications):
    - Treat synthesized code as untrusted until reviewed.
    - Sanitize inputs to code synthesis functions to prevent injection attacks that could influence the generated code negatively.
    - Be mindful of resource consumption during code synthesis.
- **Secure API Key Handling**: If interacting with external services for code synthesis (e.g., LLMs), manage API keys securely.
- Follow the principle of least privilege when configuring access or permissions related to this module.
- Regularly review configurations and logs for suspicious activity.

Thank you for helping keep Codomyrmex and the Build Synthesis module secure. 