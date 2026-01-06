# Codomyrmex Agents — src/codomyrmex/security/cognitive

## Signposting
- **Parent**: [security](../AGENTS.md)
- **Self**: [Cognitive Security Agents](AGENTS.md)
- **Children**:
    - None
- **Key Artifacts**:
    - [Functional Spec](SPEC.md)
    - [Human Readme](README.md)

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: December 2025

## Purpose

The Cognitive Security submodule provides cognitive security practices, social engineering defense, phishing detection and analysis, security awareness training, cognitive threat assessment, and human factor security analysis for the Codomyrmex platform.

This submodule addresses the human element of security, focusing on protecting against social engineering, phishing, and other cognitive-based attacks.

## Module Overview

### Key Capabilities
- **Social Engineering Detection**: Detect social engineering attempts in communications
- **Phishing Analysis**: Analyze emails and communications for phishing indicators
- **Awareness Training**: Provide security awareness training modules
- **Cognitive Threat Assessment**: Assess cognitive security threats
- **Behavior Analysis**: Analyze user behavior for security anomalies

### Key Features
- Communication analysis for social engineering indicators
- Email phishing detection with confidence scoring
- Training module creation and effectiveness assessment
- Cognitive threat evaluation
- User behavior pattern analysis

## Function Signatures

### Social Engineering Detection Functions

```python
def detect_social_engineering(
    communication: str,
    detector: Optional[SocialEngineeringDetector] = None,
) -> List[SocialEngineeringIndicator]
```

Detect social engineering indicators in communication.

**Parameters:**
- `communication` (str): Communication text to analyze
- `detector` (Optional[SocialEngineeringDetector]): Optional detector instance

**Returns:** `List[SocialEngineeringIndicator]` - List of detected indicators

```python
def analyze_communication(
    communication: str,
    detector: Optional[SocialEngineeringDetector] = None,
) -> dict
```

Analyze communication for social engineering.

**Parameters:**
- `communication` (str): Communication text to analyze
- `detector` (Optional[SocialEngineeringDetector]): Optional detector instance

**Returns:** `dict` - Analysis results with indicators and risk score

### Phishing Analysis Functions

```python
def analyze_email(
    email_content: str,
    sender: Optional[str] = None,
    analyzer: Optional[PhishingAnalyzer] = None,
) -> PhishingAnalysis
```

Analyze email for phishing indicators.

**Parameters:**
- `email_content` (str): Email content to analyze
- `sender` (Optional[str]): Optional sender address
- `analyzer` (Optional[PhishingAnalyzer]): Optional analyzer instance

**Returns:** `PhishingAnalysis` - Analysis results with phishing status and confidence

```python
def detect_phishing_attempt(
    email_content: str,
    sender: Optional[str] = None,
    analyzer: Optional[PhishingAnalyzer] = None,
) -> bool
```

Detect if email is a phishing attempt.

**Parameters:**
- `email_content` (str): Email content to analyze
- `sender` (Optional[str]): Optional sender address
- `analyzer` (Optional[PhishingAnalyzer]): Optional analyzer instance

**Returns:** `bool` - True if phishing detected, False otherwise

### Awareness Training Functions

```python
def create_training_module(
    module_id: str,
    title: str,
    description: str,
    content: str,
    difficulty: str = "intermediate",
    trainer: Optional[AwarenessTrainer] = None,
) -> TrainingModule
```

Create a security awareness training module.

**Parameters:**
- `module_id` (str): Unique module identifier
- `title` (str): Module title
- `description` (str): Module description
- `content` (str): Training content
- `difficulty` (str): Difficulty level (beginner, intermediate, advanced)
- `trainer` (Optional[AwarenessTrainer]): Optional trainer instance

**Returns:** `TrainingModule` - Created training module

```python
def assess_training_effectiveness(
    user_id: str,
    trainer: Optional[AwarenessTrainer] = None,
) -> dict
```

Assess training effectiveness for a user.

**Parameters:**
- `user_id` (str): User identifier
- `trainer` (Optional[AwarenessTrainer]): Optional trainer instance

**Returns:** `dict` - Effectiveness assessment with scores and metrics

### Cognitive Threat Assessment Functions

```python
def assess_cognitive_threats(
    context: dict,
    assessor: Optional[CognitiveThreatAssessor] = None,
) -> dict
```

Assess cognitive security threats in a context.

**Parameters:**
- `context` (dict): Context information for assessment
- `assessor` (Optional[CognitiveThreatAssessor]): Optional assessor instance

**Returns:** `dict` - Threat assessment results

```python
def evaluate_human_factors(
    scenario: dict,
    assessor: Optional[CognitiveThreatAssessor] = None,
) -> dict
```

Evaluate human factors in security scenarios.

**Parameters:**
- `scenario` (dict): Scenario information
- `assessor` (Optional[CognitiveThreatAssessor]): Optional assessor instance

**Returns:** `dict` - Human factors evaluation

### Behavior Analysis Functions

```python
def analyze_user_behavior(
    user_id: str,
    behavior_data: dict,
    analyzer: Optional[BehaviorAnalyzer] = None,
) -> List[BehaviorPattern]
```

Analyze user behavior patterns.

**Parameters:**
- `user_id` (str): User identifier
- `behavior_data` (dict): Behavior data to analyze
- `analyzer` (Optional[BehaviorAnalyzer]): Optional analyzer instance

**Returns:** `List[BehaviorPattern]` - Detected behavior patterns

```python
def detect_anomalous_behavior(
    user_id: str,
    current_behavior: dict,
    analyzer: Optional[BehaviorAnalyzer] = None,
) -> List[Anomaly]
```

Detect anomalous user behavior.

**Parameters:**
- `user_id` (str): User identifier
- `current_behavior` (dict): Current behavior data
- `analyzer` (Optional[BehaviorAnalyzer]): Optional analyzer instance

**Returns:** `List[Anomaly]` - Detected anomalies

## Active Components

### Core Implementation
- `__init__.py` – Module initialization and public API exports
- `social_engineering_detector.py` – Social engineering detection
- `phishing_analyzer.py` – Phishing email analysis
- `awareness_training.py` – Security awareness training
- `cognitive_threat_assessment.py` – Cognitive threat assessment
- `behavior_analysis.py` – User behavior analysis

## Operating Contracts

### Universal Cognitive Security Protocols

All cognitive security operations within the Codomyrmex platform must:

1. **Human-Centric**: Focus on human factors in security
2. **Education First**: Prioritize training and awareness
3. **Behavioral Analysis**: Monitor and analyze user behavior
4. **Threat Detection**: Detect cognitive-based threats
5. **Continuous Improvement**: Improve training effectiveness

### Module-Specific Guidelines

#### Social Engineering Detection
- Analyze communication patterns
- Identify urgency tactics
- Detect authority impersonation
- Assess information gathering attempts

#### Phishing Analysis
- Check for suspicious URLs
- Validate sender addresses
- Detect urgency tactics
- Identify request for sensitive information

#### Awareness Training
- Create engaging training modules
- Assess training effectiveness
- Track user progress
- Provide remediation guidance

## Related Modules
- **Security** (`../`) - Parent security module
- **Physical Security** (`../physical/`) - Physical security complement
- **Digital Security** (`../digital/`) - Digital security complement
- **Logging Monitoring** (`../../logging_monitoring/`) - Event logging integration

## Navigation Links
- **Human Documentation**: [README.md](README.md)
- **Functional Specification**: [SPEC.md](SPEC.md)

### Module Documentation
- **Module Overview**: [README.md](README.md) - Complete module documentation

### Platform Navigation
- **Parent Directory**: [security](../README.md) - Security module overview
- **Project Root**: [README](../../../../README.md) - Main project documentation
- **Source Root**: [src](../../../../README.md) - Source code documentation

