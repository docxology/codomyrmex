# Specification: Demos Module

## Goal
Provide a unified way to register, discover, and execute demonstrations of Codomyrmex modules.

## Components

### 1. `DemoRegistry`
- Maintains a mapping of demo names to their implementation (callable or script path).
- Supports categories and metadata (description, author, requirements).
- Provides methods for filtering and listing demos.

### 2. `@demo` Decorator
- Facilitates easy registration of python-based demos.
- Captures metadata at registration time.

### 3. Demo Discovery
- Ability to scan directories (like `scripts/demos/`) for standalone demo scripts.

### 4. Execution Engine
- Leverages `codomyrmex.orchestrator.thin` for running demos.
- Handles timeouts and logging.

## Data Structures

```python
@dataclass
class DemoResult:
    name: str
    success: bool
    output: str
    error: Optional[str]
    execution_time: float
```

## Security Considerations
- Demos should not execute untrusted code without proper sandboxing (leveraging the `coding` module's sandbox if necessary).
- Demos should not require elevated privileges unless explicitly stated and confirmed.
