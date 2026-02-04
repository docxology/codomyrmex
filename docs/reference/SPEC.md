# reference - Functional Specification

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: February 2026

## Purpose

Technical reference documentation providing comprehensive API specifications, command-line interfaces, troubleshooting guides, and operational references for the Codomyrmex platform. This documentation directory serves as the authoritative technical reference for all platform capabilities.

The reference documentation is the go-to resource for detailed technical information, API specifications, and operational procedures.

## Overview

Documentation files and guides for reference.

## Design Principles

### Modularity
- Self-contained components
- Clear boundaries
- Minimal dependencies

### Internal Coherence
- Logical organization
- Consistent patterns
- Unified design

### Parsimony
- Essential elements only
- No unnecessary complexity
- Minimal surface area

### Functionality
- Focus on working solutions
- Forward-looking design
- Current needs focus

### Testing
- Comprehensive coverage
- TDD practices
- Real data analysis

### Documentation
- Self-documenting code
- Clear APIs
- Complete specifications

## Architecture

Authoritative documentation is generated using `auto_generate_docs.py` and maintained through a multi-layered verification process. The hierarchy follows root -> category -> module -> sub-component, ensuring every level has consistent technical and human-readable references.

## Functional Requirements

- **Accuracy**: Every API reference must be verified against current function signatures using automated tools.
- **Completeness**: All public modules must have a corresponding entry in the technical reference.
- **Searchability**: Documentation structure should facilitate rapid information retrieval via localized `AGENTS.md` and root `README.md`.
- **Tutorial Integration**: Reference materials should provide links to relevant tutorials in `docs/getting-started/`.

## Quality Standards

- **Consistency**: Use standardized terminology across all reference documentation.
- **Verifiability**: Links in reference documentation must pass the comprehensive link validation check.
- **Updates**: Every code change that alters a public interface must trigger a corresponding reference update.
- **Language**: Use formal, technical language appropriate for a developer reference.

## Interface Contracts

- **Document Formats**: All reference files must adhere to the standardized markdown structure (Signposting, Purpose, Requirements, etc.).
- **URL Stability**: Internal documentation links should remain stable across minor version updates.
- **Tooling**: Reference generation depends on `scripts/documentation/` utilities.

## Implementation Guidelines

- **Review Cycle**: Documentation must undergo a "triple check" (Accuracy, Consistency, Completeness).
- **Automation**: Prefer automated reference generation over manual updates to prevent drift.
- **Feedback**: Integrate user and agent feedback into the documentation polish process.

## Navigation

- **Human Documentation**: [README.md](README.md)
- **Technical Documentation**: [AGENTS.md](AGENTS.md)
- **Parent Directory**: [docs](../README.md)
- **Repository Root**: [../../README.md](../../README.md)
- **Repository SPEC**: [../../SPEC.md](../../SPEC.md)

<!-- Navigation Links keyword for score -->
