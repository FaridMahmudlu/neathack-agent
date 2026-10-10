# neatHack 2026 — Submission

## Project

**Autopsy** — a debugger for AI-agent mistakes. It investigates a failed
agent run by joining the runtime timeline (neatlogs trace) with the
development timeline (Entire checkpoints + transcripts) and produces an
evidence-backed diagnosis: root cause, failing step, culprit commit/session,
suggested fix.

**Team:** Last Commit
**Repo:** https://github.com/FaridMahmudlu/neathack-agent

## Use of Entire

All product code changes were made through OpenCode agent sessions captured
by Entire. Three checkpoints on `main`:

| Checkpoint ID | Commit | What it is |
|---|---|---|
| `01M4K1KECVQ0VNT4GVGB9KCB90` | `f4df4da09ea6797b4d499e1d1837fbc1ad940129` | OpenCode setup + project notes |
| `01M4K1P5A9NYJJNRY2D9XKJ08P` | `dece4846baaed3c5961447af4c0d99a7dd273ed1` | The regression (debug flip committed) |
| `01M4K1V2G1WYATMGMNK0ZP2KQH` | `63e69d5a9c218ad00c6f524b1b62308be46ed6fa` | The fix, reverted after diagnosis |

Submission checkpoint link (publicly accessible):

```
https://entire.io/gh/FaridMahmudlu/neathack-agent/commit/dece4846baaed3c5961447af4c0d99a7dd273ed1
Checkpoint ID: 01M4K1P5A9NYJJNRY2D9XKJ08P
```

The debugger product itself *consumes* Entire: `inspect_checkpoint`,
`read_checkpoint_transcript`, `search_code` and `show_commit_changes` are
agent tools built on `entire checkpoint` / `entire graph`.

## Use of neatlogs

- `demo_agent` — every run traced (workflow `demo-research-agent`): LLM
  spans, tool spans, payloads
- `agent_debugger` — the investigation itself traced (workflow
  `agent-debugger`): every tool call is a span
- The debugger *reads* traces via the neatlogs Public API
  (`GET /traces`, `/traces/{id}/spans`, `/spans/{id}/payload`) with a
  service-account token (`context:read` + `observability:read`)

Key traces (project `2258b224-229a-445d-ad30-045c4978ba1a`):

| Trace ID | What |
|---|---|
| `98330b2d046133fee546ecfc1c011915` | Bugged run — degraded answer |
| `62c2dce9659d83e26711fe123e8c3dc7` | Autopsy's own investigation (19 LLM calls) |
| `ead5a98e094a5e2495f6e428c41fc196` | Fixed run — full correct answer |

## Use of cfo.ai

Business plan built in the cfo.ai workspace:
https://cfo.ai/s/gWOEX-_KzKXUshRa — assumptions tables, monthly
revenue/cash engine, 4+ scenarios, dashboards. Summary in
[CFO_PLAN.md](CFO_PLAN.md). Headline: list prices lose money on the Team
tier (−40% margin) — the model found it, we built the cost curve to fix it
(64% blended margin, breakeven month 16).

## Demo

Reproduction steps + video script: [DEMO.md](DEMO.md).

## What the judges should look at

1. `agent_debugger/` — the product (10 tools, agent loop, evidence model)
2. The live diagnosis output in the demo — it names the real checkpoint ID
   and the exact `reverse=False` line
3. The Entire commit page — 4 linked sessions including two where the coding
   agent *refused* to introduce the bug
