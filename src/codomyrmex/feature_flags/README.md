# feature_flags

Dynamic feature management and toggle module.

## Overview

This module provides a robust framework for managing feature flags (toggles) within Codomyrmex applications. It enables safe feature rollouts, A/B testing, and operational toggles without code redeployment.

## Key Features

- **Decoupled Configuration**: Feature states are managed independently of the application logic.
- **Contextual Evaluation**: Flags can be evaluated based on user context or environment.
- **Persistence Layer**: Built-in `load_from_file` and `save_to_file` for flag configuration.
- **Rollout Strategies**: Support for percentage-based rollouts and target groups.
- **Audit Logging**: Traceability of flag state changes and evaluation results.

## Usage

```python
from codomyrmex.feature_flags import FeatureManager

manager = FeatureManager()

# Evaluate a flag for a specific user
if manager.is_enabled("new-ui-v2", user_id="user_123"):
    render_new_ui()
else:
    render_old_ui()
```

## Navigation Links

- [Functional Specification](SPEC.md)
- [Technical Documentation](AGENTS.md)
