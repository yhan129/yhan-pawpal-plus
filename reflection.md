# PawPal+ Project Reflection

## 1. System Design

a. Initial design

I went with four classes: Task, Pet, Owner, and Scheduler. Task holds the info for one care activity like what it is, when it happens, how often, and if its done yet. Pet keeps a list of its own tasks. Owner holds all the pets. Scheduler is the only one actually doing logic like sorting or finding conflicts.

I tried to keep each class focused on its own thing. Task doesnt know anything about Pet, Pet doesnt know anything about Owner, and only the Scheduler has to look across everything at once.

b. Design changes

Originally Task didnt have a pet_name field. I thought the Scheduler could just search backwards through the pets to find who owned a task. That got annoying once I started building conflict warnings because the message needs to say which pet has the problem. I ended up just adding pet_name directly on Task and having add_task() fill it in automatically. Small change but it made things a lot cleaner.

---

## 2. Scheduling Logic and Tradeoffs

a. Constraints and priorities

The two things the scheduler cares about are time and frequency. Every task has an HH:MM time and it sorts by that. Frequency controls what happens when you mark something done. Time felt like the most important thing to get right since the whole point is knowing when to do stuff.

b. Tradeoffs

The conflict check only catches tasks at the exact same time. It wont catch something like a 30 minute walk at 7:15 overlapping with a feeding at 7:30. That's a limitation but tasks dont store a duration anyway so there's no way to do better math right now. Exact time matches are the cases that actually matter most.

---

## 3. AI Collaboration

a. How you used AI

I used Copilot a lot. The most helpful part was generating the UML diagram early on. I described the four classes and it gave me Mermaid syntax to work from which saved me from having to look all that up myself. It also pointed me toward timedelta for recurrence which I probably wouldve figured out eventually.

For testing it helped me think of edge cases I missed, like what happens with an owner who has no pets at all.

I noticed asking about behavior worked better than asking for code. Something like "when a daily task is marked complete what should happen to it" got more useful answers than just "write a mark_complete method."

b. Judgment and verification

At one point Copilot suggested putting the task list on the Scheduler instead of on each Pet, saying it would be simpler to sort. I didnt go with it because it didnt make sense to me. If the Scheduler holds the tasks then what does Pet even represent. I traced through what would happen when you add a new pet mid session and realized youd need extra bookkeeping to connect tasks back to the right pet. Keeping tasks on Pet was just cleaner.

---

## 4. Testing and Verification

a. What you tested

I wrote 15 tests covering the main behaviors. Marking a task complete, adding tasks to a pet, daily and weekly recurrence rolling the due date forward, one time tasks becoming done and staying in the list, sorting order, filtering by pet name and status, and conflict detection. The ones I cared most about were recurrence and conflict detection since bugs there would mean actually missing a vet appointment or a medication.

b. Confidence

All 15 pass so I feel pretty good about the core stuff. Things I didnt get to test are what happens if a task gets completed right around midnight, and whether filtering by both pet name and status at the same time works right since I only tested them one at a time. Would add those with more time.

---

## 5. Reflection

a. What went well

Writing and testing main.py before touching app.py was the right call. By the time I connected the Streamlit UI I already trusted the backend so I wasnt debugging two things at once. The Scheduler being the only thing app.py talks to also helped since the UI never reaches directly into pet.tasks.

b. What you would improve

I would add duration to Task so conflict detection can catch overlapping windows instead of just exact matches. A priority field with a secondary sort would be useful too since right now if two tasks are at the same time the order between them is kind of random.

c. Key takeaway

Vague prompts kept getting vague answers. Once I started describing what I actually wanted the behavior to be the suggestions got way more useful. You still have to know what youre building, the AI just helps write it faster once you do.
