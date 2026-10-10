"""CLI:  python -m demo_agent "question"
"""

import argparse
import sys

import neatlogs
from config import init_neatlogs


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    parser = argparse.ArgumentParser(prog="demo_agent")
    parser.add_argument(
        "question",
        nargs="?",
        default="What is the capital of the country whose flag shows a "
        "crescent and an eight-pointed star?",
    )
    args = parser.parse_args()

    init_neatlogs(workflow_name="demo-research-agent")
    from demo_agent.app import run

    answer = run(args.question)
    print("\n===== ANSWER =====\n")
    print(answer)

    neatlogs.flush()
    neatlogs.shutdown()


if __name__ == "__main__":
    main()
