from models import FixedEvent, FlexibleTask
from greedy import schedule_greedy, print_schedule
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

    result = schedule_greedy(fixed_events, flexible_tasks)
    print_schedule(result)

    scored = score_schedule(result, flexible_tasks)
    print_score(scored)

if __name__ == "__main__":
    main()