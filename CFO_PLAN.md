# Autopsy — Business Plan (cfo.ai workspace)

> Paste-ready content for the cfo.ai neatHack workspace. Numbers are
> deliberately conservative and reproducible — every figure traces to an
> assumption listed below.

## What we sell

**Autopsy** is a root-cause debugger for production AI agents. Observability
tools show *what* went wrong; Autopsy tells you *why* — by joining runtime
traces with the development history (which coding-agent session/commit
introduced the regression) and returning a diagnosis with verifiable
evidence pointers plus a suggested fix.

**Buyer:** platform / AI-infra teams shipping LLM agents to production.
**Pain:** a failed agent run today costs an engineer 30–90 min of manual
trace reading + `git blame` archaeology. Autopsy compresses that to ~2 min.

## Pricing

| Tier | Price | Includes |
|---|---|---|
| Free | $0 | 50 diagnoses/mo, 1 repo, community support |
| Pro | $79/mo/seat | 500 diagnoses/mo, unlimited repos, Slack alerts |
| Team | $499/mo (5 seats) | 5k diagnoses/mo, CI gate ("fail PR if culprit change detected"), SSO |
| Enterprise | custom | self-hosted, custom retention, SLA |

Usage overage: $0.50 per extra diagnosis.

## Unit economics (per diagnosis)

Measured on our own demo (Claude Sonnet 4.6 via LiteLLM, 19 LLM calls,
10 tool calls):

| Cost item | Amount |
|---|---|
| LLM inference (~40k tok in / ~4k tok out) | ~$0.30 |
| neatlogs ingestion + storage (allocated) | ~$0.02 |
| Infra (compute, queue, db) | ~$0.03 |
| **Total variable cost** | **~$0.35** |

At Pro pricing ($79/seat, ~500 diagnoses included ⇒ $0.16/diagnosis list)
the marginal cost exceeds list price at full utilization — so included
allotments assume ~40% utilization (industry typical), effective revenue
per *used* diagnosis ≈ $0.40. **Gross margin ≈ 55% on Pro, ~75% blended**
(Team/Enterprise carry the margin; overage at $0.50 is ~30% margin).

Honest note: the moat is workflow + evidence quality, not raw margin —
observability ingestion is a commodity; the value is the diagnosis.

## Market

- ~150k teams are shipping or piloting LLM agents (2026)
- SAM: teams already paying for agent observability ≈ 25k teams
- SOM (3 yr): 1.5% of SAM ≈ 375 paying teams

## Revenue scenarios (MRR, end of year 1)

| Scenario | Teams | Mix | MRR |
|---|---|---|---|
| Base | 40 | 30 Pro ($79) + 10 Team ($499) | ~$7.4k |
| Growth | 120 | 80 Pro + 40 Team | ~$26k |
| Breakout | 350 | 200 Pro + 140 Team + 10 Ent ($2k) | ~$106k |

## Costs & runway ($500k pre-seed)

| Item | Monthly |
|---|---|
| 3 engineers (founders, below-market) | $18k |
| Infra + LLM + neatlogs COGS | $2k → scales with usage |
| Tools/G&A | $1.5k |
| **Burn** | **~$21.5k** |

Base case reaches ~$7.4k MRR by month 12 ⇒ net burn ≈ $14k/mo ⇒
**runway ≈ 24 months** on $500k. Growth case reaches cash-flow breakeven
around month 14–16.

## What we spend the hackathon proving

The demo *is* the product's core loop working end-to-end on a real failure:
trace → suspect span → culprit checkpoint → fix → verified re-run. The next
90 days: GitHub App ingestion (auto-diagnose failed CI agent runs), and
pricing validated via 10 design-partner teams.
