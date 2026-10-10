"""Tools the debugger agent can call. Every function doubles as a neatlogs
TOOL span, so the debugger's own investigation is traced end to end.
"""

import json
import os
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
    spans = spans_payload.get("data", spans_payload)
    if isinstance(spans, dict):
        spans = spans.get("spans") or spans.get("items") or list(spans.values())
    if not isinstance(spans, list):
        return [{"raw": spans}]
    summary = []
    for s in spans:
        if not isinstance(s, dict):
            summary.append({"raw": s})
            continue
        attrs = s.get("attributes") or {}
        summary.append(
            {
                "span_id": s.get("spanId") or s.get("span_id") or s.get("id"),
                "parent": s.get("parentSpanId") or s.get("parent_span_id"),
                "name": s.get("name") or attrs.get("neatlogs.span.name"),
                "kind": s.get("kind") or attrs.get("neatlogs.span.kind"),
                "status": s.get("status") or s.get("statusCode"),
                "start": s.get("startTime") or s.get("start_time"),
                "duration_ms": s.get("durationMs") or s.get("duration_ms"),
                "error": s.get("error") or attrs.get("error.message"),
                "model": attrs.get("gen_ai.request.model") or attrs.get("llm.model"),
                "tokens": attrs.get("gen_ai.usage.total_tokens")
                or attrs.get("llm.usage.total_tokens"),
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
    list_checkpoints,
    inspect_checkpoint,
    read_checkpoint_transcript,
    search_code,
    show_commit_changes,
    read_source_file,
    write_diagnosis,
]
