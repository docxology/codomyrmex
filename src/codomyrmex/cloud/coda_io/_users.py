"""User models for Coda.io."""

from dataclasses import dataclass
from typing import Any

from ._references import WorkspaceReference


@dataclass
class User:
    """Current user information from whoami endpoint."""

    name: str
    login_id: str
    type: str
    scoped: bool
    token_name: str
    href: str
    workspace: WorkspaceReference | None = None
    picture_link: str | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "User":

        return cls(
            name=data.get("name", ""),
            login_id=data.get("loginId", ""),
            type=data.get("type", "user"),
            scoped=data.get("scoped", False),
            token_name=data.get("tokenName", ""),
            href=data.get("href", ""),
            workspace=WorkspaceReference.from_dict(data.get("workspace")),
            picture_link=data.get("pictureLink"),
        )
