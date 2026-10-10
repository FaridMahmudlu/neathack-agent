"""A tiny research agent: answers a question using two tools over a small
offline corpus. It is the *target* the debugger investigates — its own
runs are traced to neatlogs under workflow 'demo-research-agent'.
"""

import neatlogs

from common import llm, toolcall

PAGES = {
    "flag-of-azerbaijan": (
        "The national flag of Azerbaijan is a horizontal tricolour of blue, "
        "red, and green, with a white crescent and an eight-pointed star in "
        "the centre. It was readopted in 1991 after independence."
    ),
    "baku": (
        "Baku is the capital and largest city of Azerbaijan, located on the "
        "Absheron Peninsula along the Caspian Sea. Its population is about "
        "2.3 million."
    ),
    "flag-of-turkiye": (
        "The flag of Turkiye is red with a white crescent and a five-pointed "
        "star. It should not be confused with the eight-pointed star of "
        "Azerbaijan's flag."
    ),
    "crescent-symbolism": (
        "The crescent appears on several national flags, including those of "
        "Turkiye, Azerbaijan, Pakistan, and Algeria."
    ),
}


def _score(query: str, text: str) -> int:
    q = {w.strip(".,?").lower() for w in query.split() if len(w) > 3}
    words = {w.strip(".,:;()").lower() for w in text.split()}
    return len(q & words)


@neatlogs.span(kind="TOOL", tool_name="search_docs")
def search_docs(query: str) -> str:
    """Search the offline corpus. Returns the most relevant page titles
    ranked by keyword relevance, best first.

    Args:
        query: plain-language search query.
    """
    scored = sorted(PAGES.items(), key=lambda kv: _score(query, kv[1]), reverse=True)
    return "\n".join(f"{title}: {text[:80]}…" for title, text in scored[:3])


@neatlogs.span(kind="TOOL", tool_name="fetch_page")
def fetch_page(title: str) -> str:
    """Fetch the full text of a corpus page by its title.

    Args:
        title: page title as returned by search_docs.
    """
    return PAGES.get(title, f"error: no page titled {title!r}")


SYSTEM_PROMPT = (
    "You are a research agent. Answer the question using ONLY the "
    "search_docs and fetch_page tools — never your own knowledge. "
    "Cite the page titles you relied on."
)


@neatlogs.span(kind="WORKFLOW")
def run(question: str) -> str:
    client = llm.make_client()
    return toolcall.run_agent(
        client, llm.DEMO_MODEL, SYSTEM_PROMPT, [search_docs, fetch_page], question
    )
