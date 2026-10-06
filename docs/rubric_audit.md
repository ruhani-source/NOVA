# NOVA Rubric Audit

Audit of branch `feature/ai-data` against `data/raw/README.txt`. Baseline: commit `0b3bc4a`. Audit date: 2026-10-04.

- **Full answers:** `docs/evaluation/baseline_answers.json` (before) and `docs/evaluation/after_answers.json` (after). Both were produced by `python -m tests.run_official_questions`.
- **Ground truth:** `tests/fixtures/ground_truth_q01_q10.json`. It was built manually from the corpus, and every locator is checked by `tests/test_evidence_store.py`.
- **Scores are our own estimates against the rubric (0/3/5), not judge scores.**
- **Status labels:** ✅ verified (tested or re-run) · 🟡 partially verified · ⬜ not yet verified · 🔗 depends on `feature/api-frontend` integration.

## Root causes found in the baseline

1. **Lossy context.** `answer_question` only saw Gemini-extracted summaries (decisions, owners, deadlines, commitments, risks). They had no dates, no line, page or cell locators, and no raw text, so answers could not cite precise evidence.
2. **Images ignored.** The batch processor skips PNGs. The corpus contains **8 real PNGs**, not 3, and the runbook capture needed for Q10 is the file `SEC-210.txt`.
3. **Shuffled names.** File names don't match content. For example, `ACC-301_labels.png` is the 26 Sept committee transcript, and `OPS-601_runbook.png` shows the INT-101 screen. The baseline cited files by their apparent names.
4. **Undecoded emails.** Quoted-printable emails hidden under `.txt` (e.g. `M01_CR_Demarrage_07juillet.txt`) were stored still encoded.

## Fixes applied (AI/data only)

| Fix | Files |
|---|---|
| Evidence corpus: every passage of `data/raw` with a locator, real type detected from content, attachments matched to identical files by SHA-256. | `backend/services/evidence_store.py`, `data/evidence_corpus.json` |
| Manual transcription of the 8 images (visible text only). | `data/image_transcriptions.json` |
| `answer_question` sends the full corpus (~45k characters) instead of the summaries, with a rubric-aware prompt: baseline date; proposal ≠ decision; delivered ≠ accepted; authorized/invoiced/paid; authority and date; attachments are not independent; filename + locator; recommendation ≠ commitment; update rules. | `backend/services/ask_nova.py` |
| Temperature 0. Deterministic citation check (unknown file or quote not found) → one correction pass → visible warning if still unverified. | `backend/services/ask_nova.py`, `evidence_store.verify_quotes` |
| Keyword search `search_evidence(query)`, returning file + locator + passage. | `backend/services/evidence_store.py` |
| Targeted prompt hint (documented): unqualified « la date » or « le changement » refers to the go-live date change, not a change request (CR). Added because Q03 was misread twice. | `backend/services/ask_nova.py` |

The signature `answer_question(question, additional_information=None)` is unchanged ✅. `processed_insights.json` is untouched; it is still used as a fallback if the corpus is missing.

## Initial Questions — 50 points

### Q01. Date de mise en production approuvée et réserve
- **Baseline answer:** 22 oct. + conditions (lists 4, one redundant); no locators.
- **Ground truth:** 22 octobre 2026, approved by the steering committee on 10 Sept. Not an automatic go: conditional on SEC-210 validation, ACC-303 closure and runbook approval including rollback (committee of 26 Sept).
- **Sources:** M06_Transcript_Comite_26sept.txt — [L17], [L23], [L24]; ACC-301_labels.png — [L11], [L16]; E10_Fonction_mobile.eml — [L5].
- **Contradictions:** the plan still shows 15 Oct (CR-01_Rapports_avances_APPROUVE.pdf — [feuille 'Plan projet', ligne 7 (A7:G7)]); Newsletter_Boreal_Septembre.txt — [L5] confirms the plan was not corrected.
- **Score:** before **5** → after **5** ✅ (now with locators).

### Q02. Pourquoi la date a changé; état de la cause initiale
- **Baseline answer:** connector + closed, but attributed the fix to the DATA-401 idempotence key (wrong ticket) and added "lenteurs".
- **Ground truth:** the INT-101 connector (service token expired after a secret change, 401 errors, then intermittent errors) consumed the margin. Boréal recommended 22 Oct. Cause fixed by secret rotation + token-renewal logic, validated 120/120, closed 17 Sept by Marc Gervais. Risk register R-01 is still "Ouvert" (stale).
- **Sources:** E06_Transition_charge_projet.eml — [L3]; OPS-601.txt — [L15], [L18], [L20]; PERF-501.txt — [L1]; M01_CR_Demarrage_07juillet.txt — [L3]; INV-001.pdf — [feuille 'Risques', ligne 2 (A2:H2)].
- **Score:** before **3** (wrong mechanism) → after **5** ✅. Remaining risk: the final run doesn't mention the stale R-01 entry.

### Q03. Qui a approuvé le changement et quand
- **Baseline answer:** answered about CR-01/CR-04. Wrong change.
- **Ground truth:** proposal by Julien Moreau (Boréal), email of 8 Sept (« il s'agit d'une proposition »), repeated at the 10 Sept committee. Approval by the steering committee on 10 Sept 2026, decision formulated by Élodie Caron, no objection.
- **Sources:** E06_Transition_charge_projet.eml — [L5], [L7]; M06_Transcript_Comite_26sept.txt — [L6], [L17]-[L23].
- **Fix:** glossary hint.
- **Score:** before **0** → after **5** ✅. Remaining risk: the answer still appends the CR-01/CR-04/ADR-007 changes after the correct answer.

### Q04. Responsable et depuis quand
- **Baseline answer:** correct (Nicolas Perron, 16 Sept); cited a file that doesn't mention the transition.
- **Ground truth:** Nicolas Perron since 16 Sept 2026; Élodie Caron before that, from 7 July.
- **Sources:** E07_Facture_003_question.eml — [L3]; Registre_Risques_29sept.xlsx — [L4]; Notes_personnelles_quelquun.txt — [L4].
- **Contradiction:** the old plan names Élodie (CONTRAT_Boreal_NOVA.pdf — [feuille 'Plan projet', ligne 7 (A7:G7)]).
- **Score:** before **5** → after **5** ✅.

### Q05. Montant contractuel autorisé et calcul
- **Baseline answer:** listed 180k and 24k but didn't state the total; confused the 36k invoice line.
- **Ground truth:** 204 000 $ = 180 000 $ (contract maximum) + 24 000 $ (CR-01 approved 14 Aug). CR-04 (18 000 $) excluded. Invoiced 186 000 $; paid 132 000 $.
- **Sources:** INV-003.pdf — [page 1]; ADR-007_Localisation_donnees.md — [page 1]; Architecture_NOVA_v1.pdf — [page 1].
- **Score:** before **3** → after **5** ✅.

### Q06. Problème d'INV-003, montant et traitement
- **Baseline answer:** 18k CR-04 identified; handling vague.
- **Ground truth:** INV-003 (54 000 $, en validation) bills 18 000 $ for CR-04, which is an unapproved draft deferred to phase 2 on 24 Sept. The contract requires an approved change before execution and invoicing. Handling: do not release the 18 000 $ (documented); process the 36 000 $ jalon 3 line and request a corrected invoice (our recommendation).
- **Sources:** Teams_15sept_ProjetNOVA.txt — [page 1]; E08_Correctif_journalisation.eml — [L5]; E11_Communication_statut.eml — [L5]; INV-778_Projet_ORION.pdf — [L4]; INV-003.pdf — [page 1].
- **Score:** before **3** → after **5** ✅ on the final run. 🟡 An intermediate run mislabeled the 36k line as "jalon 1" (a 3 on that run).

### Q07. Hébergement et preuve de mise en œuvre
- **Baseline answer:** Canada Central with the verification quote; misdated the source.
- **Ground truth:** Canada Central (ADR-007, 23 July, Acceptée; v1 East US replaced). Proof: Boréal's declaration of 26 Aug (deployment and connectivity test, v2 schema) plus verification by the architecture team (27 Aug committee). The v2 attachment is the same file as Courriel_archive_17sept.eml, so it is not independent proof.
- **Sources:** Teams_19sept_Securite.txt — [L4], [L10]; E04_Corrections_accessibilite.eml — [L3], [L5]; M05_CR_Suivi_18sept.txt — [L5]; Courriel_archive_17sept.eml — [page 1].
- **Score:** before **5** → after **5** ✅. It regressed to 3 on one intermediate run; fixed with the "vendor declaration ≠ verification" rule.

### Q08. Sécurité acceptée? Livraison vs validation
- **Ground truth:** No. Delivered: fix deployed in validation on 19 Sept. Validation: not given; re-test planned; status EN VALIDATION on 26 Sept. The 21 Sept status report ("VERT") is contradicted.
- **Sources:** E09_Rappel_mise_en_production.eml — [L3]; Note_transition_Elodie_16sept.txt — [L24], [L25]; ACC-301_labels.png — [L7]; Plan_NOVA_preliminaire_juin.xlsx — [L5].
- **Score:** before **5** → after **5** ✅.

### Q09. Accessibilité complétée?
- **Ground truth:** No. ACC-301 and ACC-302 were closed after re-test (15 and 20 Aug). ACC-303 is OPEN and blocking: in the modal, keyboard focus never reaches Enregistrer. A fix is announced but not delivered.
- **Sources:** DATA-401_doublons.png — [L6], [L14], [L16]; ACC-301_labels.png — [L9]; DATA-401_echantillon.csv — [capture, élément 5].
- **Score:** before **5** → after **5** ✅. Earlier runs cited tickets by their logical file names (flagged by the quote check).

### Q10. Trois conditions de go-live; travaux manquants du runbook (capture)
- **Baseline answer:** correct conditions; runbook: rollback + "une autre étape" (could not read the image); cited the wrong file as the capture.
- **Ground truth:** SEC-210 validation; ACC-303 closure; runbook approval including rollback. The capture (version du 25 sept.) shows step 4 "Procédure de retour arrière" TODO and step 5 "Validation fonctionnelle post-déploiement" À compléter.
- **Sources:** ACC-301_labels.png — [L11]; SEC-210.txt — [capture, élément 1], [6], [7]; PERF-501_lenteur.png — [L14], [L16].
- **Score:** before **3** → after **5** ✅. Remaining risk: the final run says in a side remark that ACC-303's fix was "déployé" (it was only announced).

### Totals

| | Q01 | Q02 | Q03 | Q04 | Q05 | Q06 | Q07 | Q08 | Q09 | Q10 | **Total** |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Before | 5 | 3 | 0 | 5 | 3 | 3 | 5 | 5 | 5 | 3 | **37/50** |
| After (final run) | 5 | 5 | 5 | 5 | 5 | 5 | 5 | 5 | 5 | 5 | **50/50** |

Generated answers vary between runs; the earlier post-fix runs scored 46 and 48. **The realistic expectation is 48–50.** `docs/memoire_operationnelle.md` holds the stable, verified answers.

## Evidence & Navigation — /10
- **Criteria:** ≥3 answers with a retrievable file and locator; ≥2 answers that cross distinct sources.
- **Before:** filenames only, often wrong → ~5.
- **Now:** every answer cites `fichier — [repère]` across several distinct sources; quotes are checked automatically; `search_evidence()` gives navigation; all ground-truth and memo locators are tested ✅.
- **Estimate: 10** 🟡. Some generated line locators may still be off; the memo is the verified fallback.

## Timeline & Contradictions — /10
- **Criteria:** proposal / decision / validation with dates and sources; ≥2 contradictions explained by authority or date, including one in a plan or risk register.
- **Now:** chronology table with each item typed (proposition / décision / livraison / validation) and 6 resolved contradictions, including **C1 plan projet F7=2026-10-15** and **C2 registre R-01 Ouvert** (`docs/memoire_operationnelle.md` §2–3) ✅.
- **Before:** 0–5. **Estimate: 10** 🟡. Content is verified; the judge must be able to open it.

## Brief & Actions — /10
- **Criteria:** the 5 themes on one page; the 3 launch conditions linked to actions, owners and deadlines (known or « à confirmer »).
- **Now:** one-page brief table (responsable, date + conditions, portée, budget, factures, priorités) and actions A1–A10 linking each condition to an owner (confirmed or proposed), evidence and deadline, labelled engagement vs recommandation ✅.
- **Before:** 0. **Estimate: 10** 🟡.

## Usage & Uncertainty — /10
- **Criteria:** the judge can open the deliverable and find evidence; the team shows its research and states limits.
- **Now:** `docs/mode_emploi.md` (opening, navigation, tools, manual steps, limits); verified docs open without installation; the live demo depends on Ruhani's UI 🔗.
- **Estimate: 5 now, 10 after integration and a rehearsed demo** ⬜.

## Update After Event — /10
- **Criteria:** distinguish the issue's status, the earlier decision and the new proposal; keep the baseline; give sourced impacts and actions; invent no approval and close no other condition.
- **Now:** `additional_information` is appended as timestamped « NOUVELLES INFORMATIONS »; prompt rules forbid inventing approvals or closing conditions; the baseline corpus is never modified; Supabase keeps timestamped history 🟡.
- **Simulated event** (« ACC-303 livré build 2026.10.01; Boréal propose le 20 oct. »): NOVA kept 22 Oct as the approved date, treated 20 Oct as a proposal, treated ACC-303 as delivered but not validated, and kept the other conditions open 🟡.
- **Estimate: 5–10.** The real event is unknown, and the "baseline vs updated" view must be shown in the UI 🔗.

## Current Estimated Total

| Criterion | Before | Now (estimate) | Status |
|---|---|---|---|
| Q01–Q10 | 37 | 48–50 | ✅ re-run |
| Preuves | ~5 | 10 | 🟡 |
| Chronologie | 0–5 | 10 | 🟡 |
| Brief/actions | 0 | 10 | 🟡 |
| Utilisation | 0–5 | 5 (10 with demo) | 🔗 |
| Mise à jour | ~5 | 5–10 | 🔗 |
| **Total** | **~47–57** | **~88–100** | not guaranteed |

## What `feature/api-frontend` still needs (Ruhani)
1. Use the Supabase layer: `docs/database_integration.md` (`save_information` / `get_information`).
2. Render answers as Markdown; keep the « Sources » list and any « ⚠️ Références non vérifiées » warning visible.
3. Expose `docs/memoire_operationnelle.md` (brief, chronology, contradictions, actions) in the UI, or link to it.
4. Optional evidence search: `GET /evidence?q=...` → `search_evidence(q)`, showing `filename`, `locator`, `text`.
5. Update view: show the baseline answer next to the post-event answer (`answer_question_with_database` or `answer_question(q, get_information())`), with timestamps.
