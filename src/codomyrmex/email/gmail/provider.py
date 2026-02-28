"""Gmail implementation of the EmailProvider interface."""

import base64
import os
from datetime import datetime
from email.message import EmailMessage as PyEmailMessage

from ..exceptions import (
    EmailAPIError,
    EmailAuthError,
    InvalidMessageError,
    MessageNotFoundError,
)
from ..generics import EmailAddress, EmailDraft, EmailMessage, EmailProvider

try:
    from google.oauth2.credentials import Credentials
    from googleapiclient.discovery import Resource, build
    from googleapiclient.errors import HttpError
    GMAIL_AVAILABLE = True
except ImportError:
    Credentials = None
    Resource = None
    HttpError = Exception
    build = None
    GMAIL_AVAILABLE = False

_GMAIL_SCOPES = [
    "https://www.googleapis.com/auth/gmail.send",
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/gmail.modify",
]


class GmailProvider(EmailProvider):
    """Google Mail provider implementation."""

    def __init__(self, credentials: Credentials | None = None, service: Resource | None = None):
        """
        Initialize the Gmail provider.

        Args:
            credentials: A google.oauth2.credentials.Credentials object.
            service: A pre-built and authenticated Google Mail API resource object.
        """
        if not GMAIL_AVAILABLE:
            raise ImportError(
                "Gmail dependencies are not installed. "
                "Please install codomyrmex with the 'email' extra: uv sync --extra email"
            )

        if not credentials and not service:
            raise EmailAuthError("Either credentials or a built service object must be provided.")

        try:
            self.service = service or build('gmail', 'v1', credentials=credentials)
        except Exception as e:
            raise EmailAuthError(f"Failed to initialize Gmail API service: {e}")

    @classmethod
    def from_env(cls) -> "GmailProvider":
        """Create a GmailProvider from environment variables.

        Tries OAuth2 env vars first (GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET,
        GOOGLE_REFRESH_TOKEN), then falls back to Application Default Credentials
        (GOOGLE_APPLICATION_CREDENTIALS).

        Raises:
            EmailAuthError: If no valid credentials are available.
            ImportError: If Gmail dependencies are not installed.
        """
        if not GMAIL_AVAILABLE:
            raise ImportError(
                "Gmail dependencies are not installed. "
                "Run: uv sync --extra email"
            )

        # Option 1: Explicit OAuth2 env vars
        refresh_token = os.getenv("GOOGLE_REFRESH_TOKEN")
        client_id = os.getenv("GOOGLE_CLIENT_ID")
        client_secret = os.getenv("GOOGLE_CLIENT_SECRET")

        if refresh_token and client_id and client_secret:
            creds = Credentials(
                token=None,
                refresh_token=refresh_token,
                token_uri="https://oauth2.googleapis.com/token",
                client_id=client_id,
                client_secret=client_secret,
                scopes=_GMAIL_SCOPES,
            )
            return cls(credentials=creds)

        # Option 2: Application Default Credentials
        try:
            import google.auth  # noqa: PLC0415 — conditional import
            creds, _ = google.auth.default(scopes=_GMAIL_SCOPES)
            return cls(credentials=creds)
        except Exception as e:
            raise EmailAuthError(
                "No Gmail credentials found. Set GOOGLE_CLIENT_ID + "
                "GOOGLE_CLIENT_SECRET + GOOGLE_REFRESH_TOKEN env vars, "
                f"or configure GOOGLE_APPLICATION_CREDENTIALS: {e}"
            ) from e

    def _parse_email_address(self, raw_header: str) -> list[EmailAddress]:
        """Parse a raw 'To' or 'From' header into a list of EmailAddress objects."""
        # This is a very simplistic parser. In a real scenario, use `email.utils.getaddresses`.
        addresses = []
        import email.utils
        for name, addr in email.utils.getaddresses([raw_header]):
            addresses.append(EmailAddress(name=name if name else None, email=addr))
        return addresses

    def _gmail_dict_to_message(self, payload: dict) -> EmailMessage:
        """Convert a Gmail API message dictionary to an EmailMessage."""
        try:
            headers_list = payload.get('payload', {}).get('headers', [])
            headers = {h['name'].lower(): h['value'] for h in headers_list}

            sender_addrs = self._parse_email_address(headers.get('from', ''))
            sender = sender_addrs[0] if sender_addrs else EmailAddress(email="unknown@example.com")

            to_addrs = self._parse_email_address(headers.get('to', ''))
            cc_addrs = self._parse_email_address(headers.get('cc', ''))
            bcc_addrs = self._parse_email_address(headers.get('bcc', ''))

            date_str = headers.get('date', '')
            import email.utils
            parsed_date = email.utils.parsedate_to_datetime(date_str) if date_str else datetime.utcnow()

            body_text = ""
            body_html = ""

            def extract_parts(parts):
                """Execute Extract Parts operations natively."""
                nonlocal body_text, body_html
                for part in parts:
                    mime_type = part.get('mimeType')
                    body_data = part.get('body', {}).get('data', '')
                    if body_data:
                        decoded_data = base64.urlsafe_b64decode(body_data).decode('utf-8')
                        if mime_type == 'text/plain':
                            body_text += decoded_data
                        elif mime_type == 'text/html':
                            body_html += decoded_data
                    if 'parts' in part:
                        extract_parts(part['parts'])

            payload_part = payload.get('payload', {})
            if payload_part.get('mimeType') == 'text/plain':
                 body_data = payload_part.get('body', {}).get('data', '')
                 if body_data:
                     body_text = base64.urlsafe_b64decode(body_data).decode('utf-8')
            elif payload_part.get('mimeType') == 'text/html':
                body_data = payload_part.get('body', {}).get('data', '')
                if body_data:
                    body_html = base64.urlsafe_b64decode(body_data).decode('utf-8')
            else:
                 extract_parts(payload_part.get('parts', []))

            return EmailMessage(
                id=payload.get('id'),
                thread_id=payload.get('threadId'),
                subject=headers.get('subject', '(No Subject)'),
                sender=sender,
                to=to_addrs,
                cc=cc_addrs,
                bcc=bcc_addrs,
                body_text=body_text if body_text else None,
                body_html=body_html if body_html else None,
                date=parsed_date,
                labels=payload.get('labelIds', [])
            )
        except Exception as e:
            raise InvalidMessageError(f"Failed to parse Gmail message data: {e}")

    def _create_raw_message(self, draft: EmailDraft) -> dict:
        """Create a raw base64 string dictionary for Gmail insertion."""
        msg = PyEmailMessage()
        msg['Subject'] = draft.subject
        msg['To'] = ", ".join(draft.to)
        if draft.cc:
             msg['Cc'] = ", ".join(draft.cc)
        if draft.bcc:
             msg['Bcc'] = ", ".join(draft.bcc)

        if draft.body_html:
            msg.set_content(draft.body_text or "")
            msg.add_alternative(draft.body_html, subtype='html')
        else:
            msg.set_content(draft.body_text or "")

        raw = base64.urlsafe_b64encode(msg.as_bytes()).decode()
        return {'raw': raw}

    def list_messages(self, query: str = "", max_results: int = 100, user_id: str = 'me') -> list[EmailMessage]:
        """List messages matching the generic query."""
        try:
            results = self.service.users().messages().list(
                userId=user_id,
                q=query,
                maxResults=max_results
            ).execute()
            messages_meta = results.get('messages', [])

            # Note: The list API only returns IDs. We have to batch get them or get them individually
            # we do individually for simplicity here, but batching is better for prod
            full_messages = []
            for msg_meta in messages_meta:
                 full_messages.append(self.get_message(msg_meta['id'], user_id))
            return full_messages
        except HttpError as e:
            raise EmailAPIError(f"Failed to list messages: {e}")

    def get_message(self, message_id: str, user_id: str = 'me') -> EmailMessage:
        """Fetch a specific message by its ID."""
        try:
            message = self.service.users().messages().get(
                userId=user_id,
                id=message_id,
                format='full'
            ).execute()
            return self._gmail_dict_to_message(message)
        except HttpError as e:
            if e.resp.status == 404:
                raise MessageNotFoundError(f"Message with ID {message_id} not found.")
            raise EmailAPIError(f"Failed to fetch message: {e}")

    def send_message(self, draft: EmailDraft, user_id: str = 'me') -> EmailMessage:
        """Send a new email immediately."""
        try:
            raw_msg = self._create_raw_message(draft)
            sent_message = self.service.users().messages().send(
                userId=user_id,
                body=raw_msg
            ).execute()
            return self.get_message(sent_message['id'], user_id)
        except HttpError as e:
            raise EmailAPIError(f"Failed to send email: {e}")

    def create_draft(self, draft: EmailDraft, user_id: str = 'me') -> str:
        """Create a new draft and return its ID."""
        try:
            raw_msg = self._create_raw_message(draft)
            created_draft = self.service.users().drafts().create(
                userId=user_id,
                body={'message': raw_msg}
            ).execute()
            return created_draft['id']
        except HttpError as e:
            raise EmailAPIError(f"Failed to create draft: {e}")

    def delete_message(self, message_id: str, user_id: str = 'me') -> None:
        """Delete an email message (moves it to trash)."""
        try:
            self.service.users().messages().trash(
                userId=user_id,
                id=message_id
            ).execute()
        except HttpError as e:
            if e.resp.status == 404:
                raise MessageNotFoundError(f"Message with ID {message_id} not found for deletion.")
            raise EmailAPIError(f"Failed to delete message: {e}")

    def modify_labels(self, message_id: str, add_labels: list[str], remove_labels: list[str], user_id: str = 'me') -> None:
        """Add or remove labels from a message."""
        try:
            body = {
                'addLabelIds': add_labels,
                'removeLabelIds': remove_labels
            }
            self.service.users().messages().modify(
                userId=user_id,
                id=message_id,
                body=body
            ).execute()
        except HttpError as e:
            if e.resp.status == 404:
                raise MessageNotFoundError(f"Message with ID {message_id} not found for label modification.")
            raise EmailAPIError(f"Failed to modify message labels: {e}")
