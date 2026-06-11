from models import FixedEvent, FlexibleTask
from greedy import schedule_greedy, print_schedule
from backtracking import schedule_backtracking
from score import score_schedule, print_score, configure_scoring
from explain import print_unscheduled_reasons
import argparse
from constraints import DAYS

def parse_hhmm(s):
    """
    Convert HH:MM format into integer minutes
    """
    h, m = s.split(":")
    minutes = int(h) * 60 + int(m)
    return minutes

def parse_fixed_event(s):
    """
    Format: "Name,Day,HH:MM,HH:MM"
    Example: "Gym,Mon,07:00,08:30"
    """
    parts = [p.strip() for p in s.split(",")]
    if len(parts) != 4:
        raise argparse.ArgumentTypeError(
            f"--fixed needs 4 comma-separated fields: Name,Day,Start,End  (got {s!r})"
        )
    name, day, start_str, end_str = parts
    if day not in DAYS:
        raise argparse.ArgumentTypeError(f"Day must be one of {DAYS}, got {day!r}")
    start = parse_hhmm(start_str)
    end   = parse_hhmm(end_str)
    if end <= start:
        raise argparse.ArgumentTypeError(f"End time must be after start time in {s!r}")
    return FixedEvent(name=name, day=day, start=start, end=end)

parser = argparse.ArgumentParser()

parser.add_argument(
    "--fixed", type=parse_fixed_event, action="append",
    default=[
        FixedEvent(name="Work", day="Mon", start=16*60, end=18*60), # 4-6pm
        FixedEvent(name="AI Class", day="Tue", start=15*60, end=18*60),# 3-6pm
        FixedEvent(name="AI Class", day="Thu", start=15*60, end=18*60), # 3-6pm
    ],
    metavar="NAME,DAY,START,END",
    help="Add a fixed event, e.g. \"Gym,Mon,07:00,08:00\". Repeatable.")

parser.add_argument(
    "--weight_scheduled", type=int, default=100, help="reward per scheduled task, scaled by priority")
parser.add_argument(
    "--preferred_day", type=int, default=20, help="task placed on a preferred day"
)
parser.add_argument(
    "--preferred_time", type=int, default=20, help="task placed inside its preferred time window"
)
parser.add_argument(
    "--priority_early", type=int, default=10, help="higher-priority tasks placed earlier in the week"
)
parser.add_argument(
    "--unscheduled", type=int, default=100, help="lost per unscheduled task, scaled by priority"
)
parser.add_argument(
    "--late_night", type=int, default=5, help="per slot scheduled after LATE_NIGHT_CUTOFF"
)
parser.add_argument(
    "--late_night_cutoff", type=int, default=21*60, help="time by minute where user stops working"
)

args = parser.parse_args()

def main():
    configure_scoring(args)
    
    fixed_events = args.fixed

    flexible_tasks = [
        FlexibleTask(
            name="Study for AI Exam",
            duration=180,
            deadline_day="Thu",
            deadline_time=20*60,
            priority=3,
            preferred_end=20*60
        ),
        FlexibleTask(
            name="Do Laundry",
            duration=60,
            deadline_day="Sun",
            deadline_time=22*60,
            priority=1,
            preferred_days=["Sat", "Sun"], # prefer to do chores on the weekend
        ),
        FlexibleTask(
            name="CSC 480 Project",
            duration=120,
            deadline_day="Fri",
            deadline_time=17*60,
            priority=2,
        ),
    ]

    print("=" * 40)
    print("GREEDY BASELINE")
    print("=" * 40)
    greedy_result = schedule_greedy(fixed_events, flexible_tasks)
    print_schedule(greedy_result, fixed_events)
    greedy_scored = score_schedule(greedy_result, flexible_tasks)
    print_score(greedy_scored)
    print_unscheduled_reasons(greedy_result, flexible_tasks, fixed_events)

    print("\n" + "=" * 40)
    print("BACKTRACKING (CSP) SCHEDULER")
    print("=" * 40)
    bt_result = schedule_backtracking(fixed_events, flexible_tasks)
    print_schedule(bt_result, fixed_events)
    bt_scored = score_schedule(bt_result, flexible_tasks)
    print_score(bt_scored)
    print_unscheduled_reasons(bt_result, flexible_tasks, fixed_events)

    print("\n" + "=" * 40)
    print("Greedy score: " + str(greedy_scored["total"]) +
          "   CSP score: " + str(bt_scored["total"]))

if __name__ == "__main__":
    main()