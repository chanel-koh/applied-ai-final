# PawPal+

## Original Project

This builds on **PawPal+**, a Streamlit app originally developed in Modules 1–3 of CodePath AI110. The original goal was to design and implement a pet care planning assistant using an object-oriented system (Owner, Pet, Task, Scheduler) — first modeled in UML, then implemented in Python, then wired up to a Streamlit UI. Its original capabilities were letting an owner track pet care tasks (walks, feeding, meds, grooming), detect scheduling conflicts, and view a chronological daily plan.

## Summary

This final iteration extends PawPal+ with a **Retrieval-Augmented Generation (RAG) recommendation feature**: owners can log free-text vet notes for a pet, and the system retrieves the most relevant notes and uses them as grounding context for an LLM (Google Gemini) to generate concrete, schedulable task recommendations (e.g., "15-minute walk every day," "Administer the prescribed medication on schedule"). This matters because it turns PawPal+ from a manual task tracker into an assistant that proactively surfaces care actions grounded in a pet's actual medical history, while still degrading gracefully to a rule-based fallback if no API key or network access is available.

## Architecture Overview

See [diagrams/system-diagram.mmd](diagrams/system-diagram.mmd) for the full Mermaid diagram. At a high level, the pipeline is:

1. **Context Builder** — combines the user's request, the pet's profile (breed, age, activity level), and its saved vet notes.
2. **Retriever** (`hybrid_note_retrieval` in [pawpal_system.py](pawpal_system.py)) — scores each vet note against the query using a blend of cosine similarity over bag-of-words vectors (semantic signal) and raw keyword overlap (lexical signal), then returns the top-N most relevant notes.
3. **Reasoning Layer** (`_generate_task_suggestions`) — builds a prompt from the retrieved notes and pet context and sends it to Gemini (tries `gemini-3.1-flash-lite` → `gemini-3.1-flash` → `gemini-2.0-flash` in order), asking for exactly 3 recommendations with confidence scores.
4. **Fallback path** (`_generate_fallback_recommendations`) — if Gemini is unavailable (no API key, package missing, or the call fails), a deterministic keyword-rule engine produces recommendations from the same retrieved notes, so the feature always returns something usable.
5. **Scheduler / UI** — the user reviews recommendations in the Streamlit app and can add any of them directly as a real `Task`, which then flows through the existing sorting, conflict-detection, and recurrence logic from the original scheduler.

This keeps retrieval, generation, and scheduling as separate, independently testable stages rather than one monolithic call.

## Setup Instructions

1. **Clone and enter the project directory.**

2. **Create and activate a virtual environment:**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # Windows: .venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **(Optional) Enable live Gemini recommendations.** Create a `.env` file in the project root:
   ```
   GEMINI_API_KEY=your_api_key_here
   ```
   Without a key, the app still runs and uses the rule-based fallback recommendations automatically — no code changes needed.

5. **Run the Streamlit app:**
   ```bash
   streamlit run app.py
   ```

6. **Run the CLI demo** (exercises scheduler features without the UI):
   ```bash
   python main.py
   ```

7. **Run the test suite:**
   ```bash
   python -m pytest
   ```

## Sample Interactions

**1. Vet note → grounded recommendation**
- Input (vet note for Buddy): `"Buddy should get a 20 minute walk every day to manage his weight."`
- The retriever surfaces this note as most relevant when generating recommendations.
- Output: `20-minute walk every day` (confidence: 88%).

**2. Medication note**
- Input (vet note for Whiskers): `"Whiskers needs her thyroid medication twice daily with food."`
- Output: `Administer the prescribed medication on schedule` (confidence: 90%).

**3. No vet notes yet**
- Input: a brand-new pet profile with no saved notes.
- The system falls back to pet metadata (name, breed, activity level) as the query context.
- Output: `Review Mochi's vet notes and create a simple care task` (confidence: 70%) — a low-confidence, generic nudge rather than a fabricated specific claim.

**4. Scheduler conflict detection (core feature, still functional)**
```
Adding two tasks at the same time (11:00 AM)...
Checking for time conflicts...
Conflicts detected:
     Time conflict at 2026-06-13 11:00: Buddy (Grooming Session), Whiskers (Vet Check)
```

## Design Decisions

- **Hybrid retrieval over pure embeddings**: rather than calling an embeddings API for a small, per-pet set of short vet notes, retrieval uses lightweight bag-of-words cosine similarity blended with keyword overlap. This avoids extra API cost/latency for what is typically a handful of short notes, at the cost of missing deeper semantic paraphrase matches a real embedding model would catch.
- **Fallback-first reliability**: the recommendation feature always has a deterministic, rule-based fallback path so the app is demoable and testable without any API key, and remains usable if Gemini quota is exhausted or the network is unavailable. The trade-off is that the fallback is less flexible — it only recognizes a fixed set of keyword categories (walk, medication, grooming, feeding, vet visit).
- **Recommendations are proposals, not auto-scheduled tasks**: the user must explicitly pick a date/time and click "Add recommended task" rather than the system silently inserting tasks into the schedule. This preserves user control and avoids double-booking or acting on a bad LLM suggestion.
- **Exact-time conflict detection (carried over from the original project)**: the scheduler flags conflicts only on exact timestamp matches rather than overlapping duration windows, which is simpler to reason about and sufficient given that the full sorted schedule is always shown to the owner for a final visual check.

## Testing Summary

Test coverage includes verification of:
- Sorting correctness: tasks are returned in chronological order
- Recurrence logic: marking a daily/weekly task complete creates a new task for the following occurrence
- Conflict detection: scheduler flags duplicate times

```
============================= test session starts ==============================
platform darwin -- Python 3.13.5, pytest-9.0.3, pluggy-1.5.0
collected 19 items

tests/test_pawpal.py::test_mark_completed_sets_task_completed PASSED     [  5%]
tests/test_pawpal.py::test_add_task_to_pet_increases_task_count PASSED   [ 10%]
tests/test_pawpal.py::test_sort_tasks_by_time_ascending_order PASSED     [ 15%]
tests/test_pawpal.py::test_sort_tasks_empty_scheduler PASSED             [ 21%]
tests/test_pawpal.py::test_sort_tasks_single_task PASSED                 [ 26%]
tests/test_pawpal.py::test_sort_tasks_same_time_multiple_tasks PASSED    [ 31%]
tests/test_pawpal.py::test_sort_tasks_reverse_order PASSED               [ 36%]
tests/test_pawpal.py::test_sort_tasks_ignores_date_sorts_by_time_only PASSED [ 42%]
tests/test_pawpal.py::test_complete_daily_task_creates_next_day_occurrence PASSED [ 47%]
tests/test_pawpal.py::test_complete_weekly_task_creates_next_week_occurrence PASSED [ 52%]
tests/test_pawpal.py::test_complete_non_recurring_task_no_next_task PASSED [ 57%]
tests/test_pawpal.py::test_complete_task_with_invalid_frequency PASSED   [ 63%]
tests/test_pawpal.py::test_complete_task_frequency_case_insensitive PASSED [ 68%]
tests/test_pawpal.py::test_detect_time_conflicts_two_tasks_same_time PASSED [ 73%]
tests/test_pawpal.py::test_detect_time_conflicts_no_conflicts PASSED     [ 78%]
tests/test_pawpal.py::test_detect_time_conflicts_three_tasks_same_time PASSED [ 84%]
tests/test_pawpal.py::test_detect_time_conflicts_empty_scheduler PASSED  [ 89%]
tests/test_pawpal.py::test_detect_time_conflicts_single_task PASSED      [ 94%]
tests/test_pawpal.py::test_detect_time_conflicts_multiple_time_slots_some_conflicts PASSED [100%]

============================== 19 passed in 0.02s ==============================
```

- **What worked**: All 19 existing pytest cases covering sorting, recurrence, and conflict detection continue to pass unmodified, confirming the RAG feature was added without regressing core scheduler behavior. Manual testing in the Streamlit UI confirmed the recommendation flow end-to-end: adding a vet note, generating recommendations, and converting a recommendation into a real scheduled task.
- **What didn't work / had to change**: Early attempts at calling a single fixed Gemini model failed intermittently due to model availability/quota differences, which is why `_generate_task_suggestions` tries a list of candidate models in order before falling back to the rule engine.
- **What we learned**: Testing an LLM-backed feature requires treating "no crash and something reasonable comes back" as the bar, since exact output text isn't deterministic — the fallback path is what's unit-tested precisely, while the Gemini path is verified manually via the UI status indicator (`get_gemini_status()`), which reports whether the key/library are available.
- **Not yet tested**: duration-based conflict detection (overlapping ranges, not just exact time matches) and behavior with multiple owners/pets sharing overlapping schedules.

## Reflection

Building the RAG layer on top of an already-working scheduler clarified how much of "adding AI" is really about designing the non-AI scaffolding around it: retrieval quality, a fallback for when generation fails, and keeping the LLM's output as a suggestion a human approves rather than a decision the system acts on unilaterally. The biggest lesson was that reliability work (the fallback path, trying multiple models, surfacing an availability status to the user) ended up being as important as the generation logic itself — an AI feature that silently breaks when a quota runs out is worse than no AI feature at all. It also reinforced that grounding matters: recommendations tied to a specific retrieved vet note felt meaningfully more trustworthy than generic advice, which is the core promise of RAG over a bare LLM call.


