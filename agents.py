from langgraph.prebuilt import create_react_agent
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from tools import web_search, scrape_url
from dotenv import load_dotenv
import os
import time

load_dotenv()


# ── Retry wrapper class for chains ────────────────────────────────────────────
class RetryChain:
    def __init__(self, chain, retries=3, wait=65):
        self.chain = chain
        self.retries = retries
        self.wait = wait

    def invoke(self, inputs):
        for attempt in range(self.retries):
            try:
                return self.chain.invoke(inputs)
            except Exception as e:
                err = str(e).lower()
                if "rate limit" in err or "429" in err or "too many" in err:
                    print(f"[Retry {attempt+1}/{self.retries}] Rate limit hit. Waiting {self.wait}s...")
                    time.sleep(self.wait)
                else:
                    raise e
        raise Exception("Groq rate limit: max retries exceeded. Please wait a few minutes and try again.")


# ── Retry wrapper for agents ──────────────────────────────────────────────────
def invoke_with_retry(agent, inputs, retries=3, wait=65):
    for attempt in range(retries):
        try:
            return agent.invoke(inputs)
        except Exception as e:
            err = str(e).lower()
            if "rate limit" in err or "429" in err or "too many" in err:
                print(f"[Retry {attempt+1}/{retries}] Rate limit hit. Waiting {wait}s...")
                time.sleep(wait)
            else:
                raise e
    raise Exception("Groq rate limit: max retries exceeded. Please wait a few minutes and try again.")


# ── LLM setup ─────────────────────────────────────────────────────────────────
# Using 8b model — much higher rate limits on Groq free tier than 70b
llm = ChatGroq(
    model="llama-3.1-8b-instant",
    temperature=0,
    api_key=os.getenv("GROQ_API_KEY"),
)


# ── Agents ────────────────────────────────────────────────────────────────────
def build_search_agent():
    return create_react_agent(model=llm, tools=[web_search])

def build_reader_agent():
    return create_react_agent(model=llm, tools=[scrape_url])


# ── Writer chain ──────────────────────────────────────────────────────────────
writer_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are an expert research writer. Write clear, structured and insightful reports."),
    ("human", """Write a detailed research report on the topic below.

Topic: {topic}

Research Gathered:
{research}

Structure the report as:
- Introduction
- Key Findings (minimum 3 well-explained points)
- Conclusion
- Sources (list all URLs found in the research)

Be detailed, factual and professional."""),
])

_writer_chain = writer_prompt | llm | StrOutputParser()
writer_chain = RetryChain(_writer_chain)


# ── Critic chain ──────────────────────────────────────────────────────────────
critic_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a sharp and constructive research critic. Be honest and specific."),
    ("human", """Review the research report below and evaluate it strictly.

Report:
{report}

Respond in this exact format:

Score: X/10

Strengths:
- ...
- ...

Areas to Improve:
- ...
- ...

One line verdict:
..."""),
])

_critic_chain = critic_prompt | llm | StrOutputParser()
critic_chain = RetryChain(_critic_chain)