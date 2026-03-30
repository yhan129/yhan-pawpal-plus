"""PawPal+ core logic layer: Owner, Pet, Task, and Scheduler classes."""

from dataclasses import dataclass, field
from datetime import date, timedelta


@dataclass
class Task:
    """Represents a single pet care activity."""

    description: str
    time: str  # "HH:MM" 24-hour format
    frequency: str  # "once", "daily", "weekly"
    pet_name: str = ""
    completed: bool = False
    due_date: date = field(default_factory=date.today)

    def mark_complete(self) -> None:
        """Mark this task complete.

        For recurring tasks, rolls the due date forward and resets to pending
        so the same task object represents tomorrow's/next week's occurrence.
        For one-time tasks, sets completed=True and leaves it in the list.
        """
        if self.frequency == "daily":
            self.due_date += timedelta(days=1)
            # stays pending — it's now scheduled for tomorrow
        elif self.frequency == "weekly":
            self.due_date += timedelta(weeks=1)
        else:
            self.completed = True

    def __str__(self) -> str:
        status = "+" if self.completed else "-"
        return f"[{status}] {self.time} - {self.description} ({self.frequency})"


@dataclass
class Pet:
    """Stores pet details and a list of associated tasks."""

    name: str
    species: str
    tasks: list = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """Add a task to this pet's task list."""
        task.pet_name = self.name
        self.tasks.append(task)

    def get_tasks(self) -> list:
        """Return all tasks for this pet."""
        return self.tasks

    def __str__(self) -> str:
        return f"{self.name} ({self.species})"


class Owner:
    """Manages multiple pets and provides aggregate access to their tasks."""

    def __init__(self, name: str) -> None:
        """Initialize an Owner with a name and empty pet list."""
        self.name = name
        self.pets: list[Pet] = []

    def add_pet(self, pet: Pet) -> None:
        """Add a pet to the owner's roster."""
        self.pets.append(pet)

    def get_all_tasks(self) -> list[Task]:
        """Return every task across all pets."""
        tasks = []
        for pet in self.pets:
            tasks.extend(pet.get_tasks())
        return tasks

    def __str__(self) -> str:
        return f"Owner: {self.name} ({len(self.pets)} pet(s))"


class Scheduler:
    """Retrieves, organizes, and manages tasks across all pets for an Owner."""

    def __init__(self, owner: Owner) -> None:
        """Initialize the Scheduler with an Owner instance."""
        self.owner = owner

    def get_todays_schedule(self) -> list[Task]:
        """Return all tasks sorted chronologically by time."""
        return self.sort_by_time(self.owner.get_all_tasks())

    def sort_by_time(self, tasks: list[Task] = None) -> list[Task]:
        """Sort tasks by their HH:MM time attribute in ascending order."""
        if tasks is None:
            tasks = self.owner.get_all_tasks()
        return sorted(tasks, key=lambda t: t.time)

    def filter_tasks(
        self,
        pet_name: str = None,
        completed: bool = None,
    ) -> list[Task]:
        """Filter tasks by pet name and/or completion status.

        Pass pet_name to restrict to a single pet; pass completed=True/False
        to restrict by status. Omitting a parameter means "no filter on that field".
        """
        tasks = self.owner.get_all_tasks()
        if pet_name is not None:
            tasks = [t for t in tasks if t.pet_name == pet_name]
        if completed is not None:
            tasks = [t for t in tasks if t.completed == completed]
        return tasks

    def detect_conflicts(self) -> list[str]:
        """Return warning strings for any two tasks scheduled at the same time."""
        tasks = self.owner.get_all_tasks()
        seen: dict[str, Task] = {}
        warnings = []
        for task in tasks:
            if task.time in seen:
                other = seen[task.time]
                warnings.append(
                    f"[!] Conflict at {task.time}: '{task.description}' "
                    f"({task.pet_name}) vs '{other.description}' ({other.pet_name})"
                )
            else:
                seen[task.time] = task
        return warnings

    def mark_task_complete(self, task: Task) -> None:
        """Mark a task complete. Recurring tasks roll forward in place; one-time tasks
        become Done and stay visible in the schedule."""
        task.mark_complete()
