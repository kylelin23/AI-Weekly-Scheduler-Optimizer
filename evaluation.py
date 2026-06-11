import time

from models import FixedEvent, FlexibleTask
from constraints import DAYS
from greedy import schedule_greedy
from backtracking import schedule_backtracking
from score import score_schedule
from explain import diagnose_unscheduled

AVAIL_START = 8 * 60   # 8:00 AM
AVAIL_END = 22 * 60    # 10:00 PM


# Independently audit a produced schedule for HARD-constraint violations.
# The schedulers are supposed to never produce these; this is the check that
# proves it. Returns the number of violating placements found.
def count_violations(
    result: dict,
    fixed_events: list[FixedEvent],
    flexible_tasks: list[FlexibleTask],
    availability_start: int = AVAIL_START,
    availability_end: int = AVAIL_END,
) -> int:
    by_name = {t.name: t for t in flexible_tasks}
    violations = 0
    used = {}  # (day, start) -> task name, to catch task/task overlaps

    for name, slots in result["schedule"].items():
        task = by_name[name]

        # Must receive enough total scheduled time.
        if sum(s.end - s.start for s in slots) < task.duration:
            violations += 1

        for s in slots:
            # Must stay within available hours.
            if s.start < availability_start or s.end > availability_end:
                violations += 1

            # Must finish on or before the deadline.
            if DAYS.index(s.day) > DAYS.index(task.deadline_day):
                violations += 1
            elif s.day == task.deadline_day and s.end > task.deadline_time:
                violations += 1

            # Must not overlap another task.
            key = (s.day, s.start)
            if key in used:
                violations += 1
            else:
                used[key] = name

            # Must not overlap a fixed event.
            for e in fixed_events:
                if s.day == e.day and s.start < e.end and s.end > e.start:
                    violations += 1

    return violations


# --- Test weeks -------------------------------------------------------------
# Each returns (label, fixed_events, flexible_tasks, full_schedule_exists).
# full_schedule_exists marks weeks where every task CAN be scheduled validly,
# so we can measure "finds a valid schedule when one exists."

def easy_week():
    # Wide-open week: a couple of small tasks, almost no fixed commitments.
    fixed = [
        FixedEvent(name="Work", day="Wed", start=16 * 60, end=18 * 60),
    ]
    tasks = [
        FlexibleTask(name="Read Chapter", duration=60, deadline_day="Fri", deadline_time=22 * 60, priority=2),
        FlexibleTask(name="Workout", duration=60, deadline_day="Sat", deadline_time=22 * 60, priority=1,
                     preferred_days=["Sat"]),
    ]
    return "EASY", fixed, tasks, True


def medium_week():
    # Several fixed commitments; everything still fits, but preferences differ,
    # so the CSP scheduler should out-score greedy on soft constraints.
    fixed = [
        FixedEvent(name="Work", day="Mon", start=16 * 60, end=18 * 60),
        FixedEvent(name="AI Class", day="Tue", start=15 * 60, end=18 * 60),
        FixedEvent(name="AI Class", day="Thu", start=15 * 60, end=18 * 60),
    ]
    tasks = [
        FlexibleTask(name="Study for AI Exam", duration=180, deadline_day="Thu", deadline_time=20 * 60,
                     priority=3, preferred_end=20 * 60),
        FlexibleTask(name="Do Laundry", duration=60, deadline_day="Sun", deadline_time=22 * 60,
                     priority=1, preferred_days=["Sat", "Sun"]),
        FlexibleTask(name="CSC 480 Project", duration=120, deadline_day="Fri", deadline_time=17 * 60,
                     priority=2),
    ]
    return "MEDIUM", fixed, tasks, True


def hard_week():
    # The corner case. "Tight Errand" can ONLY go Mon 8:00-10:00 (deadline Mon
    # 10am). Greedy schedules the higher-priority tasks first, grabs those exact
    # slots, and is then forced to leave Tight Errand unscheduled -- even though
    # a full valid schedule exists (move the big tasks, reserve Mon 8-10 for the
    # errand). Backtracking finds it.
    fixed = [
        FixedEvent(name="Work", day="Mon", start=16 * 60, end=18 * 60),
        FixedEvent(name="AI Class", day="Tue", start=15 * 60, end=18 * 60),
    ]
    tasks = [
        FlexibleTask(name="Tight Errand", duration=120, deadline_day="Mon", deadline_time=10 * 60, priority=1),
        FlexibleTask(name="Study", duration=120, deadline_day="Fri", deadline_time=22 * 60, priority=3),
        FlexibleTask(name="Project", duration=120, deadline_day="Wed", deadline_time=22 * 60, priority=2),
    ]
    return "HARD", fixed, tasks, True


WEEKS = [easy_week, medium_week, hard_week]


# Run one scheduler on one week and gather metrics.
def evaluate(scheduler, fixed, tasks):
    start = time.perf_counter()
    result = scheduler(fixed, tasks)
    runtime_ms = (time.perf_counter() - start) * 1000

    scheduled = len(result["schedule"])
    violations = count_violations(result, fixed, tasks)
    total_score = score_schedule(result, tasks)["total"]
    return {
        "scheduled": scheduled,
        "total_tasks": len(tasks),
        "violations": violations,
        "score": total_score,
        "runtime_ms": runtime_ms,
        "unscheduled": result["unscheduled"],
    }


def _row(label, m):
    return (
        label.ljust(10)
        + (str(m["scheduled"]) + "/" + str(m["total_tasks"])).ljust(11)
        + str(m["violations"]).ljust(12)
        + str(m["score"]).ljust(8)
        + ("%.3f" % m["runtime_ms"])
    )


def main():
    for week in WEEKS:
        label, fixed, tasks, full_exists = week()

        g = evaluate(schedule_greedy, fixed, tasks)
        b = evaluate(schedule_backtracking, fixed, tasks)

        print("=" * 56)
        print(label + " WEEK" + ("   (a full valid schedule exists)" if full_exists else ""))
        print("=" * 56)
        print("Scheduler ".ljust(10) + "Scheduled".ljust(11) + "Violations".ljust(12) + "Score".ljust(8) + "Time(ms)")
        print(_row("Greedy", g))
        print(_row("CSP", b))

        for name in g["unscheduled"]:
            task = next(t for t in tasks if t.name == name)
            print("  Greedy dropped " + name + ": " + diagnose_unscheduled(task, fixed))
        for name in b["unscheduled"]:
            task = next(t for t in tasks if t.name == name)
            print("  CSP dropped " + name + ": " + diagnose_unscheduled(task, fixed))

        # Headline takeaways.
        if b["scheduled"] > g["scheduled"]:
            print("  -> CSP scheduled more tasks than greedy.")
        if b["score"] > g["score"]:
            print("  -> CSP found a higher-scoring schedule (+" + str(b["score"] - g["score"]) + ").")
        print()


if __name__ == "__main__":
    main()
