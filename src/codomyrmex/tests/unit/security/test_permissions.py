"""Tests for security/permissions.py — Permission, Role, Grant, PermissionModel."""


from codomyrmex.security.permissions import (
    Grant,
    Permission,
    PermissionModel,
    Role,
)


class TestPermissionEnum:
    """Tests for the Permission enum."""

    def test_all_permissions_exist(self):
        """All five permissions are defined."""
        vals = {p.value for p in Permission}
        assert vals == {"read", "write", "execute", "delete", "admin"}

    def test_permission_values(self):
        """Enum values match expected strings."""
        assert Permission.READ.value == "read"
        assert Permission.WRITE.value == "write"
        assert Permission.EXECUTE.value == "execute"
        assert Permission.DELETE.value == "delete"
        assert Permission.ADMIN.value == "admin"


class TestRoleEnum:
    """Tests for the Role enum."""

    def test_all_roles_exist(self):
        """Three roles are defined."""
        vals = {r.value for r in Role}
        assert vals == {"viewer", "operator", "admin"}

    def test_role_values(self):
        """Enum values match expected strings."""
        assert Role.VIEWER.value == "viewer"
        assert Role.OPERATOR.value == "operator"
        assert Role.ADMIN.value == "admin"


class TestGrantDataclass:
    """Tests for the Grant dataclass."""

    def test_create_minimal(self):
        """Grant stores principal and role."""
        g = Grant(principal="alice", role=Role.VIEWER)
        assert g.principal == "alice"
        assert g.role == Role.VIEWER
        assert g.resource == ""
        assert g.granted_by == ""

    def test_create_full(self):
        """Grant stores all optional fields."""
        g = Grant(
            principal="bob",
            role=Role.OPERATOR,
            resource="db/users",
            granted_by="admin",
        )
        assert g.resource == "db/users"
        assert g.granted_by == "admin"


class TestPermissionModelViewer:
    """Tests for VIEWER role behaviour in PermissionModel."""

    def test_viewer_can_read(self):
        """VIEWER has READ permission."""
        model = PermissionModel()
        model.grant("alice", Role.VIEWER)
        assert model.check("alice", Permission.READ) is True

    def test_viewer_cannot_write(self):
        """VIEWER does not have WRITE permission."""
        model = PermissionModel()
        model.grant("alice", Role.VIEWER)
        assert model.check("alice", Permission.WRITE) is False

    def test_viewer_cannot_delete(self):
        """VIEWER does not have DELETE permission."""
        model = PermissionModel()
        model.grant("alice", Role.VIEWER)
        assert model.check("alice", Permission.DELETE) is False

    def test_viewer_cannot_admin(self):
        """VIEWER does not have ADMIN permission."""
        model = PermissionModel()
        model.grant("alice", Role.VIEWER)
        assert model.check("alice", Permission.ADMIN) is False


class TestPermissionModelOperator:
    """Tests for OPERATOR role behaviour in PermissionModel."""

    def test_operator_can_read(self):
        """OPERATOR has READ permission."""
        model = PermissionModel()
        model.grant("bob", Role.OPERATOR)
        assert model.check("bob", Permission.READ) is True

    def test_operator_can_write(self):
        """OPERATOR has WRITE permission."""
        model = PermissionModel()
        model.grant("bob", Role.OPERATOR)
        assert model.check("bob", Permission.WRITE) is True

    def test_operator_can_execute(self):
        """OPERATOR has EXECUTE permission."""
        model = PermissionModel()
        model.grant("bob", Role.OPERATOR)
        assert model.check("bob", Permission.EXECUTE) is True

    def test_operator_cannot_delete(self):
        """OPERATOR does not have DELETE permission."""
        model = PermissionModel()
        model.grant("bob", Role.OPERATOR)
        assert model.check("bob", Permission.DELETE) is False

    def test_operator_cannot_admin(self):
        """OPERATOR does not have ADMIN permission."""
        model = PermissionModel()
        model.grant("bob", Role.OPERATOR)
        assert model.check("bob", Permission.ADMIN) is False


class TestPermissionModelAdmin:
    """Tests for ADMIN role behaviour in PermissionModel."""

    def test_admin_can_read(self):
        """ADMIN has READ permission."""
        model = PermissionModel()
        model.grant("root", Role.ADMIN)
        assert model.check("root", Permission.READ) is True

    def test_admin_can_write(self):
        """ADMIN has WRITE permission."""
        model = PermissionModel()
        model.grant("root", Role.ADMIN)
        assert model.check("root", Permission.WRITE) is True

    def test_admin_can_delete(self):
        """ADMIN has DELETE permission."""
        model = PermissionModel()
        model.grant("root", Role.ADMIN)
        assert model.check("root", Permission.DELETE) is True

    def test_admin_can_admin(self):
        """ADMIN has ADMIN permission."""
        model = PermissionModel()
        model.grant("root", Role.ADMIN)
        assert model.check("root", Permission.ADMIN) is True


class TestPermissionModelRevoke:
    """Tests for PermissionModel.revoke()."""

    def test_revoke_removes_grant(self):
        """revoke() removes the specified grant."""
        model = PermissionModel()
        model.grant("alice", Role.OPERATOR)
        assert model.check("alice", Permission.WRITE) is True
        result = model.revoke("alice", Role.OPERATOR)
        assert result is True
        assert model.check("alice", Permission.WRITE) is False

    def test_revoke_returns_false_when_not_found(self):
        """revoke() returns False when grant doesn't exist."""
        model = PermissionModel()
        model.grant("alice", Role.VIEWER)
        result = model.revoke("alice", Role.OPERATOR)  # wrong role
        assert result is False

    def test_revoke_unknown_principal_returns_false(self):
        """revoke() returns False for unknown principal."""
        model = PermissionModel()
        result = model.revoke("nobody", Role.VIEWER)
        assert result is False

    def test_revoke_scoped_resource(self):
        """revoke() removes resource-scoped grant."""
        model = PermissionModel()
        model.grant("alice", Role.OPERATOR, resource="db")
        assert model.check("alice", Permission.WRITE, resource="db") is True
        model.revoke("alice", Role.OPERATOR, resource="db")
        assert model.check("alice", Permission.WRITE, resource="db") is False


class TestPermissionModelResourceScoping:
    """Tests for resource-scoped permission checks."""

    def test_grant_scoped_to_resource(self):
        """Resource-scoped grant applies only to that resource."""
        model = PermissionModel()
        model.grant("alice", Role.OPERATOR, resource="db")
        # Check against correct resource
        assert model.check("alice", Permission.WRITE, resource="db") is True

    def test_scoped_grant_does_not_apply_to_other_resource(self):
        """Resource-scoped grant does not apply to a different resource."""
        model = PermissionModel()
        model.grant("alice", Role.OPERATOR, resource="db")
        assert model.check("alice", Permission.WRITE, resource="files") is False

    def test_global_grant_applies_to_any_resource(self):
        """Global (no resource) grant applies when resource is specified."""
        model = PermissionModel()
        model.grant("alice", Role.ADMIN)  # global
        assert model.check("alice", Permission.WRITE, resource="anything") is True


class TestPermissionModelEffectivePermissions:
    """Tests for PermissionModel.effective_permissions()."""

    def test_viewer_effective_permissions(self):
        """VIEWER effective permissions contain only READ."""
        model = PermissionModel()
        model.grant("alice", Role.VIEWER)
        perms = model.effective_permissions("alice")
        assert Permission.READ in perms
        assert Permission.WRITE not in perms
        assert Permission.ADMIN not in perms

    def test_admin_effective_permissions(self):
        """ADMIN effective permissions contain all five permissions."""
        model = PermissionModel()
        model.grant("root", Role.ADMIN)
        perms = model.effective_permissions("root")
        assert len(perms) == 5

    def test_unknown_principal_empty_permissions(self):
        """Unknown principal has empty effective permissions."""
        model = PermissionModel()
        perms = model.effective_permissions("ghost")
        assert perms == set()

    def test_multiple_roles_merged(self):
        """Two grants combine their permissions."""
        model = PermissionModel()
        model.grant("alice", Role.VIEWER)
        model.grant("alice", Role.OPERATOR)
        perms = model.effective_permissions("alice")
        # Should have at least read + write + execute
        assert Permission.READ in perms
        assert Permission.WRITE in perms
        assert Permission.EXECUTE in perms


class TestPermissionModelListGrants:
    """Tests for PermissionModel.list_grants()."""

    def test_list_grants_for_principal(self):
        """list_grants() with principal returns that principal's grants."""
        model = PermissionModel()
        model.grant("alice", Role.VIEWER)
        model.grant("bob", Role.ADMIN)
        grants = model.list_grants(principal="alice")
        assert len(grants) == 1
        assert grants[0].principal == "alice"

    def test_list_all_grants(self):
        """list_grants() with no args returns all grants."""
        model = PermissionModel()
        model.grant("alice", Role.VIEWER)
        model.grant("bob", Role.ADMIN)
        all_grants = model.list_grants()
        assert len(all_grants) == 2

    def test_principal_count_property(self):
        """principal_count reflects number of distinct principals."""
        model = PermissionModel()
        assert model.principal_count == 0
        model.grant("alice", Role.VIEWER)
        assert model.principal_count == 1
        model.grant("bob", Role.ADMIN)
        assert model.principal_count == 2


class TestPermissionModelMatrix:
    """Tests for PermissionModel.permission_matrix()."""

    def test_matrix_structure(self):
        """permission_matrix() returns dict of principal -> perm -> bool."""
        model = PermissionModel()
        model.grant("alice", Role.VIEWER)
        matrix = model.permission_matrix()
        assert "alice" in matrix
        assert isinstance(matrix["alice"], dict)
        assert set(matrix["alice"].keys()) == {"read", "write", "execute", "delete", "admin"}

    def test_matrix_viewer_row(self):
        """VIEWER row has only read=True."""
        model = PermissionModel()
        model.grant("viewer", Role.VIEWER)
        matrix = model.permission_matrix()
        row = matrix["viewer"]
        assert row["read"] is True
        assert row["write"] is False
        assert row["delete"] is False
        assert row["admin"] is False

    def test_matrix_admin_row(self):
        """ADMIN row has all permissions True."""
        model = PermissionModel()
        model.grant("admin", Role.ADMIN)
        matrix = model.permission_matrix()
        row = matrix["admin"]
        assert all(v is True for v in row.values())

    def test_matrix_empty_model(self):
        """Empty model produces empty matrix."""
        model = PermissionModel()
        assert model.permission_matrix() == {}

    def test_no_grant_principal_not_in_check(self):
        """Principal with no grants fails permission check."""
        model = PermissionModel()
        assert model.check("unknown", Permission.READ) is False
