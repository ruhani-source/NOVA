# NOVA — Mode d'emploi (couche IA / données)

## Ouvrir
- **Sans installation** : lire `docs/memoire_operationnelle.md` (brief, chronologie, contradictions, actions) et `docs/rubric_audit.md` (réponses Q01-Q10 avec preuves).
- **Avec l'application** : l'interface et l'API Flask (branche `feature/api-frontend`) appellent `answer_question(question, additional_information)`.

## Retrouver une preuve
- Chaque réponse cite `fichier — [repère]`. Ouvrir `data/raw/<fichier>` à ce repère :
  `L12` = ligne 12; `page 1`; `feuille 'Plan projet', ligne 7 (A7:G7)`; `en-têtes` d'un courriel; `capture, élément 6` = ligne 6 de la transcription de l'image.
- Recherche par mots-clés :
  ```python
  from backend.services.evidence_store import search_evidence
  search_evidence("runbook retour arrière")  # -> fichier, repère, texte
  ```
- **Les noms de fichiers ne correspondent pas toujours au contenu.** Par exemple, `SEC-210.txt` est en réalité la capture du runbook. Le corpus indique le type réel de chaque fichier.

## Outils utilisés
- Python : pypdf (PDF), openpyxl (XLSX), le module email (courriels, y compris ceux cachés sous `.txt`).
- Détection du type réel par signature binaire, pas par extension.
- Gemini `gemini-3.5-flash-lite`, température 0, pour répondre à partir du corpus complet.
- Supabase/PostgreSQL pour les nouvelles informations, avec un repli en fichier JSON local.

## Traitements manuels
- **Les 8 images PNG ont été transcrites à la main** dans `data/image_transcriptions.json` (texte visible uniquement, rien de déduit).
- `data/evidence_corpus.json` est régénéré avec `python -m backend.services.evidence_store`.
- La vérité terrain Q01-Q10 (`tests/fixtures/ground_truth_q01_q10.json`) a été établie manuellement; chaque repère est vérifié automatiquement par les tests.

## Contrôles automatiques
- Chaque réponse est vérifiée : un fichier cité absent du corpus, ou une citation « … » introuvable dans le fichier cité, déclenche une correction automatique. Si le problème persiste, l'avertissement « ⚠️ Références non vérifiées » est ajouté à la réponse.
- Tests : `python -m unittest tests.test_evidence_store tests.test_database_service -v`.

## Limites et incertitudes
- Les réponses générées peuvent varier d'une exécution à l'autre; la référence vérifiée reste `docs/memoire_operationnelle.md`.
- Un repère peut parfois être inexact dans une réponse générée. Les citations entre « » sont vérifiées; les repères de ligne ne le sont pas.
- Aucune échéance n'est documentée pour le re-test SEC-210, la build ACC-303 ou le runbook final : elles restent « à confirmer ».
- Les nouvelles informations sont horodatées et conservées séparément; le corpus initial (baseline) n'est jamais modifié.
