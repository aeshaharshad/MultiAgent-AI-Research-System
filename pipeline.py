from agents import build_search_agent, build_reader_agent, writer_chain, critic_chain, invoke_with_retry


def run_research_pipeline(topic: str) -> dict:
    state = {}

    # ── Step 1: Search Agent ──────────────────────────────────────────────────
    print("\n" + "=" * 50)
    print("  STEP 1 — Search Agent is working...")
    print("=" * 50)

    search_agent = build_search_agent()
    search_result = invoke_with_retry(search_agent, {
        "messages": [("user", f"Find recent, reliable and detailed information about: {topic}")]
    })
    state["search_results"] = search_result["messages"][-1].content
    print("\n Search Results:\n", state["search_results"])

    # ── Step 2: Reader Agent ──────────────────────────────────────────────────
    print("\n" + "=" * 50)
    print("  STEP 2 — Reader Agent is scraping top resources...")
    print("=" * 50)

    reader_agent = build_reader_agent()
    reader_result = invoke_with_retry(reader_agent, {
        "messages": [("user",
            f"Based on the following search results about '{topic}', "
            f"pick the most relevant URL and scrape it for deeper content.\n\n"
            f"Search Results:\n{state['search_results'][:800]}"
        )]
    })
    state["scraped_content"] = reader_result["messages"][-1].content
    print("\n Scraped Content:\n", state["scraped_content"])

    # ── Step 3: Writer Chain ──────────────────────────────────────────────────
    print("\n" + "=" * 50)
    print("  STEP 3 — Writer is drafting the report...")
    print("=" * 50)

    research_combined = (
        f"SEARCH RESULTS:\n{state['search_results']}\n\n"
        f"DETAILED SCRAPED CONTENT:\n{state['scraped_content']}"
    )
    state["report"] = writer_chain.invoke({
        "topic": topic,
        "research": research_combined
    })
    print("\n Final Report:\n", state["report"])

    # ── Step 4: Critic Chain ──────────────────────────────────────────────────
    print("\n" + "=" * 50)
    print("  STEP 4 — Critic is reviewing the report...")
    print("=" * 50)

    state["feedback"] = critic_chain.invoke({
        "report": state["report"]
    })
    print("\n Critic Feedback:\n", state["feedback"])

    print("\n" + "=" * 50)
    print("  PIPELINE COMPLETE")
    print("=" * 50)

    return state


if __name__ == "__main__":
    topic = input("\n Enter a research topic: ")
    run_research_pipeline(topic)