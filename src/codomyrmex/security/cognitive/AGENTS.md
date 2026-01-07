# Codomyrmex Agents — src/codomyrmex/security/cognitive

## Signposting
- **Parent**: [security](../AGENTS.md)
- **Self**: [Agents](AGENTS.md)
- **Children**:
    - None
- **Key Artifacts**:
    - [Functional Spec](SPEC.md)
    - [Human Readme](README.md)

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: January 2026

## Purpose
Cognitive security including phishing analysis, social engineering detection, behavior analysis, cognitive threat assessment, and awareness training. Focuses on human-factor security threats and cognitive vulnerabilities.

## Active Components
- `README.md` – Project file
- `SPEC.md` – Project file
- `__init__.py` – Module exports and public API
- `awareness_training.py` – Security awareness training
- `behavior_analysis.py` – Behavior analysis for threat detection
- `cognitive_threat_assessment.py` – Cognitive threat assessment
- `phishing_analyzer.py` – Phishing email and message analysis
- `social_engineering_detector.py` – Social engineering attack detection

## Key Classes and Functions

### PhishingAnalyzer (`phishing_analyzer.py`)
- `PhishingAnalyzer()` – Analyze phishing attempts
- `analyze_email(email: dict) -> PhishingAnalysis` – Analyze email for phishing indicators
- `analyze_message(message: str) -> PhishingAnalysis` – Analyze message for phishing

### SocialEngineeringDetector (`social_engineering_detector.py`)
- `SocialEngineeringDetector()` – Detect social engineering attacks
- `detect_attack(interaction: dict) -> DetectionResult` – Detect social engineering attack

### CognitiveThreatAssessment (`cognitive_threat_assessment.py`)
- `CognitiveThreatAssessment()` – Assess cognitive threats
- `assess_threat(context: dict) -> ThreatAssessment` – Assess cognitive threat

### BehaviorAnalysis (`behavior_analysis.py`)
- `BehaviorAnalysis()` – Analyze user behavior
- `analyze_behavior(behavior_data: dict) -> BehaviorAnalysis` – Analyze behavior patterns

### AwarenessTraining (`awareness_training.py`)
- `AwarenessTraining()` – Security awareness training
- `generate_training_content(topic: str) -> TrainingContent` – Generate training content

## Operating Contracts
- Maintain alignment between code, documentation, and configured workflows.
- Ensure Model Context Protocol interfaces remain available for sibling agents.
- Record outcomes in shared telemetry and update TODO queues when necessary.

## Navigation Links
- **Human Documentation**: [README.md](README.md)
- **Functional Specification**: [SPEC.md](SPEC.md)
- **📁 Parent Directory**: [security](../README.md) - Parent directory documentation
- **🏠 Project Root**: [README](../../../../README.md) - Main project documentation