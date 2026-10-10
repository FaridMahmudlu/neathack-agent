# Demo video — script & reproduction (5–7 min)

## Story in one line

An agent gives a bad answer → Autopsy reads its trace, walks the Entire
checkpoints, names the exact session that broke it, and we fix + verify —
all live.

## Shot list

**0:00–0:30 — The world**
- Terminal in the repo. `git log --oneline -5` — show the three checkpoint
  commits.
- Say: "Agents fail in production. Today I'll debug one live — and the
  debugger will tell me which coding session caused it."

**0:30–1:15 — Break it** *(pre-recorded or skipped — bug commit already in
history; if re-recording, checkout `dece484`)*
- Run: `.venv/Scripts/python -m demo_agent "Which city is the capital of
  Azerbaijan and what does its flag look like?"`
- Show the degraded answer ("corpus doesn't contain detailed flag info").
- Say: "The trace is already in neatlogs."

**1:15–1:45 — The trace**
- neatlogs dashboard → Traces → `98330b2d…`
- Point at the 4 `search_docs` tool spans all returning the same 3 pages.

**1:45–3:30 — Autopsy runs**
- Run: `.venv/Scripts/python -m agent_debugger "trace 98330b2d... returned
  an incomplete answer about the flag"`
- While it works (fast-forward is fine): mention it's a 10-tool agent
  reading neatlogs + Entire + the code graph — *and* its own run is traced
  too (show `agent-debugger` workflow in neatlogs afterwards).
- Show the diagnosis output. Highlight: it names `reverse=False` at
  `app.py:51` AND the checkpoint ID `01M4K1P5…`.

**3:30–4:30 — The Entire link**
- Open `https://entire.io/gh/FaridMahmudlu/neathack-agent/commit/dece484…`
- Show: the culprit commit + the 4 OpenCode sessions behind it.
- Optional kicker: "the coding agent was asked twice to introduce this
  regression as a 'refactor' and refused — the transcripts are right here."

**4:30–5:30 — Fix & verify**
- Show fix commit `63e69d5` (or run the OpenCode fix prompt live).
- Re-run the demo agent → full correct flag answer.
- Show the fixed trace `ead5a98e…` in neatlogs side by side.

**5:30–6:00 — Close**
- "Autopsy: the first debugger that joins what your agent did with why the
  code became wrong. neatlogs for the runtime truth, Entire for the
  development truth."
- End card: repo URL + team name.

## Reproduction commands

```bash
# buggy state (at commit dece484)
git checkout dece484
.venv/Scripts/python -m demo_agent "Which city is the capital of Azerbaijan
and what does its flag look like?"

# debug it
git checkout main
.venv/Scripts/python -m agent_debugger "trace <ID> returned an incomplete
answer about the flag"

# verified state — same question again
.venv/Scripts/python -m demo_agent "Which city is the capital of Azerbaijan
and what does its flag look like?"
```
