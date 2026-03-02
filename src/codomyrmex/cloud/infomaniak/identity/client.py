"""
Infomaniak Identity Client (Keystone).

Provides authentication, application credentials, and user management
via the OpenStack Keystone API.
"""

from typing import Any

from ..base import InfomaniakOpenStackBase
from codomyrmex.logging_monitoring.core.logger_config import get_logger

logger = get_logger(__name__)


class InfomaniakIdentityClient(InfomaniakOpenStackBase):
    """
    Client for Infomaniak identity (Keystone) operations.

    Provides methods for managing application credentials, EC2 credentials,
    users, and projects.
    """

    _service_name = "identity"

    # =========================================================================
    # User Operations
    # =========================================================================

    def get_current_user(self) -> dict[str, Any]:
        """Get information about the currently authenticated user."""
        try:
            user = self._conn.identity.get_user(self._conn.current_user_id)
            return {
                "id": user.id,
                "name": user.name,
                "email": getattr(user, "email", None),
                "domain_id": user.domain_id,
                "is_enabled": user.is_enabled,
            }
        except Exception as e:
            logger.error(f"Failed to get current user: {e}")
            return {}

    def get_user(self, user_id: str) -> dict[str, Any] | None:
        """Get a specific user by ID."""
        try:
            user = self._conn.identity.get_user(user_id)
            return {
                "id": user.id,
                "name": user.name,
                "email": getattr(user, "email", None),
                "domain_id": user.domain_id,
            } if user else None
        except Exception as e:
            logger.error(f"Failed to get user {user_id}: {e}")
            return None

    # =========================================================================
    # Project Operations
    # =========================================================================

    def list_projects(self) -> list[dict[str, Any]]:
        """List accessible projects."""
        try:
            projects = list(self._conn.identity.projects())
            return [
                {
                    "id": p.id,
                    "name": p.name,
                    "description": p.description,
                    "is_enabled": p.is_enabled,
                    "domain_id": p.domain_id,
                }
                for p in projects
            ]
        except Exception as e:
            logger.error(f"Failed to list projects: {e}")
            return []

    def get_current_project(self) -> dict[str, Any]:
        """Get the currently scoped project."""
        try:
            project_id = self._conn.current_project_id
            project = self._conn.identity.get_project(project_id)
            return {
                "id": project.id,
                "name": project.name,
                "description": project.description,
            } if project else {}
        except Exception as e:
            logger.error(f"Failed to get current project: {e}")
            return {}

    # =========================================================================
    # Application Credentials Operations
    # =========================================================================

    def list_application_credentials(self) -> list[dict[str, Any]]:
        """List application credentials for the current user."""
        try:
            user_id = self._conn.current_user_id
            creds = list(self._conn.identity.application_credentials(user=user_id))
            return [
                {
                    "id": c.id,
                    "name": c.name,
                    "description": getattr(c, "description", None),
                    "expires_at": str(c.expires_at) if c.expires_at else None,
                    "roles": [r.get("name") for r in (c.roles or [])],
                }
                for c in creds
            ]
        except Exception as e:
            logger.error(f"Failed to list application credentials: {e}")
            return []

    def create_application_credential(
        self,
        name: str,
        description: str | None = None,
        expires_at: str | None = None,
        roles: list[str] | None = None,
        unrestricted: bool = False
    ) -> dict[str, Any] | None:
        """
        Create an application credential.

        Args:
            name: Credential name
            description: Optional description
            expires_at: Expiration datetime (ISO format)
            roles: List of role names (defaults to all user roles)
            unrestricted: Allow use for all operations including credential creation

        Returns:
            Credential dict including the secret (only returned once!)
        """
        try:
            user_id = self._conn.current_user_id

            cred = self._conn.identity.create_application_credential(
                user=user_id,
                name=name,
                description=description,
                expires_at=expires_at,
                roles=roles,
                unrestricted=unrestricted
            )

            logger.info(f"Created application credential: {cred.id}")
            return {
                "id": cred.id,
                "name": cred.name,
                "secret": cred.secret,  # Only returned once!
                "expires_at": str(cred.expires_at) if cred.expires_at else None,
            }
        except Exception as e:
            logger.error(f"Failed to create application credential {name}: {e}")
            return None

    def get_application_credential(self, credential_id: str) -> dict[str, Any] | None:
        """Get an application credential by ID."""
        try:
            user_id = self._conn.current_user_id
            cred = self._conn.identity.get_application_credential(
                user=user_id,
                application_credential=credential_id
            )
            return {
                "id": cred.id,
                "name": cred.name,
                "description": getattr(cred, "description", None),
                "expires_at": str(cred.expires_at) if cred.expires_at else None,
            } if cred else None
        except Exception as e:
            logger.error(f"Failed to get application credential {credential_id}: {e}")
            return None

    def delete_application_credential(self, credential_id: str) -> bool:
        """Delete an application credential."""
        try:
            user_id = self._conn.current_user_id
            self._conn.identity.delete_application_credential(
                user=user_id,
                application_credential=credential_id
            )
            logger.info(f"Deleted application credential: {credential_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to delete application credential {credential_id}: {e}")
            return False

    # =========================================================================
    # Role Operations
    # =========================================================================

    def list_roles(self) -> list[dict[str, Any]]:
        """List available roles."""
        try:
            roles = list(self._conn.identity.roles())
            return [
                {"id": r.id, "name": r.name, "description": r.description}
                for r in roles
            ]
        except Exception as e:
            logger.error(f"Failed to list roles: {e}")
            return []

    def list_user_roles(self, project_id: str | None = None) -> list[dict[str, Any]]:
        """List roles assigned to the current user."""
        try:
            user_id = self._conn.current_user_id
            project_id = project_id or self._conn.current_project_id

            role_assignments = list(self._conn.identity.role_assignments(
                user=user_id,
                project=project_id
            ))

            roles = []
            for ra in role_assignments:
                role = self._conn.identity.get_role(ra.role.get("id"))
                if role:
                    roles.append({"id": role.id, "name": role.name})
            return roles
        except Exception as e:
            logger.error(f"Failed to list user roles: {e}")
            return []

    # =========================================================================
    # EC2 Credentials (for S3)
    # =========================================================================

    def list_ec2_credentials(self) -> list[dict[str, Any]]:
        """List EC2-style credentials (used for S3 access)."""
        try:
            user_id = self._conn.current_user_id
            creds = list(self._conn.identity.credentials(user_id=user_id))
            return [
                {
                    "id": c.id,
                    "access": c.access,
                    "project_id": c.project_id,
                }
                for c in creds if c.type == "ec2"
            ]
        except Exception as e:
            logger.error(f"Failed to list EC2 credentials: {e}")
            return []

    def create_ec2_credentials(
        self,
        project_id: str | None = None
    ) -> dict[str, Any] | None:
        """
        Create EC2-style credentials for S3 access.

        Args:
            project_id: Project ID (defaults to current project)

        Returns:
            Credential dict with access and secret keys
        """
        try:
            user_id = self._conn.current_user_id
            project_id = project_id or self._conn.current_project_id

            cred = self._conn.identity.create_credential(
                user_id=user_id,
                type="ec2",
                project_id=project_id,
                blob='{"access": "", "secret": ""}'  # Keystone generates these
            )

            logger.info(f"Created EC2 credentials: {cred.id}")
            return {
                "id": cred.id,
                "access": cred.access,
                "secret": cred.secret,
                "project_id": cred.project_id,
            }
        except Exception as e:
            logger.error(f"Failed to create EC2 credentials: {e}")
            return None

    def delete_ec2_credentials(self, credential_id: str) -> bool:
        """Delete EC2-style credentials."""
        try:
            self._conn.identity.delete_credential(credential_id)
            logger.info(f"Deleted EC2 credentials: {credential_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to delete EC2 credentials {credential_id}: {e}")
            return False
