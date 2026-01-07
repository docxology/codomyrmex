# Codomyrmex Agents — src/codomyrmex/security

## Signposting
- **Parent**: [codomyrmex](../AGENTS.md)
- **Self**: [Security Agents](AGENTS.md)
- **Children**:
    - [cognitive](cognitive/AGENTS.md)
    - [digital](digital/AGENTS.md)
    - [docs](docs/AGENTS.md)
    - [physical](physical/AGENTS.md)
    - [security_theory](security_theory/AGENTS.md)
    - [tests](tests/AGENTS.md)
    - [theory](theory/AGENTS.md)
- **Key Artifacts**:
    - [Functional Spec](SPEC.md)
    - [Human Readme](README.md)

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: December 2025

## Purpose

The Security module provides comprehensive security capabilities organized into four specialized submodules:
- **Physical Security**: Physical security practices, access control, surveillance, physical asset protection
- **Digital Security**: Digital security practices - vulnerability scanning, code security analysis, secrets detection, encryption, certificate validation, compliance checking, security monitoring, and reporting
- **Cognitive Security**: Cognitive security practices, social engineering defense, phishing detection and analysis, security awareness training, cognitive threat assessment, and human factor security analysis
- **Theory**: Generic security considerations, principles, frameworks, threat modeling methodologies, risk assessment methods, security architecture patterns, and security best practices

## Module Overview

### Key Capabilities
- **Physical Security**: Access control systems, physical asset inventory, surveillance monitoring, physical vulnerability assessment, security perimeter management
- **Digital Security**: Vulnerability scanning, code security analysis, secrets detection, encryption management, certificate validation, compliance checking, security monitoring, security reporting
- **Cognitive Security**: Social engineering detection, phishing detection and analysis, security awareness training, cognitive threat assessment, human factor security analysis, security behavior analysis
- **Theory**: Security principles and frameworks, threat modeling, risk assessment methodologies, security architecture patterns, security best practices, security standards and compliance frameworks

## Function Signatures

### Digital Security (from security/digital)

See [Digital Security AGENTS.md](digital/AGENTS.md) for complete function signatures.

### Physical Security

```python
def check_access_permission(user_id: str, resource: str, permission_type: str) -> bool
def grant_access(user_id: str, resource: str, permission_type: str, expires_at: Optional[datetime] = None) -> AccessPermission
def revoke_access(user_id: str, resource: str) -> bool
def register_asset(asset_id: str, name: str, asset_type: str, location: str) -> PhysicalAsset
def track_asset(asset_id: str, location: Optional[str] = None) -> bool
def monitor_physical_access(location: str, user_id: str) -> PhysicalEvent
def assess_physical_security(location: str) -> dict
def check_perimeter_security() -> dict
```

### Cognitive Security

```python
def detect_social_engineering(communication: str) -> List[SocialEngineeringIndicator]
def analyze_email(email_content: str, sender: Optional[str] = None) -> PhishingAnalysis
def create_training_module(module_id: str, title: str, description: str, content: str) -> TrainingModule
def assess_cognitive_threats(context: dict) -> dict
def analyze_user_behavior(user_id: str, behavior_data: dict) -> List[BehaviorPattern]
```

### Security Theory

```python
def get_security_principles() -> List[SecurityPrinciple]
def get_framework(framework_name: str) -> Optional[SecurityFramework]
def create_threat_model(system_name: str, assets: List[str], attack_surface: List[str]) -> ThreatModel
def assess_risk(context: dict) -> RiskAssessment
def get_security_patterns() -> List[SecurityPattern]
def get_best_practices(category: str = None) -> List[SecurityBestPractice]
```

## Active Components

### Submodules
- `physical/` – Physical security submodule
- `digital/` – Digital security submodule (formerly security.digital)
- `cognitive/` – Cognitive security submodule
- `theory/` – Security theory submodule

### Documentation
- `README.md` – Module overview
- `SPEC.md` – Functional specification
- `AGENTS.md` – This file: agent coordination


### Additional Files
- `__init__.py` –   Init   Py
- `__pycache__` –   Pycache  
- `cognitive` – Cognitive
- `digital` – Digital
- `docs` – Docs
- `physical` – Physical
- `security_theory` – Security Theory
- `tests` – Tests
- `theory` – Theory

## Operating Contracts

### Universal Security Protocols

All security operations within the Codomyrmex platform must:

1. **Comprehensive Coverage** - Address physical, digital, cognitive, and theoretical aspects
2. **Risk-Based Approach** - Prioritize based on risk assessment
3. **Continuous Monitoring** - Monitor security events and threats
4. **Compliance Alignment** - Align with security standards and frameworks
5. **Documentation** - Maintain clear security documentation

### Module-Specific Guidelines

#### Physical Security
- Manage access control systems
- Track physical assets
- Monitor physical access events
- Assess physical vulnerabilities

#### Digital Security
- Scan for vulnerabilities
- Detect secrets and sensitive data
- Manage encryption
- Validate certificates
- Check compliance

#### Cognitive Security
- Detect social engineering
- Analyze phishing attempts
- Provide awareness training
- Assess cognitive threats

#### Security Theory
- Apply security principles
- Use security frameworks
- Perform threat modeling
- Conduct risk assessments

## Related Modules
- **Static Analysis** (`static_analysis/`) - Code security analysis integration
- **Logging Monitoring** (`logging_monitoring/`) - Security event logging
- **Environment Setup** (`environment_setup/`) - Security environment validation

## Navigation Links
- **Human Documentation**: [README.md](README.md)
- **Functional Specification**: [SPEC.md](SPEC.md)

### Module Documentation
- **Module Overview**: [README.md](README.md) - Complete module documentation

### Platform Navigation
- **Parent Directory**: [codomyrmex](../README.md) - Package overview
- **Project Root**: [README](../../../README.md) - Main project documentation
- **Source Root**: [src](../../README.md) - Source code documentation

