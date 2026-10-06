"""
Run the ten official questions (data/raw/README.txt) through Ask NOVA.
Calls Gemini: not part of the unit tests.

    python -m tests.run_official_questions docs/evaluation/after_answers.json
"""

import json
import sys
from pathlib import Path

from dotenv import load_dotenv

from backend.services.ask_nova import answer_question


QUESTIONS = {
    "Q01": "Quelle est la date de mise en production actuellement approuvée, et avec quelle réserve?",
    "Q02": "Pourquoi la date a-t-elle changé, et quel est l'état actuel de la cause initiale?",
    "Q03": "Qui a approuvé le changement et quand? Distinguez proposition et approbation.",
    "Q04": "Qui est responsable du projet et depuis quand?",
    "Q05": "Quel est le montant contractuel autorisé et comment se calcule-t-il?",
    "Q06": "Quel problème présente INV-003? Précisez le montant concerné et le traitement à prévoir.",
    "Q07": "Où les données de production doivent-elles être hébergées? Quelle preuve confirme la mise en œuvre?",
    "Q08": "La sécurité est-elle acceptée? Distinguez livraison et validation.",
    "Q09": "L'accessibilité est-elle complétée? Identifiez ce qui reste à corriger.",
    "Q10": "Quelles sont les trois conditions de go-live? Précisez les travaux manquants du runbook à partir de sa capture.",
}


def main(output_file: str) -> None:
    load_dotenv(Path(__file__).resolve().parent.parent / ".env")
    results = {}

    for question_id, question in QUESTIONS.items():
        try:
            results[question_id] = {"question": question, "answer": answer_question(question)}
        except Exception as error:
            results[question_id] = {"question": question, "error": type(error).__name__}

        print(f"{question_id} done", flush=True)
        Path(output_file).write_text(
            json.dumps(results, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "docs/evaluation/after_answers.json")
