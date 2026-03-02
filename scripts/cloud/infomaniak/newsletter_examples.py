#!/usr/bin/env python3
"""
Infomaniak Newsletter API Examples.

Demonstrates all 23 InfomaniakNewsletterClient operations:
- Campaign management (CRUD, send, schedule, statistics)
- Mailing list management (CRUD, contacts)
- Contact management (CRUD, import, subscribe/unsubscribe)
- Credits and task status

Usage:
    python newsletter_examples.py --list-campaigns
    python newsletter_examples.py --list-mailing-lists
    python newsletter_examples.py --create-campaign --subject "Test" --sender "news@activeinference.tech" --list-id 123
    python newsletter_examples.py --send-test --campaign 456 --email test@activeinference.tech
    python newsletter_examples.py --get-credits
    python newsletter_examples.py --all
"""

import sys
from pathlib import Path

try:
    import codomyrmex  # noqa: F401
except ImportError:
    project_root = Path(__file__).resolve().parent.parent.parent.parent
    sys.path.insert(0, str(project_root / "src"))

import argparse
import json
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


def update_campaign(client, campaign_id: str, **kwargs):
    """Update a campaign."""
    print(f"\n📧 Updating campaign: {campaign_id}")

    result = client.update_campaign(campaign_id, **kwargs)
    if result:
        print(f"   ✅ Campaign updated: {result.get('id')}")
    else:
        print("   ❌ Failed to update campaign")


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


def schedule_campaign(client, campaign_id: str, send_at: str):
    """Schedule a campaign for future delivery."""
    print(f"\n📅 Scheduling campaign {campaign_id} for {send_at}")

    if client.schedule_campaign(campaign_id, send_at):
        print("   ✅ Campaign scheduled")
    else:
        print("   ❌ Failed to schedule campaign")


def unschedule_campaign(client, campaign_id: str):
    """Cancel a scheduled campaign."""
    print(f"\n📅 Unscheduling campaign: {campaign_id}")

    if client.unschedule_campaign(campaign_id):
        print("   ✅ Campaign unscheduled")
    else:
        print("   ❌ Failed to unschedule campaign")


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


def get_mailing_list(client, list_id: str):
    """Get mailing list details."""
    print(f"\n📋 Mailing List Details: {list_id}\n" + "=" * 50)
    ml = client.get_mailing_list(list_id)

    if ml:
        for k, v in ml.items():
            print(f"   {k}: {v}")
    else:
        print("   Mailing list not found")


def create_mailing_list(client, name: str):
    """Create a mailing list."""
    print(f"\n📋 Creating mailing list: {name}")

    result = client.create_mailing_list(name)
    if result:
        print(f"\n   ✅ Created mailing list: {result.get('id')}")
    else:
        print("   ❌ Failed to create mailing list")


def update_mailing_list(client, list_id: str, **kwargs):
    """Update a mailing list."""
    print(f"\n📋 Updating mailing list: {list_id}")

    result = client.update_mailing_list(list_id, **kwargs)
    if result:
        print(f"   ✅ Mailing list updated: {result.get('id')}")
    else:
        print("   ❌ Failed to update mailing list")


def delete_mailing_list(client, list_id: str):
    """Delete a mailing list."""
    print(f"\n🗑️  Deleting mailing list: {list_id}")

    if client.delete_mailing_list(list_id):
        print("   ✅ Mailing list deleted")
    else:
        print("   ❌ Failed to delete mailing list")


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


def import_contacts(client, list_id: str, contacts_file: str):
    """Import contacts from a JSON file into a mailing list."""
    print(f"\n📥 Importing contacts into list {list_id} from {contacts_file}")

    try:
        with open(contacts_file, "r") as f:
            contacts = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"   ❌ Failed to read contacts file: {e}")
        return

    result = client.import_contacts(list_id, contacts)
    if result:
        print(f"   ✅ Import started: task {result.get('task_id', 'unknown')}")
    else:
        print("   ❌ Failed to import contacts")


def manage_contact(client, list_id: str, contact_id: str, action: str):
    """Manage contact subscription status."""
    print(f"\n👤 {action.capitalize()} contact {contact_id} in list {list_id}")

    if client.manage_contact(list_id, contact_id, action):
        print(f"   ✅ Contact {action}d")
    else:
        print(f"   ❌ Failed to {action} contact")


# ------------------------------------------------------------------
# Contact operations
# ------------------------------------------------------------------

def get_contact(client, contact_id: str):
    """Get contact details."""
    print(f"\n👤 Contact Details: {contact_id}\n" + "=" * 50)
    contact = client.get_contact(contact_id)

    if contact:
        for k, v in contact.items():
            print(f"   {k}: {v}")
    else:
        print("   Contact not found")


def update_contact(client, contact_id: str, **kwargs):
    """Update a contact."""
    print(f"\n👤 Updating contact: {contact_id}")

    result = client.update_contact(contact_id, **kwargs)
    if result:
        print(f"   ✅ Contact updated: {result.get('id')}")
    else:
        print("   ❌ Failed to update contact")


def delete_contact(client, contact_id: str):
    """Delete a contact."""
    print(f"\n🗑️  Deleting contact: {contact_id}")

    if client.delete_contact(contact_id):
        print("   ✅ Contact deleted")
    else:
        print("   ❌ Failed to delete contact")


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


def get_task_status(client, task_id: str):
    """Check async task status."""
    print(f"\n⏳ Task Status: {task_id}\n" + "=" * 50)
    status = client.get_task_status(task_id)

    if status:
        for k, v in status.items():
            print(f"   {k}: {v}")
    else:
        print("   Task not found")


def main():
    parser = argparse.ArgumentParser(description="Infomaniak Newsletter Examples")

    # Campaign operations
    parser.add_argument("--list-campaigns", action="store_true", help="List campaigns")
    parser.add_argument("--get-campaign", type=str, metavar="ID", help="Get campaign details")
    parser.add_argument("--create-campaign", action="store_true", help="Create a campaign")
    parser.add_argument("--update-campaign", type=str, metavar="ID", help="Update a campaign")
    parser.add_argument("--delete-campaign", type=str, metavar="ID", help="Delete a campaign")
    parser.add_argument("--send-test", action="store_true", help="Send a test email")
    parser.add_argument("--schedule", type=str, metavar="ID", help="Schedule a campaign")
    parser.add_argument("--unschedule", type=str, metavar="ID", help="Unschedule a campaign")
    parser.add_argument("--send-campaign", type=str, metavar="ID", help="Send campaign")
    parser.add_argument("--statistics", type=str, metavar="ID", help="Get campaign statistics")

    # Mailing list operations
    parser.add_argument("--list-mailing-lists", action="store_true", help="List mailing lists")
    parser.add_argument("--get-mailing-list", type=str, metavar="ID", help="Get mailing list details")
    parser.add_argument("--create-mailing-list", type=str, metavar="NAME", help="Create mailing list")
    parser.add_argument("--update-mailing-list", type=str, metavar="ID", help="Update mailing list")
    parser.add_argument("--delete-mailing-list", type=str, metavar="ID", help="Delete mailing list")
    parser.add_argument("--list-contacts", type=str, metavar="LIST_ID", help="List contacts in list")
    parser.add_argument("--import-contacts", type=str, metavar="LIST_ID", help="Import contacts into list")
    parser.add_argument("--manage-contact", action="store_true", help="Manage contact subscription")

    # Contact operations
    parser.add_argument("--get-contact", type=str, metavar="ID", help="Get contact details")
    parser.add_argument("--update-contact", type=str, metavar="ID", help="Update a contact")
    parser.add_argument("--delete-contact", type=str, metavar="ID", help="Delete a contact")

    # Utility
    parser.add_argument("--get-credits", action="store_true", help="Get newsletter credits")
    parser.add_argument("--get-task-status", type=str, metavar="ID", help="Get task status")

    # Supporting arguments
    parser.add_argument("--subject", type=str, help="Campaign subject")
    parser.add_argument("--sender", type=str, help="Sender email (e.g., news@activeinference.tech)")
    parser.add_argument("--sender-name", type=str, default="Active Inference Institute", help="Sender name")
    parser.add_argument("--content", type=str, default=None, help="HTML content")
    parser.add_argument("--list-id", type=str, help="Mailing list ID")
    parser.add_argument("--campaign", type=str, help="Campaign ID (for --send-test)")
    parser.add_argument("--email", type=str, help="Recipient email (for --send-test)")
    parser.add_argument("--schedule-at", type=str, help="ISO 8601 datetime for scheduling")
    parser.add_argument("--contact-id", type=str, help="Contact ID")
    parser.add_argument("--action", type=str, choices=["subscribe", "unsubscribe"], help="Contact action")
    parser.add_argument("--contacts-file", type=str, help="JSON file with contacts for import")
    parser.add_argument("--name", type=str, help="Name for update operations")

    # Validation
    parser.add_argument("--validate", action="store_true", help="Validate connection to API")

    # All operations
    parser.add_argument("--all", action="store_true", help="Show all information")

    args = parser.parse_args()

    try:
        client = get_client()
    except Exception as e:
        print(f"❌ Failed to create client: {e}")
        return 1

    if args.validate:
        ok = client.validate_connection()
        print(f"\n{'✅' if ok else '❌'} Connection {'valid' if ok else 'FAILED'}")
        return 0 if ok else 1

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
        content = args.content or "<h1>Newsletter</h1><p>Content here.</p>"
        create_campaign(client, args.subject, args.sender, args.sender_name,
                        content, args.list_id)
    elif args.update_campaign:
        kwargs = {}
        if args.subject:
            kwargs["subject"] = args.subject
        if args.content:
            kwargs["content"] = args.content
        update_campaign(client, args.update_campaign, **kwargs)
    elif args.delete_campaign:
        delete_campaign(client, args.delete_campaign)
    elif args.send_test:
        if not args.campaign or not args.email:
            print("❌ --send-test requires --campaign and --email")
            return 1
        send_test(client, args.campaign, args.email)
    elif args.schedule:
        if not args.schedule_at:
            print("❌ --schedule requires --schedule-at (ISO 8601 datetime)")
            return 1
        schedule_campaign(client, args.schedule, args.schedule_at)
    elif args.unschedule:
        unschedule_campaign(client, args.unschedule)
    elif args.send_campaign:
        send_campaign(client, args.send_campaign)
    elif args.statistics:
        get_statistics(client, args.statistics)
    elif args.list_mailing_lists:
        list_mailing_lists(client)
    elif args.get_mailing_list:
        get_mailing_list(client, args.get_mailing_list)
    elif args.create_mailing_list:
        create_mailing_list(client, args.create_mailing_list)
    elif args.update_mailing_list:
        kwargs = {}
        if args.name:
            kwargs["name"] = args.name
        update_mailing_list(client, args.update_mailing_list, **kwargs)
    elif args.delete_mailing_list:
        delete_mailing_list(client, args.delete_mailing_list)
    elif args.list_contacts:
        get_list_contacts(client, args.list_contacts)
    elif args.import_contacts:
        if not args.contacts_file:
            print("❌ --import-contacts requires --contacts-file")
            return 1
        import_contacts(client, args.import_contacts, args.contacts_file)
    elif args.manage_contact:
        if not all([args.list_id, args.contact_id, args.action]):
            print("❌ --manage-contact requires --list-id, --contact-id, --action")
            return 1
        manage_contact(client, args.list_id, args.contact_id, args.action)
    elif args.get_contact:
        get_contact(client, args.get_contact)
    elif args.update_contact:
        kwargs = {}
        if args.name:
            kwargs["name"] = args.name
        if args.email:
            kwargs["email"] = args.email
        update_contact(client, args.update_contact, **kwargs)
    elif args.delete_contact:
        delete_contact(client, args.delete_contact)
    elif args.get_credits:
        get_credits(client)
    elif args.get_task_status:
        get_task_status(client, args.get_task_status)
    else:
        parser.print_help()

    return 0


if __name__ == "__main__":
    sys.exit(main())
