from dataclasses import dataclass
from datetime import datetime

from codomyrmex.logging_monitoring.logger_config import get_logger

"""Physical asset inventory management."""

logger = get_logger(__name__)

# Global singleton instance for functional wrappers
_GLOBAL_INVENTORY = None


def get_asset_inventory() -> "AssetInventory":
    """Get or create the global AssetInventory instance."""
    global _GLOBAL_INVENTORY
    if _GLOBAL_INVENTORY is None:
        _GLOBAL_INVENTORY = AssetInventory()
    return _GLOBAL_INVENTORY


@dataclass
class PhysicalAsset:
    """Represents a physical asset."""

    asset_id: str
    name: str
    asset_type: str
    location: str
    status: str  # active, inactive, maintenance, lost
    registered_at: datetime
    last_checked: datetime | None = None


class AssetInventory:
    """Manages physical asset inventory."""

    def __init__(self):

        self.assets: dict[str, PhysicalAsset] = {}
        logger.info("AssetInventory initialized")

    def register_asset(
        self,
        asset_id: str,
        name: str,
        asset_type: str,
        location: str,
    ) -> PhysicalAsset:
        """Register a new physical asset."""
        asset = PhysicalAsset(
            asset_id=asset_id,
            name=name,
            asset_type=asset_type,
            location=location,
            status="active",
            registered_at=datetime.now(),
            last_checked=datetime.now(),
        )
        self.assets[asset_id] = asset
        logger.info(f"Registered asset {asset_id}: {name}")
        return asset

    def track_asset(self, asset_id: str, location: str | None = None) -> bool:
        """Update asset tracking information."""
        if asset_id not in self.assets:
            logger.warning(f"Asset {asset_id} not found")
            return False

        asset = self.assets[asset_id]
        if location:
            asset.location = location
        asset.last_checked = datetime.now()
        logger.debug(f"Tracked asset {asset_id} at {asset.location}")
        return True

    def get_asset_status(self, asset_id: str) -> PhysicalAsset | None:
        """Get asset status."""
        return self.assets.get(asset_id)


def register_asset(
    asset_id: str,
    name: str,
    asset_type: str,
    location: str,
    inventory: AssetInventory | None = None,
) -> PhysicalAsset:
    """Register a new asset."""
    if inventory is None:
        inventory = get_asset_inventory()
    return inventory.register_asset(asset_id, name, asset_type, location)


def track_asset(
    asset_id: str,
    location: str | None = None,
    inventory: AssetInventory | None = None,
) -> bool:
    """Track an asset."""
    if inventory is None:
        inventory = get_asset_inventory()
    return inventory.track_asset(asset_id, location)


def get_asset_status(
    asset_id: str,
    inventory: AssetInventory | None = None,
) -> PhysicalAsset | None:
    """Get asset status."""
    if inventory is None:
        inventory = get_asset_inventory()
    return inventory.get_asset_status(asset_id)

