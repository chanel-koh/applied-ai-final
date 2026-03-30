from datetime import datetime
from pawpal_system import Pet, Task


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
