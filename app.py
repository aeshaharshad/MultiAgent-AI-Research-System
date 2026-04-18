import streamlit as st
import time
from agents import build_reader_agent, build_search_agent, writer_chain, critic_chain, invoke_with_retry

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="ResearchMind · AI Research Agent",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&family=Space+Grotesk:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
    color: #e2e0f0;
}
.stApp {
    background: #0d0d1a;
    background-image:
        radial-gradient(ellipse 90% 55% at 10% -10%, rgba(99,79,255,0.18) 0%, transparent 60%),
        radial-gradient(ellipse 60% 50% at 90% 110%, rgba(0,210,200,0.10) 0%, transparent 55%),
        radial-gradient(ellipse 50% 40% at 50% 50%, rgba(120,60,255,0.04) 0%, transparent 70%);
}
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding: 2rem 3rem 5rem; max-width: 1240px; }

.hero { text-align: center; padding: 4rem 0 2.8rem; }
.hero-eyebrow {
    display: inline-flex;
    align-items: center;
    gap: 0.5rem;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.68rem;
    font-weight: 500;
    letter-spacing: 0.3em;
    text-transform: uppercase;
    color: #00d4c8;
    background: rgba(0,212,200,0.08);
    border: 1px solid rgba(0,212,200,0.22);
    border-radius: 100px;
    padding: 0.35rem 1.1rem;
    margin-bottom: 1.5rem;
}
.hero h1 {
    font-family: 'Space Grotesk', sans-serif;
    font-size: clamp(2.6rem, 5.5vw, 4.8rem);
    font-weight: 700;
    line-height: 1.05;
    letter-spacing: -0.04em;
    color: #f0eeff;
    margin: 0 0 0.9rem;
}
.hero h1 em {
    font-style: normal;
    background: linear-gradient(135deg, #7c5bff 0%, #00d4c8 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}
.hero-sub {
    font-size: 1rem;
    font-weight: 400;
    color: #9b96c0;
    max-width: 500px;
    margin: 0 auto;
    line-height: 1.7;
}
.divider {
    height: 1px;
    background: linear-gradient(90deg, transparent, rgba(124,91,255,0.35), rgba(0,212,200,0.2), transparent);
    margin: 2.2rem 0;
}

.input-card {
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(124,91,255,0.22);
    border-radius: 18px;
    padding: 2rem 2.4rem 2.2rem;
    margin-bottom: 1.5rem;
    position: relative;
    overflow: hidden;
}
.input-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
    background: linear-gradient(90deg, #7c5bff, #00d4c8);
    border-radius: 18px 18px 0 0;
}

.stTextInput > label {
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.7rem !important;
    letter-spacing: 0.2em !important;
    text-transform: uppercase !important;
    color: #a090ff !important;
    font-weight: 500 !important;
    margin-bottom: 0.5rem !important;
}
.stTextInput > div > div > input {
    background: rgba(255,255,255,0.92) !important;
    border: 1.5px solid rgba(124,91,255,0.32) !important;
    border-radius: 12px !important;
    color: #1a1440 !important;
    -webkit-text-fill-color: #1a1440 !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 1rem !important;
    font-weight: 400 !important;
    padding: 0.82rem 1.1rem !important;
    caret-color: #7c5bff !important;
    transition: border-color 0.2s, box-shadow 0.2s, background 0.2s !important;
}
.stTextInput > div > div > input::placeholder {
    color: rgba(80,75,120,0.5) !important;
    -webkit-text-fill-color: rgba(80,75,120,0.5) !important;
}
.stTextInput > div > div > input:focus {
    border-color: #7c5bff !important;
    background: rgba(255,255,255,0.96) !important;
    box-shadow: 0 0 0 4px rgba(124,91,255,0.15) !important;
    outline: none !important;
}

.stButton > button {
    background: linear-gradient(135deg, #7c5bff 0%, #5b3de8 100%) !important;
    color: #ffffff !important;
    font-family: 'Space Grotesk', sans-serif !important;
    font-weight: 600 !important;
    font-size: 0.95rem !important;
    letter-spacing: 0.02em !important;
    border: none !important;
    border-radius: 12px !important;
    padding: 0.78rem 2rem !important;
    cursor: pointer !important;
    width: 100%;
    margin-top: 0.8rem;
    box-shadow: 0 4px 24px rgba(124,91,255,0.38) !important;
    transition: transform 0.15s, box-shadow 0.15s !important;
}
.stButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 34px rgba(124,91,255,0.48) !important;
}
.stButton > button:active { transform: translateY(0) !important; }

.chips-row {
    display: flex;
    gap: 0.5rem;
    align-items: center;
    flex-wrap: wrap;
    margin-bottom: 1.5rem;
}
.chips-label {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.65rem;
    color: #3e3960;
    letter-spacing: 0.12em;
}
.chip {
    background: rgba(124,91,255,0.08);
    border: 1px solid rgba(124,91,255,0.22);
    border-radius: 8px;
    padding: 0.28rem 0.78rem;
    font-size: 0.78rem;
    color: #b4aaee;
    font-family: 'Inter', sans-serif;
    cursor: default;
}

.section-heading {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 1.12rem;
    font-weight: 600;
    color: #f0eeff;
    margin: 1.8rem 0 0.9rem;
    letter-spacing: -0.02em;
}

.step-card {
    background: rgba(255,255,255,0.025);
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 14px;
    padding: 1.15rem 1.5rem;
    margin-bottom: 0.8rem;
    position: relative;
    overflow: hidden;
    transition: border-color 0.3s, background 0.3s;
}
.step-card::before {
    content: '';
    position: absolute;
    left: 0; top: 0; bottom: 0;
    width: 3px;
    background: rgba(255,255,255,0.06);
    transition: background 0.3s;
}
.step-card.active {
    border-color: rgba(124,91,255,0.42);
    background: rgba(124,91,255,0.055);
}
.step-card.active::before { background: #7c5bff; }
.step-card.done {
    border-color: rgba(0,212,200,0.3);
    background: rgba(0,212,200,0.04);
}
.step-card.done::before { background: #00d4c8; }

.step-header { display: flex; align-items: center; gap: 0.75rem; }
.step-num {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.64rem;
    font-weight: 500;
    letter-spacing: 0.15em;
    color: #7c5bff;
    opacity: 0.85;
}
.step-title {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 0.9rem;
    font-weight: 600;
    color: #e8e4ff;
}
.step-status {
    margin-left: auto;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.62rem;
    letter-spacing: 0.08em;
}
.status-waiting { color: #2e2a4a; }
.status-running { color: #a090ff; }
.status-done    { color: #00d4c8; }
.step-desc {
    font-size: 0.77rem;
    color: #5e5a80;
    margin-top: 0.18rem;
    padding-left: 2.05rem;
}

.stSpinner > div { color: #7c5bff !important; }

details > summary {
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.72rem !important;
    color: #9b96c0 !important;
    letter-spacing: 0.08em !important;
    cursor: pointer;
}

.result-panel {
    background: rgba(255,255,255,0.025);
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 14px;
    padding: 1.6rem 1.8rem;
    margin-top: 0.6rem;
    margin-bottom: 1.2rem;
}
.result-panel-title {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.64rem;
    font-weight: 500;
    letter-spacing: 0.22em;
    text-transform: uppercase;
    color: #7c5bff;
    margin-bottom: 0.85rem;
    padding-bottom: 0.65rem;
    border-bottom: 1px solid rgba(124,91,255,0.18);
}
.result-content {
    font-size: 0.87rem;
    line-height: 1.85;
    color: #c8c4e4;
    white-space: pre-wrap;
    font-family: 'Inter', sans-serif;
}

.report-panel {
    background: rgba(124,91,255,0.04);
    border: 1px solid rgba(124,91,255,0.22);
    border-radius: 18px;
    padding: 2rem 2.4rem;
    margin-top: 1rem;
    position: relative;
    overflow: hidden;
}
.report-panel::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
    background: linear-gradient(90deg, #7c5bff, #00d4c8);
}
.report-panel .panel-label {
    display: block;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.64rem;
    letter-spacing: 0.22em;
    text-transform: uppercase;
    color: #a090ff;
    margin-bottom: 1.2rem;
    padding-bottom: 0.65rem;
    border-bottom: 1px solid rgba(124,91,255,0.2);
}
.report-panel p, .report-panel li, .report-panel td, .report-panel th,
.report-panel span, .report-panel div {
    color: #e8e4ff !important;
    -webkit-text-fill-color: #e8e4ff !important;
    font-size: 0.96rem !important;
    line-height: 1.9 !important;
}
.report-panel h1, .report-panel h2, .report-panel h3,
.report-panel h4, .report-panel h5, .report-panel h6 {
    color: #ffffff !important;
    -webkit-text-fill-color: #ffffff !important;
    font-family: 'Space Grotesk', sans-serif !important;
    font-weight: 600 !important;
    letter-spacing: -0.02em !important;
    margin-top: 1.6rem !important;
}
.report-panel h2 { color: #c8beff !important; -webkit-text-fill-color: #c8beff !important; }
.report-panel strong, .report-panel b {
    color: #ffffff !important;
    -webkit-text-fill-color: #ffffff !important;
    font-weight: 600 !important;
}
.report-panel em { color: #b8b0f0 !important; -webkit-text-fill-color: #b8b0f0 !important; }
.report-panel ol li, .report-panel ul li {
    color: #e8e4ff !important;
    -webkit-text-fill-color: #e8e4ff !important;
}
.report-panel code {
    background: rgba(124,91,255,0.16) !important;
    color: #00d4c8 !important;
    -webkit-text-fill-color: #00d4c8 !important;
    padding: 0.15em 0.45em !important;
    border-radius: 6px !important;
    font-size: 0.86em !important;
    font-family: 'JetBrains Mono', monospace !important;
}
.report-panel blockquote {
    border-left: 3px solid #7c5bff !important;
    padding-left: 1rem !important;
    color: #9b96c0 !important;
    margin: 1rem 0 !important;
}
.report-panel a { color: #00d4c8 !important; -webkit-text-fill-color: #00d4c8 !important; }
.report-panel hr { border-color: rgba(124,91,255,0.2) !important; margin: 1.5rem 0 !important; }

.feedback-panel {
    background: rgba(0,212,200,0.03);
    border: 1px solid rgba(0,212,200,0.2);
    border-radius: 18px;
    padding: 2rem 2.4rem;
    margin-top: 1rem;
    position: relative;
    overflow: hidden;
}
.feedback-panel::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
    background: linear-gradient(90deg, #00d4c8, #7c5bff);
}
.feedback-panel .panel-label {
    display: block;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.64rem;
    letter-spacing: 0.22em;
    text-transform: uppercase;
    color: #00d4c8;
    margin-bottom: 1.2rem;
    padding-bottom: 0.65rem;
    border-bottom: 1px solid rgba(0,212,200,0.2);
}
.feedback-panel p, .feedback-panel li, .feedback-panel span, .feedback-panel div {
    color: #d0f5f3 !important;
    -webkit-text-fill-color: #d0f5f3 !important;
    font-size: 0.96rem !important;
    line-height: 1.88 !important;
}
.feedback-panel h1, .feedback-panel h2, .feedback-panel h3 {
    color: #e8fffe !important;
    -webkit-text-fill-color: #e8fffe !important;
    font-family: 'Space Grotesk', sans-serif !important;
    font-weight: 600 !important;
}
.feedback-panel strong, .feedback-panel b {
    color: #e8fffe !important;
    -webkit-text-fill-color: #e8fffe !important;
    font-weight: 600 !important;
}
.feedback-panel ol li, .feedback-panel ul li {
    color: #d0f5f3 !important;
    -webkit-text-fill-color: #d0f5f3 !important;
}
.feedback-panel code {
    background: rgba(0,212,200,0.12) !important;
    color: #00d4c8 !important;
    -webkit-text-fill-color: #00d4c8 !important;
    padding: 0.15em 0.45em !important;
    border-radius: 6px !important;
    font-family: 'JetBrains Mono', monospace !important;
}

.stDownloadButton > button {
    background: transparent !important;
    border: 1.5px solid rgba(0,212,200,0.35) !important;
    color: #00d4c8 !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.73rem !important;
    letter-spacing: 0.12em !important;
    border-radius: 10px !important;
    padding: 0.55rem 1.4rem !important;
    margin-top: 1.2rem;
    box-shadow: none !important;
    transition: background 0.2s, border-color 0.2s !important;
}
.stDownloadButton > button:hover {
    background: rgba(0,212,200,0.08) !important;
    border-color: rgba(0,212,200,0.55) !important;
}

.stAlert {
    border-radius: 12px !important;
    background: rgba(124,91,255,0.08) !important;
    border: 1px solid rgba(124,91,255,0.25) !important;
    color: #c8beff !important;
}

.notice {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.65rem;
    color: #252040;
    text-align: center;
    margin-top: 4rem;
    letter-spacing: 0.1em;
}
</style>
""", unsafe_allow_html=True)


# ── Step card helper ──────────────────────────────────────────────────────────
def step_card(num: str, title: str, state: str, desc: str = ""):
    status_map = {
        "waiting": ("WAITING",   "status-waiting"),
        "running": ("● RUNNING", "status-running"),
        "done":    ("✓ DONE",    "status-done"),
    }
    label, cls = status_map.get(state, ("", ""))
    card_cls = {"running": "active", "done": "done"}.get(state, "")
    st.markdown(f"""
    <div class="step-card {card_cls}">
        <div class="step-header">
            <span class="step-num">{num}</span>
            <span class="step-title">{title}</span>
            <span class="step-status {cls}">{label}</span>
        </div>
        {"<div class='step-desc'>" + desc + "</div>" if desc else ""}
    </div>
    """, unsafe_allow_html=True)


# ── Session state ─────────────────────────────────────────────────────────────
for key in ("results", "running", "done"):
    if key not in st.session_state:
        st.session_state[key] = {} if key == "results" else False


# ── Hero ──────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
    <div class="hero-eyebrow">◈ Multi-Agent AI System</div>
    <h1>Research<em>Mind</em></h1>
    <p class="hero-sub">
        Four specialized AI agents collaborate — searching, scraping, writing,
        and critiquing — to deliver a polished research report on any topic.
    </p>
</div>
<div class="divider"></div>
""", unsafe_allow_html=True)


# ── Layout ────────────────────────────────────────────────────────────────────
col_input, col_gap, col_pipeline = st.columns([5, 0.4, 4])

with col_input:
    st.markdown('<div class="input-card">', unsafe_allow_html=True)
    topic = st.text_input(
        "Research Topic",
        placeholder="e.g. Quantum computing breakthroughs in 2025",
        key="topic_input",
        label_visibility="visible",
    )
    run_btn = st.button("⚡  Run Research Pipeline", use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("""
    <div class="chips-row">
        <span class="chips-label">TRY →</span>
        <span class="chip">LLM agents 2025</span>
        <span class="chip">CRISPR gene editing</span>
        <span class="chip">Fusion energy progress</span>
    </div>
    """, unsafe_allow_html=True)

with col_pipeline:
    st.markdown('<div class="section-heading">Pipeline</div>', unsafe_allow_html=True)

    r = st.session_state.results

    def s(step):
        if not r:
            return "waiting"
        steps = ["search", "reader", "writer", "critic"]
        if step in r:
            return "done"
        if st.session_state.running:
            for k in steps:
                if k not in r:
                    return "running" if k == step else "waiting"
        return "waiting"

    step_card("01", "Search Agent",  s("search"), "Gathers recent web information")
    step_card("02", "Reader Agent",  s("reader"), "Scrapes & extracts deep content")
    step_card("03", "Writer Chain",  s("writer"), "Drafts the full research report")
    step_card("04", "Critic Chain",  s("critic"), "Reviews & scores the report")


# ── Run pipeline ──────────────────────────────────────────────────────────────
if run_btn:
    if not topic.strip():
        st.warning("Please enter a research topic first.")
    else:
        st.session_state.results = {}
        st.session_state.running = True
        st.session_state.done = False
        st.rerun()

if st.session_state.running and not st.session_state.done:
    results = {}
    topic_val = st.session_state.topic_input

    # ── Step 1: Search ────────────────────────────────────────────────────────
    with st.spinner("🔍  Search Agent is working…"):
        try:
            search_agent = build_search_agent()
            sr = invoke_with_retry(search_agent, {
                "messages": [("user", f"Find recent, reliable and detailed information about: {topic_val}")]
            })
            results["search"] = sr["messages"][-1].content
            st.session_state.results = dict(results)
        except Exception as e:
            st.error(f"⚠️ Search Agent failed: {str(e)}")
            st.session_state.running = False
            st.stop()

    # ── Step 2: Reader ────────────────────────────────────────────────────────
    with st.spinner("📄  Reader Agent is scraping top resources…"):
        try:
            reader_agent = build_reader_agent()
            rr = invoke_with_retry(reader_agent, {
                "messages": [("user",
                    f"Based on the following search results about '{topic_val}', "
                    f"pick the most relevant URL and scrape it for deeper content.\n\n"
                    f"Search Results:\n{results['search'][:800]}"
                )]
            })
            results["reader"] = rr["messages"][-1].content
            st.session_state.results = dict(results)
        except Exception as e:
            st.error(f"⚠️ Reader Agent failed: {str(e)}")
            st.session_state.running = False
            st.stop()

    # ── Step 3: Writer ────────────────────────────────────────────────────────
    with st.spinner("✍️  Writer is drafting the report…"):
        try:
            research_combined = (
                f"SEARCH RESULTS:\n{results['search']}\n\n"
                f"DETAILED SCRAPED CONTENT:\n{results['reader']}"
            )
            results["writer"] = writer_chain.invoke({
                "topic": topic_val,
                "research": research_combined
            })
            st.session_state.results = dict(results)
        except Exception as e:
            st.error(f"⚠️ Writer failed: {str(e)}")
            st.session_state.running = False
            st.stop()

    # ── Step 4: Critic ────────────────────────────────────────────────────────
    with st.spinner("🧐  Critic is reviewing the report…"):
        try:
            results["critic"] = critic_chain.invoke({
                "report": results["writer"]
            })
            st.session_state.results = dict(results)
        except Exception as e:
            st.error(f"⚠️ Critic failed: {str(e)}")
            st.session_state.running = False
            st.stop()

    st.session_state.running = False
    st.session_state.done = True
    st.rerun()


# ── Results ───────────────────────────────────────────────────────────────────
r = st.session_state.results

if r:
    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
    st.markdown('<div class="section-heading">Results</div>', unsafe_allow_html=True)

    if "search" in r:
        with st.expander("🔍  Search Results (raw)", expanded=False):
            st.markdown(
                f'<div class="result-panel">'
                f'<div class="result-panel-title">Search Agent Output</div>'
                f'<div class="result-content">{r["search"]}</div>'
                f'</div>',
                unsafe_allow_html=True,
            )

    if "reader" in r:
        with st.expander("📄  Scraped Content (raw)", expanded=False):
            st.markdown(
                f'<div class="result-panel">'
                f'<div class="result-panel-title">Reader Agent Output</div>'
                f'<div class="result-content">{r["reader"]}</div>'
                f'</div>',
                unsafe_allow_html=True,
            )

    if "writer" in r:
        st.markdown(
            '<div class="report-panel"><span class="panel-label">📝  Final Research Report</span>',
            unsafe_allow_html=True,
        )
        st.markdown(r["writer"])
        st.markdown("</div>", unsafe_allow_html=True)

        st.download_button(
            label="⬇  Download Report (.md)",
            data=r["writer"],
            file_name=f"research_report_{int(time.time())}.md",
            mime="text/markdown",
        )

    if "critic" in r:
        st.markdown(
            '<div class="feedback-panel"><span class="panel-label">🧐  Critic Feedback</span>',
            unsafe_allow_html=True,
        )
        st.markdown(r["critic"])
        st.markdown("</div>", unsafe_allow_html=True)


# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="notice">
    ResearchMind · Powered by LangChain multi-agent pipeline · Built with Streamlit
</div>
""", unsafe_allow_html=True)