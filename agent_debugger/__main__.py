"""CLI:  python -m agent_debugger "failure report" [--repo PATH]

Examples:
    python -m agent_debugger "trace 99687ab0... returned a wrong answer"
    python -m agent_debugger "the demo agent answered Ankara for the flag question" --repo .
"""

import argparse
import os
import sys

import neatlogs
from config import init_neatlogs


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    parser = argparse.ArgumentParser(prog="agent_debugger")
    parser.add_argument(
        "question", nargs="?", default="", help="failure report / what to investigate"
    )
    parser.add_argument("--repo", default=".", help="target repo (default: cwd)")
    parser.add_argument(
        "--fix",
        action="store_true",
        help="after diagnosis, apply the suggested fix via an OpenCode "
             "session (lands as its own Entire checkpoint) and commit it",
    )
    parser.add_argument(
        "--verify",
        metavar="CMD",
        help="shell command to re-run after the fix (implies --fix)",
    )
    parser.add_argument(
        "--watch",
        type=int,
        nargs="?",
        const=30,
        metavar="SEC",
        help="monitor mode: poll neatlogs every SEC (default 30) and "
             "auto-diagnose each newly finished trace",
    )
    args = parser.parse_args()

    if args.watch is not None:
        init_neatlogs(workflow_name="agent-debugger")
        from agent_debugger import pipeline

        pipeline.watch(args.repo, args.watch, fix=args.fix)
        return
    if not args.question:
        parser.error("question is required unless --watch is used")

    init_neatlogs(workflow_name="agent-debugger")
    from agent_debugger.agent import diagnose

    answer = diagnose(args.question, repo_dir=args.repo)
    print("\n===== DIAGNOSIS =====\n")
    print(answer)

    if args.fix or args.verify:
        from agent_debugger import pipeline

        pipeline.apply_fix(
            os.environ.get("DIAGNOSIS_OUT", "diagnosis.json"), args.repo
        )
        if args.verify:
            pipeline.verify(args.verify, args.repo)

    neatlogs.flush()
    neatlogs.shutdown()


if __name__ == "__main__":
    main()
