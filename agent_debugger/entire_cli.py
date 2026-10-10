"""Thin wrapper over the Entire CLI for checkpoint and code-graph queries."""

import shutil
import subprocess
from pathlib import Path

_TIMEOUT = 120


def _entire() -> str:
    exe = shutil.which("entire")
    if exe:
        return exe
    for candidate in (
        Path.home() / ".local" / "bin" / "entire.exe",
        Path.home() / ".local" / "bin" / "entire",
    ):
        if candidate.exists():
            return str(candidate)
    raise RuntimeError("entire CLI not found on PATH or in ~/.local/bin")


def _run(args: list[str], cwd: str) -> str:
    proc = subprocess.run(
        [_entire(), *args],
        cwd=cwd,
        capture_output=True,
        text=True,
        timeout=_TIMEOUT,
    )
    if proc.returncode != 0:
        detail = (proc.stderr or proc.stdout).strip()
        return f"[entire exited {proc.returncode}] {detail}"
    return proc.stdout


def checkpoint_list(repo_dir: str, limit: int = 10) -> str:
    return _run(["checkpoint", "list", "--json", "--limit", str(limit)], repo_dir)


def checkpoint_explain(ref: str, repo_dir: str) -> str:
    return _run(["checkpoint", "explain", ref, "--json"], repo_dir)


def checkpoint_transcript(ref: str, repo_dir: str) -> str:
    return _run(["checkpoint", "explain", ref, "--transcript"], repo_dir)


def graph_search(query: str, repo_dir: str) -> str:
    return _run(["graph", "search", query], repo_dir)


def graph_commit(ref: str, repo_dir: str) -> str:
    return _run(["graph", "commit", ref], repo_dir)
