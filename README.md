# ResearchMind 🔬
### A Multi-Agent AI Research Pipeline

ResearchMind is an agentic system where four specialized AI agents collaborate to autonomously search, scrape, write, and critique research reports on any topic — end to end, with no human in the loop.

---

ResearchMind directly demonstrates:
- **Orchestration** — agents are chained in a defined pipeline, each with a single responsibility
- **Specialization** — each agent uses only the tools it needs (search vs. scrape)
- **Information extraction** — raw web content is transformed into structured, readable reports
- **Critique & quality control** — a dedicated critic agent evaluates output before it reaches the user

---

## Architecture

```
User Input (Topic)
        │
        ▼
┌──────────────────┐
│  Search Agent    │  ← Tavily web search tool
│  (LangGraph)     │
└────────┬─────────┘
         │ search results + URLs
         ▼
┌──────────────────┐
│  Reader Agent    │  ← BeautifulSoup scraper tool
│  (LangGraph)     │
└────────┬─────────┘
         │ scraped deep content
         ▼
┌──────────────────┐
│  Writer Chain    │  ← LLM prompt chain
│  (LangChain)     │
└────────┬─────────┘
         │ structured report
         ▼
┌──────────────────┐
│  Critic Chain    │  ← LLM prompt chain
│  (LangChain)     │
└────────┬─────────┘
         │ score + feedback
         ▼
    Final Output
```

---

## Tech Stack

| Layer | Technology |
|---|---|
| LLM | Groq (`llama-3.1-8b-instant`) |
| Agent Framework | LangGraph `create_react_agent` |
| Chain Framework | LangChain LCEL |
| Web Search | Tavily API |
| Web Scraping | Requests + BeautifulSoup4 |
| UI | Streamlit |
| Env Management | python-dotenv |

---

## Project Structure

```
researchmind/
├── app.py          # Streamlit UI — pipeline runner and results display
├── agents.py       # LLM setup, agent builders, writer/critic chains, retry logic
├── tools.py        # LangChain tools: web_search (Tavily) and scrape_url (BS4)
├── pipeline.py     # CLI version of the full pipeline
├── .env            # API keys 
└── requirements.txt
```

---

## Setup

```bash
git clone
cd researchmind
pip install -r requirements.txt
```

Create a `.env` file:
```
GROQ_API_KEY=your_groq_key
TAVILY_API_KEY=your_tavily_key
```

Run the app:
```bash
streamlit run app.py
```

Or run via CLI:
```bash
python pipeline.py
```

---

## Key Design Decisions

**Rate limit resilience** — All LLM and agent calls are wrapped in a `RetryChain` / `invoke_with_retry` layer that automatically waits and retries on Groq rate limit errors, making the pipeline robust for deployment.

**Separation of concerns** — Tools, agents, chains, and UI are in separate files. Swapping the LLM provider or adding a new agent requires changing one file only.

**Modular agent design** — Each agent is stateless and single-purpose. 

---

## Requirements

```
streamlit
langchain
langchain-groq
langchain-community
langgraph
tavily-python
beautifulsoup4
requests
python-dotenv
```
