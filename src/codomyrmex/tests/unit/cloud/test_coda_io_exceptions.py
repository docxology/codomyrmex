"""
Unit tests for Coda.io API exceptions.

Tests the exception hierarchy, status code mapping, and error message handling.
"""

import pytest


@pytest.mark.unit
class TestCodaAPIErrorBase:
    """Tests for the base CodaAPIError exception."""

    def test_base_error_creation(self):
        """Test creating base CodaAPIError."""
        from codomyrmex.cloud.coda_io.exceptions import CodaAPIError

        error = CodaAPIError("Something went wrong")

        assert "Something went wrong" in str(error)
        assert error.message == "Something went wrong"
        assert error.status_code is None
        assert error.response_body is None

    def test_base_error_with_status_code(self):
        """Test CodaAPIError with status code."""
        from codomyrmex.cloud.coda_io.exceptions import CodaAPIError

        error = CodaAPIError("Server error", status_code=500)

        assert "Server error" in str(error)
        assert "500" in str(error)
        assert error.status_code == 500

    def test_base_error_with_response_body(self):
        """Test CodaAPIError with response body."""
        from codomyrmex.cloud.coda_io.exceptions import CodaAPIError

        body = {"error": "Internal error", "details": {"code": "ERR001"}}
        error = CodaAPIError("Server error", status_code=500, response_body=body)

        assert error.response_body == body
        assert error.response_body["details"]["code"] == "ERR001"


@pytest.mark.unit
class TestCodaAuthenticationError:
    """Tests for CodaAuthenticationError (401)."""

    def test_default_message(self):
        """Test default authentication error message."""
        from codomyrmex.cloud.coda_io.exceptions import CodaAuthenticationError

        error = CodaAuthenticationError()

        assert error.status_code == 401
        assert "invalid or missing" in str(error).lower()

    def test_custom_message(self):
        """Test custom authentication error message."""
        from codomyrmex.cloud.coda_io.exceptions import CodaAuthenticationError

        error = CodaAuthenticationError(message="Token revoked")

        assert "Token revoked" in str(error)
        assert error.status_code == 401

    def test_is_subclass_of_base(self):
        """Test that CodaAuthenticationError is subclass of CodaAPIError."""
        from codomyrmex.cloud.coda_io.exceptions import (
            CodaAPIError,
            CodaAuthenticationError,
        )

        assert issubclass(CodaAuthenticationError, CodaAPIError)

        error = CodaAuthenticationError()
        assert isinstance(error, CodaAPIError)


@pytest.mark.unit
class TestCodaForbiddenError:
    """Tests for CodaForbiddenError (403)."""

    def test_default_message(self):
        """Test default forbidden error message."""
        from codomyrmex.cloud.coda_io.exceptions import CodaForbiddenError

        error = CodaForbiddenError()

        assert error.status_code == 403
        assert "access" in str(error).lower()

    def test_custom_message(self):
        """Test custom forbidden error message."""
        from codomyrmex.cloud.coda_io.exceptions import CodaForbiddenError

        error = CodaForbiddenError(message="You are not a workspace member")

        assert "workspace member" in str(error)


@pytest.mark.unit
class TestCodaNotFoundError:
    """Tests for CodaNotFoundError (404)."""

    def test_default_message(self):
        """Test default not found error message."""
        from codomyrmex.cloud.coda_io.exceptions import CodaNotFoundError

        error = CodaNotFoundError()

        assert error.status_code == 404
        assert "not" in str(error).lower()

    def test_custom_message(self):
        """Test custom not found error message."""
        from codomyrmex.cloud.coda_io.exceptions import CodaNotFoundError

        error = CodaNotFoundError(message="Doc 'AbCDeFGH' not found")

        assert "AbCDeFGH" in str(error)


@pytest.mark.unit
class TestCodaGoneError:
    """Tests for CodaGoneError (410)."""

    def test_default_message(self):
        """Test default gone error message."""
        from codomyrmex.cloud.coda_io.exceptions import CodaGoneError

        error = CodaGoneError()

        assert error.status_code == 410
        assert "deleted" in str(error).lower()


@pytest.mark.unit
class TestCodaRateLimitError:
    """Tests for CodaRateLimitError (429)."""

    def test_default_message(self):
        """Test default rate limit error message."""
        from codomyrmex.cloud.coda_io.exceptions import CodaRateLimitError

        error = CodaRateLimitError()

        assert error.status_code == 429
        assert "too many" in str(error).lower()

    def test_with_response_body(self):
        """Test rate limit error with retry info."""
        from codomyrmex.cloud.coda_io.exceptions import CodaRateLimitError

        body = {"retryAfter": 6}
        error = CodaRateLimitError(response_body=body)

        assert error.response_body["retryAfter"] == 6


@pytest.mark.unit
class TestCodaValidationError:
    """Tests for CodaValidationError (400)."""

    def test_default_message(self):
        """Test default validation error message."""
        from codomyrmex.cloud.coda_io.exceptions import CodaValidationError

        error = CodaValidationError()

        assert error.status_code == 400
        assert "parameters" in str(error).lower() or "conform" in str(error).lower()

    def test_custom_message_with_details(self):
        """Test validation error with details."""
        from codomyrmex.cloud.coda_io.exceptions import CodaValidationError

        body = {
            "message": "Invalid parameter 'limit'",
            "details": {"parameter": "limit", "value": -1},
        }
        error = CodaValidationError(message="Invalid parameter 'limit'", response_body=body)

        assert "limit" in str(error)
        assert error.response_body["details"]["value"] == -1


@pytest.mark.unit
class TestRaiseForStatus:
    """Tests for the raise_for_status helper function."""

    def test_success_codes_dont_raise(self):
        """Test that 2xx codes don't raise exceptions."""
        from codomyrmex.cloud.coda_io.exceptions import raise_for_status

        # These should not raise
        raise_for_status(200)
        raise_for_status(201)
        raise_for_status(202)
        raise_for_status(204)

    def test_400_raises_validation_error(self):
        """Test 400 raises CodaValidationError."""
        from codomyrmex.cloud.coda_io.exceptions import (
            CodaValidationError,
            raise_for_status,
        )

        with pytest.raises(CodaValidationError):
            raise_for_status(400)

    def test_401_raises_authentication_error(self):
        """Test 401 raises CodaAuthenticationError."""
        from codomyrmex.cloud.coda_io.exceptions import (
            CodaAuthenticationError,
            raise_for_status,
        )

        with pytest.raises(CodaAuthenticationError):
            raise_for_status(401)

    def test_403_raises_forbidden_error(self):
        """Test 403 raises CodaForbiddenError."""
        from codomyrmex.cloud.coda_io.exceptions import (
            CodaForbiddenError,
            raise_for_status,
        )

        with pytest.raises(CodaForbiddenError):
            raise_for_status(403)

    def test_404_raises_not_found_error(self):
        """Test 404 raises CodaNotFoundError."""
        from codomyrmex.cloud.coda_io.exceptions import (
            CodaNotFoundError,
            raise_for_status,
        )

        with pytest.raises(CodaNotFoundError):
            raise_for_status(404)

    def test_410_raises_gone_error(self):
        """Test 410 raises CodaGoneError."""
        from codomyrmex.cloud.coda_io.exceptions import (
            CodaGoneError,
            raise_for_status,
        )

        with pytest.raises(CodaGoneError):
            raise_for_status(410)

    def test_429_raises_rate_limit_error(self):
        """Test 429 raises CodaRateLimitError."""
        from codomyrmex.cloud.coda_io.exceptions import (
            CodaRateLimitError,
            raise_for_status,
        )

        with pytest.raises(CodaRateLimitError):
            raise_for_status(429)

    def test_unknown_error_raises_base_error(self):
        """Test unknown error codes raise base CodaAPIError."""
        from codomyrmex.cloud.coda_io.exceptions import (
            CodaAPIError,
            raise_for_status,
        )

        with pytest.raises(CodaAPIError):
            raise_for_status(500)

        with pytest.raises(CodaAPIError):
            raise_for_status(503)

    def test_uses_message_from_response_body(self):
        """Test that response body message is used."""
        from codomyrmex.cloud.coda_io.exceptions import (
            CodaNotFoundError,
            raise_for_status,
        )

        body = {"message": "Doc 'xyz' was not found"}

        with pytest.raises(CodaNotFoundError) as exc_info:
            raise_for_status(404, body)

        assert "xyz" in str(exc_info.value)

    def test_uses_error_field_from_response_body(self):
        """Test that response body 'error' field is used as fallback."""
        from codomyrmex.cloud.coda_io.exceptions import (
            CodaValidationError,
            raise_for_status,
        )

        body = {"error": "Missing required field 'title'"}

        with pytest.raises(CodaValidationError) as exc_info:
            raise_for_status(400, body)

        assert "title" in str(exc_info.value)


@pytest.mark.unit
class TestExceptionHierarchy:
    """Tests for the exception class hierarchy."""

    def test_all_exceptions_inherit_from_base(self):
        """Test all custom exceptions inherit from CodaAPIError."""
        from codomyrmex.cloud.coda_io.exceptions import (
            CodaAPIError,
            CodaAuthenticationError,
            CodaForbiddenError,
            CodaGoneError,
            CodaNotFoundError,
            CodaRateLimitError,
            CodaValidationError,
        )

        exceptions = [
            CodaAuthenticationError,
            CodaForbiddenError,
            CodaNotFoundError,
            CodaGoneError,
            CodaRateLimitError,
            CodaValidationError,
        ]

        for exc_class in exceptions:
            assert issubclass(exc_class, CodaAPIError), f"{exc_class.__name__} should inherit from CodaAPIError"

    def test_all_exceptions_inherit_from_exception(self):
        """Test all custom exceptions inherit from Exception."""
        from codomyrmex.cloud.coda_io.exceptions import (
            CodaAPIError,
            CodaAuthenticationError,
            CodaForbiddenError,
            CodaGoneError,
            CodaNotFoundError,
            CodaRateLimitError,
            CodaValidationError,
        )

        exceptions = [
            CodaAPIError,
            CodaAuthenticationError,
            CodaForbiddenError,
            CodaNotFoundError,
            CodaGoneError,
            CodaRateLimitError,
            CodaValidationError,
        ]

        for exc_class in exceptions:
            assert issubclass(exc_class, Exception), f"{exc_class.__name__} should inherit from Exception"

    def test_can_catch_specific_or_base(self):
        """Test exceptions can be caught specifically or via base class."""
        from codomyrmex.cloud.coda_io.exceptions import (
            CodaAPIError,
            CodaNotFoundError,
        )

        # Can catch specific
        try:
            raise CodaNotFoundError("Not found")
        except CodaNotFoundError as e:
            caught_specific = True

        assert caught_specific

        # Can catch via base
        try:
            raise CodaNotFoundError("Not found")
        except CodaAPIError as e:
            caught_base = True

        assert caught_base
