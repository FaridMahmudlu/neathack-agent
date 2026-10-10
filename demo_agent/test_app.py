"""Regression tests for demo_agent.app module."""

from demo_agent.app import search_docs


def test_search_docs_azerbaijan_flag_returns_best_match_first():
    """Regression test: search_docs('Azerbaijan flag') must return
    flag-of-azerbaijan as the first result.
    
    This prevents silent re-introduction of the reverse=False bug
    where results were returned in ascending (worst-match-first) order.
    """
    result = search_docs("Azerbaijan flag")
    lines = result.strip().split("\n")
    first_result = lines[0].split(":")[0]  # Extract the page title from the first line
    assert first_result == "flag-of-azerbaijan", (
        f"Expected 'flag-of-azerbaijan' to be first result, but got '{first_result}'. "
        f"Full results:\n{result}"
    )
