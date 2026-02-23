# ai_safety - Functional Specification

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: February 2026

## Purpose

Provides AI-specific security capabilities for the Codomyrmex platform, including jailbreak detection, prompt injection defense, adversarial containment, and unified AI safety monitoring. Integrates defense module components (ActiveDefense, RabbitHole) behind a single monitoring interface.

## Design Principles

- **Defense-in-Depth**: Layer multiple detection and containment strategies to catch threats at different stages
- **Proactive Detection**: Identify and intercept adversarial inputs before they reach downstream LLM components
- **Graceful Degradation**: Continue operating with reduced capability when optional defense modules are unavailable
- **Incident Tracking**: Record all detected threats for post-hoc analysis and continuous improvement

## Functional Requirements

1. **Input Validation**: Validate all inputs passed to AI/LLM components for safety violations
2. **Jailbreak Detection**: Detect jailbreak attempts and prompt injection patterns via ActiveDefense integration
3. **Adversarial Containment**: Contain adversarial inputs using RabbitHole when available
4. **Incident Reporting**: Maintain a rolling log of detected incidents and provide summary reports
5. **Optional Integration**: Gracefully handle missing defense module dependencies at import time

## Interface Contracts

### AISafetyMonitor

- `AISafetyMonitor()`: Instantiate the monitor; automatically initializes ActiveDefense and RabbitHole if available
- `check_input(text: str) -> dict`: Check an input string for AI safety violations. Returns a dict with `safe` (bool), `threats` (list of detected patterns), and `action` (str: "allow" or "block")
- `get_incident_report() -> dict`: Retrieve a summary of detected incidents. Returns a dict with `total_incidents` (int) and `incidents` (list of the last 10 incident records)

### Optional Components

- `ActiveDefense` (from `codomyrmex.defense.active`): Exploit detection via `detect_exploit()`. Available when `ACTIVE_DEFENSE_AVAILABLE` is True
- `RabbitHole` (from `codomyrmex.defense.rabbithole`): Adversarial containment. Available when `RABBITHOLE_AVAILABLE` is True

## Error Handling

All operations handle errors gracefully:
- Missing defense module imports are caught at module load time and flagged via availability booleans
- Input checking returns safe defaults when defense components are unavailable
- Incident tracking silently accumulates without raising exceptions

## Configuration

Module uses runtime detection of optional dependencies:
- `ACTIVE_DEFENSE_AVAILABLE`: Boolean flag indicating ActiveDefense availability
- `RABBITHOLE_AVAILABLE`: Boolean flag indicating RabbitHole availability
- Incident history retains the last 10 incidents in the report output

## Navigation

- **Human Documentation**: [README.md](README.md)
- **Technical Documentation**: [AGENTS.md](AGENTS.md)
- **Parent**: [../SPEC.md](../SPEC.md)
