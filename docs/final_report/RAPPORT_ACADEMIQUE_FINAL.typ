#set page(
  paper: "a4",
  margin: (top: 2.4cm, right: 2.2cm, bottom: 2.4cm, left: 2.2cm),
  numbering: "1",
)

#set text(
  font: "New Computer Modern",
  size: 11pt,
)

#set par(
  justify: true,
  leading: 0.68em,
)

#set table(
  stroke: (x: 0.45pt + rgb("#c5ced6"), y: 0.45pt + rgb("#c5ced6")),
  inset: 6pt,
)

#let primary = rgb("#0f3d5e")
#let accent = rgb("#2e6f95")
#let soft = rgb("#4b5563")

#align(center)[
  #v(1.7cm)
  #text(25pt, weight: "bold", fill: primary)[BI Adaptative]
  #v(5mm)
  #text(15pt, weight: "semibold", fill: accent)[Recommandation Personnalisee pour Metabase]
  #v(5mm)
  #text(14pt, fill: soft)[Rapport Academique Final]

  #v(15mm)
  #rect(
    width: 95%,
    inset: 12pt,
    radius: 8pt,
    fill: rgb("#f4f8fb"),
    stroke: 0.7pt + rgb("#d2deea"),
  )[
    #align(left)[
      *Etablissement:* ISI / S8 - SI & Big Data Engineering \
      *Module:* Projet BI & IA \
      *Date:* 31 mai 2026 \
      *Equipe:* BOUBKER NAQI - HAJJI IMRANE \
      *Role principal:* Partie "Cerveau" (Data Pipeline & Machine Learning)
    ]
  ]

  #v(18mm)
  #text(11pt, fill: soft)[Version pour soutenance]
]

#pagebreak()

#outline(title: [Table des matieres])

#pagebreak()

= Resume

Ce projet traite un probleme frequent des plateformes BI: la surcharge
d'information. Lorsqu'un utilisateur ouvre Metabase, il peut avoir des dizaines
de rapports disponibles, sans assistance intelligente pour prioriser les plus
pertinents.

La solution proposee est un systeme de recommandation adaptatif, integre autour
d'un pipeline de donnees asynchrone:

`Metabase -> RabbitMQ -> Consumer Python -> PostgreSQL -> Moteur ML -> API FastAPI`

Le systeme construit des recommandations personnalisees a partir des
interactions utilisateur et des metadonnees des rapports. Trois familles de
modeles ont ete evaluees: Collaborative Filtering, Content-Based Filtering et
approche Hybride. Le modele hybride `hybrid_knn_content` a ete retenu pour le
serving.

Le projet est valide par tests unitaires, integration, E2E et stress test. Il
est demotrable localement via Docker.

= 1. Contexte et cadrage

== 1.1 Sujet initial

#figure(
  image("assets/brief-projet.png", width: 92%),
  caption: [Brief du projet donne dans l'enonce initial.],
)

Le sujet demande:
- collecte des logs de navigation,
- construction d'un moteur collaborative + content-based,
- integration des recommandations dans l'interface BI,
- evaluation de l'impact.

== 1.2 Modalites d'evaluation academique

#figure(
  image("assets/modalites-evaluation.png", width: 92%),
  caption: [Modalites d'evaluation et criteres de notation.],
)

Le cadre officiel insiste sur:
- architecture,
- modelisation,
- tests,
- performances,
- demonstration live.

== 1.3 Probleme metier

Sans personnalisation, l'utilisateur BI perd du temps a chercher les rapports
les plus utiles. L'objectif metier est de reduire ce temps de recherche et
d'augmenter l'usage des rapports pertinents.

= 2. Objectifs du projet

== 2.1 Objectif general

Concevoir et livrer un systeme de recommandation BI adaptatif, robuste et
demotrable localement.

== 2.2 Objectifs techniques

+ Capturer les interactions Metabase.
+ Transporter les evenements de maniere asynchrone et resiliente.
+ Structurer et enrichir les donnees dans PostgreSQL.
+ Entrainer et comparer plusieurs modeles de recommandation.
+ Exposer les recommandations via API.
+ Stocker les recommandations en batch pour servir rapidement.
+ Monitorer l'etat du pipeline.
+ Valider la chaine complete par tests.

= 3. Methodologie de travail

La conduite du projet a suivi le principe:
`Learn -> Build -> Learn`.

- *Learn:* comprehension du besoin, limites de Metabase, exigences.
- *Build:* implementation incrementale du pipeline, des modeles et de l'API.
- *Learn:* tests, analyse des erreurs reelles, correction et consolidation.

Cette methodologie a permis de transformer une base partiellement initialisee
en systeme bout-en-bout valide.

= 4. Architecture globale

== 4.1 Vue d'architecture

#figure(
  image("assets/architecture-layers.png", width: 100%),
  caption: [Architecture en couches du systeme BI adaptatif.],
)

== 4.2 Vue du flux complet

#figure(
  image("assets/full-flow.png", width: 95%),
  caption: [Flux fonctionnel complet du systeme de recommandation.],
)

== 4.3 Carte mentale du projet

#figure(
  image("assets/mindmap-complete.png", width: 97%),
  caption: [Mindmap synthetisant composants, pipeline, ML et serving.],
)

== 4.4 Sequence logique simplifiee

```text
Utilisateur Metabase
  -> Metabase (UI + logs)
  -> Publisher Python
  -> RabbitMQ queues
  -> Consumer Python
  -> PostgreSQL
  -> Feature Engineering
  -> Modeles ML
  -> FastAPI
  -> Batch Recommendations + Monitoring
```

= 5. Stack technologique et justifications

#table(
  columns: (1.6fr, 1.4fr, 2.8fr),
  table.header(
    [*Composant*], [*Technologie*], [*Justification*],
  ),
  [BI Frontend], [Metabase], [Outil BI cible du projet],
  [Message Broker], [RabbitMQ], [Decouplage producteur/consommateur et resilience],
  [Base de donnees], [PostgreSQL], [SQL riche, indexation, persistance],
  [Backend IA/API], [Python + FastAPI], [Productivite et ecosysteme ML],
  [ML], [Surprise + scikit-learn], [Collaborative + content-based],
  [Orchestration], [Docker Compose], [Reproductibilite locale],
)

= 6. Pipeline de donnees

== 6.1 Ingestion des evenements

Le publisher recupere les donnees cibles et publie sur trois flux:
- `navigation_logs`
- `users_sync`
- `reports_sync`

== 6.2 Consommation et stockage

Le consumer:
+ lit le message RabbitMQ,
+ reconcilie les identifiants utilisateurs/rapports,
+ insere dans PostgreSQL.

== 6.3 Probleme reel observe et corrige

Un bug a ete detecte en test E2E: connexion PostgreSQL stale cote consumer.
Effet: un message restait `unacked`.

Correction appliquee:
- detection de connexion fermee,
- reconnexion automatique,
- rollback protege,
- `basic_qos(prefetch_count=1)`.

Ce point est critique: il valide la robustesse systeme, pas uniquement la
partie ML.

= 7. Schema de donnees et migrations

Migrations appliquees:
- `001_enrich_ml_event_schema.sql`
- `002_backfill_simulated_event_features.sql`
- `003_normalize_report_business_categories.sql`
- `004_batch_recommendations_schema.sql`
- `005_monitoring_views.sql`

Champs importants ajoutes:
- `source_event_id`, `event_type`, `duration_source`, `raw_payload`,
- `batch_id`, `rank`, `model_version`, `metadata` dans `recommendations`.

= 8. Preparation des donnees et features

== 8.1 Limite metier importante

Metabase ne fournit pas toujours une duree fiable de consultation.
Solution temporaire: `duration` simulee et tracee avec `duration_source`.

== 8.2 Split train/test

Split temporel par utilisateur:
- train: interactions anciennes,
- test: interactions recentes.

== 8.3 Features principales

- `view_count`
- `selection_count`
- `total_duration`
- `avg_duration`
- `recency_days`
- `selection_rate`
- `implicit_rating` (normalisee entre 1 et 5)

= 9. Modeles de recommandation

== 9.1 Modeles compares

+ Baseline Collaborative user-based cosine.
+ Surprise SVD.
+ Surprise KNN.
+ Content-Based TF-IDF.
+ Hybride CF + Content.

== 9.2 Modele retenu

`hybrid_knn_content` avec:
- composante collaborative: KNN,
- composante contenu: TF-IDF,
- poids: 0.6 (CF) / 0.4 (Content).

= 10. Evaluation offline

== 10.1 Metriques

- Precision\@K
- Recall\@K
- HitRate\@K
- NDCG\@K
- Catalog Coverage\@K

== 10.2 Resultats principaux (top-5)

#table(
  columns: (2.4fr, 0.6fr, 1fr, 1fr, 1fr, 1fr, 1fr),
  table.header(
    [*Modele*], [*K*], [*Precision\@K*], [*Recall\@K*], [*HitRate\@K*], [*NDCG\@K*], [*Coverage\@K*],
  ),
  [hybrid_knn_content], [5], [0.140], [0.0618], [0.49], [0.1322], [0.875],
  [tuned_surprise_svd], [5], [0.130], [0.0556], [0.50], [0.1211], [0.625],
  [tuned_surprise_knn], [5], [0.124], [0.0532], [0.47], [0.1321], [0.950],
  [baseline_user_based_cf], [5], [0.124], [0.0535], [0.48], [0.1195], [0.575],
  [content_based_tfidf], [5], [0.122], [0.0539], [0.49], [0.1189], [0.750],
)

Interpretation:
- meilleur compromis top-5: modele hybride,
- meilleure couverture: KNN pur,
- decision finale orientee usage API top-5.

= 11. Serving et API

== 11.1 Endpoints

- `GET /health`
- `POST /train`
- `GET /recommendations/{user_id}?n=5`
- `POST /batch/recommendations/generate?n=5`
- `GET /stored-recommendations/{user_id}?n=5`
- `GET /batch/status`
- `GET /monitoring/summary`

== 11.2 Batch serving

Le batch pre-calcule les recommandations pour tous les utilisateurs et les
stocke dans `recommendations`.

Avantages:
- reponses API rapides,
- auditabilite (`batch_id`, `model_version`),
- demo stable.

= 12. Validation technique

== 12.1 Tests realises

- unit tests ML/data prep,
- integration (DB + API + batch),
- E2E synthetique (RabbitMQ -> Consumer -> DB -> API),
- stress test sur lecture recommandations stockees.

== 12.2 Statut

*Suite Phase 6: PASS*

= 13. Etat actuel du systeme

#table(
  columns: (2.7fr, 1fr),
  table.header([*Indicateur*], [*Valeur*]),
  [Users], [100],
  [Reports], [40],
  [Navigation logs], [9965],
  [Logs avec duree], [9965],
  [Recommendations stockees], [4500],
  [Batches de recommandations], [9],
)

= 14. Scenario de demonstration en soutenance

Le scenario detaille est fourni dans:
`docs/final_report/SCENARIO_DEMO_PROF.md`.

Objectif: montrer en direct la chaine complete de bout en bout, avec preuves
quantitatives et indicateurs de monitoring.

= 15. Discussion critique

== 15.1 Forces

- architecture complete et coherente,
- separation claire data pipeline / ML / serving,
- robustesse amelioree apres bug reel,
- evaluation objective avec metriques standard.

== 15.2 Limites

- duree encore simulee,
- volume de donnees limite,
- absence d'authentification forte pour production.

= 16. Perspectives

+ Instrumentation front pour duree reelle et sessions.
+ Feedback online (clic recommendation -> apprentissage).
+ A/B test reel par cohortes utilisateurs.
+ CI/CD automatisant la suite de tests.
+ Durcissement securite API.

= 17. Conclusion

Le projet atteint son objectif principal: livrer un moteur de recommandation BI
adaptatif, integre, teste et demotrable localement.

La contribution majeure est d'avoir transforme une idee de recommandation BI en
systeme operationnel complet avec:
- pipeline resilient,
- modeles compares puis selectionnes,
- API de serving,
- batch stockage,
- monitoring,
- scenario de demonstration reproductible.

= 18. Alignement avec la grille d'evaluation

Cette section relie explicitement les livrables aux criteres de notation.

#table(
  columns: (2fr, 0.9fr, 2.8fr),
  table.header([*Critere*], [*Poids*], [*Preuves concretes*]),
  [Realisation technique], [40%], [
    Architecture complete, pipeline asynchrone RabbitMQ,
    migrations SQL, API FastAPI, batch serving, tests multi-niveaux.
  ],
  [Qualite BI / visualisation], [30%], [
    Integration Metabase, endpoint monitoring, vues SQL monitoring,
    recommandations top-5 servies et exploitable en dashboard.
  ],
  [Originalite / complexite], [20%], [
    Modele hybride compare a CF/CB, selection par metriques,
    correction d'un bug de resilience consumer en conditions reelles.
  ],
  [Documentation], [10%], [
    Rapport academique complet, scenario de demo, FAQ soutenance,
    scripts de collecte de preuves, tutoriel d'exploitation.
  ],
)

= 19. Roles Personne A / Personne B

Cette section clarifie ce qui est finalise dans le scope MVP demo.

#table(
  columns: (1.2fr, 2.1fr, 1fr),
  table.header([*Role*], [*Responsabilites couvertes*], [*Statut*]),
  [Personne A (Data & AI)], [
    Data prep, feature engineering, modeles CF/CB/Hybrid, evaluation offline,
    API de recommandation, batch serving, monitoring API.
  ], [Complete (MVP)],
  [Personne B (Backend & Integration)], [
    Docker stack, publisher/consumer RabbitMQ, pipeline DB, resilience,
    tests E2E/integration, demo locale operationnelle.
  ], [Complete (MVP)],
)

Points avances non finalises (hors MVP):
- bandits contextuels (proposal only),
- A/B test reel en production (proposal only),
- pipeline CI/CD GitHub Actions complet.

= 20. Plan de demonstration oral (20 min)

Plan recommande:

+ 2 min: probleme metier + objectif.
+ 3 min: architecture et data flow.
+ 6 min: demo live (`docker-compose ps`, `demo_local.py`, API).
+ 4 min: preuves techniques (monitoring, DB counts, tests PASS).
+ 3 min: resultats ML et choix du modele hybride.
+ 2 min: limites, perspectives, questions.

Scripts de reference:
- `docs/final_report/SCENARIO_DEMO_PROF.md`
- `docs/final_report/ORAL_SCRIPT_7MIN.md`

= Annexes

- `docs/final_report/QUESTIONS_PROF_REPONSES.md`
- `docs/LOCAL_DEMO_GUIDE.md`
- `docs/PHASE6_TEST_REPORT.md`
- `backend/ml_engine/evaluation_results/model_optimization_report.md`
- `docs/final_report/TUTORIAL_TESTER_UTILISER_SOLUTION.md`

== Captures live a inserer le jour J

1) Page Metabase avec un dashboard ouvert. \
2) RabbitMQ Management montrant les queues. \
3) FastAPI docs (`http://localhost:8000/docs`) avec endpoints. \
4) Sortie `monitoring/summary` apres execution `demo_local.py`.

Nommage recommande:
- `assets/live-metabase-dashboard.png`
- `assets/live-rabbitmq-queues.png`
- `assets/live-fastapi-docs.png`
- `assets/live-monitoring-summary.png`
