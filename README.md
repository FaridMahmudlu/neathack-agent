# Autopsy — a debugger for AI-agent mistakes

**Team Last Commit · [neatHack 2026](https://neatlogs.com/hackathon)**

Autopsy investigates why an AI-agent run failed. It combines:

- **neatlogs traces** — what the failing agent actually did (every LLM call,
  tool call, input, output, error)
- **Entire checkpoints** — which coding-agent session produced each commit,
  with the transcript behind it
- **Entire graph** — semantic code search and entity-level per-commit changes

and emits an evidence-backed diagnosis: root cause, the exact trace step where
it surfaced, the culprit commit/session, and a suggested fix.

## Layout

```
agent_debugger/   the debugger agent itself
  neatlogs_api.py   read-only neatlogs Public API client
  entire_cli.py     subprocess wrapper for `entire` CLI
  tools.py          agent tools (each is a neatlogs TOOL span)
  agent.py          investigation loop (WORKFLOW root)
demo_agent/       target system: a tiny research agent we break on purpose
config.py         dotenv + neatlogs init
first_trace.py    neatlogs smoke test
CURSOR_PROMPTS.md Cursor session prompts that generate Entire checkpoints
```

## Setup

```bash
python -m venv .venv
.venv/Scripts/pip install -r requirements.txt        # Git Bash
# .venv\Scripts\pip install -r requirements.txt      # cmd/PowerShell
cp .env.example .env   # fill in the keys
```

| Key | Where |
|---|---|
| `NEATLOGS_API_KEY` | neatlogs → Settings → API keys → **Project API key** |
| `NEATLOGS_TOKEN` | neatlogs → Settings → Service Accounts → token with `context:read` + `observability:read` |
| `NEATLOGS_PROJECT_ID` | project UUID (dashboard URL / service-account binding) |
| `GOOGLE_API_KEY` | [aistudio.google.com](https://aistudio.google.com) — free |

## Run

```bash
# the buggy target agent (its runs appear as 'demo-research-agent' traces)
.venv/Scripts/python -m demo_agent "What is the capital of the country whose
flag shows a crescent and an eight-pointed star?"

# the debugger investigates the latest failing run in this repo
.venv/Scripts/python -m agent_debugger "the demo agent answered with the
wrong capital" --repo .
```

The debugger's own investigation is traced too (workflow `agent-debugger`) —
open neatlogs → Traces to watch it work.

## Hackathon requirements

- **neatlogs** — both agents are fully traced; the debugger also *reads* traces
  via the Public API
- **Entire** — checkpoints link each change to its coding session; the
  debugger uses them to find which session introduced the bug
- **cfo.ai** — business plan in `docs/` (pricing, costs, revenue, runway)
