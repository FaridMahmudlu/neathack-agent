"""Tools the debugger agent can call. Every function doubles as a neatlogs
TOOL span, so the debugger's own investigation is traced end to end.
"""

import json
import os
import subprocess
from pathlib import Path

import neatlogs

from . import entire_cli, neatlogs_api

_REPO_DIR = "."
_CAP = 8000


def set_repo_dir(path: str) -> None:
    global _REPO_DIR
    _REPO_DIR = path


def _clip(payload) -> str:
    text = payload if isinstance(payload, str) else json.dumps(payload, default=str)
    return text if len(text) <= _CAP else text[:_CAP] + f"\n…[truncated {len(text) - _CAP} chars]"


def _summarize_spans(spans_payload) -> list[dict]:
    spans = (spans_payload.get("data") or {}).get("spans") or []
    summary = []
    for s in spans:
        if not isinstance(s, dict):
            summary.append({"raw": s})
            continue
        summary.append(
            {
                "span_id": s.get("spanId"),
                "parent": s.get("parentSpanId"),
                "name": s.get("spanName"),
                "kind": s.get("spanType"),
                "status": s.get("status"),
                "start": s.get("startedAt"),
                "duration_ms": s.get("durationMs"),
                "model": s.get("model") or s.get("spanName"),
                "provider": s.get("provider"),
                "tokens": s.get("totalTokens"),
                "cost_usd": s.get("costUsd"),
            }
        )
    return summary


@neatlogs.span(kind="TOOL", tool_name="list_recent_traces")
def list_recent_traces(workflow_name: str = "", limit: int = 10) -> str:
    """List recent agent runs recorded in neatlogs.

    Args:
        workflow_name: optional workflow name filter (e.g. 'demo-research-agent').
        limit: max traces to return (default 10).

    Returns JSON array of traces with id, workflow, status and timing.
    """
    data = neatlogs_api.list_traces(limit=min(limit, 50), workflow_name=workflow_name or None)
    return _clip(data)


@neatlogs.span(kind="TOOL", tool_name="inspect_trace")
def inspect_trace(trace_id: str) -> str:
    """Fetch one trace: metadata plus a summary of every span inside it
    (order, kind, status, errors, model, tokens). Use this to locate the
    step where the run went wrong.

    Args:
        trace_id: the neatlogs trace UUID.
    """
    trace = neatlogs_api.get_trace(trace_id)
    spans = _summarize_spans(neatlogs_api.list_spans(trace_id))
    return _clip({"trace": trace.get("data", trace), "spans": spans})


@neatlogs.span(kind="TOOL", tool_name="read_span_payload")
def read_span_payload(trace_id: str, span_id: str) -> str:
    """Read the full recorded input/output of one span — the actual prompt,
    tool arguments, or model response.

    Args:
        trace_id: the neatlogs trace UUID.
        span_id: the span whose payload to read.
    """
    return _clip(neatlogs_api.get_span_payload(trace_id, span_id))


@neatlogs.span(kind="TOOL", tool_name="list_checkpoints")
def list_checkpoints(limit: int = 10) -> str:
    """List Entire checkpoints in the target repository — each links a commit
    to the coding-agent session and decisions behind it.

    Args:
        limit: max checkpoints (default 10).
    """
    return _clip(entire_cli.checkpoint_list(_REPO_DIR, limit))


@neatlogs.span(kind="TOOL", tool_name="inspect_checkpoint")
def inspect_checkpoint(ref: str) -> str:
    """Explain one Entire checkpoint (by checkpoint ID or commit SHA): which
    files changed, the agent session that produced it, and the stated intent.

    Args:
        ref: checkpoint ID or commit SHA.
    """
    return _clip(entire_cli.checkpoint_explain(ref, _REPO_DIR))


@neatlogs.span(kind="TOOL", tool_name="read_checkpoint_transcript")
def read_checkpoint_transcript(ref: str) -> str:
    """Read the raw agent-session transcript attached to a checkpoint — what
    the coding agent was asked to do and what it decided.

    Args:
        ref: checkpoint ID or commit SHA.
    """
    return _clip(entire_cli.checkpoint_transcript(ref, _REPO_DIR))


@neatlogs.span(kind="TOOL", tool_name="search_code")
def search_code(query: str) -> str:
    """Semantic code search over the target repository via the Entire graph —
    find where a behavior is implemented from a plain-language description.

    Args:
        query: plain-language description, e.g. 'search result ranking'.
    """
    return _clip(entire_cli.graph_search(query, _REPO_DIR))


@neatlogs.span(kind="TOOL", tool_name="show_commit_changes")
def show_commit_changes(ref: str) -> str:
    """Show entity-level changes introduced by a commit (added/modified
    symbols) via the Entire graph — what the commit actually changed in code.

    Args:
        ref: commit SHA or ref like HEAD~1.
    """
    return _clip(entire_cli.graph_commit(ref, _REPO_DIR))


@neatlogs.span(kind="TOOL", tool_name="compare_traces")
def compare_traces(trace_id_a: str, trace_id_b: str) -> str:
    """Compare two runs side by side — e.g. a known-good trace vs a failing
    one. Returns both span summaries plus a structural diff: tool-call
    counts, which spans appear/disappear, and token deltas.

    Args:
        trace_id_a: first (usually baseline/healthy) trace UUID.
        trace_id_b: second (usually failing) trace UUID.
    """
    a = _summarize_spans(neatlogs_api.list_spans(trace_id_a))
    b = _summarize_spans(neatlogs_api.list_spans(trace_id_b))

    def tool_calls(spans):
        return [s for s in spans if s.get("kind") == "TOOL"]

    return _clip(
        {
            "trace_a": {"id": trace_id_a, "spans": a, "tool_calls": len(tool_calls(a))},
            "trace_b": {"id": trace_id_b, "spans": b, "tool_calls": len(tool_calls(b))},
            "note": "compare span names, statuses, tool-call patterns and token usage between the two runs",
        }
    )


@neatlogs.span(kind="TOOL", tool_name="find_similar_failures")
def find_similar_failures(query: str, limit: int = 10) -> str:
    """Semantic search over past traces — find earlier runs that failed in
    a similar way. Use to check whether this failure is recurring and how
    it was resolved before.

    Args:
        query: natural-language description of the failure, e.g.
            'agent returned incomplete answer citing missing context'.
        limit: max results (default 10).
    """
    return _clip(neatlogs_api.search_traces_semantic(query, limit=min(limit, 50)))


def _git(*args: str) -> str:
    proc = subprocess.run(
        ["git", *args], cwd=_REPO_DIR, capture_output=True, text=True, timeout=30
    )
    if proc.returncode != 0:
        return f"[git exited {proc.returncode}] {(proc.stderr or '').strip()}"
    return proc.stdout


@neatlogs.span(kind="TOOL", tool_name="list_recent_commits")
def list_recent_commits(limit: int = 10) -> str:
    """List recent commits in the target repository — SHA, subject, and the
    files each commit touched. Use this to attribute a suspicious function
    to the exact commit that changed it (ground truth, not inference).

    Args:
        limit: max commits (default 10).
    """
    return _clip(_git("log", f"-{min(limit, 30)}", "--format=%H %s", "--name-only"))


@neatlogs.span(kind="TOOL", tool_name="show_commit_diff")
def show_commit_diff(ref: str) -> str:
    """Show the actual code diff a commit introduced (git show) — the ground
    truth of what changed, line by line.

    Args:
        ref: commit SHA or ref like HEAD~1.
    """
    return _clip(_git("show", ref, "--format=%H %s%n%b"))


@neatlogs.span(kind="TOOL", tool_name="read_source_file")
def read_source_file(path: str) -> str:
    """Read a source file from the target repository (max 400 lines).

    Args:
        path: file path relative to the repository root.
    """
    root = Path(_REPO_DIR).resolve()
    target = (root / path).resolve()
    if root not in target.parents and target != root:
        return "error: path escapes repository root"
    if not target.is_file():
        return f"error: {path} is not a file"
    lines = target.read_text(encoding="utf-8", errors="replace").splitlines()
    body = "\n".join(f"{i + 1}| {line}" for i, line in enumerate(lines[:400]))
    return body if len(body) <= _CAP else body[:_CAP] + "\n…[file truncated]"


@neatlogs.span(kind="TOOL", tool_name="write_diagnosis")
def write_diagnosis(
    root_cause: str,
    failing_step: str,
    culprit_change: str,
    evidence: list[str],
    suggested_fix: str,
) -> str:
    """Emit the final structured diagnosis. Call exactly once, when the
    investigation is complete.

    Args:
        root_cause: one-paragraph root-cause explanation.
        failing_step: the trace step/span where the failure surfaced.
        culprit_change: the commit/checkpoint that introduced the cause,
            or 'none' if the cause is purely runtime.
        evidence: list of concrete evidence pointers (span ids, checkpoint
            ids, file:line, commit SHAs).
        suggested_fix: concrete fix proposal.
    """
    report = {
        "root_cause": root_cause,
        "failing_step": failing_step,
        "culprit_change": culprit_change,
        "evidence": evidence,
        "suggested_fix": suggested_fix,
    }
    Path(os.environ.get("DIAGNOSIS_OUT", "diagnosis.json")).write_text(
        json.dumps(report, indent=2), encoding="utf-8"
    )
    return json.dumps(report, indent=2)


TOOLS = [
    list_recent_traces,
    inspect_trace,
    read_span_payload,
    compare_traces,
    find_similar_failures,
    list_checkpoints,
    inspect_checkpoint,
    read_checkpoint_transcript,
    search_code,
    show_commit_changes,
    list_recent_commits,
    show_commit_diff,
    read_source_file,
    write_diagnosis,
]
