"""
Streamlit chat UI for the Canada RAI Competitiveness chatbot.

Run from the basic_crewai_1/ directory:
    streamlit run src/basic_crewai_1/app.py
"""

import streamlit as st

from basic_crewai_1.crew import BasicCrewai1
from basic_crewai_1.main import load_rai_context, read_docx, save_answer

REPORT_PATH = "data/final_report.docx"

EXAMPLE_QUESTIONS = [
    # Policy & Governance / RAI
    "Why does Canada rank 7th in composite RAI performance despite ranking 5th in research output?",
    "Which countries participate in the EU AI Act and why does it matter for Canada?",
    # R&D and Science & Medicine
    "What is Canada's commercialization gap and why does it exist?",
    "How does Canada's AI research strength compare to its development and commercial scores?",
    # Economy
    "What is Canada's AI economic profile — talent, startups, and venture capital?",
    "Why are Canadian businesses slow to adopt AI compared to international peers?",
    # Recommendations
    "What are the three policy recommendations and how much do they cost?",
    "What would it take to move Canada into the top 25 globally for AI literacy?",
    "How does the Translational AI R&D Mission Stream address Canada's commercialization gap?",
]


@st.cache_resource(show_spinner="Loading report and RAI data...")
def load_context() -> str:
    report = read_docx(REPORT_PATH)
    rai = load_rai_context()
    if rai:
        return f"=== GROUP REPORT ===\n{report}\n\n=== RAI ANALYSIS DATA ===\n{rai}"
    return report


def ask_crew(question: str, full_context: str) -> str:
    inputs = {"full_context": full_context, "user_question": question}
    result = BasicCrewai1().crew().kickoff(inputs=inputs)
    return str(result)


# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Canada RAI Chatbot",
    page_icon="🇨🇦",
    layout="wide",
)

st.title("Canada RAI Competitiveness — Q&A Chatbot")
st.caption("Powered by CrewAI  ·  MIE1624 Course Project  ·  Winter 2026")

# ── Sidebar: example questions ────────────────────────────────────────────────
with st.sidebar:
    st.header("Example Questions")
    st.write("Click a question to ask it:")
    for q in EXAMPLE_QUESTIONS:
        if st.button(q, use_container_width=True):
            st.session_state["pending_question"] = q
    st.divider()
    st.caption("Answers are saved to outputs/ automatically.")

# ── Chat history ──────────────────────────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state["messages"] = []

for msg in st.session_state["messages"]:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# ── Input: typed or clicked from sidebar ─────────────────────────────────────
prompt = st.chat_input("Ask about Canada's AI competitiveness...")

if "pending_question" in st.session_state:
    prompt = st.session_state.pop("pending_question")

# ── Run crew and display response ─────────────────────────────────────────────
if prompt:
    st.session_state["messages"].append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Agents thinking..."):
            full_context = load_context()
            answer = ask_crew(prompt, full_context)
            question_number = len(st.session_state["messages"])
            save_answer(question_number, prompt, answer)
        st.markdown(answer)

    st.session_state["messages"].append({"role": "assistant", "content": answer})
