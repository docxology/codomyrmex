# config/templates

## Signposting
- **Parent**: [Parent](../README.md)
- **Children**:
    - None
- **Key Artifacts**:
    - [Agent Guide](AGENTS.md)
    - [Functional Spec](SPEC.md)

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: December 2025

## Overview

Reusable configuration templates and environment scaffolding for Codomyrmex. Templates provide standardized starting points for different deployment scenarios and can be customized for specific use cases.

## Directory Contents
- `development.env` – Development environment template
- `production.env` – Production environment template

## Template Usage

Templates support variable substitution:
- `${VARIABLE_NAME}` - Required environment variables
- `${VARIABLE_NAME:-default}` - Optional with default value
- `{{template_var}}` - Template-specific variables

## Navigation
- **Technical Documentation**: [AGENTS.md](AGENTS.md)
- **Functional Specification**: [SPEC.md](SPEC.md)
- **Parent Directory**: [config](../README.md)
- **Repository Root**: [../../README.md](../../README.md)