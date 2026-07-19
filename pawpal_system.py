from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime, date, timedelta
from typing import List, Optional
from collections import defaultdict
import math
import os
import re
from dotenv import load_dotenv, dotenv_values

ENV_PATH = os.path.join(os.path.dirname(__file__), ".env")
load_dotenv(dotenv_path=ENV_PATH)

env_values = dotenv_values(ENV_PATH) or {}
for key in ["GEMINI_API_KEY", "GOOGLE_API_KEY"]:
    if not os.getenv(key) and env_values.get(key):
        os.environ[key] = env_values[key]

try:
    from google import genai as google_genai
except ImportError:  # pragma: no cover
    google_genai = None

@dataclass
class Note:
    content: str
    date: date = field(default_factory=date.today)
    source: str = "vet note"

@dataclass
class Recommendation:
    description: str
    confidence: float
    source: str = "vet note"

@dataclass
class Pet:
    name: str
    breed: str
    age: int
    activity_level: str
    medications: List[str] = field(default_factory=list)
    feeding_schedule: List[str] = field(default_factory=list)
    walking_schedule: List[str] = field(default_factory=list)
    tasks: List[Task] = field(default_factory=list)
    doctor_notes: List[Note] = field(default_factory=list)

    def add_medication(self, med: str) -> None:
        """Add a medication to the pet."""
        self.medications.append(med)

    def remove_medication(self, med: str) -> None:
        """Remove a medication from the pet if it exists."""
        if med in self.medications:
            self.medications.remove(med)

    def add_feeding(self, feeding: str) -> None:
        """Add a feeding schedule entry."""
        self.feeding_schedule.append(feeding)

    def remove_feeding(self, feeding: str) -> None:
        """Remove a feeding schedule entry if present."""
        if feeding in self.feeding_schedule:
            self.feeding_schedule.remove(feeding)

    def add_walking(self, walking: str) -> None:
        """Add a walking schedule entry."""
        self.walking_schedule.append(walking)

    def remove_walking(self, walking: str) -> None:
        """Remove a walking schedule entry if present."""
        if walking in self.walking_schedule:
            self.walking_schedule.remove(walking)

    def get_medication_schedule(self) -> List[str]:
        """Return the medication schedule."""
        return self.medications

    def get_feeding_schedule(self) -> List[str]:
        """Return the feeding schedule."""
        return self.feeding_schedule

    def get_walking_schedule(self) -> List[str]:
        """Return the walking schedule."""
        return self.walking_schedule

    def add_doctor_note(self, content: str, source: str = "vet note", note_date: Optional[date] = None) -> None:
        """Save a doctor or vet note for this pet."""
        if note_date is None:
            note_date = date.today()
        self.doctor_notes.append(Note(content=content.strip(), source=source.strip() or "vet note", date=note_date))

    def remove_doctor_note(self, note: Note) -> None:
        """Remove a specific doctor note if it exists."""
        if note in self.doctor_notes:
            self.doctor_notes.remove(note)

    def get_doctor_notes(self) -> List[Note]:
        """Return all saved doctor notes for this pet."""
        return list(self.doctor_notes)

@dataclass
class Task:
    pet: Pet
    description: str
    time: datetime
    frequency: str
    duration: int = 0
    priority: str = "medium"
    completed: bool = False
    is_recurring: bool = False
    recurrence_interval: Optional[timedelta] = None

    def update_time(self, new_time: datetime) -> None:
        """Update the scheduled time for the task."""
        self.time = new_time

    def update_frequency(self, new_frequency: str) -> None:
        """Update the execution frequency for the task."""
        self.frequency = new_frequency

    def mark_completed(self) -> None:
        """Mark this task as completed."""
        self.completed = True

    def get_next_occurrences(self, start_date: datetime, count: int = 5) -> List[datetime]:
        """Generate the next N occurrence datetimes for recurring tasks from start_date inclusive."""
        if not self.is_recurring or not self.recurrence_interval:
            return [self.time] if self.time >= start_date else []

        occurrences = []
        current = self.time

        # Advance to the first occurrence on or after start_date.
        while current < start_date:
            current += self.recurrence_interval

        while len(occurrences) < count:
            occurrences.append(current)
            current += self.recurrence_interval

        return occurrences


def _tokenize_text(text: str) -> List[str]:
    return re.findall(r"\w+", text.lower())


def _vectorize_text(text: str) -> dict[str, float]:
    vector: dict[str, float] = {}
    for token in _tokenize_text(text):
        vector[token] = vector.get(token, 0.0) + 1.0
    return vector


def _cosine_similarity(a: dict[str, float], b: dict[str, float]) -> float:
    dot = sum(a[token] * b.get(token, 0.0) for token in a)
    norm_a = math.sqrt(sum(value * value for value in a.values()))
    norm_b = math.sqrt(sum(value * value for value in b.values()))
    if not norm_a or not norm_b:
        return 0.0
    return dot / (norm_a * norm_b)


def hybrid_note_retrieval(pet: Pet, query: str, top_n: int = 3) -> List[Note]:
    query_vec = _vectorize_text(query)
    scored_notes = []

    for note in pet.doctor_notes:
        note_vec = _vectorize_text(note.content)
        semantic_score = _cosine_similarity(query_vec, note_vec)
        keyword_score = sum(1 for token in set(_tokenize_text(query)) if token in note_vec)
        score = semantic_score + 0.1 * keyword_score
        scored_notes.append((score, note))

    scored_notes.sort(key=lambda item: item[0], reverse=True)
    return [note for score, note in scored_notes[:top_n] if score > 0] or [note for _, note in scored_notes[:top_n]]


def _get_gemini_api_key() -> Optional[str]:
    return os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")


def _build_gemini_prompt(pet: Pet, notes: List[Note]) -> str:
    note_context = "\n".join(f"- {note.content}" for note in notes) if notes else "No vet notes available."
    existing_tasks = ", ".join(f"{task.description}" for task in pet.tasks) if pet.tasks else "No existing tasks."
    return (
        "You are helping generate a pet care recommendation from vet notes. "
        f"Pet name: {pet.name}. Breed: {pet.breed}. Age: {pet.age}. Activity level: {pet.activity_level}.\n"
        f"Existing tasks: {existing_tasks}\n"
        f"Relevant vet notes:\n{note_context}\n"
        "Return exactly 3 concise recommendations, each on a new line, in the format: "
        "- <specific task recommendation> | confidence:<0-100>"
    )


def _extract_duration_minutes(text: str) -> Optional[int]:
    matches = re.findall(r"(\d+)\s*(?:min|mins|minute|minutes)", text.lower())
    if matches:
        return int(matches[0])
    return None


def _extract_frequency(text: str) -> str:
    lowered = text.lower()
    if "every day" in lowered or "daily" in lowered or "once a day" in lowered:
        return "daily"
    if "every week" in lowered or "weekly" in lowered or "once a week" in lowered:
        return "weekly"
    return "once"


def _generate_fallback_recommendations(pet: Pet, notes: List[Note]) -> List[Recommendation]:
    recommendations: List[Recommendation] = []
    seen_descriptions = set()

    for note in notes or [Note(content=f"General care for {pet.name}", date=date.today())]:
        lowered = note.content.lower()

        if "walk" in lowered or "exercise" in lowered or "fresh air" in lowered:
            duration = _extract_duration_minutes(note.content)
            frequency = _extract_frequency(note.content)
            if duration:
                description = f"{duration}-minute walk"
                if frequency == "daily":
                    description += " every day"
                elif frequency == "weekly":
                    description += " every week"
            else:
                description = "Regular walk and outdoor time"
            confidence = 0.88
        elif "medication" in lowered or "medicine" in lowered or "pill" in lowered:
            description = "Administer the prescribed medication on schedule"
            confidence = 0.9
        elif "bath" in lowered or "groom" in lowered or "brush" in lowered:
            description = "Schedule a grooming or hygiene session"
            confidence = 0.82
        elif "feed" in lowered or "meal" in lowered or "food" in lowered:
            description = "Keep the feeding routine consistent"
            confidence = 0.8
        elif "vet" in lowered or "checkup" in lowered or "appointment" in lowered:
            description = "Book or prepare for the upcoming vet visit"
            confidence = 0.78
        else:
            description = f"Review {pet.name}'s care notes and monitor the condition closely"
            confidence = 0.75

        normalized = description.lower()
        if normalized not in seen_descriptions:
            recommendations.append(Recommendation(description=description, confidence=confidence, source="fallback"))
            seen_descriptions.add(normalized)

        if len(recommendations) >= 3:
            break

    if recommendations:
        return recommendations

    return [
        Recommendation(
            description=f"Review {pet.name}'s vet notes and create a simple care task",
            confidence=0.7,
            source="fallback"
        )
    ]


def _generate_task_suggestions(pet: Pet, notes: List[Note]) -> List[Recommendation]:
    api_key = _get_gemini_api_key()
    if api_key and google_genai is not None:
        try:
            client = google_genai.Client(api_key=api_key)
            prompt = _build_gemini_prompt(pet, notes)
            # Prefer a flash-lite model which often has free-tier quota available,
            # fall back to other models if the preferred one fails for quota or availability.
            candidate_models = ["gemini-3.1-flash-lite", "gemini-3.1-flash", "gemini-2.0-flash"]
            response = None
            for m in candidate_models:
                try:
                    response = client.models.generate_content(model=m, contents=prompt)
                    # if no exception, break and use this response
                    break
                except Exception:
                    response = None
                    continue
            text = getattr(response, "text", "") or ""
            lines = [line.strip() for line in text.splitlines() if line.strip()]
            parsed_recommendations = []
            for line in lines[:3]:
                if "| confidence:" in line:
                    description, confidence_text = line.split("| confidence:", 1)
                    description = description.replace("- ", "", 1).strip()
                    try:
                        confidence = max(0.0, min(1.0, int(confidence_text.strip()) / 100.0))
                    except ValueError:
                        confidence = 0.8
                    parsed_recommendations.append(Recommendation(description=description, confidence=confidence, source="gemini"))
            if parsed_recommendations:
                return parsed_recommendations
        except Exception:
            pass

    return _generate_fallback_recommendations(pet, notes)


def get_gemini_status() -> tuple[bool, str]:
    """Return (available, reason) for Gemini usage.

    - available: True if the google-genai package is importable and an API key is present.
    - reason: human-readable explanation for availability or why it's unavailable.
    """
    api_key = _get_gemini_api_key()
    if google_genai is None:
        return False, "google-genai library not installed"
    if not api_key:
        return False, "GEMINI_API_KEY or GOOGLE_API_KEY not set in environment"
    return True, "Gemini appears available (library + API key present)"


def generate_gemini_demo(pet: Pet, notes: List[Note]) -> List[Recommendation]:
    """Return a small set of demo recommendations labelled as coming from Gemini.

    This is used when the real Gemini client is unavailable but the user
    still wants to see what AI-generated recommendations would look like.
    """
    base = _generate_fallback_recommendations(pet, notes)
    demo_recs: List[Recommendation] = []
    for rec in base:
        demo_recs.append(Recommendation(description=f"{rec.description} (gemini demo)", confidence=min(1.0, rec.confidence + 0.05), source="gemini-demo"))
        if len(demo_recs) >= 3:
            break
    return demo_recs


class Owner:
    def __init__(self, name: str):
        self.name: str = name
        self.pets: List[Pet] = []
        self.scheduler: Scheduler = Scheduler()

    def add_pet(self, pet: Pet) -> None:
        """Add a pet to the owner."""
        self.pets.append(pet)

    def remove_pet(self, pet: Pet) -> None:
        """Remove a pet from the owner if present."""
        if pet in self.pets:
            self.pets.remove(pet)

    def list_pets(self) -> List[Pet]:
        """Return the owner's list of pets."""
        return self.pets

    def get_all_pet_tasks(self) -> List[Task]:
        """Collect tasks from all owned pets."""
        all_tasks = []
        for pet in self.pets:
            all_tasks.extend(pet.tasks)
        return all_tasks

    def find_pet(self, pet_name: str) -> Optional[Pet]:
        """Find a pet by name."""
        for pet in self.pets:
            if pet.name == pet_name:
                return pet
        return None

    def recommend_tasks_for_pet(self, pet_name: str, query: Optional[str] = None) -> List[Recommendation]:
        """Generate pet care recommendations using vet notes and pet context."""
        pet = self.find_pet(pet_name)
        if pet is None:
            return []

        if query is None or query.strip() == "":
            if pet.doctor_notes:
                query = " ".join(note.content for note in pet.doctor_notes)
            else:
                query = f"{pet.name} {pet.breed} {pet.activity_level}"

        notes = hybrid_note_retrieval(pet, query) if pet.doctor_notes else []
        return _generate_task_suggestions(pet, notes)

class Scheduler:
    def __init__(self):
        self.tasks: List[Task] = []

    def add_task(self, task: Task) -> None:
        """Add a task to the scheduler and keep the pet task list in sync."""
        self.tasks.append(task)
        if task not in task.pet.tasks:
            task.pet.tasks.append(task)
        self.tasks.sort(key=lambda t: t.time)

    def remove_task(self, task: Task) -> None:
        """Remove a task from the scheduler and from the pet if it exists."""
        if task in self.tasks:
            self.tasks.remove(task)
        if task in task.pet.tasks:
            task.pet.tasks.remove(task)

    def get_daily_tasks(self, target_date: date) -> List[Task]:
        """Return tasks scheduled for a specific date."""
        return [t for t in self.tasks if t.time.date() == target_date]

    def filter_tasks_by_completion(self, completed: bool) -> List[Task]:
        """Return tasks that match completion status."""
        return [t for t in self.tasks if t.completed == completed]

    def get_next_task(self) -> Optional[Task]:
        """Get the next upcoming task by time."""
        if self.tasks:
            return min(self.tasks, key=lambda t: t.time)
        return None

    def sort_tasks_by_time(self, tasks: List[Task] = None, reverse: bool = False) -> List[Task]:
        """Sort tasks by full datetime. If no tasks provided, sort all scheduler tasks."""
        task_list = tasks or self.tasks
        return sorted(task_list, key=lambda t: t.time, reverse=reverse)

    def filter_tasks_by_completion_and_pet(self, completed: bool, pet_name: str) -> List[Task]:
        """Filter tasks by both completion status and pet name."""
        return [t for t in self.tasks if t.completed == completed and t.pet.name == pet_name]

    def expand_recurring_tasks(self, start_date: date, end_date: date) -> List[Task]:
        """Generate concrete task instances from recurring tasks within date range."""
        expanded_tasks = []
        range_start = datetime.combine(start_date, datetime.min.time())
        range_end = datetime.combine(end_date, datetime.max.time())

        for task in self.tasks:
            if task.is_recurring and task.recurrence_interval:
                current = task.time

                # Advance to the first occurrence on or after range_start.
                while current < range_start:
                    current += task.recurrence_interval

                while current <= range_end:
                    if start_date <= current.date() <= end_date:
                        expanded_tasks.append(Task(
                            pet=task.pet,
                            description=task.description,
                            time=current,
                            frequency=task.frequency,
                            duration=task.duration,
                            priority=task.priority,
                            is_recurring=False,
                            recurrence_interval=None
                        ))
                    current += task.recurrence_interval
            else:
                # Non-recurring task
                if start_date <= task.time.date() <= end_date:
                    expanded_tasks.append(task)

        return expanded_tasks

    def get_tasks_for_date_range(self, start_date: date, end_date: date) -> List[Task]:
        """Get all tasks (including expanded recurring ones) for a date range."""
        return self.expand_recurring_tasks(start_date, end_date)

    def create_recurring_task(self, pet: Pet, description: str, time: datetime, 
                            frequency: str, interval: timedelta) -> Task:
        """Create and add a recurring task to the scheduler and the pet."""
        task = Task(
            pet=pet,
            description=description,
            time=time,
            frequency=frequency,
            is_recurring=True,
            recurrence_interval=interval
        )
        self.add_task(task)
        return task

    def complete_task_and_schedule_next(self, task: Task) -> None:
        """Mark a task as completed and schedule the next occurrence when possible."""
        task.mark_completed()

        recurrence_map = {
            "daily": timedelta(days=1),
            "weekly": timedelta(days=7)
        }

        next_time = None
        if task.recurrence_interval:
            next_time = task.time + task.recurrence_interval
        else:
            next_time = recurrence_map.get(task.frequency.lower())
            if next_time is not None:
                next_time = task.time + next_time

        if not next_time:
            return

        next_task = Task(
            pet=task.pet,
            description=task.description,
            time=next_time,
            frequency=task.frequency,
            duration=task.duration,
            priority=task.priority,
            completed=False,
            is_recurring=False,
            recurrence_interval=None
        )

        self.add_task(next_task)

    def get_all_tasks_from_owner_pets(self, owner: Owner) -> List[Task]:
        """Retrieve tasks from an Owner through owner task aggregation."""
        return owner.get_all_pet_tasks()

    def detect_time_conflicts(self, tasks: List[Task] = None) -> List[str]:
        """Detect tasks scheduled at the same time and return warning messages.

        If an explicit task list is provided, check conflicts only within that list.
        """
        tasks_to_check = tasks if tasks is not None else self.tasks
        time_groups = defaultdict(list)

        # Group tasks by their exact time
        for task in tasks_to_check:
            time_groups[task.time].append(task)

        return [
            f"Time conflict at {time_key.strftime('%Y-%m-%d %H:%M')}: "
            f"{', '.join(f'{task.pet.name} ({task.description})' for task in tasks_at_time)}"
            for time_key, tasks_at_time in time_groups.items()
            if len(tasks_at_time) > 1
        ]
