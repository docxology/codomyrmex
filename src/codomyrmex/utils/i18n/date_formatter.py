"""Locale-aware date and time formatting."""

from datetime import datetime, date

from .models import Locale


class DateFormatter:
    """Locale-aware date and time formatting."""

    # Format patterns per locale
    FORMATS = {
        "en": {"date": "%m/%d/%Y", "time": "%I:%M %p", "datetime": "%m/%d/%Y %I:%M %p"},
        "de": {"date": "%d.%m.%Y", "time": "%H:%M", "datetime": "%d.%m.%Y %H:%M"},
        "fr": {"date": "%d/%m/%Y", "time": "%H:%M", "datetime": "%d/%m/%Y %H:%M"},
        "es": {"date": "%d/%m/%Y", "time": "%H:%M", "datetime": "%d/%m/%Y %H:%M"},
        "ja": {"date": "%Y/%m/%d", "time": "%H:%M", "datetime": "%Y/%m/%d %H:%M"},
    }

    @classmethod
    def format_date(cls, locale: Locale, d: date) -> str:
        """Format date for locale."""
        fmt = cls.FORMATS.get(locale.language, cls.FORMATS["en"])
        return d.strftime(fmt["date"])

    @classmethod
    def format_time(cls, locale: Locale, dt: datetime) -> str:
        """Format time for locale."""
        fmt = cls.FORMATS.get(locale.language, cls.FORMATS["en"])
        return dt.strftime(fmt["time"])

    @classmethod
    def format_datetime(cls, locale: Locale, dt: datetime) -> str:
        """Format datetime for locale."""
        fmt = cls.FORMATS.get(locale.language, cls.FORMATS["en"])
        return dt.strftime(fmt["datetime"])

    @classmethod
    def relative_time(cls, dt: datetime, now: datetime = None) -> str:
        """Human-readable relative time: 'just now', '5 minutes ago', '2 hours ago', 'yesterday', '3 days ago'."""
        if now is None:
            now = datetime.now()
        diff = now - dt
        seconds = int(diff.total_seconds())
        if seconds < 60:
            return "just now"
        minutes = seconds // 60
        if minutes < 60:
            return f"{minutes} minute{'s' if minutes != 1 else ''} ago"
        hours = minutes // 60
        if hours < 24:
            return f"{hours} hour{'s' if hours != 1 else ''} ago"
        days = hours // 24
        if days == 1:
            return "yesterday"
        return f"{days} days ago"
