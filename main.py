"""CLI demo script to verify PawPal+ backend logic."""

from datetime import date
from pawpal_system import Owner, Pet, Task, Scheduler


def print_schedule(title: str, tasks: list) -> None:
    print(f"\n{'='*40}")
    print(f"  {title}")
    print(f"{'='*40}")
    if not tasks:
        print("  (no tasks)")
    for task in tasks:
        print(f"  {task}")


def main():
    # --- Setup ---
    owner = Owner("Jordan")

    mochi = Pet("Mochi", "dog")
    luna = Pet("Luna", "cat")

    # Mochi's tasks (added out of order intentionally)
    mochi.add_task(Task("Afternoon walk", "15:00", "daily"))
    mochi.add_task(Task("Morning walk", "07:30", "daily"))
    mochi.add_task(Task("Flea medication", "09:00", "weekly"))

    # Luna's tasks
    luna.add_task(Task("Breakfast feeding", "07:30", "daily"))  # same time as Mochi walk — conflict!
    luna.add_task(Task("Evening feeding", "18:00", "daily"))
    luna.add_task(Task("Vet appointment", "10:00", "once", due_date=date.today()))

    owner.add_pet(mochi)
    owner.add_pet(luna)

    scheduler = Scheduler(owner)

    # --- Today's schedule (sorted) ---
    print_schedule("Today's Schedule (sorted by time)", scheduler.get_todays_schedule())

    # --- Filter: incomplete tasks only ---
    print_schedule("Pending Tasks", scheduler.filter_tasks(completed=False))

    # --- Filter: tasks for Luna ---
    print_schedule("Luna's Tasks", scheduler.filter_tasks(pet_name="Luna"))

    # --- Conflict detection ---
    print("\n--- Conflict Check ---")
    conflicts = scheduler.detect_conflicts()
    if conflicts:
        for warning in conflicts:
            print(f"  {warning}")
    else:
        print("  No conflicts detected.")

    # --- Recurring task demo ---
    print("\n--- Recurring Task Demo ---")
    morning_walk = mochi.get_tasks()[1]  # "Morning walk"
    print(f"  Before: {morning_walk}")
    scheduler.mark_task_complete(morning_walk)
    print(f"  After:  {morning_walk}")
    print("  Mochi's tasks after completion:")
    for t in mochi.get_tasks():
        print(f"    {t}")


if __name__ == "__main__":
    main()
