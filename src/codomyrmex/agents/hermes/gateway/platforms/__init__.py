"""Hermes Gateway Platform Adapters.

Handles routing specific to downstream platforms (Telegram, Slack, WhatsApp,
Webhook, Discord, CLI).
"""

from .metrics import GatewayAdapter, PlatformContext, PlatformMetrics
from .webhook import (
    GitHubCommitPayload,
    GitHubIssuePayload,
    GitHubPRReviewPayload,
    WebhookAdapter,
    WebhookConfig,
    WebhookRoute,
    create_webhook_adapter,
)

__all__ = [
    "GatewayAdapter",
    "GitHubCommitPayload",
    "GitHubIssuePayload",
    "GitHubPRReviewPayload",
    "PlatformContext",
    "PlatformMetrics",
    "WebhookAdapter",
    "WebhookConfig",
    "WebhookRoute",
    "create_webhook_adapter",
]
