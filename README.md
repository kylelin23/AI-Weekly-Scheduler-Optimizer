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
python main.py
```

This runs the greedy scheduler on the demo week defined in `main.py` and
prints a text-based weekly calendar plus any tasks that could not be scheduled.

## Files

| File | Purpose |
|------|---------|
| `models.py` | Core data types: `TimeSlot`, `FixedEvent`, `FlexibleTask`. |
| `slots.py` | Builds the week as discrete 10-minute time slots (8am–midnight, Mon–Sun). |
| `constraints.py` | Shared `DAYS` list and `is_slot_valid()` hard-constraint check. |
| `greedy.py` | Greedy baseline scheduler: fills first valid slots, ordered by priority then deadline. |
| `main.py` | Entry point with a sample week of fixed events and flexible tasks. |
| `docs/` | Project proposal. |

## Model

- **Time** is discretized into 10-minute `TimeSlot`s. Fixed events block slots;
  flexible tasks must claim enough free slots to cover their duration.
- **Hard constraints** (must hold): no overlap with fixed events or other tasks,
  finish before the deadline, stay within available hours.
- **Soft constraints** (preferences, scored): preferred days/times, priority
  ordering, daily workload — *planned, not yet implemented.*

## Status

- [x] Data model + time-slot representation
- [x] Greedy baseline scheduler with text output
- [ ] Soft-constraint scoring function
- [ ] Backtracking (CSP) scheduler with heuristics + forward checking
- [ ] Evaluation harness comparing greedy vs. CSP on easy/medium/hard weeks
