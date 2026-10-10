"""Send the first real trace to neatlogs via the hackathon LiteLLM proxy.

    .venv/Scripts/python first_trace.py
"""

import neatlogs
from config import init_neatlogs

init_neatlogs(workflow_name="first-trace")

from common import llm

client = llm.make_client()

response = client.chat.completions.create(
    model=llm.DEMO_MODEL,
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
