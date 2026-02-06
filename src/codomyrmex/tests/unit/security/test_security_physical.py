"""
Unit tests for the security.physical module.

Tests physical security operations including access control, asset inventory,
surveillance, physical vulnerability assessment, and perimeter management.
"""

from datetime import datetime, timedelta

import pytest

from codomyrmex.security.physical import (
    AccessControlSystem,
    AssetInventory,
    PerimeterManager,
    PhysicalVulnerabilityScanner,
    SurveillanceMonitor,
    assess_physical_security,
    check_access_permission,
    check_perimeter_security,
    get_asset_status,
    grant_access,
    log_physical_event,
    manage_access_points,
    monitor_physical_access,
    register_asset,
    revoke_access,
    scan_physical_vulnerabilities,
    track_asset,
)


@pytest.mark.unit
class TestAccessControl:
    """Test access control functionality."""

    def test_access_control_system_initialization(self):
        """Test AccessControlSystem can be initialized."""
        acs = AccessControlSystem()
        assert acs is not None
        assert acs.permissions == {}

    def test_grant_access(self):
        """Test granting access permission."""
        permission = grant_access(
            user_id="user123",
            resource="server_room",
            permission_type="read"
        )
        assert permission.user_id == "user123"
        assert permission.resource == "server_room"
        assert permission.permission_type == "read"
        assert permission.granted_at is not None

    def test_grant_access_with_expiration(self):
        """Test granting access with expiration."""
        expires_at = datetime.now() + timedelta(days=30)
        permission = grant_access(
            user_id="user123",
            resource="server_room",
            permission_type="read",
            expires_at=expires_at
        )
        assert permission.expires_at == expires_at

    def test_check_access_permission(self):
        """Test checking access permission."""
        # Grant access first
        grant_access("user123", "server_room", "read")

        # Check access
        has_access = check_access_permission("user123", "server_room", "read")
        assert has_access is True

        # Check non-existent access
        has_access = check_access_permission("user456", "server_room", "read")
        assert has_access is False

    def test_revoke_access(self):
        """Test revoking access permission."""
        # Grant access
        grant_access("user123", "server_room", "read")

        # Verify access
        assert check_access_permission("user123", "server_room", "read") is True

        # Revoke access
        revoked = revoke_access("user123", "server_room")
        assert revoked is True

        # Verify access revoked
        assert check_access_permission("user123", "server_room", "read") is False

    def test_access_expiration(self):
        """Test that expired access is denied."""
        # Grant access with past expiration
        past_time = datetime.now() - timedelta(days=1)
        grant_access("user123", "server_room", "read", expires_at=past_time)

        # Should not have access
        has_access = check_access_permission("user123", "server_room", "read")
        assert has_access is False


@pytest.mark.unit
class TestAssetInventory:
    """Test asset inventory functionality."""

    def test_asset_inventory_initialization(self):
        """Test AssetInventory can be initialized."""
        inventory = AssetInventory()
        assert inventory is not None
        assert inventory.assets == {}

    def test_register_asset(self):
        """Test registering a physical asset."""
        asset = register_asset(
            asset_id="server-001",
            name="Production Server",
            asset_type="server",
            location="Data Center A"
        )
        assert asset.asset_id == "server-001"
        assert asset.name == "Production Server"
        assert asset.asset_type == "server"
        assert asset.location == "Data Center A"
        assert asset.status == "active"
        assert asset.registered_at is not None

    def test_track_asset(self):
        """Test tracking asset movement."""
        # Register asset
        register_asset("server-001", "Server", "server", "Location A")

        # Track movement
        tracked = track_asset("server-001", location="Location B")
        assert tracked is True

        # Verify location updated
        asset = get_asset_status("server-001")
        assert asset.location == "Location B"
        assert asset.last_checked is not None

    def test_get_asset_status(self):
        """Test getting asset status."""
        # Register asset
        register_asset("server-001", "Server", "server", "Location A")

        # Get status
        asset = get_asset_status("server-001")
        assert asset is not None
        assert asset.asset_id == "server-001"

        # Get non-existent asset
        asset = get_asset_status("nonexistent")
        assert asset is None


@pytest.mark.unit
class TestSurveillance:
    """Test surveillance functionality."""

    def test_surveillance_monitor_initialization(self):
        """Test SurveillanceMonitor can be initialized."""
        monitor = SurveillanceMonitor()
        assert monitor is not None
        assert monitor.events == []

    def test_monitor_physical_access(self):
        """Test monitoring physical access."""
        event = monitor_physical_access("server_room", "user123")
        assert event is not None
        assert event.event_type == "access"
        assert event.location == "server_room"
        assert "user123" in event.description
        assert event.severity == "low"

    def test_log_physical_event(self):
        """Test logging physical security event."""
        event = log_physical_event(
            event_type="alarm",
            location="main_entrance",
            description="Motion detected",
            severity="high"
        )
        assert event is not None
        assert event.event_type == "alarm"
        assert event.location == "main_entrance"
        assert event.description == "Motion detected"
        assert event.severity == "high"
        assert event.timestamp is not None


@pytest.mark.unit
class TestPhysicalVulnerability:
    """Test physical vulnerability assessment."""

    def test_physical_vulnerability_scanner_initialization(self):
        """Test PhysicalVulnerabilityScanner can be initialized."""
        scanner = PhysicalVulnerabilityScanner()
        assert scanner is not None

    def test_scan_physical_vulnerabilities(self):
        """Test scanning for physical vulnerabilities."""
        vulnerabilities = scan_physical_vulnerabilities("data_center")
        assert isinstance(vulnerabilities, list)

    def test_assess_physical_security(self):
        """Test assessing physical security."""
        assessment = assess_physical_security("data_center")
        assert isinstance(assessment, dict)
        assert "location" in assessment
        assert "total_vulnerabilities" in assessment
        assert assessment["location"] == "data_center"


@pytest.mark.unit
class TestPerimeterManagement:
    """Test perimeter management functionality."""

    def test_perimeter_manager_initialization(self):
        """Test PerimeterManager can be initialized."""
        manager = PerimeterManager()
        assert manager is not None
        assert manager.access_points == {}

    def test_check_perimeter_security(self):
        """Test checking perimeter security status."""
        status = check_perimeter_security()
        assert isinstance(status, dict)
        assert "total_access_points" in status
        assert "active_points" in status
        assert status["total_access_points"] >= 0
        assert status["active_points"] >= 0

    def test_manage_access_points(self):
        """Test managing access points."""
        points = manage_access_points()
        assert isinstance(points, list)


