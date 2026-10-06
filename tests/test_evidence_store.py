"""
Deterministic tests for the evidence corpus and Ask NOVA plumbing.
No Gemini call is made.

Run from the repository root:
    python -m unittest tests.test_evidence_store -v
"""

import inspect
import json
import re
import unittest
from pathlib import Path
from unittest import mock

from backend.services import ask_nova
from backend.services.evidence_store import (
    CORPUS_FILE,
    build_evidence_corpus,
    format_corpus_for_prompt,
    load_evidence_corpus,
    search_evidence,
    verify_quotes,
)


REPO_ROOT = Path(__file__).resolve().parent.parent
GROUND_TRUTH = REPO_ROOT / "tests" / "fixtures" / "ground_truth_q01_q10.json"


class TestCorpus(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.corpus = load_evidence_corpus()
        cls.documents = {document["filename"]: document for document in cls.corpus}

    def segment(self, filename, locator):
        for segment in self.documents[filename]["segments"]:
            if segment["locator"] == locator:
                return segment["text"]
        self.fail(f"{filename} has no locator {locator}")

    def test_saved_corpus_is_reproducible(self):
        self.assertEqual(build_evidence_corpus(), self.corpus)

    def test_readme_is_not_evidence(self):
        self.assertNotIn("README.txt", self.documents)
        self.assertEqual(len(self.corpus), 56)

    def test_types_are_detected_from_content(self):
        expected = {
            "SEC-210.txt": "png",
            "CONTRAT_Boreal_NOVA.pdf": "xlsx",
            "Courriel_archive_17sept.eml": "pdf",
            "M01_CR_Demarrage_07juillet.txt": "email",
            "INV-003.pdf": "pdf",
        }
        for filename, detected in expected.items():
            self.assertEqual(self.documents[filename]["detected_type"], detected)

    def test_every_image_is_transcribed(self):
        images = [d for d in self.corpus if d["detected_type"] == "png"]
        self.assertEqual(len(images), 8)
        for image in images:
            self.assertTrue(image["segments"], image["filename"])
            self.assertIn("transcription manuelle", image["note"])

    def test_runbook_capture_shows_missing_steps(self):
        self.assertIn("Version du 25 septembre", self.segment("SEC-210.txt", "capture, élément 1"))
        self.assertIn("Procédure de retour arrière — TODO", self.segment("SEC-210.txt", "capture, élément 6"))
        self.assertIn("post-déploiement — À compléter", self.segment("SEC-210.txt", "capture, élément 7"))

    def test_quoted_printable_email_is_decoded(self):
        text = self.segment("M01_CR_Demarrage_07juillet.txt", "L3")
        self.assertIn("120/120 recherches ont retourné", text)

    def test_spreadsheet_cells_have_locators(self):
        row = self.segment("CR-01_Rapports_avances_APPROUVE.pdf", "feuille 'Plan projet', ligne 7 (A7:G7)")
        self.assertIn("D7=Nicolas Perron", row)
        self.assertIn("F7=2026-10-15", row)

    def test_attachments_are_linked_to_identical_files(self):
        notes = [s["text"] for s in self.documents["E08_Correctif_journalisation.eml"]["segments"]
                 if s["locator"] == "pièce jointe"]
        self.assertEqual(len(notes), 1)
        self.assertIn("Teams_15sept_ProjetNOVA.txt", notes[0])

    def test_prompt_marks_misleading_extensions(self):
        prompt = format_corpus_for_prompt(self.corpus)
        self.assertIn("=== FICHIER : SEC-210.txt (contenu réel : png, l'extension ne correspond pas au contenu)", prompt)
        self.assertIn("[capture, élément 6] 4. Procédure de retour arrière — TODO", prompt)


class TestGroundTruthEvidence(unittest.TestCase):
    """Every locator in the Q01-Q10 ground truth exists and holds its snippet."""

    def test_all_ground_truth_locators_resolve(self):
        documents = {d["filename"]: d for d in load_evidence_corpus()}
        truth = json.loads(GROUND_TRUTH.read_text(encoding="utf-8"))

        for question in [f"Q{n:02d}" for n in range(1, 11)]:
            self.assertIn(question, truth)
            for item in truth[question]["evidence"]:
                with self.subTest(question=question, file=item["file"], locator=item["locator"]):
                    segments = documents[item["file"]]["segments"]
                    matches = [s for s in segments if s["locator"] == item["locator"]]
                    self.assertTrue(matches, "locator not found")
                    if item["snippet"] != item["locator"]:
                        self.assertIn(item["snippet"], matches[0]["text"])


class TestDocumentLocators(unittest.TestCase):
    """Every `fichier — [repère]` in the evidence documents resolves."""

    def test_memoire_locators_resolve(self):
        self.check_locators("memoire_operationnelle.md")

    def test_rubric_audit_locators_resolve(self):
        self.check_locators("rubric_audit.md")

    def check_locators(self, doc_name):
        documents = {d["filename"]: d for d in load_evidence_corpus()}
        text = (REPO_ROOT / "docs" / doc_name).read_text(encoding="utf-8")
        pattern = re.compile(
            r"([\w\-.]+\.(?:txt|pdf|eml|png|xlsx|csv|md)) — ((?:\[[^\]]+\](?:-\[[^\]]+\])?(?:, )?)+)"
        )
        checked = 0

        for filename, locators in pattern.findall(text):
            for locator in re.findall(r"\[([^\]]+)\]", locators):
                if locator.isdigit():
                    locator = f"capture, élément {locator}"
                with self.subTest(file=filename, locator=locator):
                    self.assertIn(filename, documents)
                    found = {s["locator"] for s in documents[filename]["segments"]}
                    self.assertIn(locator, found)
                checked += 1

        self.assertGreater(checked, 30)


class TestSearchAndVerification(unittest.TestCase):
    def test_search_finds_runbook_capture(self):
        files = [r["filename"] for r in search_evidence("runbook retour arrière TODO", limit=5)]
        self.assertIn("SEC-210.txt", files)

    def test_search_finds_invoice_line(self):
        files = [r["filename"] for r in search_evidence("INV-003 optimisation mobile CR-04", limit=5)]
        self.assertTrue({"Teams_15sept_ProjetNOVA.txt", "E08_Correctif_journalisation.eml"} & set(files))

    def test_search_ignores_accents_and_returns_locators(self):
        results = search_evidence("deploye validation SEC-210", limit=3)
        self.assertTrue(results)
        self.assertTrue(all({"filename", "locator", "text", "score"} <= set(r) for r in results))

    def test_empty_search(self):
        self.assertEqual(search_evidence("  "), [])

    def test_verify_quotes_accepts_real_quote(self):
        answer = "- ACC-301_labels.png — [L7] — « Nous n'avons pas encore donné l'acceptation sécurité de SEC-210. »"
        self.assertEqual(verify_quotes(answer), [])

    def test_verify_quotes_accepts_elided_quote(self):
        answer = ("- M06_Transcript_Comite_26sept.txt — [L17] — « La date cible de mise en production "
                  "NOVA est déplacée [...] Donc **approuvé**. Le 22 devient la date officielle. »")
        self.assertEqual(verify_quotes(answer), [])

    def test_verify_quotes_rejects_wrong_file(self):
        answer = "- Note_transition_Elodie_16sept.txt — [L4] — « Nicolas Perron reprend le rôle de chargé de projet NOVA »"
        self.assertEqual(len(verify_quotes(answer)), 1)


class TestAskNovaPlumbing(unittest.TestCase):
    def test_answer_question_signature_unchanged(self):
        parameters = inspect.signature(ask_nova.answer_question).parameters
        self.assertEqual(list(parameters), ["question", "additional_information"])
        self.assertIsNone(parameters["additional_information"].default)

    def test_context_uses_evidence_corpus(self):
        context = ask_nova.build_project_context()
        self.assertIn("=== FICHIER : SEC-210.txt", context)
        self.assertIn("[feuille 'Risques', ligne 2 (A2:H2)]", context)

    def test_unknown_files_are_flagged(self):
        flagged = ask_nova.flag_unverified_citations("Voir ACC-301_contraste.png [L3].")
        self.assertIn("fichier absent du corpus : ACC-301_contraste.png", flagged)
        self.assertEqual(ask_nova.flag_unverified_citations("Voir ACC-301_labels.png."), "Voir ACC-301_labels.png.")

    def test_new_information_reaches_prompt_and_bad_citation_triggers_correction(self):
        prompts = []
        replies = iter(["Réponse — Fichier_inexistant.txt [L1]", "Réponse — ACC-301_labels.png [L11]"])

        def fake_generate(client, prompt):
            prompts.append(prompt)
            return next(replies)

        with mock.patch.dict("os.environ", {"GEMINI_API_KEY": "test-key"}), \
                mock.patch.object(ask_nova.genai, "Client"), \
                mock.patch.object(ask_nova, "_generate", side_effect=fake_generate):
            answer = ask_nova.answer_question("Q?", ["ACC-303 fermé le 1er octobre"])

        self.assertEqual(answer, "Réponse — ACC-301_labels.png [L11]")
        self.assertEqual(len(prompts), 2)
        self.assertIn("- ACC-303 fermé le 1er octobre", prompts[0])
        self.assertIn("NOUVELLES INFORMATIONS", prompts[0])
        self.assertIn("Fichier_inexistant.txt", prompts[1])

    def test_rejects_empty_question(self):
        with self.assertRaises(ValueError):
            ask_nova.answer_question("   ")


if __name__ == "__main__":
    unittest.main()
