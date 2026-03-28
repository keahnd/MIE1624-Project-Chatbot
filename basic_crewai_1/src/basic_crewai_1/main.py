import json
from pathlib import Path
from datetime import datetime
from typing import Optional

from basic_crewai_1.crew import BasicCrewai1


OUTPUT_DIR = "outputs"

# Structured JSON context files — one per analytical section.
# These replace the raw .docx to keep token count manageable.
_CONTEXT_FILES = {
    "RAI Analysis (Policy Engagement & Responsible AI Scores)": Path("data\rai_context.json"),
    "Research, Development & Science/Medicine Analysis": Path("data/rd_context.json"),
    "Policy & Governance Analysis": Path("data/policy_context.json"),
    "Economy Analysis": Path("data/economy_context.json"),
    "Policy Recommendations": Path("data/recommendations_context.json"),
}


def load_full_context() -> str:
    """Assemble full project context from structured JSON files.

    Each file corresponds to one analytical section of the group report.
    Using JSON instead of the raw .docx reduces token count from ~150K to ~15K.
    """
    sections = []
    for label, path in _CONTEXT_FILES.items():
        if path.exists():
            with open(path, encoding="utf-8") as f:
                data = json.dumps(json.load(f), indent=2)
            sections.append(f"=== {label.upper()} ===\n{data}")
        else:
            sections.append(f"=== {label.upper()} ===\n[File not found: {path}]")
    return "\n\n".join(sections)


# Keep load_rai_context() as a standalone helper used by app.py cache
def load_rai_context() -> str:
    path = _CONTEXT_FILES["RAI Analysis (Policy Engagement & Responsible AI Scores)"]
    if not path.exists():
        return ""
    with open(path, encoding="utf-8") as f:
        return json.dumps(json.load(f), indent=2)


def save_answer(question_number: int, question: str, answer: str) -> Path:
    """Save each CrewAI response to a markdown file automatically."""
    output_dir = Path(OUTPUT_DIR)
    output_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    file_path = output_dir / f"qa_{question_number}_{timestamp}.md"

    content = (
        f"# Question {question_number}\n\n"
        f"## User Question\n{question}\n\n"
        f"## CrewAI Answer\n{answer}\n"
    )

    file_path.write_text(content, encoding="utf-8")
    return file_path


def run():
    full_context = load_full_context()

    print("\nCrewAI chatbot is ready. Type 'stop' to exit.\n")

    i = 1
    while True:
        user_question = input(f"Question {i}: ").strip()

        if not user_question:
            print("Please enter a question.\n")
            continue

        if user_question.lower() in ("stop", "exit", "quit"):
            print("Session ended.")
            break

        inputs = {
            "full_context": full_context,
            "user_question": user_question
        }

        result = BasicCrewai1().crew().kickoff(inputs=inputs)
        result_text = str(result)

        saved_file = save_answer(i, user_question, result_text)

        print("\n===== ANSWER =====\n")
        print(result_text)
        print(f"\nSaved to: {saved_file}\n")

        i += 1

    print("Session ended.")


def train():
    print("Training hook not implemented.")


def replay():
    print("Replay hook not implemented.")


def test():
    print("Test hook not implemented.")


def run_with_trigger():
    run()