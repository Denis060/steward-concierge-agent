"""
Steward - a plan-first Concierge agent (Google ADK).

PHASE 3 (polished) - REAL TOOLS VIA MCP
---------------------------------------
The Executor connects to a locally running Google Workspace MCP server
(gmail + calendar), so the agent reads your ACTUAL calendar and email. The
architecture is unchanged: Orchestrator routes Interrogator -> Planner ->
Executor, and the consent rule still guards any irreversible action.

This version smooths three rough edges:
  1. The current date is injected automatically, so no agent ever has to ask
     "what is today's date?" when working out "tomorrow", "this week", etc.
  2. Your email is set as a default (USER_EMAIL), so the agent stops asking
     which account to use.
  3. The Interrogator is told NOT to re-ask anything the user already provided,
     which removes the over-questioning.

BEFORE RUNNING
    1. The MCP server must already be running in its own terminal:
         uvx workspace-mcp --transport streamable-http --single-user --tools gmail calendar
    2. Then run this agent with `adk web --port 8080` from the project folder.
"""

from __future__ import annotations

import datetime
from pathlib import Path
from google.adk.agents import Agent
from google.adk.tools.mcp_tool.mcp_toolset import McpToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StreamableHTTPConnectionParams

# The model the agents think with. Full Flash routes tools more reliably than
# Flash-Lite (which sometimes prints the tool call instead of executing it).
MODEL = "gemini-2.5-flash"

# The user's Google account. The agent uses this whenever a Workspace tool needs
# an email, so it never has to ask. Change this to your address.
USER_EMAIL = "ibrahimdenisfofanah060@gmail.com"

# Today's date, computed fresh every time the agent starts. Injected into the
# agents so they can resolve "tomorrow" / "this week" without asking the user.
TODAY = datetime.date.today().strftime("%A, %B %d, %Y")

# ---------------------------------------------------------------------------
# Plan-first Skill - the interrogation conventions, loaded from file.
# ---------------------------------------------------------------------------
SKILL_PATH = Path(__file__).parent / "plan_first_skill.md"
PLAN_FIRST_SKILL = SKILL_PATH.read_text(encoding="utf-8") if SKILL_PATH.exists() else ""

# ---------------------------------------------------------------------------
# REAL TOOLS via MCP. One toolset exposes all the server's Gmail + Calendar
# tools (get_events, search_gmail_messages, send_gmail_message, etc.).
# ---------------------------------------------------------------------------
workspace_mcp = McpToolset(
    connection_params=StreamableHTTPConnectionParams(
        url="http://localhost:8000/mcp",
    )
)

# ---------------------------------------------------------------------------
# SUB-AGENTS
# ---------------------------------------------------------------------------

interrogator = Agent(
    name="interrogator",
    model=MODEL,
    description="Clarifies a vague request before any work is planned.",
    instruction=(
        f"Today's date is {TODAY}. The user's email is {USER_EMAIL}.\n\n"
        "You clarify the user's intent BEFORE anything is planned or done.\n"
        "Apply these plan-first conventions when deciding what to ask:\n\n"
        f"{PLAN_FIRST_SKILL}\n\n"
        "IMPORTANT RULES TO AVOID OVER-ASKING:\n"
        "- Never ask for anything the user already provided in their message.\n"
        "- Never ask for today's date or the year - you already know it above.\n"
        "- Never ask which email or account to use - you already know it above.\n"
        "- If the request is already clear, do NOT ask anything: write the intent "
        "spec immediately and hand back.\n"
        "- Only ask a question when a detail is genuinely missing AND needed to act.\n\n"
        "When the intent is clear, write a short structured 'intent spec' (goal, "
        "constraints, what done looks like), then hand back to the orchestrator."
    ),
)

planner = Agent(
    name="planner",
    model=MODEL,
    description="Turns a clarified intent spec into an ordered action plan.",
    instruction=(
        f"Today's date is {TODAY}. The user's email is {USER_EMAIL}.\n\n"
        "Given a clarified intent spec, produce a short numbered plan of the exact "
        "tool actions needed, in order. Resolve relative dates (like 'tomorrow') "
        "yourself using today's date above - never ask the user for the date. "
        "Clearly mark any step that is irreversible (sending, deleting, sharing) "
        "so it can be gated for approval. Then hand to the executor to run it."
    ),
)

executor = Agent(
    name="executor",
    model=MODEL,
    description="Carries out the plan using the real Google Workspace tools.",
    instruction=(
        f"Today's date is {TODAY}. The user's email is {USER_EMAIL}.\n\n"
        "Carry out the approved plan using your Google Workspace tools (Gmail and "
        "Calendar). Whenever a tool needs a user email, ALWAYS use "
        f"{USER_EMAIL} - never ask the user for it. Resolve 'tomorrow' / 'this "
        "week' yourself from today's date above.\n\n"
        "USE THE EXACT TOOL NAMES the server provides - do not invent names. "
        "The calendar tools are `list_calendars` and `get_events` (NOT "
        "'get_calendar_events'). The Gmail tools include `search_gmail_messages`, "
        "`get_gmail_message_content`, `draft_gmail_message`, and "
        "`send_gmail_message`. If you are unsure of a tool's exact name or "
        "arguments, inspect the available tools rather than guessing.\n\n"
        "You may read the calendar and search/read email freely. STRICT RULE: "
        "before any irreversible action - above all SENDING an email with "
        "send_gmail_message - you MUST first state the exact recipient, subject, "
        "and body to the user and ask for explicit approval. Do NOT send until the "
        "user replies yes. Prefer creating a draft (draft_gmail_message) over "
        "sending whenever possible."
    ),
    tools=[workspace_mcp],
)

# ---------------------------------------------------------------------------
# ROOT AGENT (the Orchestrator). Must be named `root_agent`.
# ---------------------------------------------------------------------------

root_agent = Agent(
    name="steward",
    model=MODEL,
    description="A plan-first personal concierge grounded in your real Workspace data.",
    instruction=(
        f"Today's date is {TODAY}. The user's email is {USER_EMAIL}.\n\n"
        "You are Steward, a plan-first assistant grounded in the user's real "
        "Google Calendar and Gmail. For any request:\n"
        "1) First delegate to `interrogator` to clarify intent - but if the "
        "request is already clear, it should pass straight through without asking.\n"
        "2) Then delegate to `planner` to build an ordered plan.\n"
        "3) Then delegate to `executor` to carry it out with the real tools.\n"
        "Nothing irreversible (especially sending email) happens without the "
        "user's explicit approval."
    ),
    sub_agents=[interrogator, planner, executor],
)