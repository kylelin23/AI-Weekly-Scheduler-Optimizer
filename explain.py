from models import FixedEvent, FlexibleTask
from slots import create_time_slots
from constraints import get_blocked_slots
from backtracking import build_domain
from greedy import format_time

AVAIL_START = 8 * 60
AVAIL_END = 22 * 60


def format_duration(minutes: int) -> str:
    hours = minutes // 60
    mins = minutes % 60
    if hours and mins:
        return str(hours) + "h" + str(mins) + "m"
    if hours:
        return str(hours) + "h"
    return str(mins) + "m"


# Explain, in plain English, why a flexible task ended up unscheduled.
#
# We rebuild the task's domain considering ONLY the fixed events (i.e. on an
# otherwise empty calendar). If even then no valid block exists, the task is
# intrinsically infeasible -- we report the binding hard constraint. If a block
# *does* exist on the empty calendar, the task was simply crowded out by the
# other tasks that got scheduled first.
def diagnose_unscheduled(
    task: FlexibleTask,
    fixed_events: list[FixedEvent],
    availability_start: int = AVAIL_START,
    availability_end: int = AVAIL_END,
) -> str:
    all_slots = create_time_slots()
    slot_index = {(s.day, s.start): s for s in all_slots}
    blocked_fixed = get_blocked_slots(fixed_events, all_slots)

    domain = build_domain(task, slot_index, blocked_fixed, availability_start, availability_end)

    if domain:
        return ("no free " + format_duration(task.duration)
                + " block remained before its " + task.deadline_day + " "
                + format_time(task.deadline_time) + " deadline -- other tasks took the time first")

    # Intrinsically infeasible: identify the binding constraint.
    daily_available = availability_end - availability_start
    if task.duration > daily_available:
        return ("needs " + format_duration(task.duration) + " in one day, but only "
                + format_duration(daily_available) + " is available per day (tasks are not split across days)")

    return ("no " + format_duration(task.duration) + " block fits before its "
            + task.deadline_day + " " + format_time(task.deadline_time)
            + " deadline within available hours")


# Print the unscheduled tasks of a result with a reason for each.
def print_unscheduled_reasons(
    result: dict,
    flexible_tasks: list[FlexibleTask],
    fixed_events: list[FixedEvent],
    availability_start: int = AVAIL_START,
    availability_end: int = AVAIL_END,
):
    if not result["unscheduled"]:
        return
    by_name = {t.name: t for t in flexible_tasks}
    print("\nUnscheduled tasks:")
    for name in result["unscheduled"]:
        reason = diagnose_unscheduled(by_name[name], fixed_events, availability_start, availability_end)
        print("  " + name + ": " + reason)
