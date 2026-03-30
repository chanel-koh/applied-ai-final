# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.

### Smarter Scheduling
There are currently four major algorithmic features: sorting by time, multi-criteria filtering, automatic task rescheduling on completion, and conflict detection. Sorting by time displays tasks in chronological order in a HH:MM format, regardless of insertion order. Multi-criteria filtering allows a user to sort by completed tasks and by pet. Automatic task rescheduling on completion checks if the task is marked complete and if frequency is "daily" or "weekly", calculates the next occurrence of a task, then creates a new task instance for the next cycle and adds it to a scheduler. Lastly, conflict detection identifies tasks with the same HH:MM and generates a warning message about the conflict.

### Testing PawPal+
To run tests, use ```python -m pytest```

Test coverage includes verification on the following:
    - Sorting correctness: tasks are returned in chronological order
    - Recurrence logic: marking a daily task complete creates a new task for the following day
    - Conflict dectection: Scheduler flags duplicate times

Confidence Level in system reliability based on test results: 5/5
