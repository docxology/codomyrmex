"""Regression tests for the legacy MCP JSON-schema validator."""

from codomyrmex.model_context_protocol.validators import SchemaValidator


def test_schema_validator_enforces_enum_and_numeric_bounds() -> None:
    validator = SchemaValidator(
        {
            "type": "integer",
            "enum": [1, 2, 3],
            "minimum": 1,
            "maximum": 3,
        }
    )

    assert validator.validate(2).valid
    assert not validator.validate(4).valid
    assert not validator.validate("2").valid


def test_schema_validator_enforces_any_of_and_unknown_properties() -> None:
    union = SchemaValidator(
        {
            "anyOf": [
                {"type": "string", "pattern": "^[a-z]+$"},
                {"type": "integer", "minimum": 1},
            ]
        }
    )
    strict_object = SchemaValidator(
        {
            "type": "object",
            "properties": {"name": {"type": "string"}},
            "additionalProperties": False,
        }
    )

    assert union.validate("valid").valid
    assert union.validate(2).valid
    assert not union.validate("123").valid
    assert strict_object.validate({"name": "ok"}).valid
    assert not strict_object.validate({"name": "ok", "extra": True}).valid
