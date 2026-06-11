# AI Weekly Schedule Optimizer

CSC 480 final project. An AI-based weekly scheduling assistant that places
**flexible tasks** (homework, studying, chores) around **fixed events**
(classes, work shifts) while respecting deadlines, priorities, availability,
and personal preferences.

The project treats weekly planning as a **search / constraint-satisfaction
problem** and compares a simple greedy baseline against a smarter
constraint-based scheduler.

## Running

Requires Python 3.10+ (uses `list[...]` / `X | None` style type hints).

```bash
python main.py        # run both schedulers on the demo week and compare scores
python evaluation.py  # run the easy/medium/hard benchmark suite
```

`main.py` runs both schedulers on the demo week and prints a text-based weekly
calendar, a soft-constraint score breakdown, and any unscheduled tasks.
`evaluation.py` runs the benchmark suite comparing the two approaches.

## Files

| File | Purpose |
|------|---------|
| `models.py` | Core data types: `TimeSlot`, `FixedEvent`, `FlexibleTask`. |
| `slots.py` | Builds the week as discrete 10-minute time slots (8am–midnight, Mon–Sun). |
| `constraints.py` | Shared `DAYS` list and `is_slot_valid()` hard-constraint check. |
| `greedy.py` | Greedy baseline scheduler: fills first valid slots, ordered by priority then deadline. |
| `backtracking.py` | Constraint-based scheduler: backtracking search with most-constrained-first ordering, best-score-first values, and branch-and-bound pruning. Maximizes the soft-constraint score. |
| `score.py` | Soft-constraint scoring: ranks valid schedules by preference satisfaction, with a per-task breakdown. |
| `explain.py` | Diagnoses *why* a task was left unscheduled (intrinsically infeasible vs. crowded out). |
| `evaluation.py` | Evaluation harness: runs both schedulers on easy/medium/hard test weeks, audits hard-constraint violations, and prints a metrics comparison. |
| `main.py` | Entry point: runs both schedulers on a sample week and compares their scores. |
| `docs/` | Project proposal. |

## Model

- **Time** is discretized into 10-minute `TimeSlot`s. Fixed events block slots;
  flexible tasks must claim enough free slots to cover their duration.
- **Hard constraints** (must hold): no overlap with fixed events or other tasks,
  finish before the deadline, stay within available hours.
- **Soft constraints** (preferences, scored): preferred days/times and priority
  ordering, with late-night and unscheduled penalties.

## Status

- [x] Data model + time-slot representation
- [x] Greedy baseline scheduler with text output
- [x] Soft-constraint scoring function
- [x] Backtracking (CSP) scheduler with heuristics + branch-and-bound
- [x] Evaluation harness comparing greedy vs. CSP on easy/medium/hard weeks
- [x] Output polish: score breakdown + plain-English reasons for unscheduled tasks
