# Autopsy — a debugger for AI-agent mistakes

**Team Last Commit · [neatHack 2026](https://neatlogs.com/hackathon)**

Autopsy investigates *why* an AI-agent run failed — not just *where*. It is
itself an agent: given a failing run, it combines three evidence sources

- **neatlogs traces** — what the failing agent actually did at runtime
  (every LLM call, tool call, input, output, error)
- **Entire checkpoints** — which coding-agent session produced each commit,
  with the transcript of what it was asked to do
- **Entire graph** — semantic code search and entity-level per-commit changes

and emits an evidence-backed diagnosis: root cause, the exact trace step
where it surfaced, the culprit commit **and the session transcript behind
it**, plus a suggested fix.

The debugger's own investigation is fully traced in neatlogs too — the tool
for debugging agents is itself an observable agent.

## Why this matters

When an agent misbehaves, today's tools show you the *what* (a bad answer, a
failed tool call) but not the *why*. The why usually lives in two places at
once: the runtime evidence (the trace) and the development history (who
changed what, and what they were trying to do). Autopsy is the first tool
that joins those two timelines: trace span → suspect code → the checkpoint
and coding-agent transcript that introduced it.

## Demo result (live, reproducible)

We broke a small research agent (`demo_agent`) on purpose: a debugging
session flipped `search_docs` from descending to ascending order, so the
search tool started returning the *least* relevant pages first. The agent's
answer degraded — it could no longer describe the flag of Azerbaijan.

Autopsy's diagnosis on the failing trace, verbatim:

> **Root cause:** `search_docs` sorts ascending (`reverse=False` at
> `demo_agent/app.py:51`), so worst matches come first and the
> `flag-of-azerbaijan` page is cut before it reaches the LLM.
> **Failing step:** all four `search_docs` calls returned the same three
> lowest-scoring pages regardless of query phrasing.
> **Culprit:** checkpoint `01M4K1P5A9NYJJNRY2D9XKJ08P` — commit
> `dece484` "Flip search_docs ordering for ranking inspection".
> **Fix:** `reverse=True`.

After the fix commit, the same question produces the full correct answer
(*"horizontal tricolour of blue, red, and green, with a white crescent and
an eight-pointed star"*).

### Evidence

| Artifact | Link / ID |
|---|---|
| Culprit commit + sessions (Entire) | [dece484 on Entire](https://entire.io/gh/FaridMahmudlu/neathack-agent/commit/dece4846baaed3c5961447af4c0d99a7dd273ed1) |
| Checkpoint — benign change | `01M4K1KECVQ0VNT4GVGB9KCB90` (`f4df4da`) |
| Checkpoint — bug introduced | `01M4K1P5A9NYJJNRY2D9XKJ08P` (`dece484`) |
| Checkpoint — fix | `01M4K1V2G1WYATMGMNK0ZP2KQH` (`63e69d5`) |
| neatlogs trace — bugged run | `98330b2d046133fee546ecfc1c011915` |
| neatlogs trace — Autopsy's own investigation | `62c2dce9659d83e26711fe123e8c3dc7` |
| neatlogs trace — verified fixed run | `ead5a98e094a5e2495f6e428c41fc196` |

A nice side-effect captured by the checkpoints: the coding agent (OpenCode +
Claude Haiku) was asked twice to introduce the regression as a "refactor"
and *refused* — it negated the score instead of flipping the order,
preserving correct behaviour. The bug only landed when asked as a debugging
experiment. The transcripts tell that whole story; Autopsy reads them.

## Layout

```
agent_debugger/   the debugger agent
  neatlogs_api.py   read-only neatlogs Public API client
  entire_cli.py     subprocess wrapper for `entire` CLI + graph plugin
  tools.py          10 agent tools, each a neatlogs TOOL span
  agent.py          investigation loop (WORKFLOW root span)
demo_agent/       target system: a tiny research agent we broke on purpose
common/           shared LLM client (LiteLLM/Claude) + tool-call loop
config.py         dotenv + neatlogs init
opencode.json     OpenCode provider config (hackathon LiteLLM proxy)
```

## How it works

Autopsy is an LLM agent loop (Claude Sonnet 4.6) with 10 tools:

| Tool | Evidence source |
|---|---|
| `list_recent_traces`, `inspect_trace`, `read_span_payload` | neatlogs Public API |
| `list_checkpoints`, `inspect_checkpoint`, `read_checkpoint_transcript` | Entire checkpoints |
| `search_code`, `show_commit_changes` | Entire graph |
| `read_source_file` | target repository |
| `write_diagnosis` | emits `diagnosis.json` |

Method: inspect the trace → find the span where the failure surfaced → read
its payload → form a hypothesis → locate the implicated code → walk the
checkpoints to find which commit/session introduced it → emit the diagnosis
with pointers a human can verify.

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
| `LITELLM_API_KEY` | hackathon LiteLLM proxy key, or any OpenAI-compatible endpoint (`LITELLM_BASE_URL`) |

## Run

```bash
# the research agent — its runs appear as 'demo-research-agent' traces
.venv/Scripts/python -m demo_agent "Which city is the capital of Azerbaijan
and what does its flag look like?"

# the debugger investigates a run (by trace id or by description)
.venv/Scripts/python -m agent_debugger "trace 98330b2d... returned an
incomplete answer about the flag" --repo .
```

## Hackathon sponsor usage

- **neatlogs** — both agents are fully traced; the debugger also *reads*
  traces back through the Public API as a core tool
- **Entire** — every code change is linked to its coding-agent session via
  checkpoints; the debugger uses checkpoint explain + transcripts + graph to
  attribute bugs to sessions
- **cfo.ai** — business plan in [CFO_PLAN.md](CFO_PLAN.md) (pricing, unit
  economics, runway)
