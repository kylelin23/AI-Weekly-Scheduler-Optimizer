---
marp: false
theme: gaia
paginate: true
header: "AI Weekly Schedule Optimizer"
footer: "CSC 480 Final Project"
---

<!-- _class: lead -->
<!-- _paginate: false -->

# AI Weekly Schedule Optimizer

### Planning a week as search + constraint satisfaction

CSC 480 Final Project

<!--
Hi everyone. Our project is an AI scheduling assistant that builds a weekly plan
automatically. The key idea: we don't just *store* a calendar, we *reason* about
how the week should be organized under constraints. I'll walk through the problem,
the two approaches we built, and the evidence that the AI approach actually wins.
-->

---

## The Problem

- People juggle **fixed commitments** (work, classes) and **flexible tasks**
  (study, chores, projects)
- Flexible tasks have a **duration, deadline, priority,** and **preferences**
- Planning by hand is hard: many tasks, competing deadlines, limited time
- A normal calendar app *stores* events — it doesn't *decide where things go*

<!--
Everyone has fixed stuff that can't move, and flexible stuff that has to happen
sometime. The hard part is the flexible stuff: where do you actually put it so
everything fits before its deadline? A calendar app won't answer that for you —
you do it in your head. We wanted the computer to do that reasoning.
-->

---

## The AI Connection

We model the week as a **constraint-satisfaction problem (CSP):**

- The week is a grid of discrete **time slots**
- Each flexible task is a **variable** — its values are possible placements
- We **search** for an assignment that satisfies hard constraints...
- ...and **optimizes** soft preferences

> The system searches over many possible assignments, detects conflicts,
> backtracks, and compares schedules with a scoring function.

<!--
This maps directly onto search and CSP from class. Time becomes a grid of slots,
each task is a variable, and a placement is a value. Some assignments are illegal
(conflicts), so we search and backtrack. Among the legal ones, some are better
than others, so we score them. That's the whole framing.
-->

---

## How Time Is Modeled

- The week → **10-minute slots**, Mon–Sun, 8 AM to midnight
- **Fixed events** permanently block their slots
- **Flexible tasks** must claim enough free slots to cover their duration

**Why 10 minutes?** Fine enough to be realistic, coarse enough to keep the
search space small → *"plan my week"* becomes a **finite search problem.**

<!--
We chop the week into ten-minute slots. Why ten? It's the sweet spot — granular
enough to place real tasks sensibly, but coarse enough that the number of possible
placements stays manageable to search. Fixed events black out their slots up
front; flexible tasks grab enough free slots to cover their duration. Once time is
discrete and finite, it's something we can actually search over.
-->

---

## The Rules: Hard Constraints

A schedule is **only valid** if every task:

- does **not overlap** a fixed event or another flexible task
- finishes **before its deadline**
- stays **within available hours** (8 AM – 10 PM)

Both schedulers call the **same** `is_slot_valid()` check — identical rulebook.

<!--
Hard constraints are non-negotiable — break one and the schedule is invalid.
No double-booking, nothing past its deadline, nothing outside available hours.
Important design point: we centralized this into one shared function, so both of
our schedulers obey exactly the same rules. That makes the comparison fair.
-->

---

## What Makes a Schedule *Good*: Soft Constraints

We **score** valid schedules on preferences (points are tunable):

| Reward | pts | Penalty | pts |
|--------|----:|---------|----:|
| Scheduled (× priority) | +100 | Left unscheduled | −100 |
| On a preferred day | +20 | Late-night slot | −5 |
| In a preferred time window | +20 | | |
| High priority placed early | +10 | | |

<!--
Beyond just "is it legal," we ask "is it good." The scoring function rewards
hitting your preferred days and times, doing high-priority work early, and
penalizes late nights and dropped tasks. Crucially, every number comes with a
reason string, so the system can explain *why* it placed something where it did.
-->

---

## Approach 1: Greedy Baseline

- Sort tasks by **priority, then deadline**
- Drop each into the **earliest open valid slots**
- Very fast and simple but short sighted

Issue: Never reconsiders, ends up having all tasks in one day when the tasks could be done in multiple days instead

<!--
Our baseline is greedy: sort by priority and deadline, then jam each task into
the first slots that fit. It's fast and it's a fair "naive calendar-filling"
comparison point. But it never backtracks. So it can box itself into a corner —
grab time for an important task, then discover a tight-deadline task has nowhere
left to go. Hold that thought; it shows up in our results.
-->

---

## Approach 2: Backtracking CSP Scheduler

The "AI" centerpiece. Each task is a variable; its domain is every legal
**contiguous block**, plus a **"skip"** option.

Real CSP techniques:

- **Most-constrained-first** variable ordering
- **Best-score-first** value ordering
- **Branch-and-bound** pruning

Because it can **undo** bad early choices, it finds schedules greedy misses.

> **Guarantee:** it returns the **highest-scoring valid schedule** it can build —
> or, if everything can't fit, reports exactly which tasks it left out.

<!--
The smart scheduler is a backtracking search with the heuristics from class.
It handles the most constrained task first, tries the most promising slot first,
and prunes any branch that can't beat the best schedule found so far. The key
difference from greedy: it can undo a decision. So it finds valid schedules greedy
can't, and among all valid options it returns the best-scoring one.
-->

---

## Explaining Failures

When a task can't be scheduled, we say **why** — in plain English:

- **Intrinsically impossible**
  *"needs 20h in one day, but only 14h is available per day"*
- **Crowded out**
  *"no free 2h block remained before its Mon 10 PM deadline —
  other tasks took the time first"*

<!--
A good planner shouldn't just fail silently. When a task can't fit, we diagnose
why. Either it's genuinely impossible — too long, or the deadline's too tight —
or it got crowded out, meaning it *could* have fit on an empty calendar but other
tasks took the time first. That second case is exactly greedy's failure mode.
-->

---

## Evaluation: How We Tested

- **Three weeks** of increasing difficulty: easy, medium, **hard**
- The **hard** week is engineered so a full valid schedule *exists*,
  but greedy boxes itself in
- An **independent validator** re-audits every output for rule violations
  — we don't just trust the schedulers

<!--
To prove the point, we run both schedulers on three weeks from easy to hard. The
hard one is deliberately a trap for greedy: a valid full schedule exists, but only
if you backtrack. And we don't take the schedulers' word that they followed the
rules — a separate validator re-checks every output for violations.
-->

---

## Live Demo

```bash
python evaluation.py    # run both schedulers on all three test weeks
```

```
HARD WEEK   (a full valid schedule exists)
Scheduler Scheduled  Violations  Score   Time(ms)
Greedy    2/3        0           450     0.57
CSP       3/3        0           660     6.64
  Greedy dropped Tight Errand: no free 2h block remained
    before its Mon 10:00 deadline -- other tasks took the time first
```

<!--
Rather than just tell you, let me show you. I'll run the evaluation script — it
runs both schedulers on all three weeks. Watch the hard week: greedy schedules
two of three and tells us exactly why it dropped the third, while the CSP
scheduler fits all three. (If running live: switch to terminal, run the command,
then come back to the summary table.)
-->

---

## Results

| Week | Greedy | CSP | Outcome |
|------|--------|-----|---------|
| Easy | 2/2 · 330 | 2/2 · **342** | CSP wins on preferences |
| Medium | 3/3 · 680 | 3/3 · **692** | CSP wins on preferences |
| **Hard** | **2/3** · 450 | **3/3** · **660** | **Greedy fails; CSP fits all (+210)** |

- **0** hard-constraint violations anywhere
- Runtimes in **single-digit milliseconds**

<!--
Here's the payoff. On easy and medium, both schedule everything, but the CSP
scheduler scores higher because it respects preferences. On the hard week, greedy
drops a task entirely — two of three — while the CSP scheduler fits all three for
a 210-point gain. Zero violations across the board, and it all runs in
milliseconds. That's the proposal's claim, demonstrated.
-->

---

## The Hard Week, Step by Step

- "Tight Errand" can **only** go Mon 8–10 (deadline Mon 10 AM)
- Greedy schedules higher-priority tasks first → grabs Mon 8–10
- → "Tight Errand" has **nowhere to go** 
- CSP recognizes the conflict, moves the big tasks, **reserves Mon 8–10** 

<!--
Let me make the hard week concrete. There's a low-priority errand that can only
happen Monday 8 to 10 because of its deadline. Greedy, going by priority, fills
that exact window with bigger tasks first — and then the errand is stuck. The CSP
scheduler sees that the big tasks can go elsewhere, so it reserves Monday morning
for the errand. Same inputs, but backtracking finds the schedule greedy can't.
-->

---

## Architecture

| Module | Responsibility |
|--------|----------------|
| `models` · `slots` | Data types & the time grid |
| `constraints` | Shared hard-constraint rules |
| `greedy` | Baseline scheduler |
| `backtracking` | CSP scheduler |
| `score` | Soft-constraint scoring |
| `explain` | Why a task was dropped |
| `evaluation` | Benchmark suite + validator |

<!--
Quick tour of the code. Clean separation: data and the grid, one shared rulebook,
the two schedulers, the scorer, the failure-explainer, and the evaluation harness.
The shared constraints module is what keeps the comparison honest — both
schedulers play by the same rules.
-->

---

## Design Choices

- **Contiguous block per day** — a task runs in one sitting (e.g. a 3-hour study
  block), which is more realistic than scattering 10-minute fragments
- **Hand-tuned weights** — transparent and explainable; every point is traceable
- **Skip option** — when not everything fits, it degrades gracefully and *reports*
  what it dropped instead of failing

*Each is a deliberate trade-off — and a clean hook for future work.*

<!--
These were intentional decisions, not oversights. Keeping a task in one
contiguous block matches how people actually work — you study for three hours, you
don't do six five-minute bursts. Hand-tuned weights keep the scoring transparent:
we can explain every point. And the skip option means it never crashes on an
impossible week — it tells you what it couldn't fit. Each choice also opens a
natural next step, which leads into future work.
-->

---

<!-- _class: lead -->

## Takeaways

**Search + CSP + heuristics** turn a messy planning chore into a
**solvable, optimizable** problem.

We didn't just *claim* the AI approach is better — we **measured it:**

-  Schedules **more tasks** (3/3 vs 2/3 on the hard week)
-  Respects **more preferences** (higher score every week)
-  **Zero** rule violations, verified independently

### Thank you.

<!--
To wrap up: framing weekly planning as search and constraint satisfaction let us
build something that genuinely reasons about your week. And the headline is that
we measured it, we didn't just assert it — more tasks scheduled, more preferences
respected, zero violations, every week. Thanks. (Then pause — if the prof wants
questions, they'll ask; you don't need to invite them.)
-->
