"""
Unit tests for the Infomaniak module public API surface.

Tests cover:
- __all__ completeness against expected names
- Exception hierarchy and classify_openstack_error behavior
- Base class context manager and factory method contracts
- ABC implementation verification for ComputeClient and StorageClient
- Exception attribute propagation (service, operation, resource_id)

Total: ~11 tests in a single TestInfomaniakModuleExports class.
"""

import pytest
from unittest.mock import MagicMock


class TestInfomaniakModuleExports:
    """Comprehensive tests for the infomaniak package public API surface."""

    # -----------------------------------------------------------------
    # 1. __all__ completeness
    # -----------------------------------------------------------------

    def test_all_contains_every_expected_name(self):
        """__all__ in codomyrmex.cloud.infomaniak lists every public symbol."""
        import codomyrmex.cloud.infomaniak as pkg

        expected_names = {
            # Exceptions
            "InfomaniakCloudError",
            "InfomaniakAuthError",
            "InfomaniakNotFoundError",
            "InfomaniakConflictError",
            "InfomaniakQuotaExceededError",
            "InfomaniakConnectionError",
            "InfomaniakTimeoutError",
            "classify_openstack_error",
            # Base classes
            "InfomaniakOpenStackBase",
            "InfomaniakS3Base",
            # Authentication
            "InfomaniakCredentials",
            "InfomaniakS3Credentials",
            "create_openstack_connection",
            "create_s3_client",
            # Clients
            "InfomaniakComputeClient",
            "InfomaniakVolumeClient",
            "InfomaniakNetworkClient",
            "InfomaniakObjectStorageClient",
            "InfomaniakS3Client",
            "InfomaniakIdentityClient",
            "InfomaniakDNSClient",
            "InfomaniakHeatClient",
            "InfomaniakMeteringClient",
            "InfomaniakNewsletterClient",
        }

        actual_all = set(pkg.__all__)

        missing = expected_names - actual_all
        assert not missing, f"Missing from __all__: {missing}"

        extra = actual_all - expected_names
        assert not extra, f"Unexpected extras in __all__: {extra}"

    # -----------------------------------------------------------------
    # 2. Exception hierarchy
    # -----------------------------------------------------------------

    def test_exception_hierarchy(self):
        """All error classes inherit from InfomaniakCloudError which inherits from Exception."""
        from codomyrmex.cloud.infomaniak.exceptions import (
            InfomaniakCloudError,
            InfomaniakAuthError,
            InfomaniakNotFoundError,
            InfomaniakConflictError,
            InfomaniakQuotaExceededError,
            InfomaniakConnectionError,
            InfomaniakTimeoutError,
        )

        assert issubclass(InfomaniakCloudError, Exception)

        subclasses = [
            InfomaniakAuthError,
            InfomaniakNotFoundError,
            InfomaniakConflictError,
            InfomaniakQuotaExceededError,
            InfomaniakConnectionError,
            InfomaniakTimeoutError,
        ]
        for cls in subclasses:
            assert issubclass(cls, InfomaniakCloudError), (
                f"{cls.__name__} does not inherit from InfomaniakCloudError"
            )

    def test_classify_openstack_error_known_codes(self):
        """classify_openstack_error maps known patterns to correct exception types."""
        from codomyrmex.cloud.infomaniak.exceptions import (
            classify_openstack_error,
            InfomaniakAuthError,
            InfomaniakNotFoundError,
            InfomaniakConflictError,
            InfomaniakQuotaExceededError,
            InfomaniakTimeoutError,
            InfomaniakConnectionError,
        )

        cases = [
            ("HTTP 401 Unauthorized", InfomaniakAuthError),
            ("Resource 404 not found", InfomaniakNotFoundError),
            ("HTTP 409 conflict detected", InfomaniakConflictError),
            ("HTTP 413 quota exceeded", InfomaniakQuotaExceededError),
            ("Request timeout after 30s", InfomaniakTimeoutError),
            ("connection refused by host", InfomaniakConnectionError),
        ]

        for message, expected_type in cases:
            result = classify_openstack_error(
                Exception(message),
                service="test",
                operation="test_op",
            )
            assert isinstance(result, expected_type), (
                f"Expected {expected_type.__name__} for '{message}', "
                f"got {type(result).__name__}"
            )

    # -----------------------------------------------------------------
    # 3. OpenStackBase has context manager protocol
    # -----------------------------------------------------------------

    def test_openstack_base_context_manager(self):
        """InfomaniakOpenStackBase supports __enter__ and __exit__."""
        from codomyrmex.cloud.infomaniak.base import InfomaniakOpenStackBase

        assert hasattr(InfomaniakOpenStackBase, "__enter__")
        assert hasattr(InfomaniakOpenStackBase, "__exit__")

        mock_conn = MagicMock()
        base = InfomaniakOpenStackBase(mock_conn)

        with base as ctx:
            assert ctx is base

        mock_conn.close.assert_called_once()

    # -----------------------------------------------------------------
    # 4. S3Base has context manager protocol
    # -----------------------------------------------------------------

    def test_s3_base_context_manager(self):
        """InfomaniakS3Base supports __enter__ and __exit__."""
        from codomyrmex.cloud.infomaniak.base import InfomaniakS3Base

        assert hasattr(InfomaniakS3Base, "__enter__")
        assert hasattr(InfomaniakS3Base, "__exit__")

        mock_client = MagicMock()
        s3_base = InfomaniakS3Base(mock_client)

        with s3_base as ctx:
            assert ctx is s3_base

    # -----------------------------------------------------------------
    # 5. OpenStackBase has validate_connection method
    # -----------------------------------------------------------------

    def test_openstack_base_validate_connection(self):
        """InfomaniakOpenStackBase exposes a validate_connection method."""
        from codomyrmex.cloud.infomaniak.base import InfomaniakOpenStackBase

        assert hasattr(InfomaniakOpenStackBase, "validate_connection")
        assert callable(getattr(InfomaniakOpenStackBase, "validate_connection"))

    # -----------------------------------------------------------------
    # 6. ComputeClient implements ABC: has terminate_instance
    # -----------------------------------------------------------------

    def test_compute_client_has_terminate_instance(self):
        """InfomaniakComputeClient implements the ComputeClient ABC terminate_instance method."""
        from codomyrmex.cloud.infomaniak.compute import InfomaniakComputeClient
        from codomyrmex.cloud.common import ComputeClient

        assert issubclass(InfomaniakComputeClient, ComputeClient)
        assert hasattr(InfomaniakComputeClient, "terminate_instance")
        assert callable(getattr(InfomaniakComputeClient, "terminate_instance"))

    # -----------------------------------------------------------------
    # 7. S3Client implements ABC: has delete_file
    # -----------------------------------------------------------------

    def test_s3_client_has_delete_file(self):
        """InfomaniakS3Client implements the StorageClient ABC delete_file method."""
        from codomyrmex.cloud.infomaniak.object_storage import InfomaniakS3Client
        from codomyrmex.cloud.common import StorageClient

        assert issubclass(InfomaniakS3Client, StorageClient)
        assert hasattr(InfomaniakS3Client, "delete_file")
        assert callable(getattr(InfomaniakS3Client, "delete_file"))

    # -----------------------------------------------------------------
    # 8. OpenStackBase from_env and from_credentials classmethods
    # -----------------------------------------------------------------

    def test_openstack_base_factory_classmethods(self):
        """InfomaniakOpenStackBase has from_env and from_credentials classmethods."""
        from codomyrmex.cloud.infomaniak.base import InfomaniakOpenStackBase

        assert hasattr(InfomaniakOpenStackBase, "from_env")
        assert hasattr(InfomaniakOpenStackBase, "from_credentials")

        assert isinstance(
            InfomaniakOpenStackBase.__dict__["from_env"], classmethod
        )
        assert isinstance(
            InfomaniakOpenStackBase.__dict__["from_credentials"], classmethod
        )

    # -----------------------------------------------------------------
    # 9. S3Base from_env and from_credentials classmethods
    # -----------------------------------------------------------------

    def test_s3_base_factory_classmethods(self):
        """InfomaniakS3Base has from_env and from_credentials classmethods."""
        from codomyrmex.cloud.infomaniak.base import InfomaniakS3Base

        assert hasattr(InfomaniakS3Base, "from_env")
        assert hasattr(InfomaniakS3Base, "from_credentials")

        assert isinstance(
            InfomaniakS3Base.__dict__["from_env"], classmethod
        )
        assert isinstance(
            InfomaniakS3Base.__dict__["from_credentials"], classmethod
        )

    # -----------------------------------------------------------------
    # 10. Exception instances carry service/operation/resource_id
    # -----------------------------------------------------------------

    def test_exception_carries_service_operation_resource_id(self):
        """All InfomaniakCloudError subclasses propagate service, operation, resource_id."""
        from codomyrmex.cloud.infomaniak.exceptions import (
            InfomaniakCloudError,
            InfomaniakAuthError,
            InfomaniakNotFoundError,
            InfomaniakConflictError,
            InfomaniakQuotaExceededError,
            InfomaniakConnectionError,
            InfomaniakTimeoutError,
        )

        exception_classes = [
            InfomaniakCloudError,
            InfomaniakAuthError,
            InfomaniakNotFoundError,
            InfomaniakConflictError,
            InfomaniakQuotaExceededError,
            InfomaniakConnectionError,
            InfomaniakTimeoutError,
        ]

        for cls in exception_classes:
            exc = cls(
                "test error",
                service="compute",
                operation="create_instance",
                resource_id="srv-123",
            )
            assert exc.service == "compute", f"{cls.__name__}.service mismatch"
            assert exc.operation == "create_instance", f"{cls.__name__}.operation mismatch"
            assert exc.resource_id == "srv-123", f"{cls.__name__}.resource_id mismatch"
            assert "test error" in str(exc)

    # -----------------------------------------------------------------
    # 11. classify_openstack_error returns base type for unknown errors
    # -----------------------------------------------------------------

    def test_classify_openstack_error_unknown_returns_base(self):
        """classify_openstack_error returns InfomaniakCloudError for unrecognized errors."""
        from codomyrmex.cloud.infomaniak.exceptions import (
            classify_openstack_error,
            InfomaniakCloudError,
        )

        result = classify_openstack_error(
            Exception("Something completely unexpected happened"),
            service="unknown",
            operation="mystery_op",
            resource_id="res-999",
        )

        assert type(result) is InfomaniakCloudError
        assert result.service == "unknown"
        assert result.operation == "mystery_op"
        assert result.resource_id == "res-999"
        assert "Something completely unexpected happened" in str(result)
