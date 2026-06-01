# Scenario Demo Prof (30 minutes)

## Objectif

Montrer que le systeme fonctionne de bout en bout avec preuves techniques et
resultats mesurables.

---

## Plan temps

### 0-3 min: Cadrage

Message a dire:
"Le probleme est la surcharge de rapports dans Metabase. Notre systeme apprend
les habitudes utilisateurs pour recommander les rapports pertinents."

Support visuel:
- `assets/brief-projet.png`
- `assets/architecture-layers.png`

### 3-7 min: Architecture

Montrer le flux:
`Metabase -> RabbitMQ -> Consumer -> PostgreSQL -> ML -> API -> Recommandations`

Support visuel:
- `assets/full-flow.png`

### 7-12 min: Validation infrastructure

Commandes:
```powershell
docker-compose ps
```

Point a expliquer:
- Tous les services sont actifs.
- Le backend expose l'API sur `:8000`.

### 12-18 min: Demonstration pipeline live

Commande:
```powershell
docker exec bi_backend python demo_local.py --events 50 --top-n 5
```

Ce que cela prouve:
- publication d'evenements synthetiques,
- persistance consumer -> PostgreSQL,
- generation batch recommandations,
- lecture des recommandations d'un utilisateur.

### 18-22 min: Monitoring visuel

Commande:
```powershell
Invoke-RestMethod http://localhost:8000/monitoring/summary | ConvertTo-Json -Depth 10
```

A commenter:
- nombre users/reports/logs,
- evolution des recommendations et batches,
- top rapports consultes et recommandes.

### 22-26 min: Qualite ML et tests

Montrer:
- tableau metriques (Precision@5 etc.) dans le rapport final.

Commande de preuve:
```powershell
docker exec bi_backend python tests/run_phase6_tests.py
```

Message a dire:
"Le modele hybride est retenu pour le top-5, et la chaine complete est validee
par unit tests, integration, E2E et stress."

### 26-30 min: Conclusion + ouverture

Conclusion:
- objectif du module atteint,
- systeme operationnel localement.

Ouverture:
- duree reelle client-side,
- A/B testing reel,
- securisation production.

---

## Plan B (si bug live)

1. Afficher les resultats de la derniere execution `demo_local.py`.
2. Afficher `monitoring/summary`.
3. Afficher rapport de tests Phase 6 (PASS).
4. Expliquer le bug deja traite (reconnexion consumer PostgreSQL).

Ce plan B garde la credibilite technique sans perdre la narration.
