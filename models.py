from dataclasses import dataclass
from typing import Optional

@dataclass(frozen=True)
# Unit of time on calendar
# Will be slots of size 10 minutes
class TimeSlot:
    day: str
    start: int
    end: int

# Something that u have to do, such as class or work
# Ex: Work, Tuesday 2:00 PM-7:00 PM.
@dataclass
class FixedEvent:
    name: str
    day: str
    start: int
    end: int

# Something that u have to schedule, such as hanging out with friends or time for studying
# Ex: Study for AI exam, 3 hours total, due Thursday, high priority, preferably before 8:00 PM
@dataclass
class FlexibleTask:
    name: str
    duration: int
    deadline_day: str
    deadline_time: int
    priority: int

    preferred_days: Optional[list[str]] = None
    preferred_start: Optional[int] = None
    preferred_end: Optional[int] = None