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
        self.medications.append(med)

    def remove_medication(self, med: str) -> None:
        if med in self.medications:
            self.medications.remove(med)

    def add_feeding(self, feeding: str) -> None:
        self.feeding_schedule.append(feeding)

    def remove_feeding(self, feeding: str) -> None:
        if feeding in self.feeding_schedule:
            self.feeding_schedule.remove(feeding)

    def add_walking(self, walking: str) -> None:
        self.walking_schedule.append(walking)

    def remove_walking(self, walking: str) -> None:
        if walking in self.walking_schedule:
            self.walking_schedule.remove(walking)

    def get_medication_schedule(self) -> List[str]:
        return self.medications

    def get_feeding_schedule(self) -> List[str]:
        return self.feeding_schedule

    def get_walking_schedule(self) -> List[str]:
        return self.walking_schedule

@dataclass
class Task:
    pet: Pet
    description: str
    time: datetime
    frequency: str
    completed: bool = False

    def update_time(self, new_time: datetime) -> None:
        self.time = new_time

    def update_frequency(self, new_frequency: str) -> None:
        self.frequency = new_frequency

    def mark_completed(self) -> None:
        self.completed = True

class Owner:
    def __init__(self, name: str):
        self.name: str = name
        self.pets: List[Pet] = []
        self.scheduler: Scheduler = Scheduler()

    def add_pet(self, pet: Pet) -> None:
        self.pets.append(pet)

    def remove_pet(self, pet: Pet) -> None:
        if pet in self.pets:
            self.pets.remove(pet)

    def list_pets(self) -> List[Pet]:
        return self.pets

    def get_all_pet_tasks(self) -> List[Task]:
        all_tasks = []
        for pet in self.pets:
            all_tasks.extend(pet.tasks)
        return all_tasks

class Scheduler:
    def __init__(self):
        self.tasks: List[Task] = []

    def add_task(self, task: Task) -> None:
        self.tasks.append(task)

    def remove_task(self, task: Task) -> None:
        if task in self.tasks:
            self.tasks.remove(task)

    def get_daily_tasks(self, target_date: date) -> List[Task]:
        return [t for t in self.tasks if t.time.date() == target_date]

    def filter_tasks_by_completion(self, completed: bool) -> List[Task]:
        return [t for t in self.tasks if t.completed == completed]

    def get_next_task(self) -> Optional[Task]:
        if self.tasks:
            return min(self.tasks, key=lambda t: t.time)
        return None

    def get_all_tasks_from_owner_pets(self, owner: Owner) -> List[Task]:
        return owner.get_all_pet_tasks()
