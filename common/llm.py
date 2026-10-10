"""LLM provider: the neatHack LiteLLM proxy (Claude / Nova), OpenAI-compatible.

$20 shared team allowance — use Sonnet for the debugger (reasoning quality)
and Haiku for the demo target (cheap, chatty).
"""

import os

import neatlogs
from openai import OpenAI

BASE_URL = os.environ.get("LITELLM_BASE_URL", "https://litellm.vision.aivar.app/v1")
DEBUGGER_MODEL = os.environ.get("DEBUGGER_MODEL", "claude-sonnet-4.6")
DEMO_MODEL = os.environ.get("DEMO_MODEL", "claude-haiku")


def make_client() -> OpenAI:
    key = os.environ.get("LITELLM_API_KEY")
    if not key:
        raise RuntimeError(
            "LITELLM_API_KEY is not set — your team's key is at "
            "https://neatlogs.com/hackathon/models"
        )
    return neatlogs.wrap(OpenAI(base_url=BASE_URL, api_key=key))
