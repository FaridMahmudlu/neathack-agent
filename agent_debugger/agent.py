"""The debugger agent: an LLM loop that investigates a failed agent run
using neatlogs traces, Entire checkpoints, the code graph, and the source.
"""

import neatlogs

from common import llm, toolcall

from . import tools

SYSTEM_PROMPT = """You are Autopsy, an expert debugger for AI-agent failures.

You investigate why an agent run went wrong. You have tools for three
evidence sources:

- neatlogs traces: what the failing agent actually did at runtime — every
  LLM call, tool call, input, output, error.
- Entire checkpoints: which coding-agent session produced each commit, with
  transcripts of what it was asked to do.
- Entire graph + file access: the current source code and entity-level
  changes per commit.

Method:
1. Inspect the trace. Find the span where the failure surfaced (error
   status, wrong output, suspicious tool result, retry loop).
2. Read that span's payload — compare what went in vs what came out.
3. Form a hypothesis about the root cause (bad code, bad data, bad prompt,
   tool contract violation).
4. If code is implicated: locate it with search_code, then use
   list_checkpoints / inspect_checkpoint / show_commit_changes to find
   WHICH commit and agent session introduced it. Read the transcript if
   the intent matters.
5. Call write_diagnosis exactly once with evidence pointers a reviewer can
   verify (span ids, checkpoint ids, commit SHAs, file:line).

Rules:
- Evidence over speculation — every claim needs a pointer a human can check.
- Prefer the smallest sufficient explanation.
- If evidence is missing (e.g. no checkpoint for a commit), say so."""


@neatlogs.span(kind="WORKFLOW")
def diagnose(question: str, repo_dir: str = ".") -> str:
    """Investigate one failure described by `question` against `repo_dir`."""
    tools.set_repo_dir(repo_dir)
    client = llm.make_client()
    goal = (
        f"Investigate this failure and produce a diagnosis.\n\n"
        f"Failure report: {question}\n"
        f"Target repository: {repo_dir}\n"
        f"If the report names a neatlogs trace id, start there. Otherwise "
        f"list recent traces and pick the failing one that matches."
    )
    return toolcall.run_agent(
        client, llm.DEBUGGER_MODEL, SYSTEM_PROMPT, tools.TOOLS, goal
    )
