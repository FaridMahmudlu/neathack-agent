"""CLI:  python -m agent_debugger "failure report" [--repo PATH]

Examples:
    python -m agent_debugger "trace 99687ab0... returned a wrong answer"
    python -m agent_debugger "the demo agent answered Ankara for the flag question" --repo .
"""

import argparse
import sys

import neatlogs
from config import init_neatlogs


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    parser = argparse.ArgumentParser(prog="agent_debugger")
    parser.add_argument("question", help="failure report / what to investigate")
    parser.add_argument("--repo", default=".", help="target repo (default: cwd)")
    args = parser.parse_args()

    init_neatlogs(workflow_name="agent-debugger")
    from agent_debugger.agent import diagnose

    answer = diagnose(args.question, repo_dir=args.repo)
    print("\n===== DIAGNOSIS =====\n")
    print(answer)

    neatlogs.flush()
    neatlogs.shutdown()


if __name__ == "__main__":
    main()
