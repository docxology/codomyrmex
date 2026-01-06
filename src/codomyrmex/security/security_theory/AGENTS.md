# Codomyrmex Agents — src/codomyrmex/security/security_theory

## Signposting
- **Parent**: [security](../AGENTS.md)
- **Self**: [Security Theory Agents](AGENTS.md)
- **Children**:
    - None
- **Key Artifacts**:
    - [Functional Spec](SPEC.md)
    - [Human Readme](README.md)

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: December 2025

## Purpose

The Security Theory submodule provides generic security considerations, principles, frameworks, threat modeling methodologies, risk assessment methods, security architecture patterns, and security best practices for the Codomyrmex platform.

This submodule provides the theoretical foundation and frameworks that guide security implementation across all other security submodules.

## Module Overview

### Key Capabilities
- **Security Principles**: Apply fundamental security principles
- **Security Frameworks**: Use established security frameworks (OWASP, NIST, ISO 27001)
- **Threat Modeling**: Perform threat modeling and analysis
- **Risk Assessment**: Conduct risk assessments and calculations
- **Architecture Patterns**: Apply security architecture patterns
- **Best Practices**: Follow security best practices

### Key Features
- Security principle definitions and application
- Framework retrieval and application
- Threat model creation and analysis
- Risk score calculation
- Security pattern application
- Best practices compliance checking

## Function Signatures

### Security Principles Functions

```python
def get_security_principles() -> List[SecurityPrinciple]
```

Get all security principles.

**Returns:** `List[SecurityPrinciple]` - List of all security principles

```python
def apply_principle(principle_name: str, context: dict) -> dict
```

Apply a security principle to a context.

**Parameters:**
- `principle_name` (str): Name of principle to apply
- `context` (dict): Context information

**Returns:** `dict` - Application results

### Security Frameworks Functions

```python
def get_framework(framework_name: str) -> Optional[SecurityFramework]
```

Get a security framework by name.

**Parameters:**
- `framework_name` (str): Framework name (e.g., "owasp_top_10", "nist_csf", "iso_27001")

**Returns:** `Optional[SecurityFramework]` - Framework object or None if not found

```python
def apply_framework(framework_name: str, context: dict) -> dict
```

Apply a security framework to a context.

**Parameters:**
- `framework_name` (str): Framework name
- `context` (dict): Context information

**Returns:** `dict` - Application results

### Threat Modeling Functions

```python
def create_threat_model(
    system_name: str,
    assets: List[str],
    attack_surface: List[str],
    builder: Optional[ThreatModelBuilder] = None,
) -> ThreatModel
```

Create a threat model for a system.

**Parameters:**
- `system_name` (str): Name of the system
- `assets` (List[str]): List of system assets
- `attack_surface` (List[str]): List of attack surface elements
- `builder` (Optional[ThreatModelBuilder]): Optional builder instance

**Returns:** `ThreatModel` - Created threat model

```python
def analyze_threats(threat_model: ThreatModel) -> dict
```

Analyze threats in a threat model.

**Parameters:**
- `threat_model` (ThreatModel): Threat model to analyze

**Returns:** `dict` - Analysis results with threat counts and details

### Risk Assessment Functions

```python
def assess_risk(
    context: dict,
    assessor: Optional[RiskAssessor] = None,
) -> RiskAssessment
```

Perform a risk assessment.

**Parameters:**
- `context` (dict): Context information for assessment
- `assessor` (Optional[RiskAssessor]): Optional assessor instance

**Returns:** `RiskAssessment` - Risk assessment results

```python
def calculate_risk_score(likelihood: str, impact: str) -> float
```

Calculate risk score from likelihood and impact.

**Parameters:**
- `likelihood` (str): Likelihood level (low, medium, high)
- `impact` (str): Impact level (low, medium, high, critical)

**Returns:** `float` - Risk score (0.0 to 1.0)

### Architecture Patterns Functions

```python
def get_security_patterns() -> List[SecurityPattern]
```

Get all security architecture patterns.

**Returns:** `List[SecurityPattern]` - List of all security patterns

```python
def apply_pattern(pattern_name: str, context: dict) -> dict
```

Apply a security pattern to a context.

**Parameters:**
- `pattern_name` (str): Pattern name (e.g., "zero_trust", "defense_in_depth")
- `context` (dict): Context information

**Returns:** `dict` - Application results

### Best Practices Functions

```python
def get_best_practices(category: str = None) -> List[SecurityBestPractice]
```

Get security best practices, optionally filtered by category.

**Parameters:**
- `category` (str, optional): Category filter (authentication, data_protection, operations, coding)

**Returns:** `List[SecurityBestPractice]` - List of best practices

```python
def check_compliance_with_practices(context: dict) -> dict
```

Check compliance with security best practices.

**Parameters:**
- `context` (dict): Context to check

**Returns:** `dict` - Compliance check results

## Active Components

### Core Implementation
- `__init__.py` – Module initialization and public API exports
- `principles.py` – Security principles definitions
- `frameworks.py` – Security frameworks (OWASP, NIST, ISO 27001)
- `threat_modeling.py` – Threat modeling methodologies
- `risk_assessment.py` – Risk assessment methods
- `architecture_patterns.py` – Security architecture patterns
- `best_practices.py` – Security best practices


### Additional Files
- `README.md` – Readme Md
- `SPEC.md` – Spec Md

## Operating Contracts

### Universal Security Theory Protocols

All security theory operations within the Codomyrmex platform must:

1. **Framework Alignment**: Align with established security frameworks
2. **Principle Application**: Apply security principles consistently
3. **Threat Awareness**: Maintain threat awareness through modeling
4. **Risk Management**: Manage risks through assessment
5. **Best Practices**: Follow security best practices

### Module-Specific Guidelines

#### Security Principles
- Apply principles consistently
- Document principle applications
- Track principle effectiveness

#### Security Frameworks
- Support multiple frameworks
- Allow framework selection
- Provide framework guidance

#### Threat Modeling
- Identify all assets
- Map attack surface
- Assess threat severity
- Prioritize mitigations

#### Risk Assessment
- Calculate risk scores accurately
- Consider likelihood and impact
- Provide risk recommendations
- Track risk over time

## Related Modules
- **Security** (`../`) - Parent security module
- **Digital Security** (`../digital/`) - Applies security theory
- **Physical Security** (`../physical/`) - Applies security theory
- **Cognitive Security** (`../cognitive/`) - Applies security theory

## Navigation Links
- **Human Documentation**: [README.md](README.md)
- **Functional Specification**: [SPEC.md](SPEC.md)

### Module Documentation
- **Module Overview**: [README.md](README.md) - Complete module documentation

### Platform Navigation
- **Parent Directory**: [security](../README.md) - Security module overview
- **Project Root**: [README](../../../../README.md) - Main project documentation
- **Source Root**: [src](../../../../README.md) - Source code documentation

