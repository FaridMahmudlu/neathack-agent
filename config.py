"""Shared config: loads .env and initializes neatlogs.

Import `init_neatlogs()` once near the app entry point, before any LLM client
is constructed (auto-instrumentation and wrapping happen at init time).
"""

import os

from dotenv import load_dotenv

load_dotenv()

import neatlogs


def init_neatlogs(workflow_name: str) -> None:
    api_key = os.environ.get("NEATLOGS_API_KEY")
    if not api_key:
        raise RuntimeError(
            "NEATLOGS_API_KEY is not set. Copy the Project API key from "
            "neatlogs Settings -> API keys into .env"
        )
    neatlogs.init(
        api_key=api_key,
        endpoint="https://ingest.neatlogs.com",
        workflow_name=workflow_name,
    )
