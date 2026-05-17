# 🔧 GUIDE COMPLET - PERSONNE B (Backend & System Integration Engineer)

> **Tout ce que vous devez savoir pour être le "pilier" du système**

---

## 👤 VOTRE PROFIL

**Titre**: Backend & System Integration Engineer  
**Focus**: Infrastructure, DevOps, Intégration  
**Heures estimées**: 42 heures  
**Compétences requises**: Docker, Python, SQL, Metabase API  

**Responsabilités principales**:
- Architecture infrastructure (Docker, docker-compose)
- Orchestration des services (RabbitMQ, PostgreSQL)
- Pipeline de données (Consumer Python)
- Intégration Metabase
- CI/CD et résilience

---

## 📚 FONDAMENTAUX QUE VOUS DEVEZ COMPRENDRE

### 1. Qu'est-ce que Docker?

**Analogie simple**:
```
Sans Docker:
├─ Développeur A: "Python 3.9, Windows, pip install X"
├─ Développeur B: "Python 3.8, Mac, conda install Y"
└─ Serveur Prod: "Python 3.10, Linux, apt-get Z"
→ "Ça fonctionne sur ma machine!" (problème classique)

Avec Docker:
├─ Tout le monde: Une "boîte" identique avec Python 3.9 + ALL dépendances
└─ "Ça fonctionnera partout" ✅
```

**Qu'est-ce que c'est techniquement?**

Une **image** Docker est un dossier avec:
- Un OS léger (Alpine Linux)
- Python installé
- Vos dépendances (pip install)
- Votre code

Un **conteneur** est une image qui **tourne** (exécutée).

**Exemple visuel**:
```
Dockerfile (recette)
    ↓
docker build
    ↓
Image (emballage)
    ↓
docker run
    ↓
Conteneur (actif)
```

**Cycle de vie**:
```
Docker Image = Classe (blueprint)
Docker Container = Instance (en exécution)

Exemple:
Image: "ubuntu:20.04 + Python 3.9 + my_app"
Container 1: Instance de cette image (PID 1234, IP 172.17.0.2)
Container 2: Instance de cette image (PID 5678, IP 172.17.0.3)
```

---

### 2. Qu'est-ce que docker-compose?

**Problème**:
```
Pour lancer BI Adaptative, vous avez besoin de:
1. PostgreSQL (image postgres:14)
2. RabbitMQ (image rabbitmq:3.12)
3. Python Consumer (votre image personnalisée)
4. Python API (votre image personnalisée)
5. Metabase (image metabase/metabase)

Sans docker-compose:
docker run -d --name postgres_container \
  -e POSTGRES_PASSWORD=secret \
  -p 5432:5432 \
  postgres:14

docker run -d --name rabbitmq_container \
  -p 5672:5672 \
  -p 15672:15672 \
  rabbitmq:3.12-management

docker run -d --name consumer_container \
  -v $(pwd)/backend:/app \
  -p 8001:8001 \
  my_consumer:latest

... Et 2 autres docker run ...

→ 5+ commandes, difficile à gérer, facile d'oublier des détails

Avec docker-compose:
docker-compose up -d
→ 1 commande = tout est lancé avec les bonnes configurations!
```

**Qu'est-ce que docker-compose**?

Un fichier YAML qui décrit:
- Quels services (containers)
- Comment les configurer
- Comment les connecter

```yaml
version: '3.8'

services:
  postgresql:
    image: postgres:14
    environment:
      POSTGRES_PASSWORD: secret
    ports:
      - "5432:5432"

  rabbitmq:
    image: rabbitmq:3.12-management
    ports:
      - "5672:5672"
      - "15672:15672"

  consumer:
    build: ./backend/consumer
    environment:
      RABBITMQ_HOST: rabbitmq
    depends_on:
      - rabbitmq
      - postgresql
```

Puis: `docker-compose up -d`

**Comparaison**:
```
docker run:     Pour lancer 1 conteneur
docker-compose: Pour orchestrer plusieurs conteneurs
Kubernetes:     Pour orchestrer 1000+ conteneurs (pas utile ici)
```

---

### 3. Comprendre le Réseau Docker

**Problème classique**:
```
Vous êtes dans le conteneur Consumer, vous avez besoin de PostgreSQL.
Adresse à utiliser?

MAUVAIS: localhost:5432
  → "localhost" dans le conteneur = le conteneur lui-même (pas la DB!)

BON: postgresql:5432
  → "postgresql" = nom du service dans docker-compose
  → Docker résout automatiquement l'IP
```

**Comment ça fonctionne**:
```
Services dans docker-compose:
├─ postgresql (IP interne: 172.18.0.2)
├─ rabbitmq (IP interne: 172.18.0.3)
├─ consumer (IP interne: 172.18.0.4)
└─ api (IP interne: 172.18.0.5)

Tous sur le même réseau virtuel = peuvent se parler par nom!

De consumer, accéder:
- PostgreSQL: postgresql:5432
- RabbitMQ: rabbitmq:5672
```

---

### 4. Qu'est-ce que RabbitMQ?

**Problème qu'il résout**:
```
Sans RabbitMQ (synchrone):
Metabase envoie un log → Attendre que DB écrive → Retourner au user
→ Lent! (utilisateur attend)

Avec RabbitMQ (asynchrone):
Metabase envoie un log → Mettre en queue → Retourner immédiatement
                                  ↓
                          Consumer traite à son rythme
                                  ↓
                          Écrire dans DB
→ Rapide! (utilisateur ne subit pas le délai)
```

**Qu'est-ce que c'est?**

Un **Message Broker**: Un intermédiaire qui:
1. Reçoit les messages (logs)
2. Les stocke en queue
3. Les distribue aux consumers

```
Publisher → RabbitMQ → Consumer
(Metabase)    (Queue)   (Your code)
                         Writes to DB
```

**Types de messages**:
```
QUEUE: File d'attente simple
  Publisher 1 → [msg1, msg2, msg3] ← Consumer 1
  
TOPIC/FANOUT: Pubsub (publish-subscribe)
  Publisher 1 → ┌─→ Consumer 1
                ├─→ Consumer 2
                └─→ Consumer 3
```

**Dans notre cas**: Nous utilisons une QUEUE simple
```
Metabase → RabbitMQ (queue: navigation_logs) → Consumer Python → PostgreSQL
```

**Avantages**:
- ✅ Découplage (Metabase ne connaît pas le Consumer)
- ✅ Résilience (si Consumer crash, messages restent dans la queue)
- ✅ Scalabilité (ajouter plus de consumers = traiter plus vite)

---

### 5. Qu'est-ce que PostgreSQL?

**C'est quoi?**

Une base de données relationnelle open-source.

**Tables dans notre projet**:
```sql
navigation_logs:
├─ id (PRIMARY KEY)
├─ user_id (FOREIGN KEY)
├─ report_id (FOREIGN KEY)
├─ action (VARCHAR)
├─ duration (INTEGER)
└─ timestamp (DATETIME)

reports:
├─ id (PRIMARY KEY)
├─ metabase_report_id
├─ title
├─ description
├─ tags
└─ category

recommendations:
├─ id (PRIMARY KEY)
├─ user_id (FOREIGN KEY)
├─ report_id (FOREIGN KEY)
├─ score (FLOAT)
├─ algorithm (VARCHAR)
└─ created_at (DATETIME)
```

**Opérations principales**:
```sql
-- CREATE: Ajouter une ligne
INSERT INTO navigation_logs (user_id, report_id, duration)
VALUES (1, 42, 120);

-- READ: Récupérer des lignes
SELECT * FROM navigation_logs WHERE user_id = 1;

-- UPDATE: Modifier une ligne
UPDATE navigation_logs SET duration = 150 WHERE id = 1;

-- DELETE: Supprimer une ligne
DELETE FROM navigation_logs WHERE id = 1;
```

---

## 🗺️ VOTRE ROADMAP COMPLÈTE

### PHASE 1: Infrastructure & Setup (Semaine 1) - 7 heures

**C'est VOTRE PHASE - vous gérez tout**

#### Tâche 1.1: Initialiser Git & Repository (1 heure)

**Qu'est-ce que Git?**

Un système de versioning (contrôle de changements).

**Pourquoi?**
```
Sans Git:
main.py → main_v1.py → main_final.py → main_final_REALLY.py
→ Chaos!

Avec Git:
- Un seul main.py
- Historique de tous les changements
- Facile de revenir en arrière
- Collaboration sans conflits
```

**Commandes essentielles**:
```bash
# Créer un repository
git init
# ou cloner un existant
git clone https://github.com/user/bi-adaptative.git

# Créer une branche (pour votre travail)
git checkout -b feature/phase-1-setup

# Ajouter des fichiers
git add .

# Sauvegarder (commit)
git commit -m "Phase 1: Docker setup completed"

# Pousser vers GitHub
git push origin feature/phase-1-setup

# Retour à main
git checkout main

# Fusionner votre travail
git merge feature/phase-1-setup
```

**Fichiers à créer/ajouter**:
```
bi-adaptative/
├── .gitignore                 # Fichiers à ignorer
├── .env.example               # Variables d'env (template)
├── README.md                  # Documentation
├── docker-compose.yml         # ← Principal!
├── docker-compose.override.yml # (optionnel, pour dev)
├── .github/
│   └── workflows/
│       └── ci.yml            # CI/CD (Phase 6)
├── db/
│   ├── init.sql              # Schéma de base
│   └── migrations/           # Futures migrations
├── backend/
│   ├── consumer/
│   │   ├── Dockerfile
│   │   ├── consumer.py
│   │   ├── config.py
│   │   └── requirements.txt
│   ├── api/
│   │   ├── Dockerfile
│   │   ├── main.py
│   │   ├── schemas.py
│   │   └── requirements.txt
│   └── publisher/
│       ├── Dockerfile
│       ├── publisher.py
│       └── requirements.txt
└── tests/
    ├── test_consumer.py
    └── test_api.py
```

**Structure .gitignore**:
```
# Python
__pycache__/
*.py[cod]
*.egg-info/
.venv/
venv/

# Environment
.env
.env.local

# IDE
.vscode/
.idea/
*.swp

# Docker
docker-compose.override.yml

# Logs
*.log

# Database
*.db
*.sqlite
```

**À faire**:
```bash
git init
touch .gitignore
git add .
git commit -m "Initial commit: Project structure"
git branch feature/phase-1-setup
git checkout feature/phase-1-setup
```

---

#### Tâche 1.2: Créer docker-compose.yml (2 heures)

**C'est le fichier CLÉS de votre travail!**

**Qu'est-ce que vous devez créer**:

Un fichier `docker-compose.yml` qui définit 5 services:

1. **PostgreSQL** - Database
2. **RabbitMQ** - Message Broker
3. **Consumer** - Python script qui traite les messages
4. **API** - FastAPI pour les recommandations
5. **Metabase** - UI BI

**Structure complète**:

```yaml
version: '3.8'

# ============ CONFIGURATION COMMUNE ============
x-common-variables: &common-variables
  LOG_LEVEL: INFO
  ENVIRONMENT: development

# ============ SERVICES ============
services:

  # ========== 1. PostgreSQL ==========
  postgresql:
    image: postgres:14-alpine         # Image officielle, Alpine pour légèreté
    container_name: bi_adaptive_db
    restart: unless-stopped            # Redémarrer si crash
    
    environment:
      # Configurations PostgreSQL
      POSTGRES_USER: aibi_user
      POSTGRES_PASSWORD: ${DB_PASSWORD:-changeme}
      POSTGRES_DB: bi_adaptive
      POSTGRES_INITDB_ARGS: "--encoding=UTF8 --locale=en_US.UTF-8"
    
    ports:
      - "5432:5432"                    # Port externe:interne
    
    volumes:
      # Initialiser la base au démarrage
      - ./db/init.sql:/docker-entrypoint-initdb.d/init.sql:ro
      # Persister les données
      - postgres_data:/var/lib/postgresql/data
    
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U aibi_user"]
      interval: 10s
      timeout: 5s
      retries: 5
    
    networks:
      - bi_network
    
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"

  # ========== 2. RabbitMQ ==========
  rabbitmq:
    image: rabbitmq:3.12-management-alpine
    container_name: bi_adaptive_mq
    restart: unless-stopped
    
    environment:
      RABBITMQ_DEFAULT_USER: ${RABBITMQ_USER:-guest}
      RABBITMQ_DEFAULT_PASS: ${RABBITMQ_PASSWORD:-guest}
      RABBITMQ_DEFAULT_VHOST: /
    
    ports:
      - "5672:5672"      # AMQP protocol
      - "15672:15672"    # Management UI
    
    volumes:
      # Persister les messages en queue
      - rabbitmq_data:/var/lib/rabbitmq
    
    healthcheck:
      test: ["CMD", "rabbitmq-diagnostics", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5
    
    networks:
      - bi_network
    
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"

  # ========== 3. Python Consumer ==========
  consumer:
    build:
      context: ./backend/consumer
      dockerfile: Dockerfile
    container_name: bi_adaptive_consumer
    restart: unless-stopped
    
    environment:
      <<: *common-variables
      RABBITMQ_HOST: rabbitmq
      RABBITMQ_PORT: 5672
      RABBITMQ_USER: ${RABBITMQ_USER:-guest}
      RABBITMQ_PASSWORD: ${RABBITMQ_PASSWORD:-guest}
      POSTGRES_HOST: postgresql
      POSTGRES_PORT: 5432
      POSTGRES_DB: bi_adaptive
      POSTGRES_USER: aibi_user
      POSTGRES_PASSWORD: ${DB_PASSWORD:-changeme}
    
    depends_on:
      postgresql:
        condition: service_healthy
      rabbitmq:
        condition: service_healthy
    
    volumes:
      # Code source (pour développement - hot reload)
      - ./backend/consumer:/app
    
    networks:
      - bi_network
    
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"

  # ========== 4. Python API ==========
  api:
    build:
      context: ./backend/api
      dockerfile: Dockerfile
    container_name: bi_adaptive_api
    restart: unless-stopped
    
    environment:
      <<: *common-variables
      POSTGRES_HOST: postgresql
      POSTGRES_PORT: 5432
      POSTGRES_DB: bi_adaptive
      POSTGRES_USER: aibi_user
      POSTGRES_PASSWORD: ${DB_PASSWORD:-changeme}
      API_HOST: 0.0.0.0
      API_PORT: 8000
    
    ports:
      - "8000:8000"
    
    depends_on:
      postgresql:
        condition: service_healthy
    
    volumes:
      - ./backend/api:/app
    
    networks:
      - bi_network
    
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"

  # ========== 5. Metabase ==========
  metabase:
    image: metabase/metabase:latest
    container_name: bi_adaptive_metabase
    restart: unless-stopped
    
    environment:
      MB_DB_TYPE: postgres
      MB_DB_DBNAME: bi_adaptive
      MB_DB_HOST: postgresql
      MB_DB_PORT: 5432
      MB_DB_USER: aibi_user
      MB_DB_PASS: ${DB_PASSWORD:-changeme}
      MB_JAVA_TIMEZONE: UTC
    
    ports:
      - "3000:3000"
    
    depends_on:
      postgresql:
        condition: service_healthy
    
    networks:
      - bi_network
    
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"

# ============ NETWORKS ============
networks:
  bi_network:
    driver: bridge

# ============ VOLUMES ============
volumes:
  postgres_data:
    driver: local
  rabbitmq_data:
    driver: local
```

**Explications détaillées**:

**1. Version & Structure**:
```yaml
version: '3.8'  # Docker Compose version (3.8 = récent, compatible)

services:      # Définir les services (conteneurs)
networks:      # Définir les réseaux
volumes:       # Définir les volumes (stockage persistant)
```

**2. Service PostgreSQL**:
```yaml
image: postgres:14-alpine
# ↑ Quelle image utiliser
# postgres:14 = PostgreSQL 14
# -alpine = Version légère (~50MB au lieu de 300MB)

environment:
  # Variables d'environnement pour le conteneur
  POSTGRES_USER: aibi_user
  POSTGRES_PASSWORD: ${DB_PASSWORD:-changeme}
  # ${VAR:-default} = Utiliser variable $VAR, sinon "default"

ports:
  - "5432:5432"
  # Format: PORT_EXTERNE:PORT_INTERNE
  # De l'hôte (votre PC), utiliser localhost:5432

volumes:
  - ./db/init.sql:/docker-entrypoint-initdb.d/init.sql:ro
  # Exécuter init.sql au démarrage
  # :ro = Read-Only (la DB ne peut pas modifier le fichier)
  
  - postgres_data:/var/lib/postgresql/data
  # Persister les données (même si conteneur supprimé)
  # postgres_data = Volume named (défini en bas)

healthcheck:
  # Vérifier que PostgreSQL fonctionne
  test: pg_isready -U aibi_user
  interval: 10s  # Tester tous les 10s
  timeout: 5s    # Timeout après 5s
  retries: 5     # Échouer après 5 tentatives
  
  # Utilité: Les autres services attendent que le healthcheck passe
```

**3. Service RabbitMQ**:
```yaml
# Similaire à PostgreSQL, mais:
# - Port 5672: Protocole AMQP (clients)
# - Port 15672: UI management (web)
# - Url: http://localhost:15672 (user/pass: guest/guest)
```

**4. Service Consumer**:
```yaml
build:
  context: ./backend/consumer
  dockerfile: Dockerfile
# Au lieu de utiliser une image existante,
# on BUILD notre image à partir du Dockerfile

depends_on:
  postgresql:
    condition: service_healthy
# Attendre que PostgreSQL soit healthy avant de lancer Consumer
# Important: Consumer a besoin de la DB!

volumes:
  - ./backend/consumer:/app
# Monter le code source du développeur
# Permet les changements live (hot reload)
# ATTENTION: Utile en développement, pas en production!
```

**5. Service API**:
```yaml
# Similaire à Consumer
# Port 8000: L'API écoute là-dessus
# URL: http://localhost:8000
# Documentation: http://localhost:8000/docs (Swagger auto)
```

**6. Service Metabase**:
```yaml
image: metabase/metabase:latest
# Image officielle de Metabase

environment:
  MB_DB_TYPE: postgres
  MB_DB_HOST: postgresql
  # ↑ "postgresql" = nom du service dans docker-compose
  # Docker résout automatiquement l'IP interne
  
ports:
  - "3000:3000"
# URL: http://localhost:3000
```

**7. Networks**:
```yaml
networks:
  bi_network:
    driver: bridge
    
# Bridge = Tous les services sur le même réseau virtuel
# Résolution automatique: postgresql:5432 fonctionne!
```

**8. Volumes**:
```yaml
volumes:
  postgres_data:
    driver: local
    
# Named volume = persiste même si conteneur supprimé
# Utile pour éviter de perdre les données
```

**Utilisation**:

```bash
# Démarrer tous les services
docker-compose up -d

# Vérifier que tout fonctionne
docker-compose ps
# OUTPUT:
# NAME          STATUS
# postgresql    Up (healthy)
# rabbitmq      Up (healthy)
# consumer      Up
# api           Up
# metabase      Up

# Voir les logs
docker-compose logs -f consumer
docker-compose logs -f postgresql

# Arrêter
docker-compose down

# Arrêter et supprimer les volumes
docker-compose down -v
```

**À faire**:
```bash
# Créer le fichier docker-compose.yml
# Copier le contenu ci-dessus
# Créer .env.example:
cat > .env.example << EOF
DB_PASSWORD=changeme
RABBITMQ_USER=guest
RABBITMQ_PASSWORD=guest
EOF

# Tester
docker-compose up -d
docker-compose ps
```

---

#### Tâche 1.3: Créer le Schéma PostgreSQL (1.5 heures)

**Qu'est-ce que c'est?**

Définir la structure des tables (colonnes, types, contraintes).

**Pourquoi?**
Sans schéma:
- Les données sont du chaos
- Pas de validation
- Requêtes lentes

Avec schéma:
- Structure bien définie
- Indexes pour performance
- Contraintes pour intégrité

**Fichier: db/init.sql**

```sql
-- ============ EXTENSIONS ============
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ============ SCHEMA ============
CREATE SCHEMA IF NOT EXISTS bi_adaptive;
SET search_path TO bi_adaptive;

-- ============ TABLES ============

-- Table: users
-- Contient les utilisateurs du système Metabase
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table: reports
-- Contient les rapports Metabase
CREATE TABLE reports (
    id SERIAL PRIMARY KEY,
    metabase_report_id INTEGER UNIQUE NOT NULL,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    tags VARCHAR(500),
    category VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table: navigation_logs
-- Contient l'historique de navigation des utilisateurs
-- C'est la TABLE PRINCIPALE pour votre ML!
CREATE TABLE navigation_logs (
    id SERIAL PRIMARY KEY,
    
    -- Foreign Keys
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    report_id INTEGER NOT NULL REFERENCES reports(id) ON DELETE CASCADE,
    
    -- Action data
    action VARCHAR(50) DEFAULT 'view',  -- 'view', 'click', 'share', etc.
    duration INTEGER DEFAULT 0,          -- Secondes passées sur le rapport
    
    -- Metadata
    url VARCHAR(500),
    ip_address INET,
    user_agent VARCHAR(500),
    
    -- Timestamp
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Constraints
    CHECK (duration >= 0),
    
    CONSTRAINT fk_user FOREIGN KEY (user_id) REFERENCES users(id),
    CONSTRAINT fk_report FOREIGN KEY (report_id) REFERENCES reports(id)
);

-- Table: recommendations
-- Contient les recommandations générées par le ML
-- Metabase read ces données pour afficher "Rapports recommandés"
CREATE TABLE recommendations (
    id SERIAL PRIMARY KEY,
    
    -- Foreign Keys
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    report_id INTEGER NOT NULL REFERENCES reports(id) ON DELETE CASCADE,
    
    -- Recommendation data
    score FLOAT NOT NULL,              -- Score entre 0 et 1
    rank INTEGER NOT NULL,             -- Rang (1, 2, 3, ...)
    algorithm VARCHAR(50) NOT NULL,    -- 'collaborative', 'content_based', 'hybrid'
    
    -- Metadata
    experiment_group VARCHAR(50),      -- A/B testing group
    
    -- Timestamp
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Constraints
    CHECK (score >= 0 AND score <= 1),
    CHECK (rank >= 1)
);

-- Table: feedback (optionnel)
-- Tracker les clics sur recommandations (pour A/B testing)
CREATE TABLE feedback (
    id SERIAL PRIMARY KEY,
    
    -- Foreign Keys
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    recommendation_id INTEGER NOT NULL REFERENCES recommendations(id) ON DELETE CASCADE,
    
    -- Feedback data
    clicked BOOLEAN DEFAULT FALSE,
    helpful BOOLEAN,                   -- L'utilisateur a-t-il trouvé utile?
    
    -- Timestamp
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============ INDEXES ============
-- Important pour PERFORMANCE!

-- navigation_logs: Les requêtes vont chercher par user_id et timestamp
CREATE INDEX idx_navigation_logs_user_id 
    ON navigation_logs(user_id);

CREATE INDEX idx_navigation_logs_report_id 
    ON navigation_logs(report_id);

CREATE INDEX idx_navigation_logs_timestamp 
    ON navigation_logs(timestamp);

-- Recherche récente pour un utilisateur
CREATE INDEX idx_navigation_logs_user_timestamp 
    ON navigation_logs(user_id, timestamp DESC);

-- recommendations: Recherches par user_id
CREATE INDEX idx_recommendations_user_id 
    ON recommendations(user_id);

CREATE INDEX idx_recommendations_rank 
    ON recommendations(user_id, rank);

-- feedback: Tracker les clics
CREATE INDEX idx_feedback_user_id 
    ON feedback(user_id);

CREATE INDEX idx_feedback_recommendation_id 
    ON feedback(recommendation_id);

-- ============ VIEWS (optionnel) ============
-- Vues pour requêtes courantes

-- Vue: Utilisateurs actifs (plus de 10 log en 7 jours)
CREATE OR REPLACE VIEW active_users AS
SELECT 
    u.id,
    u.email,
    COUNT(nl.id) as navigation_count,
    MAX(nl.timestamp) as last_active
FROM users u
LEFT JOIN navigation_logs nl ON u.id = nl.user_id
    AND nl.timestamp > CURRENT_TIMESTAMP - INTERVAL '7 days'
GROUP BY u.id
HAVING COUNT(nl.id) > 10
ORDER BY last_active DESC;

-- Vue: Rapports populaires
CREATE OR REPLACE VIEW popular_reports AS
SELECT 
    r.id,
    r.title,
    COUNT(nl.id) as view_count,
    AVG(nl.duration) as avg_duration
FROM reports r
LEFT JOIN navigation_logs nl ON r.id = nl.report_id
GROUP BY r.id
ORDER BY view_count DESC;

-- ============ INITIAL DATA ============
-- Données de test

INSERT INTO users (email, name) VALUES
    ('user1@example.com', 'Alice'),
    ('user2@example.com', 'Bob'),
    ('user3@example.com', 'Charlie'),
    ('user4@example.com', 'Diana'),
    ('user5@example.com', 'Eve');

INSERT INTO reports (metabase_report_id, title, description, tags, category) VALUES
    (1, 'Sales by Region', 'Monthly sales breakdown', 'sales,region', 'Finance'),
    (2, 'Revenue Forecast', 'Q2 revenue prediction', 'forecast,revenue', 'Finance'),
    (3, 'Top Customers', 'Best customers by revenue', 'customers,sales', 'Sales'),
    (4, 'Inventory Status', 'Current stock levels', 'inventory,stock', 'Operations'),
    (5, 'HR Statistics', 'Employee count by department', 'hr,employees', 'HR');
```

**Explication des concepts**:

**1. Types de données**:
```sql
SERIAL          -- Auto-increment integer (1, 2, 3, ...)
INTEGER         -- Nombre entier
FLOAT           -- Nombre décimal
VARCHAR(255)    -- Texte (max 255 caractères)
TEXT            -- Texte long (illimité)
BOOLEAN         -- true/false
TIMESTAMP       -- Date et heure
INET            -- Adresse IP
```

**2. Constraints**:
```sql
PRIMARY KEY     -- Identifiant unique (1 par table)
UNIQUE          -- Valeur unique (email ne peut pas être dupliqué)
NOT NULL        -- La colonne doit avoir une valeur
DEFAULT         -- Valeur par défaut si pas fourni
FOREIGN KEY     -- Référence à une autre table
CHECK           -- Validation (duration >= 0)
```

**3. Indexes**:
```sql
CREATE INDEX idx_name ON table(column);

Avec index:
  SELECT * FROM navigation_logs WHERE user_id = 1
  → Très rapide! (direct lookup)

Sans index:
  → Lent! (scan toute la table)
  
Trade-off:
  + Requêtes rapides
  - Écriture plus lente (doit mettre à jour l'index)
  - Plus de mémoire
```

**4. Views**:
```sql
CREATE VIEW name AS SELECT ...

Syntaxe sucre pour des requêtes courantes.
Utilisable comme table: SELECT * FROM active_users;
```

**À faire**:
```bash
# Créer db/init.sql avec le contenu ci-dessus
# Vérifier la syntaxe
docker-compose up -d postgresql
docker-compose exec postgresql psql -U aibi_user -d bi_adaptive -f /docker-entrypoint-initdb.d/init.sql

# Vérifier les tables
docker-compose exec postgresql psql -U aibi_user -d bi_adaptive
\dt  -- Lister les tables
```

---

#### Tâche 1.4: Peupler Metabase (3 heures)

**Qu'est-ce que vous devez faire?**

1. Lancer Metabase
2. Setup initial (créer compte admin)
3. Connecter à PostgreSQL
4. Créer 15-20 rapports fictifs

**Étapes détaillées**:

**1. Lancer Metabase**:
```bash
docker-compose up -d metabase

# Attendre quelques secondes
sleep 10

# Ouvrir http://localhost:3000
```

**2. Setup Initial**:
```
Vous verrez: "Welcome to Metabase"
1. Email: admin@example.com
2. Password: admin123
3. Company: My Company
4. Continue
```

**3. Connecter à PostgreSQL**:
```
1. Cliquer sur "⚙️ Settings" (en haut à droite)
2. Admin Settings
3. Databases
4. Add database
5. PostgreSQL
   - Name: bi_adaptive_db
   - Host: postgresql
   - Port: 5432
   - Database name: bi_adaptive
   - Username: aibi_user
   - Password: changeme
6. Save
```

**4. Créer les rapports**:

Allez dans "Create" → "Question":

**Rapport 1: Sales by Region**
```
SELECT 
    'US' as region,
    150000 as sales
UNION ALL
SELECT 'EU', 120000
UNION ALL
SELECT 'APAC', 95000
```
→ Save as "Sales by Region"

**Rapport 2: Revenue Forecast**
```
SELECT 
    'Q1' as quarter,
    500000 as revenue
UNION ALL
SELECT 'Q2', 550000
UNION ALL
SELECT 'Q3', 580000
UNION ALL
SELECT 'Q4', 620000
```
→ Save as "Revenue Forecast"

**Rapport 3: Top Customers**
```
SELECT 
    'Acme Corp' as customer,
    250000 as revenue,
    15 as orders
UNION ALL
SELECT 'TechCo', 180000, 12
UNION ALL
SELECT 'GlobalInc', 160000, 10
UNION ALL
SELECT 'FastTrade', 145000, 9
UNION ALL
SELECT 'SmartBiz', 130000, 8
```
→ Save as "Top Customers"

(Créer 15-20 rapports similaires)

**Créer un Dashboard**:
1. Create → Dashboard → "Executive Summary"
2. Ajouter les rapports créés
3. Save

**Pourquoi?**
- Test que Metabase fonctionne
- Source de données pour le ML
- Simuler un vrai système
- Tester le tracking plus tard

---

### PHASE 2: Tracking & Messaging (Semaine 2) - 6 heures

**Votre rôle**: Créer le publisher Metabase → RabbitMQ

#### Tâche 2.1: Étudier Metabase Audit Logs API (1 heure)

**Qu'est-ce que c'est?**

Metabase enregistre TOUS les événements (clics utilisateurs).

**API Endpoint**:
```
GET http://localhost:3000/api/audit
```

**Réponse exemple**:
```json
{
  "data": [
    {
      "id": 1,
      "user_id": 1,
      "object": {
        "name": "Sales by Region",
        "id": 1,
        "model": "dashboard"
      },
      "action": "dashboard",
      "details": null,
      "timestamp": "2026-05-06T10:30:00Z"
    }
  ],
  "total": 1
}
```

**Vous devez connaître**:
- Comment appeler cette API
- Authentification (token)
- Filtres disponibles
- Format de réponse

**Test**:
```bash
# Obtenir le token
curl -X POST http://localhost:3000/api/session \
  -H "Content-Type: application/json" \
  -d '{"username": "admin@example.com", "password": "admin123"}'

# Response: {"id": "xxx-xxx-xxx"}

# Utiliser le token
curl -X GET "http://localhost:3000/api/audit" \
  -H "X-Metabase-Session: xxx-xxx-xxx"
```

---

#### Tâche 2.2: Publisher Python (2.5 heures)

**Qu'est-ce que c'est?**

Un script Python qui:
1. Poll l'API Metabase toutes les secondes
2. Récupère les nouveaux événements
3. Les envoie à RabbitMQ

**Code complet**:

```python
#!/usr/bin/env python3
"""
Metabase Publisher
Polls Metabase audit logs and publishes to RabbitMQ
"""

import os
import json
import time
import logging
import requests
import pika
from datetime import datetime
from typing import Optional, List, Dict

# ============ CONFIGURATION ============

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class MetabasePublisher:
    """Polls Metabase and publishes navigation logs to RabbitMQ"""
    
    def __init__(self):
        # Metabase Configuration
        self.metabase_url = os.getenv('METABASE_URL', 'http://metabase:3000')
        self.metabase_user = os.getenv('METABASE_USER', 'admin@example.com')
        self.metabase_password = os.getenv('METABASE_PASSWORD', 'admin123')
        
        # RabbitMQ Configuration
        self.rabbitmq_host = os.getenv('RABBITMQ_HOST', 'rabbitmq')
        self.rabbitmq_port = int(os.getenv('RABBITMQ_PORT', '5672'))
        self.rabbitmq_user = os.getenv('RABBITMQ_USER', 'guest')
        self.rabbitmq_password = os.getenv('RABBITMQ_PASSWORD', 'guest')
        
        # Session
        self.session_id: Optional[str] = None
        self.last_audit_id: int = 0
        
        # Connection
        self.connection = None
        self.channel = None
    
    def authenticate(self) -> bool:
        """Authenticate with Metabase and get session ID"""
        try:
            logger.info("Authenticating with Metabase...")
            
            url = f"{self.metabase_url}/api/session"
            payload = {
                "username": self.metabase_user,
                "password": self.metabase_password
            }
            
            response = requests.post(url, json=payload, timeout=5)
            response.raise_for_status()
            
            data = response.json()
            self.session_id = data.get('id')
            
            if self.session_id:
                logger.info(f"✓ Authenticated successfully")
                return True
            else:
                logger.error(f"✗ No session ID in response: {data}")
                return False
        
        except Exception as e:
            logger.error(f"✗ Authentication failed: {e}")
            return False
    
    def get_audit_logs(self) -> Optional[List[Dict]]:
        """Fetch recent audit logs from Metabase"""
        if not self.session_id:
            logger.warn("No session ID, authenticating...")
            if not self.authenticate():
                return None
        
        try:
            url = f"{self.metabase_url}/api/audit"
            headers = {
                "X-Metabase-Session": self.session_id
            }
            params = {
                "limit": 100  # Get last 100 events
            }
            
            response = requests.get(url, headers=headers, params=params, timeout=5)
            response.raise_for_status()
            
            data = response.json()
            logs = data.get('data', [])
            
            # Filter new logs (only logs after last_audit_id)
            new_logs = [log for log in logs if log.get('id', 0) > self.last_audit_id]
            
            if new_logs:
                self.last_audit_id = max(log.get('id', 0) for log in new_logs)
            
            return new_logs
        
        except Exception as e:
            logger.error(f"✗ Failed to get audit logs: {e}")
            return None
    
    def parse_log(self, log: Dict) -> Optional[Dict]:
        """
        Parse Metabase log into navigation_log format
        
        Metabase format:
        {
            "id": 1,
            "user_id": 1,
            "object": {"name": "Sales by Region", "id": 1},
            "action": "dashboard",
            "timestamp": "2026-05-06T10:30:00Z"
        }
        
        Output format:
        {
            "user_id": 1,
            "report_id": 1,
            "action": "view",
            "duration": 0,
            "timestamp": "2026-05-06T10:30:00Z"
        }
        """
        try:
            user_id = log.get('user_id')
            object_info = log.get('object', {})
            report_id = object_info.get('id')
            action = log.get('action', 'view')
            timestamp = log.get('timestamp')
            
            if not user_id or not report_id:
                logger.warn(f"Incomplete log (missing user or report): {log}")
                return None
            
            return {
                'user_id': user_id,
                'report_id': report_id,
                'action': action,
                'duration': 0,  # Will be updated by another process
                'timestamp': timestamp
            }
        
        except Exception as e:
            logger.error(f"✗ Failed to parse log: {e}")
            return None
    
    def connect_rabbitmq(self) -> bool:
        """Connect to RabbitMQ"""
        try:
            logger.info("Connecting to RabbitMQ...")
            
            credentials = pika.PlainCredentials(self.rabbitmq_user, self.rabbitmq_password)
            parameters = pika.ConnectionParameters(
                host=self.rabbitmq_host,
                port=self.rabbitmq_port,
                credentials=credentials,
                connection_attempts=3,
                retry_delay=5
            )
            
            self.connection = pika.BlockingConnection(parameters)
            self.channel = self.connection.channel()
            
            # Declare queue (if doesn't exist)
            self.channel.queue_declare(
                queue='navigation_logs',
                durable=True  # Persist even if RabbitMQ restarts
            )
            
            logger.info("✓ Connected to RabbitMQ")
            return True
        
        except Exception as e:
            logger.error(f"✗ RabbitMQ connection failed: {e}")
            return False
    
    def publish_message(self, message: Dict) -> bool:
        """Publish a message to RabbitMQ"""
        try:
            if not self.channel:
                logger.warn("Not connected to RabbitMQ")
                return False
            
            self.channel.basic_publish(
                exchange='',
                routing_key='navigation_logs',
                body=json.dumps(message),
                properties=pika.BasicProperties(
                    delivery_mode=pika.spec.PERSISTENT_MODE,  # Persist to disk
                    content_type='application/json'
                )
            )
            
            logger.debug(f"Published: {message}")
            return True
        
        except Exception as e:
            logger.error(f"✗ Failed to publish message: {e}")
            return False
    
    def run(self):
        """Main loop: Poll Metabase and publish to RabbitMQ"""
        logger.info("Starting Metabase Publisher...")
        
        # Initial authentication
        if not self.authenticate():
            logger.error("Cannot authenticate with Metabase. Exiting.")
            return
        
        # Connect to RabbitMQ
        if not self.connect_rabbitmq():
            logger.error("Cannot connect to RabbitMQ. Exiting.")
            return
        
        # Main polling loop
        try:
            while True:
                logger.debug("Polling Metabase...")
                
                # Get new logs
                logs = self.get_audit_logs()
                
                if logs:
                    logger.info(f"Found {len(logs)} new logs")
                    
                    # Publish each log
                    for log in logs:
                        parsed = self.parse_log(log)
                        if parsed:
                            self.publish_message(parsed)
                else:
                    logger.debug("No new logs")
                
                # Poll every 1 second
                time.sleep(1)
        
        except KeyboardInterrupt:
            logger.info("Shutting down...")
        
        except Exception as e:
            logger.error(f"✗ Error in main loop: {e}")
        
        finally:
            if self.connection:
                self.connection.close()
            logger.info("Publisher stopped")


if __name__ == '__main__':
    publisher = MetabasePublisher()
    publisher.run()
```

**Dockerfile pour le Publisher**:
```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV PYTHONUNBUFFERED=1

CMD ["python", "publisher.py"]
```

**requirements.txt**:
```
requests==2.28.1
pika==1.3.1
python-dotenv==0.20.0
```

**À faire**:
```bash
# Créer backend/publisher/
mkdir -p backend/publisher

# Copier le code
cp publisher.py backend/publisher/
cp Dockerfile backend/publisher/
cp requirements.txt backend/publisher/

# Tester localement
cd backend/publisher
pip install -r requirements.txt
python publisher.py

# Dans Metabase, cliquer sur quelques rapports
# Vous devriez voir les logs:
# "Published: {'user_id': 1, 'report_id': 42, ...}"
```

---

#### Tâche 2.3: Ajouter Publisher à docker-compose (0.5 heure)

```yaml
publisher:
  build:
    context: ./backend/publisher
    dockerfile: Dockerfile
  container_name: bi_adaptive_publisher
  restart: unless-stopped
  
  environment:
    METABASE_URL: http://metabase:3000
    METABASE_USER: admin@example.com
    METABASE_PASSWORD: admin123
    RABBITMQ_HOST: rabbitmq
    RABBITMQ_PORT: 5672
    RABBITMQ_USER: guest
    RABBITMQ_PASSWORD: guest
  
  depends_on:
    - metabase
    - rabbitmq
  
  networks:
    - bi_network
```

---

#### Tâche 2.4: Tester E2E (1.5 heures)

**Test complet**:

```bash
# 1. Démarrer tous les services
docker-compose up -d

# 2. Attendre que tout soit ready
sleep 30

# 3. Vérifier que tout tourne
docker-compose ps

# 4. Voir les logs du Publisher
docker-compose logs publisher

# 5. Ouvrir Metabase et cliquer sur des rapports
# http://localhost:3000

# 6. Vérifier RabbitMQ
# http://localhost:15672
# Admin → Queues → navigation_logs
# Vous devriez voir des messages!

# 7. Vérifier PostgreSQL
docker-compose exec postgresql psql -U aibi_user -d bi_adaptive
SELECT COUNT(*) FROM navigation_logs;
# Devrait être > 0 (si Consumer tourne)
```

---

### PHASE 3: Data Pipeline (Semaines 2-3) - 7 heures

**Votre rôle**: Créer le Consumer Python qui traite les messages

#### Tâche 3.1: Consumer RabbitMQ → PostgreSQL (4 heures)

**Qu'est-ce que c'est?**

Un script Python qui:
1. Écoute RabbitMQ
2. Récupère les messages
3. Les transforme
4. Les sauvegarde dans PostgreSQL

**Code complet**:

```python
#!/usr/bin/env python3
"""
Data Consumer
Consumes messages from RabbitMQ and writes to PostgreSQL
"""

import os
import json
import logging
import pika
import psycopg2
from datetime import datetime
from psycopg2.extras import execute_values
from typing import Optional

# ============ LOGGING ============

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ============ CONFIGURATION ============

class Config:
    # RabbitMQ
    RABBITMQ_HOST = os.getenv('RABBITMQ_HOST', 'rabbitmq')
    RABBITMQ_PORT = int(os.getenv('RABBITMQ_PORT', '5672'))
    RABBITMQ_USER = os.getenv('RABBITMQ_USER', 'guest')
    RABBITMQ_PASSWORD = os.getenv('RABBITMQ_PASSWORD', 'guest')
    
    # PostgreSQL
    POSTGRES_HOST = os.getenv('POSTGRES_HOST', 'postgresql')
    POSTGRES_PORT = int(os.getenv('POSTGRES_PORT', '5432'))
    POSTGRES_DB = os.getenv('POSTGRES_DB', 'bi_adaptive')
    POSTGRES_USER = os.getenv('POSTGRES_USER', 'aibi_user')
    POSTGRES_PASSWORD = os.getenv('POSTGRES_PASSWORD', 'changeme')
    
    # Processing
    BATCH_SIZE = 100  # Batch writes for efficiency
    ACK_TIMEOUT = 30  # seconds

# ============ CONSUMER ============

class DataConsumer:
    """Consume messages from RabbitMQ and write to PostgreSQL"""
    
    def __init__(self):
        self.rabbitmq_connection = None
        self.rabbitmq_channel = None
        self.postgres_connection = None
        self.postgres_cursor = None
        self.batch = []
    
    def connect_rabbitmq(self) -> bool:
        """Connect to RabbitMQ"""
        try:
            logger.info("Connecting to RabbitMQ...")
            
            credentials = pika.PlainCredentials(
                Config.RABBITMQ_USER,
                Config.RABBITMQ_PASSWORD
            )
            
            parameters = pika.ConnectionParameters(
                host=Config.RABBITMQ_HOST,
                port=Config.RABBITMQ_PORT,
                credentials=credentials,
                connection_attempts=3,
                retry_delay=5
            )
            
            self.rabbitmq_connection = pika.BlockingConnection(parameters)
            self.rabbitmq_channel = self.rabbitmq_connection.channel()
            
            # Declare queue
            self.rabbitmq_channel.queue_declare(
                queue='navigation_logs',
                durable=True
            )
            
            # Set prefetch (process 1 message at a time)
            self.rabbitmq_channel.basic_qos(prefetch_count=1)
            
            logger.info("✓ Connected to RabbitMQ")
            return True
        
        except Exception as e:
            logger.error(f"✗ RabbitMQ connection failed: {e}")
            return False
    
    def connect_postgres(self) -> bool:
        """Connect to PostgreSQL"""
        try:
            logger.info("Connecting to PostgreSQL...")
            
            self.postgres_connection = psycopg2.connect(
                host=Config.POSTGRES_HOST,
                port=Config.POSTGRES_PORT,
                database=Config.POSTGRES_DB,
                user=Config.POSTGRES_USER,
                password=Config.POSTGRES_PASSWORD,
                connection_timeout=5
            )
            
            self.postgres_cursor = self.postgres_connection.cursor()
            
            logger.info("✓ Connected to PostgreSQL")
            return True
        
        except Exception as e:
            logger.error(f"✗ PostgreSQL connection failed: {e}")
            return False
    
    def parse_message(self, body: bytes) -> Optional[dict]:
        """Parse RabbitMQ message"""
        try:
            message = json.loads(body.decode())
            
            # Validate required fields
            if not all(k in message for k in ['user_id', 'report_id']):
                logger.warn(f"Incomplete message: {message}")
                return None
            
            return {
                'user_id': message['user_id'],
                'report_id': message['report_id'],
                'action': message.get('action', 'view'),
                'duration': message.get('duration', 0),
                'timestamp': message.get('timestamp', datetime.utcnow().isoformat())
            }
        
        except Exception as e:
            logger.error(f"✗ Failed to parse message: {e}")
            return None
    
    def write_batch(self) -> bool:
        """Write batch of records to PostgreSQL"""
        if not self.batch:
            return True
        
        try:
            # Prepare SQL
            sql = """
            INSERT INTO navigation_logs (user_id, report_id, action, duration, timestamp)
            VALUES %s
            ON CONFLICT DO NOTHING  -- Ignore duplicates
            """
            
            # Convert to tuples
            values = [
                (r['user_id'], r['report_id'], r['action'], r['duration'], r['timestamp'])
                for r in self.batch
            ]
            
            # Execute
            execute_values(
                self.postgres_cursor,
                sql,
                values,
                page_size=1000
            )
            
            # Commit
            self.postgres_connection.commit()
            
            count = len(self.batch)
            logger.info(f"✓ Wrote {count} records to PostgreSQL")
            
            self.batch = []
            return True
        
        except Exception as e:
            logger.error(f"✗ Failed to write batch: {e}")
            self.postgres_connection.rollback()
            return False
    
    def on_message(self, ch, method, properties, body):
        """Callback when message received"""
        try:
            # Parse message
            message = self.parse_message(body)
            
            if message:
                # Add to batch
                self.batch.append(message)
                logger.debug(f"Added to batch: {message}")
                
                # Write if batch is full
                if len(self.batch) >= Config.BATCH_SIZE:
                    self.write_batch()
            
            # Acknowledge message (remove from queue)
            ch.basic_ack(delivery_tag=method.delivery_tag)
        
        except Exception as e:
            logger.error(f"✗ Error processing message: {e}")
            
            # NACK message (put back in queue for retry)
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)
    
    def run(self):
        """Main loop: Listen for messages"""
        logger.info("Starting Data Consumer...")
        
        # Connect
        if not self.connect_rabbitmq():
            logger.error("Cannot connect to RabbitMQ. Exiting.")
            return
        
        if not self.connect_postgres():
            logger.error("Cannot connect to PostgreSQL. Exiting.")
            return
        
        # Set callback
        self.rabbitmq_channel.basic_consume(
            queue='navigation_logs',
            on_message_callback=self.on_message
        )
        
        logger.info("Listening for messages...")
        
        try:
            self.rabbitmq_channel.start_consuming()
        
        except KeyboardInterrupt:
            logger.info("Shutting down...")
            
            # Write any remaining batch
            if self.batch:
                self.write_batch()
        
        except Exception as e:
            logger.error(f"✗ Error in main loop: {e}")
        
        finally:
            if self.rabbitmq_connection:
                self.rabbitmq_connection.close()
            
            if self.postgres_connection:
                self.postgres_connection.close()
            
            logger.info("Consumer stopped")


if __name__ == '__main__':
    consumer = DataConsumer()
    consumer.run()
```

**Dockerfile**:
```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV PYTHONUNBUFFERED=1

CMD ["python", "consumer.py"]
```

**requirements.txt**:
```
pika==1.3.1
psycopg2-binary==2.9.3
python-dotenv==0.20.0
```

**Concepts importants**:

**1. Message Acknowledgment**:
```python
# Avec ACK: Message supprimé de la queue (consommé)
ch.basic_ack(delivery_tag=method.delivery_tag)

# Avec NACK: Message remis en queue (retry)
ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)

Importance:
├─ ACK immédiat → Rapide mais risque de perte
├─ ACK après écriture DB → Sûr mais plus lent
└─ Nous faisons: ACK après traitement (bon compromis)
```

**2. Batch Writing**:
```python
# Mauvais: Insérer 1 par 1
for msg in messages:
    INSERT INTO ...  # 1000 inserts = 1000 requêtes!

# Bon: Batch insert
INSERT INTO ... VALUES
  (1, 42, ...),
  (2, 50, ...),
  ... (1000 tuples)
# 1 requête = 1000x plus rapide!
```

**3. ON CONFLICT**:
```sql
INSERT ... ON CONFLICT DO NOTHING
-- Si même user + report déjà existe, ignorer
-- Évite les doublons
```

**À faire**:
```bash
mkdir -p backend/consumer
cp consumer.py backend/consumer/
cp Dockerfile backend/consumer/
cp requirements.txt backend/consumer/
```

---

#### Tâche 3.2: Ajouter Consumer à docker-compose (0.5 heure)

Déjà couvert dans docker-compose (voir Tâche 1.2)

---

#### Tâche 3.3: Tester E2E (2.5 heures)

**Test complet du pipeline**:

```bash
# 1. Démarrer tout
docker-compose up -d

# 2. Attendre
sleep 30

# 3. Vérifier les services
docker-compose ps
# Tous doivent être UP/healthy

# 4. Ouvrir Metabase
# http://localhost:3000
# Créer un utilisateur si nécessaire
# Cliquer sur 3-4 rapports différents

# 5. Vérifier RabbitMQ
# http://localhost:15672
# Queues → navigation_logs
# Messages doivent diminuer (Consumer les traite)

# 6. Vérifier PostgreSQL
docker-compose exec postgresql psql -U aibi_user -d bi_adaptive
SELECT COUNT(*) FROM navigation_logs;
# Devrait être > 0

SELECT user_id, report_id, COUNT(*) 
FROM navigation_logs 
GROUP BY user_id, report_id;
# Devrait montrer les rapports visitée

# 7. Logs
docker-compose logs consumer
# Vous devez voir:
# "✓ Wrote X records to PostgreSQL"

docker-compose logs publisher
# Vous devez voir:
# "Published: {...}"

# 8. Test de résilience
# Arrêter PostgreSQL
docker-compose pause postgresql

# Cliquer sur d'autres rapports dans Metabase
# Publisher continue à envoyer à RabbitMQ
# Consumer n'arrive pas à écrire mais retry

# Redémarrer PostgreSQL
docker-compose unpause postgresql

# Consumer rattrape les messages
# Vérifier que zéro données perdues
SELECT COUNT(*) FROM navigation_logs;
```

**Validation**:
```bash
✅ docker-compose ps: tous UP
✅ Metabase: 3000 répond
✅ RabbitMQ: 15672 répond
✅ API: 8000 répond
✅ navigation_logs table: > 0 lignes
✅ Logs sans erreurs
✅ Test résilience: zéro perte
```

---

### PHASE 4-5: API & Intégration (Semaines 4-5) - 8 heures

**Votre rôle**: Intégration Metabase + CI/CD

#### Tâche 5.3: Peupler Recommendations & Dashboard Metabase (4 heures)

**Qu'est-ce que vous devez faire**?

1. Créer un script Python qui appelle l'API ML
2. Générer les recommandations pour tous les utilisateurs
3. Afficher dans Metabase

**Code: scripts/populate_recommendations.py**:

```python
#!/usr/bin/env python3
"""
Populate recommendations from ML API
"""

import requests
import psycopg2
import logging
from typing import List

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RecommendationPopulator:
    def __init__(self):
        self.api_url = "http://api:8000"
        self.db_conn = psycopg2.connect(
            host="postgresql",
            database="bi_adaptive",
            user="aibi_user",
            password="changeme"
        )
    
    def get_all_users(self) -> List[int]:
        """Get all user IDs from database"""
        cursor = self.db_conn.cursor()
        cursor.execute("SELECT DISTINCT user_id FROM navigation_logs")
        users = [row[0] for row in cursor.fetchall()]
        cursor.close()
        return users
    
    def get_recommendations(self, user_id: int, n: int = 5) -> List[dict]:
        """Call ML API to get recommendations"""
        try:
            response = requests.post(
                f"{self.api_url}/recommendations",
                json={
                    "user_id": user_id,
                    "n_recommendations": n,
                    "alpha": 0.6
                },
                timeout=10
            )
            response.raise_for_status()
            
            data = response.json()
            return data.get('recommendations', [])
        
        except Exception as e:
            logger.error(f"Failed to get recommendations for user {user_id}: {e}")
            return []
    
    def save_recommendations(self, user_id: int, recs: List[dict]):
        """Save recommendations to database"""
        cursor = self.db_conn.cursor()
        
        for rank, rec in enumerate(recs, start=1):
            cursor.execute("""
                INSERT INTO recommendations (user_id, report_id, score, rank, algorithm)
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT DO NOTHING
            """, (
                user_id,
                rec['report_id'],
                rec['score'],
                rank,
                rec['algorithm']
            ))
        
        self.db_conn.commit()
        cursor.close()
    
    def run(self):
        """Main"""
        logger.info("Populating recommendations...")
        
        users = self.get_all_users()
        logger.info(f"Found {len(users)} users")
        
        for user_id in users:
            logger.info(f"Getting recommendations for user {user_id}...")
            recs = self.get_recommendations(user_id, n=5)
            
            if recs:
                self.save_recommendations(user_id, recs)
                logger.info(f"✓ Saved {len(recs)} recommendations")
        
        logger.info("Done!")


if __name__ == '__main__':
    populator = RecommendationPopulator()
    populator.run()
```

**Créer le Dashboard Metabase**:

1. Metabase → Create → Dashboard
2. Name: "Recommended Reports"
3. Add cards:

**Card 1: Recommendations by User**
```sql
SELECT 
    u.email,
    r.title,
    rec.score,
    rec.rank
FROM recommendations rec
JOIN users u ON rec.user_id = u.id
JOIN reports r ON rec.report_id = r.id
ORDER BY u.id, rec.rank
LIMIT 20
```

**Card 2: Recommendation Performance**
```sql
SELECT 
    rec.algorithm,
    COUNT(*) as count,
    AVG(rec.score) as avg_score
FROM recommendations rec
GROUP BY algorithm
```

---

### PHASE 6: DevOps & Résilience (Semaines 5-6) - 8 heures

**Votre rôle**: CI/CD + Tests

#### Tâche 6.1: GitHub Actions CI/CD (2 heures)

**Qu'est-ce que c'est?**

Automatiser: lint → tests → build → push

**Fichier: .github/workflows/ci.yml**:

```yaml
name: CI/CD Pipeline

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    
    services:
      postgres:
        image: postgres:14
        env:
          POSTGRES_PASSWORD: test
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
      
      rabbitmq:
        image: rabbitmq:3.12
        options: >-
          --health-cmd "rabbitmqctl status"
          --health-interval 10s

    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.9'
      
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install flake8 pytest
          pip install -r backend/consumer/requirements.txt
          pip install -r backend/api/requirements.txt
      
      - name: Lint with flake8
        run: |
          flake8 backend/ --count --show-source --statistics
      
      - name: Run tests
        run: |
          pytest tests/ -v

  build:
    needs: test
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Build Docker images
        run: |
          docker build -t consumer:latest ./backend/consumer
          docker build -t api:latest ./backend/api
          docker build -t publisher:latest ./backend/publisher
      
      - name: Push to registry (optionnel)
        if: github.ref == 'refs/heads/main'
        run: |
          echo "${{ secrets.DOCKER_PASSWORD }}" | docker login -u ${{ secrets.DOCKER_USERNAME }} --password-stdin
          docker push consumer:latest
          docker push api:latest
```

---

#### Tâche 6.4: Test Résilience (3 heures)

**Qu'est-ce que c'est?**

Tester que le système fonctionne même si un service crash.

**Script: scripts/test_resilience.py**:

```python
#!/usr/bin/env python3
"""
Test system resilience
- Pause PostgreSQL
- Verify messages accumulate in RabbitMQ
- Resume PostgreSQL
- Verify zero data loss
"""

import os
import time
import subprocess
import psycopg2
import pika
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def count_messages_in_queue() -> int:
    """Count messages in RabbitMQ queue"""
    try:
        credentials = pika.PlainCredentials('guest', 'guest')
        conn = pika.BlockingConnection(pika.ConnectionParameters(
            'localhost',
            5672,
            '/',
            credentials
        ))
        channel = conn.channel()
        method = channel.queue_declare(queue='navigation_logs', passive=True)
        conn.close()
        return method.method.message_count
    except:
        return -1

def count_records_in_db() -> int:
    """Count records in PostgreSQL"""
    try:
        conn = psycopg2.connect(
            host="localhost",
            database="bi_adaptive",
            user="aibi_user",
            password="changeme"
        )
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM navigation_logs")
        count = cursor.fetchone()[0]
        conn.close()
        return count
    except:
        return -1

def test_resilience():
    logger.info("=== RESILIENCE TEST ===")
    
    # Step 1: Baseline
    logger.info("Step 1: Baseline")
    initial_count = count_records_in_db()
    logger.info(f"Initial records in DB: {initial_count}")
    
    # Step 2: Pause PostgreSQL
    logger.info("Step 2: Pausing PostgreSQL...")
    subprocess.run(["docker-compose", "pause", "postgresql"], check=True)
    time.sleep(5)
    
    # Step 3: Generate traffic (in another process)
    logger.info("Step 3: Generating traffic while DB is down...")
    # Manually click in Metabase or use script
    time.sleep(10)
    
    # Step 4: Check queue has messages
    queue_count = count_messages_in_queue()
    logger.info(f"Messages in queue: {queue_count}")
    assert queue_count > 0, "Queue should have messages!"
    
    # Step 5: Resume PostgreSQL
    logger.info("Step 4: Resuming PostgreSQL...")
    subprocess.run(["docker-compose", "unpause", "postgresql"], check=True)
    time.sleep(10)
    
    # Step 6: Wait for consumer to process queue
    logger.info("Step 5: Waiting for consumer to process queue...")
    time.sleep(20)
    
    # Step 7: Verify zero loss
    logger.info("Step 6: Verifying zero data loss...")
    final_count = count_records_in_db()
    queue_remaining = count_messages_in_queue()
    
    logger.info(f"Final records in DB: {final_count}")
    logger.info(f"Remaining in queue: {queue_remaining}")
    
    # Verify
    assert final_count > initial_count, "Should have new records!"
    assert queue_remaining == 0, "Queue should be empty!"
    
    logger.info("✓ RESILIENCE TEST PASSED")


if __name__ == '__main__':
    test_resilience()
```

---

### PHASE 7: Documentation (Semaine 6) - 6 heures

**Votre rôle**: Documenter l'infrastructure

**Sections à écrire**:

1. **DEPLOYMENT.md**: Comment déployer en production
2. **ARCHITECTURE.md**: Architecture détaillée
3. **TROUBLESHOOTING.md**: Résoudre les problèmes
4. **API.md**: Documentation API

---

## 🎓 CONCEPTS CLÉS À MAÎTRISER

### Docker Concepts

**Image vs Container**:
- Image = Template (class)
- Container = Exécution (instance)

**Dockerfile**:
- `FROM` = Image de base
- `RUN` = Exécuter commande
- `COPY` = Copier fichiers
- `CMD` = Commande par défaut
- `EXPOSE` = Port écouté

**docker-compose**:
- Services = Conteneurs à lancer
- Networks = Connexions entre conteneurs
- Volumes = Stockage persistant
- Environment = Variables d'env

### RabbitMQ Concepts

**Queue**: File d'attente FIFO
**Exchange**: Routeur de messages
**Binding**: Connexion exchange → queue
**Consumer**: Qui écoute la queue
**Publisher**: Qui envoie messages

### PostgreSQL Concepts

**ACID**:
- Atomicity: Tout ou rien
- Consistency: Toujours valide
- Isolation: Pas d'interférence
- Durability: Sauvegardé

**Indexes**: Accélèrent les recherches
**Foreign Keys**: Intégrité referentielle
**ON CONFLICT**: Gestion des doublons

---

## ✅ CHECKLIST PAR PHASE

### Phase 1: Infrastructure
- [ ] Git repo créé
- [ ] docker-compose.yml fonctionne
- [ ] Toutes les tables créées
- [ ] 15+ rapports dans Metabase

### Phase 2: Tracking
- [ ] Publisher authentifie avec Metabase
- [ ] Messages dans RabbitMQ
- [ ] RabbitMQ Management UI accessible

### Phase 3: Pipeline
- [ ] Consumer connecté à RabbitMQ
- [ ] Consumer peut écrire en DB
- [ ] Logs visibles et clairs
- [ ] Test E2E: Metabase → RabbitMQ → DB

### Phase 6: DevOps
- [ ] CI/CD workflow crée
- [ ] Tests passent
- [ ] Docker images buildent
- [ ] Résilience testée

---

## 🚨 ERREURS COMMUNES & SOLUTIONS

### Erreur: "Cannot connect to RabbitMQ"
**Cause**: Service pas démarré ou pas healthy
**Solution**:
```bash
docker-compose logs rabbitmq
docker-compose restart rabbitmq
```

### Erreur: "PostgreSQL connection refused"
**Cause**: Base pas initialisée
**Solution**:
```bash
docker-compose down -v
docker-compose up -d postgresql
docker-compose logs postgresql
```

### Erreur: "Queue already declared with different arguments"
**Cause**: Queue existante avec différentes propriétés
**Solution**:
```bash
# Via RabbitMQ Management UI:
# Admin → Virtual Hosts → delete queue
# Puis relancer
```

---

## 📊 RÉSUMÉ: VOTRE VOYAGE

**Semaine 1** (7h): Lancez l'infrastructure  
**Semaine 2** (6h): Mettez en place le tracking  
**Semaine 2-3** (7h): Construisez le pipeline complet  
**Semaines 4-5** (8h): Intégrez tout  
**Semaines 5-6** (8h): Testez et déployez  

**Au final**: Un système robuste, scalable et résistant aux pannes! 🎉

---

**Vous êtes le "gardien" de l'infrastructure. Sans vous, rien ne fonctionne!**

**Bonne chance! 🚀**
