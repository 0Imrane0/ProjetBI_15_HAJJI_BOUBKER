# 📊 BI ADAPTATIVE – Recommandation Personnalisée de Rapports
## Documentation Complète du Projet

---

## 🎯 PARTIE 1 : DE QUOI S'AGIT-IL ?

### 📝 Résumé Exécutif
Le projet **BI Adaptative** est une solution d'ingénierie orientée IA (AI-driven engineering) qui transforme une plateforme Business Intelligence (Metabase) classique en un système intelligent et proactif. Au lieu de laisser les utilisateurs noyés sous des centaines de rapports, le système recommande automatiquement les rapports les plus pertinents basés sur leur comportement passé et celui d'utilisateurs similaires.

---

## 🔴 LE PROBLÈME : Information Overload

### Contexte actuel
- Les portails BI (Business Intelligence) modernes contiennent **des centaines de rapports**
- Les utilisateurs se trouvent submergés et perdus
- Résultats : 
  - ⏱️ Perte de temps à chercher les rapports utiles
  - 📉 Sous-utilisation des rapports pertinents
  - 😤 Mauvaise expérience utilisateur

### Exemple concret
Imagine une entreprise avec 200 rapports disponibles. Un directeur commercial se connecte :
- ❌ AVANT (sans recommandation) : Il doit parcourir des dizaines de rapports pour trouver "Ventes mensuelles par région"
- ✅ APRÈS (avec recommandation) : En une seconde, le système lui propose automatiquement "Ventes mensuelles par région", "Prévisions Q2", "Client Top 10" basé sur ce qu'il a consulté avant

---

## 🎯 LES OBJECTIFS PRINCIPAUX

### 1️⃣ **Data Pipeline & Ingestion**
Créer un flux de données robuste et asynchrone :
- Capturer chaque action de l'utilisateur dans Metabase (clics, temps passé)
- Transmettre ces événements via RabbitMQ (Message Broker)
- Stocker proprement les logs dans PostgreSQL
- Pipeline capable de traiter des centaines d'événements par seconde sans bloquer l'interface

### 2️⃣ **Moteur d'Intelligence Artificielle**
Développer un système de recommandation hybride :
- **Filtrage Collaboratif** : "Les utilisateurs comme toi regardent aussi ces rapports"
  - Basé sur les similarités entre utilisateurs
  - Utilise la bibliothèque `Surprise`
  
- **Filtrage Basé sur le Contenu** : "Tu as aimé ce rapport → voici des rapports similaires"
  - Basé sur les métadonnées (tags, titre, description) des rapports
  - Utilise `scikit-learn`
  
- **Approche Hybride** : Combinaison des deux pour des résultats optimaux

### 3️⃣ **Intégration dans l'Interface**
Rendre visible et utile les recommandations :
- Ajouter une section "Rapports recommandés pour vous" dans Metabase
- Afficher les 3-5 meilleurs rapports suggérés
- Intégration transparente pour l'utilisateur final

### 4️⃣ **Résilience & Architecture**
Garantir un système robuste et "en production" :
- Tolérance aux pannes (si la base de données crash, RabbitMQ garde les données en attente)
- Orchestration complète avec Docker
- Démonstration de la résilience avec simulation de panne

### 5️⃣ **DevOps & CI/CD**
Démontrer une maîtrise de l'ingénierie logicielle :
- Pipeline d'intégration continue (GitHub Actions)
- Linting et tests automatiques
- Déploiement reproductible

---

## 🏗️ ARCHITECTURE GLOBALE

```
┌─────────────────┐
│ METABASE        │  (Interface BI - Frontend)
│ (Utilisateurs)  │
└────────┬────────┘
         │
         ├──→ [1] Capture des clics
         │       (Logs: UserID, ReportID, Duration)
         │
         ▼
┌─────────────────────────────────────┐
│        RABBITMQ (Message Broker)    │  [2] File d'attente asynchrone
│  (Garantit la fiabilité)            │      (Résilience)
└────────┬────────────────────────────┘
         │
         │ [3] Consommation asynchrone
         ▼
┌──────────────────────────┐
│  PYTHON CONSUMER         │  [4] Nettoyage et transformation
│  (Script de Pipeline)    │      des données
└────────┬─────────────────┘
         │
         │ [5] SQL INSERT
         ▼
┌──────────────────────────────┐
│    POSTGRESQL (Database)     │  [6] Historique d'utilisation
│  Table: navigation_logs      │
└────────┬─────────────────────┘
         │
         │ [7] Data extraction pour ML
         ▼
┌─────────────────────────────────────┐
│  AI & RECOMMENDATION ENGINE         │  [8] Modèles ML
│  • Surprise (Collaborative)         │  • Surprise (Collaboratif)
│  • scikit-learn (Content-based)     │  • scikit-learn (Contenu)
│  • Hybrid function                  │  • Combinaison optimale
└────────┬────────────────────────────┘
         │
         │ [9] Recommandations générées
         ▼
┌──────────────────────────┐
│   API REST (FastAPI)     │  [10] Expose les recommandations
└────────┬─────────────────┘
         │
         │ [11] Affichage dans le dashboard
         ▼
┌─────────────────────────┐
│ METABASE                │  [12] Section "Recommandations"
│ Dashboard utilisateur   │
└─────────────────────────┘
```

---

## 🛠️ STACK TECHNOLOGIQUE

| Composant | Technologie | Rôle |
|-----------|-------------|------|
| **BI Tool** | Metabase (Open Source) | Interface utilisateur, capturage des logs |
| **Message Broker** | RabbitMQ | Orchestration asynchrone, résilience |
| **Base de Données** | PostgreSQL | Stockage de l'historique d'utilisation |
| **Backend ML** | Python | Développement du moteur de recommandation |
| **Recommandation** | Surprise + scikit-learn | Algorithmes collaboratif et content-based |
| **API** | FastAPI / Flask | Exposition des recommandations |
| **Conteneurisation** | Docker & docker-compose | Orchestration locale et déploiement |
| **CI/CD** | GitHub Actions | Automatisation et tests |
| **Langue de programmation** | Python 3.9+ | Tout le backend |

---

## 🚀 ASPECTS AVANCÉS (DIFFÉRENCIATEURS)

### 1. Apprentissage par Renforcement (Contextual Bandits)
Au-delà du simple recommandeur statique :
- Le système apprend **en temps réel** de chaque clic de l'utilisateur
- Équilibre **exploration** vs **exploitation** : tester de nouveaux rapports ou montrer les meilleurs ?
- Ajuste dynamiquement les poids des recommandations

### 2. A/B Testing
Mesurer réellement l'impact :
- **Groupe A** : Utilisateurs sans recommandation (baseline)
- **Groupe B** : Utilisateurs avec recommandation
- Métriques : CTR (Click-Through Rate), temps d'utilisation, nombre de rapports consultés

---

## 📊 CRITÈRES D'ÉVALUATION

D'après la fiche du projet, voici comment vous serez notés :

| Critère | Poids | Description |
|---------|-------|-------------|
| **Réalisation Technique** | 40% | Qualité du code, architecture, pipeline complet |
| **Qualité BI & Visualisation** | 30% | Intégration dans Metabase, UX, présentation |
| **Originalité/Complexité** | 20% | Bandits contextuels, A/B testing, innovations |
| **Documentation** | 10% | Rapport clair, structure, schémas |

---

---

## 📋 PARTIE 2 : PLAN D'ACTION DÉTAILLÉ (ROADMAP)

Ce plan est conçu pour 2 développeurs travaillant en parallèle pendant **6 semaines**.

---

## 📌 PHASE 1 : Infrastructure & Setup (Semaine 1)

**Objectif** : Disposer d'un environnement de développement entièrement fonctionnel et conteneurisé.

### Tâche 1.1 : Initialiser le dépôt GitHub
- [ ] Créer un repository public/privé sur GitHub
- [ ] Inviter le collaborateur
- [ ] Créer un `.gitignore` approprié (Python, Docker, IDE)
- [ ] Initialiser un `README.md` avec description du projet

**Responsable** : Personne B (Backend)  
**Durée** : 1 heure

---

### Tâche 1.2 : Rédiger le fichier docker-compose.yml
**Description** : Ce fichier orchestre les 4 services principaux.

**Contenu minimal** :
```yaml
version: '3.8'

services:
  postgresql:
    image: postgres:14
    environment:
      POSTGRES_USER: aibi_user
      POSTGRES_PASSWORD: aibi_pass
      POSTGRES_DB: bi_adaptive
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

  rabbitmq:
    image: rabbitmq:3.12-management
    ports:
      - "5672:5672"
      - "15672:15672"
    environment:
      RABBITMQ_DEFAULT_USER: guest
      RABBITMQ_DEFAULT_PASS: guest

  metabase:
    image: metabase/metabase:latest
    ports:
      - "3000:3000"
    environment:
      MB_DB_TYPE: postgres
      MB_DB_DBNAME: bi_adaptive
      MB_DB_HOST: postgresql
      MB_DB_PORT: 5432
      MB_DB_USER: aibi_user
      MB_DB_PASS: aibi_pass

  python-consumer:
    build: ./backend
    depends_on:
      - postgresql
      - rabbitmq
    environment:
      RABBITMQ_HOST: rabbitmq
      DB_HOST: postgresql

volumes:
  postgres_data:
```

**Responsable** : Personne B (Backend)  
**Durée** : 2 heures

---

### Tâche 1.3 : Démarrer l'environnement Docker
```bash
docker-compose up -d
```

- [ ] Vérifier que PostgreSQL est accessible : `psql -h localhost -U aibi_user -d bi_adaptive`
- [ ] Vérifier RabbitMQ : http://localhost:15672 (guest/guest)
- [ ] Vérifier Metabase : http://localhost:3000
- [ ] Initialiser la base Metabase (setup wizard)

**Responsable** : Personne B (Backend)  
**Durée** : 1 heure

---

### Tâche 1.4 : Peupler Metabase avec des rapports fictifs

**Description** : Créer 15-20 tableaux de bord fictifs pour simuler le problème d'Information Overload.

**Procédure** :
1. Ouvrir Metabase (http://localhost:3000)
2. Connecter la "Sample Database" (fournie par défaut)
3. Créer manuellement 15-20 dashboards variés :
   - "Total de ventes par région"
   - "Clients les plus actifs"
   - "Produits en rupture"
   - "Tendance d'utilisation"
   - "Analyse RH"
   - "Budget vs Dépenses"
   - Etc.

**Responsable** : Personne B (Backend) + Personne A (Data/AI)  
**Durée** : 2-3 heures

---

## 📌 PHASE 2 : Tracking & Messaging (Semaine 2)

**Objectif** : Capturer chaque interaction utilisateur et la transmettre à RabbitMQ.

### Tâche 2.1 : Étudier Metabase & ses logs

**Description** : Comprendre comment Metabase capture les événements.

**Actions** :
- [ ] Lire la documentation officielle de Metabase sur les Audit Logs
- [ ] Explorer la table `audit` interne de Metabase
- [ ] Identifier comment exposer ces logs via API ou script

**Responsable** : Personne B (Backend)  
**Durée** : 1-2 heures  
**Ressources** : 
- https://www.metabase.com/docs/latest/admin-guide/audit-logs
- Documentation Metabase API

---

### Tâche 2.2 : Configurer Metabase pour publier les logs dans RabbitMQ

**Approche recommandée** : Créer un script Python qui interroge Metabase API et envoie les logs à RabbitMQ.

**Pseudo-code** :
```python
import pika
import requests
import json
from datetime import datetime

# Connexion RabbitMQ
connection = pika.BlockingConnection(pika.ConnectionParameters('rabbitmq'))
channel = connection.channel()
channel.queue_declare(queue='navigation_logs', durable=True)

# Interroger l'API Metabase pour les audit logs
response = requests.get('http://metabase:3000/api/audit')
logs = response.json()

# Publier chaque log dans RabbitMQ
for log in logs:
    message = json.dumps({
        'user_id': log['user_id'],
        'object_id': log['object_id'],  # Report ID
        'action': log['action'],  # Ex: 'view'
        'timestamp': log['timestamp'],
        'duration': log.get('details', {}).get('duration', 0)
    })
    channel.basic_publish(exchange='', routing_key='navigation_logs', body=message)

connection.close()
```

**Responsable** : Personne B (Backend)  
**Durée** : 2-3 heures

---

### Tâche 2.3 : Tester le flux de messages

**Test manuel** :
1. [ ] Ouvrir l'interface d'administration RabbitMQ : http://localhost:15672
2. [ ] Cliquer sur Metabase
3. [ ] Ouvrir quelques rapports
4. [ ] Vérifier que les messages apparaissent dans la queue `navigation_logs` de RabbitMQ
5. [ ] Vérifier le format JSON des messages

**Responsable** : Personne B (Backend)  
**Durée** : 1 heure

---

## 📌 PHASE 3 : Data Ingestion Pipeline (Semaine 2-3)

**Objectif** : Extraire les messages de RabbitMQ et les stocker dans PostgreSQL.

### Tâche 3.1 : Créer le schéma PostgreSQL

**Description** : Créer les tables pour stocker les logs de navigation.

```sql
CREATE TABLE navigation_logs (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    report_id INTEGER NOT NULL,
    action VARCHAR(50) NOT NULL,  -- 'view', 'click', etc.
    duration INTEGER DEFAULT 0,    -- Secondes
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    metabase_user_id INTEGER UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE reports (
    id SERIAL PRIMARY KEY,
    metabase_report_id INTEGER UNIQUE NOT NULL,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    tags VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Index pour performances
CREATE INDEX idx_user_timestamp ON navigation_logs(user_id, timestamp);
CREATE INDEX idx_report ON navigation_logs(report_id);
```

**Responsable** : Personne A (Data/AI)  
**Durée** : 1 heure

---

### Tâche 3.2 : Développer le script Consumer Python

**Description** : Créer un script qui écoute RabbitMQ et insère les logs dans PostgreSQL.

**Structure du projet** :
```
/backend
  ├── consumer.py          # Main script
  ├── requirements.txt     # Dependencies
  ├── config.py           # Configuration
  └── Dockerfile          # Containerization
```

**Contenu minimal de consumer.py** :
```python
import pika
import psycopg2
import json
import logging
from config import RABBITMQ_HOST, DB_HOST, DB_USER, DB_PASSWORD

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def process_message(ch, method, properties, body):
    """Process incoming message from RabbitMQ"""
    try:
        log_data = json.loads(body)
        
        # Connexion PostgreSQL
        conn = psycopg2.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database="bi_adaptive"
        )
        cur = conn.cursor()
        
        # Insert log
        cur.execute("""
            INSERT INTO navigation_logs 
            (user_id, report_id, action, duration, timestamp)
            VALUES (%s, %s, %s, %s, %s)
        """, (
            log_data['user_id'],
            log_data['report_id'],
            log_data['action'],
            log_data.get('duration', 0),
            log_data['timestamp']
        ))
        
        conn.commit()
        cur.close()
        conn.close()
        
        # Acknowledge message
        ch.basic_ack(delivery_tag=method.delivery_tag)
        logger.info(f"Processed log for user {log_data['user_id']}")
        
    except Exception as e:
        logger.error(f"Error processing message: {e}")
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)

def main():
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host=RABBITMQ_HOST)
    )
    channel = connection.channel()
    channel.queue_declare(queue='navigation_logs', durable=True)
    
    channel.basic_consume(
        queue='navigation_logs',
        on_message_callback=process_message,
        auto_ack=False
    )
    
    logger.info("Consumer started. Waiting for messages...")
    channel.start_consuming()

if __name__ == '__main__':
    main()
```

**Responsable** : Personne B (Backend)  
**Durée** : 2-3 heures

---

### Tâche 3.3 : Test End-to-End

**Procédure** :
1. [ ] Démarrer le consumer : `python backend/consumer.py`
2. [ ] Ouvrir Metabase et cliquer sur plusieurs rapports
3. [ ] Vérifier que les logs s'ajoutent dans PostgreSQL :
   ```sql
   SELECT COUNT(*) FROM navigation_logs;
   SELECT * FROM navigation_logs LIMIT 10;
   ```
4. [ ] Documenter le flux dans le README

**Responsable** : Personne B (Backend) + Personne A (Data/AI)  
**Durée** : 1-2 heures

---

## 📌 PHASE 4 : Moteur d'Intelligence Artificielle (Semaine 3-4)

**Objectif** : Construire les modèles de recommandation.

### Tâche 4.1 : Extraction et exploration des données

**Description** : Charger les logs de PostgreSQL et les analyser.

```python
import pandas as pd
import psycopg2
from sklearn.preprocessing import MinMaxScaler

# Load data from PostgreSQL
conn = psycopg2.connect(...)
query = "SELECT user_id, report_id, duration, timestamp FROM navigation_logs"
df = pd.read_sql(query, conn)

# Exploration
print(df.info())
print(df.describe())
print(f"Utilisateurs uniques: {df['user_id'].nunique()}")
print(f"Rapports uniques: {df['report_id'].nunique()}")

# Créer une matrice utilisateur-rapport
user_report_matrix = df.pivot_table(
    index='user_id',
    columns='report_id',
    values='duration',
    fill_value=0
)
```

**Responsable** : Personne A (Data/AI)  
**Durée** : 2 heures

---

### Tâche 4.2 : Modèle de Filtrage Collaboratif (Surprise)

**Description** : Utiliser la librairie Surprise pour les recommandations basées sur le comportement similaire.

```python
from surprise import Dataset, Reader, SVD, cross_validate
from surprise.model_selection import train_test_split
import pandas as pd

# Préparer les données pour Surprise
data = Dataset.load_from_df(
    df[['user_id', 'report_id', 'duration']],
    reader=Reader(rating_scale=(0, 100))
)

# Splitting
trainset, testset = train_test_split(data, test_size=0.2)

# Training
model_cf = SVD()
model_cf.fit(trainset)

# Évaluation
predictions = model_cf.test(testset)

# Fonction de recommandation
def get_collaborative_recommendations(user_id, n_recommendations=3):
    """Basé sur les utilisateurs similaires"""
    all_reports = df['report_id'].unique()
    already_seen = df[df['user_id'] == user_id]['report_id'].unique()
    
    predictions_list = []
    for report_id in all_reports:
        if report_id not in already_seen:
            pred = model_cf.predict(user_id, report_id)
            predictions_list.append((report_id, pred.est))
    
    # Trier et retourner top N
    recommendations = sorted(predictions_list, key=lambda x: x[1], reverse=True)
    return recommendations[:n_recommendations]
```

**Responsable** : Personne A (Data/AI)  
**Durée** : 2-3 heures

---

### Tâche 4.3 : Modèle de Filtrage Basé sur le Contenu (scikit-learn)

**Description** : Recommander basé sur les métadonnées des rapports.

```python
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

# Charger métadonnées des rapports
reports_df = pd.read_sql("SELECT id, title, description, tags FROM reports", conn)

# Créer une matrix TF-IDF des descriptions
vectorizer = TfidfVectorizer(stop_words='english')
tfidf_matrix = vectorizer.fit_transform(
    reports_df['description'].fillna('') + ' ' + reports_df['tags'].fillna('')
)

# Calculer similarité cosinus
similarity_matrix = cosine_similarity(tfidf_matrix)

def get_content_based_recommendations(report_id, n_recommendations=3):
    """Basé sur la similarité du contenu"""
    similarity_scores = similarity_matrix[report_id]
    
    # Trier et retourner top N (excluant le rapport lui-même)
    similar_reports = np.argsort(-similarity_scores)[1:n_recommendations+1]
    
    return [(int(rid), similarity_scores[rid]) for rid in similar_reports]
```

**Responsable** : Personne A (Data/AI)  
**Durée** : 2-3 heures

---

### Tâche 4.4 : Modèle Hybride (Combinaison)

**Description** : Combiner les deux approches pour meilleur résultat.

```python
def get_hybrid_recommendations(user_id, n_recommendations=3, alpha=0.6):
    """
    Combine Collaborative (alpha) et Content-based (1-alpha)
    alpha=0.6 signifie 60% collaboratif, 40% basé sur contenu
    """
    
    # Obtenir les rapports déjà vus
    already_seen = df[df['user_id'] == user_id]['report_id'].unique()
    all_reports = df['report_id'].unique()
    
    recommendations_hybrid = []
    
    for report_id in all_reports:
        if report_id not in already_seen:
            # Score collaboratif
            pred_cf = model_cf.predict(user_id, report_id)
            score_cf = pred_cf.est / 100  # Normaliser
            
            # Score content-based (average similarity avec rapports vus)
            seen_similarities = [
                similarity_matrix[report_id][seen_report]
                for seen_report in already_seen
                if seen_report < len(similarity_matrix[report_id])
            ]
            score_cb = np.mean(seen_similarities) if seen_similarities else 0
            
            # Score hybride
            hybrid_score = alpha * score_cf + (1 - alpha) * score_cb
            recommendations_hybrid.append((report_id, hybrid_score))
    
    # Trier et retourner top N
    recommendations = sorted(recommendations_hybrid, key=lambda x: x[1], reverse=True)
    return recommendations[:n_recommendations]
```

**Responsable** : Personne A (Data/AI)  
**Durée** : 1-2 heures

---

### Tâche 4.5 : Sauvegarde des modèles

**Description** : Sauvegarder les modèles entraînés pour réutilisation.

```python
import joblib

# Sauvegarder
joblib.dump(model_cf, 'models/collaborative_model.pkl')
joblib.dump(vectorizer, 'models/tfidf_vectorizer.pkl')
joblib.dump(tfidf_matrix, 'models/tfidf_matrix.pkl')
joblib.dump(similarity_matrix, 'models/similarity_matrix.pkl')

# Charger
model_cf = joblib.load('models/collaborative_model.pkl')
vectorizer = joblib.load('models/tfidf_vectorizer.pkl')
```

**Responsable** : Personne A (Data/AI)  
**Durée** : 30 minutes

---

## 📌 PHASE 5 : API & Intégration (Semaine 4-5)

**Objectif** : Exposer les recommandations via une API et les afficher dans Metabase.

### Tâche 5.1 : Développer l'API REST (FastAPI)

**Structure** :
```
/api
  ├── main.py            # Application FastAPI
  ├── models.py          # Pydantic models
  ├── recommendations.py # Logique de recommandation
  └── requirements.txt
```

**Contenu de main.py** :
```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import joblib
import psycopg2

app = FastAPI(title="BI Adaptive Recommendation API")

# Charger les modèles
model_cf = joblib.load('models/collaborative_model.pkl')
vectorizer = joblib.load('models/tfidf_vectorizer.pkl')

class RecommendationRequest(BaseModel):
    user_id: int
    n_recommendations: int = 3
    alpha: float = 0.6

class RecommendationResponse(BaseModel):
    user_id: int
    recommendations: list

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.post("/recommendations", response_model=RecommendationResponse)
def get_recommendations(request: RecommendationRequest):
    """Get personalized recommendations for a user"""
    try:
        recommendations = get_hybrid_recommendations(
            user_id=request.user_id,
            n_recommendations=request.n_recommendations,
            alpha=request.alpha
        )
        
        return RecommendationResponse(
            user_id=request.user_id,
            recommendations=[
                {"report_id": int(rid), "score": float(score)}
                for rid, score in recommendations
            ]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='0.0.0.0', port=8000)
```

**Responsable** : Personne A (Data/AI)  
**Durée** : 2 heures

---

### Tâche 5.2 : Tester l'API

```bash
# Démarrer l'API
python api/main.py

# Test curl
curl -X POST "http://localhost:8000/recommendations" \
  -H "Content-Type: application/json" \
  -d '{"user_id": 1, "n_recommendations": 3}'
```

**Responsable** : Personne A (Data/AI)  
**Durée** : 1 heure

---

### Tâche 5.3 : Intégration dans docker-compose.yml

```yaml
  api:
    build: ./api
    ports:
      - "8000:8000"
    depends_on:
      - postgresql
      - python-consumer
    environment:
      DB_HOST: postgresql
      MODEL_PATH: /app/models
```

**Responsable** : Personne B (Backend)  
**Durée** : 30 minutes

---

### Tâche 5.4 : Modifier Metabase pour afficher les recommandations

**Option 1 (Recommandée)** : Utiliser un Dashboard custom avec carte personnalisée

**Option 2** : Modifier le code source Metabase React pour ajouter un widget "Recommendations"

**Approche pragmatique pour 2 développeurs** :
- Créer un Dashboard Metabase spécifique "Your Recommended Reports"
- Ce dashboard affiche les rapports retournés par l'API
- Peut être affiché en tant que page d'accueil pour chaque utilisateur

**SQL dans Metabase** (pour afficher les recommendations) :
```sql
-- Créer une vue qui appelle l'API (si Metabase le permet)
-- Sinon, créer une table materialisée mise à jour régulièrement

CREATE TABLE user_recommendations AS
SELECT 
    user_id,
    report_id,
    score,
    CURRENT_TIMESTAMP as generated_at
FROM (
    -- Résultat de l'API importé
)
```

**Responsable** : Personne B (Backend)  
**Durée** : 2-3 heures

---

## 📌 PHASE 6 : Avancé & Résilience (Semaine 5-6)

**Objectif** : Ajouter les fonctionnalités avancées et démontrer la robustesse du système.

### Tâche 6.1 : Implémenter CI/CD avec GitHub Actions

**Fichier : `.github/workflows/ci.yml`**

```yaml
name: CI Pipeline

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.9'
      
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install flake8 pytest
      
      - name: Lint with flake8
        run: |
          flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
      
      - name: Run tests
        run: |
          pytest tests/
```

**Responsable** : Personne B (Backend)  
**Durée** : 1-2 heures

---

### Tâche 6.2 : Contextual Bandits (Apprentissage par renforcement - OPTIONNEL)

**Concept** : Le système apprend des clics réels sur les recommandations.

```python
from exploration_algorithms.contextual_bandits import ContextualBandits

# Initialiser l'algorithme
bandits = ContextualBandits(n_arms=len(all_reports), n_features=10)

def get_adaptive_recommendations(user_id, context, n_recommendations=3):
    """
    Recommandations qui s'adaptent avec chaque clic
    context: features de l'utilisateur (département, rôle, heure, etc.)
    """
    
    # Sélectionner les recommandations avec équilibre exploration/exploitation
    selected_reports = bandits.select(context, n_arms=n_recommendations)
    
    return selected_reports

# Quand l'utilisateur clique sur une recommandation
def log_recommendation_feedback(user_id, report_id, clicked):
    """Feedback pour améliorer le bandit"""
    reward = 1 if clicked else 0
    bandits.update(user_id, report_id, reward)
```

**Responsable** : Personne A (Data/AI)  
**Durée** : 3-4 heures (complexe)

---

### Tâche 6.3 : A/B Testing

**Conception** :
- **Groupe A** (Control) : Recommandations désactivées
- **Groupe B** (Test) : Recommandations activées

**Implémentation** :
```python
import random

def should_show_recommendations(user_id):
    """
    Déterminer si l'utilisateur est en groupe A ou B
    """
    # Hash consistant pour assurer que l'utilisateur reste dans le même groupe
    hash_value = hash(f"user_{user_id}") % 100
    
    return hash_value < 50  # 50% en groupe B

# Dans Metabase/Dashboard
if should_show_recommendations(current_user_id):
    show_recommendations_panel()
else:
    show_standard_dashboard()
```

**Métriques à tracker** :
- Nombre de rapports consultés par utilisateur
- Temps d'utilisation moyen
- Taux de clic sur les recommandations (CTR)

**Responsable** : Personne A (Data/AI) + Personne B (Backend)  
**Durée** : 2-3 heures

---

### Tâche 6.4 : Test de Résilience (Panne Simulée)

**Scénario** : Crash intentionnel de PostgreSQL, vérifier que RabbitMQ garde les données.

**Procédure de démonstration** :
```bash
# 1. Vérifier le système fonctionne
curl http://localhost:8000/health

# 2. Mettre en place monitoring pour voir les messages en queue
# Accéder à http://localhost:15672 (RabbitMQ admin)

# 3. Générer du trafic (clics dans Metabase)
# Ouvrir plusieurs rapports

# 4. CRASH intentionnel de PostgreSQL
docker-compose pause postgresql

# 5. Continuer à générer du trafic dans Metabase
# Les messages s'accumulent dans RabbitMQ (visible dans l'admin)

# 6. Restaurer PostgreSQL
docker-compose unpause postgresql

# 7. Observer que le Consumer reprend et rattrape son retard
# Les logs disparaissent de la queue et remplissent la DB

# 8. Vérifier intégrité des données
psql -h localhost -U aibi_user -d bi_adaptive -c "SELECT COUNT(*) FROM navigation_logs;"
```

**Responsable** : Personne B (Backend)  
**Durée** : 1-2 heures

---

### Tâche 6.5 : Documentation du code et du système

- [ ] Ajouter docstrings détaillées à tout le code Python
- [ ] Créer un `ARCHITECTURE.md` décrivant le système
- [ ] Créer un `SETUP.md` expliquant comment démarrer le projet
- [ ] Créer un `API_DOCUMENTATION.md`

**Responsable** : Les deux  
**Durée** : 2 heures

---

## 📌 PHASE 7 : Rapport & Soutenance (Semaine 6)

**Objectif** : Créer les livrables finaux et préparer la présentation orale.

### Tâche 7.1 : Rédiger le Rapport Écrit (20-30 pages)

**Structure recommandée** :

```
1. Introduction (2-3 pages)
   - Contexte BI actuel
   - Problématique (Information Overload)
   - Objectifs du projet

2. État de l'art (2 pages)
   - Systèmes de recommandation existants
   - Outils BI concurrents

3. Architecture et Design (4-5 pages)
   - Schéma global (avec diagrams)
   - Description de chaque composant
   - Flux de données (Data Pipeline)
   - Pipeline CI/CD

4. Détails Techniques (5-6 pages)
   - Modèles de recommandation (Surprise, scikit-learn)
   - Approche hybride
   - Intégration API
   - Stack technologique justifiée

5. Implémentation (4-5 pages)
   - Code snippets clés
   - Défis rencontrés et solutions
   - Tests et résultats

6. Résultats et Évaluation (3-4 pages)
   - Metrics de performance
   - Résultats A/B testing
   - Démonstration de résilience

7. Conclusion et Perspectives (1-2 pages)
   - Résumé des réalisations
   - Améliorations futures
   - Apprentissages

Annexes :
   - Code source complet
   - Schémas détaillés
   - Résultats détaillés des tests
```

**Responsable** : Les deux (rédaction collaborative)  
**Durée** : 4-5 heures

---

### Tâche 7.2 : Créer les Slides de Présentation (20 minutes)

**Structure** :
```
1. Titre + Introduction (1 slide)
2. Problématique (1 slide)
3. Objectifs (1 slide)
4. Architecture Globale (1 slide - diagramme principal)
5. Composants Clés (3-4 slides)
   - Data Pipeline
   - ML Engine
   - API & Integration
6. Résultats (2 slides)
   - Metrics
   - A/B Testing
7. Démo Live (mention - pas de slide)
8. Conclusion (1 slide)

Total : ~12-15 slides
```

**Responsable** : Les deux  
**Durée** : 2-3 heures

---

### Tâche 7.3 : Préparer la Démo Live

**Checklist** :
- [ ] Tous les containers démarent sans erreurs
- [ ] Metabase est accessible et rempli
- [ ] L'API retourne les recommandations
- [ ] Les recommendations s'affichent dans Metabase
- [ ] Scénario de panne simulée fonctionne

**Script de démo** (30 minutes) :
```
0-3 min   : Intro rapide du problème
3-8 min   : Architecture globale
8-13 min  : Démo du système fonctionnant :
            - Accéder à Metabase
            - Montrer les dashboards
            - Voir les recommendations
13-18 min : Montrer le pipeline technique :
            - RabbitMQ
            - PostgreSQL
            - API
18-23 min : PANNE SIMULÉE - Show résilience
23-30 min : Questions du jury
```

**Responsable** : Personne B (pour l'orchestration)  
**Durée** : 2 heures (préparation + répétitions)

---

---

## 🎬 PARTIE 3 : VISION FINALE - À QUOI RESSEMBLERA LE PROJET?

### 📺 Le Jour de la Soutenance

Imaginez la salle d'examen. Vous présentez pendant 20 minutes, puis le jury pose des questions.

---

### **Scène 1 : L'Interface Utilisateur** (Minutes 1-5)

**CE QUE VOIT LE JURY** :
Un portail BI ressemblant à Metabase, professionnel et fonctionnel. En haut de la page d'accueil, il y a une section spéciale :

```
╔════════════════════════════════════════════════════════════════╗
║  ✨ RAPPORTS RECOMMANDÉS POUR VOUS                             ║
╠════════════════════════════════════════════════════════════════╣
║                                                                 ║
║  📊 1. Analyse des Ventes par Région         [Score: 0.92]    ║
║     → Vous avez consulté 5 fois ce type de rapport             ║
║                                                                 ║
║  📈 2. Prévisions de Chiffre d'Affaires Q2   [Score: 0.88]    ║
║     → Les utilisateurs avec votre profil aiment ce rapport     ║
║                                                                 ║
║  👥 3. Clients Actifs ce Mois                [Score: 0.85]    ║
║     → Similaire à "Top Clients" que vous avez aimé             ║
║                                                                 ║
╚════════════════════════════════════════════════════════════════╝
```

**CE QUE VOUS EXPLIQUEZ** :
"Vous voyez, au lieu de se perdre dans 200 rapports, l'utilisateur voit immédiatement les 3 rapports les plus pertinents pour lui. Chacun a un score et une explication."

---

### **Scène 2 : Derrière les Coulisses - L'Architecture** (Minutes 6-15)

Vous montrez le diagramme et expliquez le flux :

**FLUX EN TEMPS RÉEL** :
```
Utilisateur clique → [Metabase capture] →
  → RabbitMQ reçoit le log →
  → Consumer Python traite →
  → PostgreSQL stocke →
  → Modèle ML génère recommendations →
  → API retourne les scores →
  → Metabase affiche "Rapports recommandés"

Tout cela en < 100ms, sans bloquer l'interface de l'utilisateur
```

**CODE VISIBLE** (Vous montrez sur écran) :
```python
# Quand un utilisateur ouvre un rapport
1. Metabase envoie : {"user_id": 5, "report_id": 42, "duration": 125}
2. RabbitMQ le met en queue
3. Notre Consumer Python le lit
4. PostgreSQL l'insère
5. Notre Moteur IA le traite :
   - Utilisateur 5 a vu le rapport 42 longtemps
   - Quels autres utilisateurs similaires aiment quoi?
   - Quels rapports sont similaires au 42?
6. API retourne : [
     {"report_id": 50, "score": 0.92},  # Recommandation 1
     {"report_id": 51, "score": 0.88},  # Recommandation 2
     {"report_id": 52, "score": 0.85}   # Recommandation 3
   ]
7. Metabase affiche ces 3 rapports au user
```

**LES MODÈLES D'IA EXPLIQUÉS** :

1. **Filtrage Collaboratif (Surprise)** :
   "L'utilisateur 5 a regardé les rapports A, B, C. L'utilisateur 3 a regardé A, B, C, D. Donc l'utilisateur 5 va probablement aimer le rapport D aussi."

2. **Content-Based (scikit-learn)** :
   "Le rapport 42 parle de 'Ventes par Région'. Les rapports 50, 51, 52 parlent aussi de 'Ventes', 'Régions', 'Analyse'... donc ils sont recommandés."

3. **Hybride** :
   "On combine 60% de l'approche collaboratif + 40% du content-based = meilleures recommandations."

---

### **Scène 3 : Le Moment "WOW" - Simulation de Panne** (Minutes 16-20)

**L'INSTANT DÉCISIF** :

Vous dites au jury : _"Je vais maintenant simuler une panne catastrophique. Je vais arrêter la base de données PostgreSQL."_

Vous exécutez :
```bash
$ docker-compose pause postgresql
```

La base de données s'arrête.

**CE QUI SE PASSE** :

1. Vous ouvrez Metabase → **Still working!** ✅
2. Vous cliquez sur des rapports → **Les clics sont toujours capturés!** ✅
3. Vous ouvrez RabbitMQ → **Les messages s'accumulent dans la queue!** ✅

**VISUALIZATION** :
```
RabbitMQ Queue Status:
┌──────────────────────────┐
│ Messages Ready: 247      │  ← Tous les logs en attente!
│ Messages Unacked: 0      │
└──────────────────────────┘
```

**CE QUE VOUS DITES** :
"Même si la base de données plante, RabbitMQ garde tous les événements en queue. L'utilisateur ne voit aucune interruption. Regardez maintenant..."

Vous redémarrez PostgreSQL :
```bash
$ docker-compose unpause postgresql
```

**MAGIC MOMENT** :
```
Terminal du Consumer Python :
[INFO] Consumer started
[INFO] Processed 247 logs for user 1, 5, 8, 12, ...
[INFO] Database reconnected
[INFO] Catching up on queue...
[INFO] Successfully processed 247 messages in 2.3s
```

**DANS POSTGRESQL** :
```sql
SELECT COUNT(*) FROM navigation_logs;
 count
-------
 500
(1 row)
```

**VOUS EXPLIQUEZ** :
"Voilà. L'intégrité des données est garantie. Aucun log n'a été perdu. C'est ça, la _résilience_. C'est crucial pour un système en production."

---

### **Scène 4 : Les Résultats** (Minutes 21-25)

Vous montrez les résultats de vos tests :

**TABLEAU A/B TESTING** :
```
╔════════════════════════════════════════════════════════════╗
║                    A/B Testing Results                      ║
╠════════════════════════════════════════════════════════════╣
║ Métrique                    │ Groupe A (sans) │ Groupe B   ║
║━━━━━━━━━━━━━━━━━━━━━━━━━━━━┼━━━━━━━━━━━━━━━━┼━━━━━━━━━━║
║ Rapports consultés/jour     │ 3.2            │ 5.8 ⬆ 81%  ║
║ Temps moyen/session         │ 12 min         │ 18 min ⬆   ║
║ CTR (Click-Through Rate)    │ N/A            │ 42% ✅     ║
║ Utilisateurs satisfaits     │ 65%            │ 89% ⬆ 37%  ║
╚════════════════════════════════════════════════════════════╝
```

**METRICS DE PERFORMANCE** :
```
API Response Time: < 50ms (p99)
Data Pipeline Latency: < 2s
Model Accuracy (Precision@3): 0.78
System Uptime: 99.98% (même avec crash simulé)
```

---

### **Questions Typiques du Jury** (Minutes 26-30)

**Q1 : "Pourquoi RabbitMQ et pas simplement écrire directement dans la base ?"**
R : "RabbitMQ nous permet de découpler Metabase du stockage. Si la base crash, Metabase continue à fonctionner. C'est l'asynchrone qui garantit la résilience."

**Q2 : "Comment ça marche si deux utilisateurs ont le même nom ?"**
R : "On utilise l'ID unique de Metabase, pas le nom. Chaque utilisateur est identifié de manière unique."

**Q3 : "Pourquoi hybrid et pas seulement collaboratif ?"**
R : "Le collaboratif est bon pour les utilisateurs avec beaucoup d'historique, mais le content-based fonctionne mieux pour les nouveaux utilisateurs (cold-start problem)."

**Q4 : "Combien de temps ça prend d'entraîner le modèle ?"**
R : "En batch, c'est ~2-3 secondes pour 500 utilisateurs et 200 rapports. On peut ré-entraîner quotidiennement sans problème."

**Q5 : "Comment vous mesurez la qualité des recommandations ?"**
R : "Principalement par CTR (Click-Through Rate) en A/B testing, et par métriques de précision/recall sur un set de validation."

---

### 🎨 **L'Impression Finale Laissée au Jury**

À la fin, le jury voit un système :

✅ **Complet** : De la capture du log jusqu'à l'affichage dans l'interface  
✅ **Robuste** : Résilience démontrée en temps réel  
✅ **Intelligent** : Modèles ML sophistiqués mais bien expliqués  
✅ **Moderne** : Architecture microservices avec Docker, CI/CD  
✅ **Mesuré** : A/B testing et métriques concrets  
✅ **Bien présenté** : Vous semblez maîtriser chaque ligne de code

---

## 📊 RÉSUMÉ VISUEL DE LA ROADMAP

```
SEMAINE 1
├─ Setup GitHub, Docker
├─ docker-compose up
├─ Metabase running
└─ 20 dashboards fictifs

SEMAINE 2-3
├─ Data tracking (Metabase → RabbitMQ)
├─ Consumer Python
├─ PostgreSQL populated
└─ End-to-end test

SEMAINE 4
├─ Modèle Collaboratif
├─ Modèle Content-based
├─ Hybrid function
└─ Models saved

SEMAINE 5
├─ FastAPI running
├─ Metabase integration
├─ Recommendations visible
└─ API tested

SEMAINE 6
├─ CI/CD pipeline
├─ Résilience (crash test)
├─ A/B Testing setup
└─ Code documentation

SEMAINE 6 (fin)
├─ Rapport écrit
├─ Slides préparées
├─ Démo scriptée
└─ Prêt pour soutenance! 🚀
```

---

## ✅ CHECKLIST FINALE

Avant la soutenance, vérifiez :

- [ ] Git repository avec bon README
- [ ] `docker-compose up` lance tout sans erreurs
- [ ] Metabase accessible avec données fictives
- [ ] RabbitMQ reçoit des messages (visible dans admin)
- [ ] PostgreSQL a des logs (SELECT COUNT(*))
- [ ] API retourne les recommandations (test curl)
- [ ] Dashboard Metabase montre les recommendations
- [ ] Panne simulée fonctionne et résilience prouvée
- [ ] Rapport écrit (20-30 pages) complété
- [ ] Slides prêtes (12-15 slides)
- [ ] Code commenté et documenté
- [ ] Démo scriptée et répétée

---

## 🏆 DIFFÉRENCIATEURS POUR EXCELLENTE NOTE

Si vous faites UNE SEULE de ces choses en plus :

1. **Contextual Bandits** : Montre une compréhension avancée du ML
2. **Dashboard esthétique** : Bonne UI/UX
3. **CI/CD sophistiqué** : Montre maîtrise DevOps
4. **Résultats A/B spectaculaires** : Impact business clair
5. **Documentation exceptionnelle** : Code readable et guide complet

---

**C'est maintenant à vous de coder! Bonne chance! 🚀**
