import streamlit as st
from pawpal_system import Owner, Pet, Task, Scheduler
from datetime import datetime, date, time

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")

st.markdown(
    """
Welcome to the PawPal+ starter app.
"""
)

with st.expander("About PawPal+", expanded=True):
    st.markdown(
        """
**PawPal+** is a pet care planning assistant. It helps a pet owner plan care tasks
for their pet(s) based on constraints like time, priority, and preferences.

"""
    )


st.divider()

st.subheader("Create Owner")
owner_name = st.text_input("Owner name", value="Jordan")

if st.button("Create Owner"):
    if "owner" not in st.session_state:
        st.session_state.owner = Owner(owner_name)
        st.success("Owner created and stored in session state!")
    else:
        st.info("Owner already exists in session state.")

st.subheader("Add Pet")
pet_name = st.text_input("Pet name", value="Mochi")
species = st.selectbox("Species", ["dog", "cat", "other"])
age = st.number_input("Age", min_value=0, max_value=30, value=1)
activity_level = st.selectbox("Activity Level", ["low", "medium", "high"], index=1)

if st.button("Add Pet"):
    if "owner" in st.session_state:
        pet = Pet(name=pet_name, breed=species, age=age, activity_level=activity_level)
        st.session_state.owner.add_pet(pet)
        st.success(f"Pet {pet_name} added to owner!")
    else:
        st.error("Create owner first.")

if "owner" in st.session_state:
    st.write(f"Stored Owner: {st.session_state.owner.name}")
    if st.session_state.owner.pets:
        st.write("Pets:")
        for pet in st.session_state.owner.pets:
            st.write(f"- {pet.name} ({pet.breed}, age {pet.age}, activity {pet.activity_level})")
    else:
        st.info("No pets added yet.")

st.markdown("### Vet Notes")
if "owner" in st.session_state and st.session_state.owner.pets:
    note_pet_name = st.selectbox("Select pet for notes", [p.name for p in st.session_state.owner.pets], key="note_pet_selector")
    note_text = st.text_area("Enter vet note", height=120)
    note_source = st.text_input("Note source", value="vet note")

    if st.button("Save vet note"):
        selected_note_pet = next(p for p in st.session_state.owner.pets if p.name == note_pet_name)
        selected_note_pet.add_doctor_note(content=note_text, source=note_source)
        st.success(f"Note saved for {selected_note_pet.name}.")

    selected_note_pet = next((p for p in st.session_state.owner.pets if p.name == note_pet_name), None)
    if selected_note_pet and selected_note_pet.doctor_notes:
        st.write(f"Saved notes for {selected_note_pet.name}:")
        for note in selected_note_pet.doctor_notes:
            st.write(f"- {note.date}: {note.source} — {note.content}")
else:
    st.info("Add a pet first to start saving vet notes.")

st.markdown("### Tasks")

if "owner" in st.session_state and st.session_state.owner.pets:
    pet_names = [p.name for p in st.session_state.owner.pets]
    selected_pet_name = st.selectbox("Select pet for task", pet_names)

    if "recommendations" not in st.session_state or st.session_state.get("recommendation_pet_name") != selected_pet_name:
        st.session_state.recommendations = []
        st.session_state.recommendation_pet_name = selected_pet_name

    if st.button("Generate recommendations"):
        st.session_state.recommendations = st.session_state.owner.recommend_tasks_for_pet(selected_pet_name)
        st.success("Recommendations generated.")

    if st.session_state.recommendations:
        st.write("Recommended tasks:")
        for rec in st.session_state.recommendations:
            st.write(f"- {rec}")

        selected_recommendation = st.selectbox(
            "Choose a recommended task to add",
            st.session_state.recommendations,
            key="recommended_task_select"
        )
        if st.button("Add recommended task"):
            selected_pet = next(p for p in st.session_state.owner.pets if p.name == selected_pet_name)
            task_datetime = datetime.combine(date.today(), time(9, 0))
            task = Task(
                pet=selected_pet,
                description=selected_recommendation,
                time=task_datetime,
                frequency="once",
                duration=15,
                priority="medium"
            )
            st.session_state.owner.scheduler.add_task(task)
            st.success(f"Added recommended task for {selected_pet_name}: {selected_recommendation}")

col1, col2, col3 = st.columns(3)
with col1:
    task_title = st.text_input("Task title", value="Morning walk")
with col2:
    duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20)
with col3:
    priority = st.selectbox("Priority", ["low", "medium", "high"], index=2)

col4, col5, col6 = st.columns(3)
with col4:
    task_date = st.date_input("Date", value=date.today())
with col5:
    task_time = st.time_input("Time", value=time(8, 0))
with col6:
    frequency = st.selectbox("Frequency", ["once", "daily", "weekly"], index=0)

if st.button("Add task"):
    if "owner" in st.session_state and st.session_state.owner.pets:
        selected_pet = next(p for p in st.session_state.owner.pets if p.name == selected_pet_name)
        task_datetime = datetime.combine(task_date, task_time)
        task = Task(
            pet=selected_pet,
            description=task_title,
            time=task_datetime,
            frequency=frequency,
            duration=duration,
            priority=priority
        )
        st.session_state.owner.scheduler.add_task(task)
        st.success(f"Task added for {selected_pet_name} on {task_date.strftime('%b %d')} at {task_time.strftime('%H:%M')}!")
    else:
        st.error("Create owner and add a pet first.")

if "owner" in st.session_state and st.session_state.owner.pets:
    for pet in st.session_state.owner.pets:
        if pet.tasks:
            st.write(f"Tasks for {pet.name}:")
            for task in pet.tasks:
                completed = st.checkbox(
                    f"{task.time.strftime('%Y-%m-%d %H:%M')} - {task.description} ({task.frequency})",
                    value=task.completed,
                    key=f"task_complete_{pet.name}_{task.description}_{task.time.isoformat()}"
                )
                if completed and not task.completed:
                    task.mark_completed()
                    st.success(f"Marked '{task.description}' complete for {pet.name}.")
                elif not completed and task.completed:
                    task.completed = False
                    st.info(f"Marked '{task.description}' incomplete for {pet.name}.")
        else:
            st.info(f"No tasks for {pet.name} yet.")
else:
    st.info("No pets yet. Add one above.")

st.divider()

st.subheader("Build Schedule")

if st.button("Generate schedule"):
    if "owner" in st.session_state:
        owner = st.session_state.owner
        scheduler = owner.scheduler

        today = date.today()
        todays_tasks = scheduler.get_daily_tasks(today)

        if not todays_tasks:
            st.info("No tasks scheduled for today. Add a task with today's date to see it here.")
        else:
            sorted_tasks = scheduler.sort_tasks_by_time(todays_tasks)
            conflict_warnings = scheduler.detect_time_conflicts(todays_tasks)

            if conflict_warnings:
                for warning in conflict_warnings:
                    st.warning(warning)
            else:
                st.success("No conflicts detected in your current schedule.")

            st.caption(f"Showing {len(sorted_tasks)} task(s) for today ({today.strftime('%B %d, %Y')})")
            task_rows = []
            for task in sorted_tasks:
                task_rows.append({
                    "Time": task.time.strftime("%Y-%m-%d %H:%M"),
                    "Pet": task.pet.name,
                    "Task": task.description,
                    "Frequency": task.frequency,
                    "Completed": "✅" if task.completed else "❌"
                })

            st.subheader("Sorted Schedule")
            st.table(task_rows)

            next_task = scheduler.get_next_task()
            if next_task:
                st.success(f"Next task: {next_task.description} for {next_task.pet.name} at {next_task.time.strftime('%H:%M')}")
            else:
                st.info("No upcoming tasks available.")
    else:
        st.error("Create owner and pet first.")
