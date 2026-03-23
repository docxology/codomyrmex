"""Hermes Gateway Webhook Platform Adapter.

Provides HTTP POST handlers for GitHub events (PR reviews, commits, issues),
custom dashboards, and other webhook-enabled integrations.

Supports HMAC-SHA256 signature verification for security.
"""

from __future__ import annotations

import hashlib
import hmac
import json
import secrets
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, Protocol, runtime_checkable

from codomyrmex.logging_monitoring import get_logger

if TYPE_CHECKING:
    from collections.abc import Callable

logger = get_logger(__name__)


# ─────────────────────────────────────────────────────────────────────
# Configuration Types
# ─────────────────────────────────────────────────────────────────────


@dataclass
class WebhookRoute:
    """Configuration for a webhook route."""

    secret: str
    prompt_template: str
    handler: Callable[[dict[str, Any]], str] | None = None


@dataclass
class WebhookConfig:
    """Webhook platform configuration."""

    port: int = 8644
    routes: dict[str, WebhookRoute] = field(default_factory=dict)
    host: str = "0.0.0.0"


# ─────────────────────────────────────────────────────────────────────
# Webhook Payloads
# ─────────────────────────────────────────────────────────────────────


@dataclass
class GitHubPRReviewPayload:
    """GitHub PR review event payload."""

    action: str
    pr_number: int
    repo: str
    author: str
    title: str
    body: str
    review_body: str | None = None
    review_state: str | None = None


@dataclass
class GitHubCommitPayload:
    """GitHub commit push event payload."""

    repo: str
    branch: str
    commits: list[dict[str, Any]]
    pusher: str
    before: str
    after: str


@dataclass
class GitHubIssuePayload:
    """GitHub issue event payload."""

    action: str
    repo: str
    issue_number: int
    title: str
    body: str
    author: str
    labels: list[str] = field(default_factory=list)


# ─────────────────────────────────────────────────────────────────────
# Payload Parsers
# ─────────────────────────────────────────────────────────────────────


class WebhookPayloadParser:
    """Parse various webhook payload formats into structured types."""

    @staticmethod
    def parse_github_pr_review(payload: dict[str, Any]) -> GitHubPRReviewPayload | None:
        """Parse GitHub PR review webhook payload."""
        try:
            action = payload.get("action", "")
            pr = payload.get("pull_request", {})
            repo = payload.get("repository", {}).get("full_name", "")
            review = payload.get("review", {})

            return GitHubPRReviewPayload(
                action=action,
                pr_number=pr.get("number", 0),
                repo=repo,
                author=pr.get("user", {}).get("login", ""),
                title=pr.get("title", ""),
                body=pr.get("body", ""),
                review_body=review.get("body"),
                review_state=review.get("state"),
            )
        except Exception as e:
            logger.error(f"Failed to parse PR review payload: {e}")
            return None

    @staticmethod
    def parse_github_commit(payload: dict[str, Any]) -> GitHubCommitPayload | None:
        """Parse GitHub commit push webhook payload."""
        try:
            repo = payload.get("repository", {}).get("full_name", "")
            commits = payload.get("commits", [])
            ref = payload.get("ref", "")

            return GitHubCommitPayload(
                repo=repo,
                branch=ref.replace("refs/heads/", ""),
                commits=commits,
                pusher=payload.get("pusher", {}).get("name", ""),
                before=payload.get("before", ""),
                after=payload.get("after", ""),
            )
        except Exception as e:
            logger.error(f"Failed to parse commit payload: {e}")
            return None

    @staticmethod
    def parse_github_issue(payload: dict[str, Any]) -> GitHubIssuePayload | None:
        """Parse GitHub issue webhook payload."""
        try:
            action = payload.get("action", "")
            issue = payload.get("issue", {})
            repo = payload.get("repository", {}).get("full_name", "")

            return GitHubIssuePayload(
                action=action,
                repo=repo,
                issue_number=issue.get("number", 0),
                title=issue.get("title", ""),
                body=issue.get("body", ""),
                author=issue.get("user", {}).get("login", ""),
                labels=[label.get("name", "") for label in issue.get("labels", [])],
            )
        except Exception as e:
            logger.error(f"Failed to parse issue payload: {e}")
            return None


# ─────────────────────────────────────────────────────────────────────
# Signature Verification
# ─────────────────────────────────────────────────────────────────────


class WebhookSignatureVerifier:
    """Verify HMAC-SHA256 webhook signatures."""

    @staticmethod
    def verify(payload: bytes, secret: str, signature: str | None) -> bool:
        """Verify webhook payload signature.

        Args:
            payload: Raw request body bytes.
            secret: Secret key for HMAC verification.
            signature: X-Hub-Signature-256 header value.

        Returns:
            True if signature is valid, False otherwise.
        """
        if not signature or not secret:
            return False

        if not signature.startswith("sha256="):
            return False

        expected = hmac.new(secret.encode("utf-8"), payload, hashlib.sha256).hexdigest()

        return hmac.compare_digest(f"sha256={expected}", signature)


# ─────────────────────────────────────────────────────────────────────
# Prompt Templates
# ─────────────────────────────────────────────────────────────────────


class WebhookPromptBuilder:
    """Build Hermes prompts from webhook events."""

    @staticmethod
    def from_pr_review(payload: GitHubPRReviewPayload, template: str) -> str:
        """Build prompt from PR review event."""
        if template == "github_pr_review":
            return f"""GitHub PR Review Event

Repository: {payload.repo}
PR: #{payload.pr_number}
Author: {payload.author}
Title: {payload.title}
Action: {payload.action}

PR Description:
{payload.body}

{"Review: " + payload.review_body if payload.review_body else ""}
{"Review State: " + payload.review_state if payload.review_state else ""}

Analyze this PR and provide feedback on whether it should be merged."""
        return (
            f"GitHub event: {payload.action} on {payload.repo} PR #{payload.pr_number}"
        )

    @staticmethod
    def from_commit(payload: GitHubCommitPayload, template: str) -> str:
        """Build prompt from commit push event."""
        if template == "github_commit_push":
            commit_msgs = "\n".join(
                f"- {c.get('message', '')}" for c in payload.commits[:5]
            )
            return f"""GitHub Commit Push Event

Repository: {payload.repo}
Branch: {payload.branch}
Pusher: {payload.pusher}
Commits ({len(payload.commits)}):
{commit_msgs}

Review these commits and summarize the changes."""
        return f"GitHub push to {payload.repo}/{payload.branch}: {len(payload.commits)} commits"

    @staticmethod
    def from_issue(payload: GitHubIssuePayload, template: str) -> str:
        """Build prompt from issue event."""
        if template == "github_issue":
            return f"""GitHub Issue Event

Repository: {payload.repo}
Issue: #{payload.issue_number}
Author: {payload.author}
Action: {payload.action}
Title: {payload.title}

{"Labels: " + ", ".join(payload.labels) if payload.labels else ""}

Description:
{payload.body}

Analyze this issue and suggest how to address it."""
        return (
            f"GitHub issue: {payload.action} on {payload.repo} #{payload.issue_number}"
        )


# ─────────────────────────────────────────────────────────────────────
# Webhook Gateway Adapter
# ─────────────────────────────────────────────────────────────────────


@runtime_checkable
class WebhookGatewayAdapter(Protocol):
    """Protocol for webhook platform adapter."""

    @property
    def platform_name(self) -> str:
        """Name of the platform."""
        ...

    async def start(self) -> None:
        """Start the webhook server."""
        ...

    async def stop(self) -> None:
        """Stop the webhook server."""
        ...


class WebhookAdapter:
    """HTTP webhook adapter for Hermes gateway.

    Handles incoming HTTP POST webhooks from GitHub, custom dashboards,
    and other webhook-enabled services with HMAC verification.

    Attributes:
        config: Webhook configuration including port and routes.
        _server: Internal HTTP server instance.

    Example::

        config = WebhookConfig(
            port=8644,
            routes={
                "github_events": WebhookRoute(
                    secret="your-hmac-secret", prompt_template="github_pr_review"
                ),
                "dashboard": WebhookRoute(
                    secret="dashboard-api-key", prompt_template="dashboard_command"
                ),
            },
        )
        adapter = WebhookAdapter(config)
        await adapter.start()
    """

    def __init__(self, config: WebhookConfig) -> None:
        """Initialize the webhook adapter.

        Args:
            config: Webhook configuration with routes and port.
        """
        self.config = config
        self._server = None
        self._running = False
        self._parser = WebhookPayloadParser()
        self._prompt_builder = WebhookPromptBuilder()
        self._verifier = WebhookSignatureVerifier()

    @property
    def platform_name(self) -> str:
        """Return platform name."""
        return "webhook"

    async def start(self) -> None:
        """Start the webhook HTTP server."""
        logger.info(
            f"Starting webhook adapter on {self.config.host}:{self.config.port}"
        )
        self._running = True
        # Note: Full HTTP server implementation would use aiohttp or similar
        # This is the adapter interface - actual server starts in GatewayRunner

    async def stop(self) -> None:
        """Stop the webhook HTTP server."""
        logger.info("Stopping webhook adapter")
        self._running = False
        self._server = None

    def verify_request(
        self, route_name: str, payload: bytes, signature: str | None
    ) -> bool:
        """Verify webhook request signature.

        Args:
            route_name: Name of the route to verify against.
            payload: Raw request body.
            signature: X-Hub-Signature-256 header.

        Returns:
            True if signature is valid.
        """
        route = self.config.routes.get(route_name)
        if not route:
            return False
        return self._verifier.verify(payload, route.secret, signature)

    def build_prompt(self, route_name: str, payload: dict[str, Any]) -> str:
        """Build Hermes prompt from webhook payload.

        Args:
            route_name: Route name to determine template.
            payload: Parsed webhook payload.

        Returns:
            Formatted prompt for Hermes.
        """
        route = self.config.routes.get(route_name)
        template = route.prompt_template if route else "default"

        # Detect event type and build appropriate prompt
        if "pull_request" in payload:
            pr_payload = self._parser.parse_github_pr_review(payload)
            if pr_payload:
                return self._prompt_builder.from_pr_review(pr_payload, template)

        if "commits" in payload:
            commit_payload = self._parser.parse_github_commit(payload)
            if commit_payload:
                return self._prompt_builder.from_commit(commit_payload, template)

        if "issue" in payload:
            issue_payload = self._parser.parse_github_issue(payload)
            if issue_payload:
                return self._prompt_builder.from_issue(issue_payload, template)

        # Fallback: return raw payload as string
        return f"Webhook event: {json.dumps(payload, indent=2)}"


# ─────────────────────────────────────────────────────────────────────
# Factory
# ─────────────────────────────────────────────────────────────────────


def create_webhook_adapter(
    port: int = 8644,
    routes: dict[str, dict[str, str]] | None = None,
    host: str = "0.0.0.0",
) -> WebhookAdapter:
    """Create a webhook adapter from simple config.

    Args:
        port: HTTP server port.
        routes: Dictionary of route configs.
        host: HTTP server host.

    Returns:
        Configured WebhookAdapter instance.
    """
    webhook_routes: dict[str, WebhookRoute] = {}

    if routes:
        for name, config in routes.items():
            webhook_routes[name] = WebhookRoute(
                secret=config.get("secret", secrets.token_hex(32)),
                prompt_template=config.get("prompt_template", "default"),
            )

    config = WebhookConfig(port=port, routes=webhook_routes, host=host)
    return WebhookAdapter(config)


__all__ = [
    "GitHubCommitPayload",
    "GitHubIssuePayload",
    "GitHubPRReviewPayload",
    "WebhookAdapter",
    "WebhookConfig",
    "WebhookPayloadParser",
    "WebhookPromptBuilder",
    "WebhookRoute",
    "WebhookSignatureVerifier",
    "create_webhook_adapter",
]
