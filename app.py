"""PawPal+ Streamlit UI — connected to the pawpal_system logic layer."""

import streamlit as st
from datetime import timedelta
from pawpal_system import Owner, Pet, Task, Scheduler

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")
st.title("🐾 PawPal+")
st.caption("Smart pet care management — powered by algorithmic scheduling.")

# ── Session state bootstrap ────────────────────────────────────────────────────
# st.session_state persists across reruns; only create Owner once.
if "owner" not in st.session_state:
    st.session_state.owner = None

if "scheduler" not in st.session_state:
    st.session_state.scheduler = None

# ── Owner setup ────────────────────────────────────────────────────────────────
with st.expander("👤 Owner Setup", expanded=st.session_state.owner is None):
    owner_name = st.text_input("Owner name", value="Jordan")
    if st.button("Create / switch owner"):
        st.session_state.owner = Owner(owner_name)
        st.session_state.scheduler = Scheduler(st.session_state.owner)
        st.success(f"Owner '{owner_name}' ready!")

if st.session_state.owner is None:
    st.info("Create an owner above to get started.")
    st.stop()

owner: Owner = st.session_state.owner
scheduler: Scheduler = st.session_state.scheduler

# ── Add a pet ─────────────────────────────────────────────────────────────────
with st.expander("🐶 Add a Pet"):
    col1, col2 = st.columns(2)
    with col1:
        pet_name = st.text_input("Pet name", value="Mochi")
    with col2:
        species = st.selectbox("Species", ["dog", "cat", "bird", "other"])
    if st.button("Add pet"):
        pet_names = [p.name for p in owner.pets]
        if pet_name in pet_names:
            st.warning(f"'{pet_name}' is already on the roster.")
        else:
            owner.add_pet(Pet(pet_name, species))
            st.success(f"{pet_name} ({species}) added!")

# ── Add a task ────────────────────────────────────────────────────────────────
with st.expander("📋 Schedule a Task"):
    if not owner.pets:
        st.info("Add a pet first.")
    else:
        pet_options = [p.name for p in owner.pets]
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            target_pet = st.selectbox("Pet", pet_options)
        with col2:
            task_desc = st.text_input("Task", value="Morning walk")
        with col3:
            task_time = st.text_input("Time (HH:MM)", value="07:30")
        with col4:
            task_freq = st.selectbox("Frequency", ["once", "daily", "weekly"])

        if st.button("Add task"):
            # Basic time format validation
            parts = task_time.split(":")
            valid_time = (
                len(parts) == 2
                and parts[0].isdigit()
                and parts[1].isdigit()
                and 0 <= int(parts[0]) <= 23
                and 0 <= int(parts[1]) <= 59
            )
            if not valid_time:
                st.error("Please use HH:MM format (e.g. 07:30).")
            else:
                for pet in owner.pets:
                    if pet.name == target_pet:
                        pet.add_task(Task(task_desc, task_time, task_freq))
                        st.success(f"Task '{task_desc}' added for {target_pet}.")
                        break

st.divider()

# ── Today's schedule ──────────────────────────────────────────────────────────
st.subheader("Today's Schedule")

all_tasks = scheduler.get_todays_schedule()

if not all_tasks:
    st.info("No tasks yet. Add a pet and schedule some tasks above.")
else:
    # Conflict warnings
    conflicts = scheduler.detect_conflicts()
    for warning in conflicts:
        st.warning(warning)

    # Build display rows
    rows = []
    for task in all_tasks:
        rows.append(
            {
                "Time": task.time,
                "Pet": task.pet_name,
                "Task": task.description,
                "Frequency": task.frequency,
                "Status": "Done" if task.completed else "Pending",
            }
        )
    st.table(rows)

st.divider()

# ── Filter panel ──────────────────────────────────────────────────────────────
st.subheader("Filter Tasks")

col_a, col_b = st.columns(2)
with col_a:
    filter_pet = st.selectbox(
        "Filter by pet",
        ["All"] + [p.name for p in owner.pets],
        key="filter_pet",
    )
with col_b:
    filter_status = st.selectbox(
        "Filter by status",
        ["All", "Pending", "Done"],
        key="filter_status",
    )

filtered = scheduler.filter_tasks(
    pet_name=None if filter_pet == "All" else filter_pet,
    completed=None if filter_status == "All" else (filter_status == "Done"),
)

if filtered:
    st.table(
        [
            {
                "Time": t.time,
                "Pet": t.pet_name,
                "Task": t.description,
                "Status": "Done" if t.completed else "Pending",
            }
            for t in scheduler.sort_by_time(filtered)
        ]
    )
else:
    st.info("No tasks match the current filter.")

st.divider()

# ── Mark task complete ────────────────────────────────────────────────────────
st.subheader("Mark a Task Complete")

pending_tasks = scheduler.filter_tasks(completed=False)
if not pending_tasks:
    st.success("All tasks are done!")
else:
    task_labels = [
        f"{t.time} - {t.pet_name}: {t.description}" for t in pending_tasks
    ]
    chosen_label = st.selectbox("Select task to complete", task_labels)
    if st.button("Mark complete"):
        idx = task_labels.index(chosen_label)
        chosen_task = pending_tasks[idx]
        scheduler.mark_task_complete(chosen_task)
        if chosen_task.frequency != "once":
            st.success(
                f"'{chosen_task.description}' marked done. "
                f"Next occurrence scheduled for {chosen_task.due_date + timedelta(days=1 if chosen_task.frequency == 'daily' else 7)}."
            )
        else:
            st.success(f"'{chosen_task.description}' marked done.")
        st.rerun()
