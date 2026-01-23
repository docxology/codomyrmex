# Codomyrmex Agents — src/codomyrmex/security/theory

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: January 2026

## Purpose

Provides security theory foundations including security principles, frameworks (OWASP, NIST, ISO 27001), threat modeling methodologies (STRIDE), risk assessment methods, security architecture patterns, and security best practices.

## Active Components

- `principles.py` - Security principles with `SecurityPrinciple`
- `frameworks.py` - Security frameworks with `SecurityFramework`
- `threat_modeling.py` - STRIDE threat modeling with `ThreatModelBuilder`
- `risk_assessment.py` - Risk assessment with `RiskAssessor`
- `architecture_patterns.py` - Security patterns with `SecurityPattern`
- `best_practices.py` - Best practices with `SecurityBestPractice`
- `__init__.py` - Module exports with conditional availability

## Key Classes and Functions

### principles.py
- **`SecurityPrinciple`** - Fundamental security principle definition.
- **`PrincipleCategory`** - Enum: ARCHITECTURE, ACCESS_CONTROL, GOVERNANCE, DESIGN, CONFIGURATION, DATA_PROTECTION, NETWORK, CRYPTOGRAPHY, INCIDENT_RESPONSE.
- **Defined Principles**: defense_in_depth, least_privilege, separation_of_duties, fail_secure, secure_by_default, need_to_know, confidentiality, integrity, availability, non_repudiation, audit.
- **Functions**: `get_security_principles()`, `get_principle(name)`, `get_principles_by_category(category)`, `apply_principle(name, context)`, `validate_principle_application(name, context)`.

### frameworks.py
- **`SecurityFramework`** - Security framework definition with standards.
- **`FrameworkStandard`** - Individual standard within a framework.
- **`FrameworkCategory`** - Enum: WEB_SECURITY, APPLICATION_SECURITY, GOVERNANCE, RISK_MANAGEMENT, INFORMATION_SECURITY, COMPLIANCE, CYBERSECURITY.
- **Defined Frameworks**:
  - `owasp_top_10` - OWASP Top 10 (2021) web security risks.
  - `nist_csf` - NIST Cybersecurity Framework (Identify, Protect, Detect, Respond, Recover).
  - `iso_27001` - ISO 27001 Information Security Management.
  - `cis_controls` - CIS Critical Security Controls v8.
  - `pci_dss` - PCI DSS v4.0 payment card security.
- **Functions**: `get_framework(name)`, `get_all_frameworks()`, `get_frameworks_by_category(category)`, `apply_framework(name, context)`, `check_framework_compliance(name, context)`.

### threat_modeling.py
- **`ThreatModelBuilder`** - Creates threat models using methodologies:
  - `create_model(system_name, assets, attack_surface, assumptions, constraints)` - Build threat model.
  - Supports STRIDE methodology: Spoofing, Tampering, Repudiation, Information Disclosure, Denial of Service, Elevation of Privilege.
- **`ThreatModel`** - Model with system_name, threats, assets, attack_surface, methodology.
- **`Threat`** - Threat with type, severity, mitigation, likelihood, impact, attack_vectors, detection_methods.
- **`ThreatSeverity`** / **`ThreatCategory`** - Enums for classification.
- **Functions**: `create_threat_model()`, `analyze_threats(model)`, `prioritize_threats(model)`.

### risk_assessment.py
- **`RiskAssessor`** - Performs risk assessments:
  - `assess(context)` - Full risk assessment with identified risks and recommendations.
  - Supports methodologies: qualitative, quantitative, hybrid.
  - Generates risk matrix and summary.
- **`Risk`** - Risk with likelihood, impact, risk_score, affected_assets, existing_controls, recommended_controls, residual_risk.
- **`RiskAssessment`** - Assessment results with risks, overall_risk_level, recommendations, risk_matrix.
- **`RiskLevel`** / **`LikelihoodLevel`** / **`ImpactLevel`** - Enums for classification.
- **Functions**: `assess_risk(context)`, `calculate_risk_score(likelihood, impact)`, `prioritize_risks(risks)`, `calculate_aggregate_risk(risks)`.

### architecture_patterns.py
- **`SecurityPattern`** - Security architecture pattern definition.
- **`PatternCategory`** - Enum: ARCHITECTURE, AUTHENTICATION, AUTHORIZATION, ENCRYPTION, NETWORK, DATA_PROTECTION, ACCESS_CONTROL, MONITORING, INCIDENT_RESPONSE.
- **Defined Patterns**: zero_trust, defense_in_depth, principle_of_least_privilege, secure_by_default, fail_secure, separation_of_concerns, microservices_security, encryption_at_rest, encryption_in_transit, rate_limiting, circuit_breaker.
- **Functions**: `get_security_patterns()`, `get_pattern(name)`, `get_patterns_by_category(category)`, `apply_pattern(name, context)`, `validate_pattern_application(name, context)`.

### best_practices.py
- **`SecurityBestPractice`** - Best practice definition with implementation guidance.
- **`PracticeCategory`** - Enum: AUTHENTICATION, AUTHORIZATION, DATA_PROTECTION, CODING, CONFIGURATION, OPERATIONS, NETWORK, CRYPTOGRAPHY, INCIDENT_RESPONSE, COMPLIANCE.
- **`PracticePriority`** - Enum: LOW, MEDIUM, HIGH, CRITICAL.
- **Defined Practices**: strong_passwords, multi_factor_authentication, encryption_at_rest, encryption_in_transit, regular_updates, input_validation, least_privilege_access, secure_coding, security_monitoring, incident_response, backup_recovery, vulnerability_management, secure_configuration, access_reviews, secure_development_lifecycle.
- **Functions**: `get_best_practices(category)`, `get_practice(name)`, `get_practices_by_priority(priority)`, `get_practices_for_category(category)`, `check_compliance_with_practices(context)`, `prioritize_practices(practices)`.

## Operating Contracts

- Risk scores are calculated as likelihood * impact (0.0 to 1.0).
- Risk levels: LOW (<0.25), MEDIUM (0.25-0.5), HIGH (0.5-0.75), CRITICAL (>0.75).
- Residual risk is calculated by reducing risk score based on existing controls.
- Threat models identify threats based on STRIDE methodology by default.
- Framework compliance checks return unknown status for automated validation.
- Best practices include compliance requirements (NIST, PCI DSS, ISO 27001, OWASP).

## Signposting

- **Dependencies**: None (pure Python implementation).
- **Parent Directory**: [security](../README.md) - Parent module documentation.
- **Related Modules**:
  - `digital/` - Applies theory to digital security.
  - `physical/` - Applies theory to physical security.
  - `cognitive/` - Applies theory to human factors.
- **Project Root**: [../../../../README.md](../../../../README.md) - Main project documentation.
