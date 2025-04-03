import datetime
from enum import Enum

import pytz


class AutoName(Enum):
    def _generate_next_value_(name, start, count, last_values):
        return name


class Clock:
    clock_instance = None

    def get_now(self) -> datetime.datetime:
        return datetime.datetime.utcnow()

    def now(self) -> datetime.datetime:
        return datetime.datetime.utcnow()

    def get_local_now(self, timezone: datetime.tzinfo) -> datetime.datetime:
        now = self.get_now()

        now = pytz.utc.localize(now)
        loc_dt = now.astimezone(timezone)

        return loc_dt

    @classmethod
    def set_clock(cls, clock) -> "Clock":
        cls.clock_instance = clock

    @classmethod
    def retrieve(cls):
        if cls.clock_instance is None:
            cls.clock_instance = Clock()

        return cls.clock_instance

    def get_start_of_day_for(self, timezone: datetime.timezone):
        now = self.get_now()

        now = pytz.utc.localize(now)
        loc_dt: datetime.datetime = now.astimezone(timezone)
        loc_dt = loc_dt.replace(hour=0, minute=0, second=0, microsecond=0)
        loc_dt = loc_dt.astimezone(timezone.utc)

        return loc_dt


class MockClock(Clock):
    def __init__(self, current_time=None):
        if current_time is None:
            self.time = datetime.datetime.utcnow()
        else:
            self.time = current_time

        self.original_time = self.time
        Clock.clock_instance = self

    def apply_delta(self, delta: datetime.timedelta):
        self.time = self.time + delta

    def set_time(self, time):
        self.time = time

    def get_now(self):
        return self.time

    def now(self):
        return self.time
