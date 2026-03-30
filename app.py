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

st.subheader("Quick Demo Inputs (UI only)")
owner_name = st.text_input("Owner name", value="Jordan")
pet_name = st.text_input("Pet name", value="Mochi")
species = st.selectbox("Species", ["dog", "cat", "other"])

st.subheader("Create Owner and Pet")
if st.button("Create Owner and Pet"):
    if "owner" not in st.session_state:
        st.session_state.owner = Owner(owner_name)
        pet = Pet(pet_name, breed=species, age=1, activity_level="medium")  # Assuming default age and activity
        st.session_state.owner.add_pet(pet)
        st.success("Owner and pet created and stored in session state!")
    else:
        st.info("Owner already exists in session state.")

if "owner" in st.session_state:
    st.write(f"Stored Owner: {st.session_state.owner.name}")
    if st.session_state.owner.pets:
        st.write(f"Stored Pet: {st.session_state.owner.pets[0].name}")

st.markdown("### Tasks")
st.caption("Add a few tasks. In your final version, these should feed into your scheduler.")

col1, col2, col3 = st.columns(3)
with col1:
    task_title = st.text_input("Task title", value="Morning walk")
with col2:
    duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20)
with col3:
    priority = st.selectbox("Priority", ["low", "medium", "high"], index=2)

if st.button("Add task"):
    if "owner" in st.session_state and st.session_state.owner.pets:
        pet = st.session_state.owner.pets[0]
        task = Task(pet=pet, description=task_title, time=datetime.now(), frequency="daily")  # Using defaults for time and frequency
        pet.tasks.append(task)
        st.success("Task added to pet!")
    else:
        st.error("Create owner and pet first.")

if "owner" in st.session_state and st.session_state.owner.pets:
    pet = st.session_state.owner.pets[0]
    if pet.tasks:
        st.write("Current tasks:")
        task_data = [{"description": t.description, "time": t.time.strftime("%Y-%m-%d %H:%M"), "frequency": t.frequency, "completed": t.completed} for t in pet.tasks]
        st.table(task_data)
    else:
        st.info("No tasks yet. Add one above.")

st.divider()

st.subheader("Build Schedule")
st.caption("This button should call your scheduling logic once you implement it.")

if st.button("Generate schedule"):
    if "owner" in st.session_state:
        tasks = st.session_state.owner.get_all_pet_tasks()
        if tasks:
            st.write("Scheduled tasks for today:")
            for task in tasks:
                st.write(f"- {task.description} at {task.time.strftime('%H:%M')} (Frequency: {task.frequency})")
        else:
            st.info("No tasks to schedule. Add some tasks first.")
    else:
        st.error("Create owner and pet first.")
