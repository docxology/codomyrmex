# Personal AI Infrastructure — Privacy Module

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

The Privacy module provides PAI integration for data anonymization and privacy protection.

## PAI Capabilities

### Data Anonymization

Anonymize sensitive data:

```python
from codomyrmex.privacy import Anonymizer

anon = Anonymizer()
safe_text = anon.anonymize(text, types=["email", "phone", "ssn"])
```

### PII Detection

Find personal information:

```python
from codomyrmex.privacy import PIIDetector

detector = PIIDetector()
pii_found = detector.scan(document)

for item in pii_found:
    print(f"{item.type}: {item.location}")
```

## PAI Integration Points

| Component | PAI Use Case |
|-----------|-------------|
| `Anonymizer` | Remove PII |
| `PIIDetector` | Find PII |
| `DataMasker` | Mask sensitive data |

## Navigation

- [README](README.md) | [AGENTS](AGENTS.md) | [SPEC](SPEC.md)
