from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime, date, timedelta
from typing import List, Optional
from collections import defaultdict

@dataclass
class Pet:
    name: str
    breed: str
    age: int
    activity_level: str
    medications: List[str] = field(default_factory=list)
    feeding_schedule: List[str] = field(default_factory=list)
    walking_schedule: List[str] = field(default_factory=list)
    tasks: List[Task] = field(default_factory=list)

    def add_medication(self, med: str) -> None:
        """Add a medication to the pet."""
        self.medications.append(med)

    def remove_medication(self, med: str) -> None:
        """Remove a medication from the pet if it exists."""
        if med in self.medications:
            self.medications.remove(med)

    def add_feeding(self, feeding: str) -> None:
        """Add a feeding schedule entry."""
        self.feeding_schedule.append(feeding)

    def remove_feeding(self, feeding: str) -> None:
        """Remove a feeding schedule entry if present."""
        if feeding in self.feeding_schedule:
            self.feeding_schedule.remove(feeding)

    def add_walking(self, walking: str) -> None:
        """Add a walking schedule entry."""
        self.walking_schedule.append(walking)

    def remove_walking(self, walking: str) -> None:
        """Remove a walking schedule entry if present."""
        if walking in self.walking_schedule:
            self.walking_schedule.remove(walking)

    def get_medication_schedule(self) -> List[str]:
        """Return the medication schedule."""
        return self.medications

    def get_feeding_schedule(self) -> List[str]:
        """Return the feeding schedule."""
        return self.feeding_schedule

    def get_walking_schedule(self) -> List[str]:
        """Return the walking schedule."""
        return self.walking_schedule

@dataclass
class Task:
    pet: Pet
    description: str
    time: datetime
    frequency: str
    completed: bool = False
    is_recurring: bool = False
    recurrence_interval: Optional[timedelta] = None

    def update_time(self, new_time: datetime) -> None:
        """Update the scheduled time for the task."""
        self.time = new_time

    def update_frequency(self, new_frequency: str) -> None:
        """Update the execution frequency for the task."""
        self.frequency = new_frequency

    def mark_completed(self) -> None:
        """Mark this task as completed."""
        self.completed = True

    def get_next_occurrences(self, start_date: datetime, count: int = 5) -> List[datetime]:
        """Generate next N occurrence dates for recurring tasks."""
        if not self.is_recurring or not self.recurrence_interval:
            return [self.time] if self.time >= start_date else []
        
        occurrences = []
        current = self.time
        while len(occurrences) < count and current >= start_date:
            if current >= start_date:
                occurrences.append(current)
            current += self.recurrence_interval
        
        return occurrences

class Owner:
    def __init__(self, name: str):
        self.name: str = name
        self.pets: List[Pet] = []
        self.scheduler: Scheduler = Scheduler()

    def add_pet(self, pet: Pet) -> None:
        """Add a pet to the owner."""
        self.pets.append(pet)

    def remove_pet(self, pet: Pet) -> None:
        """Remove a pet from the owner if present."""
        if pet in self.pets:
            self.pets.remove(pet)

    def list_pets(self) -> List[Pet]:
        """Return the owner's list of pets."""
        return self.pets

    def get_all_pet_tasks(self) -> List[Task]:
        """Collect tasks from all owned pets."""
        all_tasks = []
        for pet in self.pets:
            all_tasks.extend(pet.tasks)
        return all_tasks

class Scheduler:
    def __init__(self):
        self.tasks: List[Task] = []

    def add_task(self, task: Task) -> None:
        """Add a task to the scheduler."""
        self.tasks.append(task)

    def remove_task(self, task: Task) -> None:
        """Remove a task from the scheduler if it exists."""
        if task in self.tasks:
            self.tasks.remove(task)

    def get_daily_tasks(self, target_date: date) -> List[Task]:
        """Return tasks scheduled for a specific date."""
        return [t for t in self.tasks if t.time.date() == target_date]

    def filter_tasks_by_completion(self, completed: bool) -> List[Task]:
        """Return tasks that match completion status."""
        return [t for t in self.tasks if t.completed == completed]

    def get_next_task(self) -> Optional[Task]:
        """Get the next upcoming task by time."""
        if self.tasks:
            return min(self.tasks, key=lambda t: t.time)
        return None

    def sort_tasks_by_time(self, tasks: List[Task] = None, reverse: bool = False) -> List[Task]:
        """Sort tasks by time in HH:MM format. If no tasks provided, sort all scheduler tasks."""
        task_list = tasks or self.tasks
        return sorted(task_list, key=lambda t: t.time.strftime("%H:%M"), reverse=reverse)

    def filter_tasks_by_completion_and_pet(self, completed: bool, pet_name: str) -> List[Task]:
        """Filter tasks by both completion status and pet name."""
        return [t for t in self.tasks if t.completed == completed and t.pet.name == pet_name]

    def expand_recurring_tasks(self, start_date: date, end_date: date) -> List[Task]:
        """Generate concrete task instances from recurring tasks within date range."""
        expanded_tasks = []
        
        for task in self.tasks:
            if task.is_recurring and task.recurrence_interval:
                occurrences = task.get_next_occurrences(
                    datetime.combine(start_date, datetime.min.time()),
                    count=30  # reasonable limit to prevent infinite loops
                )
                
                for occurrence in occurrences:
                    if start_date <= occurrence.date() <= end_date:
                        # Create a new task instance for this occurrence
                        new_task = Task(
                            pet=task.pet,
                            description=task.description,
                            time=occurrence,
                            frequency=task.frequency,
                            is_recurring=False,  # concrete instances are not recurring
                            recurrence_interval=None
                        )
                        expanded_tasks.append(new_task)
            else:
                # Non-recurring task
                if start_date <= task.time.date() <= end_date:
                    expanded_tasks.append(task)
        
        return expanded_tasks

    def get_tasks_for_date_range(self, start_date: date, end_date: date) -> List[Task]:
        """Get all tasks (including expanded recurring ones) for a date range."""
        return self.expand_recurring_tasks(start_date, end_date)

    def create_recurring_task(self, pet: Pet, description: str, time: datetime, 
                            frequency: str, interval: timedelta) -> Task:
        """Create and add a recurring task to the scheduler."""
        task = Task(
            pet=pet,
            description=description,
            time=time,
            frequency=frequency,
            is_recurring=True,
            recurrence_interval=interval
        )
        self.add_task(task)
        return task

    def complete_task_and_schedule_next(self, task: Task) -> None:
        """Mark a task as completed and automatically schedule the next occurrence for recurring tasks."""
        task.mark_completed()
        
        # Check if this is a recurring task that needs a follow-up
        if task.frequency.lower() in ["daily", "weekly"]:
            # Calculate next occurrence
            if task.frequency.lower() == "daily":
                next_time = task.time + timedelta(days=1)
            elif task.frequency.lower() == "weekly":
                next_time = task.time + timedelta(days=7)
            else:
                return  # Should not reach here
            
            # Create new task instance for next occurrence
            next_task = Task(
                pet=task.pet,
                description=task.description,
                time=next_time,
                frequency=task.frequency,
                completed=False,
                is_recurring=False,  # Individual instances aren't recurring themselves
                recurrence_interval=None
            )
            
            # Add the new task to both the pet and scheduler
            task.pet.tasks.append(next_task)
            self.add_task(next_task)

    def get_all_tasks_from_owner_pets(self, owner: Owner) -> List[Task]:
        """Retrieve tasks from an Owner through owner task aggregation."""
        return owner.get_all_pet_tasks()

    def detect_time_conflicts(self) -> List[str]:
        """Detect tasks scheduled at the same time and return warning messages.
        
        Returns a list of warning strings for any time conflicts found.
        Uses defaultdict for cleaner grouping and list comprehension for concise warnings.
        """
        time_groups = defaultdict(list)
        
        # Group tasks by their exact time
        for task in self.tasks:
            time_groups[task.time].append(task)
        
        # Generate warnings for conflicts using list comprehension
        return [
            f"Time conflict at {time_key.strftime('%Y-%m-%d %H:%M')}: "
            f"{', '.join(f'{task.pet.name} ({task.description})' for task in tasks_at_time)}"
            for time_key, tasks_at_time in time_groups.items()
            if len(tasks_at_time) > 1
        ]
