"""
Unit tests for InfomaniakVolumeClient (block storage / Cinder).

Tests cover:
- Volume CRUD operations (list, get, create, delete, extend)
- Volume attach/detach (including not-attached edge case)
- Backup operations (list, create, restore, delete)
- Snapshot operations (list, create, delete)
- _volume_to_dict helper (including edge cases)
- Error handling for every method (returns default on exception)

Total: 23 tests in one TestInfomaniakBlockStorage class.
"""

import pytest

# Import the shared factory from conftest (available as module-level function)
from _stubs import Stub, make_stub_volume

from codomyrmex.cloud.infomaniak.block_storage.client import InfomaniakVolumeClient


class TestInfomaniakBlockStorage:
    """Comprehensive tests for InfomaniakVolumeClient."""

    @pytest.fixture
    def stub_openstack_connection(self):
        """Create a fully-stubbed OpenStack connection."""
        conn = Stub()
        conn.current_user_id = "user-test-123"
        conn.current_project_id = "proj-test-456"
        return conn

    # =================================================================
    # Volume Operations - Happy Path
    # =================================================================

    def test_list_volumes_returns_volume_dicts(self, stub_openstack_connection):
        """list_volumes converts OpenStack volume objects to dicts."""
        vol = make_stub_volume(volume_id="vol-aaa", name="data-disk", size=200)
        stub_openstack_connection.block_storage.volumes.return_value = [vol]

        client = InfomaniakVolumeClient(stub_openstack_connection)
        result = client.list_volumes()

        assert len(result) == 1
        assert result[0]["id"] == "vol-aaa"
        assert result[0]["name"] == "data-disk"
        assert result[0]["size"] == 200
        assert result[0]["status"] == "available"
        assert result[0]["volume_type"] == "ssd"
        assert result[0]["availability_zone"] == "dc3-a"
        assert result[0]["bootable"] is False
        assert result[0]["encrypted"] is False
        assert result[0]["attachments"] == []
        assert result[0]["created_at"] is None

    def test_get_volume_returns_dict(self, stub_openstack_connection):
        """get_volume returns a dict for a valid volume ID."""
        vol = make_stub_volume(volume_id="vol-bbb", name="boot-vol", status="in-use")
        stub_openstack_connection.block_storage.get_volume.return_value = vol

        client = InfomaniakVolumeClient(stub_openstack_connection)
        result = client.get_volume("vol-bbb")

        assert result is not None
        assert result["id"] == "vol-bbb"
        assert result["status"] == "in-use"
        stub_openstack_connection.block_storage.get_volume.assert_called_once_with(
            "vol-bbb"
        )

    def test_get_volume_returns_none_when_not_found(self, stub_openstack_connection):
        """get_volume returns None when the OpenStack SDK returns None."""
        stub_openstack_connection.block_storage.get_volume.return_value = None

        client = InfomaniakVolumeClient(stub_openstack_connection)
        result = client.get_volume("vol-nonexistent")

        assert result is None

    def test_create_volume_success(self, stub_openstack_connection):
        """create_volume returns a dict on success with all parameters forwarded."""
        vol = make_stub_volume(
            volume_id="vol-new", name="fresh-vol", status="creating", size=50
        )
        stub_openstack_connection.block_storage.create_volume.return_value = vol

        client = InfomaniakVolumeClient(stub_openstack_connection)
        result = client.create_volume(
            size=50,
            name="fresh-vol",
            description="test desc",
            volume_type="ssd",
            availability_zone="dc3-a",
            snapshot_id="snap-src",
            image_id="img-src",
        )

        assert result is not None
        assert result["id"] == "vol-new"
        assert result["size"] == 50
        stub_openstack_connection.block_storage.create_volume.assert_called_once_with(
            size=50,
            name="fresh-vol",
            description="test desc",
            volume_type="ssd",
            availability_zone="dc3-a",
            snapshot_id="snap-src",
            image_id="img-src",
        )

    def test_delete_volume_success(self, stub_openstack_connection):
        """delete_volume returns True and passes force flag through."""
        client = InfomaniakVolumeClient(stub_openstack_connection)
        result = client.delete_volume("vol-del", force=True)

        assert result is True
        stub_openstack_connection.block_storage.delete_volume.assert_called_once_with(
            "vol-del", force=True
        )

    def test_extend_volume_success(self, stub_openstack_connection):
        """extend_volume returns True and passes new_size correctly."""
        client = InfomaniakVolumeClient(stub_openstack_connection)
        result = client.extend_volume("vol-grow", 500)

        assert result is True
        stub_openstack_connection.block_storage.extend_volume.assert_called_once_with(
            "vol-grow", 500
        )

    def test_attach_volume_success(self, stub_openstack_connection):
        """attach_volume calls compute.create_volume_attachment with correct params."""
        client = InfomaniakVolumeClient(stub_openstack_connection)
        result = client.attach_volume("vol-att", "srv-111", device="/dev/vdb")

        assert result is True
        stub_openstack_connection.compute.create_volume_attachment.assert_called_once_with(
            server="srv-111",
            volume_id="vol-att",
            device="/dev/vdb",
        )

    def test_detach_volume_success(self, stub_openstack_connection):
        """detach_volume finds the matching attachment and deletes it."""
        stub_attach = Stub()
        stub_attach.id = "att-99"
        stub_attach.volume_id = "vol-det"
        stub_openstack_connection.compute.volume_attachments.return_value = [
            stub_attach
        ]

        client = InfomaniakVolumeClient(stub_openstack_connection)
        result = client.detach_volume("vol-det", "srv-222")

        assert result is True
        stub_openstack_connection.compute.delete_volume_attachment.assert_called_once_with(
            "att-99", server="srv-222"
        )

    def test_detach_volume_not_attached_returns_false(self, stub_openstack_connection):
        """detach_volume returns False with a warning when volume is not attached."""
        other_attach = Stub()
        other_attach.id = "att-other"
        other_attach.volume_id = "vol-OTHER"
        stub_openstack_connection.compute.volume_attachments.return_value = [
            other_attach
        ]

        client = InfomaniakVolumeClient(stub_openstack_connection)
        result = client.detach_volume("vol-missing", "srv-333")

        assert result is False
        stub_openstack_connection.compute.delete_volume_attachment.assert_not_called()

    # =================================================================
    # Backup Operations - Happy Path
    # =================================================================

    def test_list_backups_returns_backup_dicts(self, stub_openstack_connection):
        """list_backups converts backup objects to dicts."""
        stub_backup = Stub()
        stub_backup.id = "bkp-001"
        stub_backup.name = "nightly"
        stub_backup.status = "available"
        stub_backup.volume_id = "vol-src"
        stub_backup.size = 80
        stub_backup.created_at = "2026-01-15T00:00:00"
        stub_openstack_connection.block_storage.backups.return_value = [stub_backup]

        client = InfomaniakVolumeClient(stub_openstack_connection)
        result = client.list_backups()

        assert len(result) == 1
        assert result[0]["id"] == "bkp-001"
        assert result[0]["name"] == "nightly"
        assert result[0]["volume_id"] == "vol-src"
        assert result[0]["size"] == 80
        assert result[0]["created_at"] == "2026-01-15T00:00:00"

    def test_create_backup_success(self, stub_openstack_connection):
        """create_backup returns a dict with backup metadata."""
        stub_backup = Stub()
        stub_backup.id = "bkp-new"
        stub_backup.name = "manual-bkp"
        stub_backup.status = "creating"
        stub_backup.volume_id = "vol-src"
        stub_openstack_connection.block_storage.create_backup.return_value = stub_backup

        client = InfomaniakVolumeClient(stub_openstack_connection)
        result = client.create_backup(
            volume_id="vol-src",
            name="manual-bkp",
            description="before upgrade",
            incremental=True,
            force=True,
        )

        assert result is not None
        assert result["id"] == "bkp-new"
        assert result["name"] == "manual-bkp"
        assert result["volume_id"] == "vol-src"
        stub_openstack_connection.block_storage.create_backup.assert_called_once_with(
            volume_id="vol-src",
            name="manual-bkp",
            description="before upgrade",
            is_incremental=True,
            force=True,
        )

    def test_restore_backup_success(self, stub_openstack_connection):
        """restore_backup returns a dict with the restored volume_id."""
        stub_result = Stub()
        stub_result.volume_id = "vol-restored"
        stub_openstack_connection.block_storage.restore_backup.return_value = (
            stub_result
        )

        client = InfomaniakVolumeClient(stub_openstack_connection)
        result = client.restore_backup(
            "bkp-001", volume_id="vol-target", name="restored-vol"
        )

        assert result is not None
        assert result["volume_id"] == "vol-restored"
        stub_openstack_connection.block_storage.restore_backup.assert_called_once_with(
            "bkp-001", volume_id="vol-target", name="restored-vol"
        )

    def test_delete_backup_success(self, stub_openstack_connection):
        """delete_backup returns True and passes force flag."""
        client = InfomaniakVolumeClient(stub_openstack_connection)
        result = client.delete_backup("bkp-del", force=True)

        assert result is True
        stub_openstack_connection.block_storage.delete_backup.assert_called_once_with(
            "bkp-del", force=True
        )

    # =================================================================
    # Snapshot Operations - Happy Path
    # =================================================================

    def test_list_snapshots_returns_snapshot_dicts(self, stub_openstack_connection):
        """list_snapshots converts snapshot objects to dicts."""
        stub_snap = Stub()
        stub_snap.id = "snap-001"
        stub_snap.name = "pre-deploy"
        stub_snap.status = "available"
        stub_snap.volume_id = "vol-src"
        stub_snap.size = 100
        stub_snap.created_at = None
        stub_openstack_connection.block_storage.snapshots.return_value = [stub_snap]

        client = InfomaniakVolumeClient(stub_openstack_connection)
        result = client.list_snapshots()

        assert len(result) == 1
        assert result[0]["id"] == "snap-001"
        assert result[0]["name"] == "pre-deploy"
        assert result[0]["volume_id"] == "vol-src"
        assert result[0]["created_at"] is None

    def test_create_snapshot_success(self, stub_openstack_connection):
        """create_snapshot returns a dict with snapshot metadata."""
        stub_snap = Stub()
        stub_snap.id = "snap-new"
        stub_snap.name = "quick-snap"
        stub_snap.status = "creating"
        stub_snap.volume_id = "vol-src"
        stub_openstack_connection.block_storage.create_snapshot.return_value = stub_snap

        client = InfomaniakVolumeClient(stub_openstack_connection)
        result = client.create_snapshot(
            volume_id="vol-src",
            name="quick-snap",
            description="before resize",
            force=True,
        )

        assert result is not None
        assert result["id"] == "snap-new"
        assert result["name"] == "quick-snap"
        stub_openstack_connection.block_storage.create_snapshot.assert_called_once_with(
            volume_id="vol-src",
            name="quick-snap",
            description="before resize",
            force=True,
        )

    def test_delete_snapshot_success(self, stub_openstack_connection):
        """delete_snapshot returns True and passes force flag."""
        client = InfomaniakVolumeClient(stub_openstack_connection)
        result = client.delete_snapshot("snap-del", force=True)

        assert result is True
        stub_openstack_connection.block_storage.delete_snapshot.assert_called_once_with(
            "snap-del", force=True
        )

    # =================================================================
    # _volume_to_dict Edge Cases
    # =================================================================

    def test_volume_to_dict_with_created_at(self, stub_openstack_connection):
        """_volume_to_dict converts created_at to string when present."""
        vol = make_stub_volume(volume_id="vol-ts")
        vol.created_at = "2026-02-01T12:30:00Z"

        client = InfomaniakVolumeClient(stub_openstack_connection)
        result = client._volume_to_dict(vol)

        assert result["created_at"] == "2026-02-01T12:30:00Z"

    def test_volume_to_dict_with_none_created_at(self, stub_openstack_connection):
        """_volume_to_dict returns None for created_at when not set."""
        vol = make_stub_volume(volume_id="vol-no-ts")
        vol.created_at = None

        client = InfomaniakVolumeClient(stub_openstack_connection)
        result = client._volume_to_dict(vol)

        assert result["created_at"] is None

    def test_volume_to_dict_with_attachments(self, stub_openstack_connection):
        """_volume_to_dict preserves non-empty attachments list."""
        vol = make_stub_volume(volume_id="vol-attached")
        vol.attachments = [
            {"server_id": "srv-1", "device": "/dev/vdb"},
            {"server_id": "srv-2", "device": "/dev/vdc"},
        ]

        client = InfomaniakVolumeClient(stub_openstack_connection)
        result = client._volume_to_dict(vol)

        assert len(result["attachments"]) == 2
        assert result["attachments"][0]["server_id"] == "srv-1"

    def test_volume_to_dict_with_none_attachments(self, stub_openstack_connection):
        """_volume_to_dict returns empty list when attachments is None."""
        vol = make_stub_volume(volume_id="vol-none-att")
        vol.attachments = None

        client = InfomaniakVolumeClient(stub_openstack_connection)
        result = client._volume_to_dict(vol)

        assert result["attachments"] == []

    # =================================================================
    # Error Handling - Every Method
    # =================================================================

    def test_list_volumes_error_returns_empty_list(self, stub_openstack_connection):
        """list_volumes returns [] when the SDK raises an exception."""
        stub_openstack_connection.block_storage.volumes.side_effect = Exception(
            "conn refused"
        )

        client = InfomaniakVolumeClient(stub_openstack_connection)
        assert client.list_volumes() == []

    def test_get_volume_error_returns_none(self, stub_openstack_connection):
        """get_volume returns None when the SDK raises an exception."""
        stub_openstack_connection.block_storage.get_volume.side_effect = Exception(
            "not found"
        )

        client = InfomaniakVolumeClient(stub_openstack_connection)
        assert client.get_volume("vol-err") is None

    def test_create_volume_error_returns_none(self, stub_openstack_connection):
        """create_volume returns None when the SDK raises an exception."""
        stub_openstack_connection.block_storage.create_volume.side_effect = Exception(
            "quota"
        )

        client = InfomaniakVolumeClient(stub_openstack_connection)
        assert client.create_volume(size=100, name="fail-vol") is None

    def test_delete_volume_error_returns_false(self, stub_openstack_connection):
        """delete_volume returns False when the SDK raises an exception."""
        stub_openstack_connection.block_storage.delete_volume.side_effect = Exception(
            "locked"
        )

        client = InfomaniakVolumeClient(stub_openstack_connection)
        assert client.delete_volume("vol-locked") is False

    def test_extend_volume_error_returns_false(self, stub_openstack_connection):
        """extend_volume returns False when the SDK raises an exception."""
        stub_openstack_connection.block_storage.extend_volume.side_effect = Exception(
            "too small"
        )

        client = InfomaniakVolumeClient(stub_openstack_connection)
        assert client.extend_volume("vol-fail", 10) is False

    def test_attach_volume_error_returns_false(self, stub_openstack_connection):
        """attach_volume returns False when the SDK raises an exception."""
        stub_openstack_connection.compute.create_volume_attachment.side_effect = (
            Exception("busy")
        )

        client = InfomaniakVolumeClient(stub_openstack_connection)
        assert client.attach_volume("vol-err", "srv-err") is False

    def test_detach_volume_error_returns_false(self, stub_openstack_connection):
        """detach_volume returns False when volume_attachments raises an exception."""
        stub_openstack_connection.compute.volume_attachments.side_effect = Exception(
            "timeout"
        )

        client = InfomaniakVolumeClient(stub_openstack_connection)
        assert client.detach_volume("vol-err", "srv-err") is False

    def test_list_backups_error_returns_empty_list(self, stub_openstack_connection):
        """list_backups returns [] when the SDK raises an exception."""
        stub_openstack_connection.block_storage.backups.side_effect = Exception("503")

        client = InfomaniakVolumeClient(stub_openstack_connection)
        assert client.list_backups() == []

    def test_create_backup_error_returns_none(self, stub_openstack_connection):
        """create_backup returns None when the SDK raises an exception."""
        stub_openstack_connection.block_storage.create_backup.side_effect = Exception(
            "no space"
        )

        client = InfomaniakVolumeClient(stub_openstack_connection)
        assert client.create_backup("vol-err", "fail-bkp") is None

    def test_restore_backup_error_returns_none(self, stub_openstack_connection):
        """restore_backup returns None when the SDK raises an exception."""
        stub_openstack_connection.block_storage.restore_backup.side_effect = Exception(
            "corrupt"
        )

        client = InfomaniakVolumeClient(stub_openstack_connection)
        assert client.restore_backup("bkp-bad") is None

    def test_delete_backup_error_returns_false(self, stub_openstack_connection):
        """delete_backup returns False when the SDK raises an exception."""
        stub_openstack_connection.block_storage.delete_backup.side_effect = Exception(
            "locked"
        )

        client = InfomaniakVolumeClient(stub_openstack_connection)
        assert client.delete_backup("bkp-locked") is False

    def test_list_snapshots_error_returns_empty_list(self, stub_openstack_connection):
        """list_snapshots returns [] when the SDK raises an exception."""
        stub_openstack_connection.block_storage.snapshots.side_effect = Exception(
            "denied"
        )

        client = InfomaniakVolumeClient(stub_openstack_connection)
        assert client.list_snapshots() == []

    def test_create_snapshot_error_returns_none(self, stub_openstack_connection):
        """create_snapshot returns None when the SDK raises an exception."""
        stub_openstack_connection.block_storage.create_snapshot.side_effect = Exception(
            "quota"
        )

        client = InfomaniakVolumeClient(stub_openstack_connection)
        assert client.create_snapshot("vol-err", "fail-snap") is None

    def test_delete_snapshot_error_returns_false(self, stub_openstack_connection):
        """delete_snapshot returns False when the SDK raises an exception."""
        stub_openstack_connection.block_storage.delete_snapshot.side_effect = Exception(
            "busy"
        )

        client = InfomaniakVolumeClient(stub_openstack_connection)
        assert client.delete_snapshot("snap-busy") is False


# =========================================================================


class TestInfomaniakVolumeClientExpanded:
    """Tests for InfomaniakVolumeClient untested methods."""

    def _make_client(self):
        from codomyrmex.cloud.infomaniak.block_storage import InfomaniakVolumeClient

        stub_conn = Stub()
        return InfomaniakVolumeClient(connection=stub_conn), stub_conn

    def test_get_volume(self):
        """get_volume returns dict via _volume_to_dict."""
        client, mc = self._make_client()
        vol = Stub(
            id="v1",
            name="data",
            status="available",
            size=50,
            volume_type="SSD",
            availability_zone="dc3-a",
            is_bootable=False,
            is_encrypted=False,
            attachments=[],
            created_at=None,
        )
        mc.block_storage.get_volume.return_value = vol
        result = client.get_volume("v1")
        assert result["id"] == "v1"
        assert result["size"] == 50

    def test_create_backup(self):
        """create_backup returns dict with backup details."""
        client, mc = self._make_client()
        bk = Stub(id="bk1", name="mybk", status="creating", volume_id="v1")
        mc.block_storage.create_backup.return_value = bk
        result = client.create_backup("v1", "mybk")
        assert result["id"] == "bk1"
        assert result["volume_id"] == "v1"

    def test_restore_backup(self):
        """restore_backup returns dict with volume_id."""
        client, mc = self._make_client()
        res = Stub(volume_id="v-new")
        mc.block_storage.restore_backup.return_value = res
        result = client.restore_backup("bk1")
        assert result["volume_id"] == "v-new"

    def test_delete_backup(self):
        """delete_backup returns True on success."""
        client, mc = self._make_client()
        assert client.delete_backup("bk1") is True
        mc.block_storage.delete_backup.assert_called_once_with("bk1", force=False)

    def test_create_snapshot(self):
        """create_snapshot returns dict with snapshot details."""
        client, mc = self._make_client()
        snap = Stub(id="sn1", name="mysnap", status="creating", volume_id="v1")
        mc.block_storage.create_snapshot.return_value = snap
        result = client.create_snapshot("v1", "mysnap")
        assert result["id"] == "sn1"

    def test_delete_snapshot(self):
        """delete_snapshot returns True on success."""
        client, mc = self._make_client()
        assert client.delete_snapshot("sn1") is True
        mc.block_storage.delete_snapshot.assert_called_once_with("sn1", force=False)

    def test_list_volumes_error(self):
        """list_volumes returns [] on error."""
        client, mc = self._make_client()
        mc.block_storage.volumes.side_effect = Exception("fail")
        assert client.list_volumes() == []


# =========================================================================
# ADDITIONAL NETWORK CLIENT TESTS
# =========================================================================
