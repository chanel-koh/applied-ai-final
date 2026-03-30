from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime, date
from typing import List, Optional

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

    def update_time(self, new_time: datetime) -> None:
        """Update the scheduled time for the task."""
        self.time = new_time

    def update_frequency(self, new_frequency: str) -> None:
        """Update the execution frequency for the task."""
        self.frequency = new_frequency

    def mark_completed(self) -> None:
        """Mark this task as completed."""
        self.completed = True

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

    def get_all_tasks_from_owner_pets(self, owner: Owner) -> List[Task]:
        """Retrieve tasks from an Owner through owner task aggregation."""
        return owner.get_all_pet_tasks()
