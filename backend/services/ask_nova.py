import json
import os
import re
import time
from pathlib import Path

from google import genai
from google.genai import types

from backend.services.evidence_store import (
    format_corpus_for_prompt,
    load_evidence_corpus,
    verify_quotes,
)


KNOWLEDGE_FILE = Path("data/processed_insights.json")


def load_knowledge() -> list:
    if not KNOWLEDGE_FILE.exists():
        raise FileNotFoundError(
            "NOVA knowledge base not found. Run the batch processor first."
        )

    return json.loads(
        KNOWLEDGE_FILE.read_text(encoding="utf-8")
    )


def _insights_context() -> str:
    parts = []

    for document in load_knowledge():
        insights = document.get("insights", {})
        parts.append(
            f"=== FICHIER : {document.get('filename', 'unknown')}\n"
            + "\n".join(
                f"{key.upper()}: {json.dumps(insights.get(key, []), ensure_ascii=False)}"
                for key in ("decisions", "owners", "deadlines", "commitments", "risks")
            )
        )

    return "\n\n".join(parts)


def build_project_context() -> str:
    """
    Full evidence corpus with locators (data/evidence_corpus.json).
    Falls back to the extracted insights if the corpus is unavailable.
    """

    corpus = load_evidence_corpus()

    if corpus:
        return format_corpus_for_prompt(corpus)

    return _insights_context()


CITED_FILE = re.compile(r"[\w\-]+\.(?:txt|pdf|eml|png|xlsx|csv|md)\b")


def unknown_citations(answer: str) -> list[str]:
    """Cited filenames that do not exist in the evidence corpus."""

    known = {document["filename"] for document in load_evidence_corpus()}

    if not known:
        return []

    return sorted(set(CITED_FILE.findall(answer)) - known)


def citation_problems(answer: str) -> list[str]:
    """Unknown files plus quotes not found in the file they cite."""

    problems = [
        f"fichier absent du corpus : {name}"
        for name in unknown_citations(answer)
    ]
    problems.extend(
        f"« {item['quote'][:80]} » introuvable dans {', '.join(item['files'])}"
        for item in verify_quotes(answer)
    )

    return problems


def flag_unverified_citations(answer: str) -> str:
    """Append a visible warning for citations that remain unverified."""

    problems = citation_problems(answer)

    if problems:
        answer += "\n\n⚠️ Références non vérifiées :\n" + "\n".join(
            f"- {problem}" for problem in problems
        )

    return answer


def answer_question(
    question: str,
    additional_information: list[str] | None = None,
) -> str:
    """
    Answer a project question using NOVA's evidence corpus
    plus optional information supplied by the user.
    """

    if not question or not question.strip():
        raise ValueError("Question cannot be empty.")

    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        raise ValueError("GEMINI_API_KEY is not set.")

    additional_information = additional_information or []

    context = build_project_context()

    if additional_information:
        context += (
            "\n\n=== NOUVELLES INFORMATIONS (ajoutées après le baseline) ===\n"
            + "\n".join(f"- {item}" for item in additional_information)
        )

    prompt = f"""
You are NOVA, the operational memory of the NOVA project.

Answer the user's question using ONLY the supplied project corpus.
The baseline is 30 September 2026, 09:00 Montreal time (UTC-04:00):
"currently" means as of that date unless NEW INFORMATION says otherwise.

Reading rules:
- Never invent facts, decisions, deadlines or approvals. If evidence is
  missing, say exactly what is missing.
- A proposal or recommendation is not a decision. Say who proposed,
  who decided, and when, with the source of each.
- A delivered or deployed fix is not an accepted or validated one.
- Judge sources by authority and date of the facts, not by file name.
  Plans, status reports, charters and registers can be outdated; when
  they conflict with a later decision, say so and explain which wins.
- An old screenshot alone does not prove a defect is still open.
- Money: distinguish authorized, invoiced and paid amounts. For an
  invoice with a disputed line, state the amount that can be processed,
  the amount to withhold, and the approval or correction required.
- An email attachment that is identical to another corpus file is the
  same evidence, not an independent confirmation.
- File names do NOT always match content. Always cite the exact
  FICHIER name where the passage appears, with its [locator]
  (page, cell/row, line Lx, en-têtes, capture élément).
- A party's claim about its own work (e.g. a vendor saying a migration
  is done) is a declaration; look for independent verification by
  another team and say whether it exists.
- When asked how something should be handled, give concrete actions:
  what is documented as required, and separately your recommendation.
- If the question is ambiguous, answer the most likely interpretation
  in the project's context first, state it, and only briefly mention
  alternatives. Project glossary: unqualified "la date" or
  "le changement" refers to the go-live date change, not to a CR.
- Quote passages verbatim inside « » so they can be checked.
- Separate documented commitments from your own recommendations,
  and label recommendations explicitly.
- NEW INFORMATION may change the status of an issue, but never
  invent an approval and never close other conditions because of it.
  Keep the baseline visible and say what changed.

Answer format (same language as the question, concise):
1. Réponse directe.
2. Nuances / contradictions résolues (if any).
3. Sources : one bullet per fact, as FICHIER — [repère] — short quote.

PROJECT CORPUS:
{context}

USER QUESTION:
{question}
"""

    client = genai.Client(api_key=api_key)
    answer = _generate(client, prompt)

    problems = citation_problems(answer)

    if problems:
        # One correction pass: fix references, keep the substance.
        answer = _generate(client, f"""{prompt}

YOUR PREVIOUS ANSWER:
{answer}

These citations could not be verified in the corpus:
{chr(10).join(f"- {problem}" for problem in problems)}

Rewrite the answer with the same substance. For each quote, cite the
exact FICHIER where the passage appears and copy it verbatim.
""")

    return flag_unverified_citations(answer)


def _generate(client, prompt: str) -> str:
    for attempt in range(3):
        try:
            response = client.models.generate_content(
                model="gemini-3.5-flash-lite",
                contents=prompt,
                config=types.GenerateContentConfig(temperature=0),
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
