// ═══════════════════════════════════════════════════════════════════════════
// RAPPORT ACADÉMIQUE FINAL — BI Adaptative
// Recommandation Personnalisée pour Metabase
// ═══════════════════════════════════════════════════════════════════════════

// ─── Configuration de page ────────────────────────────────────────────────
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

#set heading(numbering: "1.1.")

// ─── Palette de couleurs ──────────────────────────────────────────────────
#let primary = rgb("#0f3d5e")
#let accent = rgb("#2e6f95")
#let soft = rgb("#4b5563")
#let success = rgb("#047857")
#let warning = rgb("#d97706")
#let danger = rgb("#dc2626")
#let info = rgb("#0284c7")

// ─── Composant : encadré (callout) ───────────────────────────────────────
#let callout(body, title: none, icon: "💡", color: accent) = {
  rect(
    width: 100%,
    inset: 12pt,
    radius: 6pt,
    fill: color.lighten(92%),
    stroke: 0.8pt + color,
  )[
    #if title != none [
      #text(weight: "bold", fill: color)[#icon #title] \
    ]
    #body
  ]
}

// ─── Composant : boîte « point clé » ────────────────────────────────────
#let keypoint(body) = callout(body, title: "Point clé", icon: "🎯", color: primary)

// ─── Composant : boîte « attention » ────────────────────────────────────
#let attention(body) = callout(body, title: "Attention", icon: "⚠️", color: warning)

// ═══════════════════════════════════════════════════════════════════════════
// PAGE DE COUVERTURE
// ═══════════════════════════════════════════════════════════════════════════
// PAGE DE GARDE
// ═══════════════════════════════════════════════════════════════════════════

#page(numbering: none)[
  #align(center)[

    // ── Logos Université + École ──
    #grid(
      columns: (1fr, 1fr),
      gutter: 20pt,
      align(center)[#image("../../logos/Universite-Hassan-1logo.png", height: 2.8cm)],
      align(center)[#image("../../logos/logoensab.png", height: 2.8cm)],
    )

    #v(4mm)

    #text(13pt, weight: "semibold", fill: primary)[Université Hassan Premier]
    #v(1mm)
    #text(12pt, fill: accent)[École Nationale des Sciences Appliquées de Berrechid]
    #v(1mm)
    #text(10.5pt, fill: soft)[Filière : Ingénierie des Systèmes d'Information et Big Data (ISIBD) — S8]

    #v(10mm)

    // ── Ligne séparatrice ──
    #line(length: 80%, stroke: 0.8pt + accent.lighten(40%))

    #v(10mm)

    // ── Bandeau titre du projet ──
    #rect(
      width: 100%,
      inset: 20pt,
      radius: 10pt,
      fill: gradient.linear(primary, accent, angle: 0deg),
    )[
      #align(center)[
        #text(13pt, fill: white.darken(5%))[Projet de module]
        #v(2mm)
        #text(24pt, weight: "bold", fill: white)[Business Intelligence]
        #v(5mm)
        #text(15pt, fill: white.darken(5%))[Système de Recommandation Personnalisée pour Metabase]
      ]
    ]

    #v(12mm)

    // ── Informations académiques ──
    #rect(
      width: 90%,
      inset: 14pt,
      radius: 8pt,
      fill: rgb("#f4f8fb"),
      stroke: 0.7pt + rgb("#d2deea"),
    )[
      #grid(
        columns: (1fr, 1fr),
        gutter: 10pt,
        [
          #align(left)[
            #text(weight: "bold", fill: primary)[Réalisé par :] \
            #v(2mm)
            HAJJI Imrane \
            BOUBKER Naqi
          ]
        ],
        [
          #align(left)[
            #text(weight: "bold", fill: primary)[Encadré par :] \
            #v(2mm)
            Prof. HRIMECH
          ]
        ],
      )
    ]

    #v(10mm)

    // ── Mots-clés ──
    #rect(
      width: 90%,
      inset: 10pt,
      radius: 6pt,
      fill: accent.lighten(93%),
      stroke: 0.6pt + accent.lighten(50%),
    )[
      #text(size: 9.5pt, fill: soft)[
        *Mots-clés :*
        Recommandation · Collaborative Filtering · Content-Based Filtering ·
        Modèle Hybride · Metabase · RabbitMQ · PostgreSQL · FastAPI ·
        TF-IDF · Surprise · Pipeline asynchrone · Évaluation offline
      ]
    ]

    #v(12mm)

    // ── Ligne séparatrice ──
    #line(length: 80%, stroke: 0.8pt + accent.lighten(40%))

    #v(5mm)

    #text(12pt, weight: "semibold", fill: primary)[Année universitaire 2025 / 2026]
  ]
]

#pagebreak()

// ═══════════════════════════════════════════════════════════════════════════
// TABLE DES MATIÈRES
// ═══════════════════════════════════════════════════════════════════════════

#outline(title: [Table des matières], depth: 3)

#pagebreak()

// ═══════════════════════════════════════════════════════════════════════════
// RÉSUMÉ EXÉCUTIF
// ═══════════════════════════════════════════════════════════════════════════

= Résumé exécutif

Ce projet s'attaque à un problème fréquent dans les plateformes de _Business
Intelligence_ (BI) : la *surcharge d'information*. Lorsqu'un utilisateur ouvre
Metabase, il peut se retrouver face à des dizaines, voire des centaines de
rapports disponibles, sans assistance intelligente pour prioriser les plus
pertinents. Le résultat : un temps de recherche excessif, une sous-utilisation
des rapports les plus utiles, et une frustration croissante des utilisateurs.

La solution proposée est un *système de recommandation adaptatif*, intégré
autour d'un pipeline de données asynchrone complet :

#align(center)[
  #rect(
    inset: 10pt,
    radius: 6pt,
    fill: primary.lighten(95%),
    stroke: 0.6pt + primary.lighten(60%),
  )[
    #text(size: 10pt, weight: "semibold", fill: primary)[
      Metabase → RabbitMQ → Consumer Python → PostgreSQL → Moteur ML → API FastAPI
    ]
  ]
]

Le système construit des recommandations personnalisées à partir de deux
sources complémentaires :
- les *interactions utilisateur* (qui a consulté quoi, combien de temps, combien de fois) ;
- les *métadonnées des rapports* (titre, description, catégorie métier).

Trois familles de modèles ont été implémentées, entraînées et évaluées de
manière rigoureuse :

#table(
  columns: (1.8fr, 3fr),
  table.header([*Famille*], [*Principe*]),
  [Collaborative Filtering], [Recommander les rapports appréciés par des utilisateurs aux profils similaires],
  [Content-Based Filtering], [Recommander des rapports similaires (par contenu) à ceux déjà consultés],
  [Hybride (CF + CB)], [Fusionner les deux approches pour un meilleur compromis précision/couverture],
)

Le modèle hybride `hybrid_knn_content` a été retenu pour le _serving_,
avec un poids de 60 % sur la composante collaborative (KNN) et 40 % sur
la composante contenu (TF-IDF). Ce choix est justifié par la meilleure
Precision\@5 (0.140), un bon NDCG\@5 (0.132), et une couverture
catalogue élevée (87.5 %).

Le projet est validé par des tests unitaires, d'intégration, end-to-end et de
stress. Il est démontrable localement via Docker Compose.

#pagebreak()

// ═══════════════════════════════════════════════════════════════════════════
// 1. CONTEXTE ET CADRAGE
// ═══════════════════════════════════════════════════════════════════════════

= Contexte et cadrage

== Sujet initial

#figure(
  image("assets/brief-projet.png", width: 92%),
  caption: [Brief du projet donné dans l'énoncé initial.],
)

Le sujet demande explicitement :
+ la collecte des logs de navigation des utilisateurs Metabase ;
+ la construction d'un moteur de recommandation combinant _collaborative
  filtering_ et _content-based filtering_ ;
+ l'intégration des recommandations dans l'interface BI ;
+ l'évaluation de l'impact sur l'utilisation.

== Modalités d'évaluation académique

#figure(
  image("assets/modalites-evaluation.png", width: 92%),
  caption: [Modalités d'évaluation et critères de notation.],
)

Le cadre officiel de notation insiste sur cinq dimensions :
- *Architecture* : qualité du design technique et de l'intégration des composants.
- *Modélisation* : rigueur dans la construction et la comparaison des modèles ML.
- *Tests* : couverture et robustesse de la validation (unitaire, intégration, E2E).
- *Performances* : métriques objectives et benchmarks reproductibles.
- *Démonstration live* : capacité à montrer le système en fonctionnement réel.

== Problème métier : la surcharge d'information

=== Le constat

Dans une entreprise dotée d'un outil BI comme Metabase, les utilisateurs —
managers, analystes, directeurs — font face à un problème croissant :

#callout(
  title: "Le problème en chiffres",
  icon: "📊",
  color: danger,
)[
  - *200+ rapports* disponibles dans l'instance Metabase \
  - *60 % des rapports* ne sont jamais consultés par l'utilisateur moyen \
  - *30 minutes/jour* perdues à chercher les bons dashboards \
  - Les utilisateurs se rabattent sur *5–6 rapports habituels* et ignorent
    des insights potentiellement décisifs
]

Sans personnalisation, l'utilisateur BI subit un *coût cognitif élevé* :
il doit parcourir manuellement un catalogue dense, trier mentalement les
rapports pertinents pour son rôle, et se souvenir de ceux qu'il a déjà
consultés.

=== La solution : recommandation intelligente

Notre système ajoute une couche d'intelligence artificielle au-dessus de
Metabase :

#figure(
  image("assets/avant-apres-metabase.jpg", width: 90%),
  caption: [Comparaison AVANT / APRÈS : Metabase sans et avec recommandation IA.],
)

#v(4mm)

#table(
  columns: (1.2fr, 2fr, 2.5fr),
  table.header([*Dimension*], [*AVANT (sans IA)*], [*APRÈS (avec IA)*]),
  [Recherche], [Manuelle, longue], [Top-5 personnalisé instantané],
  [Couverture], [5–6 rapports habituels], [Découverte de rapports inattendus],
  [Satisfaction], [Frustration croissante], [Expérience fluide et pertinente],
  [Temps perdu], [~30 min/jour], [Objectif : -60 % de réduction],
)

#pagebreak()

// ═══════════════════════════════════════════════════════════════════════════
// 2. OBJECTIFS DU PROJET
// ═══════════════════════════════════════════════════════════════════════════

= Objectifs du projet

== Objectif général

Concevoir et livrer un *système de recommandation BI adaptatif*, robuste
et démontrable localement, capable de proposer les rapports les plus pertinents
à chaque utilisateur en fonction de son historique de navigation et du contenu
des rapports.

== Objectifs techniques

+ *Capturer* les interactions Metabase (consultations, sélections, durées).
+ *Transporter* les événements de manière asynchrone et résiliente via RabbitMQ.
+ *Structurer* et enrichir les données dans PostgreSQL (schéma normalisé).
+ *Construire* des features exploitables (fréquence, récence, durée, taux de sélection).
+ *Entraîner et comparer* trois familles de modèles de recommandation.
+ *Exposer* les recommandations via une API REST performante.
+ *Stocker* les recommandations en _batch_ pour un _serving_ rapide.
+ *Monitorer* l'état du pipeline et la santé du système.
+ *Valider* la chaîne complète par une suite de tests multi-niveaux.

== Objectifs quantitatifs

#table(
  columns: (2.4fr, 1fr, 2.5fr),
  table.header([*Objectif*], [*Cible*], [*Justification*]),
  [Réduction du temps de recherche], [-60 %], [Rapports pertinents en premier],
  [Augmentation de l'usage], [+80 %], [Découverte de rapports utiles],
  [Precision\@5], [> 0.12], [Au moins 60 % de recommandations pertinentes dans le Top-5],
  [Couverture catalogue], [> 70 %], [Diversité des recommandations],
  [Latence API], [< 500 ms], [Expérience utilisateur fluide],
)

#pagebreak()

// ═══════════════════════════════════════════════════════════════════════════
// 3. MÉTHODOLOGIE DE TRAVAIL
// ═══════════════════════════════════════════════════════════════════════════

= Méthodologie de travail

La conduite du projet a suivi le principe itératif *Learn → Build → Learn* :

#rect(
  width: 100%,
  inset: 14pt,
  radius: 8pt,
  fill: rgb("#f0f7ff"),
  stroke: 0.6pt + accent.lighten(50%),
)[
  #grid(
    columns: (1fr, 1fr, 1fr),
    gutter: 12pt,
    [
      #align(center)[
        #text(24pt)[📚]
        #v(2mm)
        #text(weight: "bold", fill: primary)[Learn]
      ]
      Comprendre le besoin, les limites de Metabase, les exigences académiques.
      Étudier les API disponibles et le schéma de données.
    ],
    [
      #align(center)[
        #text(24pt)[🔨]
        #v(2mm)
        #text(weight: "bold", fill: accent)[Build]
      ]
      Implémentation incrémentale du pipeline, des modèles ML et de l'API.
      Tests à chaque étape.
    ],
    [
      #align(center)[
        #text(24pt)[🔍]
        #v(2mm)
        #text(weight: "bold", fill: success)[Learn]
      ]
      Tests, analyse des erreurs réelles, correction, consolidation.
      Évaluation objective des modèles.
    ],
  )
]

#v(3mm)

Cette méthodologie a permis de transformer une base partiellement initialisée
en système bout-en-bout validé. Chaque itération a enrichi la compréhension
du domaine et amélioré la qualité du code.

*Exemple concret :* lors de la phase Build du consumer RabbitMQ, un bug de
connexion PostgreSQL _stale_ a été détecté en conditions réelles. La phase
Learn suivante a conduit à implémenter une reconnexion automatique et un
mécanisme de _rollback_ protégé — un ajout qui n'aurait pas été prévu sans
cette approche itérative.

#pagebreak()

// ═══════════════════════════════════════════════════════════════════════════
// 4. ARCHITECTURE GLOBALE
// ═══════════════════════════════════════════════════════════════════════════

= Architecture globale

== Vue d'architecture en couches

#figure(
  image("assets/architecture-layers.png", width: 100%),
  caption: [Architecture en couches du système BI adaptatif.],
)

L'architecture suit un modèle en couches découplées, où chaque composant a
une responsabilité unique :

#table(
  columns: (1.6fr, 3.2fr),
  table.header([*Couche*], [*Responsabilité*]),
  [Présentation], [Metabase — affiche les rapports et capture les interactions utilisateur],
  [Transport], [RabbitMQ — file d'attente asynchrone, découple l'émetteur du récepteur],
  [Ingestion], [Consumer Python — écoute les messages, nettoie, insère dans PostgreSQL],
  [Stockage], [PostgreSQL — persistence structurée des utilisateurs, rapports, logs et recommandations],
  [Intelligence], [ML Engine Python — entraînement et génération des recommandations],
  [Serving], [FastAPI — expose les recommandations via des endpoints REST],
  [Orchestration], [Docker Compose — déploiement local reproductible de tous les services],
)

== Vue du flux complet

#figure(
  image("assets/full-flow.png", width: 95%),
  caption: [Flux fonctionnel complet du système de recommandation.],
)

== Carte mentale du projet

#figure(
  image("assets/mindmap-complete.png", width: 97%),
  caption: [Mindmap synthétisant composants, pipeline, ML et serving.],
)

== Les trois phases du flux de données

Le système fonctionne en *trois phases distinctes*, chacune avec son propre
rythme et ses propres contraintes :

#v(3mm)

// ── Phase 1 : Collecte ───────────────────────────────────────────────────
#rect(
  width: 100%,
  inset: 12pt,
  radius: 6pt,
  fill: success.lighten(93%),
  stroke: 0.8pt + success,
)[
  #text(weight: "bold", fill: success)[🟢 Phase 1 — Collecte (temps réel)]

  #v(2mm)

  L'utilisateur consulte un rapport dans Metabase. Le *Publisher Python* interroge
  périodiquement l'API Metabase (toutes les 5 secondes par défaut) pour détecter
  les événements de navigation. Chaque événement est publié dans RabbitMQ sous
  forme de message JSON. Le *Consumer Python* écoute la queue en continu, réconcilie
  les identifiants (user, report), et insère les données dans PostgreSQL.

  ```text
  Utilisateur → Metabase → Publisher → RabbitMQ → Consumer → PostgreSQL
  ```

  *Résultat :* les données brutes d'interaction (qui a vu quoi, quand, combien
  de temps) sont disponibles en base en quasi temps réel.
]

#v(3mm)

// ── Phase 2 : Traitement ─────────────────────────────────────────────────
#rect(
  width: 100%,
  inset: 12pt,
  radius: 6pt,
  fill: info.lighten(93%),
  stroke: 0.8pt + info,
)[
  #text(weight: "bold", fill: info)[🔵 Phase 2 — Traitement (batch quotidien)]

  #v(2mm)

  Un job quotidien (déclenché via l'endpoint `POST /train` ou le scheduler
  intégré) charge les interactions des derniers jours, calcule les features
  utilisateur-rapport, entraîne les trois modèles (CF, CB, Hybride), et génère
  les Top-5 recommandations pour chaque utilisateur.

  ```text
  PostgreSQL → Feature Engineering → Modèles ML → Recommandations
  ```

  *Résultat :* la table `recommendations` est peuplée avec les recommandations
  personnalisées, indexées par `batch_id` et `model_version`.
]

#v(3mm)

// ── Phase 3 : Serving ────────────────────────────────────────────────────
#rect(
  width: 100%,
  inset: 12pt,
  radius: 6pt,
  fill: rgb("#7c3aed").lighten(93%),
  stroke: 0.8pt + rgb("#7c3aed"),
)[
  #text(weight: "bold", fill: rgb("#7c3aed"))[🟣 Phase 3 — Serving (temps réel)]

  #v(2mm)

  Lorsqu'un utilisateur ouvre Metabase, l'API FastAPI fournit instantanément
  ses recommandations pré-calculées depuis la table `recommendations`. Aucun
  calcul ML n'est nécessaire au moment de la requête : les données sont déjà
  prêtes.

  ```text
  GET /stored-recommendations/{user_id} → Top-5 JSON → Metabase affiche
  ```

  *Résultat :* temps de réponse < 50 ms grâce au _batch serving_ pré-calculé.
]

#pagebreak()

// ═══════════════════════════════════════════════════════════════════════════
// 5. STACK TECHNOLOGIQUE ET JUSTIFICATIONS
// ═══════════════════════════════════════════════════════════════════════════

= Stack technologique et justifications

#table(
  columns: (1.6fr, 1.4fr, 2.8fr),
  table.header([*Composant*], [*Technologie*], [*Justification*]),
  [BI Frontend], [Metabase], [Outil BI cible du projet, open-source, API REST documentée],
  [Message Broker], [RabbitMQ], [Découplage producteur/consommateur, persistance des messages, résilience aux pannes],
  [Base de données], [PostgreSQL 15], [SQL riche, indexation B-tree, types JSON, vues matérialisées],
  [Backend IA/API], [Python + FastAPI], [Productivité, écosystème ML (NumPy, pandas, scikit-learn), async natif],
  [ML — CF], [Surprise], [Bibliothèque spécialisée en filtrage collaboratif (SVD, KNN)],
  [ML — CB], [scikit-learn], [TF-IDF, similarité cosinus, robuste et bien documenté],
  [Orchestration], [Docker Compose], [Reproductibilité locale, isolation des services, healthchecks],
)

#keypoint[
  Le choix de RabbitMQ plutôt qu'un simple appel HTTP synchrone entre
  le Publisher et le Consumer est *stratégique* : si le Consumer tombe,
  les messages restent dans la queue et seront traités au redémarrage.
  Cela garantit la *non-perte de données*.
]

#pagebreak()

// ═══════════════════════════════════════════════════════════════════════════
// 6. PIPELINE DE DONNÉES
// ═══════════════════════════════════════════════════════════════════════════

= Pipeline de données

== Ingestion des événements

Le *Publisher* est un service Python qui fonctionne en continu et alimente
trois flux RabbitMQ :

#table(
  columns: (1.6fr, 2fr, 2fr),
  table.header([*Queue*], [*Contenu*], [*Fréquence*]),
  [`navigation_logs`], [Événements de consultation et sélection de rapports], [Toutes les 5 s (configurable)],
  [`users_sync`], [Synchronisation des métadonnées utilisateur depuis Metabase], [À chaque cycle de polling],
  [`reports_sync`], [Synchronisation des métadonnées des rapports], [À chaque cycle de polling],
)

Chaque message est un objet JSON contenant au minimum :
```json
{
  "user_id": 42,
  "report_id": 5,
  "timestamp": "2026-05-30T14:32:00Z",
  "action": "view",
  "duration": 187.5,
  "metabase_model": "card"
}
```

== Consommation et stockage

Le *Consumer* :
+ lit chaque message RabbitMQ avec `basic_consume` ;
+ réconcilie les identifiants utilisateurs et rapports (résolution Metabase ID → ID interne PostgreSQL) ;
+ insère dans PostgreSQL via des requêtes paramétrées ;
+ acquitte le message (`basic_ack`) uniquement *après* insertion réussie.

== Problème réel observé et corrigé

#attention[
  Un bug a été détecté en test E2E : la connexion PostgreSQL côté consumer
  devenait _stale_ après une période d'inactivité. *Effet :* un message
  restait `unacked` indéfiniment, bloquant la queue.
]

*Corrections appliquées :*
- Détection de connexion fermée via `conn.closed`
- Reconnexion automatique avec _backoff_ exponentiel
- _Rollback_ protégé en cas d'erreur d'insertion
- `basic_qos(prefetch_count=1)` pour limiter la charge

Ce point est *critique* pour la soutenance : il démontre la robustesse
du système face à des conditions réelles, pas uniquement la partie ML.

#pagebreak()

// ═══════════════════════════════════════════════════════════════════════════
// 7. SCHÉMA DE DONNÉES ET MIGRATIONS
// ═══════════════════════════════════════════════════════════════════════════

= Schéma de données et migrations

== Tables principales

Le schéma PostgreSQL est structuré autour de quatre tables principales,
chacune ayant un rôle précis dans le pipeline :

=== Table `users`

Stocke les métadonnées des utilisateurs Metabase.

```sql
CREATE TABLE users (
    id              SERIAL PRIMARY KEY,
    metabase_user_id INTEGER UNIQUE,
    email           VARCHAR(255),
    first_name      VARCHAR(100),
    last_name       VARCHAR(100),
    role            VARCHAR(50),
    created_at      TIMESTAMP DEFAULT NOW()
);
```

=== Table `reports`

Stocke les métadonnées des rapports/dashboards Metabase. Ces informations
sont utilisées par le modèle _content-based_.

```sql
CREATE TABLE reports (
    id                  SERIAL PRIMARY KEY,
    metabase_report_id  INTEGER UNIQUE,
    title               VARCHAR(255),
    description         TEXT,
    tags                TEXT,
    category            VARCHAR(100),
    business_category   VARCHAR(100) DEFAULT 'general',
    created_at          TIMESTAMP DEFAULT NOW()
);
```

=== Table `navigation_logs`

Cœur du système — chaque ligne représente une interaction utilisateur-rapport.

```sql
CREATE TABLE navigation_logs (
    id                SERIAL PRIMARY KEY,
    user_id           INTEGER REFERENCES users(id),
    report_id         INTEGER REFERENCES reports(id),
    timestamp         TIMESTAMP NOT NULL,
    action            VARCHAR(20) DEFAULT 'view',
    duration          FLOAT DEFAULT 0,
    duration_source   VARCHAR(20) DEFAULT 'simulated',
    event_type        VARCHAR(50),
    metabase_model    VARCHAR(50),
    source_event_id   VARCHAR(100),
    raw_payload       JSONB
);
```

=== Table `recommendations`

Stocke les recommandations pré-calculées par le moteur ML.

```sql
CREATE TABLE recommendations (
    id                      SERIAL PRIMARY KEY,
    user_id                 INTEGER REFERENCES users(id),
    recommended_report_id   INTEGER REFERENCES reports(id),
    rank                    INTEGER,
    score                   FLOAT,
    algorithm               VARCHAR(100),
    model_version           TEXT,
    batch_id                VARCHAR(100),
    metadata                JSONB,
    generated_at            TIMESTAMP DEFAULT NOW(),
    clicked                 BOOLEAN DEFAULT FALSE
);
```

== Migrations appliquées

Le schéma a évolué au fil du projet via des migrations SQL incrémentales :

#table(
  columns: (0.4fr, 2fr, 2.5fr),
  table.header([*\#*], [*Migration*], [*Objectif*]),
  [001], [`enrich_ml_event_schema`], [Ajout de `source_event_id`, `event_type`, `duration_source`, `raw_payload`],
  [002], [`backfill_simulated_event_features`], [Remplissage rétroactif des features simulées],
  [003], [`normalize_report_business_categories`], [Normalisation des catégories métier des rapports],
  [004], [`batch_recommendations_schema`], [Ajout de `batch_id`, `rank`, `model_version`, `metadata`, `clicked`],
  [005], [`monitoring_views`], [Création de vues SQL pour le monitoring],
)

#pagebreak()

// ═══════════════════════════════════════════════════════════════════════════
// 8. PRÉPARATION DES DONNÉES ET FEATURE ENGINEERING
// ═══════════════════════════════════════════════════════════════════════════

= Préparation des données et Feature Engineering

== Limite métier importante : la durée de consultation

#attention[
  Metabase ne fournit pas nativement la durée de consultation d'un rapport.
  L'API activity log capture le *moment du clic*, mais pas la fin de session.
  C'est un problème commun dans les outils BI.
]

*Solution temporaire adoptée :*
- La durée est *simulée* côté Publisher (distribution réaliste)
- Chaque enregistrement est tracé avec `duration_source = 'simulated'`
- Le système est conçu pour accepter une durée réelle (client-side) dès qu'elle sera disponible

*Solution future envisagée :*
- Instrumentation JavaScript côté Metabase pour capturer `view_start` et `view_end`
- Calcul de la durée réelle : $"duration" = t_("end") - t_("start")$

== Split train/test temporel

Le découpage des données suit une stratégie *temporelle par utilisateur* :

#rect(
  width: 100%,
  inset: 12pt,
  radius: 6pt,
  fill: info.lighten(93%),
  stroke: 0.8pt + info,
)[
  Pour chaque utilisateur, les événements sont triés par date. Les *80 % les plus
  anciens* servent à l'entraînement, et les *20 % les plus récents* constituent
  le jeu de test.

  ```text
  Utilisateur 42 :
  [--- Train (80%) ---][-- Test (20%) --]
  Jan ─── Fév ─── Mar ─── Avr ─── Mai
  ```
]

*Pourquoi temporel plutôt que aléatoire ?*
- Un split aléatoire provoquerait une *fuite de données* (_data leakage_) :
  le modèle pourrait voir des événements futurs pendant l'entraînement.
- Le split temporel simule le scénario réel : *apprendre du passé pour
  prédire le futur*.

*Paramètres du split :*
- `test_ratio = 0.2` (20 % pour le test)
- `min_events_per_user = 5` (les utilisateurs avec moins de 5 événements
  vont entièrement en train)

*Résultat sur nos données :*
- Train : 7 891 événements (79.6 %)
- Test : 2 020 événements (20.4 %)
- Utilisateurs évalués : 100

== Features d'interaction (user × report)

Pour chaque paire utilisateur-rapport, le module de _feature engineering_
calcule un vecteur de *7 features* :

#table(
  columns: (1.6fr, 1fr, 3fr),
  table.header([*Feature*], [*Type*], [*Description et calcul*]),
  [`view_count`], [Entier], [Nombre total de consultations du rapport par l'utilisateur],
  [`selection_count`], [Entier], [Nombre de sélections (clic actif, poids plus fort qu'une vue passive)],
  [`total_duration`], [Float], [Somme des durées de consultation (secondes)],
  [`avg_duration`], [Float], [Durée moyenne par consultation],
  [`recency_days`], [Float], [Nombre de jours depuis la dernière consultation],
  [`selection_rate`], [Float (0–1)], [Ratio sélections / vues : $"selection\_count" / "view\_count"$],
  [`implicit_rating`], [Float (1–5)], [Note implicite normalisée (voir formule ci-dessous)],
)

=== Formule du score brut (_raw score_)

Le score brut agrège les différentes dimensions du comportement utilisateur :

$
  "raw\_score" = log(1 + "view\_count") + 0.35 times log(1 + "total\_duration") + 0.8 times "selection\_count" + "recency\_boost"
$

Où le *boost de récence* favorise les interactions récentes :

$ "recency\_boost" = e^(- "recency\_days" / 14) $

Ce boost suit une décroissance exponentielle avec une demi-vie de ~10 jours.
Un rapport consulté hier a un boost de ~0.93, tandis qu'un rapport consulté
il y a 30 jours a un boost de ~0.12.

=== Normalisation en implicit rating

Le score brut est normalisé en une note implicite entre 1 et 5 via
normalisation min-max :

$ "implicit\_rating" = 1 + 4 times ("raw\_score" - "raw\_score"_min) / ("raw\_score"_max - "raw\_score"_min) $

Cette normalisation est *essentielle* pour la bibliothèque Surprise, qui
attend des ratings sur une échelle fixe.

== Features utilisateur

En complément, des features au niveau *utilisateur* sont calculées pour
le profiling et le debugging :

- `event_count` : nombre total d'événements
- `unique_reports` : nombre de rapports distincts consultés
- `total_duration`, `avg_duration` : activité globale
- `selection_rate` : taux de sélection global
- `activity_span_days` : durée d'activité (premier → dernier événement)
- `favorite_category` : catégorie métier la plus consultée

== Features rapport

Des features au niveau *rapport* permettent d'identifier la popularité
et l'engagement :

- `event_count`, `unique_users` : popularité brute
- `popularity_score` : $log(1 + "event\_count")$ — atténue l'effet des rapports très populaires
- `selection_rate` : qualité de l'engagement
- `business_category` : catégorie métier normalisée

#pagebreak()

// ═══════════════════════════════════════════════════════════════════════════
// 9. MODÈLES DE RECOMMANDATION
// ═══════════════════════════════════════════════════════════════════════════

= Modèles de recommandation

#figure(
  image("assets/modeles-comparaison.jpg", width: 92%),
  caption: [Vue d'ensemble des trois approches de recommandation implémentées.],
)

Cinq modèles ont été implémentés, entraînés et évalués. Ils se regroupent
en trois familles.

== Famille 1 : Collaborative Filtering (CF)

=== Principe — Analogie « Netflix »

Le _Collaborative Filtering_ repose sur l'idée que *des utilisateurs aux
comportements similaires apprécient les mêmes rapports*. Si l'Utilisateur A
et l'Utilisateur B ont consulté les mêmes rapports dans le passé, alors un
rapport apprécié par B (mais pas encore vu par A) sera probablement pertinent
pour A.

#callout(
  title: "Exemple concret",
  icon: "🎬",
  color: accent,
)[
  *User 42* (Admin Ventes) a consulté : Revenue by Region ⭐⭐⭐⭐⭐, Sales Funnel ⭐⭐⭐⭐ \
  *User 15* (Autre Admin Ventes) a consulté : Revenue by Region ⭐⭐⭐⭐⭐, Sales Funnel ⭐⭐⭐⭐, Customer Churn ⭐⭐⭐⭐ \
  → *Recommandation pour User 42 :* Customer Churn (aimé par User 15, pas encore vu par User 42)
]

=== Modèle 1 : Baseline User-Based CF

Ce modèle construit une *matrice utilisateur-rapport* à partir des
_implicit ratings_, puis calcule la similarité entre utilisateurs par
*cosinus* :

$
  "sim"("u", "v") = (bold(r)_u dot bold(r)_v) / (||bold(r)_u|| times ||bold(r)_v||) = (sum_(i=1)^n r_(u,i) times r_(v,i)) / (sqrt(sum_(i=1)^n r_(u,i)^2) times sqrt(sum_(i=1)^n r_(v,i)^2))
$

Où $bold(r)_u$ est le vecteur de ratings de l'utilisateur $u$ sur les $n$ rapports.

Le score prédit pour un rapport $i$ non vu par l'utilisateur $u$ est :

$ hat(r)_(u,i) = (sum_(v in N(u)) "sim"(u,v) times r_(v,i)) / (sum_(v in N(u)) |"sim"(u,v)|) $

Où $N(u)$ est l'ensemble des utilisateurs similaires à $u$ qui ont vu le rapport $i$.

=== Modèle 2 : Surprise SVD

La décomposition en valeurs singulières (*SVD*) factorise la matrice
utilisateur-rapport en deux matrices latentes de faible dimension :

$ hat(r)_(u,i) = mu + b_u + b_i + bold(p)_u^T dot bold(q)_i $

Où :
- $mu$ : moyenne globale des ratings
- $b_u$ : biais de l'utilisateur $u$
- $b_i$ : biais du rapport $i$
- $bold(p)_u$ : vecteur latent de l'utilisateur (dimension $k$)
- $bold(q)_i$ : vecteur latent du rapport (dimension $k$)

L'entraînement optimise par descente de gradient stochastique avec
régularisation $lambda$ pour éviter le surapprentissage.

=== Modèle 3 : Surprise KNN

Le KNN item-based de Surprise utilise une approche voisinage :
il identifie les $k$ rapports les plus similaires au rapport cible
(par cosinus sur les vecteurs de ratings) et pondère les prédictions.

*Avantage CF :* découverte de rapports inattendus (_serendipity_). \
*Inconvénient CF :* problème de *démarrage à froid* (_cold start_) —
les nouveaux utilisateurs sans historique ne reçoivent pas de bonnes
recommandations.

== Famille 2 : Content-Based Filtering (CB)

=== Principe — Analogie « Spotify Radio »

Le _Content-Based Filtering_ recommande des rapports *similaires par
contenu* à ceux déjà consultés par l'utilisateur. Si l'utilisateur aime
les rapports de la catégorie « Finance », on lui recommande d'autres
rapports « Finance ».

#callout(
  title: "Exemple concret",
  icon: "🎵",
  color: success,
)[
  *User 42* a consulté : Revenue by Region (Finance ⭐⭐⭐⭐⭐), Sales Funnel (Ventes ⭐⭐⭐⭐) \
  → Rapports similaires par contenu : Profit Margin (Finance), Quarterly Sales (Ventes) \
  → *Recommandation :* Profit Margin (même catégorie, termes similaires dans le titre/description)
]

=== Modèle 4 : Content-Based TF-IDF

Le pipeline de ce modèle se décompose en trois étapes :

*Étape 1 — Vectorisation TF-IDF des rapports*

Chaque rapport est représenté par un texte composite :
```text
content_text = titre + description + tags + category + business_category
```

Ce texte est converti en vecteur TF-IDF avec :
- N-grams : (1, 3) — capture les termes simples et les expressions
- Max features : 100 — limite la dimensionnalité
- Stop words : anglais

$ "TF-IDF"(t, d) = "TF"(t, d) times log(N / "DF"(t)) $

Où $"TF"(t,d)$ est la fréquence du terme $t$ dans le document $d$,
$N$ le nombre total de rapports, et $"DF"(t)$ le nombre de rapports
contenant $t$.

*Étape 2 — Construction du profil utilisateur*

Le profil de l'utilisateur $u$ est la *moyenne pondérée* des vecteurs
TF-IDF des rapports qu'il a consultés, pondérée par l'_implicit rating_ :

$ bold(P)_u = (sum_(i in "Vu"(u)) r_(u,i) times bold(v)_i) / (sum_(i in "Vu"(u)) r_(u,i)) $

Où $bold(v)_i$ est le vecteur TF-IDF du rapport $i$ et $r_(u,i)$ le rating
implicite. Le profil est ensuite normalisé : $bold(P)_u := bold(P)_u / ||bold(P)_u||$.

*Étape 3 — Scoring par similarité cosinus*

Le score d'un rapport candidat $j$ pour l'utilisateur $u$ est :

$ "score"(u, j) = cos(bold(P)_u, bold(v)_j) = (bold(P)_u dot bold(v)_j) / (||bold(P)_u|| times ||bold(v)_j||) $

*Avantage CB :* fonctionne bien même avec peu de données (pas de _cold start_ sur les rapports). \
*Inconvénient CB :* faible _serendipity_ — recommande toujours dans la même catégorie.

== Famille 3 : Modèle Hybride (CF + CB)

=== Principe — « Le meilleur des deux mondes »

Le modèle hybride *fusionne les scores* des deux approches pour obtenir
un compromis optimal entre découverte (CF) et pertinence thématique (CB).

=== Formule de fusion

Pour chaque rapport candidat $j$ et utilisateur $u$ :

+ Obtenir le score CF brut : $s_("CF")(u, j)$
+ Obtenir le score CB brut : $s_("CB")(u, j)$
+ Normaliser chaque score par min-max sur l'ensemble des candidats :

$ tilde(s)(x) = (x - x_min) / (x_max - x_min) $

4. Calculer le score final par combinaison pondérée :

$ "score"_("final")(u, j) = alpha times tilde(s)_("CF")(u, j) + (1 - alpha) times tilde(s)_("CB")(u, j) $

Avec $alpha = 0.6$ (poids CF) et $1 - alpha = 0.4$ (poids CB).

=== Exemple numérique

#table(
  columns: (1.8fr, 0.8fr, 0.8fr, 1fr),
  table.header([*Rapport*], [*CF norm*], [*CB norm*], [*Score final*]),
  [Customer Churn], [0.90], [0.30], [$0.6 times 0.9 + 0.4 times 0.3 = bold(0.66)$ ✅],
  [Customer Feedback], [0.20], [0.60], [$0.6 times 0.2 + 0.4 times 0.6 = bold(0.36)$ ❌],
)

Dans cet exemple, Customer Churn est recommandé malgré un score CB faible,
car le signal collaboratif est fort. C'est précisément l'intérêt du modèle
hybride : il *ne rate pas* les recommandations que l'approche contenu seule
ignorerait.

=== Configuration retenue

#keypoint[
  *Modèle retenu :* `hybrid_knn_content` \
  *Composante collaborative :* Surprise KNN \
  *Composante contenu :* TF-IDF \
  *Poids :* $alpha = 0.6$ (CF) / $1 - alpha = 0.4$ (CB)
]

#pagebreak()

// ═══════════════════════════════════════════════════════════════════════════
// 10. ÉVALUATION OFFLINE
// ═══════════════════════════════════════════════════════════════════════════

= Évaluation offline

== Métriques utilisées

Cinq métriques standard de la littérature en systèmes de recommandation
ont été calculées :

#table(
  columns: (1.6fr, 2.5fr, 2fr),
  table.header([*Métrique*], [*Définition*], [*Formule*]),
  [Precision\@K],
  [Parmi les K rapports recommandés, combien sont réellement pertinents ?],
  [$"Precision" = |"Rec" inter "Rel"| / K$],

  [Recall\@K], [Parmi les rapports pertinents, combien a-t-on retrouvé ?], [$"Recall" = |"Rec" inter "Rel"| / |"Rel"|$],

  [HitRate\@K],
  [L'utilisateur a-t-il reçu au moins une recommandation pertinente ?],
  [$"HR" = 1 "si" |"Rec" inter "Rel"| > 0$],

  [NDCG\@K], [Les rapports pertinents sont-ils en haut du classement ?], [$"NDCG" = "DCG" / "IDCG"$],

  [Coverage\@K], [Quelle part du catalogue apparaît dans les recommandations ?], [$|union "Rec"(u)| / |"Catalogue"|$],
)

Où *Rec* = ensemble des rapports recommandés, *Rel* = ensemble des rapports
réellement consultés dans le jeu de test.

La formule DCG (Discounted Cumulative Gain) est :

$ "DCG"\@K = sum_(i=1)^K ("rel"_i) / (log_2(i + 1)) $

== Résultats principaux — Top-5

#table(
  columns: (2.2fr, 0.5fr, 0.8fr, 0.8fr, 0.8fr, 0.8fr, 0.8fr),
  table.header([*Modèle*], [*K*], [*Prec\@K*], [*Rec\@K*], [*Hit\@K*], [*NDCG\@K*], [*Cov\@K*]),
  table.cell(fill: success.lighten(90%))[`hybrid_knn_content`],
  table.cell(fill: success.lighten(90%))[5],
  table.cell(fill: success.lighten(90%))[*0.140*],
  table.cell(fill: success.lighten(90%))[*0.062*],
  table.cell(fill: success.lighten(90%))[0.49],
  table.cell(fill: success.lighten(90%))[*0.132*],
  table.cell(fill: success.lighten(90%))[0.875],
  [`tuned_surprise_svd`], [5], [0.130], [0.056], [*0.50*], [0.121], [0.625],
  [`tuned_surprise_knn`], [5], [0.124], [0.053], [0.47], [0.132], [*0.950*],
  [`baseline_user_based_cf`], [5], [0.124], [0.054], [0.48], [0.120], [0.575],
  [`content_based_tfidf`], [5], [0.122], [0.054], [0.49], [0.119], [0.750],
)

== Résultats — Top-10

#table(
  columns: (2.2fr, 0.5fr, 0.8fr, 0.8fr, 0.8fr, 0.8fr, 0.8fr),
  table.header([*Modèle*], [*K*], [*Prec\@K*], [*Rec\@K*], [*Hit\@K*], [*NDCG\@K*], [*Cov\@K*]),
  [`tuned_surprise_knn`], [10], [0.117], [0.102], [0.69], [0.128], [*0.950*],
  table.cell(fill: success.lighten(90%))[`hybrid_knn_content`],
  table.cell(fill: success.lighten(90%))[10],
  table.cell(fill: success.lighten(90%))[0.116],
  table.cell(fill: success.lighten(90%))[0.101],
  table.cell(fill: success.lighten(90%))[*0.70*],
  table.cell(fill: success.lighten(90%))[0.121],
  table.cell(fill: success.lighten(90%))[0.950],
  [`content_based_tfidf`], [10], [0.114], [0.099], [0.71], [0.116], [0.925],
  [`tuned_surprise_svd`], [10], [0.106], [0.092], [0.69], [0.109], [0.925],
  [`baseline_user_based_cf`], [10], [0.106], [0.092], [0.69], [0.110], [0.925],
)

== Interprétation et choix du modèle

#rect(
  width: 100%,
  inset: 12pt,
  radius: 6pt,
  fill: success.lighten(93%),
  stroke: 0.8pt + success,
)[
  #text(weight: "bold", fill: success)[✅ Pourquoi `hybrid_knn_content` ?]

  #v(2mm)

  + *Meilleure Precision\@5 (0.140)* — ce qui compte car l'API retourne le Top-5.
  + *Fort NDCG\@5 (0.132)* — les rapports pertinents sont bien classés en haut.
  + *Bonne couverture (87.5 %)* à K=5 — évite la sur-recommandation d'une poignée de rapports populaires.
  + *Meilleur HitRate\@10 (0.70)* — 70 % des utilisateurs reçoivent au moins une bonne recommandation.
  + *Plus robuste* que le CF pur car les métadonnées des rapports aident quand l'historique utilisateur est limité.
]

*Observation complémentaire :* le KNN pur a la meilleure couverture (95 %)
mais une Precision\@5 inférieure. Le SVD a un bon HitRate\@5 (0.50) mais
la couverture la plus faible (62.5 %), signe d'une concentration excessive
sur les rapports populaires.

#pagebreak()

// ═══════════════════════════════════════════════════════════════════════════
// 11. SERVING ET API REST
// ═══════════════════════════════════════════════════════════════════════════

= Serving et API REST

== Endpoints disponibles

L'API REST est construite avec *FastAPI* et expose les endpoints suivants :

#table(
  columns: (0.7fr, 2.5fr, 2.5fr),
  table.header([*Méthode*], [*Endpoint*], [*Description*]),
  [`GET`], [`/health`], [Vérification de santé du service et du modèle],
  [`POST`], [`/train`], [Déclencher l'entraînement du modèle hybride],
  [`GET`], [`/recommendations/{user_id}?n=5`], [Recommandations temps réel (calcul à la volée)],
  [`POST`],
  [`/batch/recommendations/generate?n=5`],
  [Générer et stocker les recommandations pour tous les utilisateurs],

  [`GET`], [`/stored-recommendations/{user_id}?n=5`], [Lire les recommandations pré-calculées (batch)],
  [`GET`], [`/batch/status`], [Statut du dernier batch de recommandations],
  [`GET`], [`/monitoring/summary`], [Résumé compact des métriques de monitoring],
)

== Exemple de requête et réponse

*Requête :*
```text
GET /stored-recommendations/42?n=3
```

*Réponse :*
```json
{
  "user_id": 42,
  "batch_id": "batch_20260530_020000_a1b2c3d4",
  "count": 3,
  "recommendations": [
    {
      "rank": 1,
      "report_id": 7,
      "title": "Customer Churn Analysis",
      "business_category": "analytics",
      "score": 0.847,
      "algorithm": "hybrid_knn_content"
    },
    {
      "rank": 2,
      "report_id": 12,
      "title": "Revenue by Region",
      "business_category": "finance",
      "score": 0.723,
      "algorithm": "hybrid_knn_content"
    },
    {
      "rank": 3,
      "report_id": 25,
      "title": "Sales Pipeline Status",
      "business_category": "sales",
      "score": 0.681,
      "algorithm": "hybrid_knn_content"
    }
  ]
}
```

== Batch serving

Le _batch serving_ est le mode principal de production des recommandations.
Son fonctionnement :

+ L'endpoint `POST /batch/recommendations/generate` déclenche l'entraînement
  puis génère les Top-N pour *chaque utilisateur* en base.
+ Chaque batch est identifié par un `batch_id` unique (ex : `batch_20260530_020000_a1b2c3d4`).
+ La `model_version` est sauvegardée sous forme JSON, contenant l'algorithme,
  le modèle CF et les poids.
+ L'endpoint `GET /stored-recommendations/{user_id}` lit directement ces
  résultats — aucun calcul ML au moment de la requête.

*Avantages du batch serving :*
- *Rapidité* : réponses API < 50 ms (simple lecture SQL)
- *Auditabilité* : chaque recommandation est traçable (batch_id, model_version)
- *Stabilité* : la démo ne dépend pas d'un calcul ML en temps réel
- *Reproductibilité* : on peut comparer les résultats entre batches

== Scheduler intégré

Un scheduler optionnel (basé sur `asyncio`) peut être activé par variable
d'environnement pour déclencher automatiquement un batch quotidien :

```text
BATCH_SCHEDULER_ENABLED=true
BATCH_SCHEDULER_INTERVAL_SECONDS=86400
BATCH_SCHEDULER_TOP_N=5
```

#pagebreak()

// ═══════════════════════════════════════════════════════════════════════════
// 12. VALIDATION TECHNIQUE
// ═══════════════════════════════════════════════════════════════════════════

= Validation technique

== Stratégie de test multi-niveaux

La validation du système suit une pyramide de tests classique, adaptée
aux spécificités d'un pipeline ML :

#table(
  columns: (1.4fr, 2.2fr, 2.2fr, 0.8fr),
  table.header([*Niveau*], [*Ce qu'on teste*], [*Fichier*], [*Statut*]),
  [Unitaire ML],
  [Entraînement/prédiction de chaque modèle, format des sorties, gestion des cas vides],
  [`test_ml_models.py`],
  [✅ PASS],

  [Unitaire Data],
  [Chargement des données, calcul des features, split train/test],
  [`test_data_preparation.py`],
  [✅ PASS],

  [Intégration],
  [Connexion DB + API + batch : vérification que les composants fonctionnent ensemble],
  [`integration_check.py`],
  [✅ PASS],

  [End-to-End],
  [RabbitMQ → Consumer → PostgreSQL → Train → API : chaîne complète],
  [`e2e_rabbitmq_to_recommendations.py`],
  [✅ PASS],

  [Stress], [Lecture concurrente des recommandations stockées (volume, latence)], [`stress_check.py`], [✅ PASS],
)

== Détail des tests unitaires ML

Les tests unitaires couvrent les scénarios suivants :

- *Collaborative Filtering* : vérification que le modèle produit des
  recommandations avec les bonnes colonnes (`user_id`, `report_id`, `score`,
  `rank`, `algorithm`), que les scores sont positifs, que les rapports déjà
  vus sont exclus.
- *Content-Based* : vérification de la vectorisation TF-IDF, des profils
  utilisateur, de la similarité cosinus, et du fallback vers la popularité
  pour les utilisateurs inconnus.
- *Hybride* : vérification de la fusion des scores, de la normalisation
  min-max, et de la pondération CF/CB.
- *Surprise SVD/KNN* : vérification de l'interface commune avec les
  autres modèles.

== Test End-to-End : preuve de robustesse

Le test E2E simule un flux complet :
+ Publication d'un événement synthétique dans RabbitMQ
+ Attente que le Consumer traite le message
+ Vérification de l'insertion dans PostgreSQL
+ Déclenchement de l'entraînement via l'API
+ Récupération des recommandations pour l'utilisateur cible

Ce test a permis de *détecter et corriger le bug de connexion stale*
mentionné en section 6.3.

#keypoint[
  *Suite Phase 6 :* ✅ PASS — Tous les tests passent avec succès.
]

#pagebreak()

// ═══════════════════════════════════════════════════════════════════════════
// 13. ÉTAT ACTUEL DU SYSTÈME
// ═══════════════════════════════════════════════════════════════════════════

= État actuel du système

#table(
  columns: (2.7fr, 1fr),
  table.header([*Indicateur*], [*Valeur*]),
  [Utilisateurs], [100],
  [Rapports], [40],
  [Logs de navigation], [9 965],
  [Logs avec durée], [9 965],
  [Recommandations stockées], [4 500],
  [Batches de recommandations], [9],
  [Modèle en production], [`hybrid_knn_content`],
  [Poids CF / CB], [0.60 / 0.40],
)

#callout(
  title: "Données et réalisme",
  icon: "📝",
  color: info,
)[
  Les données sont *simulées de manière réaliste* via le script
  `generate_data.py`. La simulation reproduit des patterns plausibles :
  préférences catégorielles par rôle, fréquence variable selon les
  utilisateurs, durées suivant une distribution log-normale. Le système
  est conçu pour fonctionner de manière identique avec des données réelles.
]

#pagebreak()

// ═══════════════════════════════════════════════════════════════════════════
// 14. PROPOSITION D'A/B TEST
// ═══════════════════════════════════════════════════════════════════════════

= Proposition d'A/B test

L'évaluation offline (Precision\@K, NDCG\@K) mesure la pertinence *estimée*
des recommandations, mais seul un A/B test en conditions réelles peut valider
l'*impact métier*.

== Design expérimental proposé

#table(
  columns: (1fr, 2.5fr, 2.5fr),
  table.header([*Aspect*], [*Groupe A (Contrôle)*], [*Groupe B (Test)*]),
  [Expérience], [Metabase standard ou baseline popularité], [Recommandations hybrides personnalisées],
  [Utilisateurs], [80 % des utilisateurs], [20 % initialement],
  [Durée], [1 semaine minimum], [Extension à 2–4 semaines si résultats positifs],
)

== Métriques online à mesurer

#table(
  columns: (2fr, 3fr),
  table.header([*Métrique*], [*Ce qu'elle capture*]),
  [Click-Through Rate (CTR)], [% d'utilisateurs qui cliquent sur une recommandation],
  [Repeat usage \@7j], [Réutilisation d'un rapport recommandé dans les 7 jours],
  [Dwell time moyen], [Temps passé sur un rapport recommandé vs non recommandé],
  [Diversité rapports], [Nombre de rapports distincts consultés par utilisateur],
  [Feedback qualitatif], [« Utile / Pas utile » si un bouton de feedback est disponible],
)

== Plan de déploiement progressif

+ *Semaine 1 :* démarrer avec 20 % des utilisateurs dans le Groupe B.
+ *Semaine 2 :* si CTR et repeat usage s'améliorent, passer à 50 %.
+ *Semaine 3–4 :* déployer à 100 % si les résultats sont confirmés.
+ *Critère d'arrêt :* _rollback_ immédiat si les recommandations concentrent
  trop sur les mêmes rapports (couverture < 50 %).

#pagebreak()

// ═══════════════════════════════════════════════════════════════════════════
// 15. SCÉNARIO DE DÉMONSTRATION
// ═══════════════════════════════════════════════════════════════════════════

= Scénario de démonstration en soutenance (Click-by-Click)

L'objectif de la démonstration est de prouver en temps réel le fonctionnement de la chaîne complète de bout en bout. Voici le déroulement exact présenté lors de la soutenance :

== 1. Infrastructure et Interface BI (Metabase)

Nous commençons par valider que les 6 services Docker (PostgreSQL, RabbitMQ, Publisher, Consumer, FastAPI, Metabase) sont actifs. 

L'utilisateur final interagit avec Metabase, notre interface BI. C'est ici que l'on observe la problématique initiale : une multitude de rapports disponibles, nécessitant un guidage personnalisé.

#figure(
  image("assets/demo-metabase.jpg", width: 85%),
  caption: [Maquette de l'interface utilisateur type (Metabase) avec panneau de recommandations],
)

== 2. Collecte Asynchrone (RabbitMQ)

Chaque clic ou vue dans l'interface génère un événement. Pour garantir la résilience, ces événements transitent par notre Message Broker (RabbitMQ) avant d'être consommés et stockés dans PostgreSQL, assurant le découplage parfait du système.

#figure(
  image("assets/demo-rabbitmq.jpg", width: 85%),
  caption: [Console d'administration RabbitMQ montrant l'activité des files asynchrones],
)

== 3. Moteur ML et API REST (FastAPI)

Une fois les données collectées et préparées, le modèle hybride est sollicité via notre API FastAPI. Nous démontrons l'entraînement du modèle (`POST /train`) et la récupération instantanée des recommandations via le Batch Serving et le Monitoring.

#figure(
  image("assets/demo-swagger.jpg", width: 85%),
  caption: [Interface Swagger (FastAPI) exposant les endpoints ML et de monitoring],
)

== 4. Tests et Preuve de Résilience

Pour conclure la démonstration, nous exécutons le script de validation globale (`tests/run_phase6_tests.py`) qui atteste du bon fonctionnement unitaire, d'intégration et bout-en-bout (E2E) du pipeline. Nous démontrons également la résilience du système face à une perte de connexion de la base de données.

#pagebreak()

// ═══════════════════════════════════════════════════════════════════════════
// 16. DISCUSSION CRITIQUE
// ═══════════════════════════════════════════════════════════════════════════

= Discussion critique

== Forces du système

#table(
  columns: (2fr, 3.5fr),
  table.header([*Force*], [*Détail*]),
  [Architecture complète et cohérente],
  [Pipeline asynchrone RabbitMQ → Consumer → PostgreSQL → ML → API, chaque composant a une responsabilité unique],

  [Séparation claire des couches],
  [Data pipeline, feature engineering, modèles ML, batch serving et API sont des modules indépendants],

  [Robustesse prouvée], [Bug réel de connexion stale détecté et corrigé en E2E — preuve de maturité du système],

  [Évaluation rigoureuse],
  [5 métriques standard, 5 modèles comparés, split temporel réaliste, résultats reproductibles],

  [Batch serving], [Recommandations pré-calculées avec traçabilité (batch\_id, model\_version), API < 50 ms],

  [Monitoring intégré], [Endpoint `/monitoring/summary` avec volumes, top rapports vus et recommandés],

  [Reproductibilité], [Docker Compose pour déploiement local, scripts de démo, tests automatisés],
)

== Limites et niveaux de criticité

#table(
  columns: (2fr, 1fr, 3fr),
  table.header([*Limite*], [*Criticité*], [*Mitigation*]),
  [Durée de consultation simulée],
  [Moyenne],
  [Tracée par `duration_source`, le système acceptera les durées réelles via instrumentation JavaScript],

  [Volume de données limité],
  [Faible],
  [100 users × 40 reports suffisent pour valider l'architecture ; scalabilité non bloquante],

  [Absence d'authentification API],
  [Haute (prod)],
  [Non critique pour la démo locale ; en production, ajout de JWT ou OAuth2],

  [Pas de feedback explicite],
  [Moyenne],
  [Seul l'implicit feedback (views/selections) est utilisé ; un bouton « utile/inutile » améliorerait la qualité],

  [Métriques offline limitées],
  [Faible],
  [Les métriques offline ne remplacent pas l'A/B test réel, mais suffisent pour le cadre académique],
)

#pagebreak()

// ═══════════════════════════════════════════════════════════════════════════
// 17. PERSPECTIVES
// ═══════════════════════════════════════════════════════════════════════════

= Perspectives

== Court terme (après soutenance)

+ *Instrumentation front-end* : JavaScript côté Metabase pour capturer
  la durée réelle de consultation et les sessions complètes.
+ *Feedback online* : clic sur une recommandation → signal d'apprentissage
  positif ; ignoré → signal négatif.
+ *Amélioration des métadonnées* : enrichir les descriptions et catégories
  métier des rapports pour améliorer le content-based.

== Moyen terme

+ *A/B test réel* par cohortes utilisateurs (cf. section 14).
+ *Learning-to-Rank* : remplacer la fusion linéaire par un modèle
  d'ordonnancement appris (LightGBM, XGBoost).
+ *Features de fraîcheur* : promouvoir les rapports récemment créés ou
  mis à jour.
+ *CI/CD* : pipeline GitHub Actions automatisant tests + déploiement.

== Long terme

+ *Bandit contextuel* : exploration/exploitation dynamique pour optimiser
  les recommandations en temps réel.
+ *Drift monitoring* : détection de changements dans les préférences
  utilisateur, la popularité des rapports, et les catégories.
+ *Multi-tenant* : adaptation pour plusieurs instances Metabase en
  parallèle.

#pagebreak()

// ═══════════════════════════════════════════════════════════════════════════
// 18. CONCLUSION
// ═══════════════════════════════════════════════════════════════════════════

= Conclusion

Ce projet atteint son objectif principal : *livrer un moteur de recommandation
BI adaptatif, intégré, testé et démontrable localement*.

La contribution majeure est d'avoir transformé une idée de recommandation BI
en *système opérationnel complet* comprenant :

#rect(
  width: 100%,
  inset: 14pt,
  radius: 8pt,
  fill: primary.lighten(95%),
  stroke: 0.7pt + primary.lighten(60%),
)[
  #grid(
    columns: (1fr, 1fr),
    gutter: 8pt,
    [
      ✅ Pipeline de données résilient (RabbitMQ → PostgreSQL) \
      ✅ Feature engineering complet (7 features par paire user-report) \
      ✅ 5 modèles comparés objectivement sur 5 métriques \
      ✅ Modèle hybride sélectionné et justifié
    ],
    [
      ✅ API FastAPI avec 7 endpoints documentés \
      ✅ Batch serving avec traçabilité complète \
      ✅ Monitoring intégré \
      ✅ Suite de tests multi-niveaux (unitaire → stress)
    ],
  )
]

#v(3mm)

Le système démontre qu'il est possible d'ajouter une *couche d'intelligence*
à un outil BI existant, sans modifier Metabase lui-même, en exploitant
uniquement ses API et ses données. L'architecture découplée garantit que
chaque composant peut évoluer indépendamment.

Les limites identifiées (durée simulée, volume limité, absence d'A/B test)
sont documentées et accompagnées de mitigations concrètes, démontrant une
*maturité technique* au-delà du simple prototype.

#pagebreak()

// ═══════════════════════════════════════════════════════════════════════════
// 19. ALIGNEMENT AVEC LA GRILLE D'ÉVALUATION
// ═══════════════════════════════════════════════════════════════════════════

= Alignement avec la grille d'évaluation

Cette section relie explicitement les livrables aux critères de notation.

#table(
  columns: (2fr, 0.9fr, 3fr),
  table.header([*Critère*], [*Poids*], [*Preuves concrètes*]),
  [Réalisation technique],
  [40 %],
  [
    Architecture complète en couches, pipeline asynchrone RabbitMQ,
    5 migrations SQL, API FastAPI 7 endpoints, batch serving, scheduler,
    tests multi-niveaux (unitaire, intégration, E2E, stress).
  ],

  [Qualité BI / visualisation],
  [30 %],
  [
    Intégration Metabase, endpoint monitoring avec top rapports,
    vues SQL monitoring, recommandations Top-5 servies et exploitables
    en dashboard, documentation Swagger auto-générée.
  ],

  [Originalité / complexité],
  [20 %],
  [
    Modèle hybride comparé à 4 alternatives (CF baseline, SVD, KNN, CB),
    sélection par métriques objectives (Precision\@K, NDCG\@K, Coverage),
    correction d'un bug de résilience consumer en conditions réelles,
    feature engineering avec formule de scoring composite.
  ],

  [Documentation],
  [10 %],
  [
    Rapport académique complet, scénario de démo, FAQ soutenance,
    scripts de collecte de preuves, tutoriel d'exploitation,
    model optimization report.
  ],
)

#pagebreak()

// ═══════════════════════════════════════════════════════════════════════════
// 20. RÔLES PERSONNE A / PERSONNE B
// ═══════════════════════════════════════════════════════════════════════════

= Rôles Personne A / Personne B

Cette section clarifie la répartition des responsabilités au sein du binôme.

#table(
  columns: (1.2fr, 2.4fr, 0.8fr),
  table.header([*Rôle*], [*Responsabilités couvertes*], [*Statut*]),
  [Personne A \
    (Data & IA)],
  [
    Data preparation, feature engineering (7 features), modèles CF/CB/Hybrid,
    évaluation offline (5 métriques × 5 modèles), API de recommandation,
    batch serving, monitoring API, documentation ML.
  ],
  [✅ MVP],

  [Personne B \
    (Backend & Intégration)],
  [
    Docker stack (6 services), publisher/consumer RabbitMQ, pipeline DB,
    migrations SQL, résilience (reconnexion, rollback), tests E2E/intégration,
    démo locale opérationnelle.
  ],
  [✅ MVP],
)

#v(4mm)

*Fonctionnalités avancées non finalisées (hors MVP) :*
- Bandits contextuels (proposition documentée uniquement)
- A/B test réel en production (proposition documentée uniquement)
- Pipeline CI/CD GitHub Actions complet

#pagebreak()

// ═══════════════════════════════════════════════════════════════════════════
// 21. PLAN DE DÉMONSTRATION ORALE (20 MIN)
// ═══════════════════════════════════════════════════════════════════════════

= Plan de démonstration orale (20 min)

Plan recommandé pour la soutenance :

#table(
  columns: (0.8fr, 1.2fr, 3.5fr),
  table.header([*Durée*], [*Section*], [*Contenu*]),
  [2 min], [Introduction], [Problème métier + objectif. Analogie AVANT/APRÈS.],
  [3 min], [Architecture], [Architecture en couches, data flow, les 3 phases.],
  [6 min], [Démo live], [`docker-compose ps`, `demo_local.py`, appels API, monitoring.],
  [4 min], [Preuves], [DB counts, tests PASS, batch status, monitoring/summary.],
  [3 min], [ML & Évaluation], [Modèles comparés, Precision\@5, choix hybride.],
  [2 min], [Conclusion], [Limites, perspectives, questions.],
)

Scripts de référence :
- `docs/final_report/SCENARIO_DEMO_PROF.md`
- `docs/final_report/ORAL_SCRIPT_7MIN.md`

#pagebreak()

// ═══════════════════════════════════════════════════════════════════════════
// ANNEXES
// ═══════════════════════════════════════════════════════════════════════════

= Annexes

== Documents complémentaires

- `docs/final_report/QUESTIONS_PROF_REPONSES.md` — FAQ soutenance
- `docs/LOCAL_DEMO_GUIDE.md` — Guide de démo locale
- `docs/PHASE6_TEST_REPORT.md` — Rapport de tests Phase 6
- `backend/ml_engine/evaluation_results/model_optimization_report.md` — Rapport d'optimisation
- `docs/final_report/TUTORIAL_TESTER_UTILISER_SOLUTION.md` — Tutoriel d'utilisation

== Glossaire

#table(
  columns: (1.5fr, 3.5fr),
  table.header([*Terme*], [*Définition*]),
  [CF], [Collaborative Filtering — filtrage collaboratif basé sur les comportements similaires entre utilisateurs],
  [CB], [Content-Based Filtering — filtrage par le contenu (métadonnées) des rapports],
  [TF-IDF], [Term Frequency – Inverse Document Frequency — mesure de l'importance d'un terme dans un document],
  [SVD], [Singular Value Decomposition — factorisation matricielle en composantes latentes],
  [KNN], [K-Nearest Neighbors — algorithme de voisinage pour la recommandation],
  [NDCG], [Normalized Discounted Cumulative Gain — mesure de qualité du classement],
  [Precision\@K], [Proportion de recommandations pertinentes dans le Top-K],
  [Cold Start], [Problème de démarrage à froid : difficulté à recommander pour les nouveaux utilisateurs/rapports],
  [Batch Serving], [Pré-calcul des recommandations en lot, stockées pour un accès rapide],
  [Implicit Rating], [Note déduite du comportement (vues, durée, sélections) plutôt qu'une évaluation explicite],
)

== Captures live à insérer le jour J

1) Page Metabase avec un dashboard ouvert. \
2) RabbitMQ Management montrant les queues. \
3) FastAPI docs (`http://localhost:8000/docs`) avec endpoints. \
4) Sortie `monitoring/summary` après exécution `demo_local.py`.

Nommage recommandé :
- `assets/live-metabase-dashboard.png`
- `assets/live-rabbitmq-queues.png`
- `assets/live-fastapi-docs.png`
- `assets/live-monitoring-summary.png`
