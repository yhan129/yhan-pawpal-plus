"""Automated tests for PawPal+ system logic."""

import pytest
from datetime import date, timedelta
from pawpal_system import Owner, Pet, Task, Scheduler


# --- Fixtures ---

@pytest.fixture
def sample_owner():
    owner = Owner("Jordan")
    mochi = Pet("Mochi", "dog")
    luna = Pet("Luna", "cat")
    mochi.add_task(Task("Morning walk", "07:30", "daily"))
    mochi.add_task(Task("Afternoon walk", "15:00", "daily"))
    luna.add_task(Task("Breakfast feeding", "08:00", "daily"))
    owner.add_pet(mochi)
    owner.add_pet(luna)
    return owner


@pytest.fixture
def scheduler(sample_owner):
    return Scheduler(sample_owner)


# --- Task tests ---

def test_mark_complete_sets_flag():
    """mark_complete() should change completed to True."""
    task = Task("Evening walk", "18:00", "once")
    assert task.completed is False
    task.mark_complete()
    assert task.completed is True


def test_adding_task_increases_count():
    """Adding a task to a Pet should increase its task count."""
    pet = Pet("Buddy", "dog")
    assert len(pet.get_tasks()) == 0
    pet.add_task(Task("Walk", "09:00", "daily"))
    assert len(pet.get_tasks()) == 1
    pet.add_task(Task("Feed", "12:00", "daily"))
    assert len(pet.get_tasks()) == 2


def test_task_pet_name_assigned_on_add():
    """Pet.add_task should stamp the pet's name onto the task."""
    pet = Pet("Mochi", "dog")
    task = Task("Walk", "09:00", "daily")
    assert task.pet_name == ""
    pet.add_task(task)
    assert task.pet_name == "Mochi"


# --- Recurrence tests ---

def test_daily_task_rolls_forward():
    """Completing a daily task should advance its due_date by 1 day and stay pending."""
    today = date.today()
    task = Task("Morning walk", "07:30", "daily", due_date=today)
    task.mark_complete()
    assert task.due_date == today + timedelta(days=1)
    assert task.completed is False


def test_weekly_task_rolls_forward():
    """Completing a weekly task should advance its due_date by 7 days and stay pending."""
    today = date.today()
    task = Task("Flea medication", "09:00", "weekly", due_date=today)
    task.mark_complete()
    assert task.due_date == today + timedelta(weeks=1)
    assert task.completed is False


def test_one_time_task_becomes_done():
    """Completing a 'once' task should set completed=True and keep it in the list."""
    task = Task("Vet appointment", "10:00", "once")
    task.mark_complete()
    assert task.completed is True


def test_mark_task_complete_keeps_task_in_list(sample_owner, scheduler):
    """Scheduler.mark_task_complete should not remove tasks from the pet's list."""
    mochi = sample_owner.pets[0]
    original_count = len(mochi.get_tasks())
    daily_task = mochi.get_tasks()[0]
    scheduler.mark_task_complete(daily_task)
    assert len(mochi.get_tasks()) == original_count
    assert daily_task in mochi.get_tasks()


# --- Sorting tests ---

def test_sort_by_time_returns_chronological_order(scheduler):
    """sort_by_time should return tasks in HH:MM ascending order."""
    sorted_tasks = scheduler.sort_by_time()
    times = [t.time for t in sorted_tasks]
    assert times == sorted(times)


def test_sort_handles_empty_list():
    """sort_by_time with no tasks should return an empty list."""
    owner = Owner("Empty")
    scheduler = Scheduler(owner)
    assert scheduler.sort_by_time() == []


# --- Filtering tests ---

def test_filter_by_pet_name(scheduler):
    """filter_tasks(pet_name=...) should return only that pet's tasks."""
    luna_tasks = scheduler.filter_tasks(pet_name="Luna")
    assert all(t.pet_name == "Luna" for t in luna_tasks)
    assert len(luna_tasks) > 0


def test_filter_incomplete_tasks(scheduler):
    """filter_tasks(completed=False) should return only incomplete tasks."""
    pending = scheduler.filter_tasks(completed=False)
    assert all(not t.completed for t in pending)


def test_filter_completed_tasks(sample_owner, scheduler):
    """filter_tasks(completed=True) should return only completed tasks."""
    # Use a one-time task so mark_complete sets completed=True
    once_task = Task("Vet visit", "11:00", "once")
    sample_owner.pets[0].add_task(once_task)
    once_task.mark_complete()
    done = scheduler.filter_tasks(completed=True)
    assert len(done) == 1
    assert done[0].completed is True


# --- Conflict detection tests ---

def test_detect_no_conflicts(scheduler):
    """No conflicts should be reported when all tasks have distinct times."""
    conflicts = scheduler.detect_conflicts()
    assert conflicts == []


def test_detect_conflict_same_time():
    """Two tasks at the same time should trigger a conflict warning."""
    owner = Owner("Test")
    pet_a = Pet("Alpha", "dog")
    pet_b = Pet("Beta", "cat")
    pet_a.add_task(Task("Walk", "09:00", "once"))
    pet_b.add_task(Task("Feed", "09:00", "once"))
    owner.add_pet(pet_a)
    owner.add_pet(pet_b)
    s = Scheduler(owner)
    conflicts = s.detect_conflicts()
    assert len(conflicts) == 1
    assert "09:00" in conflicts[0]


def test_no_conflict_for_single_pet_different_times():
    """A single pet with non-overlapping tasks should have zero conflicts."""
    owner = Owner("Solo")
    pet = Pet("Rex", "dog")
    pet.add_task(Task("Walk", "08:00", "once"))
    pet.add_task(Task("Feed", "12:00", "once"))
    owner.add_pet(pet)
    s = Scheduler(owner)
    assert s.detect_conflicts() == []
