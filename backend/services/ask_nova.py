import json
import os
import re
import time
from pathlib import Path

from google import genai


KNOWLEDGE_FILE = Path("data/processed_insights.json")


def load_knowledge() -> list:
    if not KNOWLEDGE_FILE.exists():
        raise FileNotFoundError(
            "NOVA knowledge base not found. Run the batch processor first."
        )

    return json.loads(
        KNOWLEDGE_FILE.read_text(encoding="utf-8")
    )


def answer_question(
    question: str,
    additional_information: list[str] | None = None,
) -> str:
    """
    Answer a project question using NOVA's extracted dataset
    plus optional information supplied by the user.
    """

    if not question or not question.strip():
        raise ValueError("Question cannot be empty.")

    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        raise ValueError("GEMINI_API_KEY is not set.")

    knowledge = load_knowledge()
    additional_information = additional_information or []

    context_parts = []

    for document in knowledge:
        insights = document.get("insights", {})

        context_parts.append(
            f"""
SOURCE: {document.get("filename", "unknown")}

DECISIONS:
{json.dumps(insights.get("decisions", []), ensure_ascii=False)}

OWNERS:
{json.dumps(insights.get("owners", []), ensure_ascii=False)}

DEADLINES:
{json.dumps(insights.get("deadlines", []), ensure_ascii=False)}

COMMITMENTS:
{json.dumps(insights.get("commitments", []), ensure_ascii=False)}

RISKS:
{json.dumps(insights.get("risks", []), ensure_ascii=False)}
"""
        )

    if additional_information:
        context_parts.append(
            "\nNEW INFORMATION:\n"
            + "\n".join(
                f"- {item}" for item in additional_information
            )
        )

    context = "\n".join(context_parts)

    prompt = f"""
You are NOVA, an AI assistant for the NOVA enterprise project.

Answer the user's question using ONLY the supplied project context.

Rules:
- Never invent facts.
- If the context does not contain enough evidence, say so.
- Consider decisions, owners, deadlines, commitments, and risks.
- If sources conflict, explain the conflict rather than silently choosing.
- Give priority to explicitly newer information when dates establish chronology.
- Mention relevant source filenames when useful.
- Be concise and practical.
- Answer in the same language as the user's question.

PROJECT CONTEXT:
{context}

USER QUESTION:
{question}
"""

    client = genai.Client(api_key=api_key)

    for attempt in range(3):
        try:
            response = client.models.generate_content(
                model="gemini-3.5-flash-lite",
                contents=prompt,
            )

            return response.text.strip()

        except Exception as error:
            if attempt == 2:
                raise

            error_text = str(error)

            if "429" in error_text or "RESOURCE_EXHAUSTED" in error_text:
                match = re.search(
                    r"'retryDelay': '([0-9]+)s'",
                    error_text,
                )
                wait_time = int(match.group(1)) + 2 if match else 60
            else:
                wait_time = 2 ** (attempt + 1)

            print(f"⚠️ Gemini unavailable — waiting {wait_time}s...")
            time.sleep(wait_time)

    raise RuntimeError("NOVA could not generate an answer.")


def answer_question_with_database(question: str) -> str:
    """
    Answer a question using the knowledge base plus all persisted
    new information. Timestamps are included so newer information
    can take priority over older sources.
    """

    from backend.services.database_service import get_information_records

    additional_information = [
        f"[added {record['created_at']}] {record['information']}"
        for record in get_information_records()
    ]

    return answer_question(question, additional_information)
