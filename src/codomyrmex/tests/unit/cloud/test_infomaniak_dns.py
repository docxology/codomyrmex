"""
Unit tests for InfomaniakDNSClient (Designate).

Tests cover:
- Zone CRUD operations (list, get, create, update, delete)
- Record set CRUD operations (list, get, create, update, delete)
- Reverse DNS / PTR record operations (list, set, get, delete)
- Dot-appending normalization for zone names, record names, and hostnames
- Error handling (exceptions return safe defaults: None, False, or [])
- Edge cases: FIP not found for PTR ops, names already ending in dot

Total: 24 tests in a single TestInfomaniakDNS class.
"""

from unittest.mock import MagicMock

from codomyrmex.tests.unit.cloud.conftest import make_mock_zone


class TestInfomaniakDNS:
    """Comprehensive tests for InfomaniakDNSClient."""

    # =====================================================================
    # Zone Operations
    # =====================================================================

    def test_list_zones_success(self, mock_openstack_connection):
        """list_zones returns formatted dicts for each zone."""
        from codomyrmex.cloud.infomaniak.dns.client import InfomaniakDNSClient

        zone = make_mock_zone(zone_id="z-1", name="example.com.", email="admin@example.com")
        mock_openstack_connection.dns.zones.return_value = [zone]

        client = InfomaniakDNSClient(mock_openstack_connection)
        result = client.list_zones()

        assert len(result) == 1
        assert result[0]["id"] == "z-1"
        assert result[0]["name"] == "example.com."
        assert result[0]["email"] == "admin@example.com"
        assert result[0]["status"] == "ACTIVE"
        assert result[0]["type"] == "PRIMARY"
        assert result[0]["ttl"] == 3600

    def test_list_zones_error_returns_empty(self, mock_openstack_connection):
        """list_zones returns [] when the SDK raises an exception."""
        from codomyrmex.cloud.infomaniak.dns.client import InfomaniakDNSClient

        mock_openstack_connection.dns.zones.side_effect = Exception("Connection lost")

        client = InfomaniakDNSClient(mock_openstack_connection)
        result = client.list_zones()

        assert result == []

    def test_get_zone_success(self, mock_openstack_connection):
        """get_zone returns formatted dict when zone is found."""
        from codomyrmex.cloud.infomaniak.dns.client import InfomaniakDNSClient

        zone = make_mock_zone(zone_id="z-abc", name="found.com.", email="ops@found.com")
        mock_openstack_connection.dns.find_zone.return_value = zone

        client = InfomaniakDNSClient(mock_openstack_connection)
        result = client.get_zone("z-abc")

        assert result is not None
        assert result["id"] == "z-abc"
        assert result["name"] == "found.com."
        assert result["ttl"] == 3600
        mock_openstack_connection.dns.find_zone.assert_called_once_with("z-abc")

    def test_get_zone_not_found(self, mock_openstack_connection):
        """get_zone returns None when find_zone returns None."""
        from codomyrmex.cloud.infomaniak.dns.client import InfomaniakDNSClient

        mock_openstack_connection.dns.find_zone.return_value = None

        client = InfomaniakDNSClient(mock_openstack_connection)
        result = client.get_zone("nonexistent")

        assert result is None

    def test_create_zone_appends_dot(self, mock_openstack_connection):
        """create_zone appends trailing dot to name without one."""
        from codomyrmex.cloud.infomaniak.dns.client import InfomaniakDNSClient

        mock_zone = MagicMock()
        mock_zone.id = "z-new"
        mock_zone.name = "newdomain.org."
        mock_openstack_connection.dns.create_zone.return_value = mock_zone

        client = InfomaniakDNSClient(mock_openstack_connection)
        result = client.create_zone(name="newdomain.org", email="admin@newdomain.org")

        assert result is not None
        assert result["id"] == "z-new"
        assert result["name"] == "newdomain.org."
        mock_openstack_connection.dns.create_zone.assert_called_once_with(
            name="newdomain.org.",
            email="admin@newdomain.org",
            ttl=3600,
            description=None,
        )

    def test_create_zone_name_already_has_dot(self, mock_openstack_connection):
        """create_zone does not double-append dot when name already ends with one."""
        from codomyrmex.cloud.infomaniak.dns.client import InfomaniakDNSClient

        mock_zone = MagicMock()
        mock_zone.id = "z-dotted"
        mock_zone.name = "dotted.io."
        mock_openstack_connection.dns.create_zone.return_value = mock_zone

        client = InfomaniakDNSClient(mock_openstack_connection)
        client.create_zone(name="dotted.io.", email="admin@dotted.io", ttl=7200)

        mock_openstack_connection.dns.create_zone.assert_called_once_with(
            name="dotted.io.",
            email="admin@dotted.io",
            ttl=7200,
            description=None,
        )

    def test_create_zone_error_returns_none(self, mock_openstack_connection):
        """create_zone returns None when the SDK raises an exception."""
        from codomyrmex.cloud.infomaniak.dns.client import InfomaniakDNSClient

        mock_openstack_connection.dns.create_zone.side_effect = Exception("Conflict")

        client = InfomaniakDNSClient(mock_openstack_connection)
        result = client.create_zone(name="fail.com", email="a@b.com")

        assert result is None

    def test_delete_zone_success(self, mock_openstack_connection):
        """delete_zone returns True on success."""
        from codomyrmex.cloud.infomaniak.dns.client import InfomaniakDNSClient

        client = InfomaniakDNSClient(mock_openstack_connection)
        result = client.delete_zone("z-del")

        assert result is True
        mock_openstack_connection.dns.delete_zone.assert_called_once_with("z-del")

    def test_update_zone_success(self, mock_openstack_connection):
        """update_zone passes only provided kwargs and returns True."""
        from codomyrmex.cloud.infomaniak.dns.client import InfomaniakDNSClient

        client = InfomaniakDNSClient(mock_openstack_connection)
        result = client.update_zone("z-upd", email="new@example.com", ttl=7200)

        assert result is True
        mock_openstack_connection.dns.update_zone.assert_called_once_with(
            "z-upd", email="new@example.com", ttl=7200,
        )

    # =====================================================================
    # Record Set Operations
    # =====================================================================

    def test_list_records_success(self, mock_openstack_connection):
        """list_records returns formatted dicts for each record set."""
        from codomyrmex.cloud.infomaniak.dns.client import InfomaniakDNSClient

        mock_record = MagicMock()
        mock_record.id = "rec-1"
        mock_record.name = "www.example.com."
        mock_record.type = "A"
        mock_record.records = ["195.15.220.10"]
        mock_record.ttl = 300
        mock_record.status = "ACTIVE"

        mock_openstack_connection.dns.recordsets.return_value = [mock_record]

        client = InfomaniakDNSClient(mock_openstack_connection)
        result = client.list_records("z-1")

        assert len(result) == 1
        assert result[0]["id"] == "rec-1"
        assert result[0]["type"] == "A"
        assert "195.15.220.10" in result[0]["records"]

    def test_get_record_success(self, mock_openstack_connection):
        """get_record returns formatted dict when record is found."""
        from codomyrmex.cloud.infomaniak.dns.client import InfomaniakDNSClient

        mock_record = MagicMock()
        mock_record.id = "rec-abc"
        mock_record.name = "api.example.com."
        mock_record.type = "CNAME"
        mock_record.records = ["lb.example.com."]
        mock_record.ttl = 600

        mock_openstack_connection.dns.get_recordset.return_value = mock_record

        client = InfomaniakDNSClient(mock_openstack_connection)
        result = client.get_record("z-1", "rec-abc")

        assert result is not None
        assert result["id"] == "rec-abc"
        assert result["type"] == "CNAME"
        mock_openstack_connection.dns.get_recordset.assert_called_once_with("rec-abc", "z-1")

    def test_create_record_appends_dot(self, mock_openstack_connection):
        """create_record appends trailing dot to name without one."""
        from codomyrmex.cloud.infomaniak.dns.client import InfomaniakDNSClient

        mock_record = MagicMock()
        mock_record.id = "rec-new"
        mock_record.name = "mail.example.com."
        mock_openstack_connection.dns.create_recordset.return_value = mock_record

        client = InfomaniakDNSClient(mock_openstack_connection)
        result = client.create_record(
            zone_id="z-1",
            name="mail.example.com",
            record_type="MX",
            records=["10 mx1.example.com."],
            ttl=3600,
        )

        assert result is not None
        assert result["id"] == "rec-new"
        assert result["type"] == "MX"
        mock_openstack_connection.dns.create_recordset.assert_called_once_with(
            zone="z-1",
            name="mail.example.com.",
            type="MX",
            records=["10 mx1.example.com."],
            ttl=3600,
            description=None,
        )

    def test_create_record_name_already_has_dot(self, mock_openstack_connection):
        """create_record does not double-append dot when name already ends with one."""
        from codomyrmex.cloud.infomaniak.dns.client import InfomaniakDNSClient

        mock_record = MagicMock()
        mock_record.id = "rec-dotted"
        mock_record.name = "sub.example.com."
        mock_openstack_connection.dns.create_recordset.return_value = mock_record

        client = InfomaniakDNSClient(mock_openstack_connection)
        client.create_record(
            zone_id="z-1",
            name="sub.example.com.",
            record_type="A",
            records=["10.0.0.1"],
        )

        call_kwargs = mock_openstack_connection.dns.create_recordset.call_args
        assert call_kwargs.kwargs["name"] == "sub.example.com."

    def test_create_record_error_returns_none(self, mock_openstack_connection):
        """create_record returns None when the SDK raises an exception."""
        from codomyrmex.cloud.infomaniak.dns.client import InfomaniakDNSClient

        mock_openstack_connection.dns.create_recordset.side_effect = Exception("Conflict")

        client = InfomaniakDNSClient(mock_openstack_connection)
        result = client.create_record("z-1", "dup.example.com", "A", ["1.2.3.4"])

        assert result is None

    def test_update_record_success(self, mock_openstack_connection):
        """update_record passes only provided kwargs and returns True."""
        from codomyrmex.cloud.infomaniak.dns.client import InfomaniakDNSClient

        client = InfomaniakDNSClient(mock_openstack_connection)
        result = client.update_record(
            "z-1", "rec-1", records=["10.0.0.2"], ttl=600,
        )

        assert result is True
        mock_openstack_connection.dns.update_recordset.assert_called_once_with(
            "rec-1", "z-1", records=["10.0.0.2"], ttl=600,
        )

    def test_delete_record_success(self, mock_openstack_connection):
        """delete_record returns True on success."""
        from codomyrmex.cloud.infomaniak.dns.client import InfomaniakDNSClient

        client = InfomaniakDNSClient(mock_openstack_connection)
        result = client.delete_record("z-1", "rec-del")

        assert result is True
        mock_openstack_connection.dns.delete_recordset.assert_called_once_with("rec-del", "z-1")

    def test_delete_record_error_returns_false(self, mock_openstack_connection):
        """delete_record returns False when the SDK raises an exception."""
        from codomyrmex.cloud.infomaniak.dns.client import InfomaniakDNSClient

        mock_openstack_connection.dns.delete_recordset.side_effect = Exception("Not found")

        client = InfomaniakDNSClient(mock_openstack_connection)
        result = client.delete_record("z-1", "rec-missing")

        assert result is False

    # =====================================================================
    # Reverse DNS (PTR) Operations
    # =====================================================================

    def test_list_ptr_records_success(self, mock_openstack_connection):
        """list_ptr_records returns formatted dicts for each PTR."""
        from codomyrmex.cloud.infomaniak.dns.client import InfomaniakDNSClient

        mock_ptr = MagicMock()
        mock_ptr.id = "ptr-1"
        mock_ptr.ptrdname = "host.example.com."
        mock_ptr.address = "195.15.220.10"
        mock_ptr.status = "ACTIVE"

        mock_openstack_connection.dns.ptr_records.return_value = [mock_ptr]

        client = InfomaniakDNSClient(mock_openstack_connection)
        result = client.list_ptr_records()

        assert len(result) == 1
        assert result[0]["id"] == "ptr-1"
        assert result[0]["ptrdname"] == "host.example.com."
        assert result[0]["address"] == "195.15.220.10"

    def test_set_reverse_dns_success(self, mock_openstack_connection):
        """set_reverse_dns finds FIP, appends dot to hostname, creates PTR."""
        from codomyrmex.cloud.infomaniak.dns.client import InfomaniakDNSClient

        mock_fip = MagicMock()
        mock_fip.id = "fip-1"
        mock_openstack_connection.network.find_ip.return_value = mock_fip

        mock_ptr = MagicMock()
        mock_ptr.id = "ptr-new"
        mock_openstack_connection.dns.create_ptr_record.return_value = mock_ptr

        client = InfomaniakDNSClient(mock_openstack_connection)
        result = client.set_reverse_dns("195.15.220.10", "mail.example.com")

        assert result is not None
        assert result["id"] == "ptr-new"
        assert result["address"] == "195.15.220.10"
        assert result["ptrdname"] == "mail.example.com."
        mock_openstack_connection.network.find_ip.assert_called_once_with("195.15.220.10")
        mock_openstack_connection.dns.create_ptr_record.assert_called_once_with(
            floating_ip_id="fip-1",
            ptrdname="mail.example.com.",
            ttl=3600,
            description=None,
        )

    def test_set_reverse_dns_hostname_already_has_dot(self, mock_openstack_connection):
        """set_reverse_dns does not double-append dot when hostname already ends with one."""
        from codomyrmex.cloud.infomaniak.dns.client import InfomaniakDNSClient

        mock_fip = MagicMock()
        mock_fip.id = "fip-2"
        mock_openstack_connection.network.find_ip.return_value = mock_fip

        mock_ptr = MagicMock()
        mock_ptr.id = "ptr-dotted"
        mock_openstack_connection.dns.create_ptr_record.return_value = mock_ptr

        client = InfomaniakDNSClient(mock_openstack_connection)
        client.set_reverse_dns("10.0.0.1", "host.example.com.", ttl=7200)

        mock_openstack_connection.dns.create_ptr_record.assert_called_once_with(
            floating_ip_id="fip-2",
            ptrdname="host.example.com.",
            ttl=7200,
            description=None,
        )

    def test_set_reverse_dns_fip_not_found(self, mock_openstack_connection):
        """set_reverse_dns returns None when the floating IP is not found."""
        from codomyrmex.cloud.infomaniak.dns.client import InfomaniakDNSClient

        mock_openstack_connection.network.find_ip.return_value = None

        client = InfomaniakDNSClient(mock_openstack_connection)
        result = client.set_reverse_dns("192.168.0.1", "ghost.example.com")

        assert result is None
        mock_openstack_connection.dns.create_ptr_record.assert_not_called()

    def test_get_reverse_dns_success(self, mock_openstack_connection):
        """get_reverse_dns returns formatted PTR dict when found."""
        from codomyrmex.cloud.infomaniak.dns.client import InfomaniakDNSClient

        mock_fip = MagicMock()
        mock_fip.id = "fip-get"
        mock_openstack_connection.network.find_ip.return_value = mock_fip

        mock_ptr = MagicMock()
        mock_ptr.id = "ptr-found"
        mock_ptr.ptrdname = "web.example.com."
        mock_ptr.ttl = 3600
        mock_openstack_connection.dns.get_ptr_record.return_value = mock_ptr

        client = InfomaniakDNSClient(mock_openstack_connection)
        result = client.get_reverse_dns("195.15.220.20")

        assert result is not None
        assert result["id"] == "ptr-found"
        assert result["address"] == "195.15.220.20"
        assert result["ptrdname"] == "web.example.com."
        assert result["ttl"] == 3600

    def test_get_reverse_dns_fip_not_found(self, mock_openstack_connection):
        """get_reverse_dns returns None when the floating IP is not found."""
        from codomyrmex.cloud.infomaniak.dns.client import InfomaniakDNSClient

        mock_openstack_connection.network.find_ip.return_value = None

        client = InfomaniakDNSClient(mock_openstack_connection)
        result = client.get_reverse_dns("192.168.0.99")

        assert result is None

    def test_delete_reverse_dns_success(self, mock_openstack_connection):
        """delete_reverse_dns returns True on success."""
        from codomyrmex.cloud.infomaniak.dns.client import InfomaniakDNSClient

        mock_fip = MagicMock()
        mock_fip.id = "fip-del"
        mock_openstack_connection.network.find_ip.return_value = mock_fip

        client = InfomaniakDNSClient(mock_openstack_connection)
        result = client.delete_reverse_dns("195.15.220.30")

        assert result is True
        mock_openstack_connection.dns.delete_ptr_record.assert_called_once_with("fip-del")

    def test_delete_reverse_dns_fip_not_found(self, mock_openstack_connection):
        """delete_reverse_dns returns False when the floating IP is not found."""
        from codomyrmex.cloud.infomaniak.dns.client import InfomaniakDNSClient

        mock_openstack_connection.network.find_ip.return_value = None

        client = InfomaniakDNSClient(mock_openstack_connection)
        result = client.delete_reverse_dns("192.168.0.1")

        assert result is False
        mock_openstack_connection.dns.delete_ptr_record.assert_not_called()
