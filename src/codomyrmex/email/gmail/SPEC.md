# Google Mail Specification

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: February 2026

## Design Considerations

The `GmailProvider` class provides a translation layer between the `google-api-python-client` DTOs and the system's `EmailMessage` models.

## Behavior

- Automatically parses naive date strings from incoming payload headers into aware UTC `datetime` objects.
- Normalizes base64 `urlsafe` decoded `text/plain` and `text/html` parts.
- Uses standard Python `email.message.EmailMessage` internally to convert drafted raw byte payloads for outgoing mail requests.
- Traps `googleapiclient.errors.HttpError` exceptions and normalizes them into `EmailAPIError` or `MessageNotFoundError`.
