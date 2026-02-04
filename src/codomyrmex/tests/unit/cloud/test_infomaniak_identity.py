"""
Unit tests for InfomaniakIdentityClient (Keystone).

Tests cover all identity operations:
- User operations (get_current_user, get_user)
- Project operations (list_projects, get_current_project)
- Application credentials (list, create, get, delete)
- Role operations (list_roles, list_user_roles)
- EC2 credentials (list, create, delete)
- Error handling for every method

Total: ~22 tests in a single TestInfomaniakIdentity class.
"""

import pytest
from unittest.mock import MagicMock


class TestInfomaniakIdentity:
    """Comprehensive tests for InfomaniakIdentityClient."""

    @pytest.fixture
    def mock_openstack_connection(self):
        """Create a mock OpenStack connection with standard IDs."""
        conn = MagicMock()
        conn.current_user_id = "user-test-123"
        conn.current_project_id = "proj-test-456"
        return conn

    def _make_client(self, conn):
        """Helper to create an InfomaniakIdentityClient from a mock connection."""
        from codomyrmex.cloud.infomaniak.identity.client import InfomaniakIdentityClient
        return InfomaniakIdentityClient(conn)

    # =====================================================================
    # User Operations
    # =====================================================================

    def test_get_current_user_success(self, mock_openstack_connection):
        """get_current_user returns dict with id, name, email, domain_id, is_enabled."""
        mock_user = MagicMock()
        mock_user.id = "user-test-123"
        mock_user.name = "alice"
        mock_user.email = "alice@infomaniak.cloud"
        mock_user.domain_id = "domain-abc"
        mock_user.is_enabled = True

        mock_openstack_connection.identity.get_user.return_value = mock_user

        client = self._make_client(mock_openstack_connection)
        result = client.get_current_user()

        assert result["id"] == "user-test-123"
        assert result["name"] == "alice"
        assert result["email"] == "alice@infomaniak.cloud"
        assert result["domain_id"] == "domain-abc"
        assert result["is_enabled"] is True
        mock_openstack_connection.identity.get_user.assert_called_once_with("user-test-123")

    def test_get_current_user_error_returns_empty_dict(self, mock_openstack_connection):
        """get_current_user returns {} on exception."""
        mock_openstack_connection.identity.get_user.side_effect = Exception("auth failure")

        client = self._make_client(mock_openstack_connection)
        result = client.get_current_user()

        assert result == {}

    def test_get_user_success(self, mock_openstack_connection):
        """get_user returns user dict for a specific user ID."""
        mock_user = MagicMock()
        mock_user.id = "user-other-789"
        mock_user.name = "bob"
        mock_user.email = "bob@example.com"
        mock_user.domain_id = "domain-xyz"

        mock_openstack_connection.identity.get_user.return_value = mock_user

        client = self._make_client(mock_openstack_connection)
        result = client.get_user("user-other-789")

        assert result is not None
        assert result["id"] == "user-other-789"
        assert result["name"] == "bob"
        assert result["email"] == "bob@example.com"
        assert result["domain_id"] == "domain-xyz"
        mock_openstack_connection.identity.get_user.assert_called_once_with("user-other-789")

    def test_get_user_error_returns_none(self, mock_openstack_connection):
        """get_user returns None on exception."""
        mock_openstack_connection.identity.get_user.side_effect = Exception("not found")

        client = self._make_client(mock_openstack_connection)
        result = client.get_user("nonexistent-user")

        assert result is None

    # =====================================================================
    # Project Operations
    # =====================================================================

    def test_list_projects_success(self, mock_openstack_connection):
        """list_projects returns list of project dicts."""
        mock_proj1 = MagicMock()
        mock_proj1.id = "proj-1"
        mock_proj1.name = "alpha"
        mock_proj1.description = "Alpha project"
        mock_proj1.is_enabled = True
        mock_proj1.domain_id = "domain-abc"

        mock_proj2 = MagicMock()
        mock_proj2.id = "proj-2"
        mock_proj2.name = "beta"
        mock_proj2.description = "Beta project"
        mock_proj2.is_enabled = False
        mock_proj2.domain_id = "domain-abc"

        mock_openstack_connection.identity.projects.return_value = [mock_proj1, mock_proj2]

        client = self._make_client(mock_openstack_connection)
        result = client.list_projects()

        assert len(result) == 2
        assert result[0]["id"] == "proj-1"
        assert result[0]["name"] == "alpha"
        assert result[0]["is_enabled"] is True
        assert result[1]["id"] == "proj-2"
        assert result[1]["is_enabled"] is False

    def test_list_projects_error_returns_empty_list(self, mock_openstack_connection):
        """list_projects returns [] on exception."""
        mock_openstack_connection.identity.projects.side_effect = Exception("forbidden")

        client = self._make_client(mock_openstack_connection)
        result = client.list_projects()

        assert result == []

    def test_get_current_project_success(self, mock_openstack_connection):
        """get_current_project returns dict with id, name, description."""
        mock_project = MagicMock()
        mock_project.id = "proj-test-456"
        mock_project.name = "main-project"
        mock_project.description = "The main project"

        mock_openstack_connection.identity.get_project.return_value = mock_project

        client = self._make_client(mock_openstack_connection)
        result = client.get_current_project()

        assert result["id"] == "proj-test-456"
        assert result["name"] == "main-project"
        assert result["description"] == "The main project"
        mock_openstack_connection.identity.get_project.assert_called_once_with("proj-test-456")

    def test_get_current_project_error_returns_empty_dict(self, mock_openstack_connection):
        """get_current_project returns {} on exception."""
        mock_openstack_connection.identity.get_project.side_effect = Exception("timeout")

        client = self._make_client(mock_openstack_connection)
        result = client.get_current_project()

        assert result == {}

    # =====================================================================
    # Application Credentials
    # =====================================================================

    def test_list_application_credentials_success(self, mock_openstack_connection):
        """list_application_credentials returns credential dicts with role names."""
        mock_cred = MagicMock()
        mock_cred.id = "appcred-001"
        mock_cred.name = "ci-deploy"
        mock_cred.description = "For CI/CD pipelines"
        mock_cred.expires_at = "2026-12-31T23:59:59Z"
        mock_cred.roles = [{"name": "member"}, {"name": "reader"}]

        mock_openstack_connection.identity.application_credentials.return_value = [mock_cred]

        client = self._make_client(mock_openstack_connection)
        result = client.list_application_credentials()

        assert len(result) == 1
        assert result[0]["id"] == "appcred-001"
        assert result[0]["name"] == "ci-deploy"
        assert result[0]["description"] == "For CI/CD pipelines"
        assert result[0]["expires_at"] == "2026-12-31T23:59:59Z"
        assert "member" in result[0]["roles"]
        assert "reader" in result[0]["roles"]
        mock_openstack_connection.identity.application_credentials.assert_called_once_with(
            user="user-test-123"
        )

    def test_list_application_credentials_error_returns_empty_list(self, mock_openstack_connection):
        """list_application_credentials returns [] on exception."""
        mock_openstack_connection.identity.application_credentials.side_effect = Exception("denied")

        client = self._make_client(mock_openstack_connection)
        result = client.list_application_credentials()

        assert result == []

    def test_create_application_credential_success(self, mock_openstack_connection):
        """create_application_credential returns dict with id, name, secret, expires_at."""
        mock_cred = MagicMock()
        mock_cred.id = "appcred-new"
        mock_cred.name = "terraform-cred"
        mock_cred.secret = "super-secret-value-only-shown-once"
        mock_cred.expires_at = None

        mock_openstack_connection.identity.create_application_credential.return_value = mock_cred

        client = self._make_client(mock_openstack_connection)
        result = client.create_application_credential(
            name="terraform-cred",
            description="For Terraform",
            roles=["member"],
            unrestricted=False,
        )

        assert result is not None
        assert result["id"] == "appcred-new"
        assert result["name"] == "terraform-cred"
        assert result["secret"] == "super-secret-value-only-shown-once"
        assert result["expires_at"] is None
        mock_openstack_connection.identity.create_application_credential.assert_called_once_with(
            user="user-test-123",
            name="terraform-cred",
            description="For Terraform",
            expires_at=None,
            roles=["member"],
            unrestricted=False,
        )

    def test_create_application_credential_error_returns_none(self, mock_openstack_connection):
        """create_application_credential returns None on exception."""
        mock_openstack_connection.identity.create_application_credential.side_effect = Exception(
            "duplicate name"
        )

        client = self._make_client(mock_openstack_connection)
        result = client.create_application_credential(name="duplicate-cred")

        assert result is None

    def test_get_application_credential_success(self, mock_openstack_connection):
        """get_application_credential returns credential dict by ID."""
        mock_cred = MagicMock()
        mock_cred.id = "appcred-fetch"
        mock_cred.name = "fetched-cred"
        mock_cred.description = "Some description"
        mock_cred.expires_at = "2027-06-01T00:00:00Z"

        mock_openstack_connection.identity.get_application_credential.return_value = mock_cred

        client = self._make_client(mock_openstack_connection)
        result = client.get_application_credential("appcred-fetch")

        assert result is not None
        assert result["id"] == "appcred-fetch"
        assert result["name"] == "fetched-cred"
        assert result["description"] == "Some description"
        assert result["expires_at"] == "2027-06-01T00:00:00Z"
        mock_openstack_connection.identity.get_application_credential.assert_called_once_with(
            user="user-test-123",
            application_credential="appcred-fetch",
        )

    def test_get_application_credential_error_returns_none(self, mock_openstack_connection):
        """get_application_credential returns None on exception."""
        mock_openstack_connection.identity.get_application_credential.side_effect = Exception(
            "not found"
        )

        client = self._make_client(mock_openstack_connection)
        result = client.get_application_credential("nonexistent")

        assert result is None

    def test_delete_application_credential_success(self, mock_openstack_connection):
        """delete_application_credential returns True on success."""
        client = self._make_client(mock_openstack_connection)
        result = client.delete_application_credential("appcred-del")

        assert result is True
        mock_openstack_connection.identity.delete_application_credential.assert_called_once_with(
            user="user-test-123",
            application_credential="appcred-del",
        )

    def test_delete_application_credential_error_returns_false(self, mock_openstack_connection):
        """delete_application_credential returns False on exception."""
        mock_openstack_connection.identity.delete_application_credential.side_effect = Exception(
            "forbidden"
        )

        client = self._make_client(mock_openstack_connection)
        result = client.delete_application_credential("appcred-nope")

        assert result is False

    # =====================================================================
    # Role Operations
    # =====================================================================

    def test_list_roles_success(self, mock_openstack_connection):
        """list_roles returns list of role dicts with id, name, description."""
        mock_role1 = MagicMock()
        mock_role1.id = "role-admin"
        mock_role1.name = "admin"
        mock_role1.description = "Administrator role"

        mock_role2 = MagicMock()
        mock_role2.id = "role-member"
        mock_role2.name = "member"
        mock_role2.description = "Member role"

        mock_openstack_connection.identity.roles.return_value = [mock_role1, mock_role2]

        client = self._make_client(mock_openstack_connection)
        result = client.list_roles()

        assert len(result) == 2
        assert result[0]["id"] == "role-admin"
        assert result[0]["name"] == "admin"
        assert result[1]["name"] == "member"

    def test_list_roles_error_returns_empty_list(self, mock_openstack_connection):
        """list_roles returns [] on exception."""
        mock_openstack_connection.identity.roles.side_effect = Exception("service unavailable")

        client = self._make_client(mock_openstack_connection)
        result = client.list_roles()

        assert result == []

    def test_list_user_roles_success(self, mock_openstack_connection):
        """list_user_roles resolves role assignments to role dicts."""
        mock_ra1 = MagicMock()
        mock_ra1.role = {"id": "role-1"}
        mock_ra2 = MagicMock()
        mock_ra2.role = {"id": "role-2"}

        mock_openstack_connection.identity.role_assignments.return_value = [mock_ra1, mock_ra2]

        mock_resolved_role1 = MagicMock()
        mock_resolved_role1.id = "role-1"
        mock_resolved_role1.name = "member"

        mock_resolved_role2 = MagicMock()
        mock_resolved_role2.id = "role-2"
        mock_resolved_role2.name = "reader"

        mock_openstack_connection.identity.get_role.side_effect = [
            mock_resolved_role1,
            mock_resolved_role2,
        ]

        client = self._make_client(mock_openstack_connection)
        result = client.list_user_roles()

        assert len(result) == 2
        assert result[0] == {"id": "role-1", "name": "member"}
        assert result[1] == {"id": "role-2", "name": "reader"}
        mock_openstack_connection.identity.role_assignments.assert_called_once_with(
            user="user-test-123",
            project="proj-test-456",
        )

    def test_list_user_roles_with_explicit_project(self, mock_openstack_connection):
        """list_user_roles uses provided project_id instead of current."""
        mock_openstack_connection.identity.role_assignments.return_value = []

        client = self._make_client(mock_openstack_connection)
        result = client.list_user_roles(project_id="proj-explicit-999")

        assert result == []
        mock_openstack_connection.identity.role_assignments.assert_called_once_with(
            user="user-test-123",
            project="proj-explicit-999",
        )

    def test_list_user_roles_error_returns_empty_list(self, mock_openstack_connection):
        """list_user_roles returns [] on exception."""
        mock_openstack_connection.identity.role_assignments.side_effect = Exception("timeout")

        client = self._make_client(mock_openstack_connection)
        result = client.list_user_roles()

        assert result == []

    # =====================================================================
    # EC2 Credentials
    # =====================================================================

    def test_list_ec2_credentials_filters_by_type(self, mock_openstack_connection):
        """list_ec2_credentials only returns credentials with type=='ec2'."""
        mock_ec2_cred = MagicMock()
        mock_ec2_cred.id = "cred-ec2"
        mock_ec2_cred.type = "ec2"
        mock_ec2_cred.access = "AKIA-EXAMPLE"
        mock_ec2_cred.project_id = "proj-test-456"

        mock_other_cred = MagicMock()
        mock_other_cred.id = "cred-other"
        mock_other_cred.type = "cert"
        mock_other_cred.access = "CERT-EXAMPLE"
        mock_other_cred.project_id = "proj-test-456"

        mock_openstack_connection.identity.credentials.return_value = [
            mock_ec2_cred,
            mock_other_cred,
        ]

        client = self._make_client(mock_openstack_connection)
        result = client.list_ec2_credentials()

        assert len(result) == 1
        assert result[0]["id"] == "cred-ec2"
        assert result[0]["access"] == "AKIA-EXAMPLE"
        assert result[0]["project_id"] == "proj-test-456"
        mock_openstack_connection.identity.credentials.assert_called_once_with(
            user_id="user-test-123"
        )

    def test_list_ec2_credentials_error_returns_empty_list(self, mock_openstack_connection):
        """list_ec2_credentials returns [] on exception."""
        mock_openstack_connection.identity.credentials.side_effect = Exception("connection error")

        client = self._make_client(mock_openstack_connection)
        result = client.list_ec2_credentials()

        assert result == []

    def test_create_ec2_credentials_success(self, mock_openstack_connection):
        """create_ec2_credentials returns dict with id, access, secret, project_id."""
        mock_cred = MagicMock()
        mock_cred.id = "ec2-new"
        mock_cred.access = "AKIA-NEW"
        mock_cred.secret = "SECRET-NEW-VALUE"
        mock_cred.project_id = "proj-test-456"

        mock_openstack_connection.identity.create_credential.return_value = mock_cred

        client = self._make_client(mock_openstack_connection)
        result = client.create_ec2_credentials()

        assert result is not None
        assert result["id"] == "ec2-new"
        assert result["access"] == "AKIA-NEW"
        assert result["secret"] == "SECRET-NEW-VALUE"
        assert result["project_id"] == "proj-test-456"
        mock_openstack_connection.identity.create_credential.assert_called_once_with(
            user_id="user-test-123",
            type="ec2",
            project_id="proj-test-456",
            blob='{"access": "", "secret": ""}',
        )

    def test_create_ec2_credentials_with_explicit_project(self, mock_openstack_connection):
        """create_ec2_credentials uses provided project_id when specified."""
        mock_cred = MagicMock()
        mock_cred.id = "ec2-custom"
        mock_cred.access = "AKIA-CUSTOM"
        mock_cred.secret = "SECRET-CUSTOM"
        mock_cred.project_id = "proj-other-789"

        mock_openstack_connection.identity.create_credential.return_value = mock_cred

        client = self._make_client(mock_openstack_connection)
        result = client.create_ec2_credentials(project_id="proj-other-789")

        assert result is not None
        assert result["project_id"] == "proj-other-789"
        mock_openstack_connection.identity.create_credential.assert_called_once_with(
            user_id="user-test-123",
            type="ec2",
            project_id="proj-other-789",
            blob='{"access": "", "secret": ""}',
        )

    def test_create_ec2_credentials_error_returns_none(self, mock_openstack_connection):
        """create_ec2_credentials returns None on exception."""
        mock_openstack_connection.identity.create_credential.side_effect = Exception("quota exceeded")

        client = self._make_client(mock_openstack_connection)
        result = client.create_ec2_credentials()

        assert result is None

    def test_delete_ec2_credentials_success(self, mock_openstack_connection):
        """delete_ec2_credentials returns True on success."""
        client = self._make_client(mock_openstack_connection)
        result = client.delete_ec2_credentials("ec2-del")

        assert result is True
        mock_openstack_connection.identity.delete_credential.assert_called_once_with("ec2-del")

    def test_delete_ec2_credentials_error_returns_false(self, mock_openstack_connection):
        """delete_ec2_credentials returns False on exception."""
        mock_openstack_connection.identity.delete_credential.side_effect = Exception("not found")

        client = self._make_client(mock_openstack_connection)
        result = client.delete_ec2_credentials("ec2-missing")

        assert result is False
