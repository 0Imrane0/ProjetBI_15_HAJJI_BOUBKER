# 🚀 SETUP DATA - Solution Correcte

## 🔴 Le Problème

Ton setup échoue parce que :
- ❌ Tu lances le script depuis **Windows (localhost)**
- ✅ Mais `postgres` ne marche que depuis **Docker**

**Le fix** : Lancer les scripts **À L'INTÉRIEUR Docker**.

---

## ✅ Solution 1 : SIMPLE & DIRECTE (Recommandée)

Exécute ces commandes **dans l'ordre** :

```powershell
# 1. Assure-toi d'être dans le bon dossier
cd "C:\Users\LOQ\Documents\ISIBD S8\BI\ProjetBI_15_HAJJI_BOUBKER"

# 2. Lance juste PostgreSQL
docker-compose up -d postgres

# 3. Attends que PostgreSQL soit prêt (15-20 secondes)
Start-Sleep -Seconds 20

# 4. Lance create_metabase_reports.py DANS Docker ⭐
docker-compose exec -T postgres bash -c "cd /app && python create_metabase_reports.py"

# 5. Attends 30 secondes
Start-Sleep -Seconds 30

# 6. Lance generate_data.py DANS Docker ⭐
docker-compose exec -T postgres bash -c "cd /app && python generate_data.py"
```

### Explications

- `docker-compose exec -T postgres` = exécute une commande DANS le container postgres
- `-T` = pas d'allocation TTY (besoin pour PowerShell)
- `cd /app` = naviguer où les fichiers Python sont
- Les scripts utilisent automatiquement `DB_HOST=postgres` (qui marche en Docker)

---

## ✅ Solution 2 : Avec un Conteneur Setup Dédié

Si tu préfères une approche plus "propre" :

```powershell
# 1. Créer un container de setup
docker-compose exec -T postgres bash -c "
cd /app && \
python create_metabase_reports.py && \
python generate_data.py
"
```

Cela exécute les deux en séquence.

---

## ✅ Vérifier le Résultat

Après les commandes ci-dessus :

```powershell
docker exec -it bi_postgres psql -U admin -d bi_recommendation

# Exécute ces commandes:
SELECT COUNT(*) FROM report_card;     -- Doit être 40
SELECT COUNT(*) FROM core_user;       -- Doit être ~100
SELECT COUNT(*) FROM recent_views;    -- Doit être ~6000

\q
```

---

## 🐛 Dépannage

### Erreur 1 : "No such container"

```powershell
# PostgreSQL n'est pas lancé. Lance-le d'abord:
docker-compose up -d postgres
Start-Sleep -Seconds 20
```

### Erreur 2 : "postgres: command not found"

```powershell
# Essaye d'exécuter directement dans le container:
docker exec -it bi_postgres bash
# À l'intérieur du container:
cd /app
python create_metabase_reports.py
python generate_data.py
exit
```

### Erreur 3 : "Permission denied"

```powershell
# Ajoute -T pour éviter TTY:
docker-compose exec -T postgres bash -c "cd /app && python create_metabase_reports.py"
```

---

## 📋 Commandes Rapides (Copy-Paste)

### Windows PowerShell

```powershell
cd "C:\Users\LOQ\Documents\ISIBD S8\BI\ProjetBI_15_HAJJI_BOUBKER"
docker-compose up -d postgres
Start-Sleep -Seconds 20
docker-compose exec -T postgres bash -c "cd /app && python create_metabase_reports.py"
Start-Sleep -Seconds 30
docker-compose exec -T postgres bash -c "cd /app && python generate_data.py"
```

### Vérification

```powershell
docker exec -it bi_postgres psql -U admin -d bi_recommendation -c "
SELECT COUNT(*) as report_card FROM report_card;
SELECT COUNT(*) as core_user FROM core_user;
SELECT COUNT(*) as recent_views FROM recent_views;
"
```

---

## 🎯 Prochaines Étapes

Une fois ✅ confirmé (tous les COUNTs > 0) :

```powershell
# 1. Relance tous les services
docker-compose up -d

# 2. Attends 10 secondes
Start-Sleep -Seconds 10

# 3. Regarde les logs (Ctrl+C pour quitter)
docker-compose logs -f publisher consumer

# 4. Après 1-2 minutes, tu devrais voir:
# publisher | [recent_views] 📤 100 events
# consumer  | [navigation_logs] ✅ processed
```

---

**Essaye maintenant ! 🚀**
