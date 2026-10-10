"""Minimal read-only client for the neatlogs Public API.

Requires a service-account token: the SDK ingest key cannot read traces.
Settings -> Service Accounts -> bind project -> mint token with
context:read + observability:read -> NEATLOGS_TOKEN in .env
"""

import os

import httpx

BASE_URL = os.environ.get("NEATLOGS_API_URL", "https://app.neatlogs.com")
API = f"{BASE_URL}/api/v1/public"


def _headers() -> dict:
    token = os.environ.get("NEATLOGS_TOKEN")
    if not token:
        raise RuntimeError(
            "NEATLOGS_TOKEN is not set. Mint a service-account token in "
            "neatlogs Settings -> Service Accounts with context:read and "
            "observability:read, then put it in .env"
        )
    headers = {"Authorization": f"Bearer {token}"}
    project = os.environ.get("NEATLOGS_PROJECT_ID")
    if project:
        headers["x-project-id"] = project
    return headers


def _get(path: str, **params):
    r = httpx.get(f"{API}{path}", headers=_headers(), params=params, timeout=30)
    r.raise_for_status()
    return r.json()


def _post(path: str, body: dict):
    r = httpx.post(f"{API}{path}", headers=_headers(), json=body, timeout=30)
    r.raise_for_status()
    return r.json()


def list_traces(limit: int = 10, workflow_name: str | None = None) -> dict:
    params: dict = {"limit": limit}
    if workflow_name:
        params["workflowName"] = workflow_name
    return _get("/traces", **params)


def get_trace(trace_id: str) -> dict:
    return _get(f"/traces/{trace_id}")


def list_spans(trace_id: str) -> dict:
    return _get(f"/traces/{trace_id}/spans")


def get_span_payload(trace_id: str, span_id: str) -> dict:
    return _get(
        f"/traces/{trace_id}/spans/{span_id}/payload",
        fields="input,output,error",
    )


def search_traces_semantic(
    q: str, limit: int = 10, workflow_name: str | None = None
) -> dict:
    body: dict = {"q": q, "limit": min(limit, 50)}
    if workflow_name:
        body["workflowName"] = workflow_name
    return _post("/search/traces/semantic", body)
