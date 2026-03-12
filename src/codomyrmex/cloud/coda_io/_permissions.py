"""Permissions and ACL models for Coda.io."""

from dataclasses import dataclass
from typing import Any


@dataclass
class Principal:
    """A principal (user or group) for permissions."""

    type: str  # "email", "domain", "anyone"
    email: str | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Principal":

        return cls(
            type=data.get("type", ""),
            email=data.get("email"),
        )

    def to_dict(self) -> dict[str, Any]:

        result = {"type": self.type}
        if self.email:
            result["email"] = self.email
        return result


@dataclass
class Permission:
    """A permission on a doc."""

    id: str
    principal: Principal
    access: str

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Permission":

        return cls(
            id=data.get("id", ""),
            principal=Principal.from_dict(data.get("principal", {})),
            access=data.get("access", ""),
        )


@dataclass
class PermissionList:
    """List of permissions with pagination."""

    items: list[Permission]
    href: str
    next_page_token: str | None = None
    next_page_link: str | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "PermissionList":

        return cls(
            items=[Permission.from_dict(item) for item in data.get("items", [])],
            href=data.get("href", ""),
            next_page_token=data.get("nextPageToken"),
            next_page_link=data.get("nextPageLink"),
        )


@dataclass
class SharingMetadata:
    """Sharing metadata for a doc."""

    can_share: bool
    can_share_with_workspace: bool
    can_share_with_org: bool
    can_copy: bool

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "SharingMetadata":

        return cls(
            can_share=data.get("canShare", False),
            can_share_with_workspace=data.get("canShareWithWorkspace", False),
            can_share_with_org=data.get("canShareWithOrg", False),
            can_copy=data.get("canCopy", False),
        )


@dataclass
class ACLSettings:
    """ACL settings for a doc."""

    allow_editors_to_change_permissions: bool
    allow_copying: bool
    allow_viewers_to_request_editing: bool

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ACLSettings":

        return cls(
            allow_editors_to_change_permissions=data.get(
                "allowEditorsToChangePermissions", False
            ),
            allow_copying=data.get("allowCopying", False),
            allow_viewers_to_request_editing=data.get(
                "allowViewersToRequestEditing", False
            ),
        )
