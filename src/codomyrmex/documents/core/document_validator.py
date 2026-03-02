"""Document validation operations."""

from __future__ import annotations

from codomyrmex.logging_monitoring.core.logger_config import get_logger

from ..models.document import Document

logger = get_logger(__name__)


class ValidationResult:
    """Result of document validation."""

    def __init__(self, is_valid: bool, errors: list[str] = None, warnings: list[str] = None):

        self.is_valid = is_valid
        self.errors = errors or []
        self.warnings = warnings or []

    def __bool__(self) -> bool:
        """bool ."""

        return self.is_valid


class DocumentValidator:
    """Validator for document content and structure."""

    def validate(
        self,
        document: Document,
        schema: dict | None = None,
    ) -> ValidationResult:
        """
        Validate a document against a schema or format rules.

        Args:
            document: Document to validate
            schema: Optional JSON schema for validation

        Returns:
            ValidationResult with validation status and any errors/warnings
        """
        errors = []
        warnings = []

        # Basic validation
        if document.content is None:
            errors.append("Document content is None")

        if document.format is None:
            errors.append("Document format is not set")

        # Format-specific validation
        if document.format.value == "json":
            errors.extend(self._validate_json(document))
        elif document.format.value == "yaml":
            errors.extend(self._validate_yaml(document))

        # Schema validation if provided
        if schema:
            schema_errors = self._validate_against_schema(document, schema)
            errors.extend(schema_errors)

        is_valid = len(errors) == 0

        return ValidationResult(is_valid, errors, warnings)

    def _validate_json(self, document: Document) -> list[str]:
        """Validate JSON document."""
        errors = []
        try:
            if isinstance(document.content, str):
                import json
                json.loads(document.content)
            elif isinstance(document.content, dict):
                # Already parsed, validate structure
                pass
            else:
                errors.append("JSON content must be string or dict")
        except json.JSONDecodeError as e:
            errors.append(f"Invalid JSON: {str(e)}")
        return errors

    def _validate_yaml(self, document: Document) -> list[str]:
        """Validate YAML document."""
        errors = []
        try:
            if isinstance(document.content, str):
                import yaml
                yaml.safe_load(document.content)
            elif isinstance(document.content, dict):
                # Already parsed
                pass
            else:
                errors.append("YAML content must be string or dict")
        except yaml.YAMLError as e:
            errors.append(f"Invalid YAML: {str(e)}")
        return errors

    def _validate_against_schema(self, document: Document, schema: dict) -> list[str]:
        """Validate document against JSON schema."""
        errors = []
        try:
            import jsonschema

            # Get content as dict
            if isinstance(document.content, dict):
                content_dict = document.content
            elif isinstance(document.content, str):
                if document.format.value == "json":
                    import json
                    content_dict = json.loads(document.content)
                elif document.format.value == "yaml":
                    import yaml
                    content_dict = yaml.safe_load(document.content)
                else:
                    return errors  # Schema validation only for structured formats
            else:
                return errors

            jsonschema.validate(instance=content_dict, schema=schema)

        except jsonschema.ValidationError as e:
            errors.append(f"Schema validation error: {str(e)}")
        except Exception as e:
            errors.append(f"Schema validation failed: {str(e)}")

        return errors


def validate_document(
    document: Document,
    schema: dict | None = None,
) -> ValidationResult:
    """
    Validate a document.

    Convenience function that creates a DocumentValidator and validates the document.

    Args:
        document: Document to validate
        schema: Optional JSON schema for validation

    Returns:
        ValidationResult
    """
    validator = DocumentValidator()
    return validator.validate(document, schema)

