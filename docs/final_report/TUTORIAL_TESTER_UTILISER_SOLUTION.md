# Tutoriel Complet
## Tester le projet et utiliser la solution (mode soutenance)

Ce guide est ecrit pour te permettre de:
1. lancer le projet proprement,
2. valider le pipeline de bout en bout,
3. demonstrer la solution devant le prof avec des preuves.

---

## 0) Ce que tu dois comprendre avant de lancer

Le systeme a deux niveaux de donnees:

1. **Donnees source Metabase**:
- `report_card`
- `core_user`
- `recent_views`

2. **Donnees cibles du moteur de reco**:
- `reports`
- `users`
- `navigation_logs`
- `recommendations`

Le chemin est:

`Metabase source tables -> Publisher -> RabbitMQ -> Consumer -> Local BI tables -> ML/API`

---

## 1) Preconditions

Assure-toi que:
- Docker Desktop est demarre
- Python est disponible en local
- Tu es dans le dossier racine du projet

Commande:

```powershell
cd "C:\Users\LOQ\Documents\ISIBD S8\BI\ProjetBI_15_HAJJI_BOUBKER"
docker-compose ps
```

---

## 2) Initialiser les donnees source (script de ton ami)

Ton ami a raison: lance d'abord:

```powershell
.\setup_data.ps1
```

Ce script fait:
1. creer 40 rapports dans `report_card`,
2. generer 100 users et ~6000+ events dans `recent_views`.

---

## 3) Apres setup_data.ps1: quoi faire exactement

### 3.1 Lancer tous les services

```powershell
docker-compose up -d
Start-Sleep -Seconds 10
docker-compose ps
```

### 3.2 Verifier publisher/consumer

```powershell
docker-compose logs --tail=80 publisher
docker-compose logs --tail=80 consumer
```

Tu dois voir des lignes du style:
- `publisher ... [recent_views] ... events`
- `consumer ... [navigation_logs] processed`

### 3.3 Verifier les donnees cibles en DB

```powershell
docker exec bi_postgres psql -U admin -d bi_recommendation -c "SELECT COUNT(*) FROM users; SELECT COUNT(*) FROM reports; SELECT COUNT(*) FROM navigation_logs;"
```

Valeurs attendues (ordre de grandeur):
- `users` ~100
- `reports` ~40
- `navigation_logs` grandit (ex: ~9000+)

---

## 4) Tester l'API de recommandation

### 4.1 Health check

```powershell
Invoke-RestMethod "http://localhost:8000/health" | ConvertTo-Json -Depth 10
```

### 4.2 Entrainement

```powershell
Invoke-RestMethod -Method Post "http://localhost:8000/train" | ConvertTo-Json -Depth 10
```

### 4.3 Recommandation online

```powershell
Invoke-RestMethod "http://localhost:8000/recommendations/1?n=5" | ConvertTo-Json -Depth 10
```

---

## 5) Tester le batch serving (important pour demo)

### 5.1 Generer les recommandations batch

```powershell
Invoke-RestMethod -Method Post "http://localhost:8000/batch/recommendations/generate?n=5" | ConvertTo-Json -Depth 10
```

### 5.2 Lire recommandations stockees

```powershell
Invoke-RestMethod "http://localhost:8000/stored-recommendations/1?n=5" | ConvertTo-Json -Depth 10
```

### 5.3 Verifier le monitoring

```powershell
Invoke-RestMethod "http://localhost:8000/monitoring/summary" | ConvertTo-Json -Depth 10
```

---

## 6) Test E2E + stress (preuve qualite)

Depuis le backend container:

```powershell
docker exec bi_backend python tests/run_phase6_tests.py
```

Tu dois finir avec:
- `PASS` unit tests
- `PASS` integration
- `PASS` E2E
- `PASS` stress

---

## 7) Script demo officiel (celui a montrer au prof)

```powershell
docker exec bi_backend python demo_local.py --events 50 --top-n 5
```

Ce script montre en une commande:
1. publication events,
2. persistance consumer,
3. generation batch,
4. restitution recommandations.

---

## 8) Demo live: ordre de passage devant le prof

1. `docker-compose ps`
2. `demo_local.py --events 50 --top-n 5`
3. `GET /stored-recommendations/1?n=5`
4. `GET /monitoring/summary`
5. "Bug reel trouve puis corrige": reconnexion PostgreSQL du consumer

---

## 9) Reponses a la confusion "setup_data puis apres ?"

Apres `setup_data.ps1`, tu fais toujours:

1. `docker-compose up -d`
2. `docker-compose logs --tail=80 publisher`
3. `docker-compose logs --tail=80 consumer`
4. verifier `users/reports/navigation_logs`
5. tester `train` + `recommendations`

Si tu fais seulement `setup_data.ps1` et tu t'arretes la, le pipeline n'est pas
encore demontre.

---

## 10) Erreurs frequentes et fix rapide

### Erreur A: `Channel is closed` dans publisher
- Action: redemarrer le publisher
```powershell
docker-compose restart publisher
```

### Erreur B: `server closed the connection unexpectedly` dans consumer
- Action: redemarrer consumer (fix deja integre)
```powershell
docker-compose restart consumer
```

### Erreur C: Pas de croissance `navigation_logs`
- Verifier logs publisher/consumer
- Verifier queue RabbitMQ
```powershell
docker exec bi_rabbitmq rabbitmqctl list_queues name messages messages_ready messages_unacknowledged consumers
```

---

## 11) Livrables rapport a utiliser

- `docs/final_report/RAPPORT_ACADEMIQUE_FINAL.typ`
- `docs/final_report/SCENARIO_DEMO_PROF.md`
- `docs/final_report/QUESTIONS_PROF_REPONSES.md`
- `docs/final_report/ORAL_SCRIPT_7MIN.md`
- `docs/final_report/evidence/*`

---

## 12) Checklist finale (la veille)

Avant de dormir:

1. `docker exec bi_backend python tests/run_phase6_tests.py` -> PASS
2. `docker exec bi_backend python demo_local.py --events 50 --top-n 5` -> PASS
3. `powershell -ExecutionPolicy Bypass -File docs/final_report/collect_evidence.ps1`
4. verifier que les JSON de preuve existent dans `docs/final_report/evidence`

Si ces 4 points sont OK, la demo est prete.
