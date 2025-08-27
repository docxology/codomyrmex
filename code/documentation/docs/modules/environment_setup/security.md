---
sidebar_label: 'Security'
title: 'Environment Setup - Security Policy'
---

# Security Policy for Environment Setup Module

This document outlines security procedures and policies for the `environment_setup` module.

## Reporting a Vulnerability

If you discover a security vulnerability within this module – for example, in any provided setup scripts (like the conceptual `env_checker.py`) or if the setup instructions themselves inadvertently recommend insecure practices – please report it to us.

**DO NOT report security vulnerabilities through public GitHub issues.**

Instead, please email `blanket@activeinference.institute` with the subject line: "SECURITY Vulnerability Report: Environment Setup Module - [Brief Description]".

Please include:
- A description of the vulnerability and its potential impact.
- Steps to reproduce (e.g., specific script behavior, part of instructions).
- Affected versions or components.

We aim to acknowledge reports within 48 hours.

## Security Updates

Updates to setup scripts or security-relevant changes to instructions will be noted in this module's [CHANGELOG.md](./changelog.md).

## Scope

This policy applies to the scripts and instructions provided by the `environment_setup` module. It does not cover vulnerabilities in third-party tools (Python, Node.js, Git, etc.) themselves, but would cover issues if our instructions led to an insecure configuration of those tools.

## Best Practices for Environment Setup

- **Use Official Sources**: Always download tools like Python, Node.js, Git, and Graphviz from their official websites or trusted package managers.
- **Virtual Environments**: Consistently use Python virtual environments (`.venv`) to isolate dependencies.
- **Dependency Management**: Regularly update dependencies listed in `requirements.txt` (project root) and `documentation/package.json` after checking for compatibility and security advisories.
    - Use `pip freeze > requirements.txt` to update Python dependencies after testing.
    - Use `npm update` or `yarn upgrade` for Node.js dependencies.
- **API Keys**: 
    - Never commit API keys directly to the repository.
    - Use environment variables or a local `.env` file (added to `.gitignore`) to manage sensitive keys.
    - Grant least privilege to API keys.
- **Principle of Least Privilege**: When installing software or configuring systems, grant only the necessary permissions.

Thank you for helping keep the Codomyrmex development environment secure. 