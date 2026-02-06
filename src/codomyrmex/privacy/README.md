# Privacy Module

**Version**: v0.1.0 | **Status**: Active

Data sanitization and anonymous routing for privacy protection.

## Quick Start

```python
from codomyrmex.privacy import CrumbCleaner, MixnetProxy

# Data sanitization
cleaner = CrumbCleaner()

# Remove PII from text
sanitized = cleaner.clean("Contact me at john@example.com or 555-1234")
# "Contact me at [EMAIL] or [PHONE]"

# Configure patterns
cleaner.add_pattern("ssn", r"\d{3}-\d{2}-\d{4}", "[SSN]")
cleaner.add_pattern("credit_card", r"\d{4}-\d{4}-\d{4}-\d{4}", "[CARD]")

# Anonymous routing via mixnet
proxy = MixnetProxy()
proxy.configure(hop_count=3, encryption="aes-256")

# Route request anonymously
response = proxy.route(request, destination="api.example.com")
```

## Exports

| Class | Description |
|-------|-------------|
| `CrumbCleaner` | PII detection and sanitization |
| `MixnetProxy` | Anonymous multi-hop routing |

## Use Cases

- **Log sanitization** — Remove sensitive data before logging
- **Data export** — Clean PII from datasets
- **Anonymous requests** — Route API calls through mixnet

## Navigation

- [SPEC](SPEC.md) | [AGENTS](AGENTS.md) | [PAI](PAI.md)
