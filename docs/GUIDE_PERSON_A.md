# 🧠 GUIDE COMPLET - PERSONNE A (Data & AI Engineer)

> **Tout ce que vous devez savoir pour exceller dans votre rôle**

---

## 👤 VOTRE PROFIL

**Titre**: Data & AI Engineer  
**Focus**: Machine Learning et Recommandations  
**Heures estimées**: 36 heures  
**Compétences requises**: Python, ML, Data Analysis  

**Responsabilités principales**:
- Exploration et compréhension des données
- Création des modèles de recommandation
- Développement de l'API REST
- A/B Testing et évaluation

---

## 📚 FONDAMENTAUX QUE VOUS DEVEZ COMPRENDRE

### 1. Qu'est-ce qu'un Système de Recommandation?

**Définition simple**:
Un système qui prédit ce qu'un utilisateur va aimer basé sur:
- Ce qu'il a aimé avant (son historique)
- Ce que les autres utilisateurs similaires ont aimé
- Similarité entre les produits/rapports

**Exemple concret - Netflix**:
```
Vous regardez "Breaking Bad" (Drama)
  ↓
Netflix analyse: "Cet utilisateur aime les dramas"
  ↓
Netflix cherche: "Quels autres dramas existent?"
  ↓
Netflix recommande: "You", "The Crown", etc.
```

**Dans notre projet - BI Adaptative**:
```
Utilisateur clique sur "Rapport Ventes par Région"
  ↓
Notre système analyse: "Cette personne aime les rapports de ventes"
  ↓
Notre système cherche: "Quels autres rapports de ventes existent?"
  ↓
Notre système recommande: "Prévisions Q2", "Top Clients", etc.
```

---

### 2. Les 2 Approches de Recommandation

#### 🔵 APPROCHE 1: Filtrage Collaboratif (Collaborative Filtering)

**Principe**: "Les gens qui aiment les mêmes choses s'aiment"

**Comment ça marche**:
```
Utilisateur A aime: Rapport Sales, Rapport Revenue, Rapport Clients
Utilisateur B aime: Rapport Sales, Rapport Revenue, Rapport Expenses

Observation: A et B ont des goûts similaires (2/3 rapports identiques)
↓
Action: Si B aime "Rapport Expenses", alors A va probablement l'aimer aussi!
↓
Recommandation à A: "Rapport Expenses"
```

**Mathématiquement**:
- Créer une **matrice utilisateur-rapport**
- Chaque cellule = "score" (combien de temps l'utilisateur a passé sur ce rapport)
- Calculer la **similarité** entre utilisateurs
- Recommander ce que les utilisateurs similaires ont aimé

**Avantages**:
✅ Découvre des rapports non-évidentes  
✅ Fonctionne bien avec beaucoup d'utilisateurs  
✅ Pas besoin de savoir le contenu du rapport  

**Inconvénients**:
❌ Problème du "Cold Start" (nouvel utilisateur = pas d'historique)  
❌ Problème du "Cold Start" (nouveau rapport = personne ne l'a vu)  

**Bibliothèque Python**: `Surprise` (spécialisée là-dedans)

---

#### 🟢 APPROCHE 2: Filtrage Basé sur le Contenu (Content-Based)

**Principe**: "Si tu aimais les dramas, tu aimeras aussi les autres dramas"

**Comment ça marche**:
```
Utilisateur aime: "Rapport Sales par Région"
  ↓
Analyse du rapport: Mots clés = ["Sales", "Région", "Ventes"]
  ↓
Cherche d'autres rapports avec les mêmes mots clés
  ↓
Recommande: "Rapport Sales par Pays", "Rapport Ventes Mensuelles"
```

**Mathématiquement**:
- Extraire les **caractéristiques** de chaque rapport (titre, description, tags)
- Créer des **vecteurs de features** (représentation numérique)
- Calculer la **similarité** entre rapports (combien de features communs?)
- Recommander les rapports similaires à ceux qu'il a aimés

**Avantages**:
✅ Pas de problème du "Cold Start" (fonctionne même pour nouveaux rapports)  
✅ Expliquable ("Vous aimez Sales, voici d'autres Sales")  

**Inconvénients**:
❌ Recommande des choses trop similaires (pas de découverte)  
❌ Besoin de bonne description des rapports  

**Bibliothèque Python**: `scikit-learn` (TF-IDF, Cosine Similarity)

---

#### 🟣 APPROCHE 3: Hybride (Ce que vous ferez)

**Principe**: Combiner les avantages des 2 approches

**Comment ça marche**:
```
Score Final = (0.6 × Score Collaboratif) + (0.4 × Score Contenu)
                   ↑                            ↑
              60% confiance              40% confiance
```

**Avantages**:
✅ Découvre de choses grâce au collaboratif  
✅ Pas de cold-start grâce au contenu  
✅ Expliquable grâce à la transparence  

---

## 🗺️ VOTRE ROADMAP COMPLÈTE

### PHASE 1: Infrastructure (Semaine 1) - 1 heure

**Votre rôle**: Très minime cette semaine

**Tâche 1.4**: Peupler Metabase avec 15-20 rapports fictifs

**Pourquoi**:
- Vous avez besoin de données pour tester les modèles
- Les rapports fictifs simulent les données réelles
- C'est la "source d'entraînement" pour votre IA

**Comment**:
```
Metabase UI → Créer une Question → SQL Query
Exemple: SELECT customer_name, SUM(amount) FROM orders GROUP BY customer_name

Sauvegarder → Ajouter au Dashboard
```

**Besoin de connaître**:
- Comprendre le Sample Database de Metabase
- Écrire des requêtes SQL basiques (SELECT, GROUP BY, WHERE)
- Naviguer l'interface Metabase

**Ressources**:
- SQL tutorial: https://www.w3schools.com/sql/
- Metabase docs: https://www.metabase.com/docs

---

### PHASE 3: Data Pipeline (Semaines 2-3) - 3 heures

**Votre rôle**: Préparation des données + validation

#### Tâche 3.1: Exploration et Préparation des Données

**Qu'est-ce que c'est**?
Avant d'entraîner votre modèle, vous devez comprendre vos données.

**Qu'est-ce que vous devez faire**?
```
1. Charger les données de PostgreSQL
2. Analyser leur structure
3. Vérifier leur qualité
4. Créer la matrice utilisateur-rapport
```

**Code que vous exécuterez**:
```python
import pandas as pd
import psycopg2

# 1. CHARGER LES DONNÉES
conn = psycopg2.connect(...)
df = pd.read_sql("SELECT user_id, report_id, duration FROM navigation_logs", conn)

# 2. ANALYSER LA STRUCTURE
print(df.head())       # Voir les 5 premières lignes
print(df.info())       # Types de données
print(df.describe())   # Statistiques

# 3. VÉRIFIER LA QUALITÉ
print(df.isnull().sum())  # Valeurs manquantes?
print(df.duplicated())    # Doublons?

# 4. CRÉER LA MATRICE
matrix = df.pivot_table(
    index='user_id',           # Lignes = utilisateurs
    columns='report_id',       # Colonnes = rapports
    values='duration',         # Valeurs = durée visualisation
    fill_value=0               # Compléter avec 0 si absent
)
# Résultat: Matrice de 100x50 (100 utilisateurs, 50 rapports)
```

**Qu'est-ce que vous apprendrez**?
- Comment charger les données depuis une base de données
- Pandas pour manipuler les données
- Comprendre les distributions des données
- Préparer les données pour le ML (nettoyage)

**Pourquoi c'est important**?
- Les données sales → Les modèles meilleures
- Données mal préparées → Recommandations mauvaises
- C'est 80% du travail en ML!

**Validation**:
```bash
# À la fin, vous devez avoir:
✅ DataFrames chargés sans erreurs
✅ Compris le nombre d'utilisateurs et rapports
✅ Trouvé les données manquantes/bizarres
✅ Créé la matrice utilisateur-rapport
```

---

### PHASE 4: Machine Learning (Semaines 3-4) - 16 heures

**Votre rôle**: C'est VOTRE PHASE - 100% votre responsabilité

**Environ 4 heures par semaine**

#### Tâche 4.2: Modèle Collaboratif Filtering (4 heures)

**Qu'est-ce que c'est**?

Un algorithme qui apprend les **préférences latentes** des utilisateurs.

**Exemple simplifié**:
```
Supposons que chaque utilisateur a une "signature" invisible:
- Utilisateur A: [Aime Sales: 0.9, Aime HR: 0.1, Aime Inventory: 0.7]
- Utilisateur B: [Aime Sales: 0.8, Aime HR: 0.2, Aime Inventory: 0.8]

Et chaque rapport a aussi une signature:
- Rapport Sales: [C'est un rapport Sales: 0.95, C'est HR: 0.05]
- Rapport Inventory: [C'est Sales: 0.2, C'est Inventory: 0.9]

Prédiction = Multiplier les signatures!
Score pour A × Rapport Inventory = 0.9×0.2 + 0.1×0.05 + 0.7×0.9 = ...
```

**Algorithme utilisé**: SVD (Singular Value Decomposition)

**Code simplifié**:
```python
from surprise import SVD, Dataset, Reader

# 1. PRÉPARER LES DONNÉES
reader = Reader(rating_scale=(0, 100))  # Les durées vont de 0 à 100
data = Dataset.load_from_df(
    df[['user_id', 'report_id', 'duration']],  # Données
    reader
)

# 2. DIVISER TRAIN/TEST (80/20)
trainset, testset = train_test_split(data, test_size=0.2)

# 3. ENTRAÎNER LE MODÈLE
model = SVD(n_factors=50)  # 50 "signatures latentes"
model.fit(trainset)

# 4. ÉVALUER LE MODÈLE
predictions = model.test(testset)
rmse = accuracy.rmse(predictions)  # Erreur moyenne
print(f"RMSE: {rmse:.4f}")

# 5. FAIRE UNE PRÉDICTION
pred = model.predict(user_id=1, report_id=42)
print(f"Score pour user 1, report 42: {pred.est}")  # Entre 0 et 100
```

**Qu'est-ce que vous apprendrez**?
- Comment fonctionne SVD (mathématiquement)
- Comment entraîner un modèle ML
- Comment diviser les données (train/test)
- Comment évaluer un modèle (RMSE, MAE)
- Librarie Surprise

**Hyperparamètres importants**:
```python
SVD(
    n_factors=50,      # Nombre de "signatures" (plus = plus complexe)
    n_epochs=20,       # Combien de fois voir les données
    lr_all=0.005,      # Learning rate (comment rapidement apprendre?)
    reg_all=0.02       # Regularization (éviter overfitting)
)
```

**Validation**:
```bash
✅ Modèle entraîné sans erreurs
✅ RMSE < 0.3 (bon score)
✅ Prédictions réalistes (entre 0-100)
✅ Modèle sauvegardé en pickle
```

**Ressources**:
- Surprise docs: http://surpriselib.com/
- SVD explanation: https://en.wikipedia.org/wiki/Singular_value_decomposition

---

#### Tâche 4.3: Modèle Content-Based (3 heures)

**Qu'est-ce que c'est**?

Analyser le **texte** des rapports (titre, description, tags) et recommander les similaires.

**Exemple**:
```
Rapport 1: "Sales Analysis by Region"
Rapport 2: "Sales Forecast by Region"
Rapport 3: "HR Statistics by Department"

Rapport 1 et 2 ont beaucoup de mots en commun ("Sales", "Region")
→ Similarité = 0.85

Rapport 1 et 3 n'ont pas grand chose en commun
→ Similarité = 0.15
```

**Algorithme utilisé**: TF-IDF + Cosine Similarity

**Explication simple**:
```
TF-IDF = "Term Frequency - Inverse Document Frequency"
- TF: Combien de fois un mot apparaît dans le document?
- IDF: Combien de documents contiennent ce mot? (si beaucoup = moins important)

Cosine Similarity = Angle entre deux vecteurs
- 1.0 = Identical (angle 0°)
- 0.5 = Partiellement similaire
- 0.0 = Complètement différent
```

**Code simplifié**:
```python
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# 1. CHARGER LE TEXTE DES RAPPORTS
reports_df = pd.read_sql(
    "SELECT id, title, description, tags FROM reports",
    conn
)

# 2. CRÉER LES VECTEURS TF-IDF
text_features = (
    reports_df['title'] + ' ' +
    reports_df['description'] + ' ' +
    reports_df['tags']
)

vectorizer = TfidfVectorizer(
    max_features=100,        # Maximum 100 mots uniques
    stop_words='english',    # Ignorer "the", "a", "is"
    ngram_range=(1, 2)       # Mots simples et paires
)
tfidf_matrix = vectorizer.fit_transform(text_features)
# Résultat: Matrice 50×100 (50 rapports, 100 features)

# 3. CALCULER LA SIMILARITÉ
similarity_matrix = cosine_similarity(tfidf_matrix)
# Résultat: Matrice 50×50 (similitude entre tous les rapports)

# 4. RECOMMANDER
def recommend_similar(report_id, n=3):
    similarities = similarity_matrix[report_id]
    similar_ids = np.argsort(-similarities)[1:n+1]  # Top N (excluant lui-même)
    return similar_ids

# Exemple
similar = recommend_similar(report_id=0, n=3)
# Résultat: [5, 12, 18] (les 3 rapports les plus similaires)
```

**Qu'est-ce que vous apprendrez**?
- Traitement du texte (text preprocessing)
- TF-IDF (important concept en NLP)
- Cosine similarity
- scikit-learn

**Validation**:
```bash
✅ Vecteurs TF-IDF créés
✅ Matrice similarité créée
✅ Recommandations sensées (vérifier manuellement)
✅ Modèle sauvegardé
```

**Ressources**:
- TF-IDF explanation: https://en.wikipedia.org/wiki/Tf%E2%80%93idf
- scikit-learn: https://scikit-learn.org/

---

#### Tâche 4.4: Modèle Hybride (4 heures)

**Qu'est-ce que c'est**?

Combiner les 2 modèles pour une meilleure prédiction.

**Mathématiquement**:
```
Score Final = α × Score Collaboratif + (1-α) × Score Content-Based

Où α = poids (0 à 1)
- α = 0.6 signifie: 60% confiance au collaboratif, 40% au contenu
```

**Pourquoi?**
```
Collaboratif seul:
  ✅ Bonne découverte
  ❌ Problème cold-start (nouveaux utilisateurs/rapports)

Content-based seul:
  ✅ Pas de cold-start
  ❌ Recommande trop similaire (pas de découverte)

Hybride:
  ✅ Découverte + pas de cold-start + expliquabilité!
```

**Code simplifié**:
```python
def get_hybrid_recommendations(user_id, alpha=0.6, n=3):
    """
    alpha: 0.6 = 60% collaboratif, 40% contenu
    """
    
    # 1. RECOMMANDATIONS COLLABORATIVES
    cf_scores = {}
    for report_id in all_reports:
        pred = model_cf.predict(user_id, report_id)
        cf_scores[report_id] = pred.est / 100  # Normaliser 0-1
    
    # 2. RECOMMANDATIONS CONTENU
    # Supposons utilisateur a vu les rapports [1, 5, 12]
    viewed_reports = [1, 5, 12]
    cb_scores = {}
    
    for report_id in all_reports:
        if report_id not in viewed_reports:
            # Moyenne similarité avec rapports vus
            similarities = [
                similarity_matrix[report_id][seen]
                for seen in viewed_reports
            ]
            cb_scores[report_id] = np.mean(similarities)
    
    # 3. COMBINER
    hybrid_scores = {}
    for report_id in all_reports:
        if report_id not in viewed_reports:
            score = (alpha * cf_scores.get(report_id, 0) +
                    (1 - alpha) * cb_scores.get(report_id, 0))
            hybrid_scores[report_id] = score
    
    # 4. RETOURNER TOP N
    top_recs = sorted(hybrid_scores.items(), key=lambda x: x[1], reverse=True)
    return [rid for rid, _ in top_recs[:n]]

# Utilisation
recs = get_hybrid_recommendations(user_id=1, alpha=0.6, n=5)
# Résultat: [42, 15, 8, 33, 50]
```

**Validation**:
```bash
✅ Modèle hybride fonctionne
✅ Poids α testés (0.4, 0.5, 0.6, 0.7)
✅ Résultats sensés
✅ Modèle sauvegardé
```

---

#### Tâche 4.5: Pipeline d'Entraînement (2 heures)

**Qu'est-ce que c'est**?

Un script unique qui entraîne tous les modèles en séquence.

**Pourquoi**?
- Vous entraînerez le modèle plusieurs fois
- Besoin d'un processus reproductible
- Documenter l'entraînement

**Code**:
```python
#!/usr/bin/env python3
"""
Training Pipeline for ML Models
"""

def main():
    # Step 1: Data Preparation
    logger.info("[1/4] Preparing data...")
    prep = DataPreparation()
    prep.connect()
    df = prep.load_data()
    prep.explore_data(df)
    
    # Step 2: Train Collaborative Filtering
    logger.info("[2/4] Training Collaborative Filtering...")
    cf = CollaborativeFiltering()
    data = cf.load_data()
    cf.train(data)
    cf.save_model()
    
    # Step 3: Train Content-Based
    logger.info("[3/4] Training Content-Based...")
    cb = ContentBasedFiltering()
    cb.train()
    cb.save_models()
    
    # Step 4: Create Hybrid
    logger.info("[4/4] Creating Hybrid...")
    hybrid = HybridRecommender(alpha=0.6)
    hybrid.train()
    
    logger.info("Training complete!")

if __name__ == '__main__':
    main()
```

**Utilisation**:
```bash
python backend/ml_engine/train.py
# Output:
# [1/4] Preparing data...
# [2/4] Training Collaborative Filtering...
# RMSE: 0.25
# [3/4] Training Content-Based...
# [4/4] Creating Hybrid...
# Training complete!
```

---

### PHASE 5: API & Intégration (Semaines 4-5) - 4 heures

**Votre rôle**: Créer l'API REST

#### Tâche 5.1: API REST FastAPI (4 heures)

**Qu'est-ce qu'une API REST?**

Un service web que les autres applications peuvent interroger.

**Exemple**:
```
Client (Metabase) demande: "Donne-moi les 3 meilleurs rapports pour user 1"
  ↓
API reçoit la requête
  ↓
API charge les modèles ML
  ↓
API exécute: get_hybrid_recommendations(user_id=1, n=3)
  ↓
API retourne: [{"report_id": 42, "score": 0.92}, ...]
  ↓
Metabase affiche les recommandations
```

**Qu'est-ce que FastAPI?**

Un framework Python pour créer des APIs REST rapidement avec validation automatique.

**Code complet**:
```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List

app = FastAPI(title="BI Adaptive Recommendation API")

# Charger les modèles au démarrage
recommender = None

@app.on_event("startup")
async def startup():
    global recommender
    recommender = HybridRecommender(alpha=0.6)
    # Charger modèles sauvegardés
    recommender.load_models()

# ============ SCHEMAS (Validation) ============

class RecommendationRequest(BaseModel):
    user_id: int          # ID de l'utilisateur
    n_recommendations: int = 3  # Nombre de recommandations (défaut 3)
    alpha: float = 0.6    # Poids du collaboratif (défaut 0.6)

class RecommendationResponse(BaseModel):
    user_id: int
    recommendations: List[dict]

# ============ ENDPOINTS ============

@app.get("/health")
async def health_check():
    """Vérifier que l'API fonctionne"""
    return {
        "status": "ok",
        "service": "BI Adaptive Recommendation API"
    }

@app.post("/recommendations", response_model=RecommendationResponse)
async def get_recommendations(request: RecommendationRequest):
    """
    Endpoint principal pour obtenir les recommandations
    
    Exemple d'utilisation:
    POST /recommendations
    {
        "user_id": 1,
        "n_recommendations": 5,
        "alpha": 0.6
    }
    
    Réponse:
    {
        "user_id": 1,
        "recommendations": [
            {"report_id": 42, "score": 0.92, "algorithm": "hybrid"},
            ...
        ]
    }
    """
    
    try:
        if not recommender:
            raise HTTPException(status_code=503, detail="Models not loaded")
        
        # Validation
        if request.user_id < 1:
            raise HTTPException(status_code=400, detail="user_id must be >= 1")
        if request.n_recommendations < 1:
            raise HTTPException(status_code=400, detail="n_recommendations must be >= 1")
        if not (0 <= request.alpha <= 1):
            raise HTTPException(status_code=400, detail="alpha must be 0-1")
        
        # Obtenir les recommandations
        recs = recommender.get_recommendations(
            user_id=request.user_id,
            n_recommendations=request.n_recommendations,
            alpha=request.alpha
        )
        
        return RecommendationResponse(
            user_id=request.user_id,
            recommendations=[
                {
                    "report_id": int(rec['report_id']),
                    "score": float(rec['score']),
                    "algorithm": rec['algorithm']
                }
                for rec in recs
            ]
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='0.0.0.0', port=8000)
```

**Comment tester l'API**:
```bash
# Lancer l'API
python backend/api/main.py

# Dans un autre terminal, tester
curl -X POST "http://localhost:8000/recommendations" \
  -H "Content-Type: application/json" \
  -d '{"user_id": 1, "n_recommendations": 3}'

# Résultat:
# {
#   "user_id": 1,
#   "recommendations": [
#     {"report_id": 42, "score": 0.92, "algorithm": "hybrid"},
#     ...
#   ]
# }
```

**Qu'est-ce que vous apprendrez?**
- Créer des APIs REST avec FastAPI
- Pydantic pour validation
- HTTP status codes
- Documentation auto (Swagger)

**Ressources**:
- FastAPI: https://fastapi.tiangolo.com/
- REST API basics: https://www.restapitutorial.com/

---

### PHASE 6: Tests & Avancé (Semaines 5-6) - 6 heures

**Votre rôle**: Amélioration et évaluation

#### Tâche 6.2: Contextual Bandits (OPTIONNEL, 3 heures)

**Qu'est-ce que c'est?**

Un algorithme qui **apprend** des clics réels sur vos recommandations.

**Concept simple**:
```
Vous recommandez 3 rapports à un utilisateur:
[Rapport A, Rapport B, Rapport C]

L'utilisateur clique sur Rapport A:
- Reward = 1 (positif!)
- Le modèle apprend: "Cet utilisateur aime cette recommandation"

L'utilisateur ignore B et C:
- Reward = 0
- Le modèle apprend: "Ces recommandations n'étaient pas bonnes"

La prochaine fois:
- Le modèle recommandera plus de choses comme A
- Moins de choses comme B et C
```

**Avantage**: Le modèle s'améliore avec le temps!

**Bibliothèques possibles**:
- `vowpal_wabbit`
- `mabwiser`

**Conceptuel seulement** (complexe à implémenter):
```python
class ContextualBandits:
    def select(self, user_context, n_arms):
        """Sélectionner n meilleurs rapports avec exploration"""
        # Exploitation: Recommander les meilleurs
        # Exploration: Tester aussi des "mauvais" (pour apprendre)
        pass
    
    def update(self, user_id, report_id, reward):
        """Apprendre du feedback utilisateur"""
        # Reward = 1 si clic, 0 sinon
        # Mettre à jour les poids internes
        pass
```

---

#### Tâche 6.3: A/B Testing (2 heures)

**Qu'est-ce que c'est?**

Comparer deux versions pour voir laquelle fonctionne mieux.

**Design**:
```
Groupe A (50% des utilisateurs):
└─ Pas de recommandations
└─ Métrique: Combien de rapports consultés par jour?
└─ Résultat: Moyenne = 3.2 rapports/jour

Groupe B (50% des utilisateurs):
└─ Avec recommandations
└─ Métrique: Combien de rapports consultés par jour?
└─ Résultat: Moyenne = 5.8 rapports/jour

Conclusion: Recommandations augmentent l'usage de 81%!
```

**Code pour diviser les utilisateurs**:
```python
def should_show_recommendations(user_id):
    """
    Diviser les utilisateurs de façon déterministe
    Utilisateur 1, 3, 5, 7... → Groupe A (sans recs)
    Utilisateur 2, 4, 6, 8... → Groupe B (avec recs)
    """
    return user_id % 2 == 0

# Utilisation
if should_show_recommendations(user_id):
    # Montrer les recommandations
    recs = api.get_recommendations(user_id)
    show_in_ui(recs)
else:
    # Dashboard normal sans recommandations
    show_standard_dashboard()
```

**Métriques à tracker**:
```python
# Pour chaque utilisateur, tracker:
- Nombre de rapports consultés/jour
- Temps moyen par rapport
- Nombre de clics sur recommandations (CTR)
- Satisfaction perçue (si possible demander)

# Après 2-4 semaines, comparer:
- Groupe A vs Groupe B
- T-test statistique pour vérifier si différence significative
```

---

### PHASE 7: Documentation (Semaine 6) - 6 heures

**Votre rôle**: Écrire le rapport technique

**Sections à écrire**:
1. Introduction au ML (1 page)
2. Détail des 3 algorithmes (3 pages)
3. Résultats & performance (2 pages)
4. A/B Testing (1 page)

---

## 🎓 CONCEPTS CLÉS À MAÎTRISER

### Concepts ML Importants

#### Train/Test Split
```python
# Pourquoi?
# Pour éviter qu'un modèle "triche" en se souvenant de tout

# Exemple
data = [interactions 1000]
train = data[:800]  # 80% pour entraîner
test = data[800:]   # 20% pour évaluer
```

#### Overfitting vs Underfitting
```
Underfitting: Modèle trop simple (RMSE mauvais)
  └─ Solution: Plus de données ou modèle plus complexe

Just right: Modèle équilibré (RMSE bon)
  └─ C'est ce qu'on veut!

Overfitting: Modèle mémorise tout (RMSE: parfait sur train, mauvais sur test)
  └─ Solution: Regularization ou moins de features
```

#### RMSE (Root Mean Square Error)
```
RMSE = √(moyenne des (prédictions - réalités)²)

RMSE = 0.1: Excellent (prédictions très précises)
RMSE = 0.3: Bon
RMSE = 0.5: Acceptable
RMSE = 1.0: Mauvais
```

#### Precision@K
```
Si vous recommandez Top 3, combien l'utilisateur aime réellement?

Precision@3 = 0.67 signifie:
  "En moyenne, 2 des 3 recommandations plaisent à l'utilisateur"
```

---

## 📊 DONNÉES QUE VOUS ALLEZ UTILISER

### Table: navigation_logs

```sql
CREATE TABLE navigation_logs (
    id INTEGER PRIMARY KEY,
    user_id INTEGER,
    report_id INTEGER,
    action VARCHAR(50),
    duration INTEGER,  -- Secondes passées
    timestamp TIMESTAMP
);
```

**Exemple de données**:
```
user_id | report_id | duration | timestamp
--------|-----------|----------|-------------------
   1    |    42     |   120    | 2026-05-06 10:30
   1    |    50     |    85    | 2026-05-06 10:35
   2    |    42     |   200    | 2026-05-06 10:40
   2    |    60     |    45    | 2026-05-06 10:50
   ...
```

**Ce que vous apprendrez d'elle**:
- Qui regarde quoi (collaboration)
- Combien de temps ils passent (intérêt)
- Quand ils le regardent (patterns temporels)

### Table: reports

```sql
CREATE TABLE reports (
    id INTEGER PRIMARY KEY,
    metabase_report_id INTEGER,
    title VARCHAR(255),
    description TEXT,
    tags VARCHAR(255),
    category VARCHAR(100)
);
```

**Exemple**:
```
id | title              | description        | tags
---|--------------------|--------------------|----------------
42 | Sales by Region    | Monthly sales...   | sales,region
50 | Revenue Forecast   | Quarterly forecast | forecast,revenue
60 | Inventory Status   | Current inventory  | inventory,stock
```

**Ce qu'elle fournit**:
- Caractéristiques des rapports (pour content-based)
- Tags pour calcul de similarité

---

## ⚙️ OUTILS & COMMANDES ESSENTIELS

### Python & Bibliothèques

```bash
# Installation de votre environnement
pip install pandas numpy scikit-learn surprise fastapi uvicorn psycopg2-binary joblib

# Vérifier les imports dans Python
python3 -c "import pandas; print(pandas.__version__)"
```

### Commandes pour Tester

```bash
# Charger les modèles et tester
python backend/ml_engine/train.py

# Lancer l'API
python backend/api/main.py

# Tester l'API
curl -X POST "http://localhost:8000/recommendations" \
  -H "Content-Type: application/json" \
  -d '{"user_id": 1, "n_recommendations": 3}'
```

### Jupyter Notebook (Optionnel mais Recommandé)

```bash
# Pour explorer vos données interactivement
pip install jupyter
jupyter notebook

# Créer un fichier exploration.ipynb
```

---

## ✅ CHECKLIST PAR PHASE

### Phase 3: Data
- [ ] Données chargées sans erreurs
- [ ] Compris le nombre d'utilisateurs et rapports
- [ ] Matrice créée (shape correct)
- [ ] Pas de NaN ou valeurs bizarres

### Phase 4.2: Collaborative
- [ ] Modèle entraîné avec RMSE < 0.3
- [ ] Prédictions entre 0-100
- [ ] Modèle sauvegardé

### Phase 4.3: Content-Based
- [ ] Vecteurs TF-IDF créés
- [ ] Matrice similarité créée
- [ ] Recommandations sensées (vérifier 3-4 manuellement)
- [ ] Modèle sauvegardé

### Phase 4.4: Hybrid
- [ ] Fonction hybride fonctionne
- [ ] Poids α testés (essayer 0.4, 0.5, 0.6, 0.7)
- [ ] Résultats sensés
- [ ] Modèle sauvegardé

### Phase 4.5: Pipeline
- [ ] Script train.py fonctionne
- [ ] Entraînement complet < 5 minutes
- [ ] Logs clairs et informatifs

### Phase 5.1: API
- [ ] API démarre sans erreurs
- [ ] Health check fonctionne
- [ ] POST /recommendations fonctionne
- [ ] Validation fonctionne (erreurs appropriées)

### Phase 6.2: Bandits
- [ ] Conceptuel compris
- [ ] Implémentation basique (si temps)

### Phase 6.3: A/B Testing
- [ ] Métriques définies
- [ ] Division utilisateurs testée
- [ ] Résultats collectés

---

## 🚨 ERREURS COMMUNES & SOLUTIONS

### Erreur 1: RMSE trop élevé (> 0.5)
**Cause**: Données mauvaises ou paramètres mauvais
**Solution**:
```python
# Vérifier les données
print(df.describe())
print(df.isnull().sum())

# Essayer différents paramètres
SVD(n_factors=30)  # Réduire facteurs
SVD(n_factors=100) # Augmenter facteurs
SVD(n_epochs=50)   # Plus d'entraînement
```

### Erreur 2: "ModuleNotFoundError: No module named 'surprise'"
**Cause**: Bibliothèque pas installée
**Solution**:
```bash
pip install surprise
```

### Erreur 3: "IndexError: list index out of range" lors des prédictions
**Cause**: User ID ou Report ID n'existe pas
**Solution**:
```python
# Vérifier les IDs valides
print(df['user_id'].min(), df['user_id'].max())
print(df['report_id'].min(), df['report_id'].max())

# Ne prédire que pour IDs valides
if user_id in valid_users and report_id in valid_reports:
    pred = model.predict(user_id, report_id)
```

---

## 📚 RESSOURCES SUPPLÉMENTAIRES

### Blogs & Tutoriels
- Recommendation Systems: https://towardsdatascience.com/recommendation-engines-4b4e87aefc6
- Collaborative Filtering: https://en.wikipedia.org/wiki/Collaborative_filtering
- TF-IDF: https://en.wikipedia.org/wiki/Tf%E2%80%93idf

### Livres Recommandés
- "Hands-On Machine Learning" (Aurélien Géron)
- "Introduction to Information Retrieval" (Manning et al.)

### Documentation Officielle
- Surprise: http://surpriselib.com/
- scikit-learn: https://scikit-learn.org/
- FastAPI: https://fastapi.tiangolo.com/
- Pandas: https://pandas.pydata.org/

---

## 🎯 RÉSUMÉ: VOTRE VOYAGE

**Semaine 1**: Découvrez les données (1h)
**Semaines 2-4**: Entraînez les modèles (16h)
**Semaines 4-5**: Exposez via API (4h)
**Semaines 5-6**: Testez & améliorez (6h)
**Semaine 6**: Écrivez le rapport (6h)

**Au final**: Un système qui recommande intelligemment les meilleurs rapports! 🎉

---

**Vous avez un rôle critique. Votre code est le "cerveau" du système!**

**Bonne chance! 🚀**
