# Google Calendar Specification

## Design Considerations

The `GoogleCalendar` class provides a translation layer between the `google-api-python-client` DTOs and the system's `CalendarEvent` models.

## Behavior

- Automatically adjusts naive dates from incoming payloads (e.g. all-day `date` representations vs `dateTime`).
- Traps `googleapiclient.errors.HttpError` exceptions and normalizes them into `CalendarAPIError` or `EventNotFoundError`.
