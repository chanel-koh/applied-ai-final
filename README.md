# PawPal+ (Module 2 Project)

Thsi project builds **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

This project workflow first designed the system (UML), then implemented the logic in Python, then connected it to Streamlit UI.

## What Was Built

This final app:

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

## Smarter Scheduling Features

### Chronological Schedule Sorting (`sort_tasks_by_time()`)
Tasks are sorted by their `HH:MM` time string using Python's built-in `sorted()` with a key function, ensuring the schedule always displays in chronological order regardless of insertion order. Supports both ascending and descending order.

### Time Conflict Detection (`detect_time_conflicts()`)
The scheduler groups tasks by their exact timestamp using a `defaultdict`, then scans for groups with more than one task. Any conflicts surface as human-readable warning messages (e.g., `"Time conflict at 2026-03-29 08:00: Mochi (Walk), Luna (Feeding)"`) displayed in the UI before the schedule renders.

### Automatic Task Recurrence on Completion (`complete_task_and_schedule_next()`)
Marking a `daily` or `weekly` task complete triggers the scheduler to calculate the next occurrence (`+1 day` or `+7 days`) and automatically create and append a new `Task` instance to both the pet's task list and the scheduler — so the next cycle is always ready without manual re-entry.

### Recurring Task Expansion (`expand_recurring_tasks()`)
Tasks can be flagged as recurring with a `recurrence_interval` (`timedelta`). The scheduler expands them into concrete, non-recurring instances across any given date range — useful for viewing a multi-day plan without duplicating source tasks.

### Multi-Criteria Filtering (`filter_tasks_by_completion_and_pet()`)
Tasks can be filtered by completion status alone or combined with a pet name, making it easy to view pending tasks for a specific pet.

### Next Task Lookup (`get_next_task()`)
`get_next_task()` returns the single soonest upcoming task using `min()` over the task list by time — an O(n) scan that's simple and correct for the expected dataset size.

### Testing PawPal+
To run tests, use ```python -m pytest```

Test coverage includes verification on the following:
    - Sorting correctness: tasks are returned in chronological order
    - Recurrence logic: marking a daily task complete creates a new task for the following day
    - Conflict dectection: Scheduler flags duplicate times

Here is the output of a successful test run:

```
============================= test session starts ==============================
platform darwin -- Python 3.13.5, pytest-9.0.3, pluggy-1.5.0 -- /opt/miniconda3/
bin/python
cachedir: .pytest_cache
rootdir: /Users/chanelk/Documents/extracurriculars/CodePath/AI110/week5_pawpal_show
plugins: anyio-4.13.0
collected 19 items                                                             

tests/test_pawpal.py::test_mark_completed_sets_task_completed PASSED     [  5%]
tests/test_pawpal.py::test_add_task_to_pet_increases_task_count PASSED   [ 10%]
tests/test_pawpal.py::test_sort_tasks_by_time_ascending_order PASSED     [ 15%]
tests/test_pawpal.py::test_sort_tasks_empty_scheduler PASSED             [ 21%]
tests/test_pawpal.py::test_sort_tasks_single_task PASSED                 [ 26%]
tests/test_pawpal.py::test_sort_tasks_same_time_multiple_tasks PASSED    [ 31%]
tests/test_pawpal.py::test_sort_tasks_reverse_order PASSED               [ 36%]
tests/test_pawpal.py::test_sort_tasks_ignores_date_sorts_by_time_only PASSED [ 42%]
tests/test_pawpal.py::test_complete_daily_task_creates_next_day_occurrence PASSED [ 47%]
tests/test_pawpal.py::test_complete_weekly_task_creates_next_week_occurrence PASSED [ 52%]
tests/test_pawpal.py::test_complete_non_recurring_task_no_next_task PASSED [ 57%]
tests/test_pawpal.py::test_complete_task_with_invalid_frequency PASSED   [ 63%]
tests/test_pawpal.py::test_complete_task_frequency_case_insensitive PASSED [ 68%]
tests/test_pawpal.py::test_detect_time_conflicts_two_tasks_same_time PASSED [ 73%]
tests/test_pawpal.py::test_detect_time_conflicts_no_conflicts PASSED     [ 78%]
tests/test_pawpal.py::test_detect_time_conflicts_three_tasks_same_time PASSED [ 84%]
tests/test_pawpal.py::test_detect_time_conflicts_empty_scheduler PASSED  [ 89%]
tests/test_pawpal.py::test_detect_time_conflicts_single_task PASSED      [ 94%]
tests/test_pawpal.py::test_detect_time_conflicts_multiple_time_slots_some_conflicts PASSED [100%]

============================== 19 passed in 0.02s ==============================
```

Confidence Level in system reliability based on test results: 5/5

## Sample Output
```
Tasks sorted by time (using sort_tasks_by_time):
  ✓ 08:00: Morning Walk for Buddy
  ○ 09:00: Medication for Buddy
  ✓ 10:30: Vet Appointment for Buddy
  ○ 12:00: Feeding for Whiskers
  ○ 14:00: Play Time for Whiskers
  ○ 18:00: Evening Walk for Buddy
```

## Demo Walkthrough

### Main UI Features and User Actions

PawPal+ provides an intuitive interface for managing pet care schedules:

**Owner & Pet Management:**
- Create an owner profile with a name
- Add multiple pets with details (name, breed, age, activity level)
- View all registered pets and their information

**Task Scheduling:**
- Add pet care tasks with:
  - Task title (e.g., "Morning Walk", "Feeding", "Medication")
  - Duration (in minutes)
  - Priority level (low, medium, high)
  - Specific date and time (HH:MM format)
  - Frequency (once, daily, weekly)
- Tasks are automatically assigned to a specific pet
- View and filter tasks by completion status and pet

**Schedule Viewing:**
- Display today's complete schedule in chronological order
- View all upcoming tasks with time conflicts highlighted
- Automatically reschedule recurring tasks when marked complete

### Example Workflow

Here's a typical user journey in PawPal+:

1. **Create Owner:** User "Alice" starts the app and creates her profile
2. **Add Pets:** Alice adds two pets:
   - Buddy (Golden Retriever, 3 years old, high activity level)
   - Whiskers (Cat, 2 years old, low activity level)
3. **Schedule Tasks:** Alice adds daily care tasks:
   - 08:00 - Morning Walk (Buddy)
   - 12:00 - Feeding (Whiskers)
   - 14:00 - Play Time (Whiskers)
   - 18:00 - Evening Walk (Buddy)
4. **View Schedule:** The scheduler automatically sorts all tasks chronologically
5. **Mark Complete:** Alice marks the morning walk complete → scheduler automatically creates tomorrow's morning walk task
6. **Check Conflicts:** When Alice tries to add a vet appointment and grooming session at the same time, the system warns her of the time conflict

### Key Scheduler Behaviors

**Chronological Sorting:** All tasks are automatically sorted by time (HH:MM format) regardless of insertion order, making it easy to see the day's timeline at a glance.

**Conflict Detection:** The scheduler automatically identifies when multiple tasks are scheduled at the exact same time and displays warning messages to help users avoid double-booking.

**Automatic Rescheduling:** When a user marks a daily or weekly task as complete, the system:
- Marks the original task as done (✓ indicator)
- Calculates the next occurrence (+1 day for daily, +7 days for weekly)
- Automatically creates a new task instance for the next cycle

**Multi-Criteria Filtering:** Tasks can be filtered by:
- Completion status alone (show all pending or completed tasks)
- Combined filters (show only incomplete tasks for a specific pet)

**Recurring Task Expansion:** Tasks flagged as recurring are expanded into concrete instances across any date range, allowing users to preview multiple days of care needs at once.

### Sample CLI Output

Running `main.py` demonstrates the core scheduling features:

```
=== DEMONSTRATING SORTING AND FILTERING METHODS ===

1. Tasks sorted by time (using sort_tasks_by_time):
  ✓ 08:00: Morning Walk for Buddy
  ○ 09:00: Medication for Buddy
  ✓ 10:30: Vet Appointment for Buddy
  ○ 12:00: Feeding for Whiskers
  ○ 14:00: Play Time for Whiskers
  ○ 18:00: Evening Walk for Buddy

2. Filtering by completion status and pet:
   Completed tasks for Buddy:
     ✓ 08:00: Morning Walk
     ✓ 10:30: Vet Appointment
   Incomplete tasks for Whiskers:
     ○ 12:00: Feeding
     ○ 14:00: Play Time

3. Recurring task expansion for next 3 days:
     2026-06-13 09:00: Medication
     2026-06-14 09:00: Medication
     2026-06-15 09:00: Medication

4. Today's schedule (original method):
  ✓ 08:00: Morning Walk for Buddy
  ○ 09:00: Medication for Buddy
  ✓ 10:30: Vet Appointment for Buddy
  ○ 12:00: Feeding for Whiskers
  ○ 14:00: Play Time for Whiskers
  ○ 18:00: Evening Walk for Buddy

5. Demonstrating automatic task completion and rescheduling:
   Before completing the evening walk:
     ○ 18:00: Evening Walk (completed: False)
   Completing the evening walk and scheduling next occurrence...
   After completion:
     ✓ 18:00: Evening Walk (completed: True)
     New tasks in scheduler:
       ✓ 2026-06-13 18:00: Evening Walk (completed: True)
       ○ 2026-06-14 18:00: Evening Walk (completed: False)

6. Demonstrating conflict detection:
   Adding two tasks at the same time (11:00 AM)...
   Checking for time conflicts...
Conflicts detected:
     Time conflict at 2026-06-13 11:00: Buddy (Grooming Session), Whiskers (Vet Check)
```

