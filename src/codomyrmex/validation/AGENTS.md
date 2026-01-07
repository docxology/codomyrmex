# Codomyrmex Agents — src/codomyrmex/validation

## Signposting
- **Parent**: [codomyrmex](../AGENTS.md)
- **Self**: [Agents](AGENTS.md)
- **Children**:
    - None
- **Key Artifacts**:
    - [Functional Spec](SPEC.md)
    - [Human Readme](README.md)

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: January 2026

## Purpose
Unified input validation framework with support for JSON Schema, Pydantic models, and custom validators. Consolidates validation logic across modules with structured error reporting and nested validation support.

## Active Components
- `README.md` – Project file
- `SPEC.md` – Project file
- `__init__.py` – Module exports and public API
- `validation_manager.py` – Validation manager for registering and managing validators
- `validator.py` – Base validator interface and implementations
- `examples_validator.py` – Examples validator for validation testing

## Key Classes and Functions

### Validator (`validator.py`)
- `Validator(validator_type: str = "json_schema")` – Initialize validator with specified type (json_schema, pydantic, custom)
- `validate(data: Any, schema: Any) -> ValidationResult` – Validate data against a schema, returns ValidationResult
- `_validate_json_schema(data: Any, schema: dict) -> ValidationResult` – Internal JSON Schema validation
- `_validate_pydantic(data: Any, schema: Any) -> ValidationResult` – Internal Pydantic model validation
- `_validate_custom(data: Any, schema: Callable) -> ValidationResult` – Internal custom validator

### ValidationResult (`validator.py`)
- `ValidationResult` (dataclass) – Result of validation operation:
  - `is_valid: bool` – Whether validation passed
  - `errors: list[ValidationError]` – List of validation errors
  - `warnings: list[ValidationWarning]` – List of validation warnings
  - `__bool__() -> bool` – Boolean conversion (returns is_valid)

### ValidationError (`validator.py`, `__init__.py`)
- `ValidationError(message: str, field: Optional[str] = None, code: Optional[str] = None, path: Optional[list[str]] = None)` – Raised when validation fails
  - `field: Optional[str]` – Field name where error occurred
  - `code: Optional[str]` – Error code
  - `path: Optional[list[str]]` – Path to field in nested structure

### ValidationWarning (`validator.py`)
- `ValidationWarning` (dataclass) – Validation warning information:
  - `message: str` – Warning message
  - `field: Optional[str]` – Field name
  - `code: Optional[str]` – Warning code

### ValidationManager (`validation_manager.py`)
- `ValidationManager()` – Manager for validation operations and custom validators
- `register_validator(name: str, validator: Callable) -> None` – Register a custom validator function
- `get_validator(name: str) -> Optional[Callable]` – Get a registered validator by name
- `validate(data: Any, schema: Any, validator_type: str = "json_schema") -> ValidationResult` – Validate data using registered or default validator

### Module Functions (`__init__.py`)
- `validate(data: Any, schema: Any, validator_type: str = "json_schema") -> ValidationResult` – Validate data against a schema
- `is_valid(data: Any, schema: Any, validator_type: str = "json_schema") -> bool` – Check if data is valid (returns boolean)
- `get_errors(data: Any, schema: Any, validator_type: str = "json_schema") -> list[ValidationError]` – Get validation errors for data

## Operating Contracts
- Maintain alignment between code, documentation, and configured workflows.
- Ensure Model Context Protocol interfaces remain available for sibling agents.
- Record outcomes in shared telemetry and update TODO queues when necessary.

## Navigation Links
- **Human Documentation**: [README.md](README.md)
- **Functional Specification**: [SPEC.md](SPEC.md)
- **📁 Parent Directory**: [codomyrmex](../README.md) - Parent directory documentation
- **🏠 Project Root**: [README](../../../README.md) - Main project documentation