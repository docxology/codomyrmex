# Codomyrmex Agents — src/codomyrmex/security/cognitive

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Purpose

Human-factor security analysis covering social engineering detection, phishing analysis, awareness training, cognitive threat assessment, and behavioral anomaly detection. All components use regex-based and heuristic pattern matching against communications and user behavior data.

## Key Components

| File | Class / Function | Role |
|------|-----------------|------|
| `social_engineering_detector.py` | `SocialEngineeringDetector` | Regex detection across 5 tactic categories (urgency, authority, information_gathering, reward, fear); `detect()` returns `SocialEngineeringIndicator` list |
| `social_engineering_detector.py` | `analyze_communication()` | Full analysis with risk score calculation |
| `phishing_analyzer.py` | `PhishingAnalyzer` | 8-indicator phishing detection: IP URLs, URL shorteners, non-HTTPS, urgency language, sensitive info requests, excessive punctuation/caps, sender domain mismatch |
| `phishing_analyzer.py` | `analyze_email()` / `detect_phishing_attempt()` | Convenience wrappers returning `PhishingAnalysis` or `bool` |
| `awareness_training.py` | `AwarenessTrainer` | Training module management with 8 pre-built `TrainingTopic` templates; `create_module()` and `assess_effectiveness()` |
| `cognitive_threat_assessment.py` | `CognitiveThreatAssessor` | Context-based threat assessment checking training level, access level, environment, recent incidents, social media exposure; returns `CognitiveThreat` list |
| `cognitive_threat_assessment.py` | `evaluate_human_factors()` | Risk scoring (0.0-1.0) based on training, stress, risk tolerance, and access level |
| `behavior_analysis.py` | `BehaviorAnalyzer` | User behavior pattern analysis with history tracking; `analyze_behavior()` classifies actions by risk level against `SENSITIVE_RESOURCES` set |
| `behavior_analysis.py` | `detect_anomalies()` | Anomaly detection for unusual login times, new locations, and first-time sensitive resource access |

## Operating Contracts

- All detectors are stateless per-call; `BehaviorAnalyzer` accumulates user history across calls.
- Phishing confidence scales linearly: `min(indicator_count * 0.2, 1.0)`.
- `BehaviorAnalyzer.SENSITIVE_RESOURCES` defines the canonical set of high-risk resources.
- Anomaly detection uses a 4-hour deviation threshold for login time anomalies.
- Errors must be logged via `logging_monitoring` before re-raising.

## Integration Points

- **Depends on**: `codomyrmex.logging_monitoring.core.logger_config`
- **Used by**: Security dashboards, agent input screening, compliance assessments

## Navigation

- **Parent**: [security](../README.md)
- **Root**: [Root](../../../../README.md)
