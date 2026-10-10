"""Closed loop: after write_diagnosis, hand the suggested fix to a coding
agent (OpenCode — so the fix itself lands as an Entire checkpoint), commit,
and re-run the target agent to verify.
"""

import json
import os
import shutil
import subprocess
import time
from pathlib import Path

_ENTIRE_BIN = Path.home() / ".local" / "bin"


def _env() -> dict:
    env = dict(os.environ)
    env["PATH"] = str(_ENTIRE_BIN) + os.pathsep + env.get("PATH", "")
    return env


def apply_fix(diag_path: str, repo_dir: str) -> None:
    diag = json.loads(Path(diag_path).read_text(encoding="utf-8"))
    prompt = (
        "Apply this debugging fix to the repository.\n\n"
        f"Root cause: {diag['root_cause'][:800]}\n\n"
        f"Suggested fix: {diag['suggested_fix']}\n\n"
        "Make the minimal change — nothing else."
    )
    exe = shutil.which("opencode.cmd") or shutil.which("opencode")
    if not exe:
        raise RuntimeError("opencode CLI not found on PATH")
    flat_prompt = " ".join(prompt.split())
    proc = subprocess.run(
        [exe, "run", "--title", "Autopsy fix", flat_prompt],
        cwd=repo_dir, env=_env(), capture_output=True, text=True,
        timeout=900, shell=True,
    )
    print(proc.stdout[-3000:] or proc.stderr[-2000:])

    subprocess.run(["git", "add", "-A"], cwd=repo_dir, check=True)
    commit = subprocess.run(
        ["git", "commit", "-m", "Apply fix suggested by Autopsy diagnosis"],
        cwd=repo_dir, capture_output=True, text=True,
    )
    if commit.returncode != 0:
        print("(no changes to commit — fix may already be applied)")
        return
    print(commit.stdout.strip().splitlines()[0])
    push = subprocess.run(
        ["git", "push", "origin", "HEAD"],
        cwd=repo_dir, capture_output=True, text=True,
    )
    if push.returncode != 0:
        # transient remote rejections happen — retry once
        push = subprocess.run(
            ["git", "push", "origin", "HEAD"],
            cwd=repo_dir, capture_output=True, text=True,
        )
    print((push.stdout + push.stderr).strip()[-400:])


def verify(cmd: str, repo_dir: str) -> None:
    proc = subprocess.run(
        cmd, cwd=repo_dir, shell=True, env=_env(),
        capture_output=True, text=True, timeout=600,
    )
    print("\n===== VERIFICATION =====")
    print(proc.stdout[-3000:])
    if proc.returncode != 0:
        print(proc.stderr[-1000:])


def _recent_trace_ids() -> list[dict]:
    from . import neatlogs_api

    return (neatlogs_api.list_traces(limit=15).get("data") or {}).get(
        "traces", []
    )


def watch(repo_dir: str, interval: int = 30, fix: bool = False) -> None:
    """Poll neatlogs for newly finished traces and auto-diagnose each one —
    a regression gate: any agent run that ends gets audited immediately.
    Skips the debugger's own 'agent-debugger' workflow to avoid recursion.
    """
    from . import neatlogs_api
    from .agent import diagnose

    seen = {t.get("traceId") for t in _recent_trace_ids()}
    print(f"[watch] polling every {interval}s — seeded {len(seen)} existing traces")
    while True:
        time.sleep(interval)
        for t in _recent_trace_ids():
            tid = t.get("traceId")
            if not tid or tid in seen:
                continue
            seen.add(tid)
            meta = (neatlogs_api.get_trace(tid).get("data") or {})
            wf = meta.get("workflowName") or meta.get("workflow_name") or "?"
            if "agent-debugger" in str(wf):
                print(f"[watch] skipping own investigation trace {tid[:8]}")
                continue
            status = meta.get("status", "?")
            print(f"\n[watch] new trace {tid[:12]}… workflow={wf} status={status} — auditing")
            answer = diagnose(
                f"Audit freshly finished trace {tid} (workflow '{wf}', status "
                f"'{status}'). If it failed, produced a wrong/incomplete "
                f"result, or looks anomalous, find the root cause and culprit "
                f"change. If it's healthy, say so with evidence.",
                repo_dir=repo_dir,
            )
            print(answer)
            if fix:
                apply_fix(os.environ.get("DIAGNOSIS_OUT", "diagnosis.json"), repo_dir)
