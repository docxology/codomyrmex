# feature_flags - Technical Documentation

## Operating Contract

- Always provide a safe default value if a flag evaluation fails.
- Minimize latency in flag evaluations by using local caching.
- Ensure all flags are documented with their purpose and owner.
- Periodically audit and remove deprecated flags to prevent 'toggle debt'.

## Directory Structure

- `__init__.py`: Module entry point and exports.
- `manager.py`: Core `FeatureManager` implementation.
- `strategies.py`: Flag evaluation strategies (Static, Percentage, Targeting).
- `providers.py`: Connectors for external flag management services.

## Flag Evaluation Flow

1. **Request**: `manager.is_enabled(flag_key, context)`.
2. **Lookup**: Retrieve flag definition from the configured provider/cache.
3. **Evaluate**: Pass context and definition to the sequence of `Strategy` objects.
4. **Resolution**: Return the first definitive True/False, or the default value.

## Testing Strategy

- Unit tests for each evaluation strategy.
- Mocking of external flag providers.
- Verification of default value behavior when flags are missing.
