"""AccessMixin functionality."""

from typing import Any

from codomyrmex.cloud.coda_io.models import (
    ACLSettings,
    PermissionList,
    Principal,
    SharingMetadata,
)
from codomyrmex.logging_monitoring import get_logger

logger = get_logger(__name__)

class AccessMixin:
    """AccessMixin class."""

    def get_sharing_metadata(self, doc_id: str) -> SharingMetadata:
        """
        Get sharing metadata for a doc.

        Args:
            doc_id: The doc ID

        Returns:
            SharingMetadata with sharing permissions
        """
        path = f"/docs/{self._encode_id(doc_id)}/acl/metadata"
        data = self._get(path)
        return SharingMetadata.from_dict(data)

    def list_permissions(
        self,
        doc_id: str,
        limit: int = 25,
        page_token: str | None = None,
    ) -> PermissionList:
        """
        List permissions for a doc.

        Args:
            doc_id: The doc ID
            limit: Maximum results
            page_token: Pagination token

        Returns:
            PermissionList with items
        """
        params = {"limit": limit, "pageToken": page_token}
        path = f"/docs/{self._encode_id(doc_id)}/acl/permissions"
        data = self._get(path, params=params)
        return PermissionList.from_dict(data)

    def add_permission(
        self,
        doc_id: str,
        access: str,
        principal: Principal | dict[str, Any],
        suppress_email: bool = False,
    ) -> dict[str, Any]:
        """
        Add a permission to a doc.

        Args:
            doc_id: The doc ID
            access: Access level ("readonly", "write", "comment")
            principal: Principal to add (email, domain, or anyone)
            suppress_email: Don't send notification email

        Returns:
            Result
        """
        if isinstance(principal, Principal):
            principal_dict = principal.to_dict()
        else:
            principal_dict = principal

        body = {
            "access": access,
            "principal": principal_dict,
            "suppressEmail": suppress_email,
        }

        path = f"/docs/{self._encode_id(doc_id)}/acl/permissions"
        return self._post(path, json_data=body)

    def delete_permission(self, doc_id: str, permission_id: str) -> dict[str, Any]:
        """
        Delete a permission.

        Args:
            doc_id: The doc ID
            permission_id: The permission ID to delete

        Returns:
            Deletion result
        """
        path = f"/docs/{self._encode_id(doc_id)}/acl/permissions/{self._encode_id(permission_id)}"
        return self._delete(path)

    def search_principals(
        self,
        doc_id: str,
        query: str | None = None,
    ) -> dict[str, Any]:
        """
        Search for principals that the doc can be shared with.

        Args:
            doc_id: The doc ID
            query: Search query (if empty, returns no results)

        Returns:
            Dict with users and groups lists
        """
        params = {"query": query} if query else {}
        path = f"/docs/{self._encode_id(doc_id)}/acl/principals/search"
        return self._get(path, params=params if params else None)

    def get_acl_settings(self, doc_id: str) -> ACLSettings:
        """
        Get ACL settings for a doc.

        Args:
            doc_id: The doc ID

        Returns:
            ACLSettings
        """
        path = f"/docs/{self._encode_id(doc_id)}/acl/settings"
        data = self._get(path)
        return ACLSettings.from_dict(data)

    def update_acl_settings(
        self,
        doc_id: str,
        allow_editors_to_change_permissions: bool | None = None,
        allow_copying: bool | None = None,
        allow_viewers_to_request_editing: bool | None = None,
    ) -> ACLSettings:
        """
        Update ACL settings for a doc.

        Args:
            doc_id: The doc ID
            allow_editors_to_change_permissions: Allow editors to change permissions
            allow_copying: Allow viewers to copy the doc
            allow_viewers_to_request_editing: Allow viewers to request edit access

        Returns:
            Updated ACLSettings
        """
        body = {}
        if allow_editors_to_change_permissions is not None:
            body["allowEditorsToChangePermissions"] = allow_editors_to_change_permissions
        if allow_copying is not None:
            body["allowCopying"] = allow_copying
        if allow_viewers_to_request_editing is not None:
            body["allowViewersToRequestEditing"] = allow_viewers_to_request_editing

        path = f"/docs/{self._encode_id(doc_id)}/acl/settings"
        data = self._patch(path, json_data=body)
        return ACLSettings.from_dict(data)

    def get_categories(self) -> dict[str, Any]:
        """
        Get all available doc categories.

        Returns:
            Dict with items list of categories
        """
        return self._get("/categories")

    def publish_doc(
        self,
        doc_id: str,
        slug: str | None = None,
        discoverable: bool | None = None,
        earn_credit: bool | None = None,
        category_names: list[str] | None = None,
        mode: str | None = None,
    ) -> dict[str, Any]:
        """
        Publish a doc.

        Args:
            doc_id: The doc ID
            slug: URL slug for the published doc
            discoverable: Make doc discoverable
            earn_credit: Earn credit for signups via doc
            category_names: Categories to apply
            mode: Publish mode ("view", "play", "edit")

        Returns:
            Result with request_id
        """
        body = {}
        if slug is not None:
            body["slug"] = slug
        if discoverable is not None:
            body["discoverable"] = discoverable
        if earn_credit is not None:
            body["earnCredit"] = earn_credit
        if category_names is not None:
            body["categoryNames"] = category_names
        if mode is not None:
            body["mode"] = mode

        path = f"/docs/{self._encode_id(doc_id)}/publish"
        return self._put(path, json_data=body)

    def unpublish_doc(self, doc_id: str) -> dict[str, Any]:
        """
        Unpublish a doc.

        Args:
            doc_id: The doc ID

        Returns:
            Result
        """
        path = f"/docs/{self._encode_id(doc_id)}/publish"
        return self._delete(path)

