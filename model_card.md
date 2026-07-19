# Model Card — PawPal+ RAG Recommendation Feature

## What are the limitations or biases in your system?
Retrieval relies on bag-of-words cosine similarity plus keyword overlap rather than true semantic embeddings, so it can miss relevant vet notes that use different wording than the query. The system is also biased toward pets with rich note histories — a new pet with no notes gets only a generic, low-confidence nudge instead of a tailored recommendation.

## Could your AI be misused, and how would you prevent that?
A malicious or careless user could log false vet notes to get the LLM to recommend inappropriate care actions (e.g., over-medicating), or an owner could blindly trust a low-confidence/fallback suggestion as veterinary advice. This is mitigated by keeping recommendations as proposals the owner must manually review and explicitly add as a task, rather than actions the system executes automatically.

## What surprised you while testing your AI's reliability?
Calling a single fixed Gemini model failed intermittently due to availability/quota issues, which wasn't obvious until manual testing — this is why the system tries a list of candidate models before falling back to the rule engine. It was also surprising how much testing an LLM feature meant testing the fallback path precisely while only verifying the generative path informally, since its output isn't deterministic.

## Describe your collaboration with AI during this project.
AI was used as a design and implementation partner: brainstorming missing class relationships, writing pytest cases, and building out CLI functionality before wiring up the UI, generally in separate chat sessions scoped to one phase of work at a time.

**Helpful suggestion:** AI recommended trying multiple Gemini model names in sequence (`gemini-3.1-flash-lite` → `gemini-3.1-flash` → `gemini-2.0-flash`) instead of hardcoding one, which fixed intermittent failures caused by model availability/quota differences.

**Flawed suggestion:** For task creation, AI initially suggested auto-setting a task's `time` to when the user added it, rather than letting the user specify when the task should actually occur; this was caught by manually testing the Streamlit app and corrected by asking AI to take a user-defined time instead.
