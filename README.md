# Steward - a plan-first Concierge agent

Steward is a personal assistant agent. You give it a vague request like
"sort out my week", and instead of guessing, it **asks the right questions
first**, makes a plan, and then acts - checking with you before it does
anything it can't undo (like sending an email).

It is built with Google's Agent Development Kit (ADK) as a multi-agent system.

---

## Run it in 3 steps

You only need your Google AI Studio API key. Nothing else has to be set up yet.

### 1. Install ADK
Open a terminal in this folder and run:

```
pip install google-adk[mcp]
```

(If you use a virtual environment, activate it first.)

### 2. Paste your API key
Open the file `steward/.env`. Replace `PASTE_YOUR_AI_STUDIO_KEY_HERE` with
your real key. Save the file. That's the only secret you need.

### 3. Start it
From **this** folder (the one with this README), run:

```
adk web
```

Open the link it prints (usually http://localhost:8000), pick **steward**
from the dropdown, and start chatting. Try: *"Help me sort out tomorrow."*

To open it in Antigravity instead: open this whole folder, then run
`adk web` in Antigravity's terminal.

---

## What's real and what's simulated

Right now the agent runs fully, but the parts that touch Gmail, Calendar, and
Drive return **fake data** on purpose - so it works today with no Google
sign-in and no setup headaches. You'll see it interrogate, plan, and ask for
approval correctly; the data behind the tools is just placeholder for now.

Connecting the real Gmail / Calendar / Drive (via MCP) is the next phase.

---

## How it's built

| Part | What it does |
| --- | --- |
| Orchestrator (`root_agent`) | Routes the request through the steps below |
| Interrogator | Clarifies the request using your plan-first conventions |
| Planner | Turns the clarified intent into an ordered plan |
| Executor | Carries out the plan using tools |
| Guardian (consent gate) | Stops any irreversible action until you approve |

Your plan-first conventions live in `steward/plan_first_skill.md` - edit that
file to change how the agent thinks.

The tools the Executor can use are simulated functions in `steward/agent.py`,
each marked with where the real MCP connection will go in the next phase.
