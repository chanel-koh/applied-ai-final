from datetime import datetime, date, timedelta
from pawpal_system import Pet, Task, Scheduler, Owner


def test_mark_completed_sets_task_completed():
    pet = Pet(name="Buddy", breed="Golden Retriever", age=4, activity_level="high")
    task = Task(pet=pet, description="Walk the dog", time=datetime.now(), frequency="daily")
    assert task.completed is False

    task.mark_completed()

    assert task.completed is True


def test_add_task_to_pet_increases_task_count():
    pet = Pet(name="Whiskers", breed="Tabby", age=2, activity_level="low")
    assert len(pet.tasks) == 0

    task = Task(pet=pet, description="Feed cat", time=datetime.now(), frequency="daily")
    pet.tasks.append(task)

    assert len(pet.tasks) == 1


# ==================== SORTING CORRECTNESS TESTS ====================

def test_sort_tasks_by_time_ascending_order():
    """Happy path: Verify tasks are returned in chronological order (ascending)."""
    pet = Pet(name="Buddy", breed="Golden Retriever", age=4, activity_level="high")
    scheduler = Scheduler()
    
    # Create tasks at different times
    time_1 = datetime(2026, 3, 29, 8, 0)
    time_2 = datetime(2026, 3, 29, 14, 30)
    time_3 = datetime(2026, 3, 29, 18, 45)
    
    task_3 = Task(pet=pet, description="Evening walk", time=time_3, frequency="daily")
    task_1 = Task(pet=pet, description="Morning walk", time=time_1, frequency="daily")
    task_2 = Task(pet=pet, description="Afternoon walk", time=time_2, frequency="daily")
    
    scheduler.add_task(task_3)
    scheduler.add_task(task_1)
    scheduler.add_task(task_2)
    
    sorted_tasks = scheduler.sort_tasks_by_time()
    
    assert len(sorted_tasks) == 3
    assert sorted_tasks[0].time == time_1
    assert sorted_tasks[1].time == time_2
    assert sorted_tasks[2].time == time_3


def test_sort_tasks_empty_scheduler():
    """Edge case: Empty scheduler returns empty list."""
    scheduler = Scheduler()
    
    sorted_tasks = scheduler.sort_tasks_by_time()
    
    assert sorted_tasks == []


def test_sort_tasks_single_task():
    """Edge case: Single task sorted trivially."""
    pet = Pet(name="Max", breed="Poodle", age=3, activity_level="medium")
    scheduler = Scheduler()
    
    task = Task(pet=pet, description="Groom", time=datetime(2026, 3, 29, 10, 0), frequency="weekly")
    scheduler.add_task(task)
    
    sorted_tasks = scheduler.sort_tasks_by_time()
    
    assert len(sorted_tasks) == 1
    assert sorted_tasks[0] == task


def test_sort_tasks_same_time_multiple_tasks():
    """Edge case: Multiple tasks at exact same time remain in list."""
    pet1 = Pet(name="Buddy", breed="Golden Retriever", age=4, activity_level="high")
    pet2 = Pet(name="Whiskers", breed="Tabby", age=2, activity_level="low")
    scheduler = Scheduler()
    
    same_time = datetime(2026, 3, 29, 12, 0)
    task_1 = Task(pet=pet1, description="Walk dog", time=same_time, frequency="daily")
    task_2 = Task(pet=pet2, description="Feed cat", time=same_time, frequency="daily")
    
    scheduler.add_task(task_1)
    scheduler.add_task(task_2)
    
    sorted_tasks = scheduler.sort_tasks_by_time()
    
    assert len(sorted_tasks) == 2
    # Both have same time, so both should be in result
    assert all(t.time == same_time for t in sorted_tasks)


def test_sort_tasks_reverse_order():
    """Happy path: Reverse sort returns tasks in descending time order."""
    pet = Pet(name="Buddy", breed="Golden Retriever", age=4, activity_level="high")
    scheduler = Scheduler()
    
    time_1 = datetime(2026, 3, 29, 8, 0)
    time_2 = datetime(2026, 3, 29, 14, 30)
    time_3 = datetime(2026, 3, 29, 18, 45)
    
    task_1 = Task(pet=pet, description="Morning walk", time=time_1, frequency="daily")
    task_2 = Task(pet=pet, description="Afternoon walk", time=time_2, frequency="daily")
    task_3 = Task(pet=pet, description="Evening walk", time=time_3, frequency="daily")
    
    scheduler.add_task(task_1)
    scheduler.add_task(task_2)
    scheduler.add_task(task_3)
    
    sorted_tasks = scheduler.sort_tasks_by_time(reverse=True)
    
    assert sorted_tasks[0].time == time_3
    assert sorted_tasks[1].time == time_2
    assert sorted_tasks[2].time == time_1


def test_sort_tasks_ignores_date_sorts_by_time_only():
    """Edge case: Sorting by HH:MM only, not full datetime."""
    pet = Pet(name="Buddy", breed="Golden Retriever", age=4, activity_level="high")
    scheduler = Scheduler()
    
    # Same HH:MM but different dates
    time_1 = datetime(2026, 3, 28, 14, 30)  # March 28 at 14:30
    time_2 = datetime(2026, 3, 29, 14, 30)  # March 29 at 14:30
    
    task_1 = Task(pet=pet, description="Task 1", time=time_1, frequency="daily")
    task_2 = Task(pet=pet, description="Task 2", time=time_2, frequency="daily")
    
    scheduler.add_task(task_1)
    scheduler.add_task(task_2)
    
    sorted_tasks = scheduler.sort_tasks_by_time()
    
    # Should have both tasks (same HH:MM so order may vary, but both present)
    assert len(sorted_tasks) == 2


# ==================== RECURRENCE LOGIC TESTS ====================

def test_complete_daily_task_creates_next_day_occurrence():
    """Happy path: Completing a daily task creates a new task for the following day."""
    pet = Pet(name="Buddy", breed="Golden Retriever", age=4, activity_level="high")
    scheduler = Scheduler()
    
    current_time = datetime(2026, 3, 29, 9, 0)
    task = Task(pet=pet, description="Walk the dog", time=current_time, frequency="daily", is_recurring=False)
    
    pet.tasks.append(task)
    scheduler.add_task(task)
    
    initial_pet_task_count = len(pet.tasks)
    initial_scheduler_task_count = len(scheduler.tasks)
    
    scheduler.complete_task_and_schedule_next(task)
    
    # Original task should be marked complete
    assert task.completed is True
    
    # New task should be created
    assert len(pet.tasks) == initial_pet_task_count + 1
    assert len(scheduler.tasks) == initial_scheduler_task_count + 1
    
    # New task should be scheduled for next day
    new_task = pet.tasks[-1]
    assert new_task.time == current_time + timedelta(days=1)
    assert new_task.completed is False


def test_complete_weekly_task_creates_next_week_occurrence():
    """Happy path: Completing a weekly task creates a new task for the following week."""
    pet = Pet(name="Whiskers", breed="Tabby", age=2, activity_level="low")
    scheduler = Scheduler()
    
    current_time = datetime(2026, 3, 29, 10, 0)
    task = Task(pet=pet, description="Bathe cat", time=current_time, frequency="weekly", is_recurring=False)
    
    pet.tasks.append(task)
    scheduler.add_task(task)
    
    scheduler.complete_task_and_schedule_next(task)
    
    assert task.completed is True
    
    new_task = pet.tasks[-1]
    assert new_task.time == current_time + timedelta(days=7)
    assert new_task.frequency == "weekly"


def test_complete_non_recurring_task_no_next_task():
    """Edge case: Completing a non-recurring task does not create a new task."""
    pet = Pet(name="Buddy", breed="Golden Retriever", age=4, activity_level="high")
    scheduler = Scheduler()
    
    task = Task(pet=pet, description="Vet appointment", time=datetime(2026, 3, 29, 14, 0), frequency="once", is_recurring=False)
    
    pet.tasks.append(task)
    scheduler.add_task(task)
    
    initial_task_count = len(scheduler.tasks)
    
    scheduler.complete_task_and_schedule_next(task)
    
    assert task.completed is True
    assert len(scheduler.tasks) == initial_task_count  # No new task created


def test_complete_task_with_invalid_frequency():
    """Edge case: Task with frequency not in ['daily', 'weekly'] returns early."""
    pet = Pet(name="Max", breed="Poodle", age=3, activity_level="medium")
    scheduler = Scheduler()
    
    task = Task(pet=pet, description="Random task", time=datetime(2026, 3, 29, 15, 0), frequency="monthly", is_recurring=False)
    
    pet.tasks.append(task)
    scheduler.add_task(task)
    
    initial_task_count = len(scheduler.tasks)
    
    scheduler.complete_task_and_schedule_next(task)
    
    assert task.completed is True
    assert len(scheduler.tasks) == initial_task_count  # No new task created


def test_complete_task_frequency_case_insensitive():
    """Edge case: Frequency matching handles different cases (Daily, DAILY, etc.)."""
    pet = Pet(name="Buddy", breed="Golden Retriever", age=4, activity_level="high")
    scheduler = Scheduler()
    
    current_time = datetime(2026, 3, 29, 9, 0)
    # Note: Implementation uses .lower() so "Daily" should work
    task = Task(pet=pet, description="Walk", time=current_time, frequency="Daily", is_recurring=False)
    
    pet.tasks.append(task)
    scheduler.add_task(task)
    
    scheduler.complete_task_and_schedule_next(task)
    
    # Should create next occurrence since "Daily".lower() == "daily"
    assert len(pet.tasks) == 2
    assert pet.tasks[-1].time == current_time + timedelta(days=1)


# ==================== CONFLICT DETECTION TESTS ====================

def test_detect_time_conflicts_two_tasks_same_time():
    """Happy path: Scheduler detects when two tasks are at the same time."""
    pet1 = Pet(name="Buddy", breed="Golden Retriever", age=4, activity_level="high")
    pet2 = Pet(name="Whiskers", breed="Tabby", age=2, activity_level="low")
    scheduler = Scheduler()
    
    same_time = datetime(2026, 3, 29, 12, 0)
    task_1 = Task(pet=pet1, description="Walk dog", time=same_time, frequency="daily")
    task_2 = Task(pet=pet2, description="Feed cat", time=same_time, frequency="daily")
    
    scheduler.add_task(task_1)
    scheduler.add_task(task_2)
    
    conflicts = scheduler.detect_time_conflicts()
    
    assert len(conflicts) > 0
    assert any("Time conflict" in conflict for conflict in conflicts)
    assert any("Buddy" in conflict and "Walk dog" in conflict for conflict in conflicts)
    assert any("Whiskers" in conflict and "Feed cat" in conflict for conflict in conflicts)


def test_detect_time_conflicts_no_conflicts():
    """Edge case: No conflicts when all tasks have different times."""
    pet = Pet(name="Buddy", breed="Golden Retriever", age=4, activity_level="high")
    scheduler = Scheduler()
    
    task_1 = Task(pet=pet, description="Morning walk", time=datetime(2026, 3, 29, 8, 0), frequency="daily")
    task_2 = Task(pet=pet, description="Afternoon walk", time=datetime(2026, 3, 29, 14, 0), frequency="daily")
    task_3 = Task(pet=pet, description="Evening walk", time=datetime(2026, 3, 29, 18, 0), frequency="daily")
    
    scheduler.add_task(task_1)
    scheduler.add_task(task_2)
    scheduler.add_task(task_3)
    
    conflicts = scheduler.detect_time_conflicts()
    
    assert len(conflicts) == 0


def test_detect_time_conflicts_three_tasks_same_time():
    """Edge case: Three or more tasks at the same time all included in warning."""
    pet1 = Pet(name="Buddy", breed="Golden Retriever", age=4, activity_level="high")
    pet2 = Pet(name="Whiskers", breed="Tabby", age=2, activity_level="low")
    pet3 = Pet(name="Max", breed="Poodle", age=3, activity_level="medium")
    scheduler = Scheduler()
    
    same_time = datetime(2026, 3, 29, 12, 0)
    task_1 = Task(pet=pet1, description="Walk", time=same_time, frequency="daily")
    task_2 = Task(pet=pet2, description="Feed", time=same_time, frequency="daily")
    task_3 = Task(pet=pet3, description="Groom", time=same_time, frequency="daily")
    
    scheduler.add_task(task_1)
    scheduler.add_task(task_2)
    scheduler.add_task(task_3)
    
    conflicts = scheduler.detect_time_conflicts()
    
    assert len(conflicts) >= 1
    conflict_message = conflicts[0]
    # All three pets should be mentioned
    assert "Buddy" in conflict_message
    assert "Whiskers" in conflict_message
    assert "Max" in conflict_message


def test_detect_time_conflicts_empty_scheduler():
    """Edge case: Empty scheduler has no conflicts."""
    scheduler = Scheduler()
    
    conflicts = scheduler.detect_time_conflicts()
    
    assert len(conflicts) == 0


def test_detect_time_conflicts_single_task():
    """Edge case: Single task cannot conflict with itself."""
    pet = Pet(name="Buddy", breed="Golden Retriever", age=4, activity_level="high")
    scheduler = Scheduler()
    
    task = Task(pet=pet, description="Walk", time=datetime(2026, 3, 29, 12, 0), frequency="daily")
    scheduler.add_task(task)
    
    conflicts = scheduler.detect_time_conflicts()
    
    assert len(conflicts) == 0


def test_detect_time_conflicts_multiple_time_slots_some_conflicts():
    """Edge case: Multiple time slots with conflicts at some but not others."""
    pet1 = Pet(name="Buddy", breed="Golden Retriever", age=4, activity_level="high")
    pet2 = Pet(name="Whiskers", breed="Tabby", age=2, activity_level="low")
    pet3 = Pet(name="Max", breed="Poodle", age=3, activity_level="medium")
    scheduler = Scheduler()
    
    # Two tasks at 12:00
    task_1 = Task(pet=pet1, description="Walk", time=datetime(2026, 3, 29, 12, 0), frequency="daily")
    task_2 = Task(pet=pet2, description="Feed", time=datetime(2026, 3, 29, 12, 0), frequency="daily")
    
    # One task at 14:00 (no conflict)
    task_3 = Task(pet=pet3, description="Groom", time=datetime(2026, 3, 29, 14, 0), frequency="daily")
    
    scheduler.add_task(task_1)
    scheduler.add_task(task_2)
    scheduler.add_task(task_3)
    
    conflicts = scheduler.detect_time_conflicts()
    
    # Should have exactly 1 conflict (at 12:00)
    assert len(conflicts) == 1
    assert "12:00" in conflicts[0]
