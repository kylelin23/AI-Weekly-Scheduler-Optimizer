from models import FixedEvent, FlexibleTask
from greedy import schedule_greedy, print_schedule
from backtracking import schedule_backtracking
from score import score_schedule, print_score

def main():
    fixed_events = [
        FixedEvent(name="Work", day="Mon", start=16*60, end=18*60), # 4-6pm
        FixedEvent(name="AI Class", day="Tue", start=15*60, end=18*60),# 3-6pm
        FixedEvent(name="AI Class", day="Thu", start=15*60, end=18*60), # 3-6pm
    ]

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
    print_schedule(greedy_result)
    greedy_scored = score_schedule(greedy_result, flexible_tasks)
    print_score(greedy_scored)

    print("\n" + "=" * 40)
    print("BACKTRACKING (CSP) SCHEDULER")
    print("=" * 40)
    bt_result = schedule_backtracking(fixed_events, flexible_tasks)
    print_schedule(bt_result)
    bt_scored = score_schedule(bt_result, flexible_tasks)
    print_score(bt_scored)

    print("\n" + "=" * 40)
    print("Greedy score: " + str(greedy_scored["total"]) +
          "   CSP score: " + str(bt_scored["total"]))

if __name__ == "__main__":
    main()