# PawPal+ Project Reflection

## 1. System Design
As stated in the README, PawPal is a stremalit app that helps a pet owner plan care tasks for their pet. PawPal must have functionality to track pet care tasks, consider contraints, and produce and explain a daily plan for the owner. 

**a. Initial design**
Three core actions a user should be able to perform are adding a pet, view today's tasks, and schedule a task. 

Classes that will help accomplish these actions are Owner, Pet, Task, and Scheduler. Owner attributes will be name and pet list. Owner will have responsibilities like adding a pet. Pet attribues will be name, breed, age, activity level, and medications. Pet will have responsibilities like keeping track of what medications the pet needs and at what intervals, a feeding schedule, and a walking schedule. Task attributes will be pet, name, time, location, and priority. Task will have responsibilities like update time and update location. Scheduler will have a tasks attribute. Scheduler will have responsibilities like adding a task, displaying daily tasks and filtering by priority.

UML Diagram:
![alt text](PawPalUML.png)

**b. Design changes**

Yes, my design changed during implementation to include missing relationships. One specific change I made based on Copilot feedback was to add a scheduler attribute to Owner so that they can create tasks for their pets. Another change I made was to add a tasks: List[Task] attribute to Pet for easy display of tasks for a certain Pet.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
