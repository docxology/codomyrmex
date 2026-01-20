# Codomyrmex Agents — src/codomyrmex/security

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: January 2026

## Purpose

The `security` module provides the foundational infrastructure for protecting agents, data, and physical assets. It orchestrates vulnerability scanning, encryption, compliance checking, and physical access control across the Codomyrmex ecosystem.

## Active Components

- `digital/` – Core digital defense: vulnerability scanning, encryption, and secrets detection.
- `physical/` – Real-world security: access control systems, asset tracking, and surveillance.
- `cognitive/` – Human-centric security: social engineering detection and phishing analysis.
- `theory/` – Security architecture patterns, threat modeling, and risk assessment frameworks.

## Operating Contracts

1. **Uniform Validity**: All security results (`SecurityScanResult`, `VulnerabilityReport`) must provide a `.valid` property for simplified agent checking.
2. **Context Persistence**: Use global singletons (e.g., `_GLOBAL_ACS`) via functional wrappers to maintain security state across agent interactions.
3. **Defense in Depth**: Leverage multiple submodules to provide layered security (e.g., combining digital audit with risk assessment).

## Navigation Links

- **📁 Parent Directory**: [codomyrmex](../README.md) - Parent directory documentation
- **🏠 Project Root**: ../../../README.md - Main project documentation
