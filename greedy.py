from models import TimeSlot, FixedEvent, FlexibleTask
from slots import create_time_slots
from constraints import DAYS, is_slot_valid

# Create set of blocked slots
def get_blocked_slots(fixed_events: list[FixedEvent], all_slots: list[TimeSlot]) -> set[TimeSlot]:
    blocked = set()
    for slot in all_slots:
        for event in fixed_events:
            if slot.day == event.day and slot.start >= event.start and slot.end <= event.end:
                blocked.add(slot)
    return blocked

# Create the schedule
# Returns a dictionary
# First entry is schedule
# Second entry is unscheduled events
def schedule_greedy(
    fixed_events: list[FixedEvent],
    flexible_tasks: list[FlexibleTask],
    availability_start: int = 8 * 60,
    availability_end: int = 22 * 60,
) -> dict:

    all_slots = create_time_slots() # create weekly slots
    blocked = get_blocked_slots(fixed_events, all_slots) # get the blocked slots from fixed events

    # Sort the flexible tasks by priority
    sorted_tasks = sorted(
        flexible_tasks,
        key=lambda t: (-t.priority, DAYS.index(t.deadline_day))
    )

    schedule = {} # return value
    unscheduled = [] # will hold tasks we can't schedule

    for task in sorted_tasks:
        slots_needed = task.duration // 10 # get number of slots needed bc we have 10 minute slots
        assigned = [] # will contain slots we use

        for slot in all_slots: # Goes through every slot in the week
            if len(assigned) == slots_needed: # We got through all the tasks
                break
            if not is_slot_valid(slot, task, blocked, availability_start, availability_end):
                continue

            assigned.append(slot)
            blocked.add(slot)

        if len(assigned) == slots_needed:
            schedule[task.name] = assigned
        else:
            unscheduled.append(task.name)

    return {"schedule": schedule, "unscheduled": unscheduled}

# Formatting the schedule and printing it
def print_schedule(result: dict):
    for day in DAYS:
        print("\n" + day + ":")

        for task_name, slots in result["schedule"].items():
            day_slots = []
            for s in slots:
                if s.day == day:
                    day_slots.append(s)

            if day_slots:
                start = min(s.start for s in day_slots)
                end = max(s.end for s in day_slots)
                start_hour = str(start // 60)
                start_min = str(start % 60).zfill(2) # use zfill for formatting
                end_hour = str(end // 60)
                end_min = str(end % 60).zfill(2)
                print("  " + task_name + ": " + start_hour + ":" + start_min + " - " + end_hour + ":" + end_min)

    if result["unscheduled"]:
        print("\nUnscheduled: " + ", ".join(result["unscheduled"]))