from pawpal_system import Pet, Task, Owner
from datetime import datetime, date

# Create owner
owner = Owner("Alice")

# Create pets
pet1 = Pet("Buddy", "Golden Retriever", 3, "High")
pet2 = Pet("Whiskers", "Cat", 2, "Low")

# Add pets to owner
owner.add_pet(pet1)
owner.add_pet(pet2)

# Create tasks with different times
now = datetime.now()
task1 = Task(pet1, "Morning Walk", now.replace(hour=8, minute=0), "daily")
task2 = Task(pet1, "Vet Appointment", now.replace(hour=10, minute=30), "monthly")
task3 = Task(pet2, "Feeding", now.replace(hour=12, minute=0), "daily")

# Add tasks to pets
pet1.tasks.append(task1)
pet1.tasks.append(task2)
pet2.tasks.append(task3)

# Add tasks to scheduler
owner.scheduler.add_task(task1)
owner.scheduler.add_task(task2)
owner.scheduler.add_task(task3)

# Get today's schedule
today = date.today()
tasks_today = owner.scheduler.get_daily_tasks(today)

# Print Today's Schedule
print("Today's Schedule")
for task in sorted(tasks_today, key=lambda t: t.time):
    print(f"{task.time.strftime('%H:%M')}: {task.description} ({task.frequency}) for {task.pet.name}")
