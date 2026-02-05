# validation

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

Unified input validation framework for Codomyrmex with support for JSON Schema, Pydantic models, and custom validators. Provides a `Validator` class that validates data against schemas, a `ValidationManager` for managing multiple validators, contextual validation with issue tracking, type-safe parsing, and a comprehensive exception hierarchy for granular error reporting. Includes submodules for reusable validation rules, input sanitizers, and schema definitions.

## Key Exports

### Core Classes
- **`Validator`** -- Main validation engine that validates data against a schema using a configurable `validator_type` (json_schema, pydantic, custom)
- **`ValidationManager`** -- Manages collections of validators and coordinates multi-schema validation workflows
- **`ValidationResult`** -- Result object containing `is_valid` boolean, list of errors, and validation metadata
- **`ValidationWarning`** -- Non-fatal validation warning with severity and location information
- **`ContextualValidator`** -- Context-aware validator that accumulates `ValidationIssue` objects for complex nested structures
- **`ValidationIssue`** -- Describes a specific validation problem with path, message, and severity
- **`TypeSafeParser`** -- Parser that coerces and validates data into expected types with detailed error reporting
- **`ValidationSummary`** -- Aggregated summary of validation results across multiple validation runs

### Convenience Functions
- **`validate()`** -- Validate data against a schema in one call, returns a `ValidationResult`
- **`is_valid()`** -- Returns True/False for whether data passes schema validation
- **`get_errors()`** -- Returns the list of validation errors for given data and schema

### Submodules
- **`rules`** -- Reusable validation rule definitions (string patterns, numeric ranges, custom predicates)
- **`sanitizers`** -- Input sanitization utilities (HTML stripping, whitespace normalization, encoding fixes)
- **`schemas`** -- Predefined JSON Schema definitions for common data structures

### Exceptions
- **`ValidationError`** -- Base validation error
- **`SchemaError`** -- Invalid or malformed schema definition
- **`ConstraintViolationError`** -- Data violates a defined constraint
- **`TypeValidationError`** -- Data type does not match expected type
- **`RequiredFieldError`** -- Required field is missing from input
- **`RangeValidationError`** -- Numeric value outside allowed range
- **`FormatValidationError`** -- String does not match expected format (email, URL, etc.)
- **`LengthValidationError`** -- String or collection length outside allowed bounds
- **`CustomValidationError`** -- Error from a custom validation rule

## Directory Contents

- `validator.py` -- Core Validator class, ValidationResult, and ValidationWarning
- `validation_manager.py` -- ValidationManager for multi-schema coordination
- `contextual.py` -- ContextualValidator and ValidationIssue for nested structure validation
- `parser.py` -- TypeSafeParser for type coercion with validation
- `summary.py` -- ValidationSummary for aggregating results
- `examples_validator.py` -- Validation of code examples and documentation samples
- `exceptions.py` -- Full exception hierarchy for validation errors
- `rules/` -- Reusable validation rule definitions
- `sanitizers/` -- Input sanitization utilities
- `schemas/` -- Predefined JSON Schema definitions

## Navigation

- **Full Documentation**: [docs/modules/validation/](../../../docs/modules/validation/)
- **Parent Directory**: [codomyrmex](../README.md)
- **Project Root**: ../../../README.md
