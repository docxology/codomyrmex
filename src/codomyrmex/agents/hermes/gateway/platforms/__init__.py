"""Hermes Gateway Platform Adapters.

Handles routing specific to downstream platforms (Telegram, Slack, WhatsApp).
"""

from .metrics import GatewayAdapter, PlatformContext, PlatformMetrics

__all__ = ["GatewayAdapter", "PlatformContext", "PlatformMetrics"]
