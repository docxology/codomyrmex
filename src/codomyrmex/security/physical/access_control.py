from datetime import datetime
from typing import Optional

from dataclasses import dataclass

from codomyrmex.logging_monitoring.logger_config import get_logger




























"""Physical access control systems."""



logger = get_logger(__name__)


@dataclass
class AccessPermission:
    """Represents an access permission."""
    
    user_id: str
    resource: str
    permission_type: str  # read, write, admin
    granted_at: datetime
    expires_at: Optional[datetime] = None


class AccessControlSystem:
    """Manages physical access control."""
    
    def __init__(self):
        self.permissions: dict[str, list[AccessPermission]] = {}
        logger.info("AccessControlSystem initialized")
    
    def grant_access(
        self,
        user_id: str,
        resource: str,
        permission_type: str,
        expires_at: Optional[datetime] = None,
    ) -> AccessPermission:
        """Grant access permission to a user."""
        permission = AccessPermission(
            user_id=user_id,
            resource=resource,
            permission_type=permission_type,
            granted_at=datetime.now(),
            expires_at=expires_at,
        )
        
        if user_id not in self.permissions:
            self.permissions[user_id] = []
        
        self.permissions[user_id].append(permission)
        logger.info(f"Granted {permission_type} access to {user_id} for {resource}")
        return permission
    
    def revoke_access(self, user_id: str, resource: str) -> bool:
        """Revoke access permission for a user."""
        if user_id in self.permissions:
            self.permissions[user_id] = [
                p for p in self.permissions[user_id]
                if p.resource != resource
            ]
            logger.info(f"Revoked access for {user_id} to {resource}")
            return True
        return False
    
    def check_access(self, user_id: str, resource: str, permission_type: str) -> bool:
        """Check if user has access permission."""
        if user_id not in self.permissions:
            return False
        
        now = datetime.now()
        for permission in self.permissions[user_id]:
            if permission.resource == resource:
                if permission.permission_type == permission_type or permission.permission_type == "admin":
                    if permission.expires_at is None or permission.expires_at > now:
                        return True
        return False


def check_access_permission(
    user_id: str,
    resource: str,
    permission_type: str,
    access_control: Optional[AccessControlSystem] = None,
) -> bool:
    """Check access permission."""
    if access_control is None:
        access_control = AccessControlSystem()
    return access_control.check_access(user_id, resource, permission_type)


def grant_access(
    user_id: str,
    resource: str,
    permission_type: str,
    expires_at: Optional[datetime] = None,
    access_control: Optional[AccessControlSystem] = None,
) -> AccessPermission:
    """Grant access permission."""
    if access_control is None:
        access_control = AccessControlSystem()
    return access_control.grant_access(user_id, resource, permission_type, expires_at)


def revoke_access(
    user_id: str,
    resource: str,
    access_control: Optional[AccessControlSystem] = None,
) -> bool:
    """Revoke access permission."""
    if access_control is None:
        access_control = AccessControlSystem()
    return access_control.revoke_access(user_id, resource)



