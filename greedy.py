from models import TimeSlot, FixedEvent, FlexibleTask
from slots import create_time_slots
from constraints import DAYS, is_slot_valid, get_blocked_slots

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
def format_time(minutes: int) -> str:
    return str(minutes // 60) + ":" + str(minutes % 60).zfill(2)

def print_schedule(result: dict, fixed_events: list[FixedEvent] = None):
    if fixed_events is None:
        fixed_events = []

    for day in DAYS:
        print("\n" + day + ":")

        # Print fixed events first
        for event in fixed_events:
            if event.day == day:
                print(
                    "  " + event.name + " (fixed): "
                    + format_time(event.start)
                    + " - "
                    + format_time(event.end)
                )

        # Print scheduled flexible tasks
        for task_name, slots in result["schedule"].items():
            day_slots = [s for s in slots if s.day == day]

            if day_slots:
                start = min(s.start for s in day_slots)
                end = max(s.end for s in day_slots)
                print(
                    "  " + task_name + ": "
                    + format_time(start)
                    + " - "
                    + format_time(end)
                )

    if result["unscheduled"]:
        print("\nUnscheduled: " + ", ".join(result["unscheduled"]))