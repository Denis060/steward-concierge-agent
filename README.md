# Steward — a Plan-First Concierge Agent (Google ADK)

> A multi-agent assistant that interviews you, writes a plan, then acts on your real Gmail and Google Calendar through MCP — and never takes an irreversible action without explicit consent.

![Python](https://img.shields.io/badge/Python-3-blue.svg) ![Google ADK](https://img.shields.io/badge/Google-ADK-4285F4.svg) ![MCP](https://img.shields.io/badge/tools-MCP-black.svg)

## Overview

Steward is a concierge agent built on Google's Agent Development Kit. Instead of acting immediately on a vague request, it follows a **plan-first** loop: clarify → plan → execute, with a consent gate before anything that can't be undone (e.g. sending an email or creating an event).

## Problem / Motivation

Most assistant agents either ask too many questions or act too eagerly. Steward explores the middle ground: ask only what's missing, show the plan, and require confirmation for side effects.

## Approach & tech stack

- **Orchestrator** routes between three sub-agents:
  - **Interrogator** – asks only for missing details (never re-asks what you already said)
  - **Planner** – turns the request into a step-by-step plan
  - **Executor** – carries out the plan using real tools
- **Tools:** Gmail + Calendar via a local Google Workspace MCP server (`McpToolset` over streamable HTTP)
- **Conventions:** a reusable "plan-first" skill file (`steward/plan_first_skill.md`) injected into the agents
- Current date is injected so "tomorrow" / "this week" resolve without asking
- **Stack:** Python · Google ADK · Gemini 2.5 Flash · Model Context Protocol (MCP)

## Key features

- Plan-first workflow with explicit consent rule for irreversible actions
- Real calendar and email reads/writes through MCP
- Minimal-questioning interrogation style
- Runs in the ADK web UI

## How to run

```bash
pip install "google-adk[mcp]"
# 1) start the Workspace MCP server in its own terminal
uvx workspace-mcp --transport streamable-http --single-user --tools gmail calendar
# 2) set your Gemini API key (see ADK docs), and USER_EMAIL in steward/agent.py
# 3) run the agent
adk web --port 8080
```

---

## About the author

**Ibrahim Denis Fofanah** — Data Scientist · ML / GenAI (RAG, agents) · BI & analytics · MS Data Science, Pace University (2025)

[LinkedIn](https://www.linkedin.com/in/ibrahim-denis-fofanah/) · [Email](mailto:ibrahim.fofanah.ds@gmail.com) · [Live RAG portfolio project](https://moijey-copilot.vercel.app) · [GitHub](https://github.com/Denis060)
