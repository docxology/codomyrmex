"""
MCP Tool Argument Validation

Validates tool arguments against their JSON Schema ``inputSchema`` before
dispatch, preventing invalid data from reaching handlers.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any, Callable
import inspect

logger = logging.getLogger(__name__)
from inspect import signature as _mutmut_signature
from typing import Annotated
from typing import Callable
from typing import ClassVar


MutantDict = Annotated[dict[str, Callable], "Mutant"]


def _mutmut_trampoline(orig, mutants, call_args, call_kwargs, self_arg = None):
    """Forward call to original or mutated function, depending on the environment"""
    import os
    mutant_under_test = os.environ['MUTANT_UNDER_TEST']
    if mutant_under_test == 'fail':
        from mutmut.__main__ import MutmutProgrammaticFailException
        raise MutmutProgrammaticFailException('Failed programmatically')      
    elif mutant_under_test == 'stats':
        from mutmut.__main__ import record_trampoline_hit
        record_trampoline_hit(orig.__module__ + '.' + orig.__name__)
        result = orig(*call_args, **call_kwargs)
        return result
    prefix = orig.__module__ + '.' + orig.__name__ + '__mutmut_'
    if not mutant_under_test.startswith(prefix):
        result = orig(*call_args, **call_kwargs)
        return result
    mutant_name = mutant_under_test.rpartition('.')[-1]
    if self_arg is not None:
        # call to a class method where self is not bound
        result = mutants[mutant_name](self_arg, *call_args, **call_kwargs)
    else:
        result = mutants[mutant_name](*call_args, **call_kwargs)
    return result


# ---------------------------------------------------------------------------
# Result container
# ---------------------------------------------------------------------------

@dataclass(slots=True)
class ValidationResult:
    """Outcome of validating tool arguments against a schema."""

    valid: bool
    errors: list[str] = field(default_factory=list)
    coerced_args: dict[str, Any] = field(default_factory=dict)


# ---------------------------------------------------------------------------
# Core validation function
# ---------------------------------------------------------------------------

def x_validate_tool_arguments__mutmut_orig(
    tool_name: str,
    arguments: dict[str, Any] | None,
    schema: dict[str, Any],
    *,
    coerce: bool = True,
) -> ValidationResult:
    """Validate *arguments* against the tool's ``inputSchema``.

    Parameters
    ----------
    tool_name:
        Used only for logging / error messages.
    arguments:
        The raw arguments dict supplied by the caller.
    schema:
        The full tool schema dict.  The ``inputSchema`` key is extracted
        automatically; if *schema* itself looks like a JSON Schema object
        (has ``"type"`` or ``"properties"``) it is used directly.
    coerce:
        When ``True``, attempt lightweight type coercion for common
        mismatches (``str → int``, ``str → bool``, ``str → float``).

    Returns
    -------
    ValidationResult
        ``valid=True`` with (optionally coerced) ``coerced_args`` on success,
        or ``valid=False`` with human-readable ``errors`` on failure.
    """
    # Normalise None → empty dict
    if arguments is None:
        arguments = {}

    # Extract the actual JSON Schema object
    input_schema = _extract_input_schema(schema)
    if input_schema is None:
        # No schema to validate against — pass through
        return ValidationResult(valid=True, coerced_args=dict(arguments))

    working_args = dict(arguments)

    if coerce:
        working_args = _coerce_types(working_args, input_schema)

    errors = _validate_against_schema(working_args, input_schema, tool_name)

    if errors:
        return ValidationResult(valid=False, errors=errors)

    return ValidationResult(valid=True, coerced_args=working_args)


# ---------------------------------------------------------------------------
# Core validation function
# ---------------------------------------------------------------------------

def x_validate_tool_arguments__mutmut_1(
    tool_name: str,
    arguments: dict[str, Any] | None,
    schema: dict[str, Any],
    *,
    coerce: bool = False,
) -> ValidationResult:
    """Validate *arguments* against the tool's ``inputSchema``.

    Parameters
    ----------
    tool_name:
        Used only for logging / error messages.
    arguments:
        The raw arguments dict supplied by the caller.
    schema:
        The full tool schema dict.  The ``inputSchema`` key is extracted
        automatically; if *schema* itself looks like a JSON Schema object
        (has ``"type"`` or ``"properties"``) it is used directly.
    coerce:
        When ``True``, attempt lightweight type coercion for common
        mismatches (``str → int``, ``str → bool``, ``str → float``).

    Returns
    -------
    ValidationResult
        ``valid=True`` with (optionally coerced) ``coerced_args`` on success,
        or ``valid=False`` with human-readable ``errors`` on failure.
    """
    # Normalise None → empty dict
    if arguments is None:
        arguments = {}

    # Extract the actual JSON Schema object
    input_schema = _extract_input_schema(schema)
    if input_schema is None:
        # No schema to validate against — pass through
        return ValidationResult(valid=True, coerced_args=dict(arguments))

    working_args = dict(arguments)

    if coerce:
        working_args = _coerce_types(working_args, input_schema)

    errors = _validate_against_schema(working_args, input_schema, tool_name)

    if errors:
        return ValidationResult(valid=False, errors=errors)

    return ValidationResult(valid=True, coerced_args=working_args)


# ---------------------------------------------------------------------------
# Core validation function
# ---------------------------------------------------------------------------

def x_validate_tool_arguments__mutmut_2(
    tool_name: str,
    arguments: dict[str, Any] | None,
    schema: dict[str, Any],
    *,
    coerce: bool = True,
) -> ValidationResult:
    """Validate *arguments* against the tool's ``inputSchema``.

    Parameters
    ----------
    tool_name:
        Used only for logging / error messages.
    arguments:
        The raw arguments dict supplied by the caller.
    schema:
        The full tool schema dict.  The ``inputSchema`` key is extracted
        automatically; if *schema* itself looks like a JSON Schema object
        (has ``"type"`` or ``"properties"``) it is used directly.
    coerce:
        When ``True``, attempt lightweight type coercion for common
        mismatches (``str → int``, ``str → bool``, ``str → float``).

    Returns
    -------
    ValidationResult
        ``valid=True`` with (optionally coerced) ``coerced_args`` on success,
        or ``valid=False`` with human-readable ``errors`` on failure.
    """
    # Normalise None → empty dict
    if arguments is not None:
        arguments = {}

    # Extract the actual JSON Schema object
    input_schema = _extract_input_schema(schema)
    if input_schema is None:
        # No schema to validate against — pass through
        return ValidationResult(valid=True, coerced_args=dict(arguments))

    working_args = dict(arguments)

    if coerce:
        working_args = _coerce_types(working_args, input_schema)

    errors = _validate_against_schema(working_args, input_schema, tool_name)

    if errors:
        return ValidationResult(valid=False, errors=errors)

    return ValidationResult(valid=True, coerced_args=working_args)


# ---------------------------------------------------------------------------
# Core validation function
# ---------------------------------------------------------------------------

def x_validate_tool_arguments__mutmut_3(
    tool_name: str,
    arguments: dict[str, Any] | None,
    schema: dict[str, Any],
    *,
    coerce: bool = True,
) -> ValidationResult:
    """Validate *arguments* against the tool's ``inputSchema``.

    Parameters
    ----------
    tool_name:
        Used only for logging / error messages.
    arguments:
        The raw arguments dict supplied by the caller.
    schema:
        The full tool schema dict.  The ``inputSchema`` key is extracted
        automatically; if *schema* itself looks like a JSON Schema object
        (has ``"type"`` or ``"properties"``) it is used directly.
    coerce:
        When ``True``, attempt lightweight type coercion for common
        mismatches (``str → int``, ``str → bool``, ``str → float``).

    Returns
    -------
    ValidationResult
        ``valid=True`` with (optionally coerced) ``coerced_args`` on success,
        or ``valid=False`` with human-readable ``errors`` on failure.
    """
    # Normalise None → empty dict
    if arguments is None:
        arguments = None

    # Extract the actual JSON Schema object
    input_schema = _extract_input_schema(schema)
    if input_schema is None:
        # No schema to validate against — pass through
        return ValidationResult(valid=True, coerced_args=dict(arguments))

    working_args = dict(arguments)

    if coerce:
        working_args = _coerce_types(working_args, input_schema)

    errors = _validate_against_schema(working_args, input_schema, tool_name)

    if errors:
        return ValidationResult(valid=False, errors=errors)

    return ValidationResult(valid=True, coerced_args=working_args)


# ---------------------------------------------------------------------------
# Core validation function
# ---------------------------------------------------------------------------

def x_validate_tool_arguments__mutmut_4(
    tool_name: str,
    arguments: dict[str, Any] | None,
    schema: dict[str, Any],
    *,
    coerce: bool = True,
) -> ValidationResult:
    """Validate *arguments* against the tool's ``inputSchema``.

    Parameters
    ----------
    tool_name:
        Used only for logging / error messages.
    arguments:
        The raw arguments dict supplied by the caller.
    schema:
        The full tool schema dict.  The ``inputSchema`` key is extracted
        automatically; if *schema* itself looks like a JSON Schema object
        (has ``"type"`` or ``"properties"``) it is used directly.
    coerce:
        When ``True``, attempt lightweight type coercion for common
        mismatches (``str → int``, ``str → bool``, ``str → float``).

    Returns
    -------
    ValidationResult
        ``valid=True`` with (optionally coerced) ``coerced_args`` on success,
        or ``valid=False`` with human-readable ``errors`` on failure.
    """
    # Normalise None → empty dict
    if arguments is None:
        arguments = {}

    # Extract the actual JSON Schema object
    input_schema = None
    if input_schema is None:
        # No schema to validate against — pass through
        return ValidationResult(valid=True, coerced_args=dict(arguments))

    working_args = dict(arguments)

    if coerce:
        working_args = _coerce_types(working_args, input_schema)

    errors = _validate_against_schema(working_args, input_schema, tool_name)

    if errors:
        return ValidationResult(valid=False, errors=errors)

    return ValidationResult(valid=True, coerced_args=working_args)


# ---------------------------------------------------------------------------
# Core validation function
# ---------------------------------------------------------------------------

def x_validate_tool_arguments__mutmut_5(
    tool_name: str,
    arguments: dict[str, Any] | None,
    schema: dict[str, Any],
    *,
    coerce: bool = True,
) -> ValidationResult:
    """Validate *arguments* against the tool's ``inputSchema``.

    Parameters
    ----------
    tool_name:
        Used only for logging / error messages.
    arguments:
        The raw arguments dict supplied by the caller.
    schema:
        The full tool schema dict.  The ``inputSchema`` key is extracted
        automatically; if *schema* itself looks like a JSON Schema object
        (has ``"type"`` or ``"properties"``) it is used directly.
    coerce:
        When ``True``, attempt lightweight type coercion for common
        mismatches (``str → int``, ``str → bool``, ``str → float``).

    Returns
    -------
    ValidationResult
        ``valid=True`` with (optionally coerced) ``coerced_args`` on success,
        or ``valid=False`` with human-readable ``errors`` on failure.
    """
    # Normalise None → empty dict
    if arguments is None:
        arguments = {}

    # Extract the actual JSON Schema object
    input_schema = _extract_input_schema(None)
    if input_schema is None:
        # No schema to validate against — pass through
        return ValidationResult(valid=True, coerced_args=dict(arguments))

    working_args = dict(arguments)

    if coerce:
        working_args = _coerce_types(working_args, input_schema)

    errors = _validate_against_schema(working_args, input_schema, tool_name)

    if errors:
        return ValidationResult(valid=False, errors=errors)

    return ValidationResult(valid=True, coerced_args=working_args)


# ---------------------------------------------------------------------------
# Core validation function
# ---------------------------------------------------------------------------

def x_validate_tool_arguments__mutmut_6(
    tool_name: str,
    arguments: dict[str, Any] | None,
    schema: dict[str, Any],
    *,
    coerce: bool = True,
) -> ValidationResult:
    """Validate *arguments* against the tool's ``inputSchema``.

    Parameters
    ----------
    tool_name:
        Used only for logging / error messages.
    arguments:
        The raw arguments dict supplied by the caller.
    schema:
        The full tool schema dict.  The ``inputSchema`` key is extracted
        automatically; if *schema* itself looks like a JSON Schema object
        (has ``"type"`` or ``"properties"``) it is used directly.
    coerce:
        When ``True``, attempt lightweight type coercion for common
        mismatches (``str → int``, ``str → bool``, ``str → float``).

    Returns
    -------
    ValidationResult
        ``valid=True`` with (optionally coerced) ``coerced_args`` on success,
        or ``valid=False`` with human-readable ``errors`` on failure.
    """
    # Normalise None → empty dict
    if arguments is None:
        arguments = {}

    # Extract the actual JSON Schema object
    input_schema = _extract_input_schema(schema)
    if input_schema is not None:
        # No schema to validate against — pass through
        return ValidationResult(valid=True, coerced_args=dict(arguments))

    working_args = dict(arguments)

    if coerce:
        working_args = _coerce_types(working_args, input_schema)

    errors = _validate_against_schema(working_args, input_schema, tool_name)

    if errors:
        return ValidationResult(valid=False, errors=errors)

    return ValidationResult(valid=True, coerced_args=working_args)


# ---------------------------------------------------------------------------
# Core validation function
# ---------------------------------------------------------------------------

def x_validate_tool_arguments__mutmut_7(
    tool_name: str,
    arguments: dict[str, Any] | None,
    schema: dict[str, Any],
    *,
    coerce: bool = True,
) -> ValidationResult:
    """Validate *arguments* against the tool's ``inputSchema``.

    Parameters
    ----------
    tool_name:
        Used only for logging / error messages.
    arguments:
        The raw arguments dict supplied by the caller.
    schema:
        The full tool schema dict.  The ``inputSchema`` key is extracted
        automatically; if *schema* itself looks like a JSON Schema object
        (has ``"type"`` or ``"properties"``) it is used directly.
    coerce:
        When ``True``, attempt lightweight type coercion for common
        mismatches (``str → int``, ``str → bool``, ``str → float``).

    Returns
    -------
    ValidationResult
        ``valid=True`` with (optionally coerced) ``coerced_args`` on success,
        or ``valid=False`` with human-readable ``errors`` on failure.
    """
    # Normalise None → empty dict
    if arguments is None:
        arguments = {}

    # Extract the actual JSON Schema object
    input_schema = _extract_input_schema(schema)
    if input_schema is None:
        # No schema to validate against — pass through
        return ValidationResult(valid=None, coerced_args=dict(arguments))

    working_args = dict(arguments)

    if coerce:
        working_args = _coerce_types(working_args, input_schema)

    errors = _validate_against_schema(working_args, input_schema, tool_name)

    if errors:
        return ValidationResult(valid=False, errors=errors)

    return ValidationResult(valid=True, coerced_args=working_args)


# ---------------------------------------------------------------------------
# Core validation function
# ---------------------------------------------------------------------------

def x_validate_tool_arguments__mutmut_8(
    tool_name: str,
    arguments: dict[str, Any] | None,
    schema: dict[str, Any],
    *,
    coerce: bool = True,
) -> ValidationResult:
    """Validate *arguments* against the tool's ``inputSchema``.

    Parameters
    ----------
    tool_name:
        Used only for logging / error messages.
    arguments:
        The raw arguments dict supplied by the caller.
    schema:
        The full tool schema dict.  The ``inputSchema`` key is extracted
        automatically; if *schema* itself looks like a JSON Schema object
        (has ``"type"`` or ``"properties"``) it is used directly.
    coerce:
        When ``True``, attempt lightweight type coercion for common
        mismatches (``str → int``, ``str → bool``, ``str → float``).

    Returns
    -------
    ValidationResult
        ``valid=True`` with (optionally coerced) ``coerced_args`` on success,
        or ``valid=False`` with human-readable ``errors`` on failure.
    """
    # Normalise None → empty dict
    if arguments is None:
        arguments = {}

    # Extract the actual JSON Schema object
    input_schema = _extract_input_schema(schema)
    if input_schema is None:
        # No schema to validate against — pass through
        return ValidationResult(valid=True, coerced_args=None)

    working_args = dict(arguments)

    if coerce:
        working_args = _coerce_types(working_args, input_schema)

    errors = _validate_against_schema(working_args, input_schema, tool_name)

    if errors:
        return ValidationResult(valid=False, errors=errors)

    return ValidationResult(valid=True, coerced_args=working_args)


# ---------------------------------------------------------------------------
# Core validation function
# ---------------------------------------------------------------------------

def x_validate_tool_arguments__mutmut_9(
    tool_name: str,
    arguments: dict[str, Any] | None,
    schema: dict[str, Any],
    *,
    coerce: bool = True,
) -> ValidationResult:
    """Validate *arguments* against the tool's ``inputSchema``.

    Parameters
    ----------
    tool_name:
        Used only for logging / error messages.
    arguments:
        The raw arguments dict supplied by the caller.
    schema:
        The full tool schema dict.  The ``inputSchema`` key is extracted
        automatically; if *schema* itself looks like a JSON Schema object
        (has ``"type"`` or ``"properties"``) it is used directly.
    coerce:
        When ``True``, attempt lightweight type coercion for common
        mismatches (``str → int``, ``str → bool``, ``str → float``).

    Returns
    -------
    ValidationResult
        ``valid=True`` with (optionally coerced) ``coerced_args`` on success,
        or ``valid=False`` with human-readable ``errors`` on failure.
    """
    # Normalise None → empty dict
    if arguments is None:
        arguments = {}

    # Extract the actual JSON Schema object
    input_schema = _extract_input_schema(schema)
    if input_schema is None:
        # No schema to validate against — pass through
        return ValidationResult(coerced_args=dict(arguments))

    working_args = dict(arguments)

    if coerce:
        working_args = _coerce_types(working_args, input_schema)

    errors = _validate_against_schema(working_args, input_schema, tool_name)

    if errors:
        return ValidationResult(valid=False, errors=errors)

    return ValidationResult(valid=True, coerced_args=working_args)


# ---------------------------------------------------------------------------
# Core validation function
# ---------------------------------------------------------------------------

def x_validate_tool_arguments__mutmut_10(
    tool_name: str,
    arguments: dict[str, Any] | None,
    schema: dict[str, Any],
    *,
    coerce: bool = True,
) -> ValidationResult:
    """Validate *arguments* against the tool's ``inputSchema``.

    Parameters
    ----------
    tool_name:
        Used only for logging / error messages.
    arguments:
        The raw arguments dict supplied by the caller.
    schema:
        The full tool schema dict.  The ``inputSchema`` key is extracted
        automatically; if *schema* itself looks like a JSON Schema object
        (has ``"type"`` or ``"properties"``) it is used directly.
    coerce:
        When ``True``, attempt lightweight type coercion for common
        mismatches (``str → int``, ``str → bool``, ``str → float``).

    Returns
    -------
    ValidationResult
        ``valid=True`` with (optionally coerced) ``coerced_args`` on success,
        or ``valid=False`` with human-readable ``errors`` on failure.
    """
    # Normalise None → empty dict
    if arguments is None:
        arguments = {}

    # Extract the actual JSON Schema object
    input_schema = _extract_input_schema(schema)
    if input_schema is None:
        # No schema to validate against — pass through
        return ValidationResult(valid=True, )

    working_args = dict(arguments)

    if coerce:
        working_args = _coerce_types(working_args, input_schema)

    errors = _validate_against_schema(working_args, input_schema, tool_name)

    if errors:
        return ValidationResult(valid=False, errors=errors)

    return ValidationResult(valid=True, coerced_args=working_args)


# ---------------------------------------------------------------------------
# Core validation function
# ---------------------------------------------------------------------------

def x_validate_tool_arguments__mutmut_11(
    tool_name: str,
    arguments: dict[str, Any] | None,
    schema: dict[str, Any],
    *,
    coerce: bool = True,
) -> ValidationResult:
    """Validate *arguments* against the tool's ``inputSchema``.

    Parameters
    ----------
    tool_name:
        Used only for logging / error messages.
    arguments:
        The raw arguments dict supplied by the caller.
    schema:
        The full tool schema dict.  The ``inputSchema`` key is extracted
        automatically; if *schema* itself looks like a JSON Schema object
        (has ``"type"`` or ``"properties"``) it is used directly.
    coerce:
        When ``True``, attempt lightweight type coercion for common
        mismatches (``str → int``, ``str → bool``, ``str → float``).

    Returns
    -------
    ValidationResult
        ``valid=True`` with (optionally coerced) ``coerced_args`` on success,
        or ``valid=False`` with human-readable ``errors`` on failure.
    """
    # Normalise None → empty dict
    if arguments is None:
        arguments = {}

    # Extract the actual JSON Schema object
    input_schema = _extract_input_schema(schema)
    if input_schema is None:
        # No schema to validate against — pass through
        return ValidationResult(valid=False, coerced_args=dict(arguments))

    working_args = dict(arguments)

    if coerce:
        working_args = _coerce_types(working_args, input_schema)

    errors = _validate_against_schema(working_args, input_schema, tool_name)

    if errors:
        return ValidationResult(valid=False, errors=errors)

    return ValidationResult(valid=True, coerced_args=working_args)


# ---------------------------------------------------------------------------
# Core validation function
# ---------------------------------------------------------------------------

def x_validate_tool_arguments__mutmut_12(
    tool_name: str,
    arguments: dict[str, Any] | None,
    schema: dict[str, Any],
    *,
    coerce: bool = True,
) -> ValidationResult:
    """Validate *arguments* against the tool's ``inputSchema``.

    Parameters
    ----------
    tool_name:
        Used only for logging / error messages.
    arguments:
        The raw arguments dict supplied by the caller.
    schema:
        The full tool schema dict.  The ``inputSchema`` key is extracted
        automatically; if *schema* itself looks like a JSON Schema object
        (has ``"type"`` or ``"properties"``) it is used directly.
    coerce:
        When ``True``, attempt lightweight type coercion for common
        mismatches (``str → int``, ``str → bool``, ``str → float``).

    Returns
    -------
    ValidationResult
        ``valid=True`` with (optionally coerced) ``coerced_args`` on success,
        or ``valid=False`` with human-readable ``errors`` on failure.
    """
    # Normalise None → empty dict
    if arguments is None:
        arguments = {}

    # Extract the actual JSON Schema object
    input_schema = _extract_input_schema(schema)
    if input_schema is None:
        # No schema to validate against — pass through
        return ValidationResult(valid=True, coerced_args=dict(None))

    working_args = dict(arguments)

    if coerce:
        working_args = _coerce_types(working_args, input_schema)

    errors = _validate_against_schema(working_args, input_schema, tool_name)

    if errors:
        return ValidationResult(valid=False, errors=errors)

    return ValidationResult(valid=True, coerced_args=working_args)


# ---------------------------------------------------------------------------
# Core validation function
# ---------------------------------------------------------------------------

def x_validate_tool_arguments__mutmut_13(
    tool_name: str,
    arguments: dict[str, Any] | None,
    schema: dict[str, Any],
    *,
    coerce: bool = True,
) -> ValidationResult:
    """Validate *arguments* against the tool's ``inputSchema``.

    Parameters
    ----------
    tool_name:
        Used only for logging / error messages.
    arguments:
        The raw arguments dict supplied by the caller.
    schema:
        The full tool schema dict.  The ``inputSchema`` key is extracted
        automatically; if *schema* itself looks like a JSON Schema object
        (has ``"type"`` or ``"properties"``) it is used directly.
    coerce:
        When ``True``, attempt lightweight type coercion for common
        mismatches (``str → int``, ``str → bool``, ``str → float``).

    Returns
    -------
    ValidationResult
        ``valid=True`` with (optionally coerced) ``coerced_args`` on success,
        or ``valid=False`` with human-readable ``errors`` on failure.
    """
    # Normalise None → empty dict
    if arguments is None:
        arguments = {}

    # Extract the actual JSON Schema object
    input_schema = _extract_input_schema(schema)
    if input_schema is None:
        # No schema to validate against — pass through
        return ValidationResult(valid=True, coerced_args=dict(arguments))

    working_args = None

    if coerce:
        working_args = _coerce_types(working_args, input_schema)

    errors = _validate_against_schema(working_args, input_schema, tool_name)

    if errors:
        return ValidationResult(valid=False, errors=errors)

    return ValidationResult(valid=True, coerced_args=working_args)


# ---------------------------------------------------------------------------
# Core validation function
# ---------------------------------------------------------------------------

def x_validate_tool_arguments__mutmut_14(
    tool_name: str,
    arguments: dict[str, Any] | None,
    schema: dict[str, Any],
    *,
    coerce: bool = True,
) -> ValidationResult:
    """Validate *arguments* against the tool's ``inputSchema``.

    Parameters
    ----------
    tool_name:
        Used only for logging / error messages.
    arguments:
        The raw arguments dict supplied by the caller.
    schema:
        The full tool schema dict.  The ``inputSchema`` key is extracted
        automatically; if *schema* itself looks like a JSON Schema object
        (has ``"type"`` or ``"properties"``) it is used directly.
    coerce:
        When ``True``, attempt lightweight type coercion for common
        mismatches (``str → int``, ``str → bool``, ``str → float``).

    Returns
    -------
    ValidationResult
        ``valid=True`` with (optionally coerced) ``coerced_args`` on success,
        or ``valid=False`` with human-readable ``errors`` on failure.
    """
    # Normalise None → empty dict
    if arguments is None:
        arguments = {}

    # Extract the actual JSON Schema object
    input_schema = _extract_input_schema(schema)
    if input_schema is None:
        # No schema to validate against — pass through
        return ValidationResult(valid=True, coerced_args=dict(arguments))

    working_args = dict(None)

    if coerce:
        working_args = _coerce_types(working_args, input_schema)

    errors = _validate_against_schema(working_args, input_schema, tool_name)

    if errors:
        return ValidationResult(valid=False, errors=errors)

    return ValidationResult(valid=True, coerced_args=working_args)


# ---------------------------------------------------------------------------
# Core validation function
# ---------------------------------------------------------------------------

def x_validate_tool_arguments__mutmut_15(
    tool_name: str,
    arguments: dict[str, Any] | None,
    schema: dict[str, Any],
    *,
    coerce: bool = True,
) -> ValidationResult:
    """Validate *arguments* against the tool's ``inputSchema``.

    Parameters
    ----------
    tool_name:
        Used only for logging / error messages.
    arguments:
        The raw arguments dict supplied by the caller.
    schema:
        The full tool schema dict.  The ``inputSchema`` key is extracted
        automatically; if *schema* itself looks like a JSON Schema object
        (has ``"type"`` or ``"properties"``) it is used directly.
    coerce:
        When ``True``, attempt lightweight type coercion for common
        mismatches (``str → int``, ``str → bool``, ``str → float``).

    Returns
    -------
    ValidationResult
        ``valid=True`` with (optionally coerced) ``coerced_args`` on success,
        or ``valid=False`` with human-readable ``errors`` on failure.
    """
    # Normalise None → empty dict
    if arguments is None:
        arguments = {}

    # Extract the actual JSON Schema object
    input_schema = _extract_input_schema(schema)
    if input_schema is None:
        # No schema to validate against — pass through
        return ValidationResult(valid=True, coerced_args=dict(arguments))

    working_args = dict(arguments)

    if coerce:
        working_args = None

    errors = _validate_against_schema(working_args, input_schema, tool_name)

    if errors:
        return ValidationResult(valid=False, errors=errors)

    return ValidationResult(valid=True, coerced_args=working_args)


# ---------------------------------------------------------------------------
# Core validation function
# ---------------------------------------------------------------------------

def x_validate_tool_arguments__mutmut_16(
    tool_name: str,
    arguments: dict[str, Any] | None,
    schema: dict[str, Any],
    *,
    coerce: bool = True,
) -> ValidationResult:
    """Validate *arguments* against the tool's ``inputSchema``.

    Parameters
    ----------
    tool_name:
        Used only for logging / error messages.
    arguments:
        The raw arguments dict supplied by the caller.
    schema:
        The full tool schema dict.  The ``inputSchema`` key is extracted
        automatically; if *schema* itself looks like a JSON Schema object
        (has ``"type"`` or ``"properties"``) it is used directly.
    coerce:
        When ``True``, attempt lightweight type coercion for common
        mismatches (``str → int``, ``str → bool``, ``str → float``).

    Returns
    -------
    ValidationResult
        ``valid=True`` with (optionally coerced) ``coerced_args`` on success,
        or ``valid=False`` with human-readable ``errors`` on failure.
    """
    # Normalise None → empty dict
    if arguments is None:
        arguments = {}

    # Extract the actual JSON Schema object
    input_schema = _extract_input_schema(schema)
    if input_schema is None:
        # No schema to validate against — pass through
        return ValidationResult(valid=True, coerced_args=dict(arguments))

    working_args = dict(arguments)

    if coerce:
        working_args = _coerce_types(None, input_schema)

    errors = _validate_against_schema(working_args, input_schema, tool_name)

    if errors:
        return ValidationResult(valid=False, errors=errors)

    return ValidationResult(valid=True, coerced_args=working_args)


# ---------------------------------------------------------------------------
# Core validation function
# ---------------------------------------------------------------------------

def x_validate_tool_arguments__mutmut_17(
    tool_name: str,
    arguments: dict[str, Any] | None,
    schema: dict[str, Any],
    *,
    coerce: bool = True,
) -> ValidationResult:
    """Validate *arguments* against the tool's ``inputSchema``.

    Parameters
    ----------
    tool_name:
        Used only for logging / error messages.
    arguments:
        The raw arguments dict supplied by the caller.
    schema:
        The full tool schema dict.  The ``inputSchema`` key is extracted
        automatically; if *schema* itself looks like a JSON Schema object
        (has ``"type"`` or ``"properties"``) it is used directly.
    coerce:
        When ``True``, attempt lightweight type coercion for common
        mismatches (``str → int``, ``str → bool``, ``str → float``).

    Returns
    -------
    ValidationResult
        ``valid=True`` with (optionally coerced) ``coerced_args`` on success,
        or ``valid=False`` with human-readable ``errors`` on failure.
    """
    # Normalise None → empty dict
    if arguments is None:
        arguments = {}

    # Extract the actual JSON Schema object
    input_schema = _extract_input_schema(schema)
    if input_schema is None:
        # No schema to validate against — pass through
        return ValidationResult(valid=True, coerced_args=dict(arguments))

    working_args = dict(arguments)

    if coerce:
        working_args = _coerce_types(working_args, None)

    errors = _validate_against_schema(working_args, input_schema, tool_name)

    if errors:
        return ValidationResult(valid=False, errors=errors)

    return ValidationResult(valid=True, coerced_args=working_args)


# ---------------------------------------------------------------------------
# Core validation function
# ---------------------------------------------------------------------------

def x_validate_tool_arguments__mutmut_18(
    tool_name: str,
    arguments: dict[str, Any] | None,
    schema: dict[str, Any],
    *,
    coerce: bool = True,
) -> ValidationResult:
    """Validate *arguments* against the tool's ``inputSchema``.

    Parameters
    ----------
    tool_name:
        Used only for logging / error messages.
    arguments:
        The raw arguments dict supplied by the caller.
    schema:
        The full tool schema dict.  The ``inputSchema`` key is extracted
        automatically; if *schema* itself looks like a JSON Schema object
        (has ``"type"`` or ``"properties"``) it is used directly.
    coerce:
        When ``True``, attempt lightweight type coercion for common
        mismatches (``str → int``, ``str → bool``, ``str → float``).

    Returns
    -------
    ValidationResult
        ``valid=True`` with (optionally coerced) ``coerced_args`` on success,
        or ``valid=False`` with human-readable ``errors`` on failure.
    """
    # Normalise None → empty dict
    if arguments is None:
        arguments = {}

    # Extract the actual JSON Schema object
    input_schema = _extract_input_schema(schema)
    if input_schema is None:
        # No schema to validate against — pass through
        return ValidationResult(valid=True, coerced_args=dict(arguments))

    working_args = dict(arguments)

    if coerce:
        working_args = _coerce_types(input_schema)

    errors = _validate_against_schema(working_args, input_schema, tool_name)

    if errors:
        return ValidationResult(valid=False, errors=errors)

    return ValidationResult(valid=True, coerced_args=working_args)


# ---------------------------------------------------------------------------
# Core validation function
# ---------------------------------------------------------------------------

def x_validate_tool_arguments__mutmut_19(
    tool_name: str,
    arguments: dict[str, Any] | None,
    schema: dict[str, Any],
    *,
    coerce: bool = True,
) -> ValidationResult:
    """Validate *arguments* against the tool's ``inputSchema``.

    Parameters
    ----------
    tool_name:
        Used only for logging / error messages.
    arguments:
        The raw arguments dict supplied by the caller.
    schema:
        The full tool schema dict.  The ``inputSchema`` key is extracted
        automatically; if *schema* itself looks like a JSON Schema object
        (has ``"type"`` or ``"properties"``) it is used directly.
    coerce:
        When ``True``, attempt lightweight type coercion for common
        mismatches (``str → int``, ``str → bool``, ``str → float``).

    Returns
    -------
    ValidationResult
        ``valid=True`` with (optionally coerced) ``coerced_args`` on success,
        or ``valid=False`` with human-readable ``errors`` on failure.
    """
    # Normalise None → empty dict
    if arguments is None:
        arguments = {}

    # Extract the actual JSON Schema object
    input_schema = _extract_input_schema(schema)
    if input_schema is None:
        # No schema to validate against — pass through
        return ValidationResult(valid=True, coerced_args=dict(arguments))

    working_args = dict(arguments)

    if coerce:
        working_args = _coerce_types(working_args, )

    errors = _validate_against_schema(working_args, input_schema, tool_name)

    if errors:
        return ValidationResult(valid=False, errors=errors)

    return ValidationResult(valid=True, coerced_args=working_args)


# ---------------------------------------------------------------------------
# Core validation function
# ---------------------------------------------------------------------------

def x_validate_tool_arguments__mutmut_20(
    tool_name: str,
    arguments: dict[str, Any] | None,
    schema: dict[str, Any],
    *,
    coerce: bool = True,
) -> ValidationResult:
    """Validate *arguments* against the tool's ``inputSchema``.

    Parameters
    ----------
    tool_name:
        Used only for logging / error messages.
    arguments:
        The raw arguments dict supplied by the caller.
    schema:
        The full tool schema dict.  The ``inputSchema`` key is extracted
        automatically; if *schema* itself looks like a JSON Schema object
        (has ``"type"`` or ``"properties"``) it is used directly.
    coerce:
        When ``True``, attempt lightweight type coercion for common
        mismatches (``str → int``, ``str → bool``, ``str → float``).

    Returns
    -------
    ValidationResult
        ``valid=True`` with (optionally coerced) ``coerced_args`` on success,
        or ``valid=False`` with human-readable ``errors`` on failure.
    """
    # Normalise None → empty dict
    if arguments is None:
        arguments = {}

    # Extract the actual JSON Schema object
    input_schema = _extract_input_schema(schema)
    if input_schema is None:
        # No schema to validate against — pass through
        return ValidationResult(valid=True, coerced_args=dict(arguments))

    working_args = dict(arguments)

    if coerce:
        working_args = _coerce_types(working_args, input_schema)

    errors = None

    if errors:
        return ValidationResult(valid=False, errors=errors)

    return ValidationResult(valid=True, coerced_args=working_args)


# ---------------------------------------------------------------------------
# Core validation function
# ---------------------------------------------------------------------------

def x_validate_tool_arguments__mutmut_21(
    tool_name: str,
    arguments: dict[str, Any] | None,
    schema: dict[str, Any],
    *,
    coerce: bool = True,
) -> ValidationResult:
    """Validate *arguments* against the tool's ``inputSchema``.

    Parameters
    ----------
    tool_name:
        Used only for logging / error messages.
    arguments:
        The raw arguments dict supplied by the caller.
    schema:
        The full tool schema dict.  The ``inputSchema`` key is extracted
        automatically; if *schema* itself looks like a JSON Schema object
        (has ``"type"`` or ``"properties"``) it is used directly.
    coerce:
        When ``True``, attempt lightweight type coercion for common
        mismatches (``str → int``, ``str → bool``, ``str → float``).

    Returns
    -------
    ValidationResult
        ``valid=True`` with (optionally coerced) ``coerced_args`` on success,
        or ``valid=False`` with human-readable ``errors`` on failure.
    """
    # Normalise None → empty dict
    if arguments is None:
        arguments = {}

    # Extract the actual JSON Schema object
    input_schema = _extract_input_schema(schema)
    if input_schema is None:
        # No schema to validate against — pass through
        return ValidationResult(valid=True, coerced_args=dict(arguments))

    working_args = dict(arguments)

    if coerce:
        working_args = _coerce_types(working_args, input_schema)

    errors = _validate_against_schema(None, input_schema, tool_name)

    if errors:
        return ValidationResult(valid=False, errors=errors)

    return ValidationResult(valid=True, coerced_args=working_args)


# ---------------------------------------------------------------------------
# Core validation function
# ---------------------------------------------------------------------------

def x_validate_tool_arguments__mutmut_22(
    tool_name: str,
    arguments: dict[str, Any] | None,
    schema: dict[str, Any],
    *,
    coerce: bool = True,
) -> ValidationResult:
    """Validate *arguments* against the tool's ``inputSchema``.

    Parameters
    ----------
    tool_name:
        Used only for logging / error messages.
    arguments:
        The raw arguments dict supplied by the caller.
    schema:
        The full tool schema dict.  The ``inputSchema`` key is extracted
        automatically; if *schema* itself looks like a JSON Schema object
        (has ``"type"`` or ``"properties"``) it is used directly.
    coerce:
        When ``True``, attempt lightweight type coercion for common
        mismatches (``str → int``, ``str → bool``, ``str → float``).

    Returns
    -------
    ValidationResult
        ``valid=True`` with (optionally coerced) ``coerced_args`` on success,
        or ``valid=False`` with human-readable ``errors`` on failure.
    """
    # Normalise None → empty dict
    if arguments is None:
        arguments = {}

    # Extract the actual JSON Schema object
    input_schema = _extract_input_schema(schema)
    if input_schema is None:
        # No schema to validate against — pass through
        return ValidationResult(valid=True, coerced_args=dict(arguments))

    working_args = dict(arguments)

    if coerce:
        working_args = _coerce_types(working_args, input_schema)

    errors = _validate_against_schema(working_args, None, tool_name)

    if errors:
        return ValidationResult(valid=False, errors=errors)

    return ValidationResult(valid=True, coerced_args=working_args)


# ---------------------------------------------------------------------------
# Core validation function
# ---------------------------------------------------------------------------

def x_validate_tool_arguments__mutmut_23(
    tool_name: str,
    arguments: dict[str, Any] | None,
    schema: dict[str, Any],
    *,
    coerce: bool = True,
) -> ValidationResult:
    """Validate *arguments* against the tool's ``inputSchema``.

    Parameters
    ----------
    tool_name:
        Used only for logging / error messages.
    arguments:
        The raw arguments dict supplied by the caller.
    schema:
        The full tool schema dict.  The ``inputSchema`` key is extracted
        automatically; if *schema* itself looks like a JSON Schema object
        (has ``"type"`` or ``"properties"``) it is used directly.
    coerce:
        When ``True``, attempt lightweight type coercion for common
        mismatches (``str → int``, ``str → bool``, ``str → float``).

    Returns
    -------
    ValidationResult
        ``valid=True`` with (optionally coerced) ``coerced_args`` on success,
        or ``valid=False`` with human-readable ``errors`` on failure.
    """
    # Normalise None → empty dict
    if arguments is None:
        arguments = {}

    # Extract the actual JSON Schema object
    input_schema = _extract_input_schema(schema)
    if input_schema is None:
        # No schema to validate against — pass through
        return ValidationResult(valid=True, coerced_args=dict(arguments))

    working_args = dict(arguments)

    if coerce:
        working_args = _coerce_types(working_args, input_schema)

    errors = _validate_against_schema(working_args, input_schema, None)

    if errors:
        return ValidationResult(valid=False, errors=errors)

    return ValidationResult(valid=True, coerced_args=working_args)


# ---------------------------------------------------------------------------
# Core validation function
# ---------------------------------------------------------------------------

def x_validate_tool_arguments__mutmut_24(
    tool_name: str,
    arguments: dict[str, Any] | None,
    schema: dict[str, Any],
    *,
    coerce: bool = True,
) -> ValidationResult:
    """Validate *arguments* against the tool's ``inputSchema``.

    Parameters
    ----------
    tool_name:
        Used only for logging / error messages.
    arguments:
        The raw arguments dict supplied by the caller.
    schema:
        The full tool schema dict.  The ``inputSchema`` key is extracted
        automatically; if *schema* itself looks like a JSON Schema object
        (has ``"type"`` or ``"properties"``) it is used directly.
    coerce:
        When ``True``, attempt lightweight type coercion for common
        mismatches (``str → int``, ``str → bool``, ``str → float``).

    Returns
    -------
    ValidationResult
        ``valid=True`` with (optionally coerced) ``coerced_args`` on success,
        or ``valid=False`` with human-readable ``errors`` on failure.
    """
    # Normalise None → empty dict
    if arguments is None:
        arguments = {}

    # Extract the actual JSON Schema object
    input_schema = _extract_input_schema(schema)
    if input_schema is None:
        # No schema to validate against — pass through
        return ValidationResult(valid=True, coerced_args=dict(arguments))

    working_args = dict(arguments)

    if coerce:
        working_args = _coerce_types(working_args, input_schema)

    errors = _validate_against_schema(input_schema, tool_name)

    if errors:
        return ValidationResult(valid=False, errors=errors)

    return ValidationResult(valid=True, coerced_args=working_args)


# ---------------------------------------------------------------------------
# Core validation function
# ---------------------------------------------------------------------------

def x_validate_tool_arguments__mutmut_25(
    tool_name: str,
    arguments: dict[str, Any] | None,
    schema: dict[str, Any],
    *,
    coerce: bool = True,
) -> ValidationResult:
    """Validate *arguments* against the tool's ``inputSchema``.

    Parameters
    ----------
    tool_name:
        Used only for logging / error messages.
    arguments:
        The raw arguments dict supplied by the caller.
    schema:
        The full tool schema dict.  The ``inputSchema`` key is extracted
        automatically; if *schema* itself looks like a JSON Schema object
        (has ``"type"`` or ``"properties"``) it is used directly.
    coerce:
        When ``True``, attempt lightweight type coercion for common
        mismatches (``str → int``, ``str → bool``, ``str → float``).

    Returns
    -------
    ValidationResult
        ``valid=True`` with (optionally coerced) ``coerced_args`` on success,
        or ``valid=False`` with human-readable ``errors`` on failure.
    """
    # Normalise None → empty dict
    if arguments is None:
        arguments = {}

    # Extract the actual JSON Schema object
    input_schema = _extract_input_schema(schema)
    if input_schema is None:
        # No schema to validate against — pass through
        return ValidationResult(valid=True, coerced_args=dict(arguments))

    working_args = dict(arguments)

    if coerce:
        working_args = _coerce_types(working_args, input_schema)

    errors = _validate_against_schema(working_args, tool_name)

    if errors:
        return ValidationResult(valid=False, errors=errors)

    return ValidationResult(valid=True, coerced_args=working_args)


# ---------------------------------------------------------------------------
# Core validation function
# ---------------------------------------------------------------------------

def x_validate_tool_arguments__mutmut_26(
    tool_name: str,
    arguments: dict[str, Any] | None,
    schema: dict[str, Any],
    *,
    coerce: bool = True,
) -> ValidationResult:
    """Validate *arguments* against the tool's ``inputSchema``.

    Parameters
    ----------
    tool_name:
        Used only for logging / error messages.
    arguments:
        The raw arguments dict supplied by the caller.
    schema:
        The full tool schema dict.  The ``inputSchema`` key is extracted
        automatically; if *schema* itself looks like a JSON Schema object
        (has ``"type"`` or ``"properties"``) it is used directly.
    coerce:
        When ``True``, attempt lightweight type coercion for common
        mismatches (``str → int``, ``str → bool``, ``str → float``).

    Returns
    -------
    ValidationResult
        ``valid=True`` with (optionally coerced) ``coerced_args`` on success,
        or ``valid=False`` with human-readable ``errors`` on failure.
    """
    # Normalise None → empty dict
    if arguments is None:
        arguments = {}

    # Extract the actual JSON Schema object
    input_schema = _extract_input_schema(schema)
    if input_schema is None:
        # No schema to validate against — pass through
        return ValidationResult(valid=True, coerced_args=dict(arguments))

    working_args = dict(arguments)

    if coerce:
        working_args = _coerce_types(working_args, input_schema)

    errors = _validate_against_schema(working_args, input_schema, )

    if errors:
        return ValidationResult(valid=False, errors=errors)

    return ValidationResult(valid=True, coerced_args=working_args)


# ---------------------------------------------------------------------------
# Core validation function
# ---------------------------------------------------------------------------

def x_validate_tool_arguments__mutmut_27(
    tool_name: str,
    arguments: dict[str, Any] | None,
    schema: dict[str, Any],
    *,
    coerce: bool = True,
) -> ValidationResult:
    """Validate *arguments* against the tool's ``inputSchema``.

    Parameters
    ----------
    tool_name:
        Used only for logging / error messages.
    arguments:
        The raw arguments dict supplied by the caller.
    schema:
        The full tool schema dict.  The ``inputSchema`` key is extracted
        automatically; if *schema* itself looks like a JSON Schema object
        (has ``"type"`` or ``"properties"``) it is used directly.
    coerce:
        When ``True``, attempt lightweight type coercion for common
        mismatches (``str → int``, ``str → bool``, ``str → float``).

    Returns
    -------
    ValidationResult
        ``valid=True`` with (optionally coerced) ``coerced_args`` on success,
        or ``valid=False`` with human-readable ``errors`` on failure.
    """
    # Normalise None → empty dict
    if arguments is None:
        arguments = {}

    # Extract the actual JSON Schema object
    input_schema = _extract_input_schema(schema)
    if input_schema is None:
        # No schema to validate against — pass through
        return ValidationResult(valid=True, coerced_args=dict(arguments))

    working_args = dict(arguments)

    if coerce:
        working_args = _coerce_types(working_args, input_schema)

    errors = _validate_against_schema(working_args, input_schema, tool_name)

    if errors:
        return ValidationResult(valid=None, errors=errors)

    return ValidationResult(valid=True, coerced_args=working_args)


# ---------------------------------------------------------------------------
# Core validation function
# ---------------------------------------------------------------------------

def x_validate_tool_arguments__mutmut_28(
    tool_name: str,
    arguments: dict[str, Any] | None,
    schema: dict[str, Any],
    *,
    coerce: bool = True,
) -> ValidationResult:
    """Validate *arguments* against the tool's ``inputSchema``.

    Parameters
    ----------
    tool_name:
        Used only for logging / error messages.
    arguments:
        The raw arguments dict supplied by the caller.
    schema:
        The full tool schema dict.  The ``inputSchema`` key is extracted
        automatically; if *schema* itself looks like a JSON Schema object
        (has ``"type"`` or ``"properties"``) it is used directly.
    coerce:
        When ``True``, attempt lightweight type coercion for common
        mismatches (``str → int``, ``str → bool``, ``str → float``).

    Returns
    -------
    ValidationResult
        ``valid=True`` with (optionally coerced) ``coerced_args`` on success,
        or ``valid=False`` with human-readable ``errors`` on failure.
    """
    # Normalise None → empty dict
    if arguments is None:
        arguments = {}

    # Extract the actual JSON Schema object
    input_schema = _extract_input_schema(schema)
    if input_schema is None:
        # No schema to validate against — pass through
        return ValidationResult(valid=True, coerced_args=dict(arguments))

    working_args = dict(arguments)

    if coerce:
        working_args = _coerce_types(working_args, input_schema)

    errors = _validate_against_schema(working_args, input_schema, tool_name)

    if errors:
        return ValidationResult(valid=False, errors=None)

    return ValidationResult(valid=True, coerced_args=working_args)


# ---------------------------------------------------------------------------
# Core validation function
# ---------------------------------------------------------------------------

def x_validate_tool_arguments__mutmut_29(
    tool_name: str,
    arguments: dict[str, Any] | None,
    schema: dict[str, Any],
    *,
    coerce: bool = True,
) -> ValidationResult:
    """Validate *arguments* against the tool's ``inputSchema``.

    Parameters
    ----------
    tool_name:
        Used only for logging / error messages.
    arguments:
        The raw arguments dict supplied by the caller.
    schema:
        The full tool schema dict.  The ``inputSchema`` key is extracted
        automatically; if *schema* itself looks like a JSON Schema object
        (has ``"type"`` or ``"properties"``) it is used directly.
    coerce:
        When ``True``, attempt lightweight type coercion for common
        mismatches (``str → int``, ``str → bool``, ``str → float``).

    Returns
    -------
    ValidationResult
        ``valid=True`` with (optionally coerced) ``coerced_args`` on success,
        or ``valid=False`` with human-readable ``errors`` on failure.
    """
    # Normalise None → empty dict
    if arguments is None:
        arguments = {}

    # Extract the actual JSON Schema object
    input_schema = _extract_input_schema(schema)
    if input_schema is None:
        # No schema to validate against — pass through
        return ValidationResult(valid=True, coerced_args=dict(arguments))

    working_args = dict(arguments)

    if coerce:
        working_args = _coerce_types(working_args, input_schema)

    errors = _validate_against_schema(working_args, input_schema, tool_name)

    if errors:
        return ValidationResult(errors=errors)

    return ValidationResult(valid=True, coerced_args=working_args)


# ---------------------------------------------------------------------------
# Core validation function
# ---------------------------------------------------------------------------

def x_validate_tool_arguments__mutmut_30(
    tool_name: str,
    arguments: dict[str, Any] | None,
    schema: dict[str, Any],
    *,
    coerce: bool = True,
) -> ValidationResult:
    """Validate *arguments* against the tool's ``inputSchema``.

    Parameters
    ----------
    tool_name:
        Used only for logging / error messages.
    arguments:
        The raw arguments dict supplied by the caller.
    schema:
        The full tool schema dict.  The ``inputSchema`` key is extracted
        automatically; if *schema* itself looks like a JSON Schema object
        (has ``"type"`` or ``"properties"``) it is used directly.
    coerce:
        When ``True``, attempt lightweight type coercion for common
        mismatches (``str → int``, ``str → bool``, ``str → float``).

    Returns
    -------
    ValidationResult
        ``valid=True`` with (optionally coerced) ``coerced_args`` on success,
        or ``valid=False`` with human-readable ``errors`` on failure.
    """
    # Normalise None → empty dict
    if arguments is None:
        arguments = {}

    # Extract the actual JSON Schema object
    input_schema = _extract_input_schema(schema)
    if input_schema is None:
        # No schema to validate against — pass through
        return ValidationResult(valid=True, coerced_args=dict(arguments))

    working_args = dict(arguments)

    if coerce:
        working_args = _coerce_types(working_args, input_schema)

    errors = _validate_against_schema(working_args, input_schema, tool_name)

    if errors:
        return ValidationResult(valid=False, )

    return ValidationResult(valid=True, coerced_args=working_args)


# ---------------------------------------------------------------------------
# Core validation function
# ---------------------------------------------------------------------------

def x_validate_tool_arguments__mutmut_31(
    tool_name: str,
    arguments: dict[str, Any] | None,
    schema: dict[str, Any],
    *,
    coerce: bool = True,
) -> ValidationResult:
    """Validate *arguments* against the tool's ``inputSchema``.

    Parameters
    ----------
    tool_name:
        Used only for logging / error messages.
    arguments:
        The raw arguments dict supplied by the caller.
    schema:
        The full tool schema dict.  The ``inputSchema`` key is extracted
        automatically; if *schema* itself looks like a JSON Schema object
        (has ``"type"`` or ``"properties"``) it is used directly.
    coerce:
        When ``True``, attempt lightweight type coercion for common
        mismatches (``str → int``, ``str → bool``, ``str → float``).

    Returns
    -------
    ValidationResult
        ``valid=True`` with (optionally coerced) ``coerced_args`` on success,
        or ``valid=False`` with human-readable ``errors`` on failure.
    """
    # Normalise None → empty dict
    if arguments is None:
        arguments = {}

    # Extract the actual JSON Schema object
    input_schema = _extract_input_schema(schema)
    if input_schema is None:
        # No schema to validate against — pass through
        return ValidationResult(valid=True, coerced_args=dict(arguments))

    working_args = dict(arguments)

    if coerce:
        working_args = _coerce_types(working_args, input_schema)

    errors = _validate_against_schema(working_args, input_schema, tool_name)

    if errors:
        return ValidationResult(valid=True, errors=errors)

    return ValidationResult(valid=True, coerced_args=working_args)


# ---------------------------------------------------------------------------
# Core validation function
# ---------------------------------------------------------------------------

def x_validate_tool_arguments__mutmut_32(
    tool_name: str,
    arguments: dict[str, Any] | None,
    schema: dict[str, Any],
    *,
    coerce: bool = True,
) -> ValidationResult:
    """Validate *arguments* against the tool's ``inputSchema``.

    Parameters
    ----------
    tool_name:
        Used only for logging / error messages.
    arguments:
        The raw arguments dict supplied by the caller.
    schema:
        The full tool schema dict.  The ``inputSchema`` key is extracted
        automatically; if *schema* itself looks like a JSON Schema object
        (has ``"type"`` or ``"properties"``) it is used directly.
    coerce:
        When ``True``, attempt lightweight type coercion for common
        mismatches (``str → int``, ``str → bool``, ``str → float``).

    Returns
    -------
    ValidationResult
        ``valid=True`` with (optionally coerced) ``coerced_args`` on success,
        or ``valid=False`` with human-readable ``errors`` on failure.
    """
    # Normalise None → empty dict
    if arguments is None:
        arguments = {}

    # Extract the actual JSON Schema object
    input_schema = _extract_input_schema(schema)
    if input_schema is None:
        # No schema to validate against — pass through
        return ValidationResult(valid=True, coerced_args=dict(arguments))

    working_args = dict(arguments)

    if coerce:
        working_args = _coerce_types(working_args, input_schema)

    errors = _validate_against_schema(working_args, input_schema, tool_name)

    if errors:
        return ValidationResult(valid=False, errors=errors)

    return ValidationResult(valid=None, coerced_args=working_args)


# ---------------------------------------------------------------------------
# Core validation function
# ---------------------------------------------------------------------------

def x_validate_tool_arguments__mutmut_33(
    tool_name: str,
    arguments: dict[str, Any] | None,
    schema: dict[str, Any],
    *,
    coerce: bool = True,
) -> ValidationResult:
    """Validate *arguments* against the tool's ``inputSchema``.

    Parameters
    ----------
    tool_name:
        Used only for logging / error messages.
    arguments:
        The raw arguments dict supplied by the caller.
    schema:
        The full tool schema dict.  The ``inputSchema`` key is extracted
        automatically; if *schema* itself looks like a JSON Schema object
        (has ``"type"`` or ``"properties"``) it is used directly.
    coerce:
        When ``True``, attempt lightweight type coercion for common
        mismatches (``str → int``, ``str → bool``, ``str → float``).

    Returns
    -------
    ValidationResult
        ``valid=True`` with (optionally coerced) ``coerced_args`` on success,
        or ``valid=False`` with human-readable ``errors`` on failure.
    """
    # Normalise None → empty dict
    if arguments is None:
        arguments = {}

    # Extract the actual JSON Schema object
    input_schema = _extract_input_schema(schema)
    if input_schema is None:
        # No schema to validate against — pass through
        return ValidationResult(valid=True, coerced_args=dict(arguments))

    working_args = dict(arguments)

    if coerce:
        working_args = _coerce_types(working_args, input_schema)

    errors = _validate_against_schema(working_args, input_schema, tool_name)

    if errors:
        return ValidationResult(valid=False, errors=errors)

    return ValidationResult(valid=True, coerced_args=None)


# ---------------------------------------------------------------------------
# Core validation function
# ---------------------------------------------------------------------------

def x_validate_tool_arguments__mutmut_34(
    tool_name: str,
    arguments: dict[str, Any] | None,
    schema: dict[str, Any],
    *,
    coerce: bool = True,
) -> ValidationResult:
    """Validate *arguments* against the tool's ``inputSchema``.

    Parameters
    ----------
    tool_name:
        Used only for logging / error messages.
    arguments:
        The raw arguments dict supplied by the caller.
    schema:
        The full tool schema dict.  The ``inputSchema`` key is extracted
        automatically; if *schema* itself looks like a JSON Schema object
        (has ``"type"`` or ``"properties"``) it is used directly.
    coerce:
        When ``True``, attempt lightweight type coercion for common
        mismatches (``str → int``, ``str → bool``, ``str → float``).

    Returns
    -------
    ValidationResult
        ``valid=True`` with (optionally coerced) ``coerced_args`` on success,
        or ``valid=False`` with human-readable ``errors`` on failure.
    """
    # Normalise None → empty dict
    if arguments is None:
        arguments = {}

    # Extract the actual JSON Schema object
    input_schema = _extract_input_schema(schema)
    if input_schema is None:
        # No schema to validate against — pass through
        return ValidationResult(valid=True, coerced_args=dict(arguments))

    working_args = dict(arguments)

    if coerce:
        working_args = _coerce_types(working_args, input_schema)

    errors = _validate_against_schema(working_args, input_schema, tool_name)

    if errors:
        return ValidationResult(valid=False, errors=errors)

    return ValidationResult(coerced_args=working_args)


# ---------------------------------------------------------------------------
# Core validation function
# ---------------------------------------------------------------------------

def x_validate_tool_arguments__mutmut_35(
    tool_name: str,
    arguments: dict[str, Any] | None,
    schema: dict[str, Any],
    *,
    coerce: bool = True,
) -> ValidationResult:
    """Validate *arguments* against the tool's ``inputSchema``.

    Parameters
    ----------
    tool_name:
        Used only for logging / error messages.
    arguments:
        The raw arguments dict supplied by the caller.
    schema:
        The full tool schema dict.  The ``inputSchema`` key is extracted
        automatically; if *schema* itself looks like a JSON Schema object
        (has ``"type"`` or ``"properties"``) it is used directly.
    coerce:
        When ``True``, attempt lightweight type coercion for common
        mismatches (``str → int``, ``str → bool``, ``str → float``).

    Returns
    -------
    ValidationResult
        ``valid=True`` with (optionally coerced) ``coerced_args`` on success,
        or ``valid=False`` with human-readable ``errors`` on failure.
    """
    # Normalise None → empty dict
    if arguments is None:
        arguments = {}

    # Extract the actual JSON Schema object
    input_schema = _extract_input_schema(schema)
    if input_schema is None:
        # No schema to validate against — pass through
        return ValidationResult(valid=True, coerced_args=dict(arguments))

    working_args = dict(arguments)

    if coerce:
        working_args = _coerce_types(working_args, input_schema)

    errors = _validate_against_schema(working_args, input_schema, tool_name)

    if errors:
        return ValidationResult(valid=False, errors=errors)

    return ValidationResult(valid=True, )


# ---------------------------------------------------------------------------
# Core validation function
# ---------------------------------------------------------------------------

def x_validate_tool_arguments__mutmut_36(
    tool_name: str,
    arguments: dict[str, Any] | None,
    schema: dict[str, Any],
    *,
    coerce: bool = True,
) -> ValidationResult:
    """Validate *arguments* against the tool's ``inputSchema``.

    Parameters
    ----------
    tool_name:
        Used only for logging / error messages.
    arguments:
        The raw arguments dict supplied by the caller.
    schema:
        The full tool schema dict.  The ``inputSchema`` key is extracted
        automatically; if *schema* itself looks like a JSON Schema object
        (has ``"type"`` or ``"properties"``) it is used directly.
    coerce:
        When ``True``, attempt lightweight type coercion for common
        mismatches (``str → int``, ``str → bool``, ``str → float``).

    Returns
    -------
    ValidationResult
        ``valid=True`` with (optionally coerced) ``coerced_args`` on success,
        or ``valid=False`` with human-readable ``errors`` on failure.
    """
    # Normalise None → empty dict
    if arguments is None:
        arguments = {}

    # Extract the actual JSON Schema object
    input_schema = _extract_input_schema(schema)
    if input_schema is None:
        # No schema to validate against — pass through
        return ValidationResult(valid=True, coerced_args=dict(arguments))

    working_args = dict(arguments)

    if coerce:
        working_args = _coerce_types(working_args, input_schema)

    errors = _validate_against_schema(working_args, input_schema, tool_name)

    if errors:
        return ValidationResult(valid=False, errors=errors)

    return ValidationResult(valid=False, coerced_args=working_args)

x_validate_tool_arguments__mutmut_mutants : ClassVar[MutantDict] = {
'x_validate_tool_arguments__mutmut_1': x_validate_tool_arguments__mutmut_1, 
    'x_validate_tool_arguments__mutmut_2': x_validate_tool_arguments__mutmut_2, 
    'x_validate_tool_arguments__mutmut_3': x_validate_tool_arguments__mutmut_3, 
    'x_validate_tool_arguments__mutmut_4': x_validate_tool_arguments__mutmut_4, 
    'x_validate_tool_arguments__mutmut_5': x_validate_tool_arguments__mutmut_5, 
    'x_validate_tool_arguments__mutmut_6': x_validate_tool_arguments__mutmut_6, 
    'x_validate_tool_arguments__mutmut_7': x_validate_tool_arguments__mutmut_7, 
    'x_validate_tool_arguments__mutmut_8': x_validate_tool_arguments__mutmut_8, 
    'x_validate_tool_arguments__mutmut_9': x_validate_tool_arguments__mutmut_9, 
    'x_validate_tool_arguments__mutmut_10': x_validate_tool_arguments__mutmut_10, 
    'x_validate_tool_arguments__mutmut_11': x_validate_tool_arguments__mutmut_11, 
    'x_validate_tool_arguments__mutmut_12': x_validate_tool_arguments__mutmut_12, 
    'x_validate_tool_arguments__mutmut_13': x_validate_tool_arguments__mutmut_13, 
    'x_validate_tool_arguments__mutmut_14': x_validate_tool_arguments__mutmut_14, 
    'x_validate_tool_arguments__mutmut_15': x_validate_tool_arguments__mutmut_15, 
    'x_validate_tool_arguments__mutmut_16': x_validate_tool_arguments__mutmut_16, 
    'x_validate_tool_arguments__mutmut_17': x_validate_tool_arguments__mutmut_17, 
    'x_validate_tool_arguments__mutmut_18': x_validate_tool_arguments__mutmut_18, 
    'x_validate_tool_arguments__mutmut_19': x_validate_tool_arguments__mutmut_19, 
    'x_validate_tool_arguments__mutmut_20': x_validate_tool_arguments__mutmut_20, 
    'x_validate_tool_arguments__mutmut_21': x_validate_tool_arguments__mutmut_21, 
    'x_validate_tool_arguments__mutmut_22': x_validate_tool_arguments__mutmut_22, 
    'x_validate_tool_arguments__mutmut_23': x_validate_tool_arguments__mutmut_23, 
    'x_validate_tool_arguments__mutmut_24': x_validate_tool_arguments__mutmut_24, 
    'x_validate_tool_arguments__mutmut_25': x_validate_tool_arguments__mutmut_25, 
    'x_validate_tool_arguments__mutmut_26': x_validate_tool_arguments__mutmut_26, 
    'x_validate_tool_arguments__mutmut_27': x_validate_tool_arguments__mutmut_27, 
    'x_validate_tool_arguments__mutmut_28': x_validate_tool_arguments__mutmut_28, 
    'x_validate_tool_arguments__mutmut_29': x_validate_tool_arguments__mutmut_29, 
    'x_validate_tool_arguments__mutmut_30': x_validate_tool_arguments__mutmut_30, 
    'x_validate_tool_arguments__mutmut_31': x_validate_tool_arguments__mutmut_31, 
    'x_validate_tool_arguments__mutmut_32': x_validate_tool_arguments__mutmut_32, 
    'x_validate_tool_arguments__mutmut_33': x_validate_tool_arguments__mutmut_33, 
    'x_validate_tool_arguments__mutmut_34': x_validate_tool_arguments__mutmut_34, 
    'x_validate_tool_arguments__mutmut_35': x_validate_tool_arguments__mutmut_35, 
    'x_validate_tool_arguments__mutmut_36': x_validate_tool_arguments__mutmut_36
}

def validate_tool_arguments(*args, **kwargs):
    result = _mutmut_trampoline(x_validate_tool_arguments__mutmut_orig, x_validate_tool_arguments__mutmut_mutants, args, kwargs)
    return result 

validate_tool_arguments.__signature__ = _mutmut_signature(x_validate_tool_arguments__mutmut_orig)
x_validate_tool_arguments__mutmut_orig.__name__ = 'x_validate_tool_arguments'


# ---------------------------------------------------------------------------
# Schema extraction
# ---------------------------------------------------------------------------

def x__extract_input_schema__mutmut_orig(schema: dict[str, Any]) -> dict[str, Any] | None:
    """Pull the ``inputSchema`` out of a tool schema dict.

    Handles both ``{"inputSchema": {...}}`` and a bare JSON Schema object.
    """
    if "inputSchema" in schema:
        return schema["inputSchema"]
    if "type" in schema or "properties" in schema:
        return schema
    return None


# ---------------------------------------------------------------------------
# Schema extraction
# ---------------------------------------------------------------------------

def x__extract_input_schema__mutmut_1(schema: dict[str, Any]) -> dict[str, Any] | None:
    """Pull the ``inputSchema`` out of a tool schema dict.

    Handles both ``{"inputSchema": {...}}`` and a bare JSON Schema object.
    """
    if "XXinputSchemaXX" in schema:
        return schema["inputSchema"]
    if "type" in schema or "properties" in schema:
        return schema
    return None


# ---------------------------------------------------------------------------
# Schema extraction
# ---------------------------------------------------------------------------

def x__extract_input_schema__mutmut_2(schema: dict[str, Any]) -> dict[str, Any] | None:
    """Pull the ``inputSchema`` out of a tool schema dict.

    Handles both ``{"inputSchema": {...}}`` and a bare JSON Schema object.
    """
    if "inputschema" in schema:
        return schema["inputSchema"]
    if "type" in schema or "properties" in schema:
        return schema
    return None


# ---------------------------------------------------------------------------
# Schema extraction
# ---------------------------------------------------------------------------

def x__extract_input_schema__mutmut_3(schema: dict[str, Any]) -> dict[str, Any] | None:
    """Pull the ``inputSchema`` out of a tool schema dict.

    Handles both ``{"inputSchema": {...}}`` and a bare JSON Schema object.
    """
    if "INPUTSCHEMA" in schema:
        return schema["inputSchema"]
    if "type" in schema or "properties" in schema:
        return schema
    return None


# ---------------------------------------------------------------------------
# Schema extraction
# ---------------------------------------------------------------------------

def x__extract_input_schema__mutmut_4(schema: dict[str, Any]) -> dict[str, Any] | None:
    """Pull the ``inputSchema`` out of a tool schema dict.

    Handles both ``{"inputSchema": {...}}`` and a bare JSON Schema object.
    """
    if "inputSchema" not in schema:
        return schema["inputSchema"]
    if "type" in schema or "properties" in schema:
        return schema
    return None


# ---------------------------------------------------------------------------
# Schema extraction
# ---------------------------------------------------------------------------

def x__extract_input_schema__mutmut_5(schema: dict[str, Any]) -> dict[str, Any] | None:
    """Pull the ``inputSchema`` out of a tool schema dict.

    Handles both ``{"inputSchema": {...}}`` and a bare JSON Schema object.
    """
    if "inputSchema" in schema:
        return schema["XXinputSchemaXX"]
    if "type" in schema or "properties" in schema:
        return schema
    return None


# ---------------------------------------------------------------------------
# Schema extraction
# ---------------------------------------------------------------------------

def x__extract_input_schema__mutmut_6(schema: dict[str, Any]) -> dict[str, Any] | None:
    """Pull the ``inputSchema`` out of a tool schema dict.

    Handles both ``{"inputSchema": {...}}`` and a bare JSON Schema object.
    """
    if "inputSchema" in schema:
        return schema["inputschema"]
    if "type" in schema or "properties" in schema:
        return schema
    return None


# ---------------------------------------------------------------------------
# Schema extraction
# ---------------------------------------------------------------------------

def x__extract_input_schema__mutmut_7(schema: dict[str, Any]) -> dict[str, Any] | None:
    """Pull the ``inputSchema`` out of a tool schema dict.

    Handles both ``{"inputSchema": {...}}`` and a bare JSON Schema object.
    """
    if "inputSchema" in schema:
        return schema["INPUTSCHEMA"]
    if "type" in schema or "properties" in schema:
        return schema
    return None


# ---------------------------------------------------------------------------
# Schema extraction
# ---------------------------------------------------------------------------

def x__extract_input_schema__mutmut_8(schema: dict[str, Any]) -> dict[str, Any] | None:
    """Pull the ``inputSchema`` out of a tool schema dict.

    Handles both ``{"inputSchema": {...}}`` and a bare JSON Schema object.
    """
    if "inputSchema" in schema:
        return schema["inputSchema"]
    if "type" in schema and "properties" in schema:
        return schema
    return None


# ---------------------------------------------------------------------------
# Schema extraction
# ---------------------------------------------------------------------------

def x__extract_input_schema__mutmut_9(schema: dict[str, Any]) -> dict[str, Any] | None:
    """Pull the ``inputSchema`` out of a tool schema dict.

    Handles both ``{"inputSchema": {...}}`` and a bare JSON Schema object.
    """
    if "inputSchema" in schema:
        return schema["inputSchema"]
    if "XXtypeXX" in schema or "properties" in schema:
        return schema
    return None


# ---------------------------------------------------------------------------
# Schema extraction
# ---------------------------------------------------------------------------

def x__extract_input_schema__mutmut_10(schema: dict[str, Any]) -> dict[str, Any] | None:
    """Pull the ``inputSchema`` out of a tool schema dict.

    Handles both ``{"inputSchema": {...}}`` and a bare JSON Schema object.
    """
    if "inputSchema" in schema:
        return schema["inputSchema"]
    if "TYPE" in schema or "properties" in schema:
        return schema
    return None


# ---------------------------------------------------------------------------
# Schema extraction
# ---------------------------------------------------------------------------

def x__extract_input_schema__mutmut_11(schema: dict[str, Any]) -> dict[str, Any] | None:
    """Pull the ``inputSchema`` out of a tool schema dict.

    Handles both ``{"inputSchema": {...}}`` and a bare JSON Schema object.
    """
    if "inputSchema" in schema:
        return schema["inputSchema"]
    if "type" not in schema or "properties" in schema:
        return schema
    return None


# ---------------------------------------------------------------------------
# Schema extraction
# ---------------------------------------------------------------------------

def x__extract_input_schema__mutmut_12(schema: dict[str, Any]) -> dict[str, Any] | None:
    """Pull the ``inputSchema`` out of a tool schema dict.

    Handles both ``{"inputSchema": {...}}`` and a bare JSON Schema object.
    """
    if "inputSchema" in schema:
        return schema["inputSchema"]
    if "type" in schema or "XXpropertiesXX" in schema:
        return schema
    return None


# ---------------------------------------------------------------------------
# Schema extraction
# ---------------------------------------------------------------------------

def x__extract_input_schema__mutmut_13(schema: dict[str, Any]) -> dict[str, Any] | None:
    """Pull the ``inputSchema`` out of a tool schema dict.

    Handles both ``{"inputSchema": {...}}`` and a bare JSON Schema object.
    """
    if "inputSchema" in schema:
        return schema["inputSchema"]
    if "type" in schema or "PROPERTIES" in schema:
        return schema
    return None


# ---------------------------------------------------------------------------
# Schema extraction
# ---------------------------------------------------------------------------

def x__extract_input_schema__mutmut_14(schema: dict[str, Any]) -> dict[str, Any] | None:
    """Pull the ``inputSchema`` out of a tool schema dict.

    Handles both ``{"inputSchema": {...}}`` and a bare JSON Schema object.
    """
    if "inputSchema" in schema:
        return schema["inputSchema"]
    if "type" in schema or "properties" not in schema:
        return schema
    return None

x__extract_input_schema__mutmut_mutants : ClassVar[MutantDict] = {
'x__extract_input_schema__mutmut_1': x__extract_input_schema__mutmut_1, 
    'x__extract_input_schema__mutmut_2': x__extract_input_schema__mutmut_2, 
    'x__extract_input_schema__mutmut_3': x__extract_input_schema__mutmut_3, 
    'x__extract_input_schema__mutmut_4': x__extract_input_schema__mutmut_4, 
    'x__extract_input_schema__mutmut_5': x__extract_input_schema__mutmut_5, 
    'x__extract_input_schema__mutmut_6': x__extract_input_schema__mutmut_6, 
    'x__extract_input_schema__mutmut_7': x__extract_input_schema__mutmut_7, 
    'x__extract_input_schema__mutmut_8': x__extract_input_schema__mutmut_8, 
    'x__extract_input_schema__mutmut_9': x__extract_input_schema__mutmut_9, 
    'x__extract_input_schema__mutmut_10': x__extract_input_schema__mutmut_10, 
    'x__extract_input_schema__mutmut_11': x__extract_input_schema__mutmut_11, 
    'x__extract_input_schema__mutmut_12': x__extract_input_schema__mutmut_12, 
    'x__extract_input_schema__mutmut_13': x__extract_input_schema__mutmut_13, 
    'x__extract_input_schema__mutmut_14': x__extract_input_schema__mutmut_14
}

def _extract_input_schema(*args, **kwargs):
    result = _mutmut_trampoline(x__extract_input_schema__mutmut_orig, x__extract_input_schema__mutmut_mutants, args, kwargs)
    return result 

_extract_input_schema.__signature__ = _mutmut_signature(x__extract_input_schema__mutmut_orig)
x__extract_input_schema__mutmut_orig.__name__ = 'x__extract_input_schema'


# ---------------------------------------------------------------------------
# Lightweight type coercion
# ---------------------------------------------------------------------------

_BOOL_TRUTHY = frozenset({"true", "1", "yes", "on"})
_BOOL_FALSY = frozenset({"false", "0", "no", "off"})


def x__coerce_types__mutmut_orig(
    args: dict[str, Any],
    schema: dict[str, Any],
) -> dict[str, Any]:
    """Best-effort coercion of string values to declared schema types."""
    properties = schema.get("properties", {})
    coerced = dict(args)

    for key, value in coerced.items():
        if key not in properties:
            continue
        prop_schema = properties[key]
        expected_type = prop_schema.get("type")
        if expected_type is None or not isinstance(value, str):
            continue

        try:
            if expected_type == "integer":
                coerced[key] = int(value)
            elif expected_type == "number":
                coerced[key] = float(value)
            elif expected_type == "boolean":
                low = value.lower()
                if low in _BOOL_TRUTHY:
                    coerced[key] = True
                elif low in _BOOL_FALSY:
                    coerced[key] = False
        except (ValueError, TypeError):
            pass  # Let validation catch it

    return coerced


def x__coerce_types__mutmut_1(
    args: dict[str, Any],
    schema: dict[str, Any],
) -> dict[str, Any]:
    """Best-effort coercion of string values to declared schema types."""
    properties = None
    coerced = dict(args)

    for key, value in coerced.items():
        if key not in properties:
            continue
        prop_schema = properties[key]
        expected_type = prop_schema.get("type")
        if expected_type is None or not isinstance(value, str):
            continue

        try:
            if expected_type == "integer":
                coerced[key] = int(value)
            elif expected_type == "number":
                coerced[key] = float(value)
            elif expected_type == "boolean":
                low = value.lower()
                if low in _BOOL_TRUTHY:
                    coerced[key] = True
                elif low in _BOOL_FALSY:
                    coerced[key] = False
        except (ValueError, TypeError):
            pass  # Let validation catch it

    return coerced


def x__coerce_types__mutmut_2(
    args: dict[str, Any],
    schema: dict[str, Any],
) -> dict[str, Any]:
    """Best-effort coercion of string values to declared schema types."""
    properties = schema.get(None, {})
    coerced = dict(args)

    for key, value in coerced.items():
        if key not in properties:
            continue
        prop_schema = properties[key]
        expected_type = prop_schema.get("type")
        if expected_type is None or not isinstance(value, str):
            continue

        try:
            if expected_type == "integer":
                coerced[key] = int(value)
            elif expected_type == "number":
                coerced[key] = float(value)
            elif expected_type == "boolean":
                low = value.lower()
                if low in _BOOL_TRUTHY:
                    coerced[key] = True
                elif low in _BOOL_FALSY:
                    coerced[key] = False
        except (ValueError, TypeError):
            pass  # Let validation catch it

    return coerced


def x__coerce_types__mutmut_3(
    args: dict[str, Any],
    schema: dict[str, Any],
) -> dict[str, Any]:
    """Best-effort coercion of string values to declared schema types."""
    properties = schema.get("properties", None)
    coerced = dict(args)

    for key, value in coerced.items():
        if key not in properties:
            continue
        prop_schema = properties[key]
        expected_type = prop_schema.get("type")
        if expected_type is None or not isinstance(value, str):
            continue

        try:
            if expected_type == "integer":
                coerced[key] = int(value)
            elif expected_type == "number":
                coerced[key] = float(value)
            elif expected_type == "boolean":
                low = value.lower()
                if low in _BOOL_TRUTHY:
                    coerced[key] = True
                elif low in _BOOL_FALSY:
                    coerced[key] = False
        except (ValueError, TypeError):
            pass  # Let validation catch it

    return coerced


def x__coerce_types__mutmut_4(
    args: dict[str, Any],
    schema: dict[str, Any],
) -> dict[str, Any]:
    """Best-effort coercion of string values to declared schema types."""
    properties = schema.get({})
    coerced = dict(args)

    for key, value in coerced.items():
        if key not in properties:
            continue
        prop_schema = properties[key]
        expected_type = prop_schema.get("type")
        if expected_type is None or not isinstance(value, str):
            continue

        try:
            if expected_type == "integer":
                coerced[key] = int(value)
            elif expected_type == "number":
                coerced[key] = float(value)
            elif expected_type == "boolean":
                low = value.lower()
                if low in _BOOL_TRUTHY:
                    coerced[key] = True
                elif low in _BOOL_FALSY:
                    coerced[key] = False
        except (ValueError, TypeError):
            pass  # Let validation catch it

    return coerced


def x__coerce_types__mutmut_5(
    args: dict[str, Any],
    schema: dict[str, Any],
) -> dict[str, Any]:
    """Best-effort coercion of string values to declared schema types."""
    properties = schema.get("properties", )
    coerced = dict(args)

    for key, value in coerced.items():
        if key not in properties:
            continue
        prop_schema = properties[key]
        expected_type = prop_schema.get("type")
        if expected_type is None or not isinstance(value, str):
            continue

        try:
            if expected_type == "integer":
                coerced[key] = int(value)
            elif expected_type == "number":
                coerced[key] = float(value)
            elif expected_type == "boolean":
                low = value.lower()
                if low in _BOOL_TRUTHY:
                    coerced[key] = True
                elif low in _BOOL_FALSY:
                    coerced[key] = False
        except (ValueError, TypeError):
            pass  # Let validation catch it

    return coerced


def x__coerce_types__mutmut_6(
    args: dict[str, Any],
    schema: dict[str, Any],
) -> dict[str, Any]:
    """Best-effort coercion of string values to declared schema types."""
    properties = schema.get("XXpropertiesXX", {})
    coerced = dict(args)

    for key, value in coerced.items():
        if key not in properties:
            continue
        prop_schema = properties[key]
        expected_type = prop_schema.get("type")
        if expected_type is None or not isinstance(value, str):
            continue

        try:
            if expected_type == "integer":
                coerced[key] = int(value)
            elif expected_type == "number":
                coerced[key] = float(value)
            elif expected_type == "boolean":
                low = value.lower()
                if low in _BOOL_TRUTHY:
                    coerced[key] = True
                elif low in _BOOL_FALSY:
                    coerced[key] = False
        except (ValueError, TypeError):
            pass  # Let validation catch it

    return coerced


def x__coerce_types__mutmut_7(
    args: dict[str, Any],
    schema: dict[str, Any],
) -> dict[str, Any]:
    """Best-effort coercion of string values to declared schema types."""
    properties = schema.get("PROPERTIES", {})
    coerced = dict(args)

    for key, value in coerced.items():
        if key not in properties:
            continue
        prop_schema = properties[key]
        expected_type = prop_schema.get("type")
        if expected_type is None or not isinstance(value, str):
            continue

        try:
            if expected_type == "integer":
                coerced[key] = int(value)
            elif expected_type == "number":
                coerced[key] = float(value)
            elif expected_type == "boolean":
                low = value.lower()
                if low in _BOOL_TRUTHY:
                    coerced[key] = True
                elif low in _BOOL_FALSY:
                    coerced[key] = False
        except (ValueError, TypeError):
            pass  # Let validation catch it

    return coerced


def x__coerce_types__mutmut_8(
    args: dict[str, Any],
    schema: dict[str, Any],
) -> dict[str, Any]:
    """Best-effort coercion of string values to declared schema types."""
    properties = schema.get("properties", {})
    coerced = None

    for key, value in coerced.items():
        if key not in properties:
            continue
        prop_schema = properties[key]
        expected_type = prop_schema.get("type")
        if expected_type is None or not isinstance(value, str):
            continue

        try:
            if expected_type == "integer":
                coerced[key] = int(value)
            elif expected_type == "number":
                coerced[key] = float(value)
            elif expected_type == "boolean":
                low = value.lower()
                if low in _BOOL_TRUTHY:
                    coerced[key] = True
                elif low in _BOOL_FALSY:
                    coerced[key] = False
        except (ValueError, TypeError):
            pass  # Let validation catch it

    return coerced


def x__coerce_types__mutmut_9(
    args: dict[str, Any],
    schema: dict[str, Any],
) -> dict[str, Any]:
    """Best-effort coercion of string values to declared schema types."""
    properties = schema.get("properties", {})
    coerced = dict(None)

    for key, value in coerced.items():
        if key not in properties:
            continue
        prop_schema = properties[key]
        expected_type = prop_schema.get("type")
        if expected_type is None or not isinstance(value, str):
            continue

        try:
            if expected_type == "integer":
                coerced[key] = int(value)
            elif expected_type == "number":
                coerced[key] = float(value)
            elif expected_type == "boolean":
                low = value.lower()
                if low in _BOOL_TRUTHY:
                    coerced[key] = True
                elif low in _BOOL_FALSY:
                    coerced[key] = False
        except (ValueError, TypeError):
            pass  # Let validation catch it

    return coerced


def x__coerce_types__mutmut_10(
    args: dict[str, Any],
    schema: dict[str, Any],
) -> dict[str, Any]:
    """Best-effort coercion of string values to declared schema types."""
    properties = schema.get("properties", {})
    coerced = dict(args)

    for key, value in coerced.items():
        if key in properties:
            continue
        prop_schema = properties[key]
        expected_type = prop_schema.get("type")
        if expected_type is None or not isinstance(value, str):
            continue

        try:
            if expected_type == "integer":
                coerced[key] = int(value)
            elif expected_type == "number":
                coerced[key] = float(value)
            elif expected_type == "boolean":
                low = value.lower()
                if low in _BOOL_TRUTHY:
                    coerced[key] = True
                elif low in _BOOL_FALSY:
                    coerced[key] = False
        except (ValueError, TypeError):
            pass  # Let validation catch it

    return coerced


def x__coerce_types__mutmut_11(
    args: dict[str, Any],
    schema: dict[str, Any],
) -> dict[str, Any]:
    """Best-effort coercion of string values to declared schema types."""
    properties = schema.get("properties", {})
    coerced = dict(args)

    for key, value in coerced.items():
        if key not in properties:
            break
        prop_schema = properties[key]
        expected_type = prop_schema.get("type")
        if expected_type is None or not isinstance(value, str):
            continue

        try:
            if expected_type == "integer":
                coerced[key] = int(value)
            elif expected_type == "number":
                coerced[key] = float(value)
            elif expected_type == "boolean":
                low = value.lower()
                if low in _BOOL_TRUTHY:
                    coerced[key] = True
                elif low in _BOOL_FALSY:
                    coerced[key] = False
        except (ValueError, TypeError):
            pass  # Let validation catch it

    return coerced


def x__coerce_types__mutmut_12(
    args: dict[str, Any],
    schema: dict[str, Any],
) -> dict[str, Any]:
    """Best-effort coercion of string values to declared schema types."""
    properties = schema.get("properties", {})
    coerced = dict(args)

    for key, value in coerced.items():
        if key not in properties:
            continue
        prop_schema = None
        expected_type = prop_schema.get("type")
        if expected_type is None or not isinstance(value, str):
            continue

        try:
            if expected_type == "integer":
                coerced[key] = int(value)
            elif expected_type == "number":
                coerced[key] = float(value)
            elif expected_type == "boolean":
                low = value.lower()
                if low in _BOOL_TRUTHY:
                    coerced[key] = True
                elif low in _BOOL_FALSY:
                    coerced[key] = False
        except (ValueError, TypeError):
            pass  # Let validation catch it

    return coerced


def x__coerce_types__mutmut_13(
    args: dict[str, Any],
    schema: dict[str, Any],
) -> dict[str, Any]:
    """Best-effort coercion of string values to declared schema types."""
    properties = schema.get("properties", {})
    coerced = dict(args)

    for key, value in coerced.items():
        if key not in properties:
            continue
        prop_schema = properties[key]
        expected_type = None
        if expected_type is None or not isinstance(value, str):
            continue

        try:
            if expected_type == "integer":
                coerced[key] = int(value)
            elif expected_type == "number":
                coerced[key] = float(value)
            elif expected_type == "boolean":
                low = value.lower()
                if low in _BOOL_TRUTHY:
                    coerced[key] = True
                elif low in _BOOL_FALSY:
                    coerced[key] = False
        except (ValueError, TypeError):
            pass  # Let validation catch it

    return coerced


def x__coerce_types__mutmut_14(
    args: dict[str, Any],
    schema: dict[str, Any],
) -> dict[str, Any]:
    """Best-effort coercion of string values to declared schema types."""
    properties = schema.get("properties", {})
    coerced = dict(args)

    for key, value in coerced.items():
        if key not in properties:
            continue
        prop_schema = properties[key]
        expected_type = prop_schema.get(None)
        if expected_type is None or not isinstance(value, str):
            continue

        try:
            if expected_type == "integer":
                coerced[key] = int(value)
            elif expected_type == "number":
                coerced[key] = float(value)
            elif expected_type == "boolean":
                low = value.lower()
                if low in _BOOL_TRUTHY:
                    coerced[key] = True
                elif low in _BOOL_FALSY:
                    coerced[key] = False
        except (ValueError, TypeError):
            pass  # Let validation catch it

    return coerced


def x__coerce_types__mutmut_15(
    args: dict[str, Any],
    schema: dict[str, Any],
) -> dict[str, Any]:
    """Best-effort coercion of string values to declared schema types."""
    properties = schema.get("properties", {})
    coerced = dict(args)

    for key, value in coerced.items():
        if key not in properties:
            continue
        prop_schema = properties[key]
        expected_type = prop_schema.get("XXtypeXX")
        if expected_type is None or not isinstance(value, str):
            continue

        try:
            if expected_type == "integer":
                coerced[key] = int(value)
            elif expected_type == "number":
                coerced[key] = float(value)
            elif expected_type == "boolean":
                low = value.lower()
                if low in _BOOL_TRUTHY:
                    coerced[key] = True
                elif low in _BOOL_FALSY:
                    coerced[key] = False
        except (ValueError, TypeError):
            pass  # Let validation catch it

    return coerced


def x__coerce_types__mutmut_16(
    args: dict[str, Any],
    schema: dict[str, Any],
) -> dict[str, Any]:
    """Best-effort coercion of string values to declared schema types."""
    properties = schema.get("properties", {})
    coerced = dict(args)

    for key, value in coerced.items():
        if key not in properties:
            continue
        prop_schema = properties[key]
        expected_type = prop_schema.get("TYPE")
        if expected_type is None or not isinstance(value, str):
            continue

        try:
            if expected_type == "integer":
                coerced[key] = int(value)
            elif expected_type == "number":
                coerced[key] = float(value)
            elif expected_type == "boolean":
                low = value.lower()
                if low in _BOOL_TRUTHY:
                    coerced[key] = True
                elif low in _BOOL_FALSY:
                    coerced[key] = False
        except (ValueError, TypeError):
            pass  # Let validation catch it

    return coerced


def x__coerce_types__mutmut_17(
    args: dict[str, Any],
    schema: dict[str, Any],
) -> dict[str, Any]:
    """Best-effort coercion of string values to declared schema types."""
    properties = schema.get("properties", {})
    coerced = dict(args)

    for key, value in coerced.items():
        if key not in properties:
            continue
        prop_schema = properties[key]
        expected_type = prop_schema.get("type")
        if expected_type is None and not isinstance(value, str):
            continue

        try:
            if expected_type == "integer":
                coerced[key] = int(value)
            elif expected_type == "number":
                coerced[key] = float(value)
            elif expected_type == "boolean":
                low = value.lower()
                if low in _BOOL_TRUTHY:
                    coerced[key] = True
                elif low in _BOOL_FALSY:
                    coerced[key] = False
        except (ValueError, TypeError):
            pass  # Let validation catch it

    return coerced


def x__coerce_types__mutmut_18(
    args: dict[str, Any],
    schema: dict[str, Any],
) -> dict[str, Any]:
    """Best-effort coercion of string values to declared schema types."""
    properties = schema.get("properties", {})
    coerced = dict(args)

    for key, value in coerced.items():
        if key not in properties:
            continue
        prop_schema = properties[key]
        expected_type = prop_schema.get("type")
        if expected_type is not None or not isinstance(value, str):
            continue

        try:
            if expected_type == "integer":
                coerced[key] = int(value)
            elif expected_type == "number":
                coerced[key] = float(value)
            elif expected_type == "boolean":
                low = value.lower()
                if low in _BOOL_TRUTHY:
                    coerced[key] = True
                elif low in _BOOL_FALSY:
                    coerced[key] = False
        except (ValueError, TypeError):
            pass  # Let validation catch it

    return coerced


def x__coerce_types__mutmut_19(
    args: dict[str, Any],
    schema: dict[str, Any],
) -> dict[str, Any]:
    """Best-effort coercion of string values to declared schema types."""
    properties = schema.get("properties", {})
    coerced = dict(args)

    for key, value in coerced.items():
        if key not in properties:
            continue
        prop_schema = properties[key]
        expected_type = prop_schema.get("type")
        if expected_type is None or isinstance(value, str):
            continue

        try:
            if expected_type == "integer":
                coerced[key] = int(value)
            elif expected_type == "number":
                coerced[key] = float(value)
            elif expected_type == "boolean":
                low = value.lower()
                if low in _BOOL_TRUTHY:
                    coerced[key] = True
                elif low in _BOOL_FALSY:
                    coerced[key] = False
        except (ValueError, TypeError):
            pass  # Let validation catch it

    return coerced


def x__coerce_types__mutmut_20(
    args: dict[str, Any],
    schema: dict[str, Any],
) -> dict[str, Any]:
    """Best-effort coercion of string values to declared schema types."""
    properties = schema.get("properties", {})
    coerced = dict(args)

    for key, value in coerced.items():
        if key not in properties:
            continue
        prop_schema = properties[key]
        expected_type = prop_schema.get("type")
        if expected_type is None or not isinstance(value, str):
            break

        try:
            if expected_type == "integer":
                coerced[key] = int(value)
            elif expected_type == "number":
                coerced[key] = float(value)
            elif expected_type == "boolean":
                low = value.lower()
                if low in _BOOL_TRUTHY:
                    coerced[key] = True
                elif low in _BOOL_FALSY:
                    coerced[key] = False
        except (ValueError, TypeError):
            pass  # Let validation catch it

    return coerced


def x__coerce_types__mutmut_21(
    args: dict[str, Any],
    schema: dict[str, Any],
) -> dict[str, Any]:
    """Best-effort coercion of string values to declared schema types."""
    properties = schema.get("properties", {})
    coerced = dict(args)

    for key, value in coerced.items():
        if key not in properties:
            continue
        prop_schema = properties[key]
        expected_type = prop_schema.get("type")
        if expected_type is None or not isinstance(value, str):
            continue

        try:
            if expected_type != "integer":
                coerced[key] = int(value)
            elif expected_type == "number":
                coerced[key] = float(value)
            elif expected_type == "boolean":
                low = value.lower()
                if low in _BOOL_TRUTHY:
                    coerced[key] = True
                elif low in _BOOL_FALSY:
                    coerced[key] = False
        except (ValueError, TypeError):
            pass  # Let validation catch it

    return coerced


def x__coerce_types__mutmut_22(
    args: dict[str, Any],
    schema: dict[str, Any],
) -> dict[str, Any]:
    """Best-effort coercion of string values to declared schema types."""
    properties = schema.get("properties", {})
    coerced = dict(args)

    for key, value in coerced.items():
        if key not in properties:
            continue
        prop_schema = properties[key]
        expected_type = prop_schema.get("type")
        if expected_type is None or not isinstance(value, str):
            continue

        try:
            if expected_type == "XXintegerXX":
                coerced[key] = int(value)
            elif expected_type == "number":
                coerced[key] = float(value)
            elif expected_type == "boolean":
                low = value.lower()
                if low in _BOOL_TRUTHY:
                    coerced[key] = True
                elif low in _BOOL_FALSY:
                    coerced[key] = False
        except (ValueError, TypeError):
            pass  # Let validation catch it

    return coerced


def x__coerce_types__mutmut_23(
    args: dict[str, Any],
    schema: dict[str, Any],
) -> dict[str, Any]:
    """Best-effort coercion of string values to declared schema types."""
    properties = schema.get("properties", {})
    coerced = dict(args)

    for key, value in coerced.items():
        if key not in properties:
            continue
        prop_schema = properties[key]
        expected_type = prop_schema.get("type")
        if expected_type is None or not isinstance(value, str):
            continue

        try:
            if expected_type == "INTEGER":
                coerced[key] = int(value)
            elif expected_type == "number":
                coerced[key] = float(value)
            elif expected_type == "boolean":
                low = value.lower()
                if low in _BOOL_TRUTHY:
                    coerced[key] = True
                elif low in _BOOL_FALSY:
                    coerced[key] = False
        except (ValueError, TypeError):
            pass  # Let validation catch it

    return coerced


def x__coerce_types__mutmut_24(
    args: dict[str, Any],
    schema: dict[str, Any],
) -> dict[str, Any]:
    """Best-effort coercion of string values to declared schema types."""
    properties = schema.get("properties", {})
    coerced = dict(args)

    for key, value in coerced.items():
        if key not in properties:
            continue
        prop_schema = properties[key]
        expected_type = prop_schema.get("type")
        if expected_type is None or not isinstance(value, str):
            continue

        try:
            if expected_type == "integer":
                coerced[key] = None
            elif expected_type == "number":
                coerced[key] = float(value)
            elif expected_type == "boolean":
                low = value.lower()
                if low in _BOOL_TRUTHY:
                    coerced[key] = True
                elif low in _BOOL_FALSY:
                    coerced[key] = False
        except (ValueError, TypeError):
            pass  # Let validation catch it

    return coerced


def x__coerce_types__mutmut_25(
    args: dict[str, Any],
    schema: dict[str, Any],
) -> dict[str, Any]:
    """Best-effort coercion of string values to declared schema types."""
    properties = schema.get("properties", {})
    coerced = dict(args)

    for key, value in coerced.items():
        if key not in properties:
            continue
        prop_schema = properties[key]
        expected_type = prop_schema.get("type")
        if expected_type is None or not isinstance(value, str):
            continue

        try:
            if expected_type == "integer":
                coerced[key] = int(None)
            elif expected_type == "number":
                coerced[key] = float(value)
            elif expected_type == "boolean":
                low = value.lower()
                if low in _BOOL_TRUTHY:
                    coerced[key] = True
                elif low in _BOOL_FALSY:
                    coerced[key] = False
        except (ValueError, TypeError):
            pass  # Let validation catch it

    return coerced


def x__coerce_types__mutmut_26(
    args: dict[str, Any],
    schema: dict[str, Any],
) -> dict[str, Any]:
    """Best-effort coercion of string values to declared schema types."""
    properties = schema.get("properties", {})
    coerced = dict(args)

    for key, value in coerced.items():
        if key not in properties:
            continue
        prop_schema = properties[key]
        expected_type = prop_schema.get("type")
        if expected_type is None or not isinstance(value, str):
            continue

        try:
            if expected_type == "integer":
                coerced[key] = int(value)
            elif expected_type != "number":
                coerced[key] = float(value)
            elif expected_type == "boolean":
                low = value.lower()
                if low in _BOOL_TRUTHY:
                    coerced[key] = True
                elif low in _BOOL_FALSY:
                    coerced[key] = False
        except (ValueError, TypeError):
            pass  # Let validation catch it

    return coerced


def x__coerce_types__mutmut_27(
    args: dict[str, Any],
    schema: dict[str, Any],
) -> dict[str, Any]:
    """Best-effort coercion of string values to declared schema types."""
    properties = schema.get("properties", {})
    coerced = dict(args)

    for key, value in coerced.items():
        if key not in properties:
            continue
        prop_schema = properties[key]
        expected_type = prop_schema.get("type")
        if expected_type is None or not isinstance(value, str):
            continue

        try:
            if expected_type == "integer":
                coerced[key] = int(value)
            elif expected_type == "XXnumberXX":
                coerced[key] = float(value)
            elif expected_type == "boolean":
                low = value.lower()
                if low in _BOOL_TRUTHY:
                    coerced[key] = True
                elif low in _BOOL_FALSY:
                    coerced[key] = False
        except (ValueError, TypeError):
            pass  # Let validation catch it

    return coerced


def x__coerce_types__mutmut_28(
    args: dict[str, Any],
    schema: dict[str, Any],
) -> dict[str, Any]:
    """Best-effort coercion of string values to declared schema types."""
    properties = schema.get("properties", {})
    coerced = dict(args)

    for key, value in coerced.items():
        if key not in properties:
            continue
        prop_schema = properties[key]
        expected_type = prop_schema.get("type")
        if expected_type is None or not isinstance(value, str):
            continue

        try:
            if expected_type == "integer":
                coerced[key] = int(value)
            elif expected_type == "NUMBER":
                coerced[key] = float(value)
            elif expected_type == "boolean":
                low = value.lower()
                if low in _BOOL_TRUTHY:
                    coerced[key] = True
                elif low in _BOOL_FALSY:
                    coerced[key] = False
        except (ValueError, TypeError):
            pass  # Let validation catch it

    return coerced


def x__coerce_types__mutmut_29(
    args: dict[str, Any],
    schema: dict[str, Any],
) -> dict[str, Any]:
    """Best-effort coercion of string values to declared schema types."""
    properties = schema.get("properties", {})
    coerced = dict(args)

    for key, value in coerced.items():
        if key not in properties:
            continue
        prop_schema = properties[key]
        expected_type = prop_schema.get("type")
        if expected_type is None or not isinstance(value, str):
            continue

        try:
            if expected_type == "integer":
                coerced[key] = int(value)
            elif expected_type == "number":
                coerced[key] = None
            elif expected_type == "boolean":
                low = value.lower()
                if low in _BOOL_TRUTHY:
                    coerced[key] = True
                elif low in _BOOL_FALSY:
                    coerced[key] = False
        except (ValueError, TypeError):
            pass  # Let validation catch it

    return coerced


def x__coerce_types__mutmut_30(
    args: dict[str, Any],
    schema: dict[str, Any],
) -> dict[str, Any]:
    """Best-effort coercion of string values to declared schema types."""
    properties = schema.get("properties", {})
    coerced = dict(args)

    for key, value in coerced.items():
        if key not in properties:
            continue
        prop_schema = properties[key]
        expected_type = prop_schema.get("type")
        if expected_type is None or not isinstance(value, str):
            continue

        try:
            if expected_type == "integer":
                coerced[key] = int(value)
            elif expected_type == "number":
                coerced[key] = float(None)
            elif expected_type == "boolean":
                low = value.lower()
                if low in _BOOL_TRUTHY:
                    coerced[key] = True
                elif low in _BOOL_FALSY:
                    coerced[key] = False
        except (ValueError, TypeError):
            pass  # Let validation catch it

    return coerced


def x__coerce_types__mutmut_31(
    args: dict[str, Any],
    schema: dict[str, Any],
) -> dict[str, Any]:
    """Best-effort coercion of string values to declared schema types."""
    properties = schema.get("properties", {})
    coerced = dict(args)

    for key, value in coerced.items():
        if key not in properties:
            continue
        prop_schema = properties[key]
        expected_type = prop_schema.get("type")
        if expected_type is None or not isinstance(value, str):
            continue

        try:
            if expected_type == "integer":
                coerced[key] = int(value)
            elif expected_type == "number":
                coerced[key] = float(value)
            elif expected_type != "boolean":
                low = value.lower()
                if low in _BOOL_TRUTHY:
                    coerced[key] = True
                elif low in _BOOL_FALSY:
                    coerced[key] = False
        except (ValueError, TypeError):
            pass  # Let validation catch it

    return coerced


def x__coerce_types__mutmut_32(
    args: dict[str, Any],
    schema: dict[str, Any],
) -> dict[str, Any]:
    """Best-effort coercion of string values to declared schema types."""
    properties = schema.get("properties", {})
    coerced = dict(args)

    for key, value in coerced.items():
        if key not in properties:
            continue
        prop_schema = properties[key]
        expected_type = prop_schema.get("type")
        if expected_type is None or not isinstance(value, str):
            continue

        try:
            if expected_type == "integer":
                coerced[key] = int(value)
            elif expected_type == "number":
                coerced[key] = float(value)
            elif expected_type == "XXbooleanXX":
                low = value.lower()
                if low in _BOOL_TRUTHY:
                    coerced[key] = True
                elif low in _BOOL_FALSY:
                    coerced[key] = False
        except (ValueError, TypeError):
            pass  # Let validation catch it

    return coerced


def x__coerce_types__mutmut_33(
    args: dict[str, Any],
    schema: dict[str, Any],
) -> dict[str, Any]:
    """Best-effort coercion of string values to declared schema types."""
    properties = schema.get("properties", {})
    coerced = dict(args)

    for key, value in coerced.items():
        if key not in properties:
            continue
        prop_schema = properties[key]
        expected_type = prop_schema.get("type")
        if expected_type is None or not isinstance(value, str):
            continue

        try:
            if expected_type == "integer":
                coerced[key] = int(value)
            elif expected_type == "number":
                coerced[key] = float(value)
            elif expected_type == "BOOLEAN":
                low = value.lower()
                if low in _BOOL_TRUTHY:
                    coerced[key] = True
                elif low in _BOOL_FALSY:
                    coerced[key] = False
        except (ValueError, TypeError):
            pass  # Let validation catch it

    return coerced


def x__coerce_types__mutmut_34(
    args: dict[str, Any],
    schema: dict[str, Any],
) -> dict[str, Any]:
    """Best-effort coercion of string values to declared schema types."""
    properties = schema.get("properties", {})
    coerced = dict(args)

    for key, value in coerced.items():
        if key not in properties:
            continue
        prop_schema = properties[key]
        expected_type = prop_schema.get("type")
        if expected_type is None or not isinstance(value, str):
            continue

        try:
            if expected_type == "integer":
                coerced[key] = int(value)
            elif expected_type == "number":
                coerced[key] = float(value)
            elif expected_type == "boolean":
                low = None
                if low in _BOOL_TRUTHY:
                    coerced[key] = True
                elif low in _BOOL_FALSY:
                    coerced[key] = False
        except (ValueError, TypeError):
            pass  # Let validation catch it

    return coerced


def x__coerce_types__mutmut_35(
    args: dict[str, Any],
    schema: dict[str, Any],
) -> dict[str, Any]:
    """Best-effort coercion of string values to declared schema types."""
    properties = schema.get("properties", {})
    coerced = dict(args)

    for key, value in coerced.items():
        if key not in properties:
            continue
        prop_schema = properties[key]
        expected_type = prop_schema.get("type")
        if expected_type is None or not isinstance(value, str):
            continue

        try:
            if expected_type == "integer":
                coerced[key] = int(value)
            elif expected_type == "number":
                coerced[key] = float(value)
            elif expected_type == "boolean":
                low = value.upper()
                if low in _BOOL_TRUTHY:
                    coerced[key] = True
                elif low in _BOOL_FALSY:
                    coerced[key] = False
        except (ValueError, TypeError):
            pass  # Let validation catch it

    return coerced


def x__coerce_types__mutmut_36(
    args: dict[str, Any],
    schema: dict[str, Any],
) -> dict[str, Any]:
    """Best-effort coercion of string values to declared schema types."""
    properties = schema.get("properties", {})
    coerced = dict(args)

    for key, value in coerced.items():
        if key not in properties:
            continue
        prop_schema = properties[key]
        expected_type = prop_schema.get("type")
        if expected_type is None or not isinstance(value, str):
            continue

        try:
            if expected_type == "integer":
                coerced[key] = int(value)
            elif expected_type == "number":
                coerced[key] = float(value)
            elif expected_type == "boolean":
                low = value.lower()
                if low not in _BOOL_TRUTHY:
                    coerced[key] = True
                elif low in _BOOL_FALSY:
                    coerced[key] = False
        except (ValueError, TypeError):
            pass  # Let validation catch it

    return coerced


def x__coerce_types__mutmut_37(
    args: dict[str, Any],
    schema: dict[str, Any],
) -> dict[str, Any]:
    """Best-effort coercion of string values to declared schema types."""
    properties = schema.get("properties", {})
    coerced = dict(args)

    for key, value in coerced.items():
        if key not in properties:
            continue
        prop_schema = properties[key]
        expected_type = prop_schema.get("type")
        if expected_type is None or not isinstance(value, str):
            continue

        try:
            if expected_type == "integer":
                coerced[key] = int(value)
            elif expected_type == "number":
                coerced[key] = float(value)
            elif expected_type == "boolean":
                low = value.lower()
                if low in _BOOL_TRUTHY:
                    coerced[key] = None
                elif low in _BOOL_FALSY:
                    coerced[key] = False
        except (ValueError, TypeError):
            pass  # Let validation catch it

    return coerced


def x__coerce_types__mutmut_38(
    args: dict[str, Any],
    schema: dict[str, Any],
) -> dict[str, Any]:
    """Best-effort coercion of string values to declared schema types."""
    properties = schema.get("properties", {})
    coerced = dict(args)

    for key, value in coerced.items():
        if key not in properties:
            continue
        prop_schema = properties[key]
        expected_type = prop_schema.get("type")
        if expected_type is None or not isinstance(value, str):
            continue

        try:
            if expected_type == "integer":
                coerced[key] = int(value)
            elif expected_type == "number":
                coerced[key] = float(value)
            elif expected_type == "boolean":
                low = value.lower()
                if low in _BOOL_TRUTHY:
                    coerced[key] = False
                elif low in _BOOL_FALSY:
                    coerced[key] = False
        except (ValueError, TypeError):
            pass  # Let validation catch it

    return coerced


def x__coerce_types__mutmut_39(
    args: dict[str, Any],
    schema: dict[str, Any],
) -> dict[str, Any]:
    """Best-effort coercion of string values to declared schema types."""
    properties = schema.get("properties", {})
    coerced = dict(args)

    for key, value in coerced.items():
        if key not in properties:
            continue
        prop_schema = properties[key]
        expected_type = prop_schema.get("type")
        if expected_type is None or not isinstance(value, str):
            continue

        try:
            if expected_type == "integer":
                coerced[key] = int(value)
            elif expected_type == "number":
                coerced[key] = float(value)
            elif expected_type == "boolean":
                low = value.lower()
                if low in _BOOL_TRUTHY:
                    coerced[key] = True
                elif low not in _BOOL_FALSY:
                    coerced[key] = False
        except (ValueError, TypeError):
            pass  # Let validation catch it

    return coerced


def x__coerce_types__mutmut_40(
    args: dict[str, Any],
    schema: dict[str, Any],
) -> dict[str, Any]:
    """Best-effort coercion of string values to declared schema types."""
    properties = schema.get("properties", {})
    coerced = dict(args)

    for key, value in coerced.items():
        if key not in properties:
            continue
        prop_schema = properties[key]
        expected_type = prop_schema.get("type")
        if expected_type is None or not isinstance(value, str):
            continue

        try:
            if expected_type == "integer":
                coerced[key] = int(value)
            elif expected_type == "number":
                coerced[key] = float(value)
            elif expected_type == "boolean":
                low = value.lower()
                if low in _BOOL_TRUTHY:
                    coerced[key] = True
                elif low in _BOOL_FALSY:
                    coerced[key] = None
        except (ValueError, TypeError):
            pass  # Let validation catch it

    return coerced


def x__coerce_types__mutmut_41(
    args: dict[str, Any],
    schema: dict[str, Any],
) -> dict[str, Any]:
    """Best-effort coercion of string values to declared schema types."""
    properties = schema.get("properties", {})
    coerced = dict(args)

    for key, value in coerced.items():
        if key not in properties:
            continue
        prop_schema = properties[key]
        expected_type = prop_schema.get("type")
        if expected_type is None or not isinstance(value, str):
            continue

        try:
            if expected_type == "integer":
                coerced[key] = int(value)
            elif expected_type == "number":
                coerced[key] = float(value)
            elif expected_type == "boolean":
                low = value.lower()
                if low in _BOOL_TRUTHY:
                    coerced[key] = True
                elif low in _BOOL_FALSY:
                    coerced[key] = True
        except (ValueError, TypeError):
            pass  # Let validation catch it

    return coerced

x__coerce_types__mutmut_mutants : ClassVar[MutantDict] = {
'x__coerce_types__mutmut_1': x__coerce_types__mutmut_1, 
    'x__coerce_types__mutmut_2': x__coerce_types__mutmut_2, 
    'x__coerce_types__mutmut_3': x__coerce_types__mutmut_3, 
    'x__coerce_types__mutmut_4': x__coerce_types__mutmut_4, 
    'x__coerce_types__mutmut_5': x__coerce_types__mutmut_5, 
    'x__coerce_types__mutmut_6': x__coerce_types__mutmut_6, 
    'x__coerce_types__mutmut_7': x__coerce_types__mutmut_7, 
    'x__coerce_types__mutmut_8': x__coerce_types__mutmut_8, 
    'x__coerce_types__mutmut_9': x__coerce_types__mutmut_9, 
    'x__coerce_types__mutmut_10': x__coerce_types__mutmut_10, 
    'x__coerce_types__mutmut_11': x__coerce_types__mutmut_11, 
    'x__coerce_types__mutmut_12': x__coerce_types__mutmut_12, 
    'x__coerce_types__mutmut_13': x__coerce_types__mutmut_13, 
    'x__coerce_types__mutmut_14': x__coerce_types__mutmut_14, 
    'x__coerce_types__mutmut_15': x__coerce_types__mutmut_15, 
    'x__coerce_types__mutmut_16': x__coerce_types__mutmut_16, 
    'x__coerce_types__mutmut_17': x__coerce_types__mutmut_17, 
    'x__coerce_types__mutmut_18': x__coerce_types__mutmut_18, 
    'x__coerce_types__mutmut_19': x__coerce_types__mutmut_19, 
    'x__coerce_types__mutmut_20': x__coerce_types__mutmut_20, 
    'x__coerce_types__mutmut_21': x__coerce_types__mutmut_21, 
    'x__coerce_types__mutmut_22': x__coerce_types__mutmut_22, 
    'x__coerce_types__mutmut_23': x__coerce_types__mutmut_23, 
    'x__coerce_types__mutmut_24': x__coerce_types__mutmut_24, 
    'x__coerce_types__mutmut_25': x__coerce_types__mutmut_25, 
    'x__coerce_types__mutmut_26': x__coerce_types__mutmut_26, 
    'x__coerce_types__mutmut_27': x__coerce_types__mutmut_27, 
    'x__coerce_types__mutmut_28': x__coerce_types__mutmut_28, 
    'x__coerce_types__mutmut_29': x__coerce_types__mutmut_29, 
    'x__coerce_types__mutmut_30': x__coerce_types__mutmut_30, 
    'x__coerce_types__mutmut_31': x__coerce_types__mutmut_31, 
    'x__coerce_types__mutmut_32': x__coerce_types__mutmut_32, 
    'x__coerce_types__mutmut_33': x__coerce_types__mutmut_33, 
    'x__coerce_types__mutmut_34': x__coerce_types__mutmut_34, 
    'x__coerce_types__mutmut_35': x__coerce_types__mutmut_35, 
    'x__coerce_types__mutmut_36': x__coerce_types__mutmut_36, 
    'x__coerce_types__mutmut_37': x__coerce_types__mutmut_37, 
    'x__coerce_types__mutmut_38': x__coerce_types__mutmut_38, 
    'x__coerce_types__mutmut_39': x__coerce_types__mutmut_39, 
    'x__coerce_types__mutmut_40': x__coerce_types__mutmut_40, 
    'x__coerce_types__mutmut_41': x__coerce_types__mutmut_41
}

def _coerce_types(*args, **kwargs):
    result = _mutmut_trampoline(x__coerce_types__mutmut_orig, x__coerce_types__mutmut_mutants, args, kwargs)
    return result 

_coerce_types.__signature__ = _mutmut_signature(x__coerce_types__mutmut_orig)
x__coerce_types__mutmut_orig.__name__ = 'x__coerce_types'


# ---------------------------------------------------------------------------
# Schema validation (pure-Python, no external deps for core path)
# ---------------------------------------------------------------------------

def x__validate_against_schema__mutmut_orig(
    args: dict[str, Any],
    schema: dict[str, Any],
    tool_name: str,
) -> list[str]:
    """Validate *args* against a JSON Schema object.

    Uses ``jsonschema`` if available (preferred), otherwise falls back to
    a lightweight built-in checker for ``required``, ``type``, ``enum``,
    ``minimum``/``maximum``, and ``pattern``.
    """
    try:
        return _validate_with_jsonschema(args, schema, tool_name)
    except ImportError:
        logger.debug("jsonschema not available; using built-in validator")
        return _validate_builtin(args, schema, tool_name)


# ---------------------------------------------------------------------------
# Schema validation (pure-Python, no external deps for core path)
# ---------------------------------------------------------------------------

def x__validate_against_schema__mutmut_1(
    args: dict[str, Any],
    schema: dict[str, Any],
    tool_name: str,
) -> list[str]:
    """Validate *args* against a JSON Schema object.

    Uses ``jsonschema`` if available (preferred), otherwise falls back to
    a lightweight built-in checker for ``required``, ``type``, ``enum``,
    ``minimum``/``maximum``, and ``pattern``.
    """
    try:
        return _validate_with_jsonschema(None, schema, tool_name)
    except ImportError:
        logger.debug("jsonschema not available; using built-in validator")
        return _validate_builtin(args, schema, tool_name)


# ---------------------------------------------------------------------------
# Schema validation (pure-Python, no external deps for core path)
# ---------------------------------------------------------------------------

def x__validate_against_schema__mutmut_2(
    args: dict[str, Any],
    schema: dict[str, Any],
    tool_name: str,
) -> list[str]:
    """Validate *args* against a JSON Schema object.

    Uses ``jsonschema`` if available (preferred), otherwise falls back to
    a lightweight built-in checker for ``required``, ``type``, ``enum``,
    ``minimum``/``maximum``, and ``pattern``.
    """
    try:
        return _validate_with_jsonschema(args, None, tool_name)
    except ImportError:
        logger.debug("jsonschema not available; using built-in validator")
        return _validate_builtin(args, schema, tool_name)


# ---------------------------------------------------------------------------
# Schema validation (pure-Python, no external deps for core path)
# ---------------------------------------------------------------------------

def x__validate_against_schema__mutmut_3(
    args: dict[str, Any],
    schema: dict[str, Any],
    tool_name: str,
) -> list[str]:
    """Validate *args* against a JSON Schema object.

    Uses ``jsonschema`` if available (preferred), otherwise falls back to
    a lightweight built-in checker for ``required``, ``type``, ``enum``,
    ``minimum``/``maximum``, and ``pattern``.
    """
    try:
        return _validate_with_jsonschema(args, schema, None)
    except ImportError:
        logger.debug("jsonschema not available; using built-in validator")
        return _validate_builtin(args, schema, tool_name)


# ---------------------------------------------------------------------------
# Schema validation (pure-Python, no external deps for core path)
# ---------------------------------------------------------------------------

def x__validate_against_schema__mutmut_4(
    args: dict[str, Any],
    schema: dict[str, Any],
    tool_name: str,
) -> list[str]:
    """Validate *args* against a JSON Schema object.

    Uses ``jsonschema`` if available (preferred), otherwise falls back to
    a lightweight built-in checker for ``required``, ``type``, ``enum``,
    ``minimum``/``maximum``, and ``pattern``.
    """
    try:
        return _validate_with_jsonschema(schema, tool_name)
    except ImportError:
        logger.debug("jsonschema not available; using built-in validator")
        return _validate_builtin(args, schema, tool_name)


# ---------------------------------------------------------------------------
# Schema validation (pure-Python, no external deps for core path)
# ---------------------------------------------------------------------------

def x__validate_against_schema__mutmut_5(
    args: dict[str, Any],
    schema: dict[str, Any],
    tool_name: str,
) -> list[str]:
    """Validate *args* against a JSON Schema object.

    Uses ``jsonschema`` if available (preferred), otherwise falls back to
    a lightweight built-in checker for ``required``, ``type``, ``enum``,
    ``minimum``/``maximum``, and ``pattern``.
    """
    try:
        return _validate_with_jsonschema(args, tool_name)
    except ImportError:
        logger.debug("jsonschema not available; using built-in validator")
        return _validate_builtin(args, schema, tool_name)


# ---------------------------------------------------------------------------
# Schema validation (pure-Python, no external deps for core path)
# ---------------------------------------------------------------------------

def x__validate_against_schema__mutmut_6(
    args: dict[str, Any],
    schema: dict[str, Any],
    tool_name: str,
) -> list[str]:
    """Validate *args* against a JSON Schema object.

    Uses ``jsonschema`` if available (preferred), otherwise falls back to
    a lightweight built-in checker for ``required``, ``type``, ``enum``,
    ``minimum``/``maximum``, and ``pattern``.
    """
    try:
        return _validate_with_jsonschema(args, schema, )
    except ImportError:
        logger.debug("jsonschema not available; using built-in validator")
        return _validate_builtin(args, schema, tool_name)


# ---------------------------------------------------------------------------
# Schema validation (pure-Python, no external deps for core path)
# ---------------------------------------------------------------------------

def x__validate_against_schema__mutmut_7(
    args: dict[str, Any],
    schema: dict[str, Any],
    tool_name: str,
) -> list[str]:
    """Validate *args* against a JSON Schema object.

    Uses ``jsonschema`` if available (preferred), otherwise falls back to
    a lightweight built-in checker for ``required``, ``type``, ``enum``,
    ``minimum``/``maximum``, and ``pattern``.
    """
    try:
        return _validate_with_jsonschema(args, schema, tool_name)
    except ImportError:
        logger.debug(None)
        return _validate_builtin(args, schema, tool_name)


# ---------------------------------------------------------------------------
# Schema validation (pure-Python, no external deps for core path)
# ---------------------------------------------------------------------------

def x__validate_against_schema__mutmut_8(
    args: dict[str, Any],
    schema: dict[str, Any],
    tool_name: str,
) -> list[str]:
    """Validate *args* against a JSON Schema object.

    Uses ``jsonschema`` if available (preferred), otherwise falls back to
    a lightweight built-in checker for ``required``, ``type``, ``enum``,
    ``minimum``/``maximum``, and ``pattern``.
    """
    try:
        return _validate_with_jsonschema(args, schema, tool_name)
    except ImportError:
        logger.debug("XXjsonschema not available; using built-in validatorXX")
        return _validate_builtin(args, schema, tool_name)


# ---------------------------------------------------------------------------
# Schema validation (pure-Python, no external deps for core path)
# ---------------------------------------------------------------------------

def x__validate_against_schema__mutmut_9(
    args: dict[str, Any],
    schema: dict[str, Any],
    tool_name: str,
) -> list[str]:
    """Validate *args* against a JSON Schema object.

    Uses ``jsonschema`` if available (preferred), otherwise falls back to
    a lightweight built-in checker for ``required``, ``type``, ``enum``,
    ``minimum``/``maximum``, and ``pattern``.
    """
    try:
        return _validate_with_jsonschema(args, schema, tool_name)
    except ImportError:
        logger.debug("JSONSCHEMA NOT AVAILABLE; USING BUILT-IN VALIDATOR")
        return _validate_builtin(args, schema, tool_name)


# ---------------------------------------------------------------------------
# Schema validation (pure-Python, no external deps for core path)
# ---------------------------------------------------------------------------

def x__validate_against_schema__mutmut_10(
    args: dict[str, Any],
    schema: dict[str, Any],
    tool_name: str,
) -> list[str]:
    """Validate *args* against a JSON Schema object.

    Uses ``jsonschema`` if available (preferred), otherwise falls back to
    a lightweight built-in checker for ``required``, ``type``, ``enum``,
    ``minimum``/``maximum``, and ``pattern``.
    """
    try:
        return _validate_with_jsonschema(args, schema, tool_name)
    except ImportError:
        logger.debug("jsonschema not available; using built-in validator")
        return _validate_builtin(None, schema, tool_name)


# ---------------------------------------------------------------------------
# Schema validation (pure-Python, no external deps for core path)
# ---------------------------------------------------------------------------

def x__validate_against_schema__mutmut_11(
    args: dict[str, Any],
    schema: dict[str, Any],
    tool_name: str,
) -> list[str]:
    """Validate *args* against a JSON Schema object.

    Uses ``jsonschema`` if available (preferred), otherwise falls back to
    a lightweight built-in checker for ``required``, ``type``, ``enum``,
    ``minimum``/``maximum``, and ``pattern``.
    """
    try:
        return _validate_with_jsonschema(args, schema, tool_name)
    except ImportError:
        logger.debug("jsonschema not available; using built-in validator")
        return _validate_builtin(args, None, tool_name)


# ---------------------------------------------------------------------------
# Schema validation (pure-Python, no external deps for core path)
# ---------------------------------------------------------------------------

def x__validate_against_schema__mutmut_12(
    args: dict[str, Any],
    schema: dict[str, Any],
    tool_name: str,
) -> list[str]:
    """Validate *args* against a JSON Schema object.

    Uses ``jsonschema`` if available (preferred), otherwise falls back to
    a lightweight built-in checker for ``required``, ``type``, ``enum``,
    ``minimum``/``maximum``, and ``pattern``.
    """
    try:
        return _validate_with_jsonschema(args, schema, tool_name)
    except ImportError:
        logger.debug("jsonschema not available; using built-in validator")
        return _validate_builtin(args, schema, None)


# ---------------------------------------------------------------------------
# Schema validation (pure-Python, no external deps for core path)
# ---------------------------------------------------------------------------

def x__validate_against_schema__mutmut_13(
    args: dict[str, Any],
    schema: dict[str, Any],
    tool_name: str,
) -> list[str]:
    """Validate *args* against a JSON Schema object.

    Uses ``jsonschema`` if available (preferred), otherwise falls back to
    a lightweight built-in checker for ``required``, ``type``, ``enum``,
    ``minimum``/``maximum``, and ``pattern``.
    """
    try:
        return _validate_with_jsonschema(args, schema, tool_name)
    except ImportError:
        logger.debug("jsonschema not available; using built-in validator")
        return _validate_builtin(schema, tool_name)


# ---------------------------------------------------------------------------
# Schema validation (pure-Python, no external deps for core path)
# ---------------------------------------------------------------------------

def x__validate_against_schema__mutmut_14(
    args: dict[str, Any],
    schema: dict[str, Any],
    tool_name: str,
) -> list[str]:
    """Validate *args* against a JSON Schema object.

    Uses ``jsonschema`` if available (preferred), otherwise falls back to
    a lightweight built-in checker for ``required``, ``type``, ``enum``,
    ``minimum``/``maximum``, and ``pattern``.
    """
    try:
        return _validate_with_jsonschema(args, schema, tool_name)
    except ImportError:
        logger.debug("jsonschema not available; using built-in validator")
        return _validate_builtin(args, tool_name)


# ---------------------------------------------------------------------------
# Schema validation (pure-Python, no external deps for core path)
# ---------------------------------------------------------------------------

def x__validate_against_schema__mutmut_15(
    args: dict[str, Any],
    schema: dict[str, Any],
    tool_name: str,
) -> list[str]:
    """Validate *args* against a JSON Schema object.

    Uses ``jsonschema`` if available (preferred), otherwise falls back to
    a lightweight built-in checker for ``required``, ``type``, ``enum``,
    ``minimum``/``maximum``, and ``pattern``.
    """
    try:
        return _validate_with_jsonschema(args, schema, tool_name)
    except ImportError:
        logger.debug("jsonschema not available; using built-in validator")
        return _validate_builtin(args, schema, )

x__validate_against_schema__mutmut_mutants : ClassVar[MutantDict] = {
'x__validate_against_schema__mutmut_1': x__validate_against_schema__mutmut_1, 
    'x__validate_against_schema__mutmut_2': x__validate_against_schema__mutmut_2, 
    'x__validate_against_schema__mutmut_3': x__validate_against_schema__mutmut_3, 
    'x__validate_against_schema__mutmut_4': x__validate_against_schema__mutmut_4, 
    'x__validate_against_schema__mutmut_5': x__validate_against_schema__mutmut_5, 
    'x__validate_against_schema__mutmut_6': x__validate_against_schema__mutmut_6, 
    'x__validate_against_schema__mutmut_7': x__validate_against_schema__mutmut_7, 
    'x__validate_against_schema__mutmut_8': x__validate_against_schema__mutmut_8, 
    'x__validate_against_schema__mutmut_9': x__validate_against_schema__mutmut_9, 
    'x__validate_against_schema__mutmut_10': x__validate_against_schema__mutmut_10, 
    'x__validate_against_schema__mutmut_11': x__validate_against_schema__mutmut_11, 
    'x__validate_against_schema__mutmut_12': x__validate_against_schema__mutmut_12, 
    'x__validate_against_schema__mutmut_13': x__validate_against_schema__mutmut_13, 
    'x__validate_against_schema__mutmut_14': x__validate_against_schema__mutmut_14, 
    'x__validate_against_schema__mutmut_15': x__validate_against_schema__mutmut_15
}

def _validate_against_schema(*args, **kwargs):
    result = _mutmut_trampoline(x__validate_against_schema__mutmut_orig, x__validate_against_schema__mutmut_mutants, args, kwargs)
    return result 

_validate_against_schema.__signature__ = _mutmut_signature(x__validate_against_schema__mutmut_orig)
x__validate_against_schema__mutmut_orig.__name__ = 'x__validate_against_schema'


def x__validate_with_jsonschema__mutmut_orig(
    args: dict[str, Any],
    schema: dict[str, Any],
    tool_name: str,
) -> list[str]:
    """Validate using the ``jsonschema`` library."""
    import jsonschema

    validator = jsonschema.Draft7Validator(schema)
    errors: list[str] = []
    for err in sorted(validator.iter_errors(args), key=lambda e: list(e.path)):
        path = ".".join(str(p) for p in err.absolute_path) or "<root>"
        errors.append(f"{path}: {err.message}")
    return errors


def x__validate_with_jsonschema__mutmut_1(
    args: dict[str, Any],
    schema: dict[str, Any],
    tool_name: str,
) -> list[str]:
    """Validate using the ``jsonschema`` library."""
    import jsonschema

    validator = None
    errors: list[str] = []
    for err in sorted(validator.iter_errors(args), key=lambda e: list(e.path)):
        path = ".".join(str(p) for p in err.absolute_path) or "<root>"
        errors.append(f"{path}: {err.message}")
    return errors


def x__validate_with_jsonschema__mutmut_2(
    args: dict[str, Any],
    schema: dict[str, Any],
    tool_name: str,
) -> list[str]:
    """Validate using the ``jsonschema`` library."""
    import jsonschema

    validator = jsonschema.Draft7Validator(None)
    errors: list[str] = []
    for err in sorted(validator.iter_errors(args), key=lambda e: list(e.path)):
        path = ".".join(str(p) for p in err.absolute_path) or "<root>"
        errors.append(f"{path}: {err.message}")
    return errors


def x__validate_with_jsonschema__mutmut_3(
    args: dict[str, Any],
    schema: dict[str, Any],
    tool_name: str,
) -> list[str]:
    """Validate using the ``jsonschema`` library."""
    import jsonschema

    validator = jsonschema.Draft7Validator(schema)
    errors: list[str] = None
    for err in sorted(validator.iter_errors(args), key=lambda e: list(e.path)):
        path = ".".join(str(p) for p in err.absolute_path) or "<root>"
        errors.append(f"{path}: {err.message}")
    return errors


def x__validate_with_jsonschema__mutmut_4(
    args: dict[str, Any],
    schema: dict[str, Any],
    tool_name: str,
) -> list[str]:
    """Validate using the ``jsonschema`` library."""
    import jsonschema

    validator = jsonschema.Draft7Validator(schema)
    errors: list[str] = []
    for err in sorted(None, key=lambda e: list(e.path)):
        path = ".".join(str(p) for p in err.absolute_path) or "<root>"
        errors.append(f"{path}: {err.message}")
    return errors


def x__validate_with_jsonschema__mutmut_5(
    args: dict[str, Any],
    schema: dict[str, Any],
    tool_name: str,
) -> list[str]:
    """Validate using the ``jsonschema`` library."""
    import jsonschema

    validator = jsonschema.Draft7Validator(schema)
    errors: list[str] = []
    for err in sorted(validator.iter_errors(args), key=None):
        path = ".".join(str(p) for p in err.absolute_path) or "<root>"
        errors.append(f"{path}: {err.message}")
    return errors


def x__validate_with_jsonschema__mutmut_6(
    args: dict[str, Any],
    schema: dict[str, Any],
    tool_name: str,
) -> list[str]:
    """Validate using the ``jsonschema`` library."""
    import jsonschema

    validator = jsonschema.Draft7Validator(schema)
    errors: list[str] = []
    for err in sorted(key=lambda e: list(e.path)):
        path = ".".join(str(p) for p in err.absolute_path) or "<root>"
        errors.append(f"{path}: {err.message}")
    return errors


def x__validate_with_jsonschema__mutmut_7(
    args: dict[str, Any],
    schema: dict[str, Any],
    tool_name: str,
) -> list[str]:
    """Validate using the ``jsonschema`` library."""
    import jsonschema

    validator = jsonschema.Draft7Validator(schema)
    errors: list[str] = []
    for err in sorted(validator.iter_errors(args), ):
        path = ".".join(str(p) for p in err.absolute_path) or "<root>"
        errors.append(f"{path}: {err.message}")
    return errors


def x__validate_with_jsonschema__mutmut_8(
    args: dict[str, Any],
    schema: dict[str, Any],
    tool_name: str,
) -> list[str]:
    """Validate using the ``jsonschema`` library."""
    import jsonschema

    validator = jsonschema.Draft7Validator(schema)
    errors: list[str] = []
    for err in sorted(validator.iter_errors(None), key=lambda e: list(e.path)):
        path = ".".join(str(p) for p in err.absolute_path) or "<root>"
        errors.append(f"{path}: {err.message}")
    return errors


def x__validate_with_jsonschema__mutmut_9(
    args: dict[str, Any],
    schema: dict[str, Any],
    tool_name: str,
) -> list[str]:
    """Validate using the ``jsonschema`` library."""
    import jsonschema

    validator = jsonschema.Draft7Validator(schema)
    errors: list[str] = []
    for err in sorted(validator.iter_errors(args), key=lambda e: None):
        path = ".".join(str(p) for p in err.absolute_path) or "<root>"
        errors.append(f"{path}: {err.message}")
    return errors


def x__validate_with_jsonschema__mutmut_10(
    args: dict[str, Any],
    schema: dict[str, Any],
    tool_name: str,
) -> list[str]:
    """Validate using the ``jsonschema`` library."""
    import jsonschema

    validator = jsonschema.Draft7Validator(schema)
    errors: list[str] = []
    for err in sorted(validator.iter_errors(args), key=lambda e: list(None)):
        path = ".".join(str(p) for p in err.absolute_path) or "<root>"
        errors.append(f"{path}: {err.message}")
    return errors


def x__validate_with_jsonschema__mutmut_11(
    args: dict[str, Any],
    schema: dict[str, Any],
    tool_name: str,
) -> list[str]:
    """Validate using the ``jsonschema`` library."""
    import jsonschema

    validator = jsonschema.Draft7Validator(schema)
    errors: list[str] = []
    for err in sorted(validator.iter_errors(args), key=lambda e: list(e.path)):
        path = None
        errors.append(f"{path}: {err.message}")
    return errors


def x__validate_with_jsonschema__mutmut_12(
    args: dict[str, Any],
    schema: dict[str, Any],
    tool_name: str,
) -> list[str]:
    """Validate using the ``jsonschema`` library."""
    import jsonschema

    validator = jsonschema.Draft7Validator(schema)
    errors: list[str] = []
    for err in sorted(validator.iter_errors(args), key=lambda e: list(e.path)):
        path = ".".join(str(p) for p in err.absolute_path) and "<root>"
        errors.append(f"{path}: {err.message}")
    return errors


def x__validate_with_jsonschema__mutmut_13(
    args: dict[str, Any],
    schema: dict[str, Any],
    tool_name: str,
) -> list[str]:
    """Validate using the ``jsonschema`` library."""
    import jsonschema

    validator = jsonschema.Draft7Validator(schema)
    errors: list[str] = []
    for err in sorted(validator.iter_errors(args), key=lambda e: list(e.path)):
        path = ".".join(None) or "<root>"
        errors.append(f"{path}: {err.message}")
    return errors


def x__validate_with_jsonschema__mutmut_14(
    args: dict[str, Any],
    schema: dict[str, Any],
    tool_name: str,
) -> list[str]:
    """Validate using the ``jsonschema`` library."""
    import jsonschema

    validator = jsonschema.Draft7Validator(schema)
    errors: list[str] = []
    for err in sorted(validator.iter_errors(args), key=lambda e: list(e.path)):
        path = "XX.XX".join(str(p) for p in err.absolute_path) or "<root>"
        errors.append(f"{path}: {err.message}")
    return errors


def x__validate_with_jsonschema__mutmut_15(
    args: dict[str, Any],
    schema: dict[str, Any],
    tool_name: str,
) -> list[str]:
    """Validate using the ``jsonschema`` library."""
    import jsonschema

    validator = jsonschema.Draft7Validator(schema)
    errors: list[str] = []
    for err in sorted(validator.iter_errors(args), key=lambda e: list(e.path)):
        path = ".".join(str(None) for p in err.absolute_path) or "<root>"
        errors.append(f"{path}: {err.message}")
    return errors


def x__validate_with_jsonschema__mutmut_16(
    args: dict[str, Any],
    schema: dict[str, Any],
    tool_name: str,
) -> list[str]:
    """Validate using the ``jsonschema`` library."""
    import jsonschema

    validator = jsonschema.Draft7Validator(schema)
    errors: list[str] = []
    for err in sorted(validator.iter_errors(args), key=lambda e: list(e.path)):
        path = ".".join(str(p) for p in err.absolute_path) or "XX<root>XX"
        errors.append(f"{path}: {err.message}")
    return errors


def x__validate_with_jsonschema__mutmut_17(
    args: dict[str, Any],
    schema: dict[str, Any],
    tool_name: str,
) -> list[str]:
    """Validate using the ``jsonschema`` library."""
    import jsonschema

    validator = jsonschema.Draft7Validator(schema)
    errors: list[str] = []
    for err in sorted(validator.iter_errors(args), key=lambda e: list(e.path)):
        path = ".".join(str(p) for p in err.absolute_path) or "<ROOT>"
        errors.append(f"{path}: {err.message}")
    return errors


def x__validate_with_jsonschema__mutmut_18(
    args: dict[str, Any],
    schema: dict[str, Any],
    tool_name: str,
) -> list[str]:
    """Validate using the ``jsonschema`` library."""
    import jsonschema

    validator = jsonschema.Draft7Validator(schema)
    errors: list[str] = []
    for err in sorted(validator.iter_errors(args), key=lambda e: list(e.path)):
        path = ".".join(str(p) for p in err.absolute_path) or "<root>"
        errors.append(None)
    return errors

x__validate_with_jsonschema__mutmut_mutants : ClassVar[MutantDict] = {
'x__validate_with_jsonschema__mutmut_1': x__validate_with_jsonschema__mutmut_1, 
    'x__validate_with_jsonschema__mutmut_2': x__validate_with_jsonschema__mutmut_2, 
    'x__validate_with_jsonschema__mutmut_3': x__validate_with_jsonschema__mutmut_3, 
    'x__validate_with_jsonschema__mutmut_4': x__validate_with_jsonschema__mutmut_4, 
    'x__validate_with_jsonschema__mutmut_5': x__validate_with_jsonschema__mutmut_5, 
    'x__validate_with_jsonschema__mutmut_6': x__validate_with_jsonschema__mutmut_6, 
    'x__validate_with_jsonschema__mutmut_7': x__validate_with_jsonschema__mutmut_7, 
    'x__validate_with_jsonschema__mutmut_8': x__validate_with_jsonschema__mutmut_8, 
    'x__validate_with_jsonschema__mutmut_9': x__validate_with_jsonschema__mutmut_9, 
    'x__validate_with_jsonschema__mutmut_10': x__validate_with_jsonschema__mutmut_10, 
    'x__validate_with_jsonschema__mutmut_11': x__validate_with_jsonschema__mutmut_11, 
    'x__validate_with_jsonschema__mutmut_12': x__validate_with_jsonschema__mutmut_12, 
    'x__validate_with_jsonschema__mutmut_13': x__validate_with_jsonschema__mutmut_13, 
    'x__validate_with_jsonschema__mutmut_14': x__validate_with_jsonschema__mutmut_14, 
    'x__validate_with_jsonschema__mutmut_15': x__validate_with_jsonschema__mutmut_15, 
    'x__validate_with_jsonschema__mutmut_16': x__validate_with_jsonschema__mutmut_16, 
    'x__validate_with_jsonschema__mutmut_17': x__validate_with_jsonschema__mutmut_17, 
    'x__validate_with_jsonschema__mutmut_18': x__validate_with_jsonschema__mutmut_18
}

def _validate_with_jsonschema(*args, **kwargs):
    result = _mutmut_trampoline(x__validate_with_jsonschema__mutmut_orig, x__validate_with_jsonschema__mutmut_mutants, args, kwargs)
    return result 

_validate_with_jsonschema.__signature__ = _mutmut_signature(x__validate_with_jsonschema__mutmut_orig)
x__validate_with_jsonschema__mutmut_orig.__name__ = 'x__validate_with_jsonschema'


def x__validate_builtin__mutmut_orig(
    args: dict[str, Any],
    schema: dict[str, Any],
    tool_name: str,
) -> list[str]:
    """Lightweight fallback validation without ``jsonschema``."""
    errors: list[str] = []
    properties = schema.get("properties", {})
    required = set(schema.get("required", []))

    # Required field check
    for req in required:
        if req not in args:
            errors.append(f"{req}: required field is missing")

    # Type checks
    _TYPE_MAP: dict[str, tuple[type, ...]] = {
        "string": (str,),
        "integer": (int,),
        "number": (int, float),
        "boolean": (bool,),
        "array": (list,),
        "object": (dict,),
    }

    for key, value in args.items():
        if key not in properties:
            # additionalProperties — skip unknown fields by default
            continue

        prop_schema = properties[key]
        expected = prop_schema.get("type")

        if expected and expected in _TYPE_MAP:
            if not isinstance(value, _TYPE_MAP[expected]):
                errors.append(
                    f"{key}: expected type '{expected}', "
                    f"got '{type(value).__name__}'"
                )
                continue

        # Enum
        enum_values = prop_schema.get("enum")
        if enum_values is not None and value not in enum_values:
            errors.append(
                f"{key}: value {value!r} not in allowed values {enum_values}"
            )

        # Min / max (numeric)
        if isinstance(value, (int, float)):
            mn = prop_schema.get("minimum")
            mx = prop_schema.get("maximum")
            if mn is not None and value < mn:
                errors.append(f"{key}: {value} < minimum {mn}")
            if mx is not None and value > mx:
                errors.append(f"{key}: {value} > maximum {mx}")

        # Pattern (string)
        if isinstance(value, str):
            import re

            pattern = prop_schema.get("pattern")
            if pattern and not re.search(pattern, value):
                errors.append(
                    f"{key}: value {value!r} does not match pattern {pattern!r}"
                )

    return errors


def x__validate_builtin__mutmut_1(
    args: dict[str, Any],
    schema: dict[str, Any],
    tool_name: str,
) -> list[str]:
    """Lightweight fallback validation without ``jsonschema``."""
    errors: list[str] = None
    properties = schema.get("properties", {})
    required = set(schema.get("required", []))

    # Required field check
    for req in required:
        if req not in args:
            errors.append(f"{req}: required field is missing")

    # Type checks
    _TYPE_MAP: dict[str, tuple[type, ...]] = {
        "string": (str,),
        "integer": (int,),
        "number": (int, float),
        "boolean": (bool,),
        "array": (list,),
        "object": (dict,),
    }

    for key, value in args.items():
        if key not in properties:
            # additionalProperties — skip unknown fields by default
            continue

        prop_schema = properties[key]
        expected = prop_schema.get("type")

        if expected and expected in _TYPE_MAP:
            if not isinstance(value, _TYPE_MAP[expected]):
                errors.append(
                    f"{key}: expected type '{expected}', "
                    f"got '{type(value).__name__}'"
                )
                continue

        # Enum
        enum_values = prop_schema.get("enum")
        if enum_values is not None and value not in enum_values:
            errors.append(
                f"{key}: value {value!r} not in allowed values {enum_values}"
            )

        # Min / max (numeric)
        if isinstance(value, (int, float)):
            mn = prop_schema.get("minimum")
            mx = prop_schema.get("maximum")
            if mn is not None and value < mn:
                errors.append(f"{key}: {value} < minimum {mn}")
            if mx is not None and value > mx:
                errors.append(f"{key}: {value} > maximum {mx}")

        # Pattern (string)
        if isinstance(value, str):
            import re

            pattern = prop_schema.get("pattern")
            if pattern and not re.search(pattern, value):
                errors.append(
                    f"{key}: value {value!r} does not match pattern {pattern!r}"
                )

    return errors


def x__validate_builtin__mutmut_2(
    args: dict[str, Any],
    schema: dict[str, Any],
    tool_name: str,
) -> list[str]:
    """Lightweight fallback validation without ``jsonschema``."""
    errors: list[str] = []
    properties = None
    required = set(schema.get("required", []))

    # Required field check
    for req in required:
        if req not in args:
            errors.append(f"{req}: required field is missing")

    # Type checks
    _TYPE_MAP: dict[str, tuple[type, ...]] = {
        "string": (str,),
        "integer": (int,),
        "number": (int, float),
        "boolean": (bool,),
        "array": (list,),
        "object": (dict,),
    }

    for key, value in args.items():
        if key not in properties:
            # additionalProperties — skip unknown fields by default
            continue

        prop_schema = properties[key]
        expected = prop_schema.get("type")

        if expected and expected in _TYPE_MAP:
            if not isinstance(value, _TYPE_MAP[expected]):
                errors.append(
                    f"{key}: expected type '{expected}', "
                    f"got '{type(value).__name__}'"
                )
                continue

        # Enum
        enum_values = prop_schema.get("enum")
        if enum_values is not None and value not in enum_values:
            errors.append(
                f"{key}: value {value!r} not in allowed values {enum_values}"
            )

        # Min / max (numeric)
        if isinstance(value, (int, float)):
            mn = prop_schema.get("minimum")
            mx = prop_schema.get("maximum")
            if mn is not None and value < mn:
                errors.append(f"{key}: {value} < minimum {mn}")
            if mx is not None and value > mx:
                errors.append(f"{key}: {value} > maximum {mx}")

        # Pattern (string)
        if isinstance(value, str):
            import re

            pattern = prop_schema.get("pattern")
            if pattern and not re.search(pattern, value):
                errors.append(
                    f"{key}: value {value!r} does not match pattern {pattern!r}"
                )

    return errors


def x__validate_builtin__mutmut_3(
    args: dict[str, Any],
    schema: dict[str, Any],
    tool_name: str,
) -> list[str]:
    """Lightweight fallback validation without ``jsonschema``."""
    errors: list[str] = []
    properties = schema.get(None, {})
    required = set(schema.get("required", []))

    # Required field check
    for req in required:
        if req not in args:
            errors.append(f"{req}: required field is missing")

    # Type checks
    _TYPE_MAP: dict[str, tuple[type, ...]] = {
        "string": (str,),
        "integer": (int,),
        "number": (int, float),
        "boolean": (bool,),
        "array": (list,),
        "object": (dict,),
    }

    for key, value in args.items():
        if key not in properties:
            # additionalProperties — skip unknown fields by default
            continue

        prop_schema = properties[key]
        expected = prop_schema.get("type")

        if expected and expected in _TYPE_MAP:
            if not isinstance(value, _TYPE_MAP[expected]):
                errors.append(
                    f"{key}: expected type '{expected}', "
                    f"got '{type(value).__name__}'"
                )
                continue

        # Enum
        enum_values = prop_schema.get("enum")
        if enum_values is not None and value not in enum_values:
            errors.append(
                f"{key}: value {value!r} not in allowed values {enum_values}"
            )

        # Min / max (numeric)
        if isinstance(value, (int, float)):
            mn = prop_schema.get("minimum")
            mx = prop_schema.get("maximum")
            if mn is not None and value < mn:
                errors.append(f"{key}: {value} < minimum {mn}")
            if mx is not None and value > mx:
                errors.append(f"{key}: {value} > maximum {mx}")

        # Pattern (string)
        if isinstance(value, str):
            import re

            pattern = prop_schema.get("pattern")
            if pattern and not re.search(pattern, value):
                errors.append(
                    f"{key}: value {value!r} does not match pattern {pattern!r}"
                )

    return errors


def x__validate_builtin__mutmut_4(
    args: dict[str, Any],
    schema: dict[str, Any],
    tool_name: str,
) -> list[str]:
    """Lightweight fallback validation without ``jsonschema``."""
    errors: list[str] = []
    properties = schema.get("properties", None)
    required = set(schema.get("required", []))

    # Required field check
    for req in required:
        if req not in args:
            errors.append(f"{req}: required field is missing")

    # Type checks
    _TYPE_MAP: dict[str, tuple[type, ...]] = {
        "string": (str,),
        "integer": (int,),
        "number": (int, float),
        "boolean": (bool,),
        "array": (list,),
        "object": (dict,),
    }

    for key, value in args.items():
        if key not in properties:
            # additionalProperties — skip unknown fields by default
            continue

        prop_schema = properties[key]
        expected = prop_schema.get("type")

        if expected and expected in _TYPE_MAP:
            if not isinstance(value, _TYPE_MAP[expected]):
                errors.append(
                    f"{key}: expected type '{expected}', "
                    f"got '{type(value).__name__}'"
                )
                continue

        # Enum
        enum_values = prop_schema.get("enum")
        if enum_values is not None and value not in enum_values:
            errors.append(
                f"{key}: value {value!r} not in allowed values {enum_values}"
            )

        # Min / max (numeric)
        if isinstance(value, (int, float)):
            mn = prop_schema.get("minimum")
            mx = prop_schema.get("maximum")
            if mn is not None and value < mn:
                errors.append(f"{key}: {value} < minimum {mn}")
            if mx is not None and value > mx:
                errors.append(f"{key}: {value} > maximum {mx}")

        # Pattern (string)
        if isinstance(value, str):
            import re

            pattern = prop_schema.get("pattern")
            if pattern and not re.search(pattern, value):
                errors.append(
                    f"{key}: value {value!r} does not match pattern {pattern!r}"
                )

    return errors


def x__validate_builtin__mutmut_5(
    args: dict[str, Any],
    schema: dict[str, Any],
    tool_name: str,
) -> list[str]:
    """Lightweight fallback validation without ``jsonschema``."""
    errors: list[str] = []
    properties = schema.get({})
    required = set(schema.get("required", []))

    # Required field check
    for req in required:
        if req not in args:
            errors.append(f"{req}: required field is missing")

    # Type checks
    _TYPE_MAP: dict[str, tuple[type, ...]] = {
        "string": (str,),
        "integer": (int,),
        "number": (int, float),
        "boolean": (bool,),
        "array": (list,),
        "object": (dict,),
    }

    for key, value in args.items():
        if key not in properties:
            # additionalProperties — skip unknown fields by default
            continue

        prop_schema = properties[key]
        expected = prop_schema.get("type")

        if expected and expected in _TYPE_MAP:
            if not isinstance(value, _TYPE_MAP[expected]):
                errors.append(
                    f"{key}: expected type '{expected}', "
                    f"got '{type(value).__name__}'"
                )
                continue

        # Enum
        enum_values = prop_schema.get("enum")
        if enum_values is not None and value not in enum_values:
            errors.append(
                f"{key}: value {value!r} not in allowed values {enum_values}"
            )

        # Min / max (numeric)
        if isinstance(value, (int, float)):
            mn = prop_schema.get("minimum")
            mx = prop_schema.get("maximum")
            if mn is not None and value < mn:
                errors.append(f"{key}: {value} < minimum {mn}")
            if mx is not None and value > mx:
                errors.append(f"{key}: {value} > maximum {mx}")

        # Pattern (string)
        if isinstance(value, str):
            import re

            pattern = prop_schema.get("pattern")
            if pattern and not re.search(pattern, value):
                errors.append(
                    f"{key}: value {value!r} does not match pattern {pattern!r}"
                )

    return errors


def x__validate_builtin__mutmut_6(
    args: dict[str, Any],
    schema: dict[str, Any],
    tool_name: str,
) -> list[str]:
    """Lightweight fallback validation without ``jsonschema``."""
    errors: list[str] = []
    properties = schema.get("properties", )
    required = set(schema.get("required", []))

    # Required field check
    for req in required:
        if req not in args:
            errors.append(f"{req}: required field is missing")

    # Type checks
    _TYPE_MAP: dict[str, tuple[type, ...]] = {
        "string": (str,),
        "integer": (int,),
        "number": (int, float),
        "boolean": (bool,),
        "array": (list,),
        "object": (dict,),
    }

    for key, value in args.items():
        if key not in properties:
            # additionalProperties — skip unknown fields by default
            continue

        prop_schema = properties[key]
        expected = prop_schema.get("type")

        if expected and expected in _TYPE_MAP:
            if not isinstance(value, _TYPE_MAP[expected]):
                errors.append(
                    f"{key}: expected type '{expected}', "
                    f"got '{type(value).__name__}'"
                )
                continue

        # Enum
        enum_values = prop_schema.get("enum")
        if enum_values is not None and value not in enum_values:
            errors.append(
                f"{key}: value {value!r} not in allowed values {enum_values}"
            )

        # Min / max (numeric)
        if isinstance(value, (int, float)):
            mn = prop_schema.get("minimum")
            mx = prop_schema.get("maximum")
            if mn is not None and value < mn:
                errors.append(f"{key}: {value} < minimum {mn}")
            if mx is not None and value > mx:
                errors.append(f"{key}: {value} > maximum {mx}")

        # Pattern (string)
        if isinstance(value, str):
            import re

            pattern = prop_schema.get("pattern")
            if pattern and not re.search(pattern, value):
                errors.append(
                    f"{key}: value {value!r} does not match pattern {pattern!r}"
                )

    return errors


def x__validate_builtin__mutmut_7(
    args: dict[str, Any],
    schema: dict[str, Any],
    tool_name: str,
) -> list[str]:
    """Lightweight fallback validation without ``jsonschema``."""
    errors: list[str] = []
    properties = schema.get("XXpropertiesXX", {})
    required = set(schema.get("required", []))

    # Required field check
    for req in required:
        if req not in args:
            errors.append(f"{req}: required field is missing")

    # Type checks
    _TYPE_MAP: dict[str, tuple[type, ...]] = {
        "string": (str,),
        "integer": (int,),
        "number": (int, float),
        "boolean": (bool,),
        "array": (list,),
        "object": (dict,),
    }

    for key, value in args.items():
        if key not in properties:
            # additionalProperties — skip unknown fields by default
            continue

        prop_schema = properties[key]
        expected = prop_schema.get("type")

        if expected and expected in _TYPE_MAP:
            if not isinstance(value, _TYPE_MAP[expected]):
                errors.append(
                    f"{key}: expected type '{expected}', "
                    f"got '{type(value).__name__}'"
                )
                continue

        # Enum
        enum_values = prop_schema.get("enum")
        if enum_values is not None and value not in enum_values:
            errors.append(
                f"{key}: value {value!r} not in allowed values {enum_values}"
            )

        # Min / max (numeric)
        if isinstance(value, (int, float)):
            mn = prop_schema.get("minimum")
            mx = prop_schema.get("maximum")
            if mn is not None and value < mn:
                errors.append(f"{key}: {value} < minimum {mn}")
            if mx is not None and value > mx:
                errors.append(f"{key}: {value} > maximum {mx}")

        # Pattern (string)
        if isinstance(value, str):
            import re

            pattern = prop_schema.get("pattern")
            if pattern and not re.search(pattern, value):
                errors.append(
                    f"{key}: value {value!r} does not match pattern {pattern!r}"
                )

    return errors


def x__validate_builtin__mutmut_8(
    args: dict[str, Any],
    schema: dict[str, Any],
    tool_name: str,
) -> list[str]:
    """Lightweight fallback validation without ``jsonschema``."""
    errors: list[str] = []
    properties = schema.get("PROPERTIES", {})
    required = set(schema.get("required", []))

    # Required field check
    for req in required:
        if req not in args:
            errors.append(f"{req}: required field is missing")

    # Type checks
    _TYPE_MAP: dict[str, tuple[type, ...]] = {
        "string": (str,),
        "integer": (int,),
        "number": (int, float),
        "boolean": (bool,),
        "array": (list,),
        "object": (dict,),
    }

    for key, value in args.items():
        if key not in properties:
            # additionalProperties — skip unknown fields by default
            continue

        prop_schema = properties[key]
        expected = prop_schema.get("type")

        if expected and expected in _TYPE_MAP:
            if not isinstance(value, _TYPE_MAP[expected]):
                errors.append(
                    f"{key}: expected type '{expected}', "
                    f"got '{type(value).__name__}'"
                )
                continue

        # Enum
        enum_values = prop_schema.get("enum")
        if enum_values is not None and value not in enum_values:
            errors.append(
                f"{key}: value {value!r} not in allowed values {enum_values}"
            )

        # Min / max (numeric)
        if isinstance(value, (int, float)):
            mn = prop_schema.get("minimum")
            mx = prop_schema.get("maximum")
            if mn is not None and value < mn:
                errors.append(f"{key}: {value} < minimum {mn}")
            if mx is not None and value > mx:
                errors.append(f"{key}: {value} > maximum {mx}")

        # Pattern (string)
        if isinstance(value, str):
            import re

            pattern = prop_schema.get("pattern")
            if pattern and not re.search(pattern, value):
                errors.append(
                    f"{key}: value {value!r} does not match pattern {pattern!r}"
                )

    return errors


def x__validate_builtin__mutmut_9(
    args: dict[str, Any],
    schema: dict[str, Any],
    tool_name: str,
) -> list[str]:
    """Lightweight fallback validation without ``jsonschema``."""
    errors: list[str] = []
    properties = schema.get("properties", {})
    required = None

    # Required field check
    for req in required:
        if req not in args:
            errors.append(f"{req}: required field is missing")

    # Type checks
    _TYPE_MAP: dict[str, tuple[type, ...]] = {
        "string": (str,),
        "integer": (int,),
        "number": (int, float),
        "boolean": (bool,),
        "array": (list,),
        "object": (dict,),
    }

    for key, value in args.items():
        if key not in properties:
            # additionalProperties — skip unknown fields by default
            continue

        prop_schema = properties[key]
        expected = prop_schema.get("type")

        if expected and expected in _TYPE_MAP:
            if not isinstance(value, _TYPE_MAP[expected]):
                errors.append(
                    f"{key}: expected type '{expected}', "
                    f"got '{type(value).__name__}'"
                )
                continue

        # Enum
        enum_values = prop_schema.get("enum")
        if enum_values is not None and value not in enum_values:
            errors.append(
                f"{key}: value {value!r} not in allowed values {enum_values}"
            )

        # Min / max (numeric)
        if isinstance(value, (int, float)):
            mn = prop_schema.get("minimum")
            mx = prop_schema.get("maximum")
            if mn is not None and value < mn:
                errors.append(f"{key}: {value} < minimum {mn}")
            if mx is not None and value > mx:
                errors.append(f"{key}: {value} > maximum {mx}")

        # Pattern (string)
        if isinstance(value, str):
            import re

            pattern = prop_schema.get("pattern")
            if pattern and not re.search(pattern, value):
                errors.append(
                    f"{key}: value {value!r} does not match pattern {pattern!r}"
                )

    return errors


def x__validate_builtin__mutmut_10(
    args: dict[str, Any],
    schema: dict[str, Any],
    tool_name: str,
) -> list[str]:
    """Lightweight fallback validation without ``jsonschema``."""
    errors: list[str] = []
    properties = schema.get("properties", {})
    required = set(None)

    # Required field check
    for req in required:
        if req not in args:
            errors.append(f"{req}: required field is missing")

    # Type checks
    _TYPE_MAP: dict[str, tuple[type, ...]] = {
        "string": (str,),
        "integer": (int,),
        "number": (int, float),
        "boolean": (bool,),
        "array": (list,),
        "object": (dict,),
    }

    for key, value in args.items():
        if key not in properties:
            # additionalProperties — skip unknown fields by default
            continue

        prop_schema = properties[key]
        expected = prop_schema.get("type")

        if expected and expected in _TYPE_MAP:
            if not isinstance(value, _TYPE_MAP[expected]):
                errors.append(
                    f"{key}: expected type '{expected}', "
                    f"got '{type(value).__name__}'"
                )
                continue

        # Enum
        enum_values = prop_schema.get("enum")
        if enum_values is not None and value not in enum_values:
            errors.append(
                f"{key}: value {value!r} not in allowed values {enum_values}"
            )

        # Min / max (numeric)
        if isinstance(value, (int, float)):
            mn = prop_schema.get("minimum")
            mx = prop_schema.get("maximum")
            if mn is not None and value < mn:
                errors.append(f"{key}: {value} < minimum {mn}")
            if mx is not None and value > mx:
                errors.append(f"{key}: {value} > maximum {mx}")

        # Pattern (string)
        if isinstance(value, str):
            import re

            pattern = prop_schema.get("pattern")
            if pattern and not re.search(pattern, value):
                errors.append(
                    f"{key}: value {value!r} does not match pattern {pattern!r}"
                )

    return errors


def x__validate_builtin__mutmut_11(
    args: dict[str, Any],
    schema: dict[str, Any],
    tool_name: str,
) -> list[str]:
    """Lightweight fallback validation without ``jsonschema``."""
    errors: list[str] = []
    properties = schema.get("properties", {})
    required = set(schema.get(None, []))

    # Required field check
    for req in required:
        if req not in args:
            errors.append(f"{req}: required field is missing")

    # Type checks
    _TYPE_MAP: dict[str, tuple[type, ...]] = {
        "string": (str,),
        "integer": (int,),
        "number": (int, float),
        "boolean": (bool,),
        "array": (list,),
        "object": (dict,),
    }

    for key, value in args.items():
        if key not in properties:
            # additionalProperties — skip unknown fields by default
            continue

        prop_schema = properties[key]
        expected = prop_schema.get("type")

        if expected and expected in _TYPE_MAP:
            if not isinstance(value, _TYPE_MAP[expected]):
                errors.append(
                    f"{key}: expected type '{expected}', "
                    f"got '{type(value).__name__}'"
                )
                continue

        # Enum
        enum_values = prop_schema.get("enum")
        if enum_values is not None and value not in enum_values:
            errors.append(
                f"{key}: value {value!r} not in allowed values {enum_values}"
            )

        # Min / max (numeric)
        if isinstance(value, (int, float)):
            mn = prop_schema.get("minimum")
            mx = prop_schema.get("maximum")
            if mn is not None and value < mn:
                errors.append(f"{key}: {value} < minimum {mn}")
            if mx is not None and value > mx:
                errors.append(f"{key}: {value} > maximum {mx}")

        # Pattern (string)
        if isinstance(value, str):
            import re

            pattern = prop_schema.get("pattern")
            if pattern and not re.search(pattern, value):
                errors.append(
                    f"{key}: value {value!r} does not match pattern {pattern!r}"
                )

    return errors


def x__validate_builtin__mutmut_12(
    args: dict[str, Any],
    schema: dict[str, Any],
    tool_name: str,
) -> list[str]:
    """Lightweight fallback validation without ``jsonschema``."""
    errors: list[str] = []
    properties = schema.get("properties", {})
    required = set(schema.get("required", None))

    # Required field check
    for req in required:
        if req not in args:
            errors.append(f"{req}: required field is missing")

    # Type checks
    _TYPE_MAP: dict[str, tuple[type, ...]] = {
        "string": (str,),
        "integer": (int,),
        "number": (int, float),
        "boolean": (bool,),
        "array": (list,),
        "object": (dict,),
    }

    for key, value in args.items():
        if key not in properties:
            # additionalProperties — skip unknown fields by default
            continue

        prop_schema = properties[key]
        expected = prop_schema.get("type")

        if expected and expected in _TYPE_MAP:
            if not isinstance(value, _TYPE_MAP[expected]):
                errors.append(
                    f"{key}: expected type '{expected}', "
                    f"got '{type(value).__name__}'"
                )
                continue

        # Enum
        enum_values = prop_schema.get("enum")
        if enum_values is not None and value not in enum_values:
            errors.append(
                f"{key}: value {value!r} not in allowed values {enum_values}"
            )

        # Min / max (numeric)
        if isinstance(value, (int, float)):
            mn = prop_schema.get("minimum")
            mx = prop_schema.get("maximum")
            if mn is not None and value < mn:
                errors.append(f"{key}: {value} < minimum {mn}")
            if mx is not None and value > mx:
                errors.append(f"{key}: {value} > maximum {mx}")

        # Pattern (string)
        if isinstance(value, str):
            import re

            pattern = prop_schema.get("pattern")
            if pattern and not re.search(pattern, value):
                errors.append(
                    f"{key}: value {value!r} does not match pattern {pattern!r}"
                )

    return errors


def x__validate_builtin__mutmut_13(
    args: dict[str, Any],
    schema: dict[str, Any],
    tool_name: str,
) -> list[str]:
    """Lightweight fallback validation without ``jsonschema``."""
    errors: list[str] = []
    properties = schema.get("properties", {})
    required = set(schema.get([]))

    # Required field check
    for req in required:
        if req not in args:
            errors.append(f"{req}: required field is missing")

    # Type checks
    _TYPE_MAP: dict[str, tuple[type, ...]] = {
        "string": (str,),
        "integer": (int,),
        "number": (int, float),
        "boolean": (bool,),
        "array": (list,),
        "object": (dict,),
    }

    for key, value in args.items():
        if key not in properties:
            # additionalProperties — skip unknown fields by default
            continue

        prop_schema = properties[key]
        expected = prop_schema.get("type")

        if expected and expected in _TYPE_MAP:
            if not isinstance(value, _TYPE_MAP[expected]):
                errors.append(
                    f"{key}: expected type '{expected}', "
                    f"got '{type(value).__name__}'"
                )
                continue

        # Enum
        enum_values = prop_schema.get("enum")
        if enum_values is not None and value not in enum_values:
            errors.append(
                f"{key}: value {value!r} not in allowed values {enum_values}"
            )

        # Min / max (numeric)
        if isinstance(value, (int, float)):
            mn = prop_schema.get("minimum")
            mx = prop_schema.get("maximum")
            if mn is not None and value < mn:
                errors.append(f"{key}: {value} < minimum {mn}")
            if mx is not None and value > mx:
                errors.append(f"{key}: {value} > maximum {mx}")

        # Pattern (string)
        if isinstance(value, str):
            import re

            pattern = prop_schema.get("pattern")
            if pattern and not re.search(pattern, value):
                errors.append(
                    f"{key}: value {value!r} does not match pattern {pattern!r}"
                )

    return errors


def x__validate_builtin__mutmut_14(
    args: dict[str, Any],
    schema: dict[str, Any],
    tool_name: str,
) -> list[str]:
    """Lightweight fallback validation without ``jsonschema``."""
    errors: list[str] = []
    properties = schema.get("properties", {})
    required = set(schema.get("required", ))

    # Required field check
    for req in required:
        if req not in args:
            errors.append(f"{req}: required field is missing")

    # Type checks
    _TYPE_MAP: dict[str, tuple[type, ...]] = {
        "string": (str,),
        "integer": (int,),
        "number": (int, float),
        "boolean": (bool,),
        "array": (list,),
        "object": (dict,),
    }

    for key, value in args.items():
        if key not in properties:
            # additionalProperties — skip unknown fields by default
            continue

        prop_schema = properties[key]
        expected = prop_schema.get("type")

        if expected and expected in _TYPE_MAP:
            if not isinstance(value, _TYPE_MAP[expected]):
                errors.append(
                    f"{key}: expected type '{expected}', "
                    f"got '{type(value).__name__}'"
                )
                continue

        # Enum
        enum_values = prop_schema.get("enum")
        if enum_values is not None and value not in enum_values:
            errors.append(
                f"{key}: value {value!r} not in allowed values {enum_values}"
            )

        # Min / max (numeric)
        if isinstance(value, (int, float)):
            mn = prop_schema.get("minimum")
            mx = prop_schema.get("maximum")
            if mn is not None and value < mn:
                errors.append(f"{key}: {value} < minimum {mn}")
            if mx is not None and value > mx:
                errors.append(f"{key}: {value} > maximum {mx}")

        # Pattern (string)
        if isinstance(value, str):
            import re

            pattern = prop_schema.get("pattern")
            if pattern and not re.search(pattern, value):
                errors.append(
                    f"{key}: value {value!r} does not match pattern {pattern!r}"
                )

    return errors


def x__validate_builtin__mutmut_15(
    args: dict[str, Any],
    schema: dict[str, Any],
    tool_name: str,
) -> list[str]:
    """Lightweight fallback validation without ``jsonschema``."""
    errors: list[str] = []
    properties = schema.get("properties", {})
    required = set(schema.get("XXrequiredXX", []))

    # Required field check
    for req in required:
        if req not in args:
            errors.append(f"{req}: required field is missing")

    # Type checks
    _TYPE_MAP: dict[str, tuple[type, ...]] = {
        "string": (str,),
        "integer": (int,),
        "number": (int, float),
        "boolean": (bool,),
        "array": (list,),
        "object": (dict,),
    }

    for key, value in args.items():
        if key not in properties:
            # additionalProperties — skip unknown fields by default
            continue

        prop_schema = properties[key]
        expected = prop_schema.get("type")

        if expected and expected in _TYPE_MAP:
            if not isinstance(value, _TYPE_MAP[expected]):
                errors.append(
                    f"{key}: expected type '{expected}', "
                    f"got '{type(value).__name__}'"
                )
                continue

        # Enum
        enum_values = prop_schema.get("enum")
        if enum_values is not None and value not in enum_values:
            errors.append(
                f"{key}: value {value!r} not in allowed values {enum_values}"
            )

        # Min / max (numeric)
        if isinstance(value, (int, float)):
            mn = prop_schema.get("minimum")
            mx = prop_schema.get("maximum")
            if mn is not None and value < mn:
                errors.append(f"{key}: {value} < minimum {mn}")
            if mx is not None and value > mx:
                errors.append(f"{key}: {value} > maximum {mx}")

        # Pattern (string)
        if isinstance(value, str):
            import re

            pattern = prop_schema.get("pattern")
            if pattern and not re.search(pattern, value):
                errors.append(
                    f"{key}: value {value!r} does not match pattern {pattern!r}"
                )

    return errors


def x__validate_builtin__mutmut_16(
    args: dict[str, Any],
    schema: dict[str, Any],
    tool_name: str,
) -> list[str]:
    """Lightweight fallback validation without ``jsonschema``."""
    errors: list[str] = []
    properties = schema.get("properties", {})
    required = set(schema.get("REQUIRED", []))

    # Required field check
    for req in required:
        if req not in args:
            errors.append(f"{req}: required field is missing")

    # Type checks
    _TYPE_MAP: dict[str, tuple[type, ...]] = {
        "string": (str,),
        "integer": (int,),
        "number": (int, float),
        "boolean": (bool,),
        "array": (list,),
        "object": (dict,),
    }

    for key, value in args.items():
        if key not in properties:
            # additionalProperties — skip unknown fields by default
            continue

        prop_schema = properties[key]
        expected = prop_schema.get("type")

        if expected and expected in _TYPE_MAP:
            if not isinstance(value, _TYPE_MAP[expected]):
                errors.append(
                    f"{key}: expected type '{expected}', "
                    f"got '{type(value).__name__}'"
                )
                continue

        # Enum
        enum_values = prop_schema.get("enum")
        if enum_values is not None and value not in enum_values:
            errors.append(
                f"{key}: value {value!r} not in allowed values {enum_values}"
            )

        # Min / max (numeric)
        if isinstance(value, (int, float)):
            mn = prop_schema.get("minimum")
            mx = prop_schema.get("maximum")
            if mn is not None and value < mn:
                errors.append(f"{key}: {value} < minimum {mn}")
            if mx is not None and value > mx:
                errors.append(f"{key}: {value} > maximum {mx}")

        # Pattern (string)
        if isinstance(value, str):
            import re

            pattern = prop_schema.get("pattern")
            if pattern and not re.search(pattern, value):
                errors.append(
                    f"{key}: value {value!r} does not match pattern {pattern!r}"
                )

    return errors


def x__validate_builtin__mutmut_17(
    args: dict[str, Any],
    schema: dict[str, Any],
    tool_name: str,
) -> list[str]:
    """Lightweight fallback validation without ``jsonschema``."""
    errors: list[str] = []
    properties = schema.get("properties", {})
    required = set(schema.get("required", []))

    # Required field check
    for req in required:
        if req in args:
            errors.append(f"{req}: required field is missing")

    # Type checks
    _TYPE_MAP: dict[str, tuple[type, ...]] = {
        "string": (str,),
        "integer": (int,),
        "number": (int, float),
        "boolean": (bool,),
        "array": (list,),
        "object": (dict,),
    }

    for key, value in args.items():
        if key not in properties:
            # additionalProperties — skip unknown fields by default
            continue

        prop_schema = properties[key]
        expected = prop_schema.get("type")

        if expected and expected in _TYPE_MAP:
            if not isinstance(value, _TYPE_MAP[expected]):
                errors.append(
                    f"{key}: expected type '{expected}', "
                    f"got '{type(value).__name__}'"
                )
                continue

        # Enum
        enum_values = prop_schema.get("enum")
        if enum_values is not None and value not in enum_values:
            errors.append(
                f"{key}: value {value!r} not in allowed values {enum_values}"
            )

        # Min / max (numeric)
        if isinstance(value, (int, float)):
            mn = prop_schema.get("minimum")
            mx = prop_schema.get("maximum")
            if mn is not None and value < mn:
                errors.append(f"{key}: {value} < minimum {mn}")
            if mx is not None and value > mx:
                errors.append(f"{key}: {value} > maximum {mx}")

        # Pattern (string)
        if isinstance(value, str):
            import re

            pattern = prop_schema.get("pattern")
            if pattern and not re.search(pattern, value):
                errors.append(
                    f"{key}: value {value!r} does not match pattern {pattern!r}"
                )

    return errors


def x__validate_builtin__mutmut_18(
    args: dict[str, Any],
    schema: dict[str, Any],
    tool_name: str,
) -> list[str]:
    """Lightweight fallback validation without ``jsonschema``."""
    errors: list[str] = []
    properties = schema.get("properties", {})
    required = set(schema.get("required", []))

    # Required field check
    for req in required:
        if req not in args:
            errors.append(None)

    # Type checks
    _TYPE_MAP: dict[str, tuple[type, ...]] = {
        "string": (str,),
        "integer": (int,),
        "number": (int, float),
        "boolean": (bool,),
        "array": (list,),
        "object": (dict,),
    }

    for key, value in args.items():
        if key not in properties:
            # additionalProperties — skip unknown fields by default
            continue

        prop_schema = properties[key]
        expected = prop_schema.get("type")

        if expected and expected in _TYPE_MAP:
            if not isinstance(value, _TYPE_MAP[expected]):
                errors.append(
                    f"{key}: expected type '{expected}', "
                    f"got '{type(value).__name__}'"
                )
                continue

        # Enum
        enum_values = prop_schema.get("enum")
        if enum_values is not None and value not in enum_values:
            errors.append(
                f"{key}: value {value!r} not in allowed values {enum_values}"
            )

        # Min / max (numeric)
        if isinstance(value, (int, float)):
            mn = prop_schema.get("minimum")
            mx = prop_schema.get("maximum")
            if mn is not None and value < mn:
                errors.append(f"{key}: {value} < minimum {mn}")
            if mx is not None and value > mx:
                errors.append(f"{key}: {value} > maximum {mx}")

        # Pattern (string)
        if isinstance(value, str):
            import re

            pattern = prop_schema.get("pattern")
            if pattern and not re.search(pattern, value):
                errors.append(
                    f"{key}: value {value!r} does not match pattern {pattern!r}"
                )

    return errors


def x__validate_builtin__mutmut_19(
    args: dict[str, Any],
    schema: dict[str, Any],
    tool_name: str,
) -> list[str]:
    """Lightweight fallback validation without ``jsonschema``."""
    errors: list[str] = []
    properties = schema.get("properties", {})
    required = set(schema.get("required", []))

    # Required field check
    for req in required:
        if req not in args:
            errors.append(f"{req}: required field is missing")

    # Type checks
    _TYPE_MAP: dict[str, tuple[type, ...]] = None

    for key, value in args.items():
        if key not in properties:
            # additionalProperties — skip unknown fields by default
            continue

        prop_schema = properties[key]
        expected = prop_schema.get("type")

        if expected and expected in _TYPE_MAP:
            if not isinstance(value, _TYPE_MAP[expected]):
                errors.append(
                    f"{key}: expected type '{expected}', "
                    f"got '{type(value).__name__}'"
                )
                continue

        # Enum
        enum_values = prop_schema.get("enum")
        if enum_values is not None and value not in enum_values:
            errors.append(
                f"{key}: value {value!r} not in allowed values {enum_values}"
            )

        # Min / max (numeric)
        if isinstance(value, (int, float)):
            mn = prop_schema.get("minimum")
            mx = prop_schema.get("maximum")
            if mn is not None and value < mn:
                errors.append(f"{key}: {value} < minimum {mn}")
            if mx is not None and value > mx:
                errors.append(f"{key}: {value} > maximum {mx}")

        # Pattern (string)
        if isinstance(value, str):
            import re

            pattern = prop_schema.get("pattern")
            if pattern and not re.search(pattern, value):
                errors.append(
                    f"{key}: value {value!r} does not match pattern {pattern!r}"
                )

    return errors


def x__validate_builtin__mutmut_20(
    args: dict[str, Any],
    schema: dict[str, Any],
    tool_name: str,
) -> list[str]:
    """Lightweight fallback validation without ``jsonschema``."""
    errors: list[str] = []
    properties = schema.get("properties", {})
    required = set(schema.get("required", []))

    # Required field check
    for req in required:
        if req not in args:
            errors.append(f"{req}: required field is missing")

    # Type checks
    _TYPE_MAP: dict[str, tuple[type, ...]] = {
        "XXstringXX": (str,),
        "integer": (int,),
        "number": (int, float),
        "boolean": (bool,),
        "array": (list,),
        "object": (dict,),
    }

    for key, value in args.items():
        if key not in properties:
            # additionalProperties — skip unknown fields by default
            continue

        prop_schema = properties[key]
        expected = prop_schema.get("type")

        if expected and expected in _TYPE_MAP:
            if not isinstance(value, _TYPE_MAP[expected]):
                errors.append(
                    f"{key}: expected type '{expected}', "
                    f"got '{type(value).__name__}'"
                )
                continue

        # Enum
        enum_values = prop_schema.get("enum")
        if enum_values is not None and value not in enum_values:
            errors.append(
                f"{key}: value {value!r} not in allowed values {enum_values}"
            )

        # Min / max (numeric)
        if isinstance(value, (int, float)):
            mn = prop_schema.get("minimum")
            mx = prop_schema.get("maximum")
            if mn is not None and value < mn:
                errors.append(f"{key}: {value} < minimum {mn}")
            if mx is not None and value > mx:
                errors.append(f"{key}: {value} > maximum {mx}")

        # Pattern (string)
        if isinstance(value, str):
            import re

            pattern = prop_schema.get("pattern")
            if pattern and not re.search(pattern, value):
                errors.append(
                    f"{key}: value {value!r} does not match pattern {pattern!r}"
                )

    return errors


def x__validate_builtin__mutmut_21(
    args: dict[str, Any],
    schema: dict[str, Any],
    tool_name: str,
) -> list[str]:
    """Lightweight fallback validation without ``jsonschema``."""
    errors: list[str] = []
    properties = schema.get("properties", {})
    required = set(schema.get("required", []))

    # Required field check
    for req in required:
        if req not in args:
            errors.append(f"{req}: required field is missing")

    # Type checks
    _TYPE_MAP: dict[str, tuple[type, ...]] = {
        "STRING": (str,),
        "integer": (int,),
        "number": (int, float),
        "boolean": (bool,),
        "array": (list,),
        "object": (dict,),
    }

    for key, value in args.items():
        if key not in properties:
            # additionalProperties — skip unknown fields by default
            continue

        prop_schema = properties[key]
        expected = prop_schema.get("type")

        if expected and expected in _TYPE_MAP:
            if not isinstance(value, _TYPE_MAP[expected]):
                errors.append(
                    f"{key}: expected type '{expected}', "
                    f"got '{type(value).__name__}'"
                )
                continue

        # Enum
        enum_values = prop_schema.get("enum")
        if enum_values is not None and value not in enum_values:
            errors.append(
                f"{key}: value {value!r} not in allowed values {enum_values}"
            )

        # Min / max (numeric)
        if isinstance(value, (int, float)):
            mn = prop_schema.get("minimum")
            mx = prop_schema.get("maximum")
            if mn is not None and value < mn:
                errors.append(f"{key}: {value} < minimum {mn}")
            if mx is not None and value > mx:
                errors.append(f"{key}: {value} > maximum {mx}")

        # Pattern (string)
        if isinstance(value, str):
            import re

            pattern = prop_schema.get("pattern")
            if pattern and not re.search(pattern, value):
                errors.append(
                    f"{key}: value {value!r} does not match pattern {pattern!r}"
                )

    return errors


def x__validate_builtin__mutmut_22(
    args: dict[str, Any],
    schema: dict[str, Any],
    tool_name: str,
) -> list[str]:
    """Lightweight fallback validation without ``jsonschema``."""
    errors: list[str] = []
    properties = schema.get("properties", {})
    required = set(schema.get("required", []))

    # Required field check
    for req in required:
        if req not in args:
            errors.append(f"{req}: required field is missing")

    # Type checks
    _TYPE_MAP: dict[str, tuple[type, ...]] = {
        "string": (str,),
        "XXintegerXX": (int,),
        "number": (int, float),
        "boolean": (bool,),
        "array": (list,),
        "object": (dict,),
    }

    for key, value in args.items():
        if key not in properties:
            # additionalProperties — skip unknown fields by default
            continue

        prop_schema = properties[key]
        expected = prop_schema.get("type")

        if expected and expected in _TYPE_MAP:
            if not isinstance(value, _TYPE_MAP[expected]):
                errors.append(
                    f"{key}: expected type '{expected}', "
                    f"got '{type(value).__name__}'"
                )
                continue

        # Enum
        enum_values = prop_schema.get("enum")
        if enum_values is not None and value not in enum_values:
            errors.append(
                f"{key}: value {value!r} not in allowed values {enum_values}"
            )

        # Min / max (numeric)
        if isinstance(value, (int, float)):
            mn = prop_schema.get("minimum")
            mx = prop_schema.get("maximum")
            if mn is not None and value < mn:
                errors.append(f"{key}: {value} < minimum {mn}")
            if mx is not None and value > mx:
                errors.append(f"{key}: {value} > maximum {mx}")

        # Pattern (string)
        if isinstance(value, str):
            import re

            pattern = prop_schema.get("pattern")
            if pattern and not re.search(pattern, value):
                errors.append(
                    f"{key}: value {value!r} does not match pattern {pattern!r}"
                )

    return errors


def x__validate_builtin__mutmut_23(
    args: dict[str, Any],
    schema: dict[str, Any],
    tool_name: str,
) -> list[str]:
    """Lightweight fallback validation without ``jsonschema``."""
    errors: list[str] = []
    properties = schema.get("properties", {})
    required = set(schema.get("required", []))

    # Required field check
    for req in required:
        if req not in args:
            errors.append(f"{req}: required field is missing")

    # Type checks
    _TYPE_MAP: dict[str, tuple[type, ...]] = {
        "string": (str,),
        "INTEGER": (int,),
        "number": (int, float),
        "boolean": (bool,),
        "array": (list,),
        "object": (dict,),
    }

    for key, value in args.items():
        if key not in properties:
            # additionalProperties — skip unknown fields by default
            continue

        prop_schema = properties[key]
        expected = prop_schema.get("type")

        if expected and expected in _TYPE_MAP:
            if not isinstance(value, _TYPE_MAP[expected]):
                errors.append(
                    f"{key}: expected type '{expected}', "
                    f"got '{type(value).__name__}'"
                )
                continue

        # Enum
        enum_values = prop_schema.get("enum")
        if enum_values is not None and value not in enum_values:
            errors.append(
                f"{key}: value {value!r} not in allowed values {enum_values}"
            )

        # Min / max (numeric)
        if isinstance(value, (int, float)):
            mn = prop_schema.get("minimum")
            mx = prop_schema.get("maximum")
            if mn is not None and value < mn:
                errors.append(f"{key}: {value} < minimum {mn}")
            if mx is not None and value > mx:
                errors.append(f"{key}: {value} > maximum {mx}")

        # Pattern (string)
        if isinstance(value, str):
            import re

            pattern = prop_schema.get("pattern")
            if pattern and not re.search(pattern, value):
                errors.append(
                    f"{key}: value {value!r} does not match pattern {pattern!r}"
                )

    return errors


def x__validate_builtin__mutmut_24(
    args: dict[str, Any],
    schema: dict[str, Any],
    tool_name: str,
) -> list[str]:
    """Lightweight fallback validation without ``jsonschema``."""
    errors: list[str] = []
    properties = schema.get("properties", {})
    required = set(schema.get("required", []))

    # Required field check
    for req in required:
        if req not in args:
            errors.append(f"{req}: required field is missing")

    # Type checks
    _TYPE_MAP: dict[str, tuple[type, ...]] = {
        "string": (str,),
        "integer": (int,),
        "XXnumberXX": (int, float),
        "boolean": (bool,),
        "array": (list,),
        "object": (dict,),
    }

    for key, value in args.items():
        if key not in properties:
            # additionalProperties — skip unknown fields by default
            continue

        prop_schema = properties[key]
        expected = prop_schema.get("type")

        if expected and expected in _TYPE_MAP:
            if not isinstance(value, _TYPE_MAP[expected]):
                errors.append(
                    f"{key}: expected type '{expected}', "
                    f"got '{type(value).__name__}'"
                )
                continue

        # Enum
        enum_values = prop_schema.get("enum")
        if enum_values is not None and value not in enum_values:
            errors.append(
                f"{key}: value {value!r} not in allowed values {enum_values}"
            )

        # Min / max (numeric)
        if isinstance(value, (int, float)):
            mn = prop_schema.get("minimum")
            mx = prop_schema.get("maximum")
            if mn is not None and value < mn:
                errors.append(f"{key}: {value} < minimum {mn}")
            if mx is not None and value > mx:
                errors.append(f"{key}: {value} > maximum {mx}")

        # Pattern (string)
        if isinstance(value, str):
            import re

            pattern = prop_schema.get("pattern")
            if pattern and not re.search(pattern, value):
                errors.append(
                    f"{key}: value {value!r} does not match pattern {pattern!r}"
                )

    return errors


def x__validate_builtin__mutmut_25(
    args: dict[str, Any],
    schema: dict[str, Any],
    tool_name: str,
) -> list[str]:
    """Lightweight fallback validation without ``jsonschema``."""
    errors: list[str] = []
    properties = schema.get("properties", {})
    required = set(schema.get("required", []))

    # Required field check
    for req in required:
        if req not in args:
            errors.append(f"{req}: required field is missing")

    # Type checks
    _TYPE_MAP: dict[str, tuple[type, ...]] = {
        "string": (str,),
        "integer": (int,),
        "NUMBER": (int, float),
        "boolean": (bool,),
        "array": (list,),
        "object": (dict,),
    }

    for key, value in args.items():
        if key not in properties:
            # additionalProperties — skip unknown fields by default
            continue

        prop_schema = properties[key]
        expected = prop_schema.get("type")

        if expected and expected in _TYPE_MAP:
            if not isinstance(value, _TYPE_MAP[expected]):
                errors.append(
                    f"{key}: expected type '{expected}', "
                    f"got '{type(value).__name__}'"
                )
                continue

        # Enum
        enum_values = prop_schema.get("enum")
        if enum_values is not None and value not in enum_values:
            errors.append(
                f"{key}: value {value!r} not in allowed values {enum_values}"
            )

        # Min / max (numeric)
        if isinstance(value, (int, float)):
            mn = prop_schema.get("minimum")
            mx = prop_schema.get("maximum")
            if mn is not None and value < mn:
                errors.append(f"{key}: {value} < minimum {mn}")
            if mx is not None and value > mx:
                errors.append(f"{key}: {value} > maximum {mx}")

        # Pattern (string)
        if isinstance(value, str):
            import re

            pattern = prop_schema.get("pattern")
            if pattern and not re.search(pattern, value):
                errors.append(
                    f"{key}: value {value!r} does not match pattern {pattern!r}"
                )

    return errors


def x__validate_builtin__mutmut_26(
    args: dict[str, Any],
    schema: dict[str, Any],
    tool_name: str,
) -> list[str]:
    """Lightweight fallback validation without ``jsonschema``."""
    errors: list[str] = []
    properties = schema.get("properties", {})
    required = set(schema.get("required", []))

    # Required field check
    for req in required:
        if req not in args:
            errors.append(f"{req}: required field is missing")

    # Type checks
    _TYPE_MAP: dict[str, tuple[type, ...]] = {
        "string": (str,),
        "integer": (int,),
        "number": (int, float),
        "XXbooleanXX": (bool,),
        "array": (list,),
        "object": (dict,),
    }

    for key, value in args.items():
        if key not in properties:
            # additionalProperties — skip unknown fields by default
            continue

        prop_schema = properties[key]
        expected = prop_schema.get("type")

        if expected and expected in _TYPE_MAP:
            if not isinstance(value, _TYPE_MAP[expected]):
                errors.append(
                    f"{key}: expected type '{expected}', "
                    f"got '{type(value).__name__}'"
                )
                continue

        # Enum
        enum_values = prop_schema.get("enum")
        if enum_values is not None and value not in enum_values:
            errors.append(
                f"{key}: value {value!r} not in allowed values {enum_values}"
            )

        # Min / max (numeric)
        if isinstance(value, (int, float)):
            mn = prop_schema.get("minimum")
            mx = prop_schema.get("maximum")
            if mn is not None and value < mn:
                errors.append(f"{key}: {value} < minimum {mn}")
            if mx is not None and value > mx:
                errors.append(f"{key}: {value} > maximum {mx}")

        # Pattern (string)
        if isinstance(value, str):
            import re

            pattern = prop_schema.get("pattern")
            if pattern and not re.search(pattern, value):
                errors.append(
                    f"{key}: value {value!r} does not match pattern {pattern!r}"
                )

    return errors


def x__validate_builtin__mutmut_27(
    args: dict[str, Any],
    schema: dict[str, Any],
    tool_name: str,
) -> list[str]:
    """Lightweight fallback validation without ``jsonschema``."""
    errors: list[str] = []
    properties = schema.get("properties", {})
    required = set(schema.get("required", []))

    # Required field check
    for req in required:
        if req not in args:
            errors.append(f"{req}: required field is missing")

    # Type checks
    _TYPE_MAP: dict[str, tuple[type, ...]] = {
        "string": (str,),
        "integer": (int,),
        "number": (int, float),
        "BOOLEAN": (bool,),
        "array": (list,),
        "object": (dict,),
    }

    for key, value in args.items():
        if key not in properties:
            # additionalProperties — skip unknown fields by default
            continue

        prop_schema = properties[key]
        expected = prop_schema.get("type")

        if expected and expected in _TYPE_MAP:
            if not isinstance(value, _TYPE_MAP[expected]):
                errors.append(
                    f"{key}: expected type '{expected}', "
                    f"got '{type(value).__name__}'"
                )
                continue

        # Enum
        enum_values = prop_schema.get("enum")
        if enum_values is not None and value not in enum_values:
            errors.append(
                f"{key}: value {value!r} not in allowed values {enum_values}"
            )

        # Min / max (numeric)
        if isinstance(value, (int, float)):
            mn = prop_schema.get("minimum")
            mx = prop_schema.get("maximum")
            if mn is not None and value < mn:
                errors.append(f"{key}: {value} < minimum {mn}")
            if mx is not None and value > mx:
                errors.append(f"{key}: {value} > maximum {mx}")

        # Pattern (string)
        if isinstance(value, str):
            import re

            pattern = prop_schema.get("pattern")
            if pattern and not re.search(pattern, value):
                errors.append(
                    f"{key}: value {value!r} does not match pattern {pattern!r}"
                )

    return errors


def x__validate_builtin__mutmut_28(
    args: dict[str, Any],
    schema: dict[str, Any],
    tool_name: str,
) -> list[str]:
    """Lightweight fallback validation without ``jsonschema``."""
    errors: list[str] = []
    properties = schema.get("properties", {})
    required = set(schema.get("required", []))

    # Required field check
    for req in required:
        if req not in args:
            errors.append(f"{req}: required field is missing")

    # Type checks
    _TYPE_MAP: dict[str, tuple[type, ...]] = {
        "string": (str,),
        "integer": (int,),
        "number": (int, float),
        "boolean": (bool,),
        "XXarrayXX": (list,),
        "object": (dict,),
    }

    for key, value in args.items():
        if key not in properties:
            # additionalProperties — skip unknown fields by default
            continue

        prop_schema = properties[key]
        expected = prop_schema.get("type")

        if expected and expected in _TYPE_MAP:
            if not isinstance(value, _TYPE_MAP[expected]):
                errors.append(
                    f"{key}: expected type '{expected}', "
                    f"got '{type(value).__name__}'"
                )
                continue

        # Enum
        enum_values = prop_schema.get("enum")
        if enum_values is not None and value not in enum_values:
            errors.append(
                f"{key}: value {value!r} not in allowed values {enum_values}"
            )

        # Min / max (numeric)
        if isinstance(value, (int, float)):
            mn = prop_schema.get("minimum")
            mx = prop_schema.get("maximum")
            if mn is not None and value < mn:
                errors.append(f"{key}: {value} < minimum {mn}")
            if mx is not None and value > mx:
                errors.append(f"{key}: {value} > maximum {mx}")

        # Pattern (string)
        if isinstance(value, str):
            import re

            pattern = prop_schema.get("pattern")
            if pattern and not re.search(pattern, value):
                errors.append(
                    f"{key}: value {value!r} does not match pattern {pattern!r}"
                )

    return errors


def x__validate_builtin__mutmut_29(
    args: dict[str, Any],
    schema: dict[str, Any],
    tool_name: str,
) -> list[str]:
    """Lightweight fallback validation without ``jsonschema``."""
    errors: list[str] = []
    properties = schema.get("properties", {})
    required = set(schema.get("required", []))

    # Required field check
    for req in required:
        if req not in args:
            errors.append(f"{req}: required field is missing")

    # Type checks
    _TYPE_MAP: dict[str, tuple[type, ...]] = {
        "string": (str,),
        "integer": (int,),
        "number": (int, float),
        "boolean": (bool,),
        "ARRAY": (list,),
        "object": (dict,),
    }

    for key, value in args.items():
        if key not in properties:
            # additionalProperties — skip unknown fields by default
            continue

        prop_schema = properties[key]
        expected = prop_schema.get("type")

        if expected and expected in _TYPE_MAP:
            if not isinstance(value, _TYPE_MAP[expected]):
                errors.append(
                    f"{key}: expected type '{expected}', "
                    f"got '{type(value).__name__}'"
                )
                continue

        # Enum
        enum_values = prop_schema.get("enum")
        if enum_values is not None and value not in enum_values:
            errors.append(
                f"{key}: value {value!r} not in allowed values {enum_values}"
            )

        # Min / max (numeric)
        if isinstance(value, (int, float)):
            mn = prop_schema.get("minimum")
            mx = prop_schema.get("maximum")
            if mn is not None and value < mn:
                errors.append(f"{key}: {value} < minimum {mn}")
            if mx is not None and value > mx:
                errors.append(f"{key}: {value} > maximum {mx}")

        # Pattern (string)
        if isinstance(value, str):
            import re

            pattern = prop_schema.get("pattern")
            if pattern and not re.search(pattern, value):
                errors.append(
                    f"{key}: value {value!r} does not match pattern {pattern!r}"
                )

    return errors


def x__validate_builtin__mutmut_30(
    args: dict[str, Any],
    schema: dict[str, Any],
    tool_name: str,
) -> list[str]:
    """Lightweight fallback validation without ``jsonschema``."""
    errors: list[str] = []
    properties = schema.get("properties", {})
    required = set(schema.get("required", []))

    # Required field check
    for req in required:
        if req not in args:
            errors.append(f"{req}: required field is missing")

    # Type checks
    _TYPE_MAP: dict[str, tuple[type, ...]] = {
        "string": (str,),
        "integer": (int,),
        "number": (int, float),
        "boolean": (bool,),
        "array": (list,),
        "XXobjectXX": (dict,),
    }

    for key, value in args.items():
        if key not in properties:
            # additionalProperties — skip unknown fields by default
            continue

        prop_schema = properties[key]
        expected = prop_schema.get("type")

        if expected and expected in _TYPE_MAP:
            if not isinstance(value, _TYPE_MAP[expected]):
                errors.append(
                    f"{key}: expected type '{expected}', "
                    f"got '{type(value).__name__}'"
                )
                continue

        # Enum
        enum_values = prop_schema.get("enum")
        if enum_values is not None and value not in enum_values:
            errors.append(
                f"{key}: value {value!r} not in allowed values {enum_values}"
            )

        # Min / max (numeric)
        if isinstance(value, (int, float)):
            mn = prop_schema.get("minimum")
            mx = prop_schema.get("maximum")
            if mn is not None and value < mn:
                errors.append(f"{key}: {value} < minimum {mn}")
            if mx is not None and value > mx:
                errors.append(f"{key}: {value} > maximum {mx}")

        # Pattern (string)
        if isinstance(value, str):
            import re

            pattern = prop_schema.get("pattern")
            if pattern and not re.search(pattern, value):
                errors.append(
                    f"{key}: value {value!r} does not match pattern {pattern!r}"
                )

    return errors


def x__validate_builtin__mutmut_31(
    args: dict[str, Any],
    schema: dict[str, Any],
    tool_name: str,
) -> list[str]:
    """Lightweight fallback validation without ``jsonschema``."""
    errors: list[str] = []
    properties = schema.get("properties", {})
    required = set(schema.get("required", []))

    # Required field check
    for req in required:
        if req not in args:
            errors.append(f"{req}: required field is missing")

    # Type checks
    _TYPE_MAP: dict[str, tuple[type, ...]] = {
        "string": (str,),
        "integer": (int,),
        "number": (int, float),
        "boolean": (bool,),
        "array": (list,),
        "OBJECT": (dict,),
    }

    for key, value in args.items():
        if key not in properties:
            # additionalProperties — skip unknown fields by default
            continue

        prop_schema = properties[key]
        expected = prop_schema.get("type")

        if expected and expected in _TYPE_MAP:
            if not isinstance(value, _TYPE_MAP[expected]):
                errors.append(
                    f"{key}: expected type '{expected}', "
                    f"got '{type(value).__name__}'"
                )
                continue

        # Enum
        enum_values = prop_schema.get("enum")
        if enum_values is not None and value not in enum_values:
            errors.append(
                f"{key}: value {value!r} not in allowed values {enum_values}"
            )

        # Min / max (numeric)
        if isinstance(value, (int, float)):
            mn = prop_schema.get("minimum")
            mx = prop_schema.get("maximum")
            if mn is not None and value < mn:
                errors.append(f"{key}: {value} < minimum {mn}")
            if mx is not None and value > mx:
                errors.append(f"{key}: {value} > maximum {mx}")

        # Pattern (string)
        if isinstance(value, str):
            import re

            pattern = prop_schema.get("pattern")
            if pattern and not re.search(pattern, value):
                errors.append(
                    f"{key}: value {value!r} does not match pattern {pattern!r}"
                )

    return errors


def x__validate_builtin__mutmut_32(
    args: dict[str, Any],
    schema: dict[str, Any],
    tool_name: str,
) -> list[str]:
    """Lightweight fallback validation without ``jsonschema``."""
    errors: list[str] = []
    properties = schema.get("properties", {})
    required = set(schema.get("required", []))

    # Required field check
    for req in required:
        if req not in args:
            errors.append(f"{req}: required field is missing")

    # Type checks
    _TYPE_MAP: dict[str, tuple[type, ...]] = {
        "string": (str,),
        "integer": (int,),
        "number": (int, float),
        "boolean": (bool,),
        "array": (list,),
        "object": (dict,),
    }

    for key, value in args.items():
        if key in properties:
            # additionalProperties — skip unknown fields by default
            continue

        prop_schema = properties[key]
        expected = prop_schema.get("type")

        if expected and expected in _TYPE_MAP:
            if not isinstance(value, _TYPE_MAP[expected]):
                errors.append(
                    f"{key}: expected type '{expected}', "
                    f"got '{type(value).__name__}'"
                )
                continue

        # Enum
        enum_values = prop_schema.get("enum")
        if enum_values is not None and value not in enum_values:
            errors.append(
                f"{key}: value {value!r} not in allowed values {enum_values}"
            )

        # Min / max (numeric)
        if isinstance(value, (int, float)):
            mn = prop_schema.get("minimum")
            mx = prop_schema.get("maximum")
            if mn is not None and value < mn:
                errors.append(f"{key}: {value} < minimum {mn}")
            if mx is not None and value > mx:
                errors.append(f"{key}: {value} > maximum {mx}")

        # Pattern (string)
        if isinstance(value, str):
            import re

            pattern = prop_schema.get("pattern")
            if pattern and not re.search(pattern, value):
                errors.append(
                    f"{key}: value {value!r} does not match pattern {pattern!r}"
                )

    return errors


def x__validate_builtin__mutmut_33(
    args: dict[str, Any],
    schema: dict[str, Any],
    tool_name: str,
) -> list[str]:
    """Lightweight fallback validation without ``jsonschema``."""
    errors: list[str] = []
    properties = schema.get("properties", {})
    required = set(schema.get("required", []))

    # Required field check
    for req in required:
        if req not in args:
            errors.append(f"{req}: required field is missing")

    # Type checks
    _TYPE_MAP: dict[str, tuple[type, ...]] = {
        "string": (str,),
        "integer": (int,),
        "number": (int, float),
        "boolean": (bool,),
        "array": (list,),
        "object": (dict,),
    }

    for key, value in args.items():
        if key not in properties:
            # additionalProperties — skip unknown fields by default
            break

        prop_schema = properties[key]
        expected = prop_schema.get("type")

        if expected and expected in _TYPE_MAP:
            if not isinstance(value, _TYPE_MAP[expected]):
                errors.append(
                    f"{key}: expected type '{expected}', "
                    f"got '{type(value).__name__}'"
                )
                continue

        # Enum
        enum_values = prop_schema.get("enum")
        if enum_values is not None and value not in enum_values:
            errors.append(
                f"{key}: value {value!r} not in allowed values {enum_values}"
            )

        # Min / max (numeric)
        if isinstance(value, (int, float)):
            mn = prop_schema.get("minimum")
            mx = prop_schema.get("maximum")
            if mn is not None and value < mn:
                errors.append(f"{key}: {value} < minimum {mn}")
            if mx is not None and value > mx:
                errors.append(f"{key}: {value} > maximum {mx}")

        # Pattern (string)
        if isinstance(value, str):
            import re

            pattern = prop_schema.get("pattern")
            if pattern and not re.search(pattern, value):
                errors.append(
                    f"{key}: value {value!r} does not match pattern {pattern!r}"
                )

    return errors


def x__validate_builtin__mutmut_34(
    args: dict[str, Any],
    schema: dict[str, Any],
    tool_name: str,
) -> list[str]:
    """Lightweight fallback validation without ``jsonschema``."""
    errors: list[str] = []
    properties = schema.get("properties", {})
    required = set(schema.get("required", []))

    # Required field check
    for req in required:
        if req not in args:
            errors.append(f"{req}: required field is missing")

    # Type checks
    _TYPE_MAP: dict[str, tuple[type, ...]] = {
        "string": (str,),
        "integer": (int,),
        "number": (int, float),
        "boolean": (bool,),
        "array": (list,),
        "object": (dict,),
    }

    for key, value in args.items():
        if key not in properties:
            # additionalProperties — skip unknown fields by default
            continue

        prop_schema = None
        expected = prop_schema.get("type")

        if expected and expected in _TYPE_MAP:
            if not isinstance(value, _TYPE_MAP[expected]):
                errors.append(
                    f"{key}: expected type '{expected}', "
                    f"got '{type(value).__name__}'"
                )
                continue

        # Enum
        enum_values = prop_schema.get("enum")
        if enum_values is not None and value not in enum_values:
            errors.append(
                f"{key}: value {value!r} not in allowed values {enum_values}"
            )

        # Min / max (numeric)
        if isinstance(value, (int, float)):
            mn = prop_schema.get("minimum")
            mx = prop_schema.get("maximum")
            if mn is not None and value < mn:
                errors.append(f"{key}: {value} < minimum {mn}")
            if mx is not None and value > mx:
                errors.append(f"{key}: {value} > maximum {mx}")

        # Pattern (string)
        if isinstance(value, str):
            import re

            pattern = prop_schema.get("pattern")
            if pattern and not re.search(pattern, value):
                errors.append(
                    f"{key}: value {value!r} does not match pattern {pattern!r}"
                )

    return errors


def x__validate_builtin__mutmut_35(
    args: dict[str, Any],
    schema: dict[str, Any],
    tool_name: str,
) -> list[str]:
    """Lightweight fallback validation without ``jsonschema``."""
    errors: list[str] = []
    properties = schema.get("properties", {})
    required = set(schema.get("required", []))

    # Required field check
    for req in required:
        if req not in args:
            errors.append(f"{req}: required field is missing")

    # Type checks
    _TYPE_MAP: dict[str, tuple[type, ...]] = {
        "string": (str,),
        "integer": (int,),
        "number": (int, float),
        "boolean": (bool,),
        "array": (list,),
        "object": (dict,),
    }

    for key, value in args.items():
        if key not in properties:
            # additionalProperties — skip unknown fields by default
            continue

        prop_schema = properties[key]
        expected = None

        if expected and expected in _TYPE_MAP:
            if not isinstance(value, _TYPE_MAP[expected]):
                errors.append(
                    f"{key}: expected type '{expected}', "
                    f"got '{type(value).__name__}'"
                )
                continue

        # Enum
        enum_values = prop_schema.get("enum")
        if enum_values is not None and value not in enum_values:
            errors.append(
                f"{key}: value {value!r} not in allowed values {enum_values}"
            )

        # Min / max (numeric)
        if isinstance(value, (int, float)):
            mn = prop_schema.get("minimum")
            mx = prop_schema.get("maximum")
            if mn is not None and value < mn:
                errors.append(f"{key}: {value} < minimum {mn}")
            if mx is not None and value > mx:
                errors.append(f"{key}: {value} > maximum {mx}")

        # Pattern (string)
        if isinstance(value, str):
            import re

            pattern = prop_schema.get("pattern")
            if pattern and not re.search(pattern, value):
                errors.append(
                    f"{key}: value {value!r} does not match pattern {pattern!r}"
                )

    return errors


def x__validate_builtin__mutmut_36(
    args: dict[str, Any],
    schema: dict[str, Any],
    tool_name: str,
) -> list[str]:
    """Lightweight fallback validation without ``jsonschema``."""
    errors: list[str] = []
    properties = schema.get("properties", {})
    required = set(schema.get("required", []))

    # Required field check
    for req in required:
        if req not in args:
            errors.append(f"{req}: required field is missing")

    # Type checks
    _TYPE_MAP: dict[str, tuple[type, ...]] = {
        "string": (str,),
        "integer": (int,),
        "number": (int, float),
        "boolean": (bool,),
        "array": (list,),
        "object": (dict,),
    }

    for key, value in args.items():
        if key not in properties:
            # additionalProperties — skip unknown fields by default
            continue

        prop_schema = properties[key]
        expected = prop_schema.get(None)

        if expected and expected in _TYPE_MAP:
            if not isinstance(value, _TYPE_MAP[expected]):
                errors.append(
                    f"{key}: expected type '{expected}', "
                    f"got '{type(value).__name__}'"
                )
                continue

        # Enum
        enum_values = prop_schema.get("enum")
        if enum_values is not None and value not in enum_values:
            errors.append(
                f"{key}: value {value!r} not in allowed values {enum_values}"
            )

        # Min / max (numeric)
        if isinstance(value, (int, float)):
            mn = prop_schema.get("minimum")
            mx = prop_schema.get("maximum")
            if mn is not None and value < mn:
                errors.append(f"{key}: {value} < minimum {mn}")
            if mx is not None and value > mx:
                errors.append(f"{key}: {value} > maximum {mx}")

        # Pattern (string)
        if isinstance(value, str):
            import re

            pattern = prop_schema.get("pattern")
            if pattern and not re.search(pattern, value):
                errors.append(
                    f"{key}: value {value!r} does not match pattern {pattern!r}"
                )

    return errors


def x__validate_builtin__mutmut_37(
    args: dict[str, Any],
    schema: dict[str, Any],
    tool_name: str,
) -> list[str]:
    """Lightweight fallback validation without ``jsonschema``."""
    errors: list[str] = []
    properties = schema.get("properties", {})
    required = set(schema.get("required", []))

    # Required field check
    for req in required:
        if req not in args:
            errors.append(f"{req}: required field is missing")

    # Type checks
    _TYPE_MAP: dict[str, tuple[type, ...]] = {
        "string": (str,),
        "integer": (int,),
        "number": (int, float),
        "boolean": (bool,),
        "array": (list,),
        "object": (dict,),
    }

    for key, value in args.items():
        if key not in properties:
            # additionalProperties — skip unknown fields by default
            continue

        prop_schema = properties[key]
        expected = prop_schema.get("XXtypeXX")

        if expected and expected in _TYPE_MAP:
            if not isinstance(value, _TYPE_MAP[expected]):
                errors.append(
                    f"{key}: expected type '{expected}', "
                    f"got '{type(value).__name__}'"
                )
                continue

        # Enum
        enum_values = prop_schema.get("enum")
        if enum_values is not None and value not in enum_values:
            errors.append(
                f"{key}: value {value!r} not in allowed values {enum_values}"
            )

        # Min / max (numeric)
        if isinstance(value, (int, float)):
            mn = prop_schema.get("minimum")
            mx = prop_schema.get("maximum")
            if mn is not None and value < mn:
                errors.append(f"{key}: {value} < minimum {mn}")
            if mx is not None and value > mx:
                errors.append(f"{key}: {value} > maximum {mx}")

        # Pattern (string)
        if isinstance(value, str):
            import re

            pattern = prop_schema.get("pattern")
            if pattern and not re.search(pattern, value):
                errors.append(
                    f"{key}: value {value!r} does not match pattern {pattern!r}"
                )

    return errors


def x__validate_builtin__mutmut_38(
    args: dict[str, Any],
    schema: dict[str, Any],
    tool_name: str,
) -> list[str]:
    """Lightweight fallback validation without ``jsonschema``."""
    errors: list[str] = []
    properties = schema.get("properties", {})
    required = set(schema.get("required", []))

    # Required field check
    for req in required:
        if req not in args:
            errors.append(f"{req}: required field is missing")

    # Type checks
    _TYPE_MAP: dict[str, tuple[type, ...]] = {
        "string": (str,),
        "integer": (int,),
        "number": (int, float),
        "boolean": (bool,),
        "array": (list,),
        "object": (dict,),
    }

    for key, value in args.items():
        if key not in properties:
            # additionalProperties — skip unknown fields by default
            continue

        prop_schema = properties[key]
        expected = prop_schema.get("TYPE")

        if expected and expected in _TYPE_MAP:
            if not isinstance(value, _TYPE_MAP[expected]):
                errors.append(
                    f"{key}: expected type '{expected}', "
                    f"got '{type(value).__name__}'"
                )
                continue

        # Enum
        enum_values = prop_schema.get("enum")
        if enum_values is not None and value not in enum_values:
            errors.append(
                f"{key}: value {value!r} not in allowed values {enum_values}"
            )

        # Min / max (numeric)
        if isinstance(value, (int, float)):
            mn = prop_schema.get("minimum")
            mx = prop_schema.get("maximum")
            if mn is not None and value < mn:
                errors.append(f"{key}: {value} < minimum {mn}")
            if mx is not None and value > mx:
                errors.append(f"{key}: {value} > maximum {mx}")

        # Pattern (string)
        if isinstance(value, str):
            import re

            pattern = prop_schema.get("pattern")
            if pattern and not re.search(pattern, value):
                errors.append(
                    f"{key}: value {value!r} does not match pattern {pattern!r}"
                )

    return errors


def x__validate_builtin__mutmut_39(
    args: dict[str, Any],
    schema: dict[str, Any],
    tool_name: str,
) -> list[str]:
    """Lightweight fallback validation without ``jsonschema``."""
    errors: list[str] = []
    properties = schema.get("properties", {})
    required = set(schema.get("required", []))

    # Required field check
    for req in required:
        if req not in args:
            errors.append(f"{req}: required field is missing")

    # Type checks
    _TYPE_MAP: dict[str, tuple[type, ...]] = {
        "string": (str,),
        "integer": (int,),
        "number": (int, float),
        "boolean": (bool,),
        "array": (list,),
        "object": (dict,),
    }

    for key, value in args.items():
        if key not in properties:
            # additionalProperties — skip unknown fields by default
            continue

        prop_schema = properties[key]
        expected = prop_schema.get("type")

        if expected or expected in _TYPE_MAP:
            if not isinstance(value, _TYPE_MAP[expected]):
                errors.append(
                    f"{key}: expected type '{expected}', "
                    f"got '{type(value).__name__}'"
                )
                continue

        # Enum
        enum_values = prop_schema.get("enum")
        if enum_values is not None and value not in enum_values:
            errors.append(
                f"{key}: value {value!r} not in allowed values {enum_values}"
            )

        # Min / max (numeric)
        if isinstance(value, (int, float)):
            mn = prop_schema.get("minimum")
            mx = prop_schema.get("maximum")
            if mn is not None and value < mn:
                errors.append(f"{key}: {value} < minimum {mn}")
            if mx is not None and value > mx:
                errors.append(f"{key}: {value} > maximum {mx}")

        # Pattern (string)
        if isinstance(value, str):
            import re

            pattern = prop_schema.get("pattern")
            if pattern and not re.search(pattern, value):
                errors.append(
                    f"{key}: value {value!r} does not match pattern {pattern!r}"
                )

    return errors


def x__validate_builtin__mutmut_40(
    args: dict[str, Any],
    schema: dict[str, Any],
    tool_name: str,
) -> list[str]:
    """Lightweight fallback validation without ``jsonschema``."""
    errors: list[str] = []
    properties = schema.get("properties", {})
    required = set(schema.get("required", []))

    # Required field check
    for req in required:
        if req not in args:
            errors.append(f"{req}: required field is missing")

    # Type checks
    _TYPE_MAP: dict[str, tuple[type, ...]] = {
        "string": (str,),
        "integer": (int,),
        "number": (int, float),
        "boolean": (bool,),
        "array": (list,),
        "object": (dict,),
    }

    for key, value in args.items():
        if key not in properties:
            # additionalProperties — skip unknown fields by default
            continue

        prop_schema = properties[key]
        expected = prop_schema.get("type")

        if expected and expected not in _TYPE_MAP:
            if not isinstance(value, _TYPE_MAP[expected]):
                errors.append(
                    f"{key}: expected type '{expected}', "
                    f"got '{type(value).__name__}'"
                )
                continue

        # Enum
        enum_values = prop_schema.get("enum")
        if enum_values is not None and value not in enum_values:
            errors.append(
                f"{key}: value {value!r} not in allowed values {enum_values}"
            )

        # Min / max (numeric)
        if isinstance(value, (int, float)):
            mn = prop_schema.get("minimum")
            mx = prop_schema.get("maximum")
            if mn is not None and value < mn:
                errors.append(f"{key}: {value} < minimum {mn}")
            if mx is not None and value > mx:
                errors.append(f"{key}: {value} > maximum {mx}")

        # Pattern (string)
        if isinstance(value, str):
            import re

            pattern = prop_schema.get("pattern")
            if pattern and not re.search(pattern, value):
                errors.append(
                    f"{key}: value {value!r} does not match pattern {pattern!r}"
                )

    return errors


def x__validate_builtin__mutmut_41(
    args: dict[str, Any],
    schema: dict[str, Any],
    tool_name: str,
) -> list[str]:
    """Lightweight fallback validation without ``jsonschema``."""
    errors: list[str] = []
    properties = schema.get("properties", {})
    required = set(schema.get("required", []))

    # Required field check
    for req in required:
        if req not in args:
            errors.append(f"{req}: required field is missing")

    # Type checks
    _TYPE_MAP: dict[str, tuple[type, ...]] = {
        "string": (str,),
        "integer": (int,),
        "number": (int, float),
        "boolean": (bool,),
        "array": (list,),
        "object": (dict,),
    }

    for key, value in args.items():
        if key not in properties:
            # additionalProperties — skip unknown fields by default
            continue

        prop_schema = properties[key]
        expected = prop_schema.get("type")

        if expected and expected in _TYPE_MAP:
            if isinstance(value, _TYPE_MAP[expected]):
                errors.append(
                    f"{key}: expected type '{expected}', "
                    f"got '{type(value).__name__}'"
                )
                continue

        # Enum
        enum_values = prop_schema.get("enum")
        if enum_values is not None and value not in enum_values:
            errors.append(
                f"{key}: value {value!r} not in allowed values {enum_values}"
            )

        # Min / max (numeric)
        if isinstance(value, (int, float)):
            mn = prop_schema.get("minimum")
            mx = prop_schema.get("maximum")
            if mn is not None and value < mn:
                errors.append(f"{key}: {value} < minimum {mn}")
            if mx is not None and value > mx:
                errors.append(f"{key}: {value} > maximum {mx}")

        # Pattern (string)
        if isinstance(value, str):
            import re

            pattern = prop_schema.get("pattern")
            if pattern and not re.search(pattern, value):
                errors.append(
                    f"{key}: value {value!r} does not match pattern {pattern!r}"
                )

    return errors


def x__validate_builtin__mutmut_42(
    args: dict[str, Any],
    schema: dict[str, Any],
    tool_name: str,
) -> list[str]:
    """Lightweight fallback validation without ``jsonschema``."""
    errors: list[str] = []
    properties = schema.get("properties", {})
    required = set(schema.get("required", []))

    # Required field check
    for req in required:
        if req not in args:
            errors.append(f"{req}: required field is missing")

    # Type checks
    _TYPE_MAP: dict[str, tuple[type, ...]] = {
        "string": (str,),
        "integer": (int,),
        "number": (int, float),
        "boolean": (bool,),
        "array": (list,),
        "object": (dict,),
    }

    for key, value in args.items():
        if key not in properties:
            # additionalProperties — skip unknown fields by default
            continue

        prop_schema = properties[key]
        expected = prop_schema.get("type")

        if expected and expected in _TYPE_MAP:
            if not isinstance(value, _TYPE_MAP[expected]):
                errors.append(
                    None
                )
                continue

        # Enum
        enum_values = prop_schema.get("enum")
        if enum_values is not None and value not in enum_values:
            errors.append(
                f"{key}: value {value!r} not in allowed values {enum_values}"
            )

        # Min / max (numeric)
        if isinstance(value, (int, float)):
            mn = prop_schema.get("minimum")
            mx = prop_schema.get("maximum")
            if mn is not None and value < mn:
                errors.append(f"{key}: {value} < minimum {mn}")
            if mx is not None and value > mx:
                errors.append(f"{key}: {value} > maximum {mx}")

        # Pattern (string)
        if isinstance(value, str):
            import re

            pattern = prop_schema.get("pattern")
            if pattern and not re.search(pattern, value):
                errors.append(
                    f"{key}: value {value!r} does not match pattern {pattern!r}"
                )

    return errors


def x__validate_builtin__mutmut_43(
    args: dict[str, Any],
    schema: dict[str, Any],
    tool_name: str,
) -> list[str]:
    """Lightweight fallback validation without ``jsonschema``."""
    errors: list[str] = []
    properties = schema.get("properties", {})
    required = set(schema.get("required", []))

    # Required field check
    for req in required:
        if req not in args:
            errors.append(f"{req}: required field is missing")

    # Type checks
    _TYPE_MAP: dict[str, tuple[type, ...]] = {
        "string": (str,),
        "integer": (int,),
        "number": (int, float),
        "boolean": (bool,),
        "array": (list,),
        "object": (dict,),
    }

    for key, value in args.items():
        if key not in properties:
            # additionalProperties — skip unknown fields by default
            continue

        prop_schema = properties[key]
        expected = prop_schema.get("type")

        if expected and expected in _TYPE_MAP:
            if not isinstance(value, _TYPE_MAP[expected]):
                errors.append(
                    f"{key}: expected type '{expected}', "
                    f"got '{type(None).__name__}'"
                )
                continue

        # Enum
        enum_values = prop_schema.get("enum")
        if enum_values is not None and value not in enum_values:
            errors.append(
                f"{key}: value {value!r} not in allowed values {enum_values}"
            )

        # Min / max (numeric)
        if isinstance(value, (int, float)):
            mn = prop_schema.get("minimum")
            mx = prop_schema.get("maximum")
            if mn is not None and value < mn:
                errors.append(f"{key}: {value} < minimum {mn}")
            if mx is not None and value > mx:
                errors.append(f"{key}: {value} > maximum {mx}")

        # Pattern (string)
        if isinstance(value, str):
            import re

            pattern = prop_schema.get("pattern")
            if pattern and not re.search(pattern, value):
                errors.append(
                    f"{key}: value {value!r} does not match pattern {pattern!r}"
                )

    return errors


def x__validate_builtin__mutmut_44(
    args: dict[str, Any],
    schema: dict[str, Any],
    tool_name: str,
) -> list[str]:
    """Lightweight fallback validation without ``jsonschema``."""
    errors: list[str] = []
    properties = schema.get("properties", {})
    required = set(schema.get("required", []))

    # Required field check
    for req in required:
        if req not in args:
            errors.append(f"{req}: required field is missing")

    # Type checks
    _TYPE_MAP: dict[str, tuple[type, ...]] = {
        "string": (str,),
        "integer": (int,),
        "number": (int, float),
        "boolean": (bool,),
        "array": (list,),
        "object": (dict,),
    }

    for key, value in args.items():
        if key not in properties:
            # additionalProperties — skip unknown fields by default
            continue

        prop_schema = properties[key]
        expected = prop_schema.get("type")

        if expected and expected in _TYPE_MAP:
            if not isinstance(value, _TYPE_MAP[expected]):
                errors.append(
                    f"{key}: expected type '{expected}', "
                    f"got '{type(value).__name__}'"
                )
                break

        # Enum
        enum_values = prop_schema.get("enum")
        if enum_values is not None and value not in enum_values:
            errors.append(
                f"{key}: value {value!r} not in allowed values {enum_values}"
            )

        # Min / max (numeric)
        if isinstance(value, (int, float)):
            mn = prop_schema.get("minimum")
            mx = prop_schema.get("maximum")
            if mn is not None and value < mn:
                errors.append(f"{key}: {value} < minimum {mn}")
            if mx is not None and value > mx:
                errors.append(f"{key}: {value} > maximum {mx}")

        # Pattern (string)
        if isinstance(value, str):
            import re

            pattern = prop_schema.get("pattern")
            if pattern and not re.search(pattern, value):
                errors.append(
                    f"{key}: value {value!r} does not match pattern {pattern!r}"
                )

    return errors


def x__validate_builtin__mutmut_45(
    args: dict[str, Any],
    schema: dict[str, Any],
    tool_name: str,
) -> list[str]:
    """Lightweight fallback validation without ``jsonschema``."""
    errors: list[str] = []
    properties = schema.get("properties", {})
    required = set(schema.get("required", []))

    # Required field check
    for req in required:
        if req not in args:
            errors.append(f"{req}: required field is missing")

    # Type checks
    _TYPE_MAP: dict[str, tuple[type, ...]] = {
        "string": (str,),
        "integer": (int,),
        "number": (int, float),
        "boolean": (bool,),
        "array": (list,),
        "object": (dict,),
    }

    for key, value in args.items():
        if key not in properties:
            # additionalProperties — skip unknown fields by default
            continue

        prop_schema = properties[key]
        expected = prop_schema.get("type")

        if expected and expected in _TYPE_MAP:
            if not isinstance(value, _TYPE_MAP[expected]):
                errors.append(
                    f"{key}: expected type '{expected}', "
                    f"got '{type(value).__name__}'"
                )
                continue

        # Enum
        enum_values = None
        if enum_values is not None and value not in enum_values:
            errors.append(
                f"{key}: value {value!r} not in allowed values {enum_values}"
            )

        # Min / max (numeric)
        if isinstance(value, (int, float)):
            mn = prop_schema.get("minimum")
            mx = prop_schema.get("maximum")
            if mn is not None and value < mn:
                errors.append(f"{key}: {value} < minimum {mn}")
            if mx is not None and value > mx:
                errors.append(f"{key}: {value} > maximum {mx}")

        # Pattern (string)
        if isinstance(value, str):
            import re

            pattern = prop_schema.get("pattern")
            if pattern and not re.search(pattern, value):
                errors.append(
                    f"{key}: value {value!r} does not match pattern {pattern!r}"
                )

    return errors


def x__validate_builtin__mutmut_46(
    args: dict[str, Any],
    schema: dict[str, Any],
    tool_name: str,
) -> list[str]:
    """Lightweight fallback validation without ``jsonschema``."""
    errors: list[str] = []
    properties = schema.get("properties", {})
    required = set(schema.get("required", []))

    # Required field check
    for req in required:
        if req not in args:
            errors.append(f"{req}: required field is missing")

    # Type checks
    _TYPE_MAP: dict[str, tuple[type, ...]] = {
        "string": (str,),
        "integer": (int,),
        "number": (int, float),
        "boolean": (bool,),
        "array": (list,),
        "object": (dict,),
    }

    for key, value in args.items():
        if key not in properties:
            # additionalProperties — skip unknown fields by default
            continue

        prop_schema = properties[key]
        expected = prop_schema.get("type")

        if expected and expected in _TYPE_MAP:
            if not isinstance(value, _TYPE_MAP[expected]):
                errors.append(
                    f"{key}: expected type '{expected}', "
                    f"got '{type(value).__name__}'"
                )
                continue

        # Enum
        enum_values = prop_schema.get(None)
        if enum_values is not None and value not in enum_values:
            errors.append(
                f"{key}: value {value!r} not in allowed values {enum_values}"
            )

        # Min / max (numeric)
        if isinstance(value, (int, float)):
            mn = prop_schema.get("minimum")
            mx = prop_schema.get("maximum")
            if mn is not None and value < mn:
                errors.append(f"{key}: {value} < minimum {mn}")
            if mx is not None and value > mx:
                errors.append(f"{key}: {value} > maximum {mx}")

        # Pattern (string)
        if isinstance(value, str):
            import re

            pattern = prop_schema.get("pattern")
            if pattern and not re.search(pattern, value):
                errors.append(
                    f"{key}: value {value!r} does not match pattern {pattern!r}"
                )

    return errors


def x__validate_builtin__mutmut_47(
    args: dict[str, Any],
    schema: dict[str, Any],
    tool_name: str,
) -> list[str]:
    """Lightweight fallback validation without ``jsonschema``."""
    errors: list[str] = []
    properties = schema.get("properties", {})
    required = set(schema.get("required", []))

    # Required field check
    for req in required:
        if req not in args:
            errors.append(f"{req}: required field is missing")

    # Type checks
    _TYPE_MAP: dict[str, tuple[type, ...]] = {
        "string": (str,),
        "integer": (int,),
        "number": (int, float),
        "boolean": (bool,),
        "array": (list,),
        "object": (dict,),
    }

    for key, value in args.items():
        if key not in properties:
            # additionalProperties — skip unknown fields by default
            continue

        prop_schema = properties[key]
        expected = prop_schema.get("type")

        if expected and expected in _TYPE_MAP:
            if not isinstance(value, _TYPE_MAP[expected]):
                errors.append(
                    f"{key}: expected type '{expected}', "
                    f"got '{type(value).__name__}'"
                )
                continue

        # Enum
        enum_values = prop_schema.get("XXenumXX")
        if enum_values is not None and value not in enum_values:
            errors.append(
                f"{key}: value {value!r} not in allowed values {enum_values}"
            )

        # Min / max (numeric)
        if isinstance(value, (int, float)):
            mn = prop_schema.get("minimum")
            mx = prop_schema.get("maximum")
            if mn is not None and value < mn:
                errors.append(f"{key}: {value} < minimum {mn}")
            if mx is not None and value > mx:
                errors.append(f"{key}: {value} > maximum {mx}")

        # Pattern (string)
        if isinstance(value, str):
            import re

            pattern = prop_schema.get("pattern")
            if pattern and not re.search(pattern, value):
                errors.append(
                    f"{key}: value {value!r} does not match pattern {pattern!r}"
                )

    return errors


def x__validate_builtin__mutmut_48(
    args: dict[str, Any],
    schema: dict[str, Any],
    tool_name: str,
) -> list[str]:
    """Lightweight fallback validation without ``jsonschema``."""
    errors: list[str] = []
    properties = schema.get("properties", {})
    required = set(schema.get("required", []))

    # Required field check
    for req in required:
        if req not in args:
            errors.append(f"{req}: required field is missing")

    # Type checks
    _TYPE_MAP: dict[str, tuple[type, ...]] = {
        "string": (str,),
        "integer": (int,),
        "number": (int, float),
        "boolean": (bool,),
        "array": (list,),
        "object": (dict,),
    }

    for key, value in args.items():
        if key not in properties:
            # additionalProperties — skip unknown fields by default
            continue

        prop_schema = properties[key]
        expected = prop_schema.get("type")

        if expected and expected in _TYPE_MAP:
            if not isinstance(value, _TYPE_MAP[expected]):
                errors.append(
                    f"{key}: expected type '{expected}', "
                    f"got '{type(value).__name__}'"
                )
                continue

        # Enum
        enum_values = prop_schema.get("ENUM")
        if enum_values is not None and value not in enum_values:
            errors.append(
                f"{key}: value {value!r} not in allowed values {enum_values}"
            )

        # Min / max (numeric)
        if isinstance(value, (int, float)):
            mn = prop_schema.get("minimum")
            mx = prop_schema.get("maximum")
            if mn is not None and value < mn:
                errors.append(f"{key}: {value} < minimum {mn}")
            if mx is not None and value > mx:
                errors.append(f"{key}: {value} > maximum {mx}")

        # Pattern (string)
        if isinstance(value, str):
            import re

            pattern = prop_schema.get("pattern")
            if pattern and not re.search(pattern, value):
                errors.append(
                    f"{key}: value {value!r} does not match pattern {pattern!r}"
                )

    return errors


def x__validate_builtin__mutmut_49(
    args: dict[str, Any],
    schema: dict[str, Any],
    tool_name: str,
) -> list[str]:
    """Lightweight fallback validation without ``jsonschema``."""
    errors: list[str] = []
    properties = schema.get("properties", {})
    required = set(schema.get("required", []))

    # Required field check
    for req in required:
        if req not in args:
            errors.append(f"{req}: required field is missing")

    # Type checks
    _TYPE_MAP: dict[str, tuple[type, ...]] = {
        "string": (str,),
        "integer": (int,),
        "number": (int, float),
        "boolean": (bool,),
        "array": (list,),
        "object": (dict,),
    }

    for key, value in args.items():
        if key not in properties:
            # additionalProperties — skip unknown fields by default
            continue

        prop_schema = properties[key]
        expected = prop_schema.get("type")

        if expected and expected in _TYPE_MAP:
            if not isinstance(value, _TYPE_MAP[expected]):
                errors.append(
                    f"{key}: expected type '{expected}', "
                    f"got '{type(value).__name__}'"
                )
                continue

        # Enum
        enum_values = prop_schema.get("enum")
        if enum_values is not None or value not in enum_values:
            errors.append(
                f"{key}: value {value!r} not in allowed values {enum_values}"
            )

        # Min / max (numeric)
        if isinstance(value, (int, float)):
            mn = prop_schema.get("minimum")
            mx = prop_schema.get("maximum")
            if mn is not None and value < mn:
                errors.append(f"{key}: {value} < minimum {mn}")
            if mx is not None and value > mx:
                errors.append(f"{key}: {value} > maximum {mx}")

        # Pattern (string)
        if isinstance(value, str):
            import re

            pattern = prop_schema.get("pattern")
            if pattern and not re.search(pattern, value):
                errors.append(
                    f"{key}: value {value!r} does not match pattern {pattern!r}"
                )

    return errors


def x__validate_builtin__mutmut_50(
    args: dict[str, Any],
    schema: dict[str, Any],
    tool_name: str,
) -> list[str]:
    """Lightweight fallback validation without ``jsonschema``."""
    errors: list[str] = []
    properties = schema.get("properties", {})
    required = set(schema.get("required", []))

    # Required field check
    for req in required:
        if req not in args:
            errors.append(f"{req}: required field is missing")

    # Type checks
    _TYPE_MAP: dict[str, tuple[type, ...]] = {
        "string": (str,),
        "integer": (int,),
        "number": (int, float),
        "boolean": (bool,),
        "array": (list,),
        "object": (dict,),
    }

    for key, value in args.items():
        if key not in properties:
            # additionalProperties — skip unknown fields by default
            continue

        prop_schema = properties[key]
        expected = prop_schema.get("type")

        if expected and expected in _TYPE_MAP:
            if not isinstance(value, _TYPE_MAP[expected]):
                errors.append(
                    f"{key}: expected type '{expected}', "
                    f"got '{type(value).__name__}'"
                )
                continue

        # Enum
        enum_values = prop_schema.get("enum")
        if enum_values is None and value not in enum_values:
            errors.append(
                f"{key}: value {value!r} not in allowed values {enum_values}"
            )

        # Min / max (numeric)
        if isinstance(value, (int, float)):
            mn = prop_schema.get("minimum")
            mx = prop_schema.get("maximum")
            if mn is not None and value < mn:
                errors.append(f"{key}: {value} < minimum {mn}")
            if mx is not None and value > mx:
                errors.append(f"{key}: {value} > maximum {mx}")

        # Pattern (string)
        if isinstance(value, str):
            import re

            pattern = prop_schema.get("pattern")
            if pattern and not re.search(pattern, value):
                errors.append(
                    f"{key}: value {value!r} does not match pattern {pattern!r}"
                )

    return errors


def x__validate_builtin__mutmut_51(
    args: dict[str, Any],
    schema: dict[str, Any],
    tool_name: str,
) -> list[str]:
    """Lightweight fallback validation without ``jsonschema``."""
    errors: list[str] = []
    properties = schema.get("properties", {})
    required = set(schema.get("required", []))

    # Required field check
    for req in required:
        if req not in args:
            errors.append(f"{req}: required field is missing")

    # Type checks
    _TYPE_MAP: dict[str, tuple[type, ...]] = {
        "string": (str,),
        "integer": (int,),
        "number": (int, float),
        "boolean": (bool,),
        "array": (list,),
        "object": (dict,),
    }

    for key, value in args.items():
        if key not in properties:
            # additionalProperties — skip unknown fields by default
            continue

        prop_schema = properties[key]
        expected = prop_schema.get("type")

        if expected and expected in _TYPE_MAP:
            if not isinstance(value, _TYPE_MAP[expected]):
                errors.append(
                    f"{key}: expected type '{expected}', "
                    f"got '{type(value).__name__}'"
                )
                continue

        # Enum
        enum_values = prop_schema.get("enum")
        if enum_values is not None and value in enum_values:
            errors.append(
                f"{key}: value {value!r} not in allowed values {enum_values}"
            )

        # Min / max (numeric)
        if isinstance(value, (int, float)):
            mn = prop_schema.get("minimum")
            mx = prop_schema.get("maximum")
            if mn is not None and value < mn:
                errors.append(f"{key}: {value} < minimum {mn}")
            if mx is not None and value > mx:
                errors.append(f"{key}: {value} > maximum {mx}")

        # Pattern (string)
        if isinstance(value, str):
            import re

            pattern = prop_schema.get("pattern")
            if pattern and not re.search(pattern, value):
                errors.append(
                    f"{key}: value {value!r} does not match pattern {pattern!r}"
                )

    return errors


def x__validate_builtin__mutmut_52(
    args: dict[str, Any],
    schema: dict[str, Any],
    tool_name: str,
) -> list[str]:
    """Lightweight fallback validation without ``jsonschema``."""
    errors: list[str] = []
    properties = schema.get("properties", {})
    required = set(schema.get("required", []))

    # Required field check
    for req in required:
        if req not in args:
            errors.append(f"{req}: required field is missing")

    # Type checks
    _TYPE_MAP: dict[str, tuple[type, ...]] = {
        "string": (str,),
        "integer": (int,),
        "number": (int, float),
        "boolean": (bool,),
        "array": (list,),
        "object": (dict,),
    }

    for key, value in args.items():
        if key not in properties:
            # additionalProperties — skip unknown fields by default
            continue

        prop_schema = properties[key]
        expected = prop_schema.get("type")

        if expected and expected in _TYPE_MAP:
            if not isinstance(value, _TYPE_MAP[expected]):
                errors.append(
                    f"{key}: expected type '{expected}', "
                    f"got '{type(value).__name__}'"
                )
                continue

        # Enum
        enum_values = prop_schema.get("enum")
        if enum_values is not None and value not in enum_values:
            errors.append(
                None
            )

        # Min / max (numeric)
        if isinstance(value, (int, float)):
            mn = prop_schema.get("minimum")
            mx = prop_schema.get("maximum")
            if mn is not None and value < mn:
                errors.append(f"{key}: {value} < minimum {mn}")
            if mx is not None and value > mx:
                errors.append(f"{key}: {value} > maximum {mx}")

        # Pattern (string)
        if isinstance(value, str):
            import re

            pattern = prop_schema.get("pattern")
            if pattern and not re.search(pattern, value):
                errors.append(
                    f"{key}: value {value!r} does not match pattern {pattern!r}"
                )

    return errors


def x__validate_builtin__mutmut_53(
    args: dict[str, Any],
    schema: dict[str, Any],
    tool_name: str,
) -> list[str]:
    """Lightweight fallback validation without ``jsonschema``."""
    errors: list[str] = []
    properties = schema.get("properties", {})
    required = set(schema.get("required", []))

    # Required field check
    for req in required:
        if req not in args:
            errors.append(f"{req}: required field is missing")

    # Type checks
    _TYPE_MAP: dict[str, tuple[type, ...]] = {
        "string": (str,),
        "integer": (int,),
        "number": (int, float),
        "boolean": (bool,),
        "array": (list,),
        "object": (dict,),
    }

    for key, value in args.items():
        if key not in properties:
            # additionalProperties — skip unknown fields by default
            continue

        prop_schema = properties[key]
        expected = prop_schema.get("type")

        if expected and expected in _TYPE_MAP:
            if not isinstance(value, _TYPE_MAP[expected]):
                errors.append(
                    f"{key}: expected type '{expected}', "
                    f"got '{type(value).__name__}'"
                )
                continue

        # Enum
        enum_values = prop_schema.get("enum")
        if enum_values is not None and value not in enum_values:
            errors.append(
                f"{key}: value {value!r} not in allowed values {enum_values}"
            )

        # Min / max (numeric)
        if isinstance(value, (int, float)):
            mn = None
            mx = prop_schema.get("maximum")
            if mn is not None and value < mn:
                errors.append(f"{key}: {value} < minimum {mn}")
            if mx is not None and value > mx:
                errors.append(f"{key}: {value} > maximum {mx}")

        # Pattern (string)
        if isinstance(value, str):
            import re

            pattern = prop_schema.get("pattern")
            if pattern and not re.search(pattern, value):
                errors.append(
                    f"{key}: value {value!r} does not match pattern {pattern!r}"
                )

    return errors


def x__validate_builtin__mutmut_54(
    args: dict[str, Any],
    schema: dict[str, Any],
    tool_name: str,
) -> list[str]:
    """Lightweight fallback validation without ``jsonschema``."""
    errors: list[str] = []
    properties = schema.get("properties", {})
    required = set(schema.get("required", []))

    # Required field check
    for req in required:
        if req not in args:
            errors.append(f"{req}: required field is missing")

    # Type checks
    _TYPE_MAP: dict[str, tuple[type, ...]] = {
        "string": (str,),
        "integer": (int,),
        "number": (int, float),
        "boolean": (bool,),
        "array": (list,),
        "object": (dict,),
    }

    for key, value in args.items():
        if key not in properties:
            # additionalProperties — skip unknown fields by default
            continue

        prop_schema = properties[key]
        expected = prop_schema.get("type")

        if expected and expected in _TYPE_MAP:
            if not isinstance(value, _TYPE_MAP[expected]):
                errors.append(
                    f"{key}: expected type '{expected}', "
                    f"got '{type(value).__name__}'"
                )
                continue

        # Enum
        enum_values = prop_schema.get("enum")
        if enum_values is not None and value not in enum_values:
            errors.append(
                f"{key}: value {value!r} not in allowed values {enum_values}"
            )

        # Min / max (numeric)
        if isinstance(value, (int, float)):
            mn = prop_schema.get(None)
            mx = prop_schema.get("maximum")
            if mn is not None and value < mn:
                errors.append(f"{key}: {value} < minimum {mn}")
            if mx is not None and value > mx:
                errors.append(f"{key}: {value} > maximum {mx}")

        # Pattern (string)
        if isinstance(value, str):
            import re

            pattern = prop_schema.get("pattern")
            if pattern and not re.search(pattern, value):
                errors.append(
                    f"{key}: value {value!r} does not match pattern {pattern!r}"
                )

    return errors


def x__validate_builtin__mutmut_55(
    args: dict[str, Any],
    schema: dict[str, Any],
    tool_name: str,
) -> list[str]:
    """Lightweight fallback validation without ``jsonschema``."""
    errors: list[str] = []
    properties = schema.get("properties", {})
    required = set(schema.get("required", []))

    # Required field check
    for req in required:
        if req not in args:
            errors.append(f"{req}: required field is missing")

    # Type checks
    _TYPE_MAP: dict[str, tuple[type, ...]] = {
        "string": (str,),
        "integer": (int,),
        "number": (int, float),
        "boolean": (bool,),
        "array": (list,),
        "object": (dict,),
    }

    for key, value in args.items():
        if key not in properties:
            # additionalProperties — skip unknown fields by default
            continue

        prop_schema = properties[key]
        expected = prop_schema.get("type")

        if expected and expected in _TYPE_MAP:
            if not isinstance(value, _TYPE_MAP[expected]):
                errors.append(
                    f"{key}: expected type '{expected}', "
                    f"got '{type(value).__name__}'"
                )
                continue

        # Enum
        enum_values = prop_schema.get("enum")
        if enum_values is not None and value not in enum_values:
            errors.append(
                f"{key}: value {value!r} not in allowed values {enum_values}"
            )

        # Min / max (numeric)
        if isinstance(value, (int, float)):
            mn = prop_schema.get("XXminimumXX")
            mx = prop_schema.get("maximum")
            if mn is not None and value < mn:
                errors.append(f"{key}: {value} < minimum {mn}")
            if mx is not None and value > mx:
                errors.append(f"{key}: {value} > maximum {mx}")

        # Pattern (string)
        if isinstance(value, str):
            import re

            pattern = prop_schema.get("pattern")
            if pattern and not re.search(pattern, value):
                errors.append(
                    f"{key}: value {value!r} does not match pattern {pattern!r}"
                )

    return errors


def x__validate_builtin__mutmut_56(
    args: dict[str, Any],
    schema: dict[str, Any],
    tool_name: str,
) -> list[str]:
    """Lightweight fallback validation without ``jsonschema``."""
    errors: list[str] = []
    properties = schema.get("properties", {})
    required = set(schema.get("required", []))

    # Required field check
    for req in required:
        if req not in args:
            errors.append(f"{req}: required field is missing")

    # Type checks
    _TYPE_MAP: dict[str, tuple[type, ...]] = {
        "string": (str,),
        "integer": (int,),
        "number": (int, float),
        "boolean": (bool,),
        "array": (list,),
        "object": (dict,),
    }

    for key, value in args.items():
        if key not in properties:
            # additionalProperties — skip unknown fields by default
            continue

        prop_schema = properties[key]
        expected = prop_schema.get("type")

        if expected and expected in _TYPE_MAP:
            if not isinstance(value, _TYPE_MAP[expected]):
                errors.append(
                    f"{key}: expected type '{expected}', "
                    f"got '{type(value).__name__}'"
                )
                continue

        # Enum
        enum_values = prop_schema.get("enum")
        if enum_values is not None and value not in enum_values:
            errors.append(
                f"{key}: value {value!r} not in allowed values {enum_values}"
            )

        # Min / max (numeric)
        if isinstance(value, (int, float)):
            mn = prop_schema.get("MINIMUM")
            mx = prop_schema.get("maximum")
            if mn is not None and value < mn:
                errors.append(f"{key}: {value} < minimum {mn}")
            if mx is not None and value > mx:
                errors.append(f"{key}: {value} > maximum {mx}")

        # Pattern (string)
        if isinstance(value, str):
            import re

            pattern = prop_schema.get("pattern")
            if pattern and not re.search(pattern, value):
                errors.append(
                    f"{key}: value {value!r} does not match pattern {pattern!r}"
                )

    return errors


def x__validate_builtin__mutmut_57(
    args: dict[str, Any],
    schema: dict[str, Any],
    tool_name: str,
) -> list[str]:
    """Lightweight fallback validation without ``jsonschema``."""
    errors: list[str] = []
    properties = schema.get("properties", {})
    required = set(schema.get("required", []))

    # Required field check
    for req in required:
        if req not in args:
            errors.append(f"{req}: required field is missing")

    # Type checks
    _TYPE_MAP: dict[str, tuple[type, ...]] = {
        "string": (str,),
        "integer": (int,),
        "number": (int, float),
        "boolean": (bool,),
        "array": (list,),
        "object": (dict,),
    }

    for key, value in args.items():
        if key not in properties:
            # additionalProperties — skip unknown fields by default
            continue

        prop_schema = properties[key]
        expected = prop_schema.get("type")

        if expected and expected in _TYPE_MAP:
            if not isinstance(value, _TYPE_MAP[expected]):
                errors.append(
                    f"{key}: expected type '{expected}', "
                    f"got '{type(value).__name__}'"
                )
                continue

        # Enum
        enum_values = prop_schema.get("enum")
        if enum_values is not None and value not in enum_values:
            errors.append(
                f"{key}: value {value!r} not in allowed values {enum_values}"
            )

        # Min / max (numeric)
        if isinstance(value, (int, float)):
            mn = prop_schema.get("minimum")
            mx = None
            if mn is not None and value < mn:
                errors.append(f"{key}: {value} < minimum {mn}")
            if mx is not None and value > mx:
                errors.append(f"{key}: {value} > maximum {mx}")

        # Pattern (string)
        if isinstance(value, str):
            import re

            pattern = prop_schema.get("pattern")
            if pattern and not re.search(pattern, value):
                errors.append(
                    f"{key}: value {value!r} does not match pattern {pattern!r}"
                )

    return errors


def x__validate_builtin__mutmut_58(
    args: dict[str, Any],
    schema: dict[str, Any],
    tool_name: str,
) -> list[str]:
    """Lightweight fallback validation without ``jsonschema``."""
    errors: list[str] = []
    properties = schema.get("properties", {})
    required = set(schema.get("required", []))

    # Required field check
    for req in required:
        if req not in args:
            errors.append(f"{req}: required field is missing")

    # Type checks
    _TYPE_MAP: dict[str, tuple[type, ...]] = {
        "string": (str,),
        "integer": (int,),
        "number": (int, float),
        "boolean": (bool,),
        "array": (list,),
        "object": (dict,),
    }

    for key, value in args.items():
        if key not in properties:
            # additionalProperties — skip unknown fields by default
            continue

        prop_schema = properties[key]
        expected = prop_schema.get("type")

        if expected and expected in _TYPE_MAP:
            if not isinstance(value, _TYPE_MAP[expected]):
                errors.append(
                    f"{key}: expected type '{expected}', "
                    f"got '{type(value).__name__}'"
                )
                continue

        # Enum
        enum_values = prop_schema.get("enum")
        if enum_values is not None and value not in enum_values:
            errors.append(
                f"{key}: value {value!r} not in allowed values {enum_values}"
            )

        # Min / max (numeric)
        if isinstance(value, (int, float)):
            mn = prop_schema.get("minimum")
            mx = prop_schema.get(None)
            if mn is not None and value < mn:
                errors.append(f"{key}: {value} < minimum {mn}")
            if mx is not None and value > mx:
                errors.append(f"{key}: {value} > maximum {mx}")

        # Pattern (string)
        if isinstance(value, str):
            import re

            pattern = prop_schema.get("pattern")
            if pattern and not re.search(pattern, value):
                errors.append(
                    f"{key}: value {value!r} does not match pattern {pattern!r}"
                )

    return errors


def x__validate_builtin__mutmut_59(
    args: dict[str, Any],
    schema: dict[str, Any],
    tool_name: str,
) -> list[str]:
    """Lightweight fallback validation without ``jsonschema``."""
    errors: list[str] = []
    properties = schema.get("properties", {})
    required = set(schema.get("required", []))

    # Required field check
    for req in required:
        if req not in args:
            errors.append(f"{req}: required field is missing")

    # Type checks
    _TYPE_MAP: dict[str, tuple[type, ...]] = {
        "string": (str,),
        "integer": (int,),
        "number": (int, float),
        "boolean": (bool,),
        "array": (list,),
        "object": (dict,),
    }

    for key, value in args.items():
        if key not in properties:
            # additionalProperties — skip unknown fields by default
            continue

        prop_schema = properties[key]
        expected = prop_schema.get("type")

        if expected and expected in _TYPE_MAP:
            if not isinstance(value, _TYPE_MAP[expected]):
                errors.append(
                    f"{key}: expected type '{expected}', "
                    f"got '{type(value).__name__}'"
                )
                continue

        # Enum
        enum_values = prop_schema.get("enum")
        if enum_values is not None and value not in enum_values:
            errors.append(
                f"{key}: value {value!r} not in allowed values {enum_values}"
            )

        # Min / max (numeric)
        if isinstance(value, (int, float)):
            mn = prop_schema.get("minimum")
            mx = prop_schema.get("XXmaximumXX")
            if mn is not None and value < mn:
                errors.append(f"{key}: {value} < minimum {mn}")
            if mx is not None and value > mx:
                errors.append(f"{key}: {value} > maximum {mx}")

        # Pattern (string)
        if isinstance(value, str):
            import re

            pattern = prop_schema.get("pattern")
            if pattern and not re.search(pattern, value):
                errors.append(
                    f"{key}: value {value!r} does not match pattern {pattern!r}"
                )

    return errors


def x__validate_builtin__mutmut_60(
    args: dict[str, Any],
    schema: dict[str, Any],
    tool_name: str,
) -> list[str]:
    """Lightweight fallback validation without ``jsonschema``."""
    errors: list[str] = []
    properties = schema.get("properties", {})
    required = set(schema.get("required", []))

    # Required field check
    for req in required:
        if req not in args:
            errors.append(f"{req}: required field is missing")

    # Type checks
    _TYPE_MAP: dict[str, tuple[type, ...]] = {
        "string": (str,),
        "integer": (int,),
        "number": (int, float),
        "boolean": (bool,),
        "array": (list,),
        "object": (dict,),
    }

    for key, value in args.items():
        if key not in properties:
            # additionalProperties — skip unknown fields by default
            continue

        prop_schema = properties[key]
        expected = prop_schema.get("type")

        if expected and expected in _TYPE_MAP:
            if not isinstance(value, _TYPE_MAP[expected]):
                errors.append(
                    f"{key}: expected type '{expected}', "
                    f"got '{type(value).__name__}'"
                )
                continue

        # Enum
        enum_values = prop_schema.get("enum")
        if enum_values is not None and value not in enum_values:
            errors.append(
                f"{key}: value {value!r} not in allowed values {enum_values}"
            )

        # Min / max (numeric)
        if isinstance(value, (int, float)):
            mn = prop_schema.get("minimum")
            mx = prop_schema.get("MAXIMUM")
            if mn is not None and value < mn:
                errors.append(f"{key}: {value} < minimum {mn}")
            if mx is not None and value > mx:
                errors.append(f"{key}: {value} > maximum {mx}")

        # Pattern (string)
        if isinstance(value, str):
            import re

            pattern = prop_schema.get("pattern")
            if pattern and not re.search(pattern, value):
                errors.append(
                    f"{key}: value {value!r} does not match pattern {pattern!r}"
                )

    return errors


def x__validate_builtin__mutmut_61(
    args: dict[str, Any],
    schema: dict[str, Any],
    tool_name: str,
) -> list[str]:
    """Lightweight fallback validation without ``jsonschema``."""
    errors: list[str] = []
    properties = schema.get("properties", {})
    required = set(schema.get("required", []))

    # Required field check
    for req in required:
        if req not in args:
            errors.append(f"{req}: required field is missing")

    # Type checks
    _TYPE_MAP: dict[str, tuple[type, ...]] = {
        "string": (str,),
        "integer": (int,),
        "number": (int, float),
        "boolean": (bool,),
        "array": (list,),
        "object": (dict,),
    }

    for key, value in args.items():
        if key not in properties:
            # additionalProperties — skip unknown fields by default
            continue

        prop_schema = properties[key]
        expected = prop_schema.get("type")

        if expected and expected in _TYPE_MAP:
            if not isinstance(value, _TYPE_MAP[expected]):
                errors.append(
                    f"{key}: expected type '{expected}', "
                    f"got '{type(value).__name__}'"
                )
                continue

        # Enum
        enum_values = prop_schema.get("enum")
        if enum_values is not None and value not in enum_values:
            errors.append(
                f"{key}: value {value!r} not in allowed values {enum_values}"
            )

        # Min / max (numeric)
        if isinstance(value, (int, float)):
            mn = prop_schema.get("minimum")
            mx = prop_schema.get("maximum")
            if mn is not None or value < mn:
                errors.append(f"{key}: {value} < minimum {mn}")
            if mx is not None and value > mx:
                errors.append(f"{key}: {value} > maximum {mx}")

        # Pattern (string)
        if isinstance(value, str):
            import re

            pattern = prop_schema.get("pattern")
            if pattern and not re.search(pattern, value):
                errors.append(
                    f"{key}: value {value!r} does not match pattern {pattern!r}"
                )

    return errors


def x__validate_builtin__mutmut_62(
    args: dict[str, Any],
    schema: dict[str, Any],
    tool_name: str,
) -> list[str]:
    """Lightweight fallback validation without ``jsonschema``."""
    errors: list[str] = []
    properties = schema.get("properties", {})
    required = set(schema.get("required", []))

    # Required field check
    for req in required:
        if req not in args:
            errors.append(f"{req}: required field is missing")

    # Type checks
    _TYPE_MAP: dict[str, tuple[type, ...]] = {
        "string": (str,),
        "integer": (int,),
        "number": (int, float),
        "boolean": (bool,),
        "array": (list,),
        "object": (dict,),
    }

    for key, value in args.items():
        if key not in properties:
            # additionalProperties — skip unknown fields by default
            continue

        prop_schema = properties[key]
        expected = prop_schema.get("type")

        if expected and expected in _TYPE_MAP:
            if not isinstance(value, _TYPE_MAP[expected]):
                errors.append(
                    f"{key}: expected type '{expected}', "
                    f"got '{type(value).__name__}'"
                )
                continue

        # Enum
        enum_values = prop_schema.get("enum")
        if enum_values is not None and value not in enum_values:
            errors.append(
                f"{key}: value {value!r} not in allowed values {enum_values}"
            )

        # Min / max (numeric)
        if isinstance(value, (int, float)):
            mn = prop_schema.get("minimum")
            mx = prop_schema.get("maximum")
            if mn is None and value < mn:
                errors.append(f"{key}: {value} < minimum {mn}")
            if mx is not None and value > mx:
                errors.append(f"{key}: {value} > maximum {mx}")

        # Pattern (string)
        if isinstance(value, str):
            import re

            pattern = prop_schema.get("pattern")
            if pattern and not re.search(pattern, value):
                errors.append(
                    f"{key}: value {value!r} does not match pattern {pattern!r}"
                )

    return errors


def x__validate_builtin__mutmut_63(
    args: dict[str, Any],
    schema: dict[str, Any],
    tool_name: str,
) -> list[str]:
    """Lightweight fallback validation without ``jsonschema``."""
    errors: list[str] = []
    properties = schema.get("properties", {})
    required = set(schema.get("required", []))

    # Required field check
    for req in required:
        if req not in args:
            errors.append(f"{req}: required field is missing")

    # Type checks
    _TYPE_MAP: dict[str, tuple[type, ...]] = {
        "string": (str,),
        "integer": (int,),
        "number": (int, float),
        "boolean": (bool,),
        "array": (list,),
        "object": (dict,),
    }

    for key, value in args.items():
        if key not in properties:
            # additionalProperties — skip unknown fields by default
            continue

        prop_schema = properties[key]
        expected = prop_schema.get("type")

        if expected and expected in _TYPE_MAP:
            if not isinstance(value, _TYPE_MAP[expected]):
                errors.append(
                    f"{key}: expected type '{expected}', "
                    f"got '{type(value).__name__}'"
                )
                continue

        # Enum
        enum_values = prop_schema.get("enum")
        if enum_values is not None and value not in enum_values:
            errors.append(
                f"{key}: value {value!r} not in allowed values {enum_values}"
            )

        # Min / max (numeric)
        if isinstance(value, (int, float)):
            mn = prop_schema.get("minimum")
            mx = prop_schema.get("maximum")
            if mn is not None and value <= mn:
                errors.append(f"{key}: {value} < minimum {mn}")
            if mx is not None and value > mx:
                errors.append(f"{key}: {value} > maximum {mx}")

        # Pattern (string)
        if isinstance(value, str):
            import re

            pattern = prop_schema.get("pattern")
            if pattern and not re.search(pattern, value):
                errors.append(
                    f"{key}: value {value!r} does not match pattern {pattern!r}"
                )

    return errors


def x__validate_builtin__mutmut_64(
    args: dict[str, Any],
    schema: dict[str, Any],
    tool_name: str,
) -> list[str]:
    """Lightweight fallback validation without ``jsonschema``."""
    errors: list[str] = []
    properties = schema.get("properties", {})
    required = set(schema.get("required", []))

    # Required field check
    for req in required:
        if req not in args:
            errors.append(f"{req}: required field is missing")

    # Type checks
    _TYPE_MAP: dict[str, tuple[type, ...]] = {
        "string": (str,),
        "integer": (int,),
        "number": (int, float),
        "boolean": (bool,),
        "array": (list,),
        "object": (dict,),
    }

    for key, value in args.items():
        if key not in properties:
            # additionalProperties — skip unknown fields by default
            continue

        prop_schema = properties[key]
        expected = prop_schema.get("type")

        if expected and expected in _TYPE_MAP:
            if not isinstance(value, _TYPE_MAP[expected]):
                errors.append(
                    f"{key}: expected type '{expected}', "
                    f"got '{type(value).__name__}'"
                )
                continue

        # Enum
        enum_values = prop_schema.get("enum")
        if enum_values is not None and value not in enum_values:
            errors.append(
                f"{key}: value {value!r} not in allowed values {enum_values}"
            )

        # Min / max (numeric)
        if isinstance(value, (int, float)):
            mn = prop_schema.get("minimum")
            mx = prop_schema.get("maximum")
            if mn is not None and value < mn:
                errors.append(None)
            if mx is not None and value > mx:
                errors.append(f"{key}: {value} > maximum {mx}")

        # Pattern (string)
        if isinstance(value, str):
            import re

            pattern = prop_schema.get("pattern")
            if pattern and not re.search(pattern, value):
                errors.append(
                    f"{key}: value {value!r} does not match pattern {pattern!r}"
                )

    return errors


def x__validate_builtin__mutmut_65(
    args: dict[str, Any],
    schema: dict[str, Any],
    tool_name: str,
) -> list[str]:
    """Lightweight fallback validation without ``jsonschema``."""
    errors: list[str] = []
    properties = schema.get("properties", {})
    required = set(schema.get("required", []))

    # Required field check
    for req in required:
        if req not in args:
            errors.append(f"{req}: required field is missing")

    # Type checks
    _TYPE_MAP: dict[str, tuple[type, ...]] = {
        "string": (str,),
        "integer": (int,),
        "number": (int, float),
        "boolean": (bool,),
        "array": (list,),
        "object": (dict,),
    }

    for key, value in args.items():
        if key not in properties:
            # additionalProperties — skip unknown fields by default
            continue

        prop_schema = properties[key]
        expected = prop_schema.get("type")

        if expected and expected in _TYPE_MAP:
            if not isinstance(value, _TYPE_MAP[expected]):
                errors.append(
                    f"{key}: expected type '{expected}', "
                    f"got '{type(value).__name__}'"
                )
                continue

        # Enum
        enum_values = prop_schema.get("enum")
        if enum_values is not None and value not in enum_values:
            errors.append(
                f"{key}: value {value!r} not in allowed values {enum_values}"
            )

        # Min / max (numeric)
        if isinstance(value, (int, float)):
            mn = prop_schema.get("minimum")
            mx = prop_schema.get("maximum")
            if mn is not None and value < mn:
                errors.append(f"{key}: {value} < minimum {mn}")
            if mx is not None or value > mx:
                errors.append(f"{key}: {value} > maximum {mx}")

        # Pattern (string)
        if isinstance(value, str):
            import re

            pattern = prop_schema.get("pattern")
            if pattern and not re.search(pattern, value):
                errors.append(
                    f"{key}: value {value!r} does not match pattern {pattern!r}"
                )

    return errors


def x__validate_builtin__mutmut_66(
    args: dict[str, Any],
    schema: dict[str, Any],
    tool_name: str,
) -> list[str]:
    """Lightweight fallback validation without ``jsonschema``."""
    errors: list[str] = []
    properties = schema.get("properties", {})
    required = set(schema.get("required", []))

    # Required field check
    for req in required:
        if req not in args:
            errors.append(f"{req}: required field is missing")

    # Type checks
    _TYPE_MAP: dict[str, tuple[type, ...]] = {
        "string": (str,),
        "integer": (int,),
        "number": (int, float),
        "boolean": (bool,),
        "array": (list,),
        "object": (dict,),
    }

    for key, value in args.items():
        if key not in properties:
            # additionalProperties — skip unknown fields by default
            continue

        prop_schema = properties[key]
        expected = prop_schema.get("type")

        if expected and expected in _TYPE_MAP:
            if not isinstance(value, _TYPE_MAP[expected]):
                errors.append(
                    f"{key}: expected type '{expected}', "
                    f"got '{type(value).__name__}'"
                )
                continue

        # Enum
        enum_values = prop_schema.get("enum")
        if enum_values is not None and value not in enum_values:
            errors.append(
                f"{key}: value {value!r} not in allowed values {enum_values}"
            )

        # Min / max (numeric)
        if isinstance(value, (int, float)):
            mn = prop_schema.get("minimum")
            mx = prop_schema.get("maximum")
            if mn is not None and value < mn:
                errors.append(f"{key}: {value} < minimum {mn}")
            if mx is None and value > mx:
                errors.append(f"{key}: {value} > maximum {mx}")

        # Pattern (string)
        if isinstance(value, str):
            import re

            pattern = prop_schema.get("pattern")
            if pattern and not re.search(pattern, value):
                errors.append(
                    f"{key}: value {value!r} does not match pattern {pattern!r}"
                )

    return errors


def x__validate_builtin__mutmut_67(
    args: dict[str, Any],
    schema: dict[str, Any],
    tool_name: str,
) -> list[str]:
    """Lightweight fallback validation without ``jsonschema``."""
    errors: list[str] = []
    properties = schema.get("properties", {})
    required = set(schema.get("required", []))

    # Required field check
    for req in required:
        if req not in args:
            errors.append(f"{req}: required field is missing")

    # Type checks
    _TYPE_MAP: dict[str, tuple[type, ...]] = {
        "string": (str,),
        "integer": (int,),
        "number": (int, float),
        "boolean": (bool,),
        "array": (list,),
        "object": (dict,),
    }

    for key, value in args.items():
        if key not in properties:
            # additionalProperties — skip unknown fields by default
            continue

        prop_schema = properties[key]
        expected = prop_schema.get("type")

        if expected and expected in _TYPE_MAP:
            if not isinstance(value, _TYPE_MAP[expected]):
                errors.append(
                    f"{key}: expected type '{expected}', "
                    f"got '{type(value).__name__}'"
                )
                continue

        # Enum
        enum_values = prop_schema.get("enum")
        if enum_values is not None and value not in enum_values:
            errors.append(
                f"{key}: value {value!r} not in allowed values {enum_values}"
            )

        # Min / max (numeric)
        if isinstance(value, (int, float)):
            mn = prop_schema.get("minimum")
            mx = prop_schema.get("maximum")
            if mn is not None and value < mn:
                errors.append(f"{key}: {value} < minimum {mn}")
            if mx is not None and value >= mx:
                errors.append(f"{key}: {value} > maximum {mx}")

        # Pattern (string)
        if isinstance(value, str):
            import re

            pattern = prop_schema.get("pattern")
            if pattern and not re.search(pattern, value):
                errors.append(
                    f"{key}: value {value!r} does not match pattern {pattern!r}"
                )

    return errors


def x__validate_builtin__mutmut_68(
    args: dict[str, Any],
    schema: dict[str, Any],
    tool_name: str,
) -> list[str]:
    """Lightweight fallback validation without ``jsonschema``."""
    errors: list[str] = []
    properties = schema.get("properties", {})
    required = set(schema.get("required", []))

    # Required field check
    for req in required:
        if req not in args:
            errors.append(f"{req}: required field is missing")

    # Type checks
    _TYPE_MAP: dict[str, tuple[type, ...]] = {
        "string": (str,),
        "integer": (int,),
        "number": (int, float),
        "boolean": (bool,),
        "array": (list,),
        "object": (dict,),
    }

    for key, value in args.items():
        if key not in properties:
            # additionalProperties — skip unknown fields by default
            continue

        prop_schema = properties[key]
        expected = prop_schema.get("type")

        if expected and expected in _TYPE_MAP:
            if not isinstance(value, _TYPE_MAP[expected]):
                errors.append(
                    f"{key}: expected type '{expected}', "
                    f"got '{type(value).__name__}'"
                )
                continue

        # Enum
        enum_values = prop_schema.get("enum")
        if enum_values is not None and value not in enum_values:
            errors.append(
                f"{key}: value {value!r} not in allowed values {enum_values}"
            )

        # Min / max (numeric)
        if isinstance(value, (int, float)):
            mn = prop_schema.get("minimum")
            mx = prop_schema.get("maximum")
            if mn is not None and value < mn:
                errors.append(f"{key}: {value} < minimum {mn}")
            if mx is not None and value > mx:
                errors.append(None)

        # Pattern (string)
        if isinstance(value, str):
            import re

            pattern = prop_schema.get("pattern")
            if pattern and not re.search(pattern, value):
                errors.append(
                    f"{key}: value {value!r} does not match pattern {pattern!r}"
                )

    return errors


def x__validate_builtin__mutmut_69(
    args: dict[str, Any],
    schema: dict[str, Any],
    tool_name: str,
) -> list[str]:
    """Lightweight fallback validation without ``jsonschema``."""
    errors: list[str] = []
    properties = schema.get("properties", {})
    required = set(schema.get("required", []))

    # Required field check
    for req in required:
        if req not in args:
            errors.append(f"{req}: required field is missing")

    # Type checks
    _TYPE_MAP: dict[str, tuple[type, ...]] = {
        "string": (str,),
        "integer": (int,),
        "number": (int, float),
        "boolean": (bool,),
        "array": (list,),
        "object": (dict,),
    }

    for key, value in args.items():
        if key not in properties:
            # additionalProperties — skip unknown fields by default
            continue

        prop_schema = properties[key]
        expected = prop_schema.get("type")

        if expected and expected in _TYPE_MAP:
            if not isinstance(value, _TYPE_MAP[expected]):
                errors.append(
                    f"{key}: expected type '{expected}', "
                    f"got '{type(value).__name__}'"
                )
                continue

        # Enum
        enum_values = prop_schema.get("enum")
        if enum_values is not None and value not in enum_values:
            errors.append(
                f"{key}: value {value!r} not in allowed values {enum_values}"
            )

        # Min / max (numeric)
        if isinstance(value, (int, float)):
            mn = prop_schema.get("minimum")
            mx = prop_schema.get("maximum")
            if mn is not None and value < mn:
                errors.append(f"{key}: {value} < minimum {mn}")
            if mx is not None and value > mx:
                errors.append(f"{key}: {value} > maximum {mx}")

        # Pattern (string)
        if isinstance(value, str):
            import re

            pattern = None
            if pattern and not re.search(pattern, value):
                errors.append(
                    f"{key}: value {value!r} does not match pattern {pattern!r}"
                )

    return errors


def x__validate_builtin__mutmut_70(
    args: dict[str, Any],
    schema: dict[str, Any],
    tool_name: str,
) -> list[str]:
    """Lightweight fallback validation without ``jsonschema``."""
    errors: list[str] = []
    properties = schema.get("properties", {})
    required = set(schema.get("required", []))

    # Required field check
    for req in required:
        if req not in args:
            errors.append(f"{req}: required field is missing")

    # Type checks
    _TYPE_MAP: dict[str, tuple[type, ...]] = {
        "string": (str,),
        "integer": (int,),
        "number": (int, float),
        "boolean": (bool,),
        "array": (list,),
        "object": (dict,),
    }

    for key, value in args.items():
        if key not in properties:
            # additionalProperties — skip unknown fields by default
            continue

        prop_schema = properties[key]
        expected = prop_schema.get("type")

        if expected and expected in _TYPE_MAP:
            if not isinstance(value, _TYPE_MAP[expected]):
                errors.append(
                    f"{key}: expected type '{expected}', "
                    f"got '{type(value).__name__}'"
                )
                continue

        # Enum
        enum_values = prop_schema.get("enum")
        if enum_values is not None and value not in enum_values:
            errors.append(
                f"{key}: value {value!r} not in allowed values {enum_values}"
            )

        # Min / max (numeric)
        if isinstance(value, (int, float)):
            mn = prop_schema.get("minimum")
            mx = prop_schema.get("maximum")
            if mn is not None and value < mn:
                errors.append(f"{key}: {value} < minimum {mn}")
            if mx is not None and value > mx:
                errors.append(f"{key}: {value} > maximum {mx}")

        # Pattern (string)
        if isinstance(value, str):
            import re

            pattern = prop_schema.get(None)
            if pattern and not re.search(pattern, value):
                errors.append(
                    f"{key}: value {value!r} does not match pattern {pattern!r}"
                )

    return errors


def x__validate_builtin__mutmut_71(
    args: dict[str, Any],
    schema: dict[str, Any],
    tool_name: str,
) -> list[str]:
    """Lightweight fallback validation without ``jsonschema``."""
    errors: list[str] = []
    properties = schema.get("properties", {})
    required = set(schema.get("required", []))

    # Required field check
    for req in required:
        if req not in args:
            errors.append(f"{req}: required field is missing")

    # Type checks
    _TYPE_MAP: dict[str, tuple[type, ...]] = {
        "string": (str,),
        "integer": (int,),
        "number": (int, float),
        "boolean": (bool,),
        "array": (list,),
        "object": (dict,),
    }

    for key, value in args.items():
        if key not in properties:
            # additionalProperties — skip unknown fields by default
            continue

        prop_schema = properties[key]
        expected = prop_schema.get("type")

        if expected and expected in _TYPE_MAP:
            if not isinstance(value, _TYPE_MAP[expected]):
                errors.append(
                    f"{key}: expected type '{expected}', "
                    f"got '{type(value).__name__}'"
                )
                continue

        # Enum
        enum_values = prop_schema.get("enum")
        if enum_values is not None and value not in enum_values:
            errors.append(
                f"{key}: value {value!r} not in allowed values {enum_values}"
            )

        # Min / max (numeric)
        if isinstance(value, (int, float)):
            mn = prop_schema.get("minimum")
            mx = prop_schema.get("maximum")
            if mn is not None and value < mn:
                errors.append(f"{key}: {value} < minimum {mn}")
            if mx is not None and value > mx:
                errors.append(f"{key}: {value} > maximum {mx}")

        # Pattern (string)
        if isinstance(value, str):
            import re

            pattern = prop_schema.get("XXpatternXX")
            if pattern and not re.search(pattern, value):
                errors.append(
                    f"{key}: value {value!r} does not match pattern {pattern!r}"
                )

    return errors


def x__validate_builtin__mutmut_72(
    args: dict[str, Any],
    schema: dict[str, Any],
    tool_name: str,
) -> list[str]:
    """Lightweight fallback validation without ``jsonschema``."""
    errors: list[str] = []
    properties = schema.get("properties", {})
    required = set(schema.get("required", []))

    # Required field check
    for req in required:
        if req not in args:
            errors.append(f"{req}: required field is missing")

    # Type checks
    _TYPE_MAP: dict[str, tuple[type, ...]] = {
        "string": (str,),
        "integer": (int,),
        "number": (int, float),
        "boolean": (bool,),
        "array": (list,),
        "object": (dict,),
    }

    for key, value in args.items():
        if key not in properties:
            # additionalProperties — skip unknown fields by default
            continue

        prop_schema = properties[key]
        expected = prop_schema.get("type")

        if expected and expected in _TYPE_MAP:
            if not isinstance(value, _TYPE_MAP[expected]):
                errors.append(
                    f"{key}: expected type '{expected}', "
                    f"got '{type(value).__name__}'"
                )
                continue

        # Enum
        enum_values = prop_schema.get("enum")
        if enum_values is not None and value not in enum_values:
            errors.append(
                f"{key}: value {value!r} not in allowed values {enum_values}"
            )

        # Min / max (numeric)
        if isinstance(value, (int, float)):
            mn = prop_schema.get("minimum")
            mx = prop_schema.get("maximum")
            if mn is not None and value < mn:
                errors.append(f"{key}: {value} < minimum {mn}")
            if mx is not None and value > mx:
                errors.append(f"{key}: {value} > maximum {mx}")

        # Pattern (string)
        if isinstance(value, str):
            import re

            pattern = prop_schema.get("PATTERN")
            if pattern and not re.search(pattern, value):
                errors.append(
                    f"{key}: value {value!r} does not match pattern {pattern!r}"
                )

    return errors


def x__validate_builtin__mutmut_73(
    args: dict[str, Any],
    schema: dict[str, Any],
    tool_name: str,
) -> list[str]:
    """Lightweight fallback validation without ``jsonschema``."""
    errors: list[str] = []
    properties = schema.get("properties", {})
    required = set(schema.get("required", []))

    # Required field check
    for req in required:
        if req not in args:
            errors.append(f"{req}: required field is missing")

    # Type checks
    _TYPE_MAP: dict[str, tuple[type, ...]] = {
        "string": (str,),
        "integer": (int,),
        "number": (int, float),
        "boolean": (bool,),
        "array": (list,),
        "object": (dict,),
    }

    for key, value in args.items():
        if key not in properties:
            # additionalProperties — skip unknown fields by default
            continue

        prop_schema = properties[key]
        expected = prop_schema.get("type")

        if expected and expected in _TYPE_MAP:
            if not isinstance(value, _TYPE_MAP[expected]):
                errors.append(
                    f"{key}: expected type '{expected}', "
                    f"got '{type(value).__name__}'"
                )
                continue

        # Enum
        enum_values = prop_schema.get("enum")
        if enum_values is not None and value not in enum_values:
            errors.append(
                f"{key}: value {value!r} not in allowed values {enum_values}"
            )

        # Min / max (numeric)
        if isinstance(value, (int, float)):
            mn = prop_schema.get("minimum")
            mx = prop_schema.get("maximum")
            if mn is not None and value < mn:
                errors.append(f"{key}: {value} < minimum {mn}")
            if mx is not None and value > mx:
                errors.append(f"{key}: {value} > maximum {mx}")

        # Pattern (string)
        if isinstance(value, str):
            import re

            pattern = prop_schema.get("pattern")
            if pattern or not re.search(pattern, value):
                errors.append(
                    f"{key}: value {value!r} does not match pattern {pattern!r}"
                )

    return errors


def x__validate_builtin__mutmut_74(
    args: dict[str, Any],
    schema: dict[str, Any],
    tool_name: str,
) -> list[str]:
    """Lightweight fallback validation without ``jsonschema``."""
    errors: list[str] = []
    properties = schema.get("properties", {})
    required = set(schema.get("required", []))

    # Required field check
    for req in required:
        if req not in args:
            errors.append(f"{req}: required field is missing")

    # Type checks
    _TYPE_MAP: dict[str, tuple[type, ...]] = {
        "string": (str,),
        "integer": (int,),
        "number": (int, float),
        "boolean": (bool,),
        "array": (list,),
        "object": (dict,),
    }

    for key, value in args.items():
        if key not in properties:
            # additionalProperties — skip unknown fields by default
            continue

        prop_schema = properties[key]
        expected = prop_schema.get("type")

        if expected and expected in _TYPE_MAP:
            if not isinstance(value, _TYPE_MAP[expected]):
                errors.append(
                    f"{key}: expected type '{expected}', "
                    f"got '{type(value).__name__}'"
                )
                continue

        # Enum
        enum_values = prop_schema.get("enum")
        if enum_values is not None and value not in enum_values:
            errors.append(
                f"{key}: value {value!r} not in allowed values {enum_values}"
            )

        # Min / max (numeric)
        if isinstance(value, (int, float)):
            mn = prop_schema.get("minimum")
            mx = prop_schema.get("maximum")
            if mn is not None and value < mn:
                errors.append(f"{key}: {value} < minimum {mn}")
            if mx is not None and value > mx:
                errors.append(f"{key}: {value} > maximum {mx}")

        # Pattern (string)
        if isinstance(value, str):
            import re

            pattern = prop_schema.get("pattern")
            if pattern and re.search(pattern, value):
                errors.append(
                    f"{key}: value {value!r} does not match pattern {pattern!r}"
                )

    return errors


def x__validate_builtin__mutmut_75(
    args: dict[str, Any],
    schema: dict[str, Any],
    tool_name: str,
) -> list[str]:
    """Lightweight fallback validation without ``jsonschema``."""
    errors: list[str] = []
    properties = schema.get("properties", {})
    required = set(schema.get("required", []))

    # Required field check
    for req in required:
        if req not in args:
            errors.append(f"{req}: required field is missing")

    # Type checks
    _TYPE_MAP: dict[str, tuple[type, ...]] = {
        "string": (str,),
        "integer": (int,),
        "number": (int, float),
        "boolean": (bool,),
        "array": (list,),
        "object": (dict,),
    }

    for key, value in args.items():
        if key not in properties:
            # additionalProperties — skip unknown fields by default
            continue

        prop_schema = properties[key]
        expected = prop_schema.get("type")

        if expected and expected in _TYPE_MAP:
            if not isinstance(value, _TYPE_MAP[expected]):
                errors.append(
                    f"{key}: expected type '{expected}', "
                    f"got '{type(value).__name__}'"
                )
                continue

        # Enum
        enum_values = prop_schema.get("enum")
        if enum_values is not None and value not in enum_values:
            errors.append(
                f"{key}: value {value!r} not in allowed values {enum_values}"
            )

        # Min / max (numeric)
        if isinstance(value, (int, float)):
            mn = prop_schema.get("minimum")
            mx = prop_schema.get("maximum")
            if mn is not None and value < mn:
                errors.append(f"{key}: {value} < minimum {mn}")
            if mx is not None and value > mx:
                errors.append(f"{key}: {value} > maximum {mx}")

        # Pattern (string)
        if isinstance(value, str):
            import re

            pattern = prop_schema.get("pattern")
            if pattern and not re.search(None, value):
                errors.append(
                    f"{key}: value {value!r} does not match pattern {pattern!r}"
                )

    return errors


def x__validate_builtin__mutmut_76(
    args: dict[str, Any],
    schema: dict[str, Any],
    tool_name: str,
) -> list[str]:
    """Lightweight fallback validation without ``jsonschema``."""
    errors: list[str] = []
    properties = schema.get("properties", {})
    required = set(schema.get("required", []))

    # Required field check
    for req in required:
        if req not in args:
            errors.append(f"{req}: required field is missing")

    # Type checks
    _TYPE_MAP: dict[str, tuple[type, ...]] = {
        "string": (str,),
        "integer": (int,),
        "number": (int, float),
        "boolean": (bool,),
        "array": (list,),
        "object": (dict,),
    }

    for key, value in args.items():
        if key not in properties:
            # additionalProperties — skip unknown fields by default
            continue

        prop_schema = properties[key]
        expected = prop_schema.get("type")

        if expected and expected in _TYPE_MAP:
            if not isinstance(value, _TYPE_MAP[expected]):
                errors.append(
                    f"{key}: expected type '{expected}', "
                    f"got '{type(value).__name__}'"
                )
                continue

        # Enum
        enum_values = prop_schema.get("enum")
        if enum_values is not None and value not in enum_values:
            errors.append(
                f"{key}: value {value!r} not in allowed values {enum_values}"
            )

        # Min / max (numeric)
        if isinstance(value, (int, float)):
            mn = prop_schema.get("minimum")
            mx = prop_schema.get("maximum")
            if mn is not None and value < mn:
                errors.append(f"{key}: {value} < minimum {mn}")
            if mx is not None and value > mx:
                errors.append(f"{key}: {value} > maximum {mx}")

        # Pattern (string)
        if isinstance(value, str):
            import re

            pattern = prop_schema.get("pattern")
            if pattern and not re.search(pattern, None):
                errors.append(
                    f"{key}: value {value!r} does not match pattern {pattern!r}"
                )

    return errors


def x__validate_builtin__mutmut_77(
    args: dict[str, Any],
    schema: dict[str, Any],
    tool_name: str,
) -> list[str]:
    """Lightweight fallback validation without ``jsonschema``."""
    errors: list[str] = []
    properties = schema.get("properties", {})
    required = set(schema.get("required", []))

    # Required field check
    for req in required:
        if req not in args:
            errors.append(f"{req}: required field is missing")

    # Type checks
    _TYPE_MAP: dict[str, tuple[type, ...]] = {
        "string": (str,),
        "integer": (int,),
        "number": (int, float),
        "boolean": (bool,),
        "array": (list,),
        "object": (dict,),
    }

    for key, value in args.items():
        if key not in properties:
            # additionalProperties — skip unknown fields by default
            continue

        prop_schema = properties[key]
        expected = prop_schema.get("type")

        if expected and expected in _TYPE_MAP:
            if not isinstance(value, _TYPE_MAP[expected]):
                errors.append(
                    f"{key}: expected type '{expected}', "
                    f"got '{type(value).__name__}'"
                )
                continue

        # Enum
        enum_values = prop_schema.get("enum")
        if enum_values is not None and value not in enum_values:
            errors.append(
                f"{key}: value {value!r} not in allowed values {enum_values}"
            )

        # Min / max (numeric)
        if isinstance(value, (int, float)):
            mn = prop_schema.get("minimum")
            mx = prop_schema.get("maximum")
            if mn is not None and value < mn:
                errors.append(f"{key}: {value} < minimum {mn}")
            if mx is not None and value > mx:
                errors.append(f"{key}: {value} > maximum {mx}")

        # Pattern (string)
        if isinstance(value, str):
            import re

            pattern = prop_schema.get("pattern")
            if pattern and not re.search(value):
                errors.append(
                    f"{key}: value {value!r} does not match pattern {pattern!r}"
                )

    return errors


def x__validate_builtin__mutmut_78(
    args: dict[str, Any],
    schema: dict[str, Any],
    tool_name: str,
) -> list[str]:
    """Lightweight fallback validation without ``jsonschema``."""
    errors: list[str] = []
    properties = schema.get("properties", {})
    required = set(schema.get("required", []))

    # Required field check
    for req in required:
        if req not in args:
            errors.append(f"{req}: required field is missing")

    # Type checks
    _TYPE_MAP: dict[str, tuple[type, ...]] = {
        "string": (str,),
        "integer": (int,),
        "number": (int, float),
        "boolean": (bool,),
        "array": (list,),
        "object": (dict,),
    }

    for key, value in args.items():
        if key not in properties:
            # additionalProperties — skip unknown fields by default
            continue

        prop_schema = properties[key]
        expected = prop_schema.get("type")

        if expected and expected in _TYPE_MAP:
            if not isinstance(value, _TYPE_MAP[expected]):
                errors.append(
                    f"{key}: expected type '{expected}', "
                    f"got '{type(value).__name__}'"
                )
                continue

        # Enum
        enum_values = prop_schema.get("enum")
        if enum_values is not None and value not in enum_values:
            errors.append(
                f"{key}: value {value!r} not in allowed values {enum_values}"
            )

        # Min / max (numeric)
        if isinstance(value, (int, float)):
            mn = prop_schema.get("minimum")
            mx = prop_schema.get("maximum")
            if mn is not None and value < mn:
                errors.append(f"{key}: {value} < minimum {mn}")
            if mx is not None and value > mx:
                errors.append(f"{key}: {value} > maximum {mx}")

        # Pattern (string)
        if isinstance(value, str):
            import re

            pattern = prop_schema.get("pattern")
            if pattern and not re.search(pattern, ):
                errors.append(
                    f"{key}: value {value!r} does not match pattern {pattern!r}"
                )

    return errors


def x__validate_builtin__mutmut_79(
    args: dict[str, Any],
    schema: dict[str, Any],
    tool_name: str,
) -> list[str]:
    """Lightweight fallback validation without ``jsonschema``."""
    errors: list[str] = []
    properties = schema.get("properties", {})
    required = set(schema.get("required", []))

    # Required field check
    for req in required:
        if req not in args:
            errors.append(f"{req}: required field is missing")

    # Type checks
    _TYPE_MAP: dict[str, tuple[type, ...]] = {
        "string": (str,),
        "integer": (int,),
        "number": (int, float),
        "boolean": (bool,),
        "array": (list,),
        "object": (dict,),
    }

    for key, value in args.items():
        if key not in properties:
            # additionalProperties — skip unknown fields by default
            continue

        prop_schema = properties[key]
        expected = prop_schema.get("type")

        if expected and expected in _TYPE_MAP:
            if not isinstance(value, _TYPE_MAP[expected]):
                errors.append(
                    f"{key}: expected type '{expected}', "
                    f"got '{type(value).__name__}'"
                )
                continue

        # Enum
        enum_values = prop_schema.get("enum")
        if enum_values is not None and value not in enum_values:
            errors.append(
                f"{key}: value {value!r} not in allowed values {enum_values}"
            )

        # Min / max (numeric)
        if isinstance(value, (int, float)):
            mn = prop_schema.get("minimum")
            mx = prop_schema.get("maximum")
            if mn is not None and value < mn:
                errors.append(f"{key}: {value} < minimum {mn}")
            if mx is not None and value > mx:
                errors.append(f"{key}: {value} > maximum {mx}")

        # Pattern (string)
        if isinstance(value, str):
            import re

            pattern = prop_schema.get("pattern")
            if pattern and not re.search(pattern, value):
                errors.append(
                    None
                )

    return errors

x__validate_builtin__mutmut_mutants : ClassVar[MutantDict] = {
'x__validate_builtin__mutmut_1': x__validate_builtin__mutmut_1, 
    'x__validate_builtin__mutmut_2': x__validate_builtin__mutmut_2, 
    'x__validate_builtin__mutmut_3': x__validate_builtin__mutmut_3, 
    'x__validate_builtin__mutmut_4': x__validate_builtin__mutmut_4, 
    'x__validate_builtin__mutmut_5': x__validate_builtin__mutmut_5, 
    'x__validate_builtin__mutmut_6': x__validate_builtin__mutmut_6, 
    'x__validate_builtin__mutmut_7': x__validate_builtin__mutmut_7, 
    'x__validate_builtin__mutmut_8': x__validate_builtin__mutmut_8, 
    'x__validate_builtin__mutmut_9': x__validate_builtin__mutmut_9, 
    'x__validate_builtin__mutmut_10': x__validate_builtin__mutmut_10, 
    'x__validate_builtin__mutmut_11': x__validate_builtin__mutmut_11, 
    'x__validate_builtin__mutmut_12': x__validate_builtin__mutmut_12, 
    'x__validate_builtin__mutmut_13': x__validate_builtin__mutmut_13, 
    'x__validate_builtin__mutmut_14': x__validate_builtin__mutmut_14, 
    'x__validate_builtin__mutmut_15': x__validate_builtin__mutmut_15, 
    'x__validate_builtin__mutmut_16': x__validate_builtin__mutmut_16, 
    'x__validate_builtin__mutmut_17': x__validate_builtin__mutmut_17, 
    'x__validate_builtin__mutmut_18': x__validate_builtin__mutmut_18, 
    'x__validate_builtin__mutmut_19': x__validate_builtin__mutmut_19, 
    'x__validate_builtin__mutmut_20': x__validate_builtin__mutmut_20, 
    'x__validate_builtin__mutmut_21': x__validate_builtin__mutmut_21, 
    'x__validate_builtin__mutmut_22': x__validate_builtin__mutmut_22, 
    'x__validate_builtin__mutmut_23': x__validate_builtin__mutmut_23, 
    'x__validate_builtin__mutmut_24': x__validate_builtin__mutmut_24, 
    'x__validate_builtin__mutmut_25': x__validate_builtin__mutmut_25, 
    'x__validate_builtin__mutmut_26': x__validate_builtin__mutmut_26, 
    'x__validate_builtin__mutmut_27': x__validate_builtin__mutmut_27, 
    'x__validate_builtin__mutmut_28': x__validate_builtin__mutmut_28, 
    'x__validate_builtin__mutmut_29': x__validate_builtin__mutmut_29, 
    'x__validate_builtin__mutmut_30': x__validate_builtin__mutmut_30, 
    'x__validate_builtin__mutmut_31': x__validate_builtin__mutmut_31, 
    'x__validate_builtin__mutmut_32': x__validate_builtin__mutmut_32, 
    'x__validate_builtin__mutmut_33': x__validate_builtin__mutmut_33, 
    'x__validate_builtin__mutmut_34': x__validate_builtin__mutmut_34, 
    'x__validate_builtin__mutmut_35': x__validate_builtin__mutmut_35, 
    'x__validate_builtin__mutmut_36': x__validate_builtin__mutmut_36, 
    'x__validate_builtin__mutmut_37': x__validate_builtin__mutmut_37, 
    'x__validate_builtin__mutmut_38': x__validate_builtin__mutmut_38, 
    'x__validate_builtin__mutmut_39': x__validate_builtin__mutmut_39, 
    'x__validate_builtin__mutmut_40': x__validate_builtin__mutmut_40, 
    'x__validate_builtin__mutmut_41': x__validate_builtin__mutmut_41, 
    'x__validate_builtin__mutmut_42': x__validate_builtin__mutmut_42, 
    'x__validate_builtin__mutmut_43': x__validate_builtin__mutmut_43, 
    'x__validate_builtin__mutmut_44': x__validate_builtin__mutmut_44, 
    'x__validate_builtin__mutmut_45': x__validate_builtin__mutmut_45, 
    'x__validate_builtin__mutmut_46': x__validate_builtin__mutmut_46, 
    'x__validate_builtin__mutmut_47': x__validate_builtin__mutmut_47, 
    'x__validate_builtin__mutmut_48': x__validate_builtin__mutmut_48, 
    'x__validate_builtin__mutmut_49': x__validate_builtin__mutmut_49, 
    'x__validate_builtin__mutmut_50': x__validate_builtin__mutmut_50, 
    'x__validate_builtin__mutmut_51': x__validate_builtin__mutmut_51, 
    'x__validate_builtin__mutmut_52': x__validate_builtin__mutmut_52, 
    'x__validate_builtin__mutmut_53': x__validate_builtin__mutmut_53, 
    'x__validate_builtin__mutmut_54': x__validate_builtin__mutmut_54, 
    'x__validate_builtin__mutmut_55': x__validate_builtin__mutmut_55, 
    'x__validate_builtin__mutmut_56': x__validate_builtin__mutmut_56, 
    'x__validate_builtin__mutmut_57': x__validate_builtin__mutmut_57, 
    'x__validate_builtin__mutmut_58': x__validate_builtin__mutmut_58, 
    'x__validate_builtin__mutmut_59': x__validate_builtin__mutmut_59, 
    'x__validate_builtin__mutmut_60': x__validate_builtin__mutmut_60, 
    'x__validate_builtin__mutmut_61': x__validate_builtin__mutmut_61, 
    'x__validate_builtin__mutmut_62': x__validate_builtin__mutmut_62, 
    'x__validate_builtin__mutmut_63': x__validate_builtin__mutmut_63, 
    'x__validate_builtin__mutmut_64': x__validate_builtin__mutmut_64, 
    'x__validate_builtin__mutmut_65': x__validate_builtin__mutmut_65, 
    'x__validate_builtin__mutmut_66': x__validate_builtin__mutmut_66, 
    'x__validate_builtin__mutmut_67': x__validate_builtin__mutmut_67, 
    'x__validate_builtin__mutmut_68': x__validate_builtin__mutmut_68, 
    'x__validate_builtin__mutmut_69': x__validate_builtin__mutmut_69, 
    'x__validate_builtin__mutmut_70': x__validate_builtin__mutmut_70, 
    'x__validate_builtin__mutmut_71': x__validate_builtin__mutmut_71, 
    'x__validate_builtin__mutmut_72': x__validate_builtin__mutmut_72, 
    'x__validate_builtin__mutmut_73': x__validate_builtin__mutmut_73, 
    'x__validate_builtin__mutmut_74': x__validate_builtin__mutmut_74, 
    'x__validate_builtin__mutmut_75': x__validate_builtin__mutmut_75, 
    'x__validate_builtin__mutmut_76': x__validate_builtin__mutmut_76, 
    'x__validate_builtin__mutmut_77': x__validate_builtin__mutmut_77, 
    'x__validate_builtin__mutmut_78': x__validate_builtin__mutmut_78, 
    'x__validate_builtin__mutmut_79': x__validate_builtin__mutmut_79
}

def _validate_builtin(*args, **kwargs):
    result = _mutmut_trampoline(x__validate_builtin__mutmut_orig, x__validate_builtin__mutmut_mutants, args, kwargs)
    return result 

_validate_builtin.__signature__ = _mutmut_signature(x__validate_builtin__mutmut_orig)
x__validate_builtin__mutmut_orig.__name__ = 'x__validate_builtin'


def x__generate_schema_from_func__mutmut_orig(func: Callable[..., Any]) -> dict[str, Any]:
    """Generate a JSON Schema for a function's arguments."""
    sig = inspect.signature(func)
    properties = {}
    required = []
    
    for name, param in sig.parameters.items():
        if name in ("self", "cls"):
            continue
            
        param_schema: dict[str, Any] = {}
        
        # Type inference
        if param.annotation != inspect.Parameter.empty:
            if param.annotation is str:
                param_schema["type"] = "string"
            elif param.annotation is int:
                param_schema["type"] = "integer"
            elif param.annotation is float:
                param_schema["type"] = "number"
            elif param.annotation is bool:
                param_schema["type"] = "boolean"
            elif param.annotation is list:
                param_schema["type"] = "array"
            elif param.annotation is dict:
                param_schema["type"] = "object"
            else:
                # Fallback or complex types
                param_schema["type"] = "string" # simplified
        else:
            param_schema["type"] = "string" # default
            
        properties[name] = param_schema
        
        if param.default == inspect.Parameter.empty:
            required.append(name)
            
    return {
        "type": "object",
        "properties": properties,
        "required": required,
    }


def x__generate_schema_from_func__mutmut_1(func: Callable[..., Any]) -> dict[str, Any]:
    """Generate a JSON Schema for a function's arguments."""
    sig = None
    properties = {}
    required = []
    
    for name, param in sig.parameters.items():
        if name in ("self", "cls"):
            continue
            
        param_schema: dict[str, Any] = {}
        
        # Type inference
        if param.annotation != inspect.Parameter.empty:
            if param.annotation is str:
                param_schema["type"] = "string"
            elif param.annotation is int:
                param_schema["type"] = "integer"
            elif param.annotation is float:
                param_schema["type"] = "number"
            elif param.annotation is bool:
                param_schema["type"] = "boolean"
            elif param.annotation is list:
                param_schema["type"] = "array"
            elif param.annotation is dict:
                param_schema["type"] = "object"
            else:
                # Fallback or complex types
                param_schema["type"] = "string" # simplified
        else:
            param_schema["type"] = "string" # default
            
        properties[name] = param_schema
        
        if param.default == inspect.Parameter.empty:
            required.append(name)
            
    return {
        "type": "object",
        "properties": properties,
        "required": required,
    }


def x__generate_schema_from_func__mutmut_2(func: Callable[..., Any]) -> dict[str, Any]:
    """Generate a JSON Schema for a function's arguments."""
    sig = inspect.signature(None)
    properties = {}
    required = []
    
    for name, param in sig.parameters.items():
        if name in ("self", "cls"):
            continue
            
        param_schema: dict[str, Any] = {}
        
        # Type inference
        if param.annotation != inspect.Parameter.empty:
            if param.annotation is str:
                param_schema["type"] = "string"
            elif param.annotation is int:
                param_schema["type"] = "integer"
            elif param.annotation is float:
                param_schema["type"] = "number"
            elif param.annotation is bool:
                param_schema["type"] = "boolean"
            elif param.annotation is list:
                param_schema["type"] = "array"
            elif param.annotation is dict:
                param_schema["type"] = "object"
            else:
                # Fallback or complex types
                param_schema["type"] = "string" # simplified
        else:
            param_schema["type"] = "string" # default
            
        properties[name] = param_schema
        
        if param.default == inspect.Parameter.empty:
            required.append(name)
            
    return {
        "type": "object",
        "properties": properties,
        "required": required,
    }


def x__generate_schema_from_func__mutmut_3(func: Callable[..., Any]) -> dict[str, Any]:
    """Generate a JSON Schema for a function's arguments."""
    sig = inspect.signature(func)
    properties = None
    required = []
    
    for name, param in sig.parameters.items():
        if name in ("self", "cls"):
            continue
            
        param_schema: dict[str, Any] = {}
        
        # Type inference
        if param.annotation != inspect.Parameter.empty:
            if param.annotation is str:
                param_schema["type"] = "string"
            elif param.annotation is int:
                param_schema["type"] = "integer"
            elif param.annotation is float:
                param_schema["type"] = "number"
            elif param.annotation is bool:
                param_schema["type"] = "boolean"
            elif param.annotation is list:
                param_schema["type"] = "array"
            elif param.annotation is dict:
                param_schema["type"] = "object"
            else:
                # Fallback or complex types
                param_schema["type"] = "string" # simplified
        else:
            param_schema["type"] = "string" # default
            
        properties[name] = param_schema
        
        if param.default == inspect.Parameter.empty:
            required.append(name)
            
    return {
        "type": "object",
        "properties": properties,
        "required": required,
    }


def x__generate_schema_from_func__mutmut_4(func: Callable[..., Any]) -> dict[str, Any]:
    """Generate a JSON Schema for a function's arguments."""
    sig = inspect.signature(func)
    properties = {}
    required = None
    
    for name, param in sig.parameters.items():
        if name in ("self", "cls"):
            continue
            
        param_schema: dict[str, Any] = {}
        
        # Type inference
        if param.annotation != inspect.Parameter.empty:
            if param.annotation is str:
                param_schema["type"] = "string"
            elif param.annotation is int:
                param_schema["type"] = "integer"
            elif param.annotation is float:
                param_schema["type"] = "number"
            elif param.annotation is bool:
                param_schema["type"] = "boolean"
            elif param.annotation is list:
                param_schema["type"] = "array"
            elif param.annotation is dict:
                param_schema["type"] = "object"
            else:
                # Fallback or complex types
                param_schema["type"] = "string" # simplified
        else:
            param_schema["type"] = "string" # default
            
        properties[name] = param_schema
        
        if param.default == inspect.Parameter.empty:
            required.append(name)
            
    return {
        "type": "object",
        "properties": properties,
        "required": required,
    }


def x__generate_schema_from_func__mutmut_5(func: Callable[..., Any]) -> dict[str, Any]:
    """Generate a JSON Schema for a function's arguments."""
    sig = inspect.signature(func)
    properties = {}
    required = []
    
    for name, param in sig.parameters.items():
        if name not in ("self", "cls"):
            continue
            
        param_schema: dict[str, Any] = {}
        
        # Type inference
        if param.annotation != inspect.Parameter.empty:
            if param.annotation is str:
                param_schema["type"] = "string"
            elif param.annotation is int:
                param_schema["type"] = "integer"
            elif param.annotation is float:
                param_schema["type"] = "number"
            elif param.annotation is bool:
                param_schema["type"] = "boolean"
            elif param.annotation is list:
                param_schema["type"] = "array"
            elif param.annotation is dict:
                param_schema["type"] = "object"
            else:
                # Fallback or complex types
                param_schema["type"] = "string" # simplified
        else:
            param_schema["type"] = "string" # default
            
        properties[name] = param_schema
        
        if param.default == inspect.Parameter.empty:
            required.append(name)
            
    return {
        "type": "object",
        "properties": properties,
        "required": required,
    }


def x__generate_schema_from_func__mutmut_6(func: Callable[..., Any]) -> dict[str, Any]:
    """Generate a JSON Schema for a function's arguments."""
    sig = inspect.signature(func)
    properties = {}
    required = []
    
    for name, param in sig.parameters.items():
        if name in ("XXselfXX", "cls"):
            continue
            
        param_schema: dict[str, Any] = {}
        
        # Type inference
        if param.annotation != inspect.Parameter.empty:
            if param.annotation is str:
                param_schema["type"] = "string"
            elif param.annotation is int:
                param_schema["type"] = "integer"
            elif param.annotation is float:
                param_schema["type"] = "number"
            elif param.annotation is bool:
                param_schema["type"] = "boolean"
            elif param.annotation is list:
                param_schema["type"] = "array"
            elif param.annotation is dict:
                param_schema["type"] = "object"
            else:
                # Fallback or complex types
                param_schema["type"] = "string" # simplified
        else:
            param_schema["type"] = "string" # default
            
        properties[name] = param_schema
        
        if param.default == inspect.Parameter.empty:
            required.append(name)
            
    return {
        "type": "object",
        "properties": properties,
        "required": required,
    }


def x__generate_schema_from_func__mutmut_7(func: Callable[..., Any]) -> dict[str, Any]:
    """Generate a JSON Schema for a function's arguments."""
    sig = inspect.signature(func)
    properties = {}
    required = []
    
    for name, param in sig.parameters.items():
        if name in ("SELF", "cls"):
            continue
            
        param_schema: dict[str, Any] = {}
        
        # Type inference
        if param.annotation != inspect.Parameter.empty:
            if param.annotation is str:
                param_schema["type"] = "string"
            elif param.annotation is int:
                param_schema["type"] = "integer"
            elif param.annotation is float:
                param_schema["type"] = "number"
            elif param.annotation is bool:
                param_schema["type"] = "boolean"
            elif param.annotation is list:
                param_schema["type"] = "array"
            elif param.annotation is dict:
                param_schema["type"] = "object"
            else:
                # Fallback or complex types
                param_schema["type"] = "string" # simplified
        else:
            param_schema["type"] = "string" # default
            
        properties[name] = param_schema
        
        if param.default == inspect.Parameter.empty:
            required.append(name)
            
    return {
        "type": "object",
        "properties": properties,
        "required": required,
    }


def x__generate_schema_from_func__mutmut_8(func: Callable[..., Any]) -> dict[str, Any]:
    """Generate a JSON Schema for a function's arguments."""
    sig = inspect.signature(func)
    properties = {}
    required = []
    
    for name, param in sig.parameters.items():
        if name in ("self", "XXclsXX"):
            continue
            
        param_schema: dict[str, Any] = {}
        
        # Type inference
        if param.annotation != inspect.Parameter.empty:
            if param.annotation is str:
                param_schema["type"] = "string"
            elif param.annotation is int:
                param_schema["type"] = "integer"
            elif param.annotation is float:
                param_schema["type"] = "number"
            elif param.annotation is bool:
                param_schema["type"] = "boolean"
            elif param.annotation is list:
                param_schema["type"] = "array"
            elif param.annotation is dict:
                param_schema["type"] = "object"
            else:
                # Fallback or complex types
                param_schema["type"] = "string" # simplified
        else:
            param_schema["type"] = "string" # default
            
        properties[name] = param_schema
        
        if param.default == inspect.Parameter.empty:
            required.append(name)
            
    return {
        "type": "object",
        "properties": properties,
        "required": required,
    }


def x__generate_schema_from_func__mutmut_9(func: Callable[..., Any]) -> dict[str, Any]:
    """Generate a JSON Schema for a function's arguments."""
    sig = inspect.signature(func)
    properties = {}
    required = []
    
    for name, param in sig.parameters.items():
        if name in ("self", "CLS"):
            continue
            
        param_schema: dict[str, Any] = {}
        
        # Type inference
        if param.annotation != inspect.Parameter.empty:
            if param.annotation is str:
                param_schema["type"] = "string"
            elif param.annotation is int:
                param_schema["type"] = "integer"
            elif param.annotation is float:
                param_schema["type"] = "number"
            elif param.annotation is bool:
                param_schema["type"] = "boolean"
            elif param.annotation is list:
                param_schema["type"] = "array"
            elif param.annotation is dict:
                param_schema["type"] = "object"
            else:
                # Fallback or complex types
                param_schema["type"] = "string" # simplified
        else:
            param_schema["type"] = "string" # default
            
        properties[name] = param_schema
        
        if param.default == inspect.Parameter.empty:
            required.append(name)
            
    return {
        "type": "object",
        "properties": properties,
        "required": required,
    }


def x__generate_schema_from_func__mutmut_10(func: Callable[..., Any]) -> dict[str, Any]:
    """Generate a JSON Schema for a function's arguments."""
    sig = inspect.signature(func)
    properties = {}
    required = []
    
    for name, param in sig.parameters.items():
        if name in ("self", "cls"):
            break
            
        param_schema: dict[str, Any] = {}
        
        # Type inference
        if param.annotation != inspect.Parameter.empty:
            if param.annotation is str:
                param_schema["type"] = "string"
            elif param.annotation is int:
                param_schema["type"] = "integer"
            elif param.annotation is float:
                param_schema["type"] = "number"
            elif param.annotation is bool:
                param_schema["type"] = "boolean"
            elif param.annotation is list:
                param_schema["type"] = "array"
            elif param.annotation is dict:
                param_schema["type"] = "object"
            else:
                # Fallback or complex types
                param_schema["type"] = "string" # simplified
        else:
            param_schema["type"] = "string" # default
            
        properties[name] = param_schema
        
        if param.default == inspect.Parameter.empty:
            required.append(name)
            
    return {
        "type": "object",
        "properties": properties,
        "required": required,
    }


def x__generate_schema_from_func__mutmut_11(func: Callable[..., Any]) -> dict[str, Any]:
    """Generate a JSON Schema for a function's arguments."""
    sig = inspect.signature(func)
    properties = {}
    required = []
    
    for name, param in sig.parameters.items():
        if name in ("self", "cls"):
            continue
            
        param_schema: dict[str, Any] = None
        
        # Type inference
        if param.annotation != inspect.Parameter.empty:
            if param.annotation is str:
                param_schema["type"] = "string"
            elif param.annotation is int:
                param_schema["type"] = "integer"
            elif param.annotation is float:
                param_schema["type"] = "number"
            elif param.annotation is bool:
                param_schema["type"] = "boolean"
            elif param.annotation is list:
                param_schema["type"] = "array"
            elif param.annotation is dict:
                param_schema["type"] = "object"
            else:
                # Fallback or complex types
                param_schema["type"] = "string" # simplified
        else:
            param_schema["type"] = "string" # default
            
        properties[name] = param_schema
        
        if param.default == inspect.Parameter.empty:
            required.append(name)
            
    return {
        "type": "object",
        "properties": properties,
        "required": required,
    }


def x__generate_schema_from_func__mutmut_12(func: Callable[..., Any]) -> dict[str, Any]:
    """Generate a JSON Schema for a function's arguments."""
    sig = inspect.signature(func)
    properties = {}
    required = []
    
    for name, param in sig.parameters.items():
        if name in ("self", "cls"):
            continue
            
        param_schema: dict[str, Any] = {}
        
        # Type inference
        if param.annotation == inspect.Parameter.empty:
            if param.annotation is str:
                param_schema["type"] = "string"
            elif param.annotation is int:
                param_schema["type"] = "integer"
            elif param.annotation is float:
                param_schema["type"] = "number"
            elif param.annotation is bool:
                param_schema["type"] = "boolean"
            elif param.annotation is list:
                param_schema["type"] = "array"
            elif param.annotation is dict:
                param_schema["type"] = "object"
            else:
                # Fallback or complex types
                param_schema["type"] = "string" # simplified
        else:
            param_schema["type"] = "string" # default
            
        properties[name] = param_schema
        
        if param.default == inspect.Parameter.empty:
            required.append(name)
            
    return {
        "type": "object",
        "properties": properties,
        "required": required,
    }


def x__generate_schema_from_func__mutmut_13(func: Callable[..., Any]) -> dict[str, Any]:
    """Generate a JSON Schema for a function's arguments."""
    sig = inspect.signature(func)
    properties = {}
    required = []
    
    for name, param in sig.parameters.items():
        if name in ("self", "cls"):
            continue
            
        param_schema: dict[str, Any] = {}
        
        # Type inference
        if param.annotation != inspect.Parameter.empty:
            if param.annotation is not str:
                param_schema["type"] = "string"
            elif param.annotation is int:
                param_schema["type"] = "integer"
            elif param.annotation is float:
                param_schema["type"] = "number"
            elif param.annotation is bool:
                param_schema["type"] = "boolean"
            elif param.annotation is list:
                param_schema["type"] = "array"
            elif param.annotation is dict:
                param_schema["type"] = "object"
            else:
                # Fallback or complex types
                param_schema["type"] = "string" # simplified
        else:
            param_schema["type"] = "string" # default
            
        properties[name] = param_schema
        
        if param.default == inspect.Parameter.empty:
            required.append(name)
            
    return {
        "type": "object",
        "properties": properties,
        "required": required,
    }


def x__generate_schema_from_func__mutmut_14(func: Callable[..., Any]) -> dict[str, Any]:
    """Generate a JSON Schema for a function's arguments."""
    sig = inspect.signature(func)
    properties = {}
    required = []
    
    for name, param in sig.parameters.items():
        if name in ("self", "cls"):
            continue
            
        param_schema: dict[str, Any] = {}
        
        # Type inference
        if param.annotation != inspect.Parameter.empty:
            if param.annotation is str:
                param_schema["type"] = None
            elif param.annotation is int:
                param_schema["type"] = "integer"
            elif param.annotation is float:
                param_schema["type"] = "number"
            elif param.annotation is bool:
                param_schema["type"] = "boolean"
            elif param.annotation is list:
                param_schema["type"] = "array"
            elif param.annotation is dict:
                param_schema["type"] = "object"
            else:
                # Fallback or complex types
                param_schema["type"] = "string" # simplified
        else:
            param_schema["type"] = "string" # default
            
        properties[name] = param_schema
        
        if param.default == inspect.Parameter.empty:
            required.append(name)
            
    return {
        "type": "object",
        "properties": properties,
        "required": required,
    }


def x__generate_schema_from_func__mutmut_15(func: Callable[..., Any]) -> dict[str, Any]:
    """Generate a JSON Schema for a function's arguments."""
    sig = inspect.signature(func)
    properties = {}
    required = []
    
    for name, param in sig.parameters.items():
        if name in ("self", "cls"):
            continue
            
        param_schema: dict[str, Any] = {}
        
        # Type inference
        if param.annotation != inspect.Parameter.empty:
            if param.annotation is str:
                param_schema["XXtypeXX"] = "string"
            elif param.annotation is int:
                param_schema["type"] = "integer"
            elif param.annotation is float:
                param_schema["type"] = "number"
            elif param.annotation is bool:
                param_schema["type"] = "boolean"
            elif param.annotation is list:
                param_schema["type"] = "array"
            elif param.annotation is dict:
                param_schema["type"] = "object"
            else:
                # Fallback or complex types
                param_schema["type"] = "string" # simplified
        else:
            param_schema["type"] = "string" # default
            
        properties[name] = param_schema
        
        if param.default == inspect.Parameter.empty:
            required.append(name)
            
    return {
        "type": "object",
        "properties": properties,
        "required": required,
    }


def x__generate_schema_from_func__mutmut_16(func: Callable[..., Any]) -> dict[str, Any]:
    """Generate a JSON Schema for a function's arguments."""
    sig = inspect.signature(func)
    properties = {}
    required = []
    
    for name, param in sig.parameters.items():
        if name in ("self", "cls"):
            continue
            
        param_schema: dict[str, Any] = {}
        
        # Type inference
        if param.annotation != inspect.Parameter.empty:
            if param.annotation is str:
                param_schema["TYPE"] = "string"
            elif param.annotation is int:
                param_schema["type"] = "integer"
            elif param.annotation is float:
                param_schema["type"] = "number"
            elif param.annotation is bool:
                param_schema["type"] = "boolean"
            elif param.annotation is list:
                param_schema["type"] = "array"
            elif param.annotation is dict:
                param_schema["type"] = "object"
            else:
                # Fallback or complex types
                param_schema["type"] = "string" # simplified
        else:
            param_schema["type"] = "string" # default
            
        properties[name] = param_schema
        
        if param.default == inspect.Parameter.empty:
            required.append(name)
            
    return {
        "type": "object",
        "properties": properties,
        "required": required,
    }


def x__generate_schema_from_func__mutmut_17(func: Callable[..., Any]) -> dict[str, Any]:
    """Generate a JSON Schema for a function's arguments."""
    sig = inspect.signature(func)
    properties = {}
    required = []
    
    for name, param in sig.parameters.items():
        if name in ("self", "cls"):
            continue
            
        param_schema: dict[str, Any] = {}
        
        # Type inference
        if param.annotation != inspect.Parameter.empty:
            if param.annotation is str:
                param_schema["type"] = "XXstringXX"
            elif param.annotation is int:
                param_schema["type"] = "integer"
            elif param.annotation is float:
                param_schema["type"] = "number"
            elif param.annotation is bool:
                param_schema["type"] = "boolean"
            elif param.annotation is list:
                param_schema["type"] = "array"
            elif param.annotation is dict:
                param_schema["type"] = "object"
            else:
                # Fallback or complex types
                param_schema["type"] = "string" # simplified
        else:
            param_schema["type"] = "string" # default
            
        properties[name] = param_schema
        
        if param.default == inspect.Parameter.empty:
            required.append(name)
            
    return {
        "type": "object",
        "properties": properties,
        "required": required,
    }


def x__generate_schema_from_func__mutmut_18(func: Callable[..., Any]) -> dict[str, Any]:
    """Generate a JSON Schema for a function's arguments."""
    sig = inspect.signature(func)
    properties = {}
    required = []
    
    for name, param in sig.parameters.items():
        if name in ("self", "cls"):
            continue
            
        param_schema: dict[str, Any] = {}
        
        # Type inference
        if param.annotation != inspect.Parameter.empty:
            if param.annotation is str:
                param_schema["type"] = "STRING"
            elif param.annotation is int:
                param_schema["type"] = "integer"
            elif param.annotation is float:
                param_schema["type"] = "number"
            elif param.annotation is bool:
                param_schema["type"] = "boolean"
            elif param.annotation is list:
                param_schema["type"] = "array"
            elif param.annotation is dict:
                param_schema["type"] = "object"
            else:
                # Fallback or complex types
                param_schema["type"] = "string" # simplified
        else:
            param_schema["type"] = "string" # default
            
        properties[name] = param_schema
        
        if param.default == inspect.Parameter.empty:
            required.append(name)
            
    return {
        "type": "object",
        "properties": properties,
        "required": required,
    }


def x__generate_schema_from_func__mutmut_19(func: Callable[..., Any]) -> dict[str, Any]:
    """Generate a JSON Schema for a function's arguments."""
    sig = inspect.signature(func)
    properties = {}
    required = []
    
    for name, param in sig.parameters.items():
        if name in ("self", "cls"):
            continue
            
        param_schema: dict[str, Any] = {}
        
        # Type inference
        if param.annotation != inspect.Parameter.empty:
            if param.annotation is str:
                param_schema["type"] = "string"
            elif param.annotation is not int:
                param_schema["type"] = "integer"
            elif param.annotation is float:
                param_schema["type"] = "number"
            elif param.annotation is bool:
                param_schema["type"] = "boolean"
            elif param.annotation is list:
                param_schema["type"] = "array"
            elif param.annotation is dict:
                param_schema["type"] = "object"
            else:
                # Fallback or complex types
                param_schema["type"] = "string" # simplified
        else:
            param_schema["type"] = "string" # default
            
        properties[name] = param_schema
        
        if param.default == inspect.Parameter.empty:
            required.append(name)
            
    return {
        "type": "object",
        "properties": properties,
        "required": required,
    }


def x__generate_schema_from_func__mutmut_20(func: Callable[..., Any]) -> dict[str, Any]:
    """Generate a JSON Schema for a function's arguments."""
    sig = inspect.signature(func)
    properties = {}
    required = []
    
    for name, param in sig.parameters.items():
        if name in ("self", "cls"):
            continue
            
        param_schema: dict[str, Any] = {}
        
        # Type inference
        if param.annotation != inspect.Parameter.empty:
            if param.annotation is str:
                param_schema["type"] = "string"
            elif param.annotation is int:
                param_schema["type"] = None
            elif param.annotation is float:
                param_schema["type"] = "number"
            elif param.annotation is bool:
                param_schema["type"] = "boolean"
            elif param.annotation is list:
                param_schema["type"] = "array"
            elif param.annotation is dict:
                param_schema["type"] = "object"
            else:
                # Fallback or complex types
                param_schema["type"] = "string" # simplified
        else:
            param_schema["type"] = "string" # default
            
        properties[name] = param_schema
        
        if param.default == inspect.Parameter.empty:
            required.append(name)
            
    return {
        "type": "object",
        "properties": properties,
        "required": required,
    }


def x__generate_schema_from_func__mutmut_21(func: Callable[..., Any]) -> dict[str, Any]:
    """Generate a JSON Schema for a function's arguments."""
    sig = inspect.signature(func)
    properties = {}
    required = []
    
    for name, param in sig.parameters.items():
        if name in ("self", "cls"):
            continue
            
        param_schema: dict[str, Any] = {}
        
        # Type inference
        if param.annotation != inspect.Parameter.empty:
            if param.annotation is str:
                param_schema["type"] = "string"
            elif param.annotation is int:
                param_schema["XXtypeXX"] = "integer"
            elif param.annotation is float:
                param_schema["type"] = "number"
            elif param.annotation is bool:
                param_schema["type"] = "boolean"
            elif param.annotation is list:
                param_schema["type"] = "array"
            elif param.annotation is dict:
                param_schema["type"] = "object"
            else:
                # Fallback or complex types
                param_schema["type"] = "string" # simplified
        else:
            param_schema["type"] = "string" # default
            
        properties[name] = param_schema
        
        if param.default == inspect.Parameter.empty:
            required.append(name)
            
    return {
        "type": "object",
        "properties": properties,
        "required": required,
    }


def x__generate_schema_from_func__mutmut_22(func: Callable[..., Any]) -> dict[str, Any]:
    """Generate a JSON Schema for a function's arguments."""
    sig = inspect.signature(func)
    properties = {}
    required = []
    
    for name, param in sig.parameters.items():
        if name in ("self", "cls"):
            continue
            
        param_schema: dict[str, Any] = {}
        
        # Type inference
        if param.annotation != inspect.Parameter.empty:
            if param.annotation is str:
                param_schema["type"] = "string"
            elif param.annotation is int:
                param_schema["TYPE"] = "integer"
            elif param.annotation is float:
                param_schema["type"] = "number"
            elif param.annotation is bool:
                param_schema["type"] = "boolean"
            elif param.annotation is list:
                param_schema["type"] = "array"
            elif param.annotation is dict:
                param_schema["type"] = "object"
            else:
                # Fallback or complex types
                param_schema["type"] = "string" # simplified
        else:
            param_schema["type"] = "string" # default
            
        properties[name] = param_schema
        
        if param.default == inspect.Parameter.empty:
            required.append(name)
            
    return {
        "type": "object",
        "properties": properties,
        "required": required,
    }


def x__generate_schema_from_func__mutmut_23(func: Callable[..., Any]) -> dict[str, Any]:
    """Generate a JSON Schema for a function's arguments."""
    sig = inspect.signature(func)
    properties = {}
    required = []
    
    for name, param in sig.parameters.items():
        if name in ("self", "cls"):
            continue
            
        param_schema: dict[str, Any] = {}
        
        # Type inference
        if param.annotation != inspect.Parameter.empty:
            if param.annotation is str:
                param_schema["type"] = "string"
            elif param.annotation is int:
                param_schema["type"] = "XXintegerXX"
            elif param.annotation is float:
                param_schema["type"] = "number"
            elif param.annotation is bool:
                param_schema["type"] = "boolean"
            elif param.annotation is list:
                param_schema["type"] = "array"
            elif param.annotation is dict:
                param_schema["type"] = "object"
            else:
                # Fallback or complex types
                param_schema["type"] = "string" # simplified
        else:
            param_schema["type"] = "string" # default
            
        properties[name] = param_schema
        
        if param.default == inspect.Parameter.empty:
            required.append(name)
            
    return {
        "type": "object",
        "properties": properties,
        "required": required,
    }


def x__generate_schema_from_func__mutmut_24(func: Callable[..., Any]) -> dict[str, Any]:
    """Generate a JSON Schema for a function's arguments."""
    sig = inspect.signature(func)
    properties = {}
    required = []
    
    for name, param in sig.parameters.items():
        if name in ("self", "cls"):
            continue
            
        param_schema: dict[str, Any] = {}
        
        # Type inference
        if param.annotation != inspect.Parameter.empty:
            if param.annotation is str:
                param_schema["type"] = "string"
            elif param.annotation is int:
                param_schema["type"] = "INTEGER"
            elif param.annotation is float:
                param_schema["type"] = "number"
            elif param.annotation is bool:
                param_schema["type"] = "boolean"
            elif param.annotation is list:
                param_schema["type"] = "array"
            elif param.annotation is dict:
                param_schema["type"] = "object"
            else:
                # Fallback or complex types
                param_schema["type"] = "string" # simplified
        else:
            param_schema["type"] = "string" # default
            
        properties[name] = param_schema
        
        if param.default == inspect.Parameter.empty:
            required.append(name)
            
    return {
        "type": "object",
        "properties": properties,
        "required": required,
    }


def x__generate_schema_from_func__mutmut_25(func: Callable[..., Any]) -> dict[str, Any]:
    """Generate a JSON Schema for a function's arguments."""
    sig = inspect.signature(func)
    properties = {}
    required = []
    
    for name, param in sig.parameters.items():
        if name in ("self", "cls"):
            continue
            
        param_schema: dict[str, Any] = {}
        
        # Type inference
        if param.annotation != inspect.Parameter.empty:
            if param.annotation is str:
                param_schema["type"] = "string"
            elif param.annotation is int:
                param_schema["type"] = "integer"
            elif param.annotation is not float:
                param_schema["type"] = "number"
            elif param.annotation is bool:
                param_schema["type"] = "boolean"
            elif param.annotation is list:
                param_schema["type"] = "array"
            elif param.annotation is dict:
                param_schema["type"] = "object"
            else:
                # Fallback or complex types
                param_schema["type"] = "string" # simplified
        else:
            param_schema["type"] = "string" # default
            
        properties[name] = param_schema
        
        if param.default == inspect.Parameter.empty:
            required.append(name)
            
    return {
        "type": "object",
        "properties": properties,
        "required": required,
    }


def x__generate_schema_from_func__mutmut_26(func: Callable[..., Any]) -> dict[str, Any]:
    """Generate a JSON Schema for a function's arguments."""
    sig = inspect.signature(func)
    properties = {}
    required = []
    
    for name, param in sig.parameters.items():
        if name in ("self", "cls"):
            continue
            
        param_schema: dict[str, Any] = {}
        
        # Type inference
        if param.annotation != inspect.Parameter.empty:
            if param.annotation is str:
                param_schema["type"] = "string"
            elif param.annotation is int:
                param_schema["type"] = "integer"
            elif param.annotation is float:
                param_schema["type"] = None
            elif param.annotation is bool:
                param_schema["type"] = "boolean"
            elif param.annotation is list:
                param_schema["type"] = "array"
            elif param.annotation is dict:
                param_schema["type"] = "object"
            else:
                # Fallback or complex types
                param_schema["type"] = "string" # simplified
        else:
            param_schema["type"] = "string" # default
            
        properties[name] = param_schema
        
        if param.default == inspect.Parameter.empty:
            required.append(name)
            
    return {
        "type": "object",
        "properties": properties,
        "required": required,
    }


def x__generate_schema_from_func__mutmut_27(func: Callable[..., Any]) -> dict[str, Any]:
    """Generate a JSON Schema for a function's arguments."""
    sig = inspect.signature(func)
    properties = {}
    required = []
    
    for name, param in sig.parameters.items():
        if name in ("self", "cls"):
            continue
            
        param_schema: dict[str, Any] = {}
        
        # Type inference
        if param.annotation != inspect.Parameter.empty:
            if param.annotation is str:
                param_schema["type"] = "string"
            elif param.annotation is int:
                param_schema["type"] = "integer"
            elif param.annotation is float:
                param_schema["XXtypeXX"] = "number"
            elif param.annotation is bool:
                param_schema["type"] = "boolean"
            elif param.annotation is list:
                param_schema["type"] = "array"
            elif param.annotation is dict:
                param_schema["type"] = "object"
            else:
                # Fallback or complex types
                param_schema["type"] = "string" # simplified
        else:
            param_schema["type"] = "string" # default
            
        properties[name] = param_schema
        
        if param.default == inspect.Parameter.empty:
            required.append(name)
            
    return {
        "type": "object",
        "properties": properties,
        "required": required,
    }


def x__generate_schema_from_func__mutmut_28(func: Callable[..., Any]) -> dict[str, Any]:
    """Generate a JSON Schema for a function's arguments."""
    sig = inspect.signature(func)
    properties = {}
    required = []
    
    for name, param in sig.parameters.items():
        if name in ("self", "cls"):
            continue
            
        param_schema: dict[str, Any] = {}
        
        # Type inference
        if param.annotation != inspect.Parameter.empty:
            if param.annotation is str:
                param_schema["type"] = "string"
            elif param.annotation is int:
                param_schema["type"] = "integer"
            elif param.annotation is float:
                param_schema["TYPE"] = "number"
            elif param.annotation is bool:
                param_schema["type"] = "boolean"
            elif param.annotation is list:
                param_schema["type"] = "array"
            elif param.annotation is dict:
                param_schema["type"] = "object"
            else:
                # Fallback or complex types
                param_schema["type"] = "string" # simplified
        else:
            param_schema["type"] = "string" # default
            
        properties[name] = param_schema
        
        if param.default == inspect.Parameter.empty:
            required.append(name)
            
    return {
        "type": "object",
        "properties": properties,
        "required": required,
    }


def x__generate_schema_from_func__mutmut_29(func: Callable[..., Any]) -> dict[str, Any]:
    """Generate a JSON Schema for a function's arguments."""
    sig = inspect.signature(func)
    properties = {}
    required = []
    
    for name, param in sig.parameters.items():
        if name in ("self", "cls"):
            continue
            
        param_schema: dict[str, Any] = {}
        
        # Type inference
        if param.annotation != inspect.Parameter.empty:
            if param.annotation is str:
                param_schema["type"] = "string"
            elif param.annotation is int:
                param_schema["type"] = "integer"
            elif param.annotation is float:
                param_schema["type"] = "XXnumberXX"
            elif param.annotation is bool:
                param_schema["type"] = "boolean"
            elif param.annotation is list:
                param_schema["type"] = "array"
            elif param.annotation is dict:
                param_schema["type"] = "object"
            else:
                # Fallback or complex types
                param_schema["type"] = "string" # simplified
        else:
            param_schema["type"] = "string" # default
            
        properties[name] = param_schema
        
        if param.default == inspect.Parameter.empty:
            required.append(name)
            
    return {
        "type": "object",
        "properties": properties,
        "required": required,
    }


def x__generate_schema_from_func__mutmut_30(func: Callable[..., Any]) -> dict[str, Any]:
    """Generate a JSON Schema for a function's arguments."""
    sig = inspect.signature(func)
    properties = {}
    required = []
    
    for name, param in sig.parameters.items():
        if name in ("self", "cls"):
            continue
            
        param_schema: dict[str, Any] = {}
        
        # Type inference
        if param.annotation != inspect.Parameter.empty:
            if param.annotation is str:
                param_schema["type"] = "string"
            elif param.annotation is int:
                param_schema["type"] = "integer"
            elif param.annotation is float:
                param_schema["type"] = "NUMBER"
            elif param.annotation is bool:
                param_schema["type"] = "boolean"
            elif param.annotation is list:
                param_schema["type"] = "array"
            elif param.annotation is dict:
                param_schema["type"] = "object"
            else:
                # Fallback or complex types
                param_schema["type"] = "string" # simplified
        else:
            param_schema["type"] = "string" # default
            
        properties[name] = param_schema
        
        if param.default == inspect.Parameter.empty:
            required.append(name)
            
    return {
        "type": "object",
        "properties": properties,
        "required": required,
    }


def x__generate_schema_from_func__mutmut_31(func: Callable[..., Any]) -> dict[str, Any]:
    """Generate a JSON Schema for a function's arguments."""
    sig = inspect.signature(func)
    properties = {}
    required = []
    
    for name, param in sig.parameters.items():
        if name in ("self", "cls"):
            continue
            
        param_schema: dict[str, Any] = {}
        
        # Type inference
        if param.annotation != inspect.Parameter.empty:
            if param.annotation is str:
                param_schema["type"] = "string"
            elif param.annotation is int:
                param_schema["type"] = "integer"
            elif param.annotation is float:
                param_schema["type"] = "number"
            elif param.annotation is not bool:
                param_schema["type"] = "boolean"
            elif param.annotation is list:
                param_schema["type"] = "array"
            elif param.annotation is dict:
                param_schema["type"] = "object"
            else:
                # Fallback or complex types
                param_schema["type"] = "string" # simplified
        else:
            param_schema["type"] = "string" # default
            
        properties[name] = param_schema
        
        if param.default == inspect.Parameter.empty:
            required.append(name)
            
    return {
        "type": "object",
        "properties": properties,
        "required": required,
    }


def x__generate_schema_from_func__mutmut_32(func: Callable[..., Any]) -> dict[str, Any]:
    """Generate a JSON Schema for a function's arguments."""
    sig = inspect.signature(func)
    properties = {}
    required = []
    
    for name, param in sig.parameters.items():
        if name in ("self", "cls"):
            continue
            
        param_schema: dict[str, Any] = {}
        
        # Type inference
        if param.annotation != inspect.Parameter.empty:
            if param.annotation is str:
                param_schema["type"] = "string"
            elif param.annotation is int:
                param_schema["type"] = "integer"
            elif param.annotation is float:
                param_schema["type"] = "number"
            elif param.annotation is bool:
                param_schema["type"] = None
            elif param.annotation is list:
                param_schema["type"] = "array"
            elif param.annotation is dict:
                param_schema["type"] = "object"
            else:
                # Fallback or complex types
                param_schema["type"] = "string" # simplified
        else:
            param_schema["type"] = "string" # default
            
        properties[name] = param_schema
        
        if param.default == inspect.Parameter.empty:
            required.append(name)
            
    return {
        "type": "object",
        "properties": properties,
        "required": required,
    }


def x__generate_schema_from_func__mutmut_33(func: Callable[..., Any]) -> dict[str, Any]:
    """Generate a JSON Schema for a function's arguments."""
    sig = inspect.signature(func)
    properties = {}
    required = []
    
    for name, param in sig.parameters.items():
        if name in ("self", "cls"):
            continue
            
        param_schema: dict[str, Any] = {}
        
        # Type inference
        if param.annotation != inspect.Parameter.empty:
            if param.annotation is str:
                param_schema["type"] = "string"
            elif param.annotation is int:
                param_schema["type"] = "integer"
            elif param.annotation is float:
                param_schema["type"] = "number"
            elif param.annotation is bool:
                param_schema["XXtypeXX"] = "boolean"
            elif param.annotation is list:
                param_schema["type"] = "array"
            elif param.annotation is dict:
                param_schema["type"] = "object"
            else:
                # Fallback or complex types
                param_schema["type"] = "string" # simplified
        else:
            param_schema["type"] = "string" # default
            
        properties[name] = param_schema
        
        if param.default == inspect.Parameter.empty:
            required.append(name)
            
    return {
        "type": "object",
        "properties": properties,
        "required": required,
    }


def x__generate_schema_from_func__mutmut_34(func: Callable[..., Any]) -> dict[str, Any]:
    """Generate a JSON Schema for a function's arguments."""
    sig = inspect.signature(func)
    properties = {}
    required = []
    
    for name, param in sig.parameters.items():
        if name in ("self", "cls"):
            continue
            
        param_schema: dict[str, Any] = {}
        
        # Type inference
        if param.annotation != inspect.Parameter.empty:
            if param.annotation is str:
                param_schema["type"] = "string"
            elif param.annotation is int:
                param_schema["type"] = "integer"
            elif param.annotation is float:
                param_schema["type"] = "number"
            elif param.annotation is bool:
                param_schema["TYPE"] = "boolean"
            elif param.annotation is list:
                param_schema["type"] = "array"
            elif param.annotation is dict:
                param_schema["type"] = "object"
            else:
                # Fallback or complex types
                param_schema["type"] = "string" # simplified
        else:
            param_schema["type"] = "string" # default
            
        properties[name] = param_schema
        
        if param.default == inspect.Parameter.empty:
            required.append(name)
            
    return {
        "type": "object",
        "properties": properties,
        "required": required,
    }


def x__generate_schema_from_func__mutmut_35(func: Callable[..., Any]) -> dict[str, Any]:
    """Generate a JSON Schema for a function's arguments."""
    sig = inspect.signature(func)
    properties = {}
    required = []
    
    for name, param in sig.parameters.items():
        if name in ("self", "cls"):
            continue
            
        param_schema: dict[str, Any] = {}
        
        # Type inference
        if param.annotation != inspect.Parameter.empty:
            if param.annotation is str:
                param_schema["type"] = "string"
            elif param.annotation is int:
                param_schema["type"] = "integer"
            elif param.annotation is float:
                param_schema["type"] = "number"
            elif param.annotation is bool:
                param_schema["type"] = "XXbooleanXX"
            elif param.annotation is list:
                param_schema["type"] = "array"
            elif param.annotation is dict:
                param_schema["type"] = "object"
            else:
                # Fallback or complex types
                param_schema["type"] = "string" # simplified
        else:
            param_schema["type"] = "string" # default
            
        properties[name] = param_schema
        
        if param.default == inspect.Parameter.empty:
            required.append(name)
            
    return {
        "type": "object",
        "properties": properties,
        "required": required,
    }


def x__generate_schema_from_func__mutmut_36(func: Callable[..., Any]) -> dict[str, Any]:
    """Generate a JSON Schema for a function's arguments."""
    sig = inspect.signature(func)
    properties = {}
    required = []
    
    for name, param in sig.parameters.items():
        if name in ("self", "cls"):
            continue
            
        param_schema: dict[str, Any] = {}
        
        # Type inference
        if param.annotation != inspect.Parameter.empty:
            if param.annotation is str:
                param_schema["type"] = "string"
            elif param.annotation is int:
                param_schema["type"] = "integer"
            elif param.annotation is float:
                param_schema["type"] = "number"
            elif param.annotation is bool:
                param_schema["type"] = "BOOLEAN"
            elif param.annotation is list:
                param_schema["type"] = "array"
            elif param.annotation is dict:
                param_schema["type"] = "object"
            else:
                # Fallback or complex types
                param_schema["type"] = "string" # simplified
        else:
            param_schema["type"] = "string" # default
            
        properties[name] = param_schema
        
        if param.default == inspect.Parameter.empty:
            required.append(name)
            
    return {
        "type": "object",
        "properties": properties,
        "required": required,
    }


def x__generate_schema_from_func__mutmut_37(func: Callable[..., Any]) -> dict[str, Any]:
    """Generate a JSON Schema for a function's arguments."""
    sig = inspect.signature(func)
    properties = {}
    required = []
    
    for name, param in sig.parameters.items():
        if name in ("self", "cls"):
            continue
            
        param_schema: dict[str, Any] = {}
        
        # Type inference
        if param.annotation != inspect.Parameter.empty:
            if param.annotation is str:
                param_schema["type"] = "string"
            elif param.annotation is int:
                param_schema["type"] = "integer"
            elif param.annotation is float:
                param_schema["type"] = "number"
            elif param.annotation is bool:
                param_schema["type"] = "boolean"
            elif param.annotation is not list:
                param_schema["type"] = "array"
            elif param.annotation is dict:
                param_schema["type"] = "object"
            else:
                # Fallback or complex types
                param_schema["type"] = "string" # simplified
        else:
            param_schema["type"] = "string" # default
            
        properties[name] = param_schema
        
        if param.default == inspect.Parameter.empty:
            required.append(name)
            
    return {
        "type": "object",
        "properties": properties,
        "required": required,
    }


def x__generate_schema_from_func__mutmut_38(func: Callable[..., Any]) -> dict[str, Any]:
    """Generate a JSON Schema for a function's arguments."""
    sig = inspect.signature(func)
    properties = {}
    required = []
    
    for name, param in sig.parameters.items():
        if name in ("self", "cls"):
            continue
            
        param_schema: dict[str, Any] = {}
        
        # Type inference
        if param.annotation != inspect.Parameter.empty:
            if param.annotation is str:
                param_schema["type"] = "string"
            elif param.annotation is int:
                param_schema["type"] = "integer"
            elif param.annotation is float:
                param_schema["type"] = "number"
            elif param.annotation is bool:
                param_schema["type"] = "boolean"
            elif param.annotation is list:
                param_schema["type"] = None
            elif param.annotation is dict:
                param_schema["type"] = "object"
            else:
                # Fallback or complex types
                param_schema["type"] = "string" # simplified
        else:
            param_schema["type"] = "string" # default
            
        properties[name] = param_schema
        
        if param.default == inspect.Parameter.empty:
            required.append(name)
            
    return {
        "type": "object",
        "properties": properties,
        "required": required,
    }


def x__generate_schema_from_func__mutmut_39(func: Callable[..., Any]) -> dict[str, Any]:
    """Generate a JSON Schema for a function's arguments."""
    sig = inspect.signature(func)
    properties = {}
    required = []
    
    for name, param in sig.parameters.items():
        if name in ("self", "cls"):
            continue
            
        param_schema: dict[str, Any] = {}
        
        # Type inference
        if param.annotation != inspect.Parameter.empty:
            if param.annotation is str:
                param_schema["type"] = "string"
            elif param.annotation is int:
                param_schema["type"] = "integer"
            elif param.annotation is float:
                param_schema["type"] = "number"
            elif param.annotation is bool:
                param_schema["type"] = "boolean"
            elif param.annotation is list:
                param_schema["XXtypeXX"] = "array"
            elif param.annotation is dict:
                param_schema["type"] = "object"
            else:
                # Fallback or complex types
                param_schema["type"] = "string" # simplified
        else:
            param_schema["type"] = "string" # default
            
        properties[name] = param_schema
        
        if param.default == inspect.Parameter.empty:
            required.append(name)
            
    return {
        "type": "object",
        "properties": properties,
        "required": required,
    }


def x__generate_schema_from_func__mutmut_40(func: Callable[..., Any]) -> dict[str, Any]:
    """Generate a JSON Schema for a function's arguments."""
    sig = inspect.signature(func)
    properties = {}
    required = []
    
    for name, param in sig.parameters.items():
        if name in ("self", "cls"):
            continue
            
        param_schema: dict[str, Any] = {}
        
        # Type inference
        if param.annotation != inspect.Parameter.empty:
            if param.annotation is str:
                param_schema["type"] = "string"
            elif param.annotation is int:
                param_schema["type"] = "integer"
            elif param.annotation is float:
                param_schema["type"] = "number"
            elif param.annotation is bool:
                param_schema["type"] = "boolean"
            elif param.annotation is list:
                param_schema["TYPE"] = "array"
            elif param.annotation is dict:
                param_schema["type"] = "object"
            else:
                # Fallback or complex types
                param_schema["type"] = "string" # simplified
        else:
            param_schema["type"] = "string" # default
            
        properties[name] = param_schema
        
        if param.default == inspect.Parameter.empty:
            required.append(name)
            
    return {
        "type": "object",
        "properties": properties,
        "required": required,
    }


def x__generate_schema_from_func__mutmut_41(func: Callable[..., Any]) -> dict[str, Any]:
    """Generate a JSON Schema for a function's arguments."""
    sig = inspect.signature(func)
    properties = {}
    required = []
    
    for name, param in sig.parameters.items():
        if name in ("self", "cls"):
            continue
            
        param_schema: dict[str, Any] = {}
        
        # Type inference
        if param.annotation != inspect.Parameter.empty:
            if param.annotation is str:
                param_schema["type"] = "string"
            elif param.annotation is int:
                param_schema["type"] = "integer"
            elif param.annotation is float:
                param_schema["type"] = "number"
            elif param.annotation is bool:
                param_schema["type"] = "boolean"
            elif param.annotation is list:
                param_schema["type"] = "XXarrayXX"
            elif param.annotation is dict:
                param_schema["type"] = "object"
            else:
                # Fallback or complex types
                param_schema["type"] = "string" # simplified
        else:
            param_schema["type"] = "string" # default
            
        properties[name] = param_schema
        
        if param.default == inspect.Parameter.empty:
            required.append(name)
            
    return {
        "type": "object",
        "properties": properties,
        "required": required,
    }


def x__generate_schema_from_func__mutmut_42(func: Callable[..., Any]) -> dict[str, Any]:
    """Generate a JSON Schema for a function's arguments."""
    sig = inspect.signature(func)
    properties = {}
    required = []
    
    for name, param in sig.parameters.items():
        if name in ("self", "cls"):
            continue
            
        param_schema: dict[str, Any] = {}
        
        # Type inference
        if param.annotation != inspect.Parameter.empty:
            if param.annotation is str:
                param_schema["type"] = "string"
            elif param.annotation is int:
                param_schema["type"] = "integer"
            elif param.annotation is float:
                param_schema["type"] = "number"
            elif param.annotation is bool:
                param_schema["type"] = "boolean"
            elif param.annotation is list:
                param_schema["type"] = "ARRAY"
            elif param.annotation is dict:
                param_schema["type"] = "object"
            else:
                # Fallback or complex types
                param_schema["type"] = "string" # simplified
        else:
            param_schema["type"] = "string" # default
            
        properties[name] = param_schema
        
        if param.default == inspect.Parameter.empty:
            required.append(name)
            
    return {
        "type": "object",
        "properties": properties,
        "required": required,
    }


def x__generate_schema_from_func__mutmut_43(func: Callable[..., Any]) -> dict[str, Any]:
    """Generate a JSON Schema for a function's arguments."""
    sig = inspect.signature(func)
    properties = {}
    required = []
    
    for name, param in sig.parameters.items():
        if name in ("self", "cls"):
            continue
            
        param_schema: dict[str, Any] = {}
        
        # Type inference
        if param.annotation != inspect.Parameter.empty:
            if param.annotation is str:
                param_schema["type"] = "string"
            elif param.annotation is int:
                param_schema["type"] = "integer"
            elif param.annotation is float:
                param_schema["type"] = "number"
            elif param.annotation is bool:
                param_schema["type"] = "boolean"
            elif param.annotation is list:
                param_schema["type"] = "array"
            elif param.annotation is not dict:
                param_schema["type"] = "object"
            else:
                # Fallback or complex types
                param_schema["type"] = "string" # simplified
        else:
            param_schema["type"] = "string" # default
            
        properties[name] = param_schema
        
        if param.default == inspect.Parameter.empty:
            required.append(name)
            
    return {
        "type": "object",
        "properties": properties,
        "required": required,
    }


def x__generate_schema_from_func__mutmut_44(func: Callable[..., Any]) -> dict[str, Any]:
    """Generate a JSON Schema for a function's arguments."""
    sig = inspect.signature(func)
    properties = {}
    required = []
    
    for name, param in sig.parameters.items():
        if name in ("self", "cls"):
            continue
            
        param_schema: dict[str, Any] = {}
        
        # Type inference
        if param.annotation != inspect.Parameter.empty:
            if param.annotation is str:
                param_schema["type"] = "string"
            elif param.annotation is int:
                param_schema["type"] = "integer"
            elif param.annotation is float:
                param_schema["type"] = "number"
            elif param.annotation is bool:
                param_schema["type"] = "boolean"
            elif param.annotation is list:
                param_schema["type"] = "array"
            elif param.annotation is dict:
                param_schema["type"] = None
            else:
                # Fallback or complex types
                param_schema["type"] = "string" # simplified
        else:
            param_schema["type"] = "string" # default
            
        properties[name] = param_schema
        
        if param.default == inspect.Parameter.empty:
            required.append(name)
            
    return {
        "type": "object",
        "properties": properties,
        "required": required,
    }


def x__generate_schema_from_func__mutmut_45(func: Callable[..., Any]) -> dict[str, Any]:
    """Generate a JSON Schema for a function's arguments."""
    sig = inspect.signature(func)
    properties = {}
    required = []
    
    for name, param in sig.parameters.items():
        if name in ("self", "cls"):
            continue
            
        param_schema: dict[str, Any] = {}
        
        # Type inference
        if param.annotation != inspect.Parameter.empty:
            if param.annotation is str:
                param_schema["type"] = "string"
            elif param.annotation is int:
                param_schema["type"] = "integer"
            elif param.annotation is float:
                param_schema["type"] = "number"
            elif param.annotation is bool:
                param_schema["type"] = "boolean"
            elif param.annotation is list:
                param_schema["type"] = "array"
            elif param.annotation is dict:
                param_schema["XXtypeXX"] = "object"
            else:
                # Fallback or complex types
                param_schema["type"] = "string" # simplified
        else:
            param_schema["type"] = "string" # default
            
        properties[name] = param_schema
        
        if param.default == inspect.Parameter.empty:
            required.append(name)
            
    return {
        "type": "object",
        "properties": properties,
        "required": required,
    }


def x__generate_schema_from_func__mutmut_46(func: Callable[..., Any]) -> dict[str, Any]:
    """Generate a JSON Schema for a function's arguments."""
    sig = inspect.signature(func)
    properties = {}
    required = []
    
    for name, param in sig.parameters.items():
        if name in ("self", "cls"):
            continue
            
        param_schema: dict[str, Any] = {}
        
        # Type inference
        if param.annotation != inspect.Parameter.empty:
            if param.annotation is str:
                param_schema["type"] = "string"
            elif param.annotation is int:
                param_schema["type"] = "integer"
            elif param.annotation is float:
                param_schema["type"] = "number"
            elif param.annotation is bool:
                param_schema["type"] = "boolean"
            elif param.annotation is list:
                param_schema["type"] = "array"
            elif param.annotation is dict:
                param_schema["TYPE"] = "object"
            else:
                # Fallback or complex types
                param_schema["type"] = "string" # simplified
        else:
            param_schema["type"] = "string" # default
            
        properties[name] = param_schema
        
        if param.default == inspect.Parameter.empty:
            required.append(name)
            
    return {
        "type": "object",
        "properties": properties,
        "required": required,
    }


def x__generate_schema_from_func__mutmut_47(func: Callable[..., Any]) -> dict[str, Any]:
    """Generate a JSON Schema for a function's arguments."""
    sig = inspect.signature(func)
    properties = {}
    required = []
    
    for name, param in sig.parameters.items():
        if name in ("self", "cls"):
            continue
            
        param_schema: dict[str, Any] = {}
        
        # Type inference
        if param.annotation != inspect.Parameter.empty:
            if param.annotation is str:
                param_schema["type"] = "string"
            elif param.annotation is int:
                param_schema["type"] = "integer"
            elif param.annotation is float:
                param_schema["type"] = "number"
            elif param.annotation is bool:
                param_schema["type"] = "boolean"
            elif param.annotation is list:
                param_schema["type"] = "array"
            elif param.annotation is dict:
                param_schema["type"] = "XXobjectXX"
            else:
                # Fallback or complex types
                param_schema["type"] = "string" # simplified
        else:
            param_schema["type"] = "string" # default
            
        properties[name] = param_schema
        
        if param.default == inspect.Parameter.empty:
            required.append(name)
            
    return {
        "type": "object",
        "properties": properties,
        "required": required,
    }


def x__generate_schema_from_func__mutmut_48(func: Callable[..., Any]) -> dict[str, Any]:
    """Generate a JSON Schema for a function's arguments."""
    sig = inspect.signature(func)
    properties = {}
    required = []
    
    for name, param in sig.parameters.items():
        if name in ("self", "cls"):
            continue
            
        param_schema: dict[str, Any] = {}
        
        # Type inference
        if param.annotation != inspect.Parameter.empty:
            if param.annotation is str:
                param_schema["type"] = "string"
            elif param.annotation is int:
                param_schema["type"] = "integer"
            elif param.annotation is float:
                param_schema["type"] = "number"
            elif param.annotation is bool:
                param_schema["type"] = "boolean"
            elif param.annotation is list:
                param_schema["type"] = "array"
            elif param.annotation is dict:
                param_schema["type"] = "OBJECT"
            else:
                # Fallback or complex types
                param_schema["type"] = "string" # simplified
        else:
            param_schema["type"] = "string" # default
            
        properties[name] = param_schema
        
        if param.default == inspect.Parameter.empty:
            required.append(name)
            
    return {
        "type": "object",
        "properties": properties,
        "required": required,
    }


def x__generate_schema_from_func__mutmut_49(func: Callable[..., Any]) -> dict[str, Any]:
    """Generate a JSON Schema for a function's arguments."""
    sig = inspect.signature(func)
    properties = {}
    required = []
    
    for name, param in sig.parameters.items():
        if name in ("self", "cls"):
            continue
            
        param_schema: dict[str, Any] = {}
        
        # Type inference
        if param.annotation != inspect.Parameter.empty:
            if param.annotation is str:
                param_schema["type"] = "string"
            elif param.annotation is int:
                param_schema["type"] = "integer"
            elif param.annotation is float:
                param_schema["type"] = "number"
            elif param.annotation is bool:
                param_schema["type"] = "boolean"
            elif param.annotation is list:
                param_schema["type"] = "array"
            elif param.annotation is dict:
                param_schema["type"] = "object"
            else:
                # Fallback or complex types
                param_schema["type"] = None # simplified
        else:
            param_schema["type"] = "string" # default
            
        properties[name] = param_schema
        
        if param.default == inspect.Parameter.empty:
            required.append(name)
            
    return {
        "type": "object",
        "properties": properties,
        "required": required,
    }


def x__generate_schema_from_func__mutmut_50(func: Callable[..., Any]) -> dict[str, Any]:
    """Generate a JSON Schema for a function's arguments."""
    sig = inspect.signature(func)
    properties = {}
    required = []
    
    for name, param in sig.parameters.items():
        if name in ("self", "cls"):
            continue
            
        param_schema: dict[str, Any] = {}
        
        # Type inference
        if param.annotation != inspect.Parameter.empty:
            if param.annotation is str:
                param_schema["type"] = "string"
            elif param.annotation is int:
                param_schema["type"] = "integer"
            elif param.annotation is float:
                param_schema["type"] = "number"
            elif param.annotation is bool:
                param_schema["type"] = "boolean"
            elif param.annotation is list:
                param_schema["type"] = "array"
            elif param.annotation is dict:
                param_schema["type"] = "object"
            else:
                # Fallback or complex types
                param_schema["XXtypeXX"] = "string" # simplified
        else:
            param_schema["type"] = "string" # default
            
        properties[name] = param_schema
        
        if param.default == inspect.Parameter.empty:
            required.append(name)
            
    return {
        "type": "object",
        "properties": properties,
        "required": required,
    }


def x__generate_schema_from_func__mutmut_51(func: Callable[..., Any]) -> dict[str, Any]:
    """Generate a JSON Schema for a function's arguments."""
    sig = inspect.signature(func)
    properties = {}
    required = []
    
    for name, param in sig.parameters.items():
        if name in ("self", "cls"):
            continue
            
        param_schema: dict[str, Any] = {}
        
        # Type inference
        if param.annotation != inspect.Parameter.empty:
            if param.annotation is str:
                param_schema["type"] = "string"
            elif param.annotation is int:
                param_schema["type"] = "integer"
            elif param.annotation is float:
                param_schema["type"] = "number"
            elif param.annotation is bool:
                param_schema["type"] = "boolean"
            elif param.annotation is list:
                param_schema["type"] = "array"
            elif param.annotation is dict:
                param_schema["type"] = "object"
            else:
                # Fallback or complex types
                param_schema["TYPE"] = "string" # simplified
        else:
            param_schema["type"] = "string" # default
            
        properties[name] = param_schema
        
        if param.default == inspect.Parameter.empty:
            required.append(name)
            
    return {
        "type": "object",
        "properties": properties,
        "required": required,
    }


def x__generate_schema_from_func__mutmut_52(func: Callable[..., Any]) -> dict[str, Any]:
    """Generate a JSON Schema for a function's arguments."""
    sig = inspect.signature(func)
    properties = {}
    required = []
    
    for name, param in sig.parameters.items():
        if name in ("self", "cls"):
            continue
            
        param_schema: dict[str, Any] = {}
        
        # Type inference
        if param.annotation != inspect.Parameter.empty:
            if param.annotation is str:
                param_schema["type"] = "string"
            elif param.annotation is int:
                param_schema["type"] = "integer"
            elif param.annotation is float:
                param_schema["type"] = "number"
            elif param.annotation is bool:
                param_schema["type"] = "boolean"
            elif param.annotation is list:
                param_schema["type"] = "array"
            elif param.annotation is dict:
                param_schema["type"] = "object"
            else:
                # Fallback or complex types
                param_schema["type"] = "XXstringXX" # simplified
        else:
            param_schema["type"] = "string" # default
            
        properties[name] = param_schema
        
        if param.default == inspect.Parameter.empty:
            required.append(name)
            
    return {
        "type": "object",
        "properties": properties,
        "required": required,
    }


def x__generate_schema_from_func__mutmut_53(func: Callable[..., Any]) -> dict[str, Any]:
    """Generate a JSON Schema for a function's arguments."""
    sig = inspect.signature(func)
    properties = {}
    required = []
    
    for name, param in sig.parameters.items():
        if name in ("self", "cls"):
            continue
            
        param_schema: dict[str, Any] = {}
        
        # Type inference
        if param.annotation != inspect.Parameter.empty:
            if param.annotation is str:
                param_schema["type"] = "string"
            elif param.annotation is int:
                param_schema["type"] = "integer"
            elif param.annotation is float:
                param_schema["type"] = "number"
            elif param.annotation is bool:
                param_schema["type"] = "boolean"
            elif param.annotation is list:
                param_schema["type"] = "array"
            elif param.annotation is dict:
                param_schema["type"] = "object"
            else:
                # Fallback or complex types
                param_schema["type"] = "STRING" # simplified
        else:
            param_schema["type"] = "string" # default
            
        properties[name] = param_schema
        
        if param.default == inspect.Parameter.empty:
            required.append(name)
            
    return {
        "type": "object",
        "properties": properties,
        "required": required,
    }


def x__generate_schema_from_func__mutmut_54(func: Callable[..., Any]) -> dict[str, Any]:
    """Generate a JSON Schema for a function's arguments."""
    sig = inspect.signature(func)
    properties = {}
    required = []
    
    for name, param in sig.parameters.items():
        if name in ("self", "cls"):
            continue
            
        param_schema: dict[str, Any] = {}
        
        # Type inference
        if param.annotation != inspect.Parameter.empty:
            if param.annotation is str:
                param_schema["type"] = "string"
            elif param.annotation is int:
                param_schema["type"] = "integer"
            elif param.annotation is float:
                param_schema["type"] = "number"
            elif param.annotation is bool:
                param_schema["type"] = "boolean"
            elif param.annotation is list:
                param_schema["type"] = "array"
            elif param.annotation is dict:
                param_schema["type"] = "object"
            else:
                # Fallback or complex types
                param_schema["type"] = "string" # simplified
        else:
            param_schema["type"] = None # default
            
        properties[name] = param_schema
        
        if param.default == inspect.Parameter.empty:
            required.append(name)
            
    return {
        "type": "object",
        "properties": properties,
        "required": required,
    }


def x__generate_schema_from_func__mutmut_55(func: Callable[..., Any]) -> dict[str, Any]:
    """Generate a JSON Schema for a function's arguments."""
    sig = inspect.signature(func)
    properties = {}
    required = []
    
    for name, param in sig.parameters.items():
        if name in ("self", "cls"):
            continue
            
        param_schema: dict[str, Any] = {}
        
        # Type inference
        if param.annotation != inspect.Parameter.empty:
            if param.annotation is str:
                param_schema["type"] = "string"
            elif param.annotation is int:
                param_schema["type"] = "integer"
            elif param.annotation is float:
                param_schema["type"] = "number"
            elif param.annotation is bool:
                param_schema["type"] = "boolean"
            elif param.annotation is list:
                param_schema["type"] = "array"
            elif param.annotation is dict:
                param_schema["type"] = "object"
            else:
                # Fallback or complex types
                param_schema["type"] = "string" # simplified
        else:
            param_schema["XXtypeXX"] = "string" # default
            
        properties[name] = param_schema
        
        if param.default == inspect.Parameter.empty:
            required.append(name)
            
    return {
        "type": "object",
        "properties": properties,
        "required": required,
    }


def x__generate_schema_from_func__mutmut_56(func: Callable[..., Any]) -> dict[str, Any]:
    """Generate a JSON Schema for a function's arguments."""
    sig = inspect.signature(func)
    properties = {}
    required = []
    
    for name, param in sig.parameters.items():
        if name in ("self", "cls"):
            continue
            
        param_schema: dict[str, Any] = {}
        
        # Type inference
        if param.annotation != inspect.Parameter.empty:
            if param.annotation is str:
                param_schema["type"] = "string"
            elif param.annotation is int:
                param_schema["type"] = "integer"
            elif param.annotation is float:
                param_schema["type"] = "number"
            elif param.annotation is bool:
                param_schema["type"] = "boolean"
            elif param.annotation is list:
                param_schema["type"] = "array"
            elif param.annotation is dict:
                param_schema["type"] = "object"
            else:
                # Fallback or complex types
                param_schema["type"] = "string" # simplified
        else:
            param_schema["TYPE"] = "string" # default
            
        properties[name] = param_schema
        
        if param.default == inspect.Parameter.empty:
            required.append(name)
            
    return {
        "type": "object",
        "properties": properties,
        "required": required,
    }


def x__generate_schema_from_func__mutmut_57(func: Callable[..., Any]) -> dict[str, Any]:
    """Generate a JSON Schema for a function's arguments."""
    sig = inspect.signature(func)
    properties = {}
    required = []
    
    for name, param in sig.parameters.items():
        if name in ("self", "cls"):
            continue
            
        param_schema: dict[str, Any] = {}
        
        # Type inference
        if param.annotation != inspect.Parameter.empty:
            if param.annotation is str:
                param_schema["type"] = "string"
            elif param.annotation is int:
                param_schema["type"] = "integer"
            elif param.annotation is float:
                param_schema["type"] = "number"
            elif param.annotation is bool:
                param_schema["type"] = "boolean"
            elif param.annotation is list:
                param_schema["type"] = "array"
            elif param.annotation is dict:
                param_schema["type"] = "object"
            else:
                # Fallback or complex types
                param_schema["type"] = "string" # simplified
        else:
            param_schema["type"] = "XXstringXX" # default
            
        properties[name] = param_schema
        
        if param.default == inspect.Parameter.empty:
            required.append(name)
            
    return {
        "type": "object",
        "properties": properties,
        "required": required,
    }


def x__generate_schema_from_func__mutmut_58(func: Callable[..., Any]) -> dict[str, Any]:
    """Generate a JSON Schema for a function's arguments."""
    sig = inspect.signature(func)
    properties = {}
    required = []
    
    for name, param in sig.parameters.items():
        if name in ("self", "cls"):
            continue
            
        param_schema: dict[str, Any] = {}
        
        # Type inference
        if param.annotation != inspect.Parameter.empty:
            if param.annotation is str:
                param_schema["type"] = "string"
            elif param.annotation is int:
                param_schema["type"] = "integer"
            elif param.annotation is float:
                param_schema["type"] = "number"
            elif param.annotation is bool:
                param_schema["type"] = "boolean"
            elif param.annotation is list:
                param_schema["type"] = "array"
            elif param.annotation is dict:
                param_schema["type"] = "object"
            else:
                # Fallback or complex types
                param_schema["type"] = "string" # simplified
        else:
            param_schema["type"] = "STRING" # default
            
        properties[name] = param_schema
        
        if param.default == inspect.Parameter.empty:
            required.append(name)
            
    return {
        "type": "object",
        "properties": properties,
        "required": required,
    }


def x__generate_schema_from_func__mutmut_59(func: Callable[..., Any]) -> dict[str, Any]:
    """Generate a JSON Schema for a function's arguments."""
    sig = inspect.signature(func)
    properties = {}
    required = []
    
    for name, param in sig.parameters.items():
        if name in ("self", "cls"):
            continue
            
        param_schema: dict[str, Any] = {}
        
        # Type inference
        if param.annotation != inspect.Parameter.empty:
            if param.annotation is str:
                param_schema["type"] = "string"
            elif param.annotation is int:
                param_schema["type"] = "integer"
            elif param.annotation is float:
                param_schema["type"] = "number"
            elif param.annotation is bool:
                param_schema["type"] = "boolean"
            elif param.annotation is list:
                param_schema["type"] = "array"
            elif param.annotation is dict:
                param_schema["type"] = "object"
            else:
                # Fallback or complex types
                param_schema["type"] = "string" # simplified
        else:
            param_schema["type"] = "string" # default
            
        properties[name] = None
        
        if param.default == inspect.Parameter.empty:
            required.append(name)
            
    return {
        "type": "object",
        "properties": properties,
        "required": required,
    }


def x__generate_schema_from_func__mutmut_60(func: Callable[..., Any]) -> dict[str, Any]:
    """Generate a JSON Schema for a function's arguments."""
    sig = inspect.signature(func)
    properties = {}
    required = []
    
    for name, param in sig.parameters.items():
        if name in ("self", "cls"):
            continue
            
        param_schema: dict[str, Any] = {}
        
        # Type inference
        if param.annotation != inspect.Parameter.empty:
            if param.annotation is str:
                param_schema["type"] = "string"
            elif param.annotation is int:
                param_schema["type"] = "integer"
            elif param.annotation is float:
                param_schema["type"] = "number"
            elif param.annotation is bool:
                param_schema["type"] = "boolean"
            elif param.annotation is list:
                param_schema["type"] = "array"
            elif param.annotation is dict:
                param_schema["type"] = "object"
            else:
                # Fallback or complex types
                param_schema["type"] = "string" # simplified
        else:
            param_schema["type"] = "string" # default
            
        properties[name] = param_schema
        
        if param.default != inspect.Parameter.empty:
            required.append(name)
            
    return {
        "type": "object",
        "properties": properties,
        "required": required,
    }


def x__generate_schema_from_func__mutmut_61(func: Callable[..., Any]) -> dict[str, Any]:
    """Generate a JSON Schema for a function's arguments."""
    sig = inspect.signature(func)
    properties = {}
    required = []
    
    for name, param in sig.parameters.items():
        if name in ("self", "cls"):
            continue
            
        param_schema: dict[str, Any] = {}
        
        # Type inference
        if param.annotation != inspect.Parameter.empty:
            if param.annotation is str:
                param_schema["type"] = "string"
            elif param.annotation is int:
                param_schema["type"] = "integer"
            elif param.annotation is float:
                param_schema["type"] = "number"
            elif param.annotation is bool:
                param_schema["type"] = "boolean"
            elif param.annotation is list:
                param_schema["type"] = "array"
            elif param.annotation is dict:
                param_schema["type"] = "object"
            else:
                # Fallback or complex types
                param_schema["type"] = "string" # simplified
        else:
            param_schema["type"] = "string" # default
            
        properties[name] = param_schema
        
        if param.default == inspect.Parameter.empty:
            required.append(None)
            
    return {
        "type": "object",
        "properties": properties,
        "required": required,
    }


def x__generate_schema_from_func__mutmut_62(func: Callable[..., Any]) -> dict[str, Any]:
    """Generate a JSON Schema for a function's arguments."""
    sig = inspect.signature(func)
    properties = {}
    required = []
    
    for name, param in sig.parameters.items():
        if name in ("self", "cls"):
            continue
            
        param_schema: dict[str, Any] = {}
        
        # Type inference
        if param.annotation != inspect.Parameter.empty:
            if param.annotation is str:
                param_schema["type"] = "string"
            elif param.annotation is int:
                param_schema["type"] = "integer"
            elif param.annotation is float:
                param_schema["type"] = "number"
            elif param.annotation is bool:
                param_schema["type"] = "boolean"
            elif param.annotation is list:
                param_schema["type"] = "array"
            elif param.annotation is dict:
                param_schema["type"] = "object"
            else:
                # Fallback or complex types
                param_schema["type"] = "string" # simplified
        else:
            param_schema["type"] = "string" # default
            
        properties[name] = param_schema
        
        if param.default == inspect.Parameter.empty:
            required.append(name)
            
    return {
        "XXtypeXX": "object",
        "properties": properties,
        "required": required,
    }


def x__generate_schema_from_func__mutmut_63(func: Callable[..., Any]) -> dict[str, Any]:
    """Generate a JSON Schema for a function's arguments."""
    sig = inspect.signature(func)
    properties = {}
    required = []
    
    for name, param in sig.parameters.items():
        if name in ("self", "cls"):
            continue
            
        param_schema: dict[str, Any] = {}
        
        # Type inference
        if param.annotation != inspect.Parameter.empty:
            if param.annotation is str:
                param_schema["type"] = "string"
            elif param.annotation is int:
                param_schema["type"] = "integer"
            elif param.annotation is float:
                param_schema["type"] = "number"
            elif param.annotation is bool:
                param_schema["type"] = "boolean"
            elif param.annotation is list:
                param_schema["type"] = "array"
            elif param.annotation is dict:
                param_schema["type"] = "object"
            else:
                # Fallback or complex types
                param_schema["type"] = "string" # simplified
        else:
            param_schema["type"] = "string" # default
            
        properties[name] = param_schema
        
        if param.default == inspect.Parameter.empty:
            required.append(name)
            
    return {
        "TYPE": "object",
        "properties": properties,
        "required": required,
    }


def x__generate_schema_from_func__mutmut_64(func: Callable[..., Any]) -> dict[str, Any]:
    """Generate a JSON Schema for a function's arguments."""
    sig = inspect.signature(func)
    properties = {}
    required = []
    
    for name, param in sig.parameters.items():
        if name in ("self", "cls"):
            continue
            
        param_schema: dict[str, Any] = {}
        
        # Type inference
        if param.annotation != inspect.Parameter.empty:
            if param.annotation is str:
                param_schema["type"] = "string"
            elif param.annotation is int:
                param_schema["type"] = "integer"
            elif param.annotation is float:
                param_schema["type"] = "number"
            elif param.annotation is bool:
                param_schema["type"] = "boolean"
            elif param.annotation is list:
                param_schema["type"] = "array"
            elif param.annotation is dict:
                param_schema["type"] = "object"
            else:
                # Fallback or complex types
                param_schema["type"] = "string" # simplified
        else:
            param_schema["type"] = "string" # default
            
        properties[name] = param_schema
        
        if param.default == inspect.Parameter.empty:
            required.append(name)
            
    return {
        "type": "XXobjectXX",
        "properties": properties,
        "required": required,
    }


def x__generate_schema_from_func__mutmut_65(func: Callable[..., Any]) -> dict[str, Any]:
    """Generate a JSON Schema for a function's arguments."""
    sig = inspect.signature(func)
    properties = {}
    required = []
    
    for name, param in sig.parameters.items():
        if name in ("self", "cls"):
            continue
            
        param_schema: dict[str, Any] = {}
        
        # Type inference
        if param.annotation != inspect.Parameter.empty:
            if param.annotation is str:
                param_schema["type"] = "string"
            elif param.annotation is int:
                param_schema["type"] = "integer"
            elif param.annotation is float:
                param_schema["type"] = "number"
            elif param.annotation is bool:
                param_schema["type"] = "boolean"
            elif param.annotation is list:
                param_schema["type"] = "array"
            elif param.annotation is dict:
                param_schema["type"] = "object"
            else:
                # Fallback or complex types
                param_schema["type"] = "string" # simplified
        else:
            param_schema["type"] = "string" # default
            
        properties[name] = param_schema
        
        if param.default == inspect.Parameter.empty:
            required.append(name)
            
    return {
        "type": "OBJECT",
        "properties": properties,
        "required": required,
    }


def x__generate_schema_from_func__mutmut_66(func: Callable[..., Any]) -> dict[str, Any]:
    """Generate a JSON Schema for a function's arguments."""
    sig = inspect.signature(func)
    properties = {}
    required = []
    
    for name, param in sig.parameters.items():
        if name in ("self", "cls"):
            continue
            
        param_schema: dict[str, Any] = {}
        
        # Type inference
        if param.annotation != inspect.Parameter.empty:
            if param.annotation is str:
                param_schema["type"] = "string"
            elif param.annotation is int:
                param_schema["type"] = "integer"
            elif param.annotation is float:
                param_schema["type"] = "number"
            elif param.annotation is bool:
                param_schema["type"] = "boolean"
            elif param.annotation is list:
                param_schema["type"] = "array"
            elif param.annotation is dict:
                param_schema["type"] = "object"
            else:
                # Fallback or complex types
                param_schema["type"] = "string" # simplified
        else:
            param_schema["type"] = "string" # default
            
        properties[name] = param_schema
        
        if param.default == inspect.Parameter.empty:
            required.append(name)
            
    return {
        "type": "object",
        "XXpropertiesXX": properties,
        "required": required,
    }


def x__generate_schema_from_func__mutmut_67(func: Callable[..., Any]) -> dict[str, Any]:
    """Generate a JSON Schema for a function's arguments."""
    sig = inspect.signature(func)
    properties = {}
    required = []
    
    for name, param in sig.parameters.items():
        if name in ("self", "cls"):
            continue
            
        param_schema: dict[str, Any] = {}
        
        # Type inference
        if param.annotation != inspect.Parameter.empty:
            if param.annotation is str:
                param_schema["type"] = "string"
            elif param.annotation is int:
                param_schema["type"] = "integer"
            elif param.annotation is float:
                param_schema["type"] = "number"
            elif param.annotation is bool:
                param_schema["type"] = "boolean"
            elif param.annotation is list:
                param_schema["type"] = "array"
            elif param.annotation is dict:
                param_schema["type"] = "object"
            else:
                # Fallback or complex types
                param_schema["type"] = "string" # simplified
        else:
            param_schema["type"] = "string" # default
            
        properties[name] = param_schema
        
        if param.default == inspect.Parameter.empty:
            required.append(name)
            
    return {
        "type": "object",
        "PROPERTIES": properties,
        "required": required,
    }


def x__generate_schema_from_func__mutmut_68(func: Callable[..., Any]) -> dict[str, Any]:
    """Generate a JSON Schema for a function's arguments."""
    sig = inspect.signature(func)
    properties = {}
    required = []
    
    for name, param in sig.parameters.items():
        if name in ("self", "cls"):
            continue
            
        param_schema: dict[str, Any] = {}
        
        # Type inference
        if param.annotation != inspect.Parameter.empty:
            if param.annotation is str:
                param_schema["type"] = "string"
            elif param.annotation is int:
                param_schema["type"] = "integer"
            elif param.annotation is float:
                param_schema["type"] = "number"
            elif param.annotation is bool:
                param_schema["type"] = "boolean"
            elif param.annotation is list:
                param_schema["type"] = "array"
            elif param.annotation is dict:
                param_schema["type"] = "object"
            else:
                # Fallback or complex types
                param_schema["type"] = "string" # simplified
        else:
            param_schema["type"] = "string" # default
            
        properties[name] = param_schema
        
        if param.default == inspect.Parameter.empty:
            required.append(name)
            
    return {
        "type": "object",
        "properties": properties,
        "XXrequiredXX": required,
    }


def x__generate_schema_from_func__mutmut_69(func: Callable[..., Any]) -> dict[str, Any]:
    """Generate a JSON Schema for a function's arguments."""
    sig = inspect.signature(func)
    properties = {}
    required = []
    
    for name, param in sig.parameters.items():
        if name in ("self", "cls"):
            continue
            
        param_schema: dict[str, Any] = {}
        
        # Type inference
        if param.annotation != inspect.Parameter.empty:
            if param.annotation is str:
                param_schema["type"] = "string"
            elif param.annotation is int:
                param_schema["type"] = "integer"
            elif param.annotation is float:
                param_schema["type"] = "number"
            elif param.annotation is bool:
                param_schema["type"] = "boolean"
            elif param.annotation is list:
                param_schema["type"] = "array"
            elif param.annotation is dict:
                param_schema["type"] = "object"
            else:
                # Fallback or complex types
                param_schema["type"] = "string" # simplified
        else:
            param_schema["type"] = "string" # default
            
        properties[name] = param_schema
        
        if param.default == inspect.Parameter.empty:
            required.append(name)
            
    return {
        "type": "object",
        "properties": properties,
        "REQUIRED": required,
    }

x__generate_schema_from_func__mutmut_mutants : ClassVar[MutantDict] = {
'x__generate_schema_from_func__mutmut_1': x__generate_schema_from_func__mutmut_1, 
    'x__generate_schema_from_func__mutmut_2': x__generate_schema_from_func__mutmut_2, 
    'x__generate_schema_from_func__mutmut_3': x__generate_schema_from_func__mutmut_3, 
    'x__generate_schema_from_func__mutmut_4': x__generate_schema_from_func__mutmut_4, 
    'x__generate_schema_from_func__mutmut_5': x__generate_schema_from_func__mutmut_5, 
    'x__generate_schema_from_func__mutmut_6': x__generate_schema_from_func__mutmut_6, 
    'x__generate_schema_from_func__mutmut_7': x__generate_schema_from_func__mutmut_7, 
    'x__generate_schema_from_func__mutmut_8': x__generate_schema_from_func__mutmut_8, 
    'x__generate_schema_from_func__mutmut_9': x__generate_schema_from_func__mutmut_9, 
    'x__generate_schema_from_func__mutmut_10': x__generate_schema_from_func__mutmut_10, 
    'x__generate_schema_from_func__mutmut_11': x__generate_schema_from_func__mutmut_11, 
    'x__generate_schema_from_func__mutmut_12': x__generate_schema_from_func__mutmut_12, 
    'x__generate_schema_from_func__mutmut_13': x__generate_schema_from_func__mutmut_13, 
    'x__generate_schema_from_func__mutmut_14': x__generate_schema_from_func__mutmut_14, 
    'x__generate_schema_from_func__mutmut_15': x__generate_schema_from_func__mutmut_15, 
    'x__generate_schema_from_func__mutmut_16': x__generate_schema_from_func__mutmut_16, 
    'x__generate_schema_from_func__mutmut_17': x__generate_schema_from_func__mutmut_17, 
    'x__generate_schema_from_func__mutmut_18': x__generate_schema_from_func__mutmut_18, 
    'x__generate_schema_from_func__mutmut_19': x__generate_schema_from_func__mutmut_19, 
    'x__generate_schema_from_func__mutmut_20': x__generate_schema_from_func__mutmut_20, 
    'x__generate_schema_from_func__mutmut_21': x__generate_schema_from_func__mutmut_21, 
    'x__generate_schema_from_func__mutmut_22': x__generate_schema_from_func__mutmut_22, 
    'x__generate_schema_from_func__mutmut_23': x__generate_schema_from_func__mutmut_23, 
    'x__generate_schema_from_func__mutmut_24': x__generate_schema_from_func__mutmut_24, 
    'x__generate_schema_from_func__mutmut_25': x__generate_schema_from_func__mutmut_25, 
    'x__generate_schema_from_func__mutmut_26': x__generate_schema_from_func__mutmut_26, 
    'x__generate_schema_from_func__mutmut_27': x__generate_schema_from_func__mutmut_27, 
    'x__generate_schema_from_func__mutmut_28': x__generate_schema_from_func__mutmut_28, 
    'x__generate_schema_from_func__mutmut_29': x__generate_schema_from_func__mutmut_29, 
    'x__generate_schema_from_func__mutmut_30': x__generate_schema_from_func__mutmut_30, 
    'x__generate_schema_from_func__mutmut_31': x__generate_schema_from_func__mutmut_31, 
    'x__generate_schema_from_func__mutmut_32': x__generate_schema_from_func__mutmut_32, 
    'x__generate_schema_from_func__mutmut_33': x__generate_schema_from_func__mutmut_33, 
    'x__generate_schema_from_func__mutmut_34': x__generate_schema_from_func__mutmut_34, 
    'x__generate_schema_from_func__mutmut_35': x__generate_schema_from_func__mutmut_35, 
    'x__generate_schema_from_func__mutmut_36': x__generate_schema_from_func__mutmut_36, 
    'x__generate_schema_from_func__mutmut_37': x__generate_schema_from_func__mutmut_37, 
    'x__generate_schema_from_func__mutmut_38': x__generate_schema_from_func__mutmut_38, 
    'x__generate_schema_from_func__mutmut_39': x__generate_schema_from_func__mutmut_39, 
    'x__generate_schema_from_func__mutmut_40': x__generate_schema_from_func__mutmut_40, 
    'x__generate_schema_from_func__mutmut_41': x__generate_schema_from_func__mutmut_41, 
    'x__generate_schema_from_func__mutmut_42': x__generate_schema_from_func__mutmut_42, 
    'x__generate_schema_from_func__mutmut_43': x__generate_schema_from_func__mutmut_43, 
    'x__generate_schema_from_func__mutmut_44': x__generate_schema_from_func__mutmut_44, 
    'x__generate_schema_from_func__mutmut_45': x__generate_schema_from_func__mutmut_45, 
    'x__generate_schema_from_func__mutmut_46': x__generate_schema_from_func__mutmut_46, 
    'x__generate_schema_from_func__mutmut_47': x__generate_schema_from_func__mutmut_47, 
    'x__generate_schema_from_func__mutmut_48': x__generate_schema_from_func__mutmut_48, 
    'x__generate_schema_from_func__mutmut_49': x__generate_schema_from_func__mutmut_49, 
    'x__generate_schema_from_func__mutmut_50': x__generate_schema_from_func__mutmut_50, 
    'x__generate_schema_from_func__mutmut_51': x__generate_schema_from_func__mutmut_51, 
    'x__generate_schema_from_func__mutmut_52': x__generate_schema_from_func__mutmut_52, 
    'x__generate_schema_from_func__mutmut_53': x__generate_schema_from_func__mutmut_53, 
    'x__generate_schema_from_func__mutmut_54': x__generate_schema_from_func__mutmut_54, 
    'x__generate_schema_from_func__mutmut_55': x__generate_schema_from_func__mutmut_55, 
    'x__generate_schema_from_func__mutmut_56': x__generate_schema_from_func__mutmut_56, 
    'x__generate_schema_from_func__mutmut_57': x__generate_schema_from_func__mutmut_57, 
    'x__generate_schema_from_func__mutmut_58': x__generate_schema_from_func__mutmut_58, 
    'x__generate_schema_from_func__mutmut_59': x__generate_schema_from_func__mutmut_59, 
    'x__generate_schema_from_func__mutmut_60': x__generate_schema_from_func__mutmut_60, 
    'x__generate_schema_from_func__mutmut_61': x__generate_schema_from_func__mutmut_61, 
    'x__generate_schema_from_func__mutmut_62': x__generate_schema_from_func__mutmut_62, 
    'x__generate_schema_from_func__mutmut_63': x__generate_schema_from_func__mutmut_63, 
    'x__generate_schema_from_func__mutmut_64': x__generate_schema_from_func__mutmut_64, 
    'x__generate_schema_from_func__mutmut_65': x__generate_schema_from_func__mutmut_65, 
    'x__generate_schema_from_func__mutmut_66': x__generate_schema_from_func__mutmut_66, 
    'x__generate_schema_from_func__mutmut_67': x__generate_schema_from_func__mutmut_67, 
    'x__generate_schema_from_func__mutmut_68': x__generate_schema_from_func__mutmut_68, 
    'x__generate_schema_from_func__mutmut_69': x__generate_schema_from_func__mutmut_69
}

def _generate_schema_from_func(*args, **kwargs):
    result = _mutmut_trampoline(x__generate_schema_from_func__mutmut_orig, x__generate_schema_from_func__mutmut_mutants, args, kwargs)
    return result 

_generate_schema_from_func.__signature__ = _mutmut_signature(x__generate_schema_from_func__mutmut_orig)
x__generate_schema_from_func__mutmut_orig.__name__ = 'x__generate_schema_from_func'
__all__ = [
    "ValidationResult",
    "validate_tool_arguments",
    "_generate_schema_from_func",
]
