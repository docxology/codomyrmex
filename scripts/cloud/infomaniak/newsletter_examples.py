#!/usr/bin/env python3
"""
Infomaniak Newsletter API Examples.

Demonstrates all InfomaniakNewsletterClient operations:
- Campaign management (CRUD, send, schedule, statistics)
- Mailing list management (CRUD, contacts)
- Contact management
- Credits and task status

Usage:
    python newsletter_examples.py --list-campaigns
    python newsletter_examples.py --list-mailing-lists
    python newsletter_examples.py --create-campaign --subject "Test" --sender "news@activeinference.tech" --list-id 123
    python newsletter_examples.py --send-test --campaign 456 --email test@activeinference.tech
    python newsletter_examples.py --get-credits
"""

import sys
from pathlib import Path

try:
    import codomyrmex
except ImportError:
    project_root = Path(__file__).resolve().parent.parent.parent.parent
    sys.path.insert(0, str(project_root / "src"))

import argparse
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)


def get_client():
    """Get newsletter client from environment."""
    from codomyrmex.cloud.infomaniak.newsletter import InfomaniakNewsletterClient
    return InfomaniakNewsletterClient.from_env()


# ------------------------------------------------------------------
# Campaign operations
# ------------------------------------------------------------------

def list_campaigns(client):
    """List all campaigns."""
    print("\n📧 Campaigns\n" + "=" * 50)
    campaigns = client.list_campaigns()

    if not campaigns:
        print("   No campaigns found.")
        return

    for c in campaigns:
        print(f"   📨 {c.get('subject', 'Untitled')}")
        print(f"      ID: {c.get('id')}")
        print(f"      Status: {c.get('status')}")
        print()


def get_campaign(client, campaign_id: str):
    """Get campaign details."""
    print(f"\n📧 Campaign Details: {campaign_id}\n" + "=" * 50)
    campaign = client.get_campaign(campaign_id)

    if campaign:
        for k, v in campaign.items():
            print(f"   {k}: {v}")
    else:
        print("   Campaign not found")


def create_campaign(client, subject: str, sender_email: str, sender_name: str,
                    content_html: str, mailing_list_id: str):
    """Create a new campaign."""
    print(f"\n📧 Creating campaign: {subject}")

    result = client.create_campaign(
        subject=subject,
        sender_email=sender_email,
        sender_name=sender_name,
        content_html=content_html,
        mailing_list_id=mailing_list_id,
    )

    if result:
        print(f"\n   ✅ Created campaign: {result.get('id')}")
    else:
        print("   ❌ Failed to create campaign")


def delete_campaign(client, campaign_id: str):
    """Delete a campaign."""
    print(f"\n🗑️  Deleting campaign: {campaign_id}")

    if client.delete_campaign(campaign_id):
        print("   ✅ Campaign deleted")
    else:
        print("   ❌ Failed to delete campaign")


def send_test(client, campaign_id: str, email: str):
    """Send a test email."""
    print(f"\n🧪 Sending test for campaign {campaign_id} to {email}")

    if client.send_test(campaign_id, email):
        print("   ✅ Test email sent")
    else:
        print("   ❌ Failed to send test email")


def send_campaign(client, campaign_id: str):
    """Send a campaign immediately."""
    print(f"\n🚀 Sending campaign: {campaign_id}")

    if client.send_campaign(campaign_id):
        print("   ✅ Campaign sent")
    else:
        print("   ❌ Failed to send campaign")


def get_statistics(client, campaign_id: str):
    """Get campaign statistics."""
    print(f"\n📊 Campaign Statistics: {campaign_id}\n" + "=" * 50)
    stats = client.get_campaign_statistics(campaign_id)

    if stats:
        for k, v in stats.items():
            print(f"   {k}: {v}")
    else:
        print("   No statistics available")


# ------------------------------------------------------------------
# Mailing list operations
# ------------------------------------------------------------------

def list_mailing_lists(client):
    """List all mailing lists."""
    print("\n📋 Mailing Lists\n" + "=" * 50)
    lists = client.list_mailing_lists()

    if not lists:
        print("   No mailing lists found.")
        return

    for ml in lists:
        print(f"   📋 {ml.get('name', 'Unnamed')}")
        print(f"      ID: {ml.get('id')}")
        print()


def create_mailing_list(client, name: str):
    """Create a mailing list."""
    print(f"\n📋 Creating mailing list: {name}")

    result = client.create_mailing_list(name)
    if result:
        print(f"\n   ✅ Created mailing list: {result.get('id')}")
    else:
        print("   ❌ Failed to create mailing list")


def get_list_contacts(client, list_id: str):
    """Get contacts in a mailing list."""
    print(f"\n👥 Contacts in list {list_id}\n" + "=" * 50)
    contacts = client.get_list_contacts(list_id)

    if not contacts:
        print("   No contacts found.")
        return

    for c in contacts:
        print(f"   📧 {c.get('email', 'No email')}")
        print(f"      ID: {c.get('id')}")
        print()


# ------------------------------------------------------------------
# Utility operations
# ------------------------------------------------------------------

def get_credits(client):
    """Get newsletter credits."""
    print("\n💳 Newsletter Credits\n" + "=" * 50)
    credits = client.get_credits()

    if credits:
        for k, v in credits.items():
            print(f"   {k}: {v}")
    else:
        print("   Unable to retrieve credits")


def main():
    parser = argparse.ArgumentParser(description="Infomaniak Newsletter Examples")

    # Campaign operations
    parser.add_argument("--list-campaigns", action="store_true", help="List campaigns")
    parser.add_argument("--get-campaign", type=str, metavar="ID", help="Get campaign details")
    parser.add_argument("--create-campaign", action="store_true", help="Create a campaign")
    parser.add_argument("--delete-campaign", type=str, metavar="ID", help="Delete a campaign")
    parser.add_argument("--send-test", action="store_true", help="Send a test email")
    parser.add_argument("--send-campaign", type=str, metavar="ID", help="Send campaign")
    parser.add_argument("--statistics", type=str, metavar="ID", help="Get campaign statistics")

    # Mailing list operations
    parser.add_argument("--list-mailing-lists", action="store_true", help="List mailing lists")
    parser.add_argument("--create-mailing-list", type=str, metavar="NAME", help="Create mailing list")
    parser.add_argument("--list-contacts", type=str, metavar="LIST_ID", help="List contacts in list")

    # Utility
    parser.add_argument("--get-credits", action="store_true", help="Get newsletter credits")

    # Campaign creation options
    parser.add_argument("--subject", type=str, help="Campaign subject")
    parser.add_argument("--sender", type=str, help="Sender email (e.g., news@activeinference.tech)")
    parser.add_argument("--sender-name", type=str, default="Active Inference Institute", help="Sender name")
    parser.add_argument("--content", type=str, default="<h1>Newsletter</h1><p>Content here.</p>", help="HTML content")
    parser.add_argument("--list-id", type=str, help="Mailing list ID")

    # Test send options
    parser.add_argument("--campaign", type=str, help="Campaign ID (for --send-test)")
    parser.add_argument("--email", type=str, help="Recipient email (for --send-test)")

    # All operations
    parser.add_argument("--all", action="store_true", help="Show all information")

    args = parser.parse_args()

    try:
        client = get_client()
    except Exception as e:
        print(f"❌ Failed to create client: {e}")
        return 1

    if args.all:
        list_campaigns(client)
        list_mailing_lists(client)
        get_credits(client)
        return 0

    if args.list_campaigns:
        list_campaigns(client)
    elif args.get_campaign:
        get_campaign(client, args.get_campaign)
    elif args.create_campaign:
        if not all([args.subject, args.sender, args.list_id]):
            print("❌ --create-campaign requires --subject, --sender, --list-id")
            return 1
        create_campaign(client, args.subject, args.sender, args.sender_name,
                        args.content, args.list_id)
    elif args.delete_campaign:
        delete_campaign(client, args.delete_campaign)
    elif args.send_test:
        if not args.campaign or not args.email:
            print("❌ --send-test requires --campaign and --email")
            return 1
        send_test(client, args.campaign, args.email)
    elif args.send_campaign:
        send_campaign(client, args.send_campaign)
    elif args.statistics:
        get_statistics(client, args.statistics)
    elif args.list_mailing_lists:
        list_mailing_lists(client)
    elif args.create_mailing_list:
        create_mailing_list(client, args.create_mailing_list)
    elif args.list_contacts:
        get_list_contacts(client, args.list_contacts)
    elif args.get_credits:
        get_credits(client)
    else:
        parser.print_help()

    return 0


if __name__ == "__main__":
    sys.exit(main())
