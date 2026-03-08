"""
Infomaniak DNS Client (Designate).

Provides DNS zone and record management, including reverse DNS (PTR records).
"""

from typing import Any

from codomyrmex.cloud.infomaniak.base import InfomaniakOpenStackBase
from codomyrmex.logging_monitoring import get_logger

logger = get_logger(__name__)


class InfomaniakDNSClient(InfomaniakOpenStackBase):
    """
    Client for Infomaniak DNS (Designate) operations.

    Provides methods for managing DNS zones, record sets,
    and reverse DNS (PTR records) for floating IPs.

    Note: DNS Service is currently in BETA at Infomaniak.
    """

    _service_name = "dns"

    # =========================================================================
    # Zone Operations
    # =========================================================================

    def list_zones(self) -> list[dict[str, Any]]:
        """List all DNS zones."""
        try:
            zones = list(self._conn.dns.zones())
            return [
                {
                    "id": z.id,
                    "name": z.name,
                    "email": z.email,
                    "status": z.status,
                    "type": z.type,
                    "ttl": z.ttl,
                }
                for z in zones
            ]
        except Exception as e:
            logger.error("Failed to list zones: %s", e)
            raise

    def get_zone(self, zone_id: str) -> dict[str, Any] | None:
        """Get a specific zone by ID or name."""
        try:
            zone = self._conn.dns.find_zone(zone_id)
            if zone:
                return {
                    "id": zone.id,
                    "name": zone.name,
                    "email": zone.email,
                    "status": zone.status,
                    "ttl": zone.ttl,
                }
            return None
        except Exception as e:
            logger.error("Failed to get zone %s: %s", zone_id, e)
            raise

    def create_zone(
        self, name: str, email: str, ttl: int = 3600, description: str | None = None
    ) -> dict[str, Any] | None:
        """
        Create a new DNS zone.

        Args:
            name: Zone name (must end with '.')
            email: Admin email for SOA record
            ttl: Default TTL for records
            description: Optional description
        """
        try:
            # Ensure zone name ends with dot
            if not name.endswith("."):
                name = name + "."

            zone = self._conn.dns.create_zone(
                name=name, email=email, ttl=ttl, description=description
            )
            logger.info("Created zone: %s", zone.id)
            return {"id": zone.id, "name": zone.name}
        except Exception as e:
            logger.error("Failed to create zone %s: %s", name, e)
            raise

    def delete_zone(self, zone_id: str) -> bool:
        """Delete a DNS zone."""
        try:
            self._conn.dns.delete_zone(zone_id)
            logger.info("Deleted zone: %s", zone_id)
            return True
        except Exception as e:
            logger.error("Failed to delete zone %s: %s", zone_id, e)
            raise

    def update_zone(
        self,
        zone_id: str,
        email: str | None = None,
        ttl: int | None = None,
        description: str | None = None,
    ) -> bool:
        """Update a DNS zone."""
        try:
            updates = {}
            if email is not None:
                updates["email"] = email
            if ttl is not None:
                updates["ttl"] = ttl
            if description is not None:
                updates["description"] = description

            self._conn.dns.update_zone(zone_id, **updates)
            logger.info("Updated zone: %s", zone_id)
            return True
        except Exception as e:
            logger.error("Failed to update zone %s: %s", zone_id, e)
            raise

    # =========================================================================
    # Record Set Operations
    # =========================================================================

    def list_records(self, zone_id: str) -> list[dict[str, Any]]:
        """List all record sets in a zone."""
        try:
            records = list(self._conn.dns.recordsets(zone_id))
            return [
                {
                    "id": r.id,
                    "name": r.name,
                    "type": r.type,
                    "records": r.records,
                    "ttl": r.ttl,
                    "status": r.status,
                }
                for r in records
            ]
        except Exception as e:
            logger.error("Failed to list records in zone %s: %s", zone_id, e)
            raise

    def get_record(self, zone_id: str, record_id: str) -> dict[str, Any] | None:
        """Get a specific record set."""
        try:
            record = self._conn.dns.get_recordset(record_id, zone_id)
            if record:
                return {
                    "id": record.id,
                    "name": record.name,
                    "type": record.type,
                    "records": record.records,
                    "ttl": record.ttl,
                }
            return None
        except Exception as e:
            logger.error("Failed to get record %s: %s", record_id, e)
            raise

    def create_record(
        self,
        zone_id: str,
        name: str,
        record_type: str,
        records: list[str],
        ttl: int = 3600,
        description: str | None = None,
    ) -> dict[str, Any] | None:
        """
        Create a DNS record set.

        Args:
            zone_id: Zone ID or name
            name: Record name (must end with '.')
            record_type: Record type (A, AAAA, CNAME, MX, TXT, etc.)
            records: List of record values
            ttl: Time to live in seconds
            description: Optional description
        """
        try:
            # Ensure name ends with dot
            if not name.endswith("."):
                name = name + "."

            record = self._conn.dns.create_recordset(
                zone=zone_id,
                name=name,
                type=record_type,
                records=records,
                ttl=ttl,
                description=description,
            )
            logger.info("Created record: %s", record.id)
            return {"id": record.id, "name": record.name, "type": record_type}
        except Exception as e:
            logger.error("Failed to create record %s: %s", name, e)
            raise

    def update_record(
        self,
        zone_id: str,
        record_id: str,
        records: list[str] | None = None,
        ttl: int | None = None,
        description: str | None = None,
    ) -> bool:
        """Update a DNS record set."""
        try:
            updates = {}
            if records is not None:
                updates["records"] = records
            if ttl is not None:
                updates["ttl"] = ttl
            if description is not None:
                updates["description"] = description

            self._conn.dns.update_recordset(record_id, zone_id, **updates)
            logger.info("Updated record: %s", record_id)
            return True
        except Exception as e:
            logger.error("Failed to update record %s: %s", record_id, e)
            raise

    def delete_record(self, zone_id: str, record_id: str) -> bool:
        """Delete a DNS record set."""
        try:
            self._conn.dns.delete_recordset(record_id, zone_id)
            logger.info("Deleted record: %s", record_id)
            return True
        except Exception as e:
            logger.error("Failed to delete record %s: %s", record_id, e)
            raise

    # =========================================================================
    # Reverse DNS (PTR) Operations
    # =========================================================================

    def list_ptr_records(self) -> list[dict[str, Any]]:
        """List all PTR records (reverse DNS)."""
        try:
            ptrs = list(self._conn.dns.ptr_records())
            return [
                {
                    "id": ptr.id,
                    "ptrdname": ptr.ptrdname,
                    "address": ptr.address,
                    "status": ptr.status,
                }
                for ptr in ptrs
            ]
        except Exception as e:
            logger.error("Failed to list PTR records: %s", e)
            raise

    def set_reverse_dns(
        self,
        floating_ip: str,
        hostname: str,
        ttl: int = 3600,
        description: str | None = None,
    ) -> dict[str, Any] | None:
        """
        Set reverse DNS (PTR record) for a floating IP.

        Args:
            floating_ip: Floating IP address
            hostname: Hostname for PTR record (must end with '.')
            ttl: Time to live
            description: Optional description
        """
        try:
            # Ensure hostname ends with dot
            if not hostname.endswith("."):
                hostname = hostname + "."

            # Find the floating IP
            fip = self._conn.network.find_ip(floating_ip)
            if not fip:
                logger.error("Floating IP not found: %s", floating_ip)
                return None

            ptr = self._conn.dns.create_ptr_record(
                floating_ip_id=fip.id,
                ptrdname=hostname,
                ttl=ttl,
                description=description,
            )
            logger.info("Set reverse DNS for %s: %s", floating_ip, hostname)
            return {"id": ptr.id, "address": floating_ip, "ptrdname": hostname}
        except Exception as e:
            logger.error("Failed to set reverse DNS for %s: %s", floating_ip, e)
            raise

    def get_reverse_dns(self, floating_ip: str) -> dict[str, Any] | None:
        """Get reverse DNS (PTR record) for a floating IP."""
        try:
            fip = self._conn.network.find_ip(floating_ip)
            if not fip:
                return None

            ptr = self._conn.dns.get_ptr_record(fip.id)
            if ptr:
                return {
                    "id": ptr.id,
                    "address": floating_ip,
                    "ptrdname": ptr.ptrdname,
                    "ttl": ptr.ttl,
                }
            return None
        except Exception as e:
            logger.error("Failed to get reverse DNS for %s: %s", floating_ip, e)
            raise

    def delete_reverse_dns(self, floating_ip: str) -> bool:
        """Delete reverse DNS (PTR record) for a floating IP."""
        try:
            fip = self._conn.network.find_ip(floating_ip)
            if not fip:
                logger.error("Floating IP not found: %s", floating_ip)
                return False

            self._conn.dns.delete_ptr_record(fip.id)
            logger.info("Deleted reverse DNS for %s", floating_ip)
            return True
        except Exception as e:
            logger.error("Failed to delete reverse DNS for %s: %s", floating_ip, e)
            raise
