"""Date and time utilities."""
from datetime import datetime


def format_date_readable(date_str: str) -> str:
    """Convert YYYY-MM-DD to readable format like '10 Nov.'"""
    try:
        date_obj = datetime.strptime(date_str, "%Y-%m-%d")
        return f"{date_obj.day} {date_obj.strftime('%b')}."
    except (ValueError, AttributeError):
        return date_str


def parse_iso_date(date_str: str) -> datetime:
    """Parse ISO format date string to datetime object."""
    try:
        return datetime.fromisoformat(date_str.replace('Z', '+00:00'))
    except (ValueError, AttributeError):
        return datetime.now()


def format_date_for_storage(date_obj: datetime) -> str:
    """Format datetime object to YYYY-MM-DD string."""
    return date_obj.strftime('%Y-%m-%d')

