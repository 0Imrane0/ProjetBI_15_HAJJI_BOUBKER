# ⚡ QUICK START - Setup Complet en 5 Minutes

## 🎯 Résumé des Problèmes Résolus

| Problème | Cause | Solution |
|----------|-------|----------|
| ❌ `generate_data.py` échouait | `DB_HOST=localhost` ne marchait pas depuis Docker | ✅ Changé en `DB_HOST=postgres` |
| ❌ Pas de rapports Metabase | Aucun script pour les créer | ✅ Créé `create_metabase_reports.py` |
| ❌ Processus manuel compliqué | Deux scripts à lancer séparément | ✅ Créé `setup_data.ps1` pour Windows |

---

## 🚀 Lancement Rapide (5 min)

### Windows PowerShell

```powershell
# 1. Navigue vers le projet
cd "C:\Users\LOQ\Documents\ISIBD S8\BI\ProjetBI_15_HAJJI_BOUBKER"

# 2. Vérifie que PostgreSQL tourne
docker-compose ps

# 3. Si PostgreSQL n'est pas up, lance-le seul
docker-compose up -d postgres

# 4. Attends 10 secondes
Start-Sleep -Seconds 10

# 5. Lance le script de setup complet ⭐ (LE PLUS IMPORTANT)
.\setup_data.ps1

# 6. Attends 3-5 minutes
```

**Fin du script** : Tu verras ✅ ALL DATA SETUP COMPLETE!

---

## ✅ Vérification (2 min)

Après que `setup_data.ps1` finisse :

```powershell
# Relance tous les services
docker-compose up -d

# Attends 10 secondes
Start-Sleep -Seconds 10

# Voir les logs (Ctrl+C pour quitter après 30 sec)
docker-compose logs -f publisher consumer
```

**Tu devrais voir** :
```
publisher  | [recent_views] 📤 100 events
consumer   | [navigation_logs] ✅ processed
```

---

## 📊 Vérification des Données (1 min)

```powershell
# Accédez à PostgreSQL
docker exec -it bi_postgres psql -U admin -d bi_recommendation

# Exécutez:
SELECT COUNT(*) FROM report_card;     -- Doit être 40
SELECT COUNT(*) FROM core_user;       -- Doit être ~100
SELECT COUNT(*) FROM recent_views;    -- Doit être ~6000
SELECT COUNT(*) FROM users;           -- Doit croître
SELECT COUNT(*) FROM reports;         -- Doit croître
SELECT COUNT(*) FROM navigation_logs; -- Doit croître

# Quitter
\q
```

---

## 📋 Fichiers Créés / Modifiés

```
✅ generate_data.py          [MODIFIÉ] - Correction DB_HOST
✅ create_metabase_reports.py [CRÉÉ]   - Génère 40 rapports
✅ setup_data.ps1            [CRÉÉ]   - Orchestrateur Windows
✅ setup_data.sh             [CRÉÉ]   - Orchestrateur Linux/Mac
✅ DATA_SETUP_GUIDE.md       [CRÉÉ]   - Guide détaillé
✅ QUICK_START.md            [CRÉÉ]   - Ce fichier
```

---

## 🐛 Si Ça Échoue

**Erreur 1** : "connection to server... failed"
```powershell
# PostgreSQL pas prêt, attends plus longtemps
Start-Sleep -Seconds 20
.\setup_data.ps1
```

**Erreur 2** : "Table report_card does not exist"
```powershell
# Relance PostgreSQL
docker-compose down
docker-compose up -d postgres
Start-Sleep -Seconds 15
.\setup_data.ps1
```

**Erreur 3** : "Cannot create reports - connection error"
```powershell
# Exécute les scripts séparément
python create_metabase_reports.py
python generate_data.py
```

---

## 🎯 Prochaines Étapes (Phase 2)

Une fois ✅ confirmé :

1. ✅ Données créées dans PostgreSQL
2. ✅ Publisher envoie à RabbitMQ
3. ✅ Consumer insère en local
4. ⏳ **Tester le pipeline complet** (Phase 2.3 & 2.4)
5. ⏳ Identifier les problèmes (Phase 3)
6. ⏳ Solutions d'ingénierie (Phase 4)
7. ⏳ Implémenter le ML (Phase 5)

---

## 💡 Points Clés

- ✅ `setup_data.ps1` fait TOUT en une commande
- ✅ Rapporte les 5 COUNTs de vérification
- ✅ Si ça marche, tu peux continuer Phase 2
- ✅ Si ça échoue, dis-moi exactement le message d'erreur

---

**Lance le script maintenant ! 🚀**

```powershell
.\setup_data.ps1
```

**Rapporte-moi le résultat final !** ✅
