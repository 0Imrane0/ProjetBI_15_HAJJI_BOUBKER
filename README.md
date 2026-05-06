# 📊 BI Adaptative – Recommandation Personnalisée de Rapports

> Une plateforme Business Intelligence intelligente qui recommande automatiquement les rapports les plus pertinents à chaque utilisateur via Machine Learning.

[![Status](https://img.shields.io/badge/status-active-brightgreen)]()
[![Python](https://img.shields.io/badge/python-3.9+-blue)]()
[![Docker](https://img.shields.io/badge/docker-compose-blue)]()
[![License](https://img.shields.io/badge/license-MIT-green)]()

---

## 🎯 Vue d'ensemble

**BI Adaptative** résout le problème de **surcharge d'information** (Information Overload) dans les portails Business Intelligence modernes. 

Au lieu de laisser les utilisateurs naviguer dans des centaines de rapports, notre système recommande intelligemment les rapports les plus pertinents en combinant:
- **Filtrage collaboratif** : "Les utilisateurs comme toi aiment aussi..."
- **Filtrage contenu-based** : "Tu aimais ça, voici des rapports similaires..."
- **Approche hybride** : Combinaison optimale des deux approches

### 📈 Impact Attendu
- ⬆️ **+80%** d'utilisation des rapports pertinents
- ⏱️ **-60%** du temps de recherche
- 😊 **+37%** de satisfaction utilisateur

### 🗺️ Vue Complète du Projet

L'image ci-dessous résume tous les composants et interactions du projet:

![Mind Map BI Adaptative](./docs/images/mindmap-complete.png)

*Légende: Mind map complète montrant l'architecture, les technologies, les modèles ML, et l'intégration utilisateur*

---

## 🏗️ Architecture

### Vue d'ensemble du système

```
┌─────────────────────────────────────────────────────────────────┐
│                     UTILISATEUR FINAL                            │
└────────────────────┬────────────────────────────────────────────┘
                     │
          ┌──────────▼──────────┐
          │  METABASE (BI Tool) │  ← Interface + Tracking
          │    (Port 3000)      │
          │  • Dashboards       │
          │  • Audit Logs       │
          │  • Recommendations  │
          └──────────┬──────────┘
                     │
     ┌───────────────┼───────────────┐
     │               │               │
     ▼               ▼               ▼
┌──────────┐  ┌──────────┐  ┌──────────────┐
│RabbitMQ  │  │PostgreSQL│  │Python API    │
│(Queue)   │  │(Storage) │  │(Recommendations)
│Port 5672 │  │Port 5432 │  │Port 8000     │
└──────────┘  └──────────┘  └──────────────┘
     │               │               │
     └───────────────┼───────────────┘
                     │
     ┌───────────────▼───────────────┐
     │   ML Engine (Python)          │
     │  • Surprise (Collaborative)   │
     │  • scikit-learn (Content)     │
     │  • Hybrid Model               │
     └───────────────────────────────┘
```

Notre architecture repose sur 5 couches intégrées:

![Architecture BI Adaptative](./docs/images/architecture-layers.png)

*Architecture en couches: Frontend (Metabase) → Message Broker (RabbitMQ) → Backend (Python Consumer) → Storage (PostgreSQL) → AI Engine (ML Models)*

### Flux de données détaillé

```
1. Utilisateur clique sur rapport dans Metabase
              ↓
2. Metabase capture l'événement (User ID, Report ID, Duration)
              ↓
3. Événement envoyé à RabbitMQ (asynchrone)
              ↓
4. Consumer Python écoute RabbitMQ
              ↓
5. Données nettoyées et insérées dans PostgreSQL
              ↓
6. ML Engine traite les données en batch
              ↓
7. Recommandations générées via API
              ↓
8. Metabase affiche "Rapports recommandés pour vous"
```

Visualisation du flux complet:

![Flux Complet BI Adaptative](./docs/images/full-flow.png)

*Le flux montre chaque composant et comment les données circulent dans le système*

---

## 📋 Composants Clés

### 🔵 Frontend & Tracking (Metabase)
- Interface BI pour les utilisateurs
- Capture des événements : clics, visualisations, durée
- Publication des logs vers RabbitMQ

### 🟠 Message Broker (RabbitMQ)
- Queue asynchrone garantissant la résilience
- Isolation entre composants
- Zero message loss (durabilité)

### 🔧 Data Pipeline (Python Consumer)
- Écoute RabbitMQ en continu
- Nettoyage et transformation des données
- Insertion dans PostgreSQL

### 💾 Storage (PostgreSQL)
- Historique complet d'utilisation
- Structure optimisée pour les requêtes ML
- Indexes pour performances

### 🧠 ML Engine (Python)
- **Surprise**: Filtrage collaboratif
- **scikit-learn**: Filtrage contenu-based
- **Hybrid**: Combinaison optimale

### 🌐 API REST (FastAPI)
- Exposition des recommandations
- Résilience et scalabilité
- Documentation auto (Swagger)

---

## 🛠️ Stack Technologique

| Composant | Technologie | Version | Rôle |
|-----------|-------------|---------|------|
| **BI Platform** | Metabase | 45.0+ | Interface utilisateur + Tracking |
| **Message Broker** | RabbitMQ | 3.12+ | Orchestration asynchrone |
| **Database** | PostgreSQL | 14+ | Stockage des historiques |
| **Backend ML** | Python | 3.9+ | Moteur de recommandation |
| **ML Libraries** | Surprise + scikit-learn | 0.1.3+ / 1.0+ | Algorithmes de recommandation |
| **API Framework** | FastAPI | 0.95+ | Exposition des recommandations |
| **Containerization** | Docker + Compose | 20.0+ | Orchestration |
| **CI/CD** | GitHub Actions | - | Automatisation |
| **VCS** | Git + GitHub | - | Version control |

---

## 📋 Prérequis

### Installation locale
```bash
# Prérequis système
- Docker 20.0+
- Docker Compose 2.0+
- Python 3.9+ (pour développement)
- Git

# Vérifier les versions
docker --version
docker-compose --version
python --version
```

### Ports requis
```
- 3000   : Metabase
- 5672   : RabbitMQ (AMQP)
- 15672  : RabbitMQ Management Console
- 5432   : PostgreSQL
- 8000   : API Python
```

---

## 🚀 Démarrage Rapide

### 1. Cloner le repository

```bash
git clone https://github.com/0imrane0/bi-adaptative.git
cd bi-adaptative
```

### 2. Créer l'environnement

```bash
# Copier l'exemple de configuration
cp .env.example .env

# Vérifier les variables d'environnement
cat .env
```

### 3. Lancer les services

```bash
# Démarrer tous les containers
docker-compose up -d

# Vérifier que tout fonctionne
docker-compose ps

# Voir les logs
docker-compose logs -f metabase
```

### 4. Initialiser Metabase

```
Accéder à: http://localhost:3000

Suivre le setup wizard:
1. Créer un compte administrateur
2. Connecter la Sample Database
3. Créer 15-20 dashboards fictifs
```

### 5. Tester le pipeline

```bash
# Vérifier RabbitMQ
# URL: http://localhost:15672 (guest/guest)

# Ouvrir quelques rapports dans Metabase
# → Les logs doivent apparaître dans RabbitMQ

# Vérifier PostgreSQL
docker-compose exec postgresql psql -U aibi_user -d bi_adaptive -c "SELECT COUNT(*) FROM navigation_logs;"
```

---

## 📂 Structure du Projet

```
bi-adaptative/
├── docker-compose.yml              # Orchestration des services
├── .env.example                    # Variables d'environnement
├── .gitignore
├── README.md                       # Ce fichier
├── ROADMAP.md                      # Roadmap détaillée (24 tâches)
├── ARCHITECTURE.md                 # Documentation architecture
├── DETAILED_ROADMAP_2PERSONS.md   # Plan pour 2 développeurs
│
├── backend/                        # Backend Python
│   ├── consumer/                   # Consumer RabbitMQ
│   │   ├── __init__.py
│   │   ├── consumer.py            # Script principal
│   │   ├── config.py              # Configuration
│   │   └── requirements.txt
│   │
│   ├── publisher/                  # Publisher Metabase → RabbitMQ
│   │   ├── __init__.py
│   │   ├── publisher.py           # Script principal
│   │   └── requirements.txt
│   │
│   ├── ml_engine/                  # Moteur IA/ML
│   │   ├── __init__.py
│   │   ├── data_preparation.py    # Exploration données
│   │   ├── collaborative.py       # Filtrage collaboratif
│   │   ├── content_based.py       # Filtrage contenu
│   │   ├── hybrid.py              # Modèle hybride
│   │   ├── train.py               # Pipeline d'entraînement
│   │   ├── models/                # Modèles sauvegardés
│   │   └── requirements.txt
│   │
│   ├── api/                        # API REST FastAPI
│   │   ├── __init__.py
│   │   ├── main.py                # Application FastAPI
│   │   ├── schemas.py             # Pydantic models
│   │   └── requirements.txt
│   │
│   └── Dockerfile                  # Image Docker Python
│
├── db/                             # Database
│   ├── init.sql                   # Initialisation DB
│   └── migrations/                # Migrations SQL
│
├── scripts/                        # Scripts utilitaires
│   ├── setup_metabase.py          # Setup initial
│   ├── simulate_load.py           # Génération de trafic
│   └── test_pipeline.py           # Test E2E
│
├── docs/                           # Documentation
│   ├── API.md                      # Documentation API
│   ├── DEPLOYMENT.md               # Guide déploiement
│   └── TROUBLESHOOTING.md          # Dépannage
│
├── tests/                          # Tests
│   ├── test_consumer.py
│   ├── test_recommender.py
│   └── test_api.py
│
└── .github/
    └── workflows/
        └── ci.yml                  # Pipeline CI/CD
```

---

## 👥 Division des Rôles:

### 🧠 **Personne A : Data & AI Engineer**
**Focus**: Moteur de recommandation et ML

**Responsabilités**:
- ✅ Exploration et préparation des données
- ✅ Modèle Collaborative Filtering (Surprise)
- ✅ Modèle Content-based (scikit-learn)
- ✅ Approche Hybride
- ✅ API REST (FastAPI)
- ✅ A/B Testing et évaluation

**Skills**: Python, ML, Pandas, Scikit-learn, Surprise, FastAPI

---

### 🔧 **Personne B : Backend & System Integration Engineer**
**Focus**: Infrastructure, intégration et DevOps

**Responsabilités**:
- ✅ Docker & docker-compose
- ✅ RabbitMQ configuration
- ✅ Consumer Python (traitement des événements)
- ✅ PostgreSQL schema et queries
- ✅ Modification Metabase (API et UI)
- ✅ CI/CD pipeline (GitHub Actions)
- ✅ Test de résilience

**Skills**: Docker, Python, SQL, DevOps, Metabase API, GitHub Actions

---

## 🧪 Tests

### Test du pipeline complet

```bash
# 1. Vérifier que les services démarrent
docker-compose up -d
docker-compose ps

# 2. Accéder à Metabase et ouvrir des rapports
# URL: http://localhost:3000

# 3. Vérifier RabbitMQ
# URL: http://localhost:15672
# Les messages doivent s'accumuler dans 'navigation_logs'

# 4. Lancer le consumer
docker-compose logs -f python-consumer

# 5. Vérifier PostgreSQL
docker-compose exec postgresql psql -U aibi_user -d bi_adaptive
> SELECT COUNT(*) FROM navigation_logs;
> SELECT * FROM navigation_logs LIMIT 5;

# 6. Tester l'API
curl -X POST "http://localhost:8000/recommendations" \
  -H "Content-Type: application/json" \
  -d '{"user_id": 1, "n_recommendations": 3}'
```

### Test de résilience

```bash
# Simuler un crash de PostgreSQL
docker-compose pause postgresql

# Continuer à générer du trafic dans Metabase
# Les messages s'accumulent dans RabbitMQ

# Restaurer PostgreSQL
docker-compose unpause postgresql

# Le consumer reprend automatiquement
# Vérifier que zéro données n'ont été perdues
docker-compose exec postgresql psql -U aibi_user -d bi_adaptive
> SELECT COUNT(*) FROM navigation_logs;
```

---

## 📖 Documentation

- **[ROADMAP.md](./ROADMAP.md)** : Plan détaillé avec 24 tâches
- **[ARCHITECTURE.md](./ARCHITECTURE.md)** : Documentation architecture
- **[API.md](./docs/API.md)** : Documentation API
- **[DEPLOYMENT.md](./docs/DEPLOYMENT.md)** : Guide déploiement
- **[TROUBLESHOOTING.md](./docs/TROUBLESHOOTING.md)** : Dépannage

---

## 🎯 Objectifs & Critères

### Objectifs Techniques

| Objectif | Poids | Description |
|----------|-------|-------------|
| **Réalisation Technique** | 40% | Pipeline complet, code quality, architecture |
| **Qualité BI & Visualisation** | 30% | Intégration Metabase, UX, présentation |
| **Originalité/Complexité** | 20% | Bandits contextuels, A/B testing |
| **Documentation** | 10% | Rapport, README, schémas |

### Points clés de succès

✅ **Pipeline asynchrone** robuste (Metabase → RabbitMQ → PostgreSQL)  
✅ **Modèles ML** précis et justifiés  
✅ **Résilience** démontrée (crash, recovery)  
✅ **UX** claire et intuitive  
✅ **Documentation** complète et professionnelle  
✅ **CI/CD** fonctionnel et automatisé  

---

## 🚨 Résolution de Problèmes

### Le consumer ne reçoit pas de messages RabbitMQ

```bash
# Vérifier que RabbitMQ est actif
docker-compose ps rabbitmq

# Vérifier les connexions
docker-compose logs rabbitmq

# Vérifier la queue existe
docker-compose exec rabbitmq rabbitmqctl list_queues
```

### Metabase ne se connecte pas à PostgreSQL

```bash
# Vérifier les credentials dans .env
# Vérifier que PostgreSQL est actif
docker-compose logs postgresql

# Redémarrer les services
docker-compose restart
```

### API retourne une erreur 500

```bash
# Vérifier les logs de l'API
docker-compose logs python-api

# Vérifier que les modèles sont chargés
ls -la backend/ml_engine/models/
```

---

## 📊 Métriques de Performance

### Cibles à atteindre

```
API Response Time: < 100ms (p99)
Data Pipeline Latency: < 5s (end-to-end)
Model Accuracy: Precision@3 > 0.75
System Uptime: > 99.5%
Message Loss: 0%
```

### Monitoring

```bash
# Afficher les métriques en temps réel
docker-compose logs -f python-api | grep "latency\|response_time"

# Compter les messages dans RabbitMQ
docker-compose exec rabbitmq rabbitmqctl list_queues name messages
```

---

## 🔐 Sécurité

- **RabbitMQ**: Credentials par défaut (guest/guest) → Changer en production
- **PostgreSQL**: Credentials en .env → Utiliser secrets en prod
- **API**: Pas d'authentification → Implémenter JWT/OAuth en prod
- **Metabase**: Setup wizard → Configurer correctement

---

## 🤝 Contribution

### Workflow Git

```bash
# 1. Créer une branche par phase/feature
git checkout -b feature/phase-1-setup

# 2. Committer régulièrement
git add .
git commit -m "Phase 1: Docker setup completed"

# 3. Pousser avant de passer à la suite
git push origin feature/phase-1-setup

# 4. Merger dans main une fois testée
git checkout main
git merge feature/phase-1-setup
```

### Code Style

- **Python**: PEP 8 (utiliser `flake8`)
- **Commits**: Messages clairs en anglais/français
- **Documentation**: Docstrings pour chaque fonction
- **Tests**: Minimal 80% de coverage

---

## 📝 Licence

MIT License - voir [LICENSE](./LICENSE)

---

## 📞 Support

### Pour des questions sur le projet

1. **Vérifier la documentation** : ROADMAP.md, ARCHITECTURE.md,
2. **Vérifier TROUBLESHOOTING.md** : Solution rapide

### Issues et Pull Requests

- Créer une issue pour signaler un problème
- Créer une PR pour proposer une solution
- Titres clairs et descriptions détaillées

---

## 🎓 Apprentissages Clés

Ce projet couvre :

- ✅ **AI/ML** : Systèmes de recommandation, Surprise, scikit-learn
- ✅ **Data Engineering** : Pipelines, ETL, RabbitMQ, PostgreSQL
- ✅ **System Architecture** : Microservices, Docker, asynchrone
- ✅ **DevOps** : CI/CD, GitHub Actions, monitoring
- ✅ **Software Engineering** : Code quality, testing, documentation

---

*Last updated: May 2026*  
*Project: BI Adaptative - AI-driven Engineering*  
*Team: BOUBKER NAQI & IMRANE HAJJI "SI & BigData Engineering Students"*