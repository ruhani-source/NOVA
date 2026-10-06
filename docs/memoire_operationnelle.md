# NOVA — Mémoire opérationnelle (baseline 30 septembre 2026, 09 h 00 HAE)

> Toutes les références sont `fichier — [repère]`, vérifiables dans `data/raw/`.
> **Attention : les noms de fichiers du corpus ne correspondent pas toujours à leur contenu.**
> Le repère cite toujours le fichier où le passage se trouve réellement.
> Repères : `L12` = ligne 12 du fichier; `page 1`; `feuille 'X', ligne 7 (A7:G7)`; `capture, élément 6` = transcription manuelle d'une image (`data/image_transcriptions.json`).

## 1. Brief de reprise (1 page)

| Thème | État au 30 sept. 2026 | Preuve |
|---|---|---|
| **Responsable** | Nicolas Perron, chargé de projet depuis le 16 sept. 2026 (succède à Élodie Caron, en poste depuis le 7 juillet). | E07_Facture_003_question.eml — [L3]; Registre_Risques_29sept.xlsx — [L4] |
| **Date approuvée** | **22 octobre 2026**, approuvée par le comité de direction le 10 sept. **Pas un go automatique.** | M06_Transcript_Comite_26sept.txt — [L17], [L23], [L24] |
| **Conditions** | 1) validation sécurité de SEC-210; 2) fermeture d'ACC-303; 3) approbation du runbook incluant le rollback (comité du 26 sept.). Les trois sont **ouvertes**. | ACC-301_labels.png — [L11]-[L16] |
| **Portée** | Phase 1 : SSO, création/suivi de demandes, pièces jointes, workflow, tableau de suivi, rapports standards + CR-01 (rapports avancés, export de synthèse). Mobile : compatibilité de base seulement; l'optimisation avancée CR-04 est reportée en phase 2 (24 sept.). | INV-003.pdf — [page 1]; ADR-007_Localisation_donnees.md — [page 1]; INV-778_Projet_ORION.pdf — [L4]; MANIFEST.csv — [L5] |
| **Budget** | Autorisé : **204 000 $** = 180 000 $ (contrat) + 24 000 $ (CR-01 approuvé le 14 août). CR-04 (18 000 $) **non autorisé**. | INV-003.pdf — [page 1]; ADR-007_Localisation_donnees.md — [page 1]; Architecture_NOVA_v1.pdf — [page 1] |
| **Factures** | INV-001 60 000 $ **payée**; INV-002 72 000 $ **payée** (dont CR-01 24 000 $); INV-003 54 000 $ **en validation**, dont 18 000 $ CR-04 non approuvé. Facturé 186 000 $; payé 132 000 $. | Architecture_NOVA_v2.pdf — [page 1]; Decision_Portee_Phase2.md — [page 1]; Teams_15sept_ProjetNOVA.txt — [page 1] |
| **Priorités** | 1) Re-test et acceptation SEC-210. 2) Correctif et re-test ACC-303. 3) Runbook final : rollback (étape 4 TODO) + validation post-déploiement (étape 5 à compléter). 4) Retenir la ligne CR-04 de 18 000 $ sur INV-003. 5) Corriger le plan projet (toujours au 15 oct.) et le registre de risques (R-01 encore ouvert). | voir § 4 |

## 2. Chronologie (proposition → décision → validation)

| Date | Fait | Type | Source |
|---|---|---|---|
| 7 juil. | Démarrage : Élodie Caron chargée de projet, budget 180 000 $, cible 15 oct. | Décision | M03_CR_Comite_27aout.txt — [L9]-[L11] |
| 18 juil. | Architecture v1 : données en East US. | Historique | Teams_22sept_Mobile.txt — [page 1] |
| 22 juil. | Sophie Lambert demande que les données de production restent au Canada. | Demande | E03_Confirmation_Canada_Central.eml — [L5] |
| 23 juil. | Atelier : décision Canada Central (ADR-007, statut Acceptée). | Décision | M04_Transcript_Comite_direction_10sept.txt — [L13]-[L16]; Teams_19sept_Securite.txt — [L4], [L10] |
| 14 août | CR-01 (24 000 $) approuvé par le comité de projet. | Décision | ADR-007_Localisation_donnees.md — [page 1] |
| 15 / 20 août | ACC-301 (libellés) et ACC-302 (contraste) re-testés et fermés par Mélissa Gagnon. | Validation | ACC-302_contraste.png — [L16]; ACC-303_focus.png — [L16] |
| 26 août | Boréal déclare la migration Canada Central complétée. | Livraison (déclaration) | E04_Corrections_accessibilite.eml — [L3], [L5] |
| 27 août | Comité : migration vérifiée par l'équipe architecture. | Validation | M05_CR_Suivi_18sept.txt — [L5] |
| 4 sept. | CR-04 mobile (18 000 $) déposé en brouillon par Boréal. | Proposition | Architecture_NOVA_v1.pdf — [page 1] |
| 5 sept. | INT-101 : recherches vides en intégration (jeton expiré, erreurs 401). | Problème | OPS-601.txt — [L14]-[L15]; PERF-501.txt — [L1]-[L2] |
| 8 sept. | Boréal **propose** de déplacer le go-live au 22 oct. | Proposition | E06_Transition_charge_projet.eml — [L5], [L7] |
| 10 sept. | Comité de direction : 22 oct. **approuvé** (décision formulée par É. Caron, sans opposition). | Décision | M06_Transcript_Comite_26sept.txt — [L17]-[L23] |
| 16 sept. | Nicolas Perron devient chargé de projet. | Décision | E07_Facture_003_question.eml — [L3] |
| 17 sept. | INT-101 corrigé (rotation du secret + renouvellement du jeton), 120/120, fermé par Marc Gervais. | Validation | OPS-601.txt — [L17]-[L20]; M01_CR_Demarrage_07juillet.txt — [L3], [L5] |
| 17 sept. | ACC-303 ouvert : Enregistrer inatteignable au clavier dans la modale. | Problème | DATA-401_doublons.png — [L6], [L14] |
| 19 sept. | Correctif SEC-210 déployé en validation par Boréal. | Livraison | E09_Rappel_mise_en_production.eml — [L3] |
| 22 sept. | INV-003 reçue : 54 000 $, dont 18 000 $ CR-04. | Facturation | Teams_15sept_ProjetNOVA.txt — [page 1] |
| 24 sept. | CR-04 reporté en phase 2; aucune dépense sans nouvelle approbation. | Décision | INV-778_Projet_ORION.pdf — [L4]; E11_Communication_statut.eml — [L3], [L5] |
| 25 sept. | Runbook (version du 25 sept.) : étapes 4 et 5 incomplètes; OPS-601 ouvert. | Problème | SEC-210.txt — [capture, élément 1], [6], [7]; PERF-501_lenteur.png — [L6] |
| 26 sept. | Comité : 22 oct. conditionnel à trois conditions. SEC-210 reste EN VALIDATION. | Décision | ACC-301_labels.png — [L11]-[L16]; Note_transition_Elodie_16sept.txt — [L25] |
| 29 sept. | Olivier Côté n'a toujours pas reçu le runbook final. | Suivi | PERF-501_lenteur.png — [L16] |

## 3. Contradictions résolues

| # | Contradiction | Ce qui prévaut et pourquoi |
|---|---|---|
| C1 | **Plan projet** : la ligne P-06 « Mise en production » indique encore le 15 oct. (CR-01_Rapports_avances_APPROUVE.pdf — [feuille 'Plan projet', ligne 7 (A7:G7)], F7=2026-10-15). | **22 oct.** : la décision du comité du 10 sept. (M06… — [L23]) est postérieure et fait autorité. Le plan n'a pas été corrigé (Newsletter_Boreal_Septembre.txt — [L5]). Le responsable de cette ligne y est déjà Nicolas Perron : la mise à jour a été partielle. |
| C2 | **Registre de risques** : R-01 « Retard du connecteur interne » reste **Ouvert**, avec un suivi au 9 sept. (INV-001.pdf — [feuille 'Risques', ligne 2 (A2:H2)]). | **INT-101 est fermé le 17 sept.** après validation 120/120 (OPS-601.txt — [L18]; M01_CR_Demarrage_07juillet.txt — [L5]). Le registre est antérieur à la fermeture. |
| C3 | **Rapport de statut du 21 sept.** : Sécurité et Accessibilité « VERT » (CR-04_Optimisation_mobile_BROUILLON.pdf — [page 1]), repris dans un brouillon de communication (E12_Resolution_integration.eml — [L5]). | **Non accepté** : SEC-210 reste EN VALIDATION (Note_transition_Elodie_16sept.txt — [L25]), ACC-303 reste OUVERT (DATA-401_doublons.png — [L16]). Le rapport admet avoir été préparé avant la vérification détaillée. |
| C4 | **Hébergement** : l'architecture v1 indique East US (Teams_22sept_Mobile.txt — [page 1]). | **Canada Central** : ADR-007 acceptée le 23 juil. (Teams_19sept_Securite.txt — [L4], [L10]); v2 (Courriel_archive_17sept.eml — [page 1]). |
| C5 | **Accessibilité** : Boréal écrit le 20 août que « tout devrait maintenant être conforme » (E05_Retard_integration.eml — [L3]). | C'est une déclaration du fournisseur. ACC-303 est ouvert depuis le 17 sept. et bloquant (ACC-301_labels.png — [L9]). |
| C6 | **Mobile** : Boréal pensait l'optimisation avancée incluse (MANIFEST.csv — [L4]) et l'a facturée (INV-003). | **Hors portée** : la portée du contrat (INV-003.pdf — [page 1]) et la décision du 24 sept. (INV-778_Projet_ORION.pdf — [L4]) l'excluent. |

## 4. Actions restantes

« Engagement » = action déjà documentée dans le corpus. « Recommandation » = proposition de notre équipe.

| # | Action | Responsable | Échéance | Nature | Preuve |
|---|---|---|---|---|---|
| A1 | Re-test et acceptation sécurité de SEC-210 (**condition 1**) | Sophie Lambert (confirmée) | À confirmer (re-test planifié, sans date); avant le go-live du 22 oct. | Engagement | Note_transition_Elodie_16sept.txt — [L25]; INV-001.pdf — [feuille 'Risques', ligne 3 (A3:H3)] |
| A2 | Livrer le correctif ACC-303 (**condition 2**) | Boréal / Julien Moreau (confirmé) | « Prochaine build » : date à confirmer | Engagement | ACC-301_labels.png — [L15]; DATA-401_doublons.png — [L16] |
| A3 | Re-tester et fermer ACC-303 (**condition 2**) | Mélissa Gagnon (proposée : propriétaire du risque R-04) | À confirmer | Engagement (fermeture requise) | INV-001.pdf — [feuille 'Risques', ligne 5 (A5:H5)] |
| A4 | Compléter le runbook : rollback (étape 4) et validation post-déploiement (étape 5) (**condition 3**) | Boréal, équipe ops (relance par Julien Moreau) | À confirmer; Olivier Côté veut la version finale « quelques jours avant » le go-live | Engagement | SEC-210.txt — [capture, élément 6], [7]; ACC-301_labels.png — [L15]; M06… — [L12] |
| A5 | Approuver le runbook (go exploitation) (**condition 3**) | Olivier Côté (confirmé) | À confirmer | Engagement | ACC-301_labels.png — [L10]; PERF-501_lenteur.png — [L14]-[L16] |
| A6 | Ne pas libérer la ligne CR-04 de 18 000 $ d'INV-003 sans nouvelle approbation | Amélie Fortin (Finances) / Nicolas Perron | À confirmer | Engagement | E11_Communication_statut.eml — [L5]; E08_Correctif_journalisation.eml — [L5] |
| A6b | Valider et payer séparément la ligne jalon 3 (36 000 $), qui n'est pas contestée | Amélie Fortin (Finances) | À confirmer | **Recommandation** | Teams_15sept_ProjetNOVA.txt — [page 1] |
| A7 | Demander à Boréal une facture corrigée (ou une note de crédit) | Nicolas Perron (proposé) | À confirmer | **Recommandation** | — |
| A8 | Mettre à jour le plan projet (P-06 au 22 oct.) | Nicolas Perron | À confirmer | Engagement | Registre_Risques_29sept.xlsx — [L7]; Newsletter_Boreal_Septembre.txt — [L5] |
| A9 | Fermer R-01 dans le registre et y tracer les trois conditions | Marc Gervais (proposé : propriétaire de R-01) | À confirmer | **Recommandation** | INV-001.pdf — [feuille 'Risques', ligne 2 (A2:H2)] |
| A10 | Ne pas diffuser le message « NOVA au vert »; communiquer le 22 oct. comme conditionnel | Nicolas Perron / Alex Deschamps | En vigueur (consigne du 27 sept.) | Engagement | E10_Fonction_mobile.eml — [L7]; E12_Resolution_integration.eml — [L5] |

## 5. Incertitudes et limites

- Aucune date n'est documentée pour le re-test SEC-210, la prochaine build ACC-303 ou le runbook final : elles restent **à confirmer**.
- Le registre de risques (INV-001.pdf) n'est pas daté; seul R-01 porte un commentaire (« Suivi au 9 septembre 2026 »).
- Les captures d'écran sont des transcriptions manuelles. Une capture historique ne prouve pas à elle seule qu'un défaut est encore ouvert : l'état est établi par les tickets et les comités.
- Une pièce jointe identique à un autre fichier du corpus (vérifié par empreinte SHA-256) n'est pas une confirmation indépendante.
