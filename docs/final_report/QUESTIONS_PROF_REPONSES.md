# Questions Probables Du Prof Et Reponses

## 1) Pourquoi RabbitMQ et pas insertion directe en base?

RabbitMQ decouple Metabase et la base. Si PostgreSQL ralentit ou redemarre,
les messages restent en queue. Cela ameliore la resilience et evite la perte de
donnees pendant les pics.

## 2) Pourquoi un modele hybride?

Le collaboratif capte les comportements communs entre utilisateurs.
Le content-based exploite les metadonnees des rapports.
Le modele hybride combine les deux et donne le meilleur compromis top-5.

## 3) Pourquoi split temporel au lieu de random split?

Le split temporel simule le cas reel: apprendre sur le passe et predire le
futur. Un split aleatoire risquerait la fuite d'information.

## 4) Que faire si Metabase ne donne pas la vraie duree?

Actuellement on utilise une duree simulee tracee par `duration_source`.
La suite logique est d'ajouter instrumentation client-side pour capter
`view_start`/`view_end`.

## 5) Comment validez-vous le systeme?

Par quatre niveaux:
- unit tests des composants ML,
- integration DB/API,
- E2E RabbitMQ -> Consumer -> DB -> API,
- stress test lecture recommandations.

## 6) Quel bug important avez-vous trouve?

Le consumer pouvait garder une connexion PostgreSQL stale.
Un message restait `unacked`. Correction: detection connexion fermee,
reconnexion auto, rollback protege, requeue des messages.

## 7) Pourquoi stocker les recommandations en batch?

Pour servir rapidement, garder une trace audit (`batch_id`, `model_version`) et
stabiliser la demo.

## 8) Quelles metriques avez-vous utilisees?

Precision@K, Recall@K, HitRate@K, NDCG@K, Catalog Coverage@K.
Pour la soutenance, Precision@5 et NDCG@5 sont prioritaires car l'API cible un
top-5.

## 9) Quelles limites restent?

- duree simulee,
- volume de donnees encore limite,
- securite API a renforcer pour production.

## 10) Quelles evolutions prioritaires?

1. Instrumentation events client.
2. A/B test reel sur cohortes.
3. Feedback loop a partir des clics recommandations.
4. CI/CD complet des tests.
