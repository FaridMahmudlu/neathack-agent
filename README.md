# NetHack — neatHack 2026

AI agent project for [neatHack](https://neatlogs.com/hackathon) (Oct 10–12, 2026).

> Project idea: TBD

## Setup

```bash
python -m venv .venv
.venv/Scripts/pip install -r requirements.txt   # Git Bash
# or: .venv\Scripts\pip install -r requirements.txt  (cmd/PowerShell)
```

Copy `.env.example` to `.env` and fill in the keys:

- `NEATLOGS_API_KEY` — neatlogs dashboard → Settings → API keys → **Project API key** (not the `nlw_` ingest key)
- One LLM key: `OPENAI_API_KEY` / `ANTHROPIC_API_KEY` / `GOOGLE_API_KEY` / AWS Bedrock creds

## Verify neatlogs

```bash
# network-free SDK check (no key needed)
.venv/Scripts/python -m neatlogs doctor --local --json

# send a synthetic probe trace (needs only NEATLOGS_API_KEY)
.venv/Scripts/python -m neatlogs doctor --probe

# first real trace (needs an LLM key too)
.venv/Scripts/python first_trace.py
```

## Stack

- Python 3.13
- neatlogs SDK (tracing — required by hackathon)
- Entire CLI (checkpoints — required by hackathon)
- cfo.ai (business plan — required by hackathon)
