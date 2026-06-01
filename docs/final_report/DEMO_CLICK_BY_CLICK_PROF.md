# Demo Click-by-Click Prof
## Script operationnel (20 minutes)

Ce document est ton teleprompteur de demo.
Tu suis les etapes dans l'ordre, sans improviser.

---

## A. Preparation 15 min avant la soutenance

1. Ouvrir PowerShell dans le dossier projet:
```powershell
cd "C:\Users\LOQ\Documents\ISIBD S8\BI\ProjetBI_15_HAJJI_BOUBKER"
```

2. Lancer les services:
```powershell
docker-compose up -d
Start-Sleep -Seconds 10
docker-compose ps
```

3. Valider que le pipeline est vivant:
```powershell
docker-compose logs --tail=50 publisher
docker-compose logs --tail=50 consumer
```

4. Garder 4 onglets navigateur prets:
- `http://localhost:3000` (Metabase)
- `http://localhost:15672` (RabbitMQ Management)
- `http://localhost:8000/docs` (Swagger FastAPI)
- `http://localhost:8000/monitoring/summary` (monitoring API)

---

## B. Demo live minute par minute

## Minute 0-2 : Contexte et objectif

### Ce que tu affiches
1. Ouvrir le rapport final:
- `docs/final_report/RAPPORT_ACADEMIQUE_FINAL.typ`
2. Montrer les images:
- `assets/brief-projet.png`
- `assets/architecture-layers.png`

### Ce que tu dis
"Le probleme est la surcharge de rapports dans Metabase.  
Notre objectif est de recommander automatiquement les rapports pertinents a
chaque utilisateur."

---

## Minute 2-4 : Services actifs

### Ce que tu fais
1. Revenir sur PowerShell.
2. Lancer:
```powershell
docker-compose ps
```

### Ce que tu dis
"Ici on prouve que toute l'infrastructure est active: PostgreSQL, RabbitMQ,
Metabase, publisher, consumer, backend API."

---

## Minute 4-7 : Metabase (interface BI)

### Ce que tu cliques
1. Aller sur onglet `http://localhost:3000`.
2. Se connecter avec ton compte admin configure.
3. Cliquer `Browse` ou `Collections`.
4. Ouvrir un dashboard / une question existante.

### Ce que tu dis
"Metabase est l'interface utilisateur. Les actions de navigation deviennent des
evenements qui alimentent notre pipeline de recommandation."

---

## Minute 7-10 : RabbitMQ (preuve asynchrone)

### Ce que tu cliques
1. Aller sur onglet `http://localhost:15672`.
2. Login: `guest / guest` (si credentials par defaut).
3. Cliquer `Queues`.
4. Montrer `navigation_logs`, `users_sync`, `reports_sync`.

### Ce que tu dis
"RabbitMQ decouple la collecte de logs du traitement. Meme si un service
ralentit, les messages restent en file."

---

## Minute 10-13 : API et modele

### Ce que tu cliques
1. Aller sur onglet `http://localhost:8000/docs`.
2. Ouvrir endpoint `POST /train`.
3. Cliquer `Try it out`, puis `Execute`.
4. Ouvrir `GET /recommendations/{user_id}`.
5. Saisir `user_id=1`, `n=5`, puis `Execute`.

### Ce que tu dis
"Le modele hybride est servi via FastAPI. On peut entrainer puis demander un
top-5 personnalise."

---

## Minute 13-16 : Batch serving et monitoring

### Ce que tu fais (PowerShell)
```powershell
Invoke-RestMethod -Method Post "http://localhost:8000/batch/recommendations/generate?n=5" | ConvertTo-Json -Depth 10
Invoke-RestMethod "http://localhost:8000/stored-recommendations/1?n=5" | ConvertTo-Json -Depth 10
Invoke-RestMethod "http://localhost:8000/monitoring/summary" | ConvertTo-Json -Depth 10
```

### Ce que tu dis
"Le batch precalcule et stocke les recommandations pour tous les utilisateurs.
Le monitoring nous donne l'etat en temps reel du pipeline et du serving."

---

## Minute 16-18 : Test global de qualite

### Ce que tu fais
```powershell
docker exec bi_backend python tests/run_phase6_tests.py
```

### Ce que tu dis
"La chaine complete est validee par tests unitaires, integration, E2E et
stress."

---

## Minute 18-20 : Bug reel + conclusion

### Ce que tu dis
"Un bug reel a ete detecte: connexion PostgreSQL stale cote consumer.  
Nous avons corrige par reconnexion automatique et requeue des messages.
Conclusion: systeme fonctionnel, teste, et demotrable localement."

---

## C. Plan B si quelque chose bloque

Si API bloque:
```powershell
docker-compose restart backend
Start-Sleep -Seconds 8
```

Si consumer bloque:
```powershell
docker-compose restart consumer
Start-Sleep -Seconds 8
docker-compose logs --tail=50 consumer
```

Si publisher bloque:
```powershell
docker-compose restart publisher
Start-Sleep -Seconds 8
docker-compose logs --tail=50 publisher
```

Ensuite afficher les preuves deja generees:
- `docs/final_report/evidence/monitoring_summary_*.json`
- `docs/final_report/evidence/stored_recommendations_user1_*.json`
- `docs/final_report/evidence/docker_ps_*.txt`

---

## D. Repetition la veille (obligatoire)

1. Lancer:
```powershell
docker exec bi_backend python demo_local.py --events 50 --top-n 5
```
2. Lancer:
```powershell
docker exec bi_backend python tests/run_phase6_tests.py
```
3. Generer preuves:
```powershell
powershell -ExecutionPolicy Bypass -File docs/final_report/collect_evidence.ps1
```
4. Lire ton script oral:
- `docs/final_report/ORAL_SCRIPT_7MIN.md`

Si ces 4 etapes passent, tu es pret.
