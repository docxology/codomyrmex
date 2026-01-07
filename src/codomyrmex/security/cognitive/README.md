# cognitive

## Signposting
- **Parent**: [security](../README.md)
- **Children**:
    - None
- **Key Artifacts**:
    - [Agent Guide](AGENTS.md)
    - [Functional Spec](SPEC.md)

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: January 2026

## Overview

Cognitive security including phishing analysis, social engineering detection, behavior analysis, cognitive threat assessment, and awareness training. Focuses on human-factor security threats and cognitive vulnerabilities.

## Directory Contents
- `README.md` – File
- `SPEC.md` – File
- `__init__.py` – File
- `awareness_training.py` – File
- `behavior_analysis.py` – File
- `cognitive_threat_assessment.py` – File
- `phishing_analyzer.py` – File
- `social_engineering_detector.py` – File

## Navigation
- **Technical Documentation**: [AGENTS.md](AGENTS.md)
- **Functional Specification**: [SPEC.md](SPEC.md)
- **Parent Directory**: [security](../README.md)
- **Project Root**: [README](../../../../README.md)

## Getting Started

To use this module in your project, import the necessary components:

```python
from codomyrmex.security.cognitive import (
    PhishingAnalyzer,
    SocialEngineeringDetector,
    BehaviorAnalyzer,
)

# Analyze phishing attempts
phishing_analyzer = PhishingAnalyzer()
result = phishing_analyzer.analyze_email(email_content="...")
print(f"Phishing score: {result.risk_score}")

# Detect social engineering
detector = SocialEngineeringDetector()
threats = detector.detect_patterns(interaction_data={...})
print(f"Threats detected: {len(threats)}")

# Analyze behavior
behavior_analyzer = BehaviorAnalyzer()
anomalies = behavior_analyzer.analyze_patterns(user_behavior={...})
print(f"Anomalies: {len(anomalies)}")
```

