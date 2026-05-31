# 📊 DATA SETUP GUIDE

Ce guide explique comment créer les rapports Metabase et générer les données de test pour le projet BI Adaptative.

## 🎯 Objectif

1. **Créer 40 rapports** dans la table `report_card` (Metabase)
2. **Générer 100 utilisateurs** avec des interactions réalistes
3. **Créer ~6000 événements** de navigation pour entraîner les modèles ML

## 📋 Fichiers Clés

- `create_metabase_reports.py` : Script pour créer les 40 rapports
- `generate_data.py` : Script pour générer 100 utilisateurs + interactions
- `setup_data.ps1` : Script orchestrateur (Windows - PowerShell)
- `setup_data.sh` : Script orchestrateur (Linux/Mac - Bash)

## 🚀 Exécution Rapide (Recommandée)

### Sur Windows (PowerShell)

```powershell
# 1. Assure-toi que Docker tourne
docker-compose ps

# 2. Lance juste PostgreSQL (pas besoin des autres services)
docker-compose up -d postgres

# 3. Attends que PostgreSQL soit prêt
Start-Sleep -Seconds 10

# 4. Lance le script de setup complet
.\setup_data.ps1
```

**Durée** : ~3-5 minutes

### Sur Linux/Mac (Bash)

```bash
# 1. Assure-toi que Docker tourne
docker-compose ps

# 2. Lance juste PostgreSQL
docker-compose up -d postgres

# 3. Attends que PostgreSQL soit prêt
sleep 10

# 4. Lance le script de setup complet
bash setup_data.sh
```

---

## 🔧 Exécution Manuelle (Si le script échoue)

Si le script de setup automatique ne fonctionne pas, fais-le manuellement :

### Étape 1 : Créer les Rapports

```powershell
python create_metabase_reports.py
```

**Résultat attendu** :
```
============================================================================
🚀 CREATING METABASE REPORTS
============================================================================
✅ Connected to PostgreSQL

✅ Successfully created 40 reports
📊 Total reports in database: 40

📋 Sample reports created:
    1. Revenue Dashboard (table)
    2. Revenue by Region (bar)
    3. Product Performance (line)
    ...
```

### Étape 2 : Générer les Données

```powershell
python generate_data.py
```

**Résultat attendu** :
```
✅ Connected to PostgreSQL
👥 Cluster: Sales Manager (17 users)
  ✔ Alice Smith (alice.smith1@company.com) — 87 views
  ✔ Bob Johnson (bob.johnson2@company.com) — 120 views
  ...
👥 Cluster: Product Analyst (17 users)
  ...
🎉 Done! 100 users, 6000 views inserted into recent_views.
```

---

## ✅ Vérification des Données

Après l'exécution, vérifie que tout est en place :

```powershell
# Accédez à PostgreSQL
docker exec -it bi_postgres psql -U admin -d bi_recommendation

# À l'intérieur de psql, exécutez:
SELECT COUNT(*) FROM report_card;       -- Doit être 40
SELECT COUNT(*) FROM core_user;         -- Doit être ~100
SELECT COUNT(*) FROM recent_views;      -- Doit être ~6000

# Voir quelques rapports
SELECT id, name, display FROM report_card LIMIT 10;

# Voir quelques utilisateurs
SELECT id, email, first_name FROM core_user LIMIT 10;

# Voir quelques interactions
SELECT * FROM recent_views LIMIT 5;

# Quitter
\q
```

---

## 🔄 Démarrage Complet du Pipeline

Une fois que les données sont créées :

```powershell
# 1. Relancer tous les services
docker-compose up -d

# 2. Attendre 10 secondes que tout démarre
Start-Sleep -Seconds 10

# 3. Voir les logs du Publisher et Consumer
docker-compose logs -f publisher consumer

# 4. Attendre 1-2 minutes pour voir les messages passer
```

**Tu devrais voir** :
```
publisher    | [recent_views] 📤 50 events (total: 50)
publisher    | [core_user] 📤 30 events (total: 30)
publisher    | [report_card] 📤 20 events (total: 20)
consumer     | [navigation_logs] ✅ processed
consumer     | [users_sync] ✅ processed
consumer     | [reports_sync] ✅ processed
```

---

## 📊 Vérification du Pipeline Complet

```powershell
# Voir si les données sont arrives en local
docker exec -it bi_postgres psql -U admin -d bi_recommendation

# Vérifier les tables locales
SELECT COUNT(*) FROM users;              -- Doit grandir
SELECT COUNT(*) FROM reports;            -- Doit grandir
SELECT COUNT(*) FROM navigation_logs;    -- Doit grandir

# Exemple de données
SELECT * FROM users LIMIT 5;
SELECT * FROM navigation_logs LIMIT 5;

\q
```

---

## 🐛 Dépannage

### Erreur : "connection to server... failed"

**Cause** : Docker n'est pas prêt.

**Fix** :
```powershell
# Attends plus longtemps
Start-Sleep -Seconds 20

# Puis réessaye
python create_metabase_reports.py
```

### Erreur : "Table report_card does not exist"

**Cause** : init.sql ne s'est pas exécuté.

**Fix** :
```powershell
# Relance PostgreSQL complètement
docker-compose down
docker-compose up -d postgres
Start-Sleep -Seconds 15

# Réessaye
python create_metabase_reports.py
```

### Les données ne passent pas dans le pipeline

**Cause** : Publisher/Consumer pas lancés.

**Fix** :
```powershell
# Relance tous les services
docker-compose up -d

# Observe les logs
docker-compose logs -f publisher consumer
```

---

## 📈 Volume de Données

**Par défaut**, le script génère :

| Entité | Nombre | Détails |
|--------|--------|---------|
| Rapports | 40 | Répartis sur 8 catégories (Finance, Sales, Analytics, etc.) |
| Utilisateurs | 100 | 6 clusters (Sales Manager, Product Analyst, etc.) |
| Interactions | ~6000 | 50-150 par utilisateur, réparties sur 30 jours |
| Modèles | 2 | `card` (70-95%) et `dashboard` (5-30%) |

**C'est suffisant pour** :
✅ Entraîner les modèles ML  
✅ Tester le pipeline end-to-end  
✅ Évaluer les recommandations  

**C'est insuffisant pour** :
❌ Production à grande échelle  
❌ Tests de performance réalistes  

---

## 🎓 Ce Qui Se Passe Sous le Capot

### 1. `create_metabase_reports.py`

```python
INSERT INTO report_card (id, name, description, display, archived, created_at, updated_at)
VALUES 
  (1, "Revenue Dashboard", "...", "table", false, NOW(), NOW()),
  (2, "Revenue by Region", "...", "bar", false, NOW(), NOW()),
  ...
  (40, "Executive Summary", "...", "table", false, NOW(), NOW())
```

**Résultat** : 40 rapports peuvent maintenant être référencés par `generate_data.py`.

### 2. `generate_data.py`

Pour chaque cluster d'utilisateurs :

```python
for i in range(count):
    # 1. Crée un utilisateur dans core_user
    INSERT INTO core_user (id, email, first_name, last_name, ...)
    
    # 2. Génère 50-150 interactions aléatoires
    for _ in range(num_views):
        # Choisit un rapport du cluster (80%) ou aléatoire (20% bruit)
        report_id = pick_report(cluster)
        
        # Crée une interaction
        INSERT INTO recent_views (user_id, model, model_id, timestamp, context)
        VALUES (user_id, model, report_id, timestamp, context)
```

**Résultat** : 100 utilisateurs avec ~6000 interactions distribuées réalistement par cluster.

---

## 🔗 Prochaines Étapes

Une fois les données créées :

1. ✅ Les données sont dans `recent_views` (Metabase)
2. ✅ Publisher les récupère et les envoie à RabbitMQ
3. ✅ Consumer les traite et les insère dans nos tables locales (`users`, `reports`, `navigation_logs`)
4. ⏳ **Prochaine Phase 2** : Tester Publisher & Consumer
5. ⏳ **Phase 3** : Identifier les problèmes
6. ⏳ **Phase 5** : Entraîner les modèles ML

---

## 📞 Questions ?

Si quelque chose ne marche pas :

1. Vérifie que Docker tourne : `docker-compose ps`
2. Vérifie les logs : `docker-compose logs postgres`
3. Essaye de te reconnecter manuellement : `docker exec -it bi_postgres psql -U admin`
4. Rapporte-moi l'erreur exacte !

---

**Bon courage ! 🚀**
