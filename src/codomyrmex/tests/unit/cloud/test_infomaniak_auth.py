"""
Unit tests for Infomaniak authentication module.

Tests cover:
- InfomaniakAuthError re-export from exceptions module
- InfomaniakCredentials dataclass and from_env factory
- InfomaniakS3Credentials dataclass and from_env factory
- to_openstack_auth() conversion
- S3Credentials defaults
- create_openstack_connection with mock openstack module
- create_s3_client with mock boto3 module
- Error paths for missing credentials and import failures

Total: ~16 tests in 1 test class.
"""

import sys
import pytest
from unittest.mock import MagicMock, patch


class TestInfomaniakAuthModule:
    """Comprehensive tests for the Infomaniak auth module."""

    # -----------------------------------------------------------------
    # InfomaniakAuthError re-export
    # -----------------------------------------------------------------

    def test_auth_error_reexported_from_auth_module(self):
        """InfomaniakAuthError is importable directly from auth.py."""
        from codomyrmex.cloud.infomaniak.auth import InfomaniakAuthError

        assert InfomaniakAuthError is not None

    def test_auth_error_is_subclass_of_cloud_error(self):
        """InfomaniakAuthError inherits from InfomaniakCloudError."""
        from codomyrmex.cloud.infomaniak.exceptions import (
            InfomaniakAuthError,
            InfomaniakCloudError,
        )

        assert issubclass(InfomaniakAuthError, InfomaniakCloudError)
        # Also verify it is raiseable with the expected attributes
        err = InfomaniakAuthError(
            "auth failed", service="identity", operation="login"
        )
        assert err.service == "identity"
        assert err.operation == "login"
        assert "auth failed" in str(err)

    def test_auth_error_same_class_in_auth_and_exceptions(self):
        """The re-exported InfomaniakAuthError is the exact same class object."""
        from codomyrmex.cloud.infomaniak.auth import (
            InfomaniakAuthError as AuthFromAuth,
        )
        from codomyrmex.cloud.infomaniak.exceptions import (
            InfomaniakAuthError as AuthFromExceptions,
        )

        assert AuthFromAuth is AuthFromExceptions

    # -----------------------------------------------------------------
    # InfomaniakCredentials.from_env
    # -----------------------------------------------------------------

    def test_credentials_from_env_valid(self, infomaniak_openstack_env):
        """Credentials are correctly populated from valid environment variables."""
        from codomyrmex.cloud.infomaniak.auth import InfomaniakCredentials

        with patch.dict("os.environ", infomaniak_openstack_env, clear=True):
            creds = InfomaniakCredentials.from_env()

            assert creds.application_credential_id == "test-cred-id"
            assert creds.application_credential_secret == "test-cred-secret"
            assert creds.auth_url == "https://api.pub1.infomaniak.cloud/identity/v3/"
            assert creds.region == "dc3-a"

    def test_credentials_from_env_missing_raises(self):
        """Missing required env vars raise InfomaniakAuthError."""
        from codomyrmex.cloud.infomaniak.auth import (
            InfomaniakCredentials,
            InfomaniakAuthError,
        )

        with patch.dict("os.environ", {}, clear=True):
            with pytest.raises(
                InfomaniakAuthError, match="Missing required environment variables"
            ):
                InfomaniakCredentials.from_env()

    def test_credentials_from_env_defaults(self):
        """Defaults are applied when optional env vars are absent."""
        from codomyrmex.cloud.infomaniak.auth import InfomaniakCredentials

        with patch.dict(
            "os.environ",
            {
                "INFOMANIAK_APP_CREDENTIAL_ID": "id-only",
                "INFOMANIAK_APP_CREDENTIAL_SECRET": "secret-only",
            },
            clear=True,
        ):
            creds = InfomaniakCredentials.from_env()

            assert creds.auth_url == "https://api.pub1.infomaniak.cloud/identity/v3/"
            assert creds.region == "dc3-a"
            assert creds.project_id is None

    # -----------------------------------------------------------------
    # to_openstack_auth()
    # -----------------------------------------------------------------

    def test_to_openstack_auth_returns_correct_dict(self):
        """to_openstack_auth() produces the expected auth dict for the SDK."""
        from codomyrmex.cloud.infomaniak.auth import InfomaniakCredentials

        creds = InfomaniakCredentials(
            application_credential_id="my-id",
            application_credential_secret="my-secret",
            auth_url="https://custom.api/identity/v3/",
        )

        auth_dict = creds.to_openstack_auth()

        assert auth_dict == {
            "auth_url": "https://custom.api/identity/v3/",
            "application_credential_id": "my-id",
            "application_credential_secret": "my-secret",
        }

    # -----------------------------------------------------------------
    # InfomaniakS3Credentials.from_env
    # -----------------------------------------------------------------

    def test_s3_credentials_from_env_valid(self, infomaniak_s3_env):
        """S3 credentials are correctly populated from valid environment variables."""
        from codomyrmex.cloud.infomaniak.auth import InfomaniakS3Credentials

        with patch.dict("os.environ", infomaniak_s3_env, clear=True):
            creds = InfomaniakS3Credentials.from_env()

            assert creds.access_key == "test-s3-access"
            assert creds.secret_key == "test-s3-secret"
            assert creds.endpoint_url == "https://s3.pub1.infomaniak.cloud/"

    def test_s3_credentials_from_env_missing_raises(self):
        """Missing required S3 env vars raise InfomaniakAuthError."""
        from codomyrmex.cloud.infomaniak.auth import (
            InfomaniakS3Credentials,
            InfomaniakAuthError,
        )

        with patch.dict("os.environ", {}, clear=True):
            with pytest.raises(
                InfomaniakAuthError, match="Missing required environment variables"
            ):
                InfomaniakS3Credentials.from_env()

    def test_s3_credentials_defaults(self):
        """S3 credentials use correct defaults for endpoint and region."""
        from codomyrmex.cloud.infomaniak.auth import InfomaniakS3Credentials

        creds = InfomaniakS3Credentials(
            access_key="ak",
            secret_key="sk",
        )

        assert creds.endpoint_url == "https://s3.pub1.infomaniak.cloud/"
        assert creds.region == "us-east-1"

    # -----------------------------------------------------------------
    # create_openstack_connection
    # -----------------------------------------------------------------

    def test_create_openstack_connection_success(self):
        """create_openstack_connection calls openstack.connect with correct params."""
        from codomyrmex.cloud.infomaniak.auth import (
            InfomaniakCredentials,
            create_openstack_connection,
        )

        mock_openstack = MagicMock()
        mock_conn = MagicMock()
        mock_openstack.connect.return_value = mock_conn

        creds = InfomaniakCredentials(
            application_credential_id="cred-id",
            application_credential_secret="cred-secret",
            auth_url="https://api.pub1.infomaniak.cloud/identity/v3/",
            region="dc3-a",
        )

        with patch.dict(sys.modules, {"openstack": mock_openstack}):
            result = create_openstack_connection(creds)

        assert result is mock_conn
        mock_openstack.connect.assert_called_once_with(
            auth_type="v3applicationcredential",
            auth_url="https://api.pub1.infomaniak.cloud/identity/v3/",
            application_credential_id="cred-id",
            application_credential_secret="cred-secret",
            region_name="dc3-a",
        )

    def test_create_openstack_connection_auth_failure(self):
        """create_openstack_connection raises InfomaniakAuthError on SDK failure."""
        from codomyrmex.cloud.infomaniak.auth import (
            InfomaniakCredentials,
            InfomaniakAuthError,
            create_openstack_connection,
        )

        mock_openstack = MagicMock()
        mock_openstack.connect.side_effect = Exception("Unauthorized 401")

        creds = InfomaniakCredentials(
            application_credential_id="bad-id",
            application_credential_secret="bad-secret",
        )

        with patch.dict(sys.modules, {"openstack": mock_openstack}):
            with pytest.raises(InfomaniakAuthError, match="Authentication failed"):
                create_openstack_connection(creds)

    # -----------------------------------------------------------------
    # create_s3_client
    # -----------------------------------------------------------------

    def test_create_s3_client_success(self):
        """create_s3_client calls boto3.client with correct params."""
        from codomyrmex.cloud.infomaniak.auth import (
            InfomaniakS3Credentials,
            create_s3_client,
        )

        mock_boto3 = MagicMock()
        mock_client = MagicMock()
        mock_boto3.client.return_value = mock_client

        creds = InfomaniakS3Credentials(
            access_key="s3-ak",
            secret_key="s3-sk",
            endpoint_url="https://s3.pub1.infomaniak.cloud/",
            region="us-east-1",
        )

        with patch.dict(sys.modules, {"boto3": mock_boto3}):
            result = create_s3_client(creds)

        assert result is mock_client
        mock_boto3.client.assert_called_once_with(
            "s3",
            endpoint_url="https://s3.pub1.infomaniak.cloud/",
            aws_access_key_id="s3-ak",
            aws_secret_access_key="s3-sk",
            region_name="us-east-1",
        )

    def test_create_s3_client_import_error_without_boto3(self):
        """create_s3_client raises ImportError when boto3 is not installed."""
        from codomyrmex.cloud.infomaniak.auth import (
            InfomaniakS3Credentials,
            create_s3_client,
        )

        creds = InfomaniakS3Credentials(
            access_key="ak",
            secret_key="sk",
        )

        # Remove boto3 from sys.modules and make import fail
        with patch.dict(sys.modules, {"boto3": None}):
            with pytest.raises(ImportError, match="boto3 is required"):
                create_s3_client(creds)
