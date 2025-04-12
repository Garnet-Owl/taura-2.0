"""Core utilities for tests."""

from enum import Enum, auto
import pytz
from datetime import datetime, timezone, timedelta


class AutoName(Enum):
    def _generate_next_value_(name, start, count, last_values):
        return name


class UTC:
    """UTC timezone for datetime objects."""

    @classmethod
    def now(cls, offset=None):
        """Get current UTC time with optional offset.

        Args:
            offset: Optional timezone offset in hours

        Returns:
            datetime: Current time in UTC with optional timezone adjustment
        """
        now = datetime.now(timezone.utc)

        if offset:
            timezone_str = f"Etc/GMT{'+' if offset < 0 else '-'}{abs(offset)}"
            timezone = pytz.timezone(timezone_str)
            loc_dt = now.astimezone(timezone)

            return loc_dt
        return now

    @classmethod
    def local_to_utc(cls, local_dt, offset):
        """Convert local time to UTC.

        Args:
            local_dt: Local datetime
            offset: Timezone offset in hours (can be negative)

        Returns:
            datetime: UTC time
        """
        if local_dt.tzinfo is not None:
            return local_dt.astimezone(timezone.utc)

        timezone_str = f"Etc/GMT{'+' if offset < 0 else '-'}{abs(offset)}"
        timezone = pytz.timezone(timezone_str)

        loc_dt = timezone.localize(local_dt)
        loc_dt = loc_dt.astimezone(timezone.utc)

        return loc_dt


def get_timestamp():
    """Get current timestamp in ISO format."""
    return datetime.now(timezone.utc).isoformat()


def get_timestamp_offset(offset_hours=0, offset_minutes=0):
    """Get timestamp with offset.

    Args:
        offset_hours: Hour offset (positive or negative)
        offset_minutes: Minute offset (positive or negative)
    """
    offset = timedelta(hours=offset_hours, minutes=offset_minutes)
    return (datetime.now(timezone.utc) + offset).isoformat()


def get_utc_timestamp():
    """Get UTC timestamp for tests."""
    return datetime.now(timezone.utc).isoformat()
