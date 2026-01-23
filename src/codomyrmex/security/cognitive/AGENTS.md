# Codomyrmex Agents — src/codomyrmex/security/cognitive

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: January 2026

## Purpose

Provides cognitive security capabilities including social engineering detection, phishing analysis, security awareness training, cognitive threat assessment, and user behavior analysis for human factor security.

## Active Components

- `social_engineering_detector.py` - Social engineering detection with `SocialEngineeringDetector`
- `phishing_analyzer.py` - Phishing analysis with `PhishingAnalyzer`
- `awareness_training.py` - Training management with `AwarenessTrainer`
- `cognitive_threat_assessment.py` - Threat assessment with `CognitiveThreatAssessor`
- `behavior_analysis.py` - Behavior analysis with `BehaviorAnalyzer`
- `__init__.py` - Module exports with conditional availability

## Key Classes and Functions

### social_engineering_detector.py
- **`SocialEngineeringDetector`** - Detects social engineering attempts:
  - `detect(communication)` - Detect social engineering indicators in communication.
  - `analyze_communication(communication)` - Full analysis with risk score.
  - `_calculate_risk_score(indicators)` - Calculate weighted risk score.
  - Detects: urgency tactics, authority impersonation, information gathering, suspicious requests.
- **`SocialEngineeringIndicator`** - Dataclass with indicator_type, severity, description, confidence.
- **Convenience Functions**: `detect_social_engineering()`, `analyze_communication()`.

### phishing_analyzer.py
- **`PhishingAnalyzer`** - Analyzes emails for phishing attempts:
  - `analyze(email_content, sender)` - Full phishing analysis.
  - Returns: is_phishing, confidence score, indicators, risk_level, recommendation.
  - Detects: suspicious URLs, suspicious senders, urgency tactics, information requests, grammar errors.
- **`PhishingAnalysis`** - Dataclass with is_phishing, confidence (0.0-1.0), indicators, risk_level (low/medium/high/critical), recommendation.
- **Convenience Functions**: `analyze_email()`, `detect_phishing_attempt()`.

### awareness_training.py
- **`AwarenessTrainer`** - Manages security awareness training:
  - `create_module(module_id, title, description, content, difficulty)` - Create training module.
  - `assess_effectiveness(user_id)` - Assess training effectiveness for a user.
  - Returns: modules_completed, average_score, effectiveness rating.
- **`TrainingModule`** - Dataclass with module_id, title, description, content, created_at, difficulty (beginner/intermediate/advanced).
- **`TrainingResult`** - Dataclass with user_id, module_id, score (0.0-1.0), completed_at, effectiveness.
- **Convenience Functions**: `create_training_module()`, `assess_training_effectiveness()`.

### cognitive_threat_assessment.py
- **`CognitiveThreatAssessor`** - Assesses cognitive security threats:
  - `assess_threats(context)` - Identify cognitive threats in context.
  - `assess_cognitive_threats(context)` - Comprehensive assessment with counts.
  - `evaluate_human_factors(scenario)` - Evaluate human factors: training_level, experience, stress_level, risk_tolerance.
- **`CognitiveThreat`** - Dataclass with threat_id, threat_type, severity, description, human_factors, mitigation.
- **Convenience Functions**: `assess_cognitive_threats()`, `evaluate_human_factors()`.

### behavior_analysis.py
- **`BehaviorAnalyzer`** - Analyzes user behavior for security:
  - `analyze_behavior(user_id, behavior_data)` - Analyze and record behavior patterns.
  - `detect_anomalies(user_id, current_behavior)` - Detect anomalous behavior vs history.
  - Maintains behavior history per user for baseline comparison.
- **`BehaviorPattern`** - Dataclass with pattern_type, frequency, risk_level, description.
- **`Anomaly`** - Dataclass with anomaly_type, severity, description, confidence (0.0-1.0).
- **Convenience Functions**: `analyze_user_behavior()`, `detect_anomalous_behavior()`.

## Operating Contracts

- Risk scores are weighted by indicator severity (high: 1.0, medium: 0.5, low: 0.25).
- Training effectiveness is calculated from average scores across completed modules.
- Behavior analysis maintains historical data for anomaly detection.
- Confidence scores range from 0.0 (no confidence) to 1.0 (high confidence).
- Phishing risk levels: low (<0.3), medium (0.3-0.5), high (0.5-0.7), critical (>0.7).
- Human factor evaluation considers training, experience, stress, and risk tolerance.

## Signposting

- **Dependencies**: None (pure Python implementation).
- **Parent Directory**: [security](../README.md) - Parent module documentation.
- **Related Modules**:
  - `digital/` - Technical security controls.
  - `physical/` - Physical security controls.
  - `theory/` - Security frameworks and best practices.
- **Project Root**: [../../../../README.md](../../../../README.md) - Main project documentation.
