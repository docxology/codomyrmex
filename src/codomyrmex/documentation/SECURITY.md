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

We aim to acknowledge receipt of your vulnerability report within 2-3 business days and will work with you to understand and remediate the issue. We may request additional information if needed.

Public disclosure of the vulnerability will be coordinated with you after the vulnerability has been fixed and an update is available, or after a reasonable period if a fix is not immediately possible.

## Security Updates

Security patches and updates for this module will be documented in the module changelog and released as part of regular version updates. Critical vulnerabilities may warrant out-of-band releases.

## Scope

This security policy applies only to the `Documentation` module within the Codomyrmex project. For project-wide security concerns, please refer to the main project's security policy (if available) or contact the core project maintainers.

## Best Practices for Using This Module

- Always use the latest stable version of the module and its dependencies (including Docusaurus, Node.js, npm/yarn).
- **Dependency Security**: Regularly update Docusaurus, Node.js, npm/yarn, and any Docusaurus plugins or themes to their latest secure versions. Monitor for vulnerabilities in these dependencies (e.g., using `npm audit`).
- **Third-Party Scripts/Plugins**: Be cautious when adding custom JavaScript, CSS, or third-party Docusaurus plugins/themes. Ensure they are from trusted sources and review their code for potential security issues (e.g., XSS vectors, insecure data handling).
- **Content Security Policy (CSP)**: If your Docusaurus site is hosted, consider implementing a Content Security Policy to mitigate risks like XSS. This can be done via meta tags or HTTP headers.
- **Cross-Site Scripting (XSS)**: While Docusaurus generates a static site, custom components or improperly handled user-generated content (if any feature were to allow it) could introduce XSS. Sanitize any dynamic data rendered on the site.
- **Build Environment Security**: Secure the environment where the Docusaurus site is built. Ensure build scripts and tools are trusted.
- **Deployment Security**: Secure the deployment process and the hosting environment. Use HTTPS for the live documentation site.
- **Access Control**: If the documentation contains sensitive or internal information and is not intended for public access, ensure appropriate access controls are implemented at the hosting level.
- Follow the principle of least privilege when configuring access or permissions related to this module (e.g., file system permissions for the build process or server).
- Regularly review configurations and logs for suspicious activity, especially if the documentation site is publicly hosted.

Thank you for helping keep Codomyrmex and the Documentation module secure. 