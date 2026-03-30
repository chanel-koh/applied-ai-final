# PawPal+ Project Reflection

## 1. System Design
As stated in the README, PawPal is a stremalit app that helps a pet owner plan care tasks for their pet. PawPal must have functionality to track pet care tasks, consider contraints, and produce and explain a daily plan for the owner. 

**a. Initial design**
Three core actions a user should be able to perform are adding a pet, view today's tasks, and schedule a task. 

Classes that will help accomplish these actions are Owner, Pet, Task, and Scheduler. Owner attributes will be name and pet list. Owner will have responsibilities like adding a pet. Pet attribues will be name, breed, age, activity level, and medications. Pet will have responsibilities like keeping track of what medications the pet needs and at what intervals, a feeding schedule, and a walking schedule. Task attributes will be pet, name, time, location, and priority. Task will have responsibilities like update time and update location. Scheduler will have a tasks attribute. Scheduler will have responsibilities like adding a task, displaying daily tasks and filtering by priority.

**b. Design changes**

Yes, my design changed during implementation to include missing relationships. One specific change I made based on Copilot feedback was to add a scheduler attribute to Owner so that they can create tasks for their pets. Another change I made was to add a tasks: List[Task] attribute to Pet for easy display of tasks for a certain Pet.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

One constraint my scheduler considers is time- tasks are sorted by their scheduled time. Time conflicts are also detected and the system gives a warning to the user. I decided that time constraint mattered most because, as an app that is based on scheduling, most likely every user cares about time to care for their pet properly.

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

One tradeoff my scheduler makes is to only check for exact time matches instead of overlapping durations. This tradeoff is reasonable for this scenario because some tasks have variable time frames. For example, even if you have an appointment scheduled for the vet, there may be additional waiting time or extra information to talk about afterwards. Plus, the full daily schedule is shown to the owner anyway, so they can glance at it and decide, with their trained judgement, if any time periods overlap.

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

 I used AI tools during this project to brainstorm missing dependencies or logical holes in design brainstorming, aiding a "CLI-first" workflow by writing test functionality in main.py before connecting the UI, and writing pytest cases. AI was a collaborative partner, offering ideas that I should consider in my deisgn and implementation and writing tests for code to pass. 

The kinds of prompts that were the most helpful were ones that were specific in terms of file and intended outcome. For example, when asking AI to write test cases, I specified the file and what cases/functionality I wanted it to check. This made the tests AI wrote more focused.

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

A moment where I did not accept an AI suggestion as-is is when, for adding tasks, AI suggested that the 'time' aspect should get automatically instantiated to the time the user added the task, instead of the intended functionality of the time the user should do that task by. I evaulated what the AI suggested mainly by running the streamlit app and testing out the functionality manually. In the end, I eneded up asking AI to modify to take in a user-defined time for the task instead of its first suggestion.

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

Behaviors I tested were sorting correctness, recurrence logic, and conflict detection. Sorting correctness is important because if an owner has multiple pets and/or tasks for their pets, non-sorted tasks are harder to comprehend and follow. Recurrence logic is important because many tasks are recurring (going for a walk, putting out food and water), so it saves the user time by automatically accounting for recurring tasks in the scheduler. Lastly, conflict detection is important to let users know they should do something differently (schedule at a different time) without crashing the app.

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

I'm pretty confident that the scheduler works correctly on the 3 core tasks from the very beginning: track pet care tasks, consider contraints, and produce a daily plan for the owner. I'm confident because the pytest cases testing this functionality passed. I also verified these features manually by running the Streamlit app. The edge cases I would test next if I had more time is duration conflict detection (not just exact time conflict detection like how my app is now) and how the scheduling display works with multiple owners.

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

I am satisfied with the thoroughness of the test cases and the persistance of user data in Streamlit, because previously I didn't know there was a way to account for saved data. I am also satisfied with the system design of the project because there were multiple iterations of first draft of the classes, then seeing the first UML diagram draft in Mermaid, then updating this UML diagram to reflect the final implementation. Additionally, using separate chat sessions for different phases of the project helped me stay organized.

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

If I had another iteration, I would improve the system with additional ways to filter tasks, such as by priority or duration. This makes the scheduler especially useful for people with many pets and/or pets with many tasks.

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?

One important thing I learned about working with AI to design a system is that the more specific you are with what to do and what you'd like the outcome to be, the better your solutions usually turn out.
