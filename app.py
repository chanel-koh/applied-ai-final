import streamlit as st
from pawpal_system import Owner, Pet, Task, Scheduler
from datetime import datetime

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")

st.markdown(
    """
Welcome to the PawPal+ starter app.

This file is intentionally thin. It gives you a working Streamlit app so you can start quickly,
but **it does not implement the project logic**. Your job is to design the system and build it.

Use this app as your interactive demo once your backend classes/functions exist.
"""
)

with st.expander("Scenario", expanded=True):
    st.markdown(
        """
**PawPal+** is a pet care planning assistant. It helps a pet owner plan care tasks
for their pet(s) based on constraints like time, priority, and preferences.

You will design and implement the scheduling logic and connect it to this Streamlit UI.
"""
    )

with st.expander("What you need to build", expanded=True):
    st.markdown(
        """
At minimum, your system should:
- Represent pet care tasks (what needs to happen, how long it takes, priority)
- Represent the pet and the owner (basic info and preferences)
- Build a plan/schedule for a day that chooses and orders tasks based on constraints
- Explain the plan (why each task was chosen and when it happens)
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

st.markdown("### Tasks")
st.caption("Add a few tasks. In your final version, these should feed into your scheduler.")

if "owner" in st.session_state and st.session_state.owner.pets:
    pet_names = [p.name for p in st.session_state.owner.pets]
    selected_pet_name = st.selectbox("Select pet for task", pet_names)

col1, col2, col3 = st.columns(3)
with col1:
    task_title = st.text_input("Task title", value="Morning walk")
with col2:
    duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20)
with col3:
    priority = st.selectbox("Priority", ["low", "medium", "high"], index=2)

if st.button("Add task"):
    if "owner" in st.session_state and st.session_state.owner.pets:
        selected_pet = next(p for p in st.session_state.owner.pets if p.name == selected_pet_name)
        task = Task(pet=selected_pet, description=task_title, time=datetime.now(), frequency="daily")  # Using defaults for time and frequency
        selected_pet.tasks.append(task)
        st.success(f"Task added to {selected_pet_name}!")
    else:
        st.error("Create owner and add a pet first.")

if "owner" in st.session_state and st.session_state.owner.pets:
    for pet in st.session_state.owner.pets:
        if pet.tasks:
            st.write(f"Tasks for {pet.name}:")
            task_data = [{"description": t.description, "time": t.time.strftime("%Y-%m-%d %H:%M"), "frequency": t.frequency, "completed": t.completed} for t in pet.tasks]
            st.table(task_data)
        else:
            st.info(f"No tasks for {pet.name} yet.")
else:
    st.info("No pets yet. Add one above.")

st.divider()

st.subheader("Build Schedule")
st.caption("This button should call your scheduling logic once you implement it.")

if st.button("Generate schedule"):
    if "owner" in st.session_state:
        tasks = st.session_state.owner.get_all_pet_tasks()
        if tasks:
            st.write("Scheduled tasks for today:")
            for task in tasks:
                st.write(f"- {task.description} for {task.pet.name} at {task.time.strftime('%H:%M')} (Frequency: {task.frequency})")
        else:
            st.info("No tasks to schedule. Add some tasks first.")
    else:
        st.error("Create owner and pet first.")
