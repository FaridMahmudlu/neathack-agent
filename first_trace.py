"""Send the first real trace to neatlogs.

No LLM key yet? Send a synthetic probe trace with only the neatlogs key:
    .venv/Scripts/python -m neatlogs doctor --probe

Once an LLM key is in .env (OPENAI_API_KEY), run:
    .venv/Scripts/python first_trace.py
"""

import neatlogs
from config import init_neatlogs

init_neatlogs(workflow_name="first-trace")

from openai import OpenAI

client = neatlogs.wrap(OpenAI())

response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        {
            "role": "user",
            "content": "Reply with exactly: neatlogs connected",
        }
    ],
)
print(response.choices[0].message.content)

neatlogs.flush()
neatlogs.shutdown()
