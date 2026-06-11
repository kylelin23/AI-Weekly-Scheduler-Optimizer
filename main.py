import argparse, re
from models import FixedEvent, FlexibleTask
from greedy import schedule_greedy, print_schedule
from backtracking import schedule_backtracking
from score import score_schedule, print_score, configure_scoring
from explain import print_unscheduled_reasons
from constraints import DAYS
from evaluation import count_violations, easy_week, medium_week, hard_week, evaluate

week_dict = {}
for week in [easy_week, medium_week, hard_week]:
    label, fixed, tasks, full_exists = week()
    week_dict[label] = [fixed, tasks]

def week_resolver(s):
    return week_dict[s]

def parse_days(value):
    value = value.strip()

    if value.startswith("[") and value.endswith("]"):
        inner = value[1:-1]
        return [day.strip() for day in inner.split(",") if day.strip()]

    return value

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

def parser_flexible_event(s):
    parts = re.split(r',(?![^\[]*\])', s)
    parts = [p.strip() for p in parts]

    if len(parts) < 5 or len(parts) > 8:
        raise argparse.ArgumentTypeError("--flexible needs 5-8 arguments")

    name = parts[0]
    duration = parse_hhmm(parts[1])
    deadline_day = parts[2]
    deadline_time = parse_hhmm(parts[3])
    priority = int(parts[4])

    kwargs = {
        "name": name,
        "duration": duration,
        "deadline_day": deadline_day,
        "deadline_time": deadline_time,
        "priority": priority,
    }

    if len(parts) >= 6:
        value = parse_days(parts[5])

        if isinstance(value, list):
            kwargs["preferred_days"] = value
        else:
            kwargs["preferred_start"] = parse_hhmm(value)

    if len(parts) >= 7:
        if isinstance(parts[5], list):
            kwargs["preferred_start"] = parse_hhmm(parts[6])
        else:
            kwargs["preferred_end"] = parse_hhmm(parts[6])

    if len(parts) == 8:
        kwargs["preferred_end"] = parse_hhmm(parts[7])

    return FlexibleTask(**kwargs)
    
parser = argparse.ArgumentParser()

parser.add_argument(
    "--week", type=week_resolver, 
    default=[[
        FixedEvent(name="Work", day="Mon", start=16*60, end=18*60), # 4-6pm
        FixedEvent(name="AI Class", day="Tue", start=15*60, end=18*60),# 3-6pm
        FixedEvent(name="AI Class", day="Thu", start=15*60, end=18*60), # 3-6pm
    ], [
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
    ]],
    help="Choose week from created weeks"
)

parser.add_argument(
    "--fixed", type=parse_fixed_event, action="append",
    default=[],
    metavar="NAME,DAY,START,END",
    help="Add a fixed event, e.g. \"Gym,Mon,07:00,08:00\". Repeatable."
)
    #   --fixed "Gym,Mon,07:00,10:00"

parser.add_argument(
    "--flexible", type=parser_flexible_event, action="append",
    default=[],
    metavar="NAME,DURATION,DEADLINE_DAY,DEADLINE_TIME,PRIORITY",
    help="Add a flexible event"
)

parser.add_argument(
    "--weight_scheduled", type=int, default=100, help="reward per scheduled task, scaled by priority"
)
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
    
    fixed_events = args.week[0] + args.fixed

    flexible_tasks = args.week[1] + args.flexible

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