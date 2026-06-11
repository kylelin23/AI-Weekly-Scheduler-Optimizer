from models import TimeSlot, FlexibleTask
from constraints import DAYS

WEIGHT_SCHEDULED = 100
WEIGHT_PREFERRED_DAY = 20
WEIGHT_PREFERRED_TIME = 20
WEIGHT_PRIORITY_EARLY = 10
PENALTY_UNSCHEDULED = 100
PENALTY_LATE_NIGHT = 5
LATE_NIGHT_CUTOFF = 21 * 60

# Scoring weights for the SOFT constraints.
#
# Hard constraints (no overlap, deadlines, availability) are enforced by the
# scheduler itself -- a schedule that violates them is never produced. This
# module only ranks *valid* schedules by how well they satisfy preferences,
# so the constraint-based scheduler can search for a higher-scoring schedule
# than the greedy baseline.

def configure_scoring(args):
    global WEIGHT_SCHEDULED
    global WEIGHT_PREFERRED_DAY
    global WEIGHT_PREFERRED_TIME
    global WEIGHT_PRIORITY_EARLY
    global PENALTY_UNSCHEDULED
    global PENALTY_LATE_NIGHT
    global LATE_NIGHT_CUTOFF

    WEIGHT_SCHEDULED = args.weight_scheduled
    WEIGHT_PREFERRED_DAY = args.preferred_day
    WEIGHT_PREFERRED_TIME = args.preferred_time
    WEIGHT_PRIORITY_EARLY = args.priority_early
    PENALTY_UNSCHEDULED = args.unscheduled
    PENALTY_LATE_NIGHT = args.late_night
    LATE_NIGHT_CUTOFF = args.late_night_cutoff

# Score a single scheduled task against its preferences.
# Returns (points, reasons) where reasons explains each contribution.
def score_task(task: FlexibleTask, slots: list[TimeSlot]) -> tuple[int, list[str]]:
    reasons = []
    score = 0
    n = len(slots)

    # 1. Reward for being scheduled at all, scaled by priority.
    base = WEIGHT_SCHEDULED * task.priority
    score += base
    reasons.append("+" + str(base) + " scheduled (priority " + str(task.priority) + ")")

    # 2. Preferred days: credit proportional to how many slots land on one.
    if task.preferred_days:
        on_pref = sum(1 for s in slots if s.day in task.preferred_days)
        pts = round(WEIGHT_PREFERRED_DAY * on_pref / n)
        score += pts
        reasons.append("+" + str(pts) + " preferred day (" + str(on_pref) + "/" + str(n) + " slots)")

    # 3. Preferred time window: credit proportional to slots inside it.
    if task.preferred_start is not None or task.preferred_end is not None:
        lo = task.preferred_start if task.preferred_start is not None else 0
        hi = task.preferred_end if task.preferred_end is not None else 24 * 60
        in_window = sum(1 for s in slots if s.start >= lo and s.end <= hi)
        pts = round(WEIGHT_PREFERRED_TIME * in_window / n)
        score += pts
        reasons.append("+" + str(pts) + " preferred time (" + str(in_window) + "/" + str(n) + " slots)")

    # 4. Higher-priority tasks should be scheduled earlier in the week.
    earliest = min(DAYS.index(s.day) for s in slots)
    earliness = (len(DAYS) - 1 - earliest) / (len(DAYS) - 1)  # 1.0 on Mon ... 0.0 on Sun
    pts = round(WEIGHT_PRIORITY_EARLY * task.priority * earliness)
    score += pts
    reasons.append("+" + str(pts) + " priority placed early (" + DAYS[earliest] + ")")

    # 5. Penalize late-night slots.
    late = sum(1 for s in slots if s.start >= LATE_NIGHT_CUTOFF)
    if late:
        pen = PENALTY_LATE_NIGHT * late
        score -= pen
        reasons.append("-" + str(pen) + " late-night slots (" + str(late) + ")")

    return score, reasons


# Score a whole schedule (the dict returned by a scheduler).
# Returns {"total": int, "breakdown": {task_name: {"score": int, "reasons": [...]}}}.
def score_schedule(result: dict, flexible_tasks: list[FlexibleTask]) -> dict:
    by_name = {t.name: t for t in flexible_tasks}
    total = 0
    breakdown = {}

    for name, slots in result["schedule"].items():
        pts, reasons = score_task(by_name[name], slots)
        total += pts
        breakdown[name] = {"score": pts, "reasons": reasons}

    for name in result["unscheduled"]:
        task = by_name[name]
        pen = PENALTY_UNSCHEDULED * task.priority
        total -= pen
        breakdown[name] = {
            "score": -pen,
            "reasons": ["-" + str(pen) + " unscheduled (priority " + str(task.priority) + ")"],
        }

    return {"total": total, "breakdown": breakdown}


# Print a schedule's score with a per-task breakdown.
def print_score(scored: dict):
    print("\nSchedule score: " + str(scored["total"]))
    for name, info in scored["breakdown"].items():
        print("  " + name + ": " + str(info["score"]))
        for reason in info["reasons"]:
            print("    " + reason)
