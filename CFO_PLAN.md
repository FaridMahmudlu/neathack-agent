# Autopsy — Business Plan (built with cfo.ai)

> Modeled in the cfo.ai neatHack workspace:
> https://cfo.ai/s/gWOEX-_KzKXUshRa
> The headline below is what the model found — including the part that
> hurts. We keep it honest: the fix is the plan, not the spin.

## What we sell

**Autopsy** is a root-cause debugger for production AI agents. Observability
tools show *what* went wrong; Autopsy tells you *why* — by joining runtime
traces with development history (which coding-agent session/commit
introduced the regression) and returning a diagnosis with verifiable
evidence plus a suggested fix.

**Buyer:** platform / AI-infra teams shipping LLM agents to production.
**Pain:** a failed agent run costs an engineer 30–90 min of manual trace
reading + `git blame` archaeology. Autopsy compresses that to ~2 min.

## Pricing

| Tier | Price | Includes |
|---|---|---|
| Free | $0 | 25–50 diagnoses/mo, 1 repo |
| Pro | $79/mo/seat | 500 diagnoses/mo |
| Team | $499/mo (5 seats) | 2k diagnoses/mo, CI gate, SSO |
| Enterprise | ~$4k/mo (placeholder) | 15k diagnoses, self-hosted, SLA |

Overage: $0.50 per diagnosis — required, not optional (see below).

## What the model found (the honest part)

Variable cost per diagnosis ≈ **$0.35** (LLM $0.30 — 86% of cost — +
observability $0.02 + infra $0.03). At 40% utilization:

| Plan | Revenue | Cost to serve | Gross margin |
|---|---|---|---|
| Pro (2 seats) | $158 | $140 | 11% |
| Team | $499 | $700 | **−40%** |
| Enterprise | $4,000 | $2,100 | 48% |

At list prices **Team loses ~$201/customer/month**; blended margin at
month 12 is −3% to −10% and the business never breaks even — $500k runs
out in ~21 months in every scenario.

## The fix (margin scenario)

1. **Cost curve:** $0.35 → **$0.17**/diagnosis — cache repeated
   investigations, route simpler failures to smaller models, batch calls.
2. **Reprice:** Team $499 → **$799** with overage charge; trim included
   allotments (Team 5k→2k, Free 50→25); Enterprise = cost-plus.
3. **Hard caps / overage** so heavy users can't sink the margin.

Result: blended gross margin → **~64%**, cash-flow positive **month 16**
(Jan 2028), cash bottoms at ~$323k of the $500k — **the raise is never
fully consumed**.

## Scenarios (MRR at month 12, pre-fix list prices)

| Scenario | Paid accounts | MRR |
|---|---|---|
| Base | 51 | $23.8k |
| Growth | 93 | $43.0k |
| Breakout | 170 | $78.2k |

Base reaches ~360 paid teams by month 36 (~1.5% of the 25k-team SAM).

### Repricing alone is not enough (cfo.ai's 5th scenario)

Team repriced to $799/mo + $0.70 overage: month-12 MRR rises to $27.8k and
margin to +5.9%, but cash still runs out Feb 2029 — ~6 months *before*
breakeven (Aug 2029). Team margin is only 12.4% at 40% usage and goes
negative above 45.7% — while overage doesn't kick in until 100%. The cost
curve is the fix; repricing is a complement, not a substitute.

## Top 3 financial risks (per the model)

1. **Cost per diagnosis** — LLM inference is 86% of variable cost; treat it
   as the north-star engineering metric.
2. **Price/usage mismatch** — Team charges $0.10/diagnosis that costs
   $0.35 to serve; caps and overage are mandatory.
3. **Concentrated runway** — Enterprise carries most of the profit; one
   slipped deal puts fundraising mode at ~month 15.

## Pitch line

> "We've modeled it: at list prices the unit economics don't work — so we
> built the cost curve to fix it. 64% gross margin and breakeven at month
> 16 on the money we've already raised."
