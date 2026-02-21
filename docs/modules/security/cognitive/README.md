# Security Cognitive Submodule

**Version**: v1.0.0 | **Source**: [`src/codomyrmex/security/cognitive/`](../../../../src/codomyrmex/security/cognitive/)

## Overview

Cognitive security practices including social engineering detection, phishing analysis, security awareness training, cognitive threat assessment, and user behavior analysis. Organized across 5 component files, each conditionally imported.

## Components

| Source File | Classes / Functions | Availability Flag |
|-------------|--------------------|--------------------|
| `social_engineering_detector.py` | `SocialEngineeringDetector`, `detect_social_engineering()`, `analyze_communication()` | `SOCIAL_ENGINEERING_AVAILABLE` |
| `phishing_analyzer.py` | `PhishingAnalyzer`, `analyze_email()`, `detect_phishing_attempt()` | `PHISHING_ANALYSIS_AVAILABLE` |
| `awareness_training.py` | `AwarenessTrainer`, `create_training_module()`, `assess_training_effectiveness()` | `AWARENESS_TRAINING_AVAILABLE` |
| `cognitive_threat_assessment.py` | `CognitiveThreatAssessor`, `assess_cognitive_threats()`, `evaluate_human_factors()` | `COGNITIVE_THREAT_AVAILABLE` |
| `behavior_analysis.py` | `BehaviorAnalyzer`, `analyze_user_behavior()`, `detect_anomalous_behavior()` | `BEHAVIOR_ANALYSIS_AVAILABLE` |

## Exports (via top-level `security/__init__.py`)

When `COGNITIVE_AVAILABLE` is `True`, the following 15 symbols are re-exported:
- `SocialEngineeringDetector`, `detect_social_engineering`, `analyze_communication`
- `PhishingAnalyzer`, `analyze_email`, `detect_phishing_attempt`
- `AwarenessTrainer`, `create_training_module`, `assess_training_effectiveness`
- `CognitiveThreatAssessor`, `assess_cognitive_threats`, `evaluate_human_factors`
- `BehaviorAnalyzer`, `analyze_user_behavior`, `detect_anomalous_behavior`

## Convenience Functions (10)

| Function | Description |
|----------|-------------|
| `detect_social_engineering()` | Detect social engineering attempts |
| `analyze_communication()` | Analyze communication for manipulation patterns |
| `analyze_email()` | Analyze email for phishing indicators |
| `detect_phishing_attempt()` | Detect phishing attempt |
| `create_training_module()` | Create security awareness training module |
| `assess_training_effectiveness()` | Assess effectiveness of training |
| `assess_cognitive_threats()` | Assess cognitive security threats |
| `evaluate_human_factors()` | Evaluate human factor vulnerabilities |
| `analyze_user_behavior()` | Analyze user behavior patterns |
| `detect_anomalous_behavior()` | Detect anomalous behavior |

## Implementation Details

- Social engineering detection uses regex pattern matching across 5 tactic categories (urgency, authority, information gathering, reward, fear)
- Phishing analysis checks 8 indicators including suspicious URLs, urgency language, sensitive info requests, excessive punctuation, and sender domain mismatch
- Behavior analysis computes statistical profiles from user history and detects anomalies via baseline comparison
- Cognitive threat assessment generates threats based on training level, access level, environment, recent incidents, and social media exposure
- Awareness training includes TrainingTopic and TrainingDifficulty enums with predefined training templates

## Tests

[`src/codomyrmex/tests/unit/security/test_security_cognitive.py`](../../../../src/codomyrmex/tests/unit/security/test_security_cognitive.py)

## Navigation

- **Parent**: [Security Module](../README.md)
- **Source**: [`src/codomyrmex/security/cognitive/`](../../../../src/codomyrmex/security/cognitive/)
