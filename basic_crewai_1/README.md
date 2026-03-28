# Canada RAI Competitiveness — Q&A Chatbot

A multi-agent AI chatbot built with [CrewAI](https://crewai.com) and [Streamlit](https://streamlit.io) for the MIE1624 course project (Winter 2026). The chatbot answers questions about Canada's AI competitiveness using a three-agent sequential pipeline grounded in the group's analytical report.

---

## How It Works

The chatbot uses a **3-agent sequential pipeline**. When a user submits a question, three specialized AI agents collaborate in order — each agent's output feeds into the next.

```
User Question
     │
     ▼
[1] Data Analyst          → extracts relevant facts and numbers from project context
     │
     ▼
[2] Policy Strategy Analyst  → interprets findings, maps to recommendations, searches web if needed
     │
     ▼
[3] Answer Writer          → synthesizes a concise, well-cited Q&A response
```

### Agent Roles

| Agent | Role | Tools |
|---|---|---|
| **Data Analyst** | Retrieves all quantitative evidence relevant to the question from the structured project context (RAI scores, R&D metrics, economic data, policy gaps) | None — works directly from injected context |
| **Policy Strategy Analyst** | Interprets the evidence, connects findings across sections, and maps them to the three policy recommendations with costs, timelines, and agencies | Web search (only for post-2024 events not in the report) |
| **Answer Writer** | Synthesizes both outputs into a concise, well-cited answer formatted for a live Q&A audience | None |

### Project Context

All project data is pre-loaded from structured JSON files in `data/` and injected directly into the first task prompt. This keeps the full report accessible to agents without any retrieval step.

| File | Contents |
|---|---|
| `rai_context.json` | RAI scores, policy engagement, responsible AI metrics |
| `rd_context.json` | R&D indicators, talent, patent and publication data |
| `policy_context.json` | Policy & governance analysis, framework participation |
| `economy_context.json` | Economic profile, startup ecosystem, adoption rates |
| `recommendations_context.json` | Three policy recommendations with costs and timelines |
| `pr_strategy_context.json` | Public relations strategy and messaging framework |

---

## Setup

**Requirements:** Python 3.10–3.13, [uv](https://docs.astral.sh/uv/)

**1. Install dependencies**

```bash
pip install uv
crewai install
```

**2. Configure API keys**

Create a `.env` file in the `basic_crewai_1/` directory:

```
OPENAI_API_KEY=your_openai_key
SERPER_API_KEY=your_serper_key
```

`SERPER_API_KEY` is required for the web search tool on the Policy Strategy Analyst. Get a free key at [serper.dev](https://serper.dev).

---

## Running the Chatbot

### Streamlit UI (recommended)

From the `basic_crewai_1/` directory:

```bash
streamlit run src/basic_crewai_1/app.py
```

Opens a chat interface in your browser with example questions in the sidebar. Answers are saved automatically to `outputs/`.

### CLI Mode

```bash
crewai run
```

Runs the chatbot in the terminal. Type `stop` to exit.

---

## Project Structure

```
basic_crewai_1/
├── data/                         # Structured JSON context files (project report data)
├── outputs/                      # Auto-saved Q&A responses (markdown)
├── src/basic_crewai_1/
│   ├── app.py                    # Streamlit chat UI
│   ├── crew.py                   # Agent and task definitions
│   ├── main.py                   # Context loading and CLI runner
│   └── config/
│       ├── agents.yaml           # Agent roles, goals, and backstories
│       └── tasks.yaml            # Task prompts and expected outputs
├── .env                          # API keys (not committed)
└── pyproject.toml
```

---

## Design Decisions

- **Context injection over retrieval** — The full ~15K token project context is injected directly into the first task prompt rather than using a retrieval (RAG) system. This eliminates retrieval failure risk and is well within modern LLM context windows.
- **Web search is gated** — The Policy Strategy Analyst only calls the web search tool when the question explicitly asks about events after 2024. This prevents unnecessary tool calls and keeps response time down.
- **`max_iter` caps** — Each agent is capped at 2–3 reasoning iterations to prevent runaway tool-calling loops (default is 20).
- **Sequential process** — Tasks run in a fixed order; each task receives the outputs of prior tasks via CrewAI's `context:` chaining.