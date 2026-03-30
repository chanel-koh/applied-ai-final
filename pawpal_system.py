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

    def add_medication(self, med: str) -> None:
        pass

    def remove_medication(self, med: str) -> None:
        pass

    def get_medication_schedule(self) -> List[str]:
        pass

    def get_feeding_schedule(self) -> List[str]:
        pass

    def get_walking_schedule(self) -> List[str]:
        pass

@dataclass
class Task:
    pet: Pet
    title: str
    time: datetime
    location: str
    priority: int

    def update_time(self, new_time: datetime) -> None:
        pass

    def update_location(self, new_location: str) -> None:
        pass

    def set_priority(self, new_priority: int) -> None:
        pass

class Owner:
    def __init__(self, name: str):
        self.name: str = name
        self.pets: List[Pet] = []

    def add_pet(self, pet: Pet) -> None:
        pass

    def remove_pet(self, pet: Pet) -> None:
        pass

    def list_pets(self) -> List[Pet]:
        pass

class Scheduler:
    def __init__(self):
        self.tasks: List[Task] = []

    def add_task(self, task: Task) -> None:
        pass

    def remove_task(self, task: Task) -> None:
        pass

    def get_daily_tasks(self, target_date: date) -> List[Task]:
        pass

    def filter_tasks_by_priority(self, priority: int) -> List[Task]:
        pass

    def get_next_task(self) -> Optional[Task]:
        pass
