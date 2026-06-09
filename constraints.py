from models import TimeSlot, FixedEvent, FlexibleTask

# Days of the week, in order. Index is used to compare which day comes first.
DAYS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]

# Set of slots occupied by fixed events, which therefore cannot hold any task.
def get_blocked_slots(fixed_events: list[FixedEvent], all_slots: list[TimeSlot]) -> set[TimeSlot]:
    blocked = set()
    for slot in all_slots:
        for event in fixed_events:
            if slot.day == event.day and slot.start >= event.start and slot.end <= event.end:
                blocked.add(slot)
    return blocked

# Hard-constraint check for a single slot against a single task.
# Returns True if the slot is a legal place to put part of this task.
# Shared by the greedy scheduler and the backtracking (CSP) scheduler.
def is_slot_valid(
    slot: TimeSlot,
    task: FlexibleTask,
    blocked: set[TimeSlot],
    availability_start: int,
    availability_end: int,
) -> bool:
    if slot in blocked: # slot is already taken
        return False
    if slot.start < availability_start or slot.end > availability_end: # outside available hours
        return False
    if DAYS.index(slot.day) > DAYS.index(task.deadline_day): # slot is after the deadline day
        return False
    if slot.day == task.deadline_day and slot.end > task.deadline_time: # on deadline day but past the time
        return False
    return True
