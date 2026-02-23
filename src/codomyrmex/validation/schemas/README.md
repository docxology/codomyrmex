# schemas

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

JSON Schema-style and custom validation schemas for the validation module. Provides a composable schema definition system with type checking, length/value range constraints, regex pattern matching, enum validation, required field enforcement, nested object and array validation, and factory methods for building schemas fluently. Includes pre-built patterns and schema constructors for common formats like email addresses, URLs, and UUIDs.

## Key Exports

- **`SchemaType`** -- Enum of supported data types: STRING, INTEGER, NUMBER, BOOLEAN, ARRAY, OBJECT, NULL, ANY
- **`ValidationError`** -- Dataclass representing a single validation error with path, message, offending value, and constraint name
- **`ValidationResult`** -- Dataclass aggregating validation outcomes with valid flag, error list, merge support, and error_messages property
- **`FieldSchema`** -- Dataclass defining a field's schema: type, required, nullable, default, description, constraints list, items schema (for arrays), and properties map (for objects); includes a recursive validate() method
- **`Constraint`** -- Abstract base class for validation constraints with a validate() method returning Optional[ValidationError]
- **`TypeConstraint`** -- Validates that a value matches an expected SchemaType using a Python type mapping
- **`MinLengthConstraint`** -- Validates minimum length for strings, arrays, or any object supporting len()
- **`MaxLengthConstraint`** -- Validates maximum length for strings, arrays, or any object supporting len()
- **`MinValueConstraint`** -- Validates minimum numeric value with optional exclusive mode
- **`MaxValueConstraint`** -- Validates maximum numeric value with optional exclusive mode
- **`PatternConstraint`** -- Validates string values against a compiled regular expression pattern
- **`EnumConstraint`** -- Validates that a value is within a specified set of allowed values
- **`RequiredConstraint`** -- Validates that required fields are present in a dictionary
- **`Schema`** -- Main schema class with fluent factory methods: `Schema.string()`, `Schema.integer()`, `Schema.number()`, `Schema.boolean()`, `Schema.array()`, `Schema.object()`, `Schema.any()`; each returns a configured Schema with appropriate constraints
- **`validate()`** -- Top-level function to validate data against a Schema, returning a ValidationResult
- **`is_valid()`** -- Top-level function for a quick boolean validity check
- **`email_schema()`** -- Factory returning a Schema pre-configured with an email address regex pattern
- **`url_schema()`** -- Factory returning a Schema pre-configured with an HTTP/HTTPS URL regex pattern
- **`uuid_schema()`** -- Factory returning a Schema pre-configured with a UUID v4 regex pattern
- **`EMAIL_PATTERN`** -- Regex pattern constant for validating email addresses
- **`URL_PATTERN`** -- Regex pattern constant for validating HTTP/HTTPS URLs
- **`UUID_PATTERN`** -- Regex pattern constant for validating UUIDs

## Directory Contents

- `__init__.py` - All schema classes, constraint implementations, factory methods, and common patterns
- `README.md` - This file
- `SPEC.md` - Module specification
- `AGENTS.md` - Agent integration notes
- `PAI.md` - PAI algorithm context
- `py.typed` - PEP 561 typing marker

## Navigation

- **Parent Module**: [validation](../README.md)
- **Project Root**: [../../../../README.md](../../../../README.md)
