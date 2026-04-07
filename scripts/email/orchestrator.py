#!/usr/bin/env python3
"""
Orchestrator script for the Email module.
Demonstrates usage of GmailProvider and AgentMailProvider.
"""

import os
import sys
from datetime import datetime

# Add src to sys.path to allow importing codomyrmex if not installed
sys.path.insert(
    0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../src"))
)

from codomyrmex.email import (
    AGENTMAIL_AVAILABLE,
    GMAIL_AVAILABLE,
    AgentMailProvider,
    EmailDraft,
    GmailProvider,
)
from codomyrmex.email.exceptions import EmailError


def run_agentmail_demo():
    print("--- AgentMail Provider Demo ---")
    if not AGENTMAIL_AVAILABLE or AgentMailProvider is None:
        print("AgentMail SDK not installed. Skip.")
        return

    try:
        # Provider auth from environment (name matches upstream SDK)
        if not os.environ.get("AGENTMAIL_API_KEY"):
            print("AgentMail provider auth not configured. Skip live demo.")
            print("Usage: configure provider env per module docs, then AgentMailProvider()")
            return

        provider = AgentMailProvider()
        print("AgentMailProvider initialized.")

        # List inboxes
        inboxes = provider.list_inboxes(limit=5)
        print(f"Found {len(inboxes)} inboxes.")
        for ib in inboxes:
            print(f" - {ib.inbox_id} ({ib.display_name})")

        if not inboxes:
            print("No inboxes found. Creating a temporary one...")
            inbox = provider.create_inbox(display_name="Orchestrator Demo")
            print(f"Created inbox: {inbox.inbox_id}")
        else:
            inbox = inboxes[0]

        # List messages
        messages = provider.list_messages(inbox_id=inbox.inbox_id, max_results=5)
        print(f"Found {len(messages)} messages in {inbox.inbox_id}.")

        # Send a test message to ourselves
        draft = EmailDraft(
            subject=f"Test from Orchestrator - {datetime.now().isoformat()}",
            to=[inbox.inbox_id],
            body_text="This is a test message sent by the email orchestrator script.",
        )
        print(f"Sending test message to {inbox.inbox_id}...")
        sent_msg = provider.send_message(draft, inbox_id=inbox.inbox_id)
        print(f"Message sent! ID: {sent_msg.id}")

    except EmailError:
        print("AgentMail Error (details omitted; enable logging for trace)")
    except Exception as exc:
        print(f"Unexpected Error: {type(exc).__name__}")


def run_gmail_demo():
    print("\n--- Gmail Provider Demo ---")
    if not GMAIL_AVAILABLE or GmailProvider is None:
        print("Gmail dependencies not installed. Skip.")
        return

    try:
        # GmailProvider.from_env() checks for various credentials
        # It might raise EmailAuthError if none are found.
        try:
            provider = GmailProvider.from_env()
            print("GmailProvider initialized from environment.")
        except EmailError as e:
            print(f"Gmail Auth/Init Error: {e}")
            return

        # List messages
        messages = provider.list_messages(max_results=5)
        print(f"Found {len(messages)} messages.")
        for msg in messages:
            print(f" - [{msg.date}] {msg.subject} (from: {msg.sender.email})")

        # Create a draft instead of sending (safer for demo)
        draft = EmailDraft(
            subject=f"Draft from Orchestrator - {datetime.now().isoformat()}",
            to=["recipient@example.com"],
            body_text="This is a draft message created by the email orchestrator script.",
        )
        draft_id = provider.create_draft(draft)
        print(f"Created Gmail draft with ID: {draft_id}")

    except EmailError as e:
        print(f"Gmail Error: {e}")
    except Exception as e:
        print(f"Unexpected Error: {e}")


def main():
    # Auto-injected: Load configuration
    from pathlib import Path

    import yaml

    config_path = (
        Path(__file__).resolve().parent.parent.parent
        / "config"
        / "email"
        / "config.yaml"
    )
    if config_path.exists():
        with open(config_path) as f:
            yaml.safe_load(f) or {}
            print("Loaded config from config/email/config.yaml")

    print("Codomyrmex Email Orchestrator")
    print(f"Date: {datetime.now().isoformat()}")
    print("=" * 30)

    run_agentmail_demo()
    run_gmail_demo()

    print("\nOrchestrator demo complete.")


if __name__ == "__main__":
    main()
