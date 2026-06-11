from models import TimeSlot, FixedEvent, FlexibleTask
from slots import create_time_slots
from constraints import DAYS, is_slot_valid, get_blocked_slots
import score
from score import score_task

# Backtracking / constraint-satisfaction scheduler.
#
# Each flexible task is a variable. Its domain is every CONTIGUOUS block of
# slots (same day) that satisfies the hard constraints, plus a "skip" option
# that leaves the task unscheduled. We search for the assignment that maximizes
# the soft-constraint score (see score.py), using:
#   - most-constrained-first variable ordering (fewest legal placements first),
#   - best-score-first value ordering (try the most promising block first),
#   - branch-and-bound pruning with an optimistic upper bound.
#
# Unlike the greedy baseline, this can undo an early placement that would block
# a more valuable task later, so it finds valid schedules greedy misses and
# never scores worse than greedy on the same inputs.


# Every contiguous, hard-constraint-valid block where this task could go.
# Returns (score, block) pairs sorted best-score-first.
def build_domain(
    task: FlexibleTask,
    slot_index: dict,
    blocked_fixed: set,
    availability_start: int,
    availability_end: int,
) -> list[tuple[int, list[TimeSlot]]]:
    slots_needed = task.duration // 10
    placements = []

    for day in DAYS:
        start = availability_start
        # A block must fit entirely within availability on a single day.
        while start + task.duration <= availability_end:
            block = []
            valid = True
            minute = start
            for _ in range(slots_needed):
                slot = slot_index.get((day, minute))
                if slot is None or not is_slot_valid(slot, task, blocked_fixed, availability_start, availability_end):
                    valid = False
                    break
                block.append(slot)
                minute += 10
            if valid:
                placements.append((score_task(task, block)[0], block))
            start += 10

    placements.sort(key=lambda pair: -pair[0]) # best score first
    return placements


def schedule_backtracking(
    fixed_events: list[FixedEvent],
    flexible_tasks: list[FlexibleTask],
    availability_start: int = 8 * 60,
    availability_end: int = 22 * 60,
) -> dict:

    all_slots = create_time_slots()
    slot_index = {(s.day, s.start): s for s in all_slots}
    blocked_fixed = get_blocked_slots(fixed_events, all_slots)

    domains = {}
    for task in flexible_tasks:
        domains[task.name] = build_domain(task, slot_index, blocked_fixed, availability_start, availability_end)

    # Variable ordering heuristic: most constrained first (smallest domain),
    # then earliest deadline, then highest priority.
    order = sorted(
        flexible_tasks,
        key=lambda t: (len(domains[t.name]), DAYS.index(t.deadline_day), -t.priority),
    )

    # Best score each remaining task could contribute on its own (ignoring
    # conflicts) -- scheduling its top block, or skipping if it has no block.
    # Used to build an optimistic upper bound for branch-and-bound pruning.
    # Read score.PENALTY_UNSCHEDULED via the module so CLI weight overrides
    # (configure_scoring) are picked up -- a bare import would bind the value
    # at import time and miss later changes.
    skip_score = {t.name: -score.PENALTY_UNSCHEDULED * t.priority for t in flexible_tasks}
    best_possible = {}
    for t in flexible_tasks:
        placements = domains[t.name]
        best_possible[t.name] = max(placements[0][0], skip_score[t.name]) if placements else skip_score[t.name]

    # suffix_bound[i] = optimistic best total achievable from order[i:] onward.
    suffix_bound = [0] * (len(order) + 1)
    for i in range(len(order) - 1, -1, -1):
        suffix_bound[i] = suffix_bound[i + 1] + best_possible[order[i].name]

    best = {"total": None, "assignment": None, "unscheduled": None}

    def search(index: int, occupied: set, assignment: dict, unscheduled: list, running: int):
        if index == len(order):
            if best["total"] is None or running > best["total"]:
                best["total"] = running
                best["assignment"] = dict(assignment)
                best["unscheduled"] = list(unscheduled)
            return

        # Branch-and-bound: if even the optimistic remainder can't beat the best
        # complete schedule found so far, abandon this branch.
        if best["total"] is not None and running + suffix_bound[index] <= best["total"]:
            return

        task = order[index]

        # Try placing the task, best-scoring block first.
        for block_score, block in domains[task.name]:
            if any(slot in occupied for slot in block):
                continue
            occupied.update(block)
            assignment[task.name] = block
            search(index + 1, occupied, assignment, unscheduled, running + block_score)
            del assignment[task.name]
            occupied.difference_update(block)

        # Try leaving the task unscheduled.
        unscheduled.append(task.name)
        search(index + 1, occupied, assignment, unscheduled, running + skip_score[task.name])
        unscheduled.pop()

    search(0, set(blocked_fixed), {}, [], 0)

    return {
        "schedule": best["assignment"],
        "unscheduled": best["unscheduled"],
        "score": best["total"],
    }
