"""LLM provider: Google Gemini via google-genai, wrapped for neatlogs.

The client MUST be constructed after neatlogs.init() — genai caches its
transport at construction time.
"""

import os

import neatlogs
from google import genai

MODEL = os.environ.get("DEBUGGER_MODEL", "gemini-2.5-flash")


def make_client():
    key = os.environ.get("GOOGLE_API_KEY")
    if not key:
        raise RuntimeError(
            "GOOGLE_API_KEY is not set. Get a free key at "
            "https://aistudio.google.com and add it to .env"
        )
    return neatlogs.wrap(genai.Client(api_key=key))
