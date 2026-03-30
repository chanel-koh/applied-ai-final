from pawpal_system import Pet, Task, Owner
from datetime import datetime, date, timedelta

# Create owner
owner = Owner("Alice")

# Create pets
pet1 = Pet("Buddy", "Golden Retriever", 3, "High")
pet2 = Pet("Whiskers", "Cat", 2, "Low")

# Add pets to owner
owner.add_pet(pet1)
owner.add_pet(pet2)

# Create tasks OUT OF ORDER to demonstrate sorting
now = datetime.now()
task1 = Task(pet1, "Evening Walk", now.replace(hour=18, minute=0), "daily")  # 6:00 PM
task2 = Task(pet1, "Morning Walk", now.replace(hour=8, minute=0), "daily")   # 8:00 AM
task3 = Task(pet2, "Feeding", now.replace(hour=12, minute=0), "daily")       # 12:00 PM
task4 = Task(pet1, "Vet Appointment", now.replace(hour=10, minute=30), "monthly")  # 10:30 AM
task5 = Task(pet2, "Play Time", now.replace(hour=14, minute=0), "daily")     # 2:00 PM

# Mark some tasks as completed to demonstrate filtering
task2.completed = True  # Morning walk is done
task4.completed = True  # Vet appointment is done

# Add tasks to pets
pet1.tasks.append(task1)
pet1.tasks.append(task2)
pet1.tasks.append(task4)
pet2.tasks.append(task3)
pet2.tasks.append(task5)

# Add tasks to scheduler
owner.scheduler.add_task(task1)
owner.scheduler.add_task(task2)
owner.scheduler.add_task(task3)
owner.scheduler.add_task(task4)
owner.scheduler.add_task(task5)

# Create a recurring task for demonstration
recurring_task = owner.scheduler.create_recurring_task(
    pet1,
    "Medication",
    now.replace(hour=9, minute=0),  # 9:00 AM
    "daily",
    timedelta(days=1)
)

print("=== DEMONSTRATING SORTING AND FILTERING METHODS ===\n")

# Demonstrate sorting by time
print("1. Tasks sorted by time (using sort_tasks_by_time):")
sorted_tasks = owner.scheduler.sort_tasks_by_time()
for task in sorted_tasks:
    status = "✓" if task.completed else "○"
    print(f"  {status} {task.time.strftime('%H:%M')}: {task.description} for {task.pet.name}")

print("\n2. Filtering by completion status and pet:")
print("   Completed tasks for Buddy:")
completed_buddy = owner.scheduler.filter_tasks_by_completion_and_pet(True, "Buddy")
for task in completed_buddy:
    print(f"     ✓ {task.time.strftime('%H:%M')}: {task.description}")

print("   Incomplete tasks for Whiskers:")
incomplete_whiskers = owner.scheduler.filter_tasks_by_completion_and_pet(False, "Whiskers")
for task in incomplete_whiskers:
    print(f"     ○ {task.time.strftime('%H:%M')}: {task.description}")

print("\n3. Recurring task expansion for next 3 days:")
start_date = date.today()
end_date = start_date + timedelta(days=2)
expanded_tasks = owner.scheduler.expand_recurring_tasks(start_date, end_date)
recurring_only = [t for t in expanded_tasks if "Medication" in t.description]
for task in sorted(recurring_only, key=lambda t: t.time):
    print(f"     {task.time.strftime('%Y-%m-%d %H:%M')}: {task.description}")

print("\n4. Today's schedule (original method):")
tasks_today = owner.scheduler.get_daily_tasks(date.today())
for task in sorted(tasks_today, key=lambda t: t.time):
    status = "✓" if task.completed else "○"
    print(f"  {status} {task.time.strftime('%H:%M')}: {task.description} for {task.pet.name}")

print("\n5. Demonstrating automatic task completion and rescheduling:")
print("   Before completing the evening walk:")
evening_walk = next(t for t in owner.scheduler.tasks if t.description == "Evening Walk")
print(f"     ○ {evening_walk.time.strftime('%H:%M')}: {evening_walk.description} (completed: {evening_walk.completed})")

print("   Completing the evening walk and scheduling next occurrence...")
owner.scheduler.complete_task_and_schedule_next(evening_walk)

print("   After completion:")
print(f"     ✓ {evening_walk.time.strftime('%H:%M')}: {evening_walk.description} (completed: {evening_walk.completed})")
print("     New tasks in scheduler:")
for task in owner.scheduler.tasks:
    if "Evening Walk" in task.description:
        status = "✓" if task.completed else "○"
        print(f"       {status} {task.time.strftime('%Y-%m-%d %H:%M')}: {task.description} (completed: {task.completed})")

print("\n6. Demonstrating conflict detection:")
print("   Adding two tasks at the same time (11:00 AM)...")
conflict_task1 = Task(pet1, "Grooming Session", now.replace(hour=11, minute=0), "weekly")
conflict_task2 = Task(pet2, "Vet Check", now.replace(hour=11, minute=0), "monthly")
owner.scheduler.add_task(conflict_task1)
owner.scheduler.add_task(conflict_task2)

print("   Checking for time conflicts...")
conflicts = owner.scheduler.detect_time_conflicts()
if conflicts:
    print("Conflicts detected:")
    for warning in conflicts:
        print(f"     {warning}")
else:
    print("No conflicts detected.")
