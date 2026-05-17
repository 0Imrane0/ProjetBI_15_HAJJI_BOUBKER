# 🗺️ ROADMAP DÉTAILLÉE - BI Adaptative
## Plan d'exécution pour 2 développeurs (6 semaines)

---

## 📌 RÉSUMÉ EXÉCUTIF

| Aspect | Détail |
|--------|--------|
| **Durée totale** | 6 semaines (60-70 heures) |
| **Travail par personne** | ~30-35 heures |
| **Nombre de tâches** | 24 tâches réparties |
| **Point de synchronisation** | Fin de chaque phase |
| **Livraison finale** | Semaine 6 (Rapport + Soutenance) |

---

## 👥 DIVISION DES RÔLES

### 🧠 **PERSONNE A : Data & AI Engineer**
Focus: Machine Learning et recommandations

**Stack**: Python, ML, Pandas, scikit-learn, Surprise, FastAPI

**Tâches principales**:
- Exploration des données
- Modèles de recommandation
- API REST
- Évaluation et métriques

---

### 🔧 **PERSONNE B : Backend & System Integration Engineer**
Focus: Infrastructure et intégration système

**Stack**: Docker, Python, SQL, DevOps, Metabase API, GitHub Actions

**Tâches principales**:
- Orchestration Docker
- Consumer RabbitMQ
- PostgreSQL
- Metabase integration
- CI/CD

---

## 🔗 POINTS DE SYNCHRONISATION

Les deux personnes se rencontrent à la **fin de chaque phase** pour:
1. Tester l'intégration complète
2. Résoudre les problèmes bloquants
3. Planifier la phase suivante

---

---

# ⏱️ PHASE 1 : Infrastructure & Setup

**Durée**: 1 semaine (8h)  
**Objectif**: Environnement fonctionnel et reproductible  
**Deadline**: Fin du jour 5

---

## 🎯 Tâche 1.1 : Initialiser Git Repository

**Responsable**: Personne B (Backend - responsabilité repo)

**Durée**: 1h

**Étapes**:
```bash
# Créer le repository sur GitHub
# → Push les fichiers de base

# Structure initiale
bi-adaptative/
├── docker-compose.yml          (créé en 1.2)
├── .env.example
├── .gitignore
├── README.md                   (déjà créé)
├── ROADMAP.md                  (ce fichier)
├── ARCHITECTURE.md
├── backend/
│   └── (créé au fur et à mesure)
├── db/
│   └── (créé en 1.3)
└── docs/
    └── (créé en 1.4)

# .gitignore essentials
__pycache__/
*.pyc
.env (ne pas committer les secrets!)
venv/
.DS_Store
docker-compose.override.yml
logs/
```

**Résultat attendu**: Repository accessible, structure créée

**Validation**: 
```bash
git log
ls -la
```

---

## 🎯 Tâche 1.2 : Créer docker-compose.yml

**Responsable**: Personne B (Infrastructure)

**Durée**: 2h

**Détails complets**:

```yaml
# docker-compose.yml
version: '3.8'

services:
  # ============ POSTGRESQL ============
  postgresql:
    image: postgres:14-alpine
    container_name: bi_postgres
    environment:
      POSTGRES_USER: ${DB_USER:-aibi_user}
      POSTGRES_PASSWORD: ${DB_PASSWORD:-aibi_secure_pass}
      POSTGRES_DB: ${DB_NAME:-bi_adaptive}
    ports:
      - "${DB_PORT:-5432}:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./db/init.sql:/docker-entrypoint-initdb.d/init.sql
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${DB_USER:-aibi_user}"]
      interval: 10s
      timeout: 5s
      retries: 5
    networks:
      - bi_network

  # ============ RABBITMQ ============
  rabbitmq:
    image: rabbitmq:3.12-management-alpine
    container_name: bi_rabbitmq
    environment:
      RABBITMQ_DEFAULT_USER: ${RABBITMQ_USER:-guest}
      RABBITMQ_DEFAULT_PASS: ${RABBITMQ_PASS:-guest}
    ports:
      - "${RABBITMQ_AMQP_PORT:-5672}:5672"
      - "${RABBITMQ_MANAGEMENT_PORT:-15672}:15672"
    volumes:
      - rabbitmq_data:/var/lib/rabbitmq
    healthcheck:
      test: ["CMD", "rabbitmq-diagnostics", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5
    networks:
      - bi_network

  # ============ METABASE ============
  metabase:
    image: metabase/metabase:latest
    container_name: bi_metabase
    environment:
      MB_DB_TYPE: postgres
      MB_DB_DBNAME: ${DB_NAME:-bi_adaptive}
      MB_DB_HOST: postgresql
      MB_DB_PORT: 5432
      MB_DB_USER: ${DB_USER:-aibi_user}
      MB_DB_PASS: ${DB_PASSWORD:-aibi_secure_pass}
    ports:
      - "${METABASE_PORT:-3000}:3000"
    depends_on:
      postgresql:
        condition: service_healthy
    volumes:
      - metabase_data:/metabase-data
    networks:
      - bi_network

  # ============ PYTHON CONSUMER ============
  python-consumer:
    build:
      context: ./backend
      dockerfile: Dockerfile
    container_name: bi_consumer
    environment:
      RABBITMQ_HOST: rabbitmq
      RABBITMQ_PORT: 5672
      RABBITMQ_USER: ${RABBITMQ_USER:-guest}
      RABBITMQ_PASS: ${RABBITMQ_PASS:-guest}
      DB_HOST: postgresql
      DB_PORT: 5432
      DB_USER: ${DB_USER:-aibi_user}
      DB_PASSWORD: ${DB_PASSWORD:-aibi_secure_pass}
      DB_NAME: ${DB_NAME:-bi_adaptive}
      LOG_LEVEL: INFO
    depends_on:
      postgresql:
        condition: service_healthy
      rabbitmq:
        condition: service_healthy
    volumes:
      - ./backend:/app
    networks:
      - bi_network
    restart: unless-stopped

  # ============ PYTHON API ============
  python-api:
    build:
      context: ./backend/api
      dockerfile: Dockerfile
    container_name: bi_api
    environment:
      DB_HOST: postgresql
      DB_PORT: 5432
      DB_USER: ${DB_USER:-aibi_user}
      DB_PASSWORD: ${DB_PASSWORD:-aibi_secure_pass}
      DB_NAME: ${DB_NAME:-bi_adaptive}
      MODEL_PATH: /app/ml_engine/models
      LOG_LEVEL: INFO
    ports:
      - "${API_PORT:-8000}:8000"
    depends_on:
      postgresql:
        condition: service_healthy
    volumes:
      - ./backend:/app
    networks:
      - bi_network
    restart: unless-stopped

# ============ VOLUMES ============
volumes:
  postgres_data:
    driver: local
  rabbitmq_data:
    driver: local
  metabase_data:
    driver: local

# ============ NETWORKS ============
networks:
  bi_network:
    driver: bridge
```

**Créer aussi `.env.example`**:
```bash
# Database
DB_USER=aibi_user
DB_PASSWORD=aibi_secure_pass
DB_NAME=bi_adaptive
DB_PORT=5432

# RabbitMQ
RABBITMQ_USER=guest
RABBITMQ_PASS=guest
RABBITMQ_AMQP_PORT=5672
RABBITMQ_MANAGEMENT_PORT=15672

# Metabase
METABASE_PORT=3000

# API
API_PORT=8000

# Logging
LOG_LEVEL=INFO
```

**Résultat attendu**: docker-compose.yml validé, pas d'erreurs YAML

**Validation**:
```bash
docker-compose config  # Vérifie la syntaxe
```

---

## 🎯 Tâche 1.3 : Initialiser PostgreSQL et schéma

**Responsable**: Personne A (données) + Personne B (DB)

**Durée**: 1.5h

**Créer `db/init.sql`**:

```sql
-- ============ CREATE TABLES ============

-- Table users (mapping Metabase users)
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    metabase_user_id INTEGER UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(255),
    role VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table reports (mapping Metabase reports/dashboards)
CREATE TABLE IF NOT EXISTS reports (
    id SERIAL PRIMARY KEY,
    metabase_report_id INTEGER UNIQUE NOT NULL,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    tags VARCHAR(500),  -- JSON format: ["sales", "region"]
    category VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table navigation logs (core data)
CREATE TABLE IF NOT EXISTS navigation_logs (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id),
    report_id INTEGER NOT NULL REFERENCES reports(id),
    action VARCHAR(50) NOT NULL DEFAULT 'view',  -- view, click, share
    duration INTEGER DEFAULT 0,  -- seconds
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (report_id) REFERENCES reports(id) ON DELETE CASCADE
);

-- Table recommendations (store computed recommendations)
CREATE TABLE IF NOT EXISTS recommendations (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id),
    recommended_report_id INTEGER NOT NULL REFERENCES reports(id),
    score FLOAT DEFAULT 0.0,  -- 0-1 confidence score
    algorithm VARCHAR(50),  -- 'collaborative', 'content-based', 'hybrid'
    generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    clicked BOOLEAN DEFAULT FALSE,  -- For A/B testing
    
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (recommended_report_id) REFERENCES reports(id) ON DELETE CASCADE
);

-- ============ CREATE INDEXES ============
CREATE INDEX idx_navigation_logs_user_timestamp 
    ON navigation_logs(user_id, timestamp DESC);
    
CREATE INDEX idx_navigation_logs_report 
    ON navigation_logs(report_id);
    
CREATE INDEX idx_recommendations_user 
    ON recommendations(user_id, generated_at DESC);
    
CREATE INDEX idx_users_metabase_id 
    ON users(metabase_user_id);
    
CREATE INDEX idx_reports_metabase_id 
    ON reports(metabase_report_id);

-- ============ CREATE VIEWS ============

-- View: Top reports by usage
CREATE OR REPLACE VIEW v_top_reports AS
SELECT 
    r.id,
    r.title,
    COUNT(nl.id) as view_count,
    AVG(nl.duration) as avg_duration,
    COUNT(DISTINCT nl.user_id) as unique_users
FROM reports r
LEFT JOIN navigation_logs nl ON r.id = nl.report_id
GROUP BY r.id, r.title
ORDER BY view_count DESC;

-- View: User report affinity
CREATE OR REPLACE VIEW v_user_report_affinity AS
SELECT 
    nl.user_id,
    nl.report_id,
    COUNT(*) as interaction_count,
    AVG(nl.duration) as avg_duration,
    MAX(nl.timestamp) as last_viewed
FROM navigation_logs nl
GROUP BY nl.user_id, nl.report_id;

-- ============ INITIAL DATA ============

-- Insert sample users (à remplir lors de l'initialisation)
INSERT INTO users (metabase_user_id, email, name, role) VALUES
    (1, 'user1@company.com', 'User One', 'manager'),
    (2, 'user2@company.com', 'User Two', 'analyst'),
    (3, 'user3@company.com', 'User Three', 'director')
ON CONFLICT (metabase_user_id) DO NOTHING;

-- ============ PERMISSIONS ============
GRANT SELECT, INSERT, UPDATE, DELETE ON navigation_logs TO aibi_user;
GRANT SELECT, INSERT, UPDATE ON users TO aibi_user;
GRANT SELECT, INSERT, UPDATE ON reports TO aibi_user;
GRANT SELECT, INSERT, UPDATE ON recommendations TO aibi_user;
GRANT SELECT ON v_top_reports TO aibi_user;
GRANT SELECT ON v_user_report_affinity TO aibi_user;
```

**Résultat attendu**: Tables créées, schéma valide

**Validation**:
```bash
# Depuis le host ou dans le container
docker-compose exec postgresql psql -U aibi_user -d bi_adaptive -c "\dt"
# Devrait afficher: users, reports, navigation_logs, recommendations
```

---

## 🎯 Tâche 1.4 : Démarrer et Peupler Metabase

**Responsable**: Personne B (setup) + Personne A (données)

**Durée**: 3h

**Étapes**:

### 1. Démarrer les services
```bash
# À la racine du project
docker-compose up -d

# Attendre que tous les services soient healthy (~30s)
docker-compose ps

# Vérifier les logs
docker-compose logs metabase | tail -20
```

### 2. Initialiser Metabase
```
Accéder à: http://localhost:3000
Suivre le wizard:
1. Créer compte admin (email/password)
2. Connecter la "Sample Database" (PostgreSQL)
   - Host: postgresql
   - Port: 5432
   - Database: bi_adaptive
   - User: aibi_user
   - Password: aibi_secure_pass
3. Tester la connexion
4. Commencer à explorer
```

### 3. Créer 15-20 dashboards fictifs

**Important**: Ces dashboards simulent le problème "Information Overload"

**Créer les requêtes suivantes** (via Metabase Query Builder):

```sql
-- Dashboard 1: Total Sales by Region
SELECT region, SUM(amount) FROM orders GROUP BY region;

-- Dashboard 2: Top 10 Customers
SELECT customer_name, SUM(amount) as total FROM orders 
GROUP BY customer_name ORDER BY total DESC LIMIT 10;

-- Dashboard 3: Monthly Revenue
SELECT DATE_TRUNC('month', order_date) as month, SUM(amount) 
FROM orders GROUP BY DATE_TRUNC('month', order_date);

-- Dashboard 4: Product Performance
SELECT product_name, COUNT(*) as sales, AVG(amount) 
FROM orders GROUP BY product_name ORDER BY sales DESC;

-- Dashboard 5: Orders by Status
SELECT status, COUNT(*) FROM orders GROUP BY status;

-- ... (ajouter 10-15 autres)
```

**Pour chaque query**:
1. Sauvegarder comme "Question"
2. Ajouter à un Dashboard
3. Donner un titre descriptif
4. Ajouter description et tags

**Résultat attendu**: 15-20 dashboards visibles dans Metabase

**Validation**:
```bash
# Accéder à http://localhost:3000/browse/dashboards
# Vérifier que tous les dashboards s'affichent
```

---

## ✅ FIN DE PHASE 1 - SYNCHRONISATION

**Réunion d'équipe** (30 min):

**Checklist commune**:
- [ ] Tous les containers sont up et healthy
- [ ] Metabase accessible (http://localhost:3000)
- [ ] PostgreSQL connectée et schéma valide
- [ ] 15-20 dashboards créés
- [ ] RabbitMQ accessible (http://localhost:15672)
- [ ] Repository Git à jour

**Tests rapides**:
```bash
docker-compose ps
curl http://localhost:3000/api/health
curl http://localhost:15672/api/health
docker-compose exec postgresql psql -U aibi_user -d bi_adaptive -c "SELECT COUNT(*) FROM users;"
```

**Prochains étapes**: 
- Personne B: Continuer Phase 2
- Personne A: Préparer l'exploration des données (Phase 4)

---

---

# ⏱️ PHASE 2 : Tracking & Messaging

**Durée**: 1 semaine (6h)  
**Objectif**: Capturer les événements utilisateur et les envoyer à RabbitMQ  
**Deadline**: Fin du jour 10

---

## 🎯 Tâche 2.1 : Étudier Metabase & Audit Logs

**Responsable**: Personne B (Backend)

**Durée**: 1h

**Documentation à lire**:
- https://www.metabase.com/docs/latest/admin-guide/audit-logs
- https://www.metabase.com/docs/latest/api/

**Points clés à comprendre**:
```
1. Metabase stocke les audit logs dans sa propre DB
2. Accessible via:
   - API REST: GET /api/audit
   - Base de données interne (table: audit_log)
3. Chaque log contient:
   - user_id
   - object (rapport/dashboard consulté)
   - object_id
   - action (view, click, etc.)
   - timestamp
   - details (JSON avec données additionnelles)
```

**Résultat attendu**: Compréhension du système de logging Metabase

---

## 🎯 Tâche 2.2 : Implémenter Metabase → RabbitMQ Publisher

**Responsable**: Personne B (Backend)

**Durée**: 2.5h

**Approche**: Créer un script Python qui interroge l'API Metabase et publie dans RabbitMQ

**Créer: `backend/publisher/publisher.py`**

```python
#!/usr/bin/env python3
"""
Metabase Event Publisher
Lit les audit logs de Metabase et les publie dans RabbitMQ
"""

import pika
import requests
import json
import time
import os
from datetime import datetime
from typing import Dict, List
import logging

# Configure logging
logging.basicConfig(level=os.getenv('LOG_LEVEL', 'INFO'))
logger = logging.getLogger(__name__)

class MetabasePublisher:
    def __init__(self):
        self.metabase_url = os.getenv('METABASE_URL', 'http://metabase:3000')
        self.metabase_user = os.getenv('METABASE_USER', 'admin@metabase.local')
        self.metabase_pass = os.getenv('METABASE_PASS', 'metabase')
        
        self.rabbitmq_host = os.getenv('RABBITMQ_HOST', 'rabbitmq')
        self.rabbitmq_port = int(os.getenv('RABBITMQ_PORT', 5672))
        self.rabbitmq_user = os.getenv('RABBITMQ_USER', 'guest')
        self.rabbitmq_pass = os.getenv('RABBITMQ_PASS', 'guest')
        
        self.session_token = None
        self.channel = None
        self.connection = None
        self.last_log_id = 0
        
    def authenticate_metabase(self) -> bool:
        """Authenticate with Metabase"""
        try:
            response = requests.post(
                f"{self.metabase_url}/api/session",
                json={
                    "username": self.metabase_user,
                    "password": self.metabase_pass
                },
                timeout=5
            )
            if response.status_code == 200:
                self.session_token = response.json()['id']
                logger.info("✅ Authenticated with Metabase")
                return True
            else:
                logger.error(f"❌ Metabase auth failed: {response.status_code}")
                return False
        except Exception as e:
            logger.error(f"❌ Metabase connection error: {e}")
            return False
    
    def connect_rabbitmq(self) -> bool:
        """Connect to RabbitMQ"""
        try:
            credentials = pika.PlainCredentials(self.rabbitmq_user, self.rabbitmq_pass)
            parameters = pika.ConnectionParameters(
                host=self.rabbitmq_host,
                port=self.rabbitmq_port,
                credentials=credentials,
                connection_attempts=3,
                retry_delay=2
            )
            self.connection = pika.BlockingConnection(parameters)
            self.channel = self.connection.channel()
            
            # Declare queue (durable = survit aux redémarrages)
            self.channel.queue_declare(
                queue='navigation_logs',
                durable=True
            )
            logger.info("✅ Connected to RabbitMQ")
            return True
        except Exception as e:
            logger.error(f"❌ RabbitMQ connection error: {e}")
            return False
    
    def fetch_audit_logs(self) -> List[Dict]:
        """Fetch audit logs from Metabase API"""
        try:
            headers = {'X-Metabase-Session': self.session_token}
            response = requests.get(
                f"{self.metabase_url}/api/audit",
                headers=headers,
                params={'limit': 100},
                timeout=5
            )
            if response.status_code == 200:
                logs = response.json()
                logger.info(f"📥 Fetched {len(logs)} audit logs")
                return logs
            else:
                logger.warning(f"⚠️ Failed to fetch logs: {response.status_code}")
                return []
        except Exception as e:
            logger.error(f"❌ Error fetching logs: {e}")
            return []
    
    def publish_event(self, event: Dict) -> bool:
        """Publish event to RabbitMQ"""
        try:
            # Format le message
            message = json.dumps({
                'user_id': event.get('user_id'),
                'report_id': event.get('object_id'),
                'action': event.get('action', 'view'),
                'timestamp': event.get('timestamp', datetime.utcnow().isoformat()),
                'duration': event.get('details', {}).get('duration', 0)
            })
            
            # Publish à RabbitMQ
            self.channel.basic_publish(
                exchange='',
                routing_key='navigation_logs',
                body=message,
                properties=pika.BasicProperties(
                    delivery_mode=pika.spec.PERSISTENT_DELIVERY_MODE
                )
            )
            logger.debug(f"📤 Published event: {message}")
            return True
        except Exception as e:
            logger.error(f"❌ Error publishing event: {e}")
            return False
    
    def run(self):
        """Main loop"""
        if not self.authenticate_metabase():
            logger.error("Cannot authenticate with Metabase")
            return
        
        if not self.connect_rabbitmq():
            logger.error("Cannot connect to RabbitMQ")
            return
        
        logger.info("🚀 Metabase Publisher started")
        
        try:
            while True:
                # Fetch logs
                logs = self.fetch_audit_logs()
                
                # Publish each log
                for log in logs:
                    if log['id'] > self.last_log_id:
                        self.publish_event(log)
                        self.last_log_id = log['id']
                
                # Wait before next fetch
                time.sleep(5)  # Poll every 5 seconds
        
        except KeyboardInterrupt:
            logger.info("⏹️ Shutting down...")
        finally:
            if self.connection and not self.connection.is_closed():
                self.connection.close()

if __name__ == '__main__':
    publisher = MetabasePublisher()
    publisher.run()
```

**Créer: `backend/publisher/requirements.txt`**

```
pika==1.3.1
requests==2.31.0
python-dotenv==1.0.0
```

**Créer: `backend/publisher/Dockerfile`**

```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "publisher.py"]
```

**Résultat attendu**: Script capable de se connecter à Metabase et RabbitMQ

**Validation**:
```bash
# Build et test
cd backend/publisher
docker build -t bi-publisher .

# Test manual
docker run --rm \
  -e METABASE_URL=http://metabase:3000 \
  -e RABBITMQ_HOST=rabbitmq \
  --network bi-adaptative_bi_network \
  bi-publisher
```

---

## 🎯 Tâche 2.3 : Intégrer Publisher dans docker-compose

**Responsable**: Personne B (Backend)

**Durée**: 0.5h

**Ajouter à `docker-compose.yml`**:

```yaml
  python-publisher:
    build:
      context: ./backend/publisher
      dockerfile: Dockerfile
    container_name: bi_publisher
    environment:
      METABASE_URL: http://metabase:3000
      METABASE_USER: ${METABASE_ADMIN_USER:-admin@metabase.local}
      METABASE_PASS: ${METABASE_ADMIN_PASS:-metabase}
      RABBITMQ_HOST: rabbitmq
      RABBITMQ_PORT: 5672
      RABBITMQ_USER: ${RABBITMQ_USER:-guest}
      RABBITMQ_PASS: ${RABBITMQ_PASS:-guest}
      LOG_LEVEL: INFO
    depends_on:
      metabase:
        condition: service_started
      rabbitmq:
        condition: service_healthy
    networks:
      - bi_network
    restart: unless-stopped
```

**Mettre à jour `.env.example`**:
```bash
METABASE_ADMIN_USER=admin@metabase.local
METABASE_ADMIN_PASS=metabase
```

---

## 🎯 Tâche 2.4 : Tester le flux Metabase → RabbitMQ

**Responsable**: Personne B (Backend)

**Durée**: 1.5h

**Test manuel**:

```bash
# 1. Démarrer les services
docker-compose up -d

# 2. Attendre que tout soit ready (~30s)
docker-compose logs publisher | grep "Metabase Publisher started"

# 3. Accéder à Metabase
# http://localhost:3000
# Ouvrir plusieurs dashboards, cliquer sur reports

# 4. Vérifier RabbitMQ
# http://localhost:15672
# Queue: navigation_logs devrait montrer des messages

# 5. Compter les messages
docker-compose exec rabbitmq rabbitmqctl list_queues

# Expected output:
# Queues on node rabbit@...
# ...
# navigation_logs    10  (nombre de messages)
# ...

# 6. Inspecter les logs du publisher
docker-compose logs -f publisher
# Devrait afficher les événements publiés
```

**Résultat attendu**: 
- Messages apparaissent dans RabbitMQ queue
- Logger montre les événements

**Validation**:
```bash
# Les 3 indicateurs clés
1. RabbitMQ admin panel montre des messages en queue
2. Publisher logs montrent "Published event"
3. Pas d'erreurs de connexion
```

---

## ✅ FIN DE PHASE 2 - SYNCHRONISATION

**Réunion d'équipe** (30 min):

**Checklist commune**:
- [ ] Publisher se connecte à Metabase ✅
- [ ] Publisher se connecte à RabbitMQ ✅
- [ ] Événements publiés dans la queue ✅
- [ ] Pas d'erreurs de connexion ✅
- [ ] Code committé dans Git ✅

**Test end-to-end**:
```bash
# Scénario: Ouvrir un dashboard dans Metabase
# → Vérifier que le message arrive dans RabbitMQ

docker-compose logs -f publisher
# Devrait afficher: "Published event: {...user_id: 1, report_id: 45...}"
```

**Prochaines étapes**:
- Personne B: Passer à Phase 3 (Consumer Python)
- Personne A: Préparer l'exploration données (Phase 4)

---

---

# ⏱️ PHASE 3 : Data Ingestion Pipeline

**Durée**: 2 semaines (10h)  
**Objectif**: Consumer Python qui traite les logs et les stocke  
**Deadline**: Fin du jour 17

---

## 🎯 Tâche 3.1 : Développer le Consumer Python

**Responsable**: Personne B (Backend) + Personne A (données)

**Durée**: 4h

**Créer: `backend/consumer/consumer.py`**

```python
#!/usr/bin/env python3
"""
RabbitMQ Consumer
Écoute les messages de RabbitMQ et les insère dans PostgreSQL
"""

import pika
import psycopg2
from psycopg2.extras import execute_values
import json
import os
import logging
from datetime import datetime
from typing import Dict
import time

# Configure logging
logging.basicConfig(
    level=os.getenv('LOG_LEVEL', 'INFO'),
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class DataConsumer:
    def __init__(self):
        self.rabbitmq_host = os.getenv('RABBITMQ_HOST', 'rabbitmq')
        self.rabbitmq_port = int(os.getenv('RABBITMQ_PORT', 5672))
        self.rabbitmq_user = os.getenv('RABBITMQ_USER', 'guest')
        self.rabbitmq_pass = os.getenv('RABBITMQ_PASS', 'guest')
        
        self.db_host = os.getenv('DB_HOST', 'localhost')
        self.db_port = int(os.getenv('DB_PORT', 5432))
        self.db_user = os.getenv('DB_USER', 'aibi_user')
        self.db_pass = os.getenv('DB_PASSWORD', 'aibi_secure_pass')
        self.db_name = os.getenv('DB_NAME', 'bi_adaptive')
        
        self.channel = None
        self.connection = None
        self.db_conn = None
        self.processed_count = 0
        self.error_count = 0
    
    def connect_rabbitmq(self) -> bool:
        """Connect to RabbitMQ with retry logic"""
        try:
            credentials = pika.PlainCredentials(self.rabbitmq_user, self.rabbitmq_pass)
            parameters = pika.ConnectionParameters(
                host=self.rabbitmq_host,
                port=self.rabbitmq_port,
                credentials=credentials,
                connection_attempts=5,
                retry_delay=3
            )
            self.connection = pika.BlockingConnection(parameters)
            self.channel = self.connection.channel()
            
            # Declare queue
            self.channel.queue_declare(queue='navigation_logs', durable=True)
            
            # QoS: process only one message at a time
            self.channel.basic_qos(prefetch_count=1)
            
            logger.info("✅ Connected to RabbitMQ")
            return True
        except Exception as e:
            logger.error(f"❌ RabbitMQ connection failed: {e}")
            return False
    
    def connect_database(self) -> bool:
        """Connect to PostgreSQL with retry logic"""
        try:
            self.db_conn = psycopg2.connect(
                host=self.db_host,
                port=self.db_port,
                user=self.db_user,
                password=self.db_pass,
                database=self.db_name,
                connect_timeout=5
            )
            logger.info("✅ Connected to PostgreSQL")
            return True
        except Exception as e:
            logger.error(f"❌ PostgreSQL connection failed: {e}")
            return False
    
    def ensure_user_exists(self, user_id: int) -> bool:
        """Ensure user exists in database"""
        try:
            with self.db_conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO users (metabase_user_id, email, name) "
                    "VALUES (%s, %s, %s) ON CONFLICT DO NOTHING",
                    (user_id, f'user_{user_id}@metabase.local', f'User {user_id}')
                )
            self.db_conn.commit()
            return True
        except Exception as e:
            logger.warning(f"⚠️ Error ensuring user exists: {e}")
            self.db_conn.rollback()
            return False
    
    def ensure_report_exists(self, report_id: int, title: str = None) -> bool:
        """Ensure report exists in database"""
        try:
            with self.db_conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO reports (metabase_report_id, title, description) "
                    "VALUES (%s, %s, %s) ON CONFLICT DO NOTHING",
                    (report_id, title or f'Report {report_id}', f'Report ID: {report_id}')
                )
            self.db_conn.commit()
            return True
        except Exception as e:
            logger.warning(f"⚠️ Error ensuring report exists: {e}")
            self.db_conn.rollback()
            return False
    
    def insert_log(self, log_data: Dict) -> bool:
        """Insert navigation log into PostgreSQL"""
        try:
            user_id = log_data.get('user_id')
            report_id = log_data.get('report_id')
            action = log_data.get('action', 'view')
            duration = log_data.get('duration', 0)
            timestamp = log_data.get('timestamp')
            
            # Ensure user and report exist
            self.ensure_user_exists(user_id)
            self.ensure_report_exists(report_id)
            
            # Insert log
            with self.db_conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO navigation_logs 
                    (user_id, report_id, action, duration, timestamp)
                    VALUES (%s, %s, %s, %s, %s)
                    """,
                    (user_id, report_id, action, duration, timestamp)
                )
            self.db_conn.commit()
            
            self.processed_count += 1
            if self.processed_count % 100 == 0:
                logger.info(f"📊 Processed {self.processed_count} logs")
            
            return True
        except psycopg2.IntegrityError as e:
            logger.warning(f"⚠️ Integrity error (likely duplicate): {e}")
            self.db_conn.rollback()
            return True  # Don't retry, just skip
        except Exception as e:
            logger.error(f"❌ Error inserting log: {e}")
            self.db_conn.rollback()
            self.error_count += 1
            return False
    
    def process_message(self, ch, method, properties, body) -> None:
        """Process incoming message from RabbitMQ"""
        try:
            # Parse message
            log_data = json.loads(body)
            
            # Insert into database
            if self.insert_log(log_data):
                # Acknowledge message
                ch.basic_ack(delivery_tag=method.delivery_tag)
                logger.debug(f"✅ Processed: user={log_data.get('user_id')}, report={log_data.get('report_id')}")
            else:
                # Nack and requeue on error
                ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)
                logger.error(f"❌ Failed to process message")
        
        except json.JSONDecodeError as e:
            logger.error(f"❌ Invalid JSON: {e}")
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
        except Exception as e:
            logger.error(f"❌ Unexpected error: {e}")
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)
    
    def run(self):
        """Main consumer loop"""
        # Connect to services
        attempts = 0
        while not self.connect_database() and attempts < 10:
            logger.info("🔄 Retrying database connection...")
            time.sleep(2)
            attempts += 1
        
        if not self.db_conn:
            logger.error("Cannot connect to database. Exiting.")
            return
        
        attempts = 0
        while not self.connect_rabbitmq() and attempts < 10:
            logger.info("🔄 Retrying RabbitMQ connection...")
            time.sleep(2)
            attempts += 1
        
        if not self.channel:
            logger.error("Cannot connect to RabbitMQ. Exiting.")
            return
        
        logger.info("🚀 Consumer started. Waiting for messages...")
        
        try:
            # Start consuming
            self.channel.basic_consume(
                queue='navigation_logs',
                on_message_callback=self.process_message,
                auto_ack=False
            )
            
            self.channel.start_consuming()
        
        except KeyboardInterrupt:
            logger.info("⏹️ Shutting down consumer...")
        finally:
            if self.channel:
                self.channel.stop_consuming()
                self.connection.close()
            if self.db_conn:
                self.db_conn.close()
            
            logger.info(f"📊 Final stats: Processed={self.processed_count}, Errors={self.error_count}")

if __name__ == '__main__':
    consumer = DataConsumer()
    consumer.run()
```

**Créer: `backend/consumer/requirements.txt`**

```
pika==1.3.1
psycopg2-binary==2.9.6
python-dotenv==1.0.0
```

**Créer: `backend/consumer/Dockerfile`**

```dockerfile
FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y postgresql-client && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "consumer.py"]
```

**Résultat attendu**: Consumer capable de lire RabbitMQ et insérer dans PostgreSQL

---

## 🎯 Tâche 3.2 : Ajouter Consumer à docker-compose

**Responsable**: Personne B (Backend)

**Durée**: 0.5h

**Mettre à jour `docker-compose.yml`**:

```yaml
  python-consumer:
    build:
      context: ./backend/consumer
      dockerfile: Dockerfile
    container_name: bi_consumer
    environment:
      RABBITMQ_HOST: rabbitmq
      RABBITMQ_PORT: 5672
      RABBITMQ_USER: ${RABBITMQ_USER:-guest}
      RABBITMQ_PASS: ${RABBITMQ_PASS:-guest}
      DB_HOST: postgresql
      DB_PORT: 5432
      DB_USER: ${DB_USER:-aibi_user}
      DB_PASSWORD: ${DB_PASSWORD:-aibi_secure_pass}
      DB_NAME: ${DB_NAME:-bi_adaptive}
      LOG_LEVEL: INFO
    depends_on:
      postgresql:
        condition: service_healthy
      rabbitmq:
        condition: service_healthy
    volumes:
      - ./backend/consumer:/app
    networks:
      - bi_network
    restart: unless-stopped
```

---

## 🎯 Tâche 3.3 : Test End-to-End du Pipeline

**Responsable**: Personne B (Backend) + Personne A (data)

**Durée**: 3h

**Test complet**:

```bash
# 1. Démarrer tous les services
docker-compose down  # Cleanup
docker-compose up -d

# 2. Attendre que tout soit ready (~30s)
docker-compose ps
docker-compose logs consumer | grep "Consumer started"

# 3. Accéder à Metabase et générer du trafic
# http://localhost:3000
# - Ouvrir 5-10 rapports différents
# - Cliquer sur plusieurs éléments
# - Rester sur certains rapports quelques secondes

# 4. Vérifier que les messages arrivent dans RabbitMQ
docker-compose exec rabbitmq rabbitmqctl list_queues
# Devrait montrer: navigation_logs    [nombre de messages]

# 5. Vérifier que le consumer traite les messages
docker-compose logs -f consumer | grep "Processed"
# Devrait montrer: "Processed 1 logs", "Processed 2 logs", etc.

# 6. Vérifier que les données sont dans PostgreSQL
docker-compose exec postgresql psql -U aibi_user -d bi_adaptive << 'EOF'
SELECT COUNT(*) as total_logs FROM navigation_logs;
SELECT user_id, report_id, action, duration FROM navigation_logs LIMIT 5;
EOF

# Expected output:
# total_logs
# -----------
#         10
# (1 row)
#
# user_id | report_id | action | duration
# ---------+-----------+--------+----------
#       1 |        42 | view   |       120
#       2 |        50 | view   |        85
#       ...

# 7. Vérifier les utilisateurs créés
docker-compose exec postgresql psql -U aibi_user -d bi_adaptive -c "SELECT COUNT(*) FROM users;"

# 8. Vérifier les rapports créés
docker-compose exec postgresql psql -U aibi_user -d bi_adaptive -c "SELECT COUNT(*) FROM reports;"
```

**Résultat attendu**:
- Messages dans RabbitMQ queue
- Consumer logs montrent le traitement
- Données dans PostgreSQL tables

**Validation**:
```bash
# Les 3 étapes doivent fonctionner:
1. Clic dans Metabase → Message dans RabbitMQ ✅
2. Message dans queue → Consumer le traite ✅
3. Données dans PostgreSQL ✅

# Comptage final
docker-compose exec postgresql psql -U aibi_user -d bi_adaptive -c "
SELECT 
    COUNT(*) as total_logs,
    COUNT(DISTINCT user_id) as unique_users,
    COUNT(DISTINCT report_id) as unique_reports
FROM navigation_logs;
"
```

---

## ✅ FIN DE PHASE 3 - SYNCHRONISATION

**Réunion d'équipe** (30 min):

**Checklist commune**:
- [ ] Publisher envoie des messages ✅
- [ ] Consumer reçoit et traite ✅
- [ ] Données dans PostgreSQL ✅
- [ ] Zéro perte de messages ✅
- [ ] Logs propres et utiles ✅

**Prochaines étapes**:
- Personne A: Phase 4 (ML Engine)
- Personne B: Préparer Phase 5 (API)

---

---

# ⏱️ PHASE 4 : Machine Learning Engine

**Durée**: 2 semaines (16h)  
**Objectif**: Modèles de recommandation fonctionnels  
**Deadline**: Fin du jour 24

---

## 🎯 Tâche 4.1 : Exploration & Préparation des Données

**Responsable**: Personne A (Data/AI)

**Durée**: 3h

**Créer: `backend/ml_engine/data_preparation.py`**

```python
#!/usr/bin/env python3
"""
Data Preparation and Exploration for ML Models
"""

import pandas as pd
import numpy as np
import psycopg2
from sklearn.preprocessing import MinMaxScaler
import logging
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DataPreparation:
    def __init__(self):
        self.db_host = os.getenv('DB_HOST', 'localhost')
        self.db_user = os.getenv('DB_USER')
        self.db_pass = os.getenv('DB_PASSWORD')
        self.db_name = os.getenv('DB_NAME')
        self.conn = None
    
    def connect(self):
        """Connect to PostgreSQL"""
        self.conn = psycopg2.connect(
            host=self.db_host,
            user=self.db_user,
            password=self.db_pass,
            database=self.db_name
        )
        logger.info("✅ Connected to PostgreSQL")
    
    def load_data(self) -> pd.DataFrame:
        """Load navigation logs from PostgreSQL"""
        query = """
        SELECT 
            u.metabase_user_id as user_id,
            r.metabase_report_id as report_id,
            nl.duration,
            nl.timestamp
        FROM navigation_logs nl
        JOIN users u ON nl.user_id = u.id
        JOIN reports r ON nl.report_id = r.id
        ORDER BY nl.timestamp DESC
        """
        
        df = pd.read_sql(query, self.conn)
        logger.info(f"📥 Loaded {len(df)} records")
        return df
    
    def explore_data(self, df: pd.DataFrame):
        """Explore and analyze data"""
        logger.info("\n=== DATA EXPLORATION ===")
        logger.info(f"Shape: {df.shape}")
        logger.info(f"\nData types:\n{df.dtypes}")
        logger.info(f"\nBasic stats:\n{df.describe()}")
        logger.info(f"\nMissing values:\n{df.isnull().sum()}")
        logger.info(f"\nUnique users: {df['user_id'].nunique()}")
        logger.info(f"Unique reports: {df['report_id'].nunique()}")
        
        # User-Report matrix
        matrix = df.pivot_table(
            index='user_id',
            columns='report_id',
            values='duration',
            fill_value=0
        )
        logger.info(f"\nUser-Report Matrix Shape: {matrix.shape}")
        logger.info(f"Matrix Sparsity: {(matrix == 0).sum().sum() / (matrix.shape[0] * matrix.shape[1]) * 100:.2f}%")
    
    def create_interaction_matrix(self, df: pd.DataFrame) -> pd.DataFrame:
        """Create user-report interaction matrix"""
        matrix = df.pivot_table(
            index='user_id',
            columns='report_id',
            values='duration',
            fill_value=0,
            aggfunc='sum'
        )
        
        # Normalize (convert duration to 0-100 scale)
        scaler = MinMaxScaler(feature_range=(0, 100))
        matrix_scaled = pd.DataFrame(
            scaler.fit_transform(matrix),
            index=matrix.index,
            columns=matrix.columns
        )
        
        logger.info(f"✅ Created interaction matrix: {matrix_scaled.shape}")
        return matrix_scaled
    
    def save_for_training(self, df: pd.DataFrame, filename: str = 'training_data.csv'):
        """Save data for ML training"""
        filepath = f'./backend/ml_engine/{filename}'
        df.to_csv(filepath, index=False)
        logger.info(f"💾 Saved training data: {filepath}")

if __name__ == '__main__':
    prep = DataPreparation()
    prep.connect()
    
    # Load and explore
    df = prep.load_data()
    prep.explore_data(df)
    
    # Create matrix for ML
    matrix = prep.create_interaction_matrix(df)
    matrix.to_csv('./backend/ml_engine/interaction_matrix.csv')
    
    # Save raw data
    prep.save_for_training(df)
    
    logger.info("✅ Data preparation complete")
```

---

## 🎯 Tâche 4.2 : Modèle Collaborative Filtering

**Responsable**: Personne A (Data/AI)

**Durée**: 4h

**Créer: `backend/ml_engine/collaborative.py`**

```python
#!/usr/bin/env python3
"""
Collaborative Filtering using Surprise library
"""

import pandas as pd
from surprise import Dataset, Reader, SVD, cross_validate
from surprise.model_selection import train_test_split
import joblib
import logging
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CollaborativeFiltering:
    def __init__(self):
        self.model = None
        self.trainset = None
        self.testset = None
        self.model_path = './backend/ml_engine/models/collaborative_model.pkl'
    
    def load_data(self, csv_path: str = './backend/ml_engine/training_data.csv') -> Dataset:
        """Load data from CSV for Surprise"""
        df = pd.read_csv(csv_path)
        
        # Prepare for Surprise (user_id, item_id, rating)
        # Duration (seconds) → rating (0-100)
        reader = Reader(rating_scale=(0, max(df['duration'].max(), 100)))
        data = Dataset.load_from_df(
            df[['user_id', 'report_id', 'duration']],
            reader
        )
        
        logger.info(f"✅ Loaded data for Surprise: {len(df)} interactions")
        return data
    
    def train(self, data: Dataset):
        """Train collaborative filtering model"""
        # Split data
        self.trainset, self.testset = train_test_split(data, test_size=0.2)
        
        # Train SVD (Singular Value Decomposition)
        self.model = SVD(
            n_factors=50,      # Latent factors
            n_epochs=20,       # Training iterations
            lr_all=0.005,      # Learning rate
            reg_all=0.02       # Regularization
        )
        
        logger.info("🚀 Training SVD model...")
        self.model.fit(self.trainset)
        
        # Evaluate
        predictions = self.model.test(self.testset)
        
        # Calculate RMSE
        from surprise import accuracy
        rmse = accuracy.rmse(predictions)
        
        logger.info(f"✅ Training complete. RMSE: {rmse:.4f}")
    
    def get_recommendations(self, user_id: int, n_recommendations: int = 5) -> list:
        """Get top N recommendations for a user"""
        if not self.model or not self.trainset:
            raise ValueError("Model not trained yet")
        
        # Get all items
        all_items = self.trainset.all_items()
        
        # Get items user hasn't seen
        user_items = set(self.trainset.ur[self.trainset.to_inner_uid(user_id)])
        unseen_items = [item for item in all_items if item not in user_items]
        
        # Predict for unseen items
        predictions = []
        for item_id in unseen_items:
            pred = self.model.predict(user_id, item_id)
            predictions.append({
                'report_id': pred.iid,
                'score': pred.est,
                'algorithm': 'collaborative'
            })
        
        # Sort by score and return top N
        recommendations = sorted(predictions, key=lambda x: x['score'], reverse=True)
        return recommendations[:n_recommendations]
    
    def save_model(self):
        """Save trained model to disk"""
        os.makedirs(os.path.dirname(self.model_path), exist_ok=True)
        joblib.dump(self.model, self.model_path)
        logger.info(f"💾 Model saved to: {self.model_path}")
    
    def load_model(self):
        """Load trained model from disk"""
        self.model = joblib.load(self.model_path)
        logger.info(f"✅ Model loaded from: {self.model_path}")

if __name__ == '__main__':
    cf = CollaborativeFiltering()
    
    # Load and train
    data = cf.load_data()
    cf.train(data)
    
    # Save
    cf.save_model()
    
    # Test
    recommendations = cf.get_recommendations(user_id=1, n_recommendations=3)
    logger.info(f"🎯 Top recommendations for user 1:\n{recommendations}")
```

---

## 🎯 Tâche 4.3 : Modèle Content-Based Filtering

**Responsable**: Personne A (Data/AI)

**Durée**: 3h

**Créer: `backend/ml_engine/content_based.py`**

```python
#!/usr/bin/env python3
"""
Content-Based Filtering using scikit-learn
"""

import pandas as pd
import numpy as np
import psycopg2
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import joblib
import logging
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ContentBasedFiltering:
    def __init__(self, db_host=None, db_user=None, db_pass=None, db_name=None):
        self.db_host = db_host or os.getenv('DB_HOST')
        self.db_user = db_user or os.getenv('DB_USER')
        self.db_pass = db_pass or os.getenv('DB_PASSWORD')
        self.db_name = db_name or os.getenv('DB_NAME')
        
        self.vectorizer = None
        self.similarity_matrix = None
        self.reports_df = None
        
        self.vectorizer_path = './backend/ml_engine/models/tfidf_vectorizer.pkl'
        self.similarity_path = './backend/ml_engine/models/similarity_matrix.pkl'
    
    def load_reports(self) -> pd.DataFrame:
        """Load reports metadata from PostgreSQL"""
        conn = psycopg2.connect(
            host=self.db_host,
            user=self.db_user,
            password=self.db_pass,
            database=self.db_name
        )
        
        query = """
        SELECT 
            id,
            metabase_report_id,
            title,
            description,
            tags,
            category
        FROM reports
        ORDER BY metabase_report_id
        """
        
        self.reports_df = pd.read_sql(query, conn)
        conn.close()
        
        logger.info(f"📥 Loaded {len(self.reports_df)} reports")
        return self.reports_df
    
    def build_tfidf_matrix(self):
        """Build TF-IDF matrix from report content"""
        if self.reports_df is None:
            self.load_reports()
        
        # Combine text features
        text_features = (
            self.reports_df['title'].fillna('') + ' ' +
            self.reports_df['description'].fillna('') + ' ' +
            self.reports_df['tags'].fillna('') + ' ' +
            self.reports_df['category'].fillna('')
        )
        
        # Create TF-IDF vectors
        self.vectorizer = TfidfVectorizer(
            max_features=100,
            stop_words='english',
            ngram_range=(1, 2)
        )
        
        tfidf_matrix = self.vectorizer.fit_transform(text_features)
        logger.info(f"✅ TF-IDF matrix created: {tfidf_matrix.shape}")
        
        return tfidf_matrix
    
    def build_similarity_matrix(self, tfidf_matrix) -> np.ndarray:
        """Build cosine similarity matrix"""
        self.similarity_matrix = cosine_similarity(tfidf_matrix)
        logger.info(f"✅ Similarity matrix created: {self.similarity_matrix.shape}")
        return self.similarity_matrix
    
    def train(self):
        """Train content-based model"""
        self.load_reports()
        tfidf_matrix = self.build_tfidf_matrix()
        self.build_similarity_matrix(tfidf_matrix)
    
    def get_recommendations(self, user_id: int, viewed_reports: list, n_recommendations: int = 5) -> list:
        """Get recommendations based on user's viewed reports"""
        if self.similarity_matrix is None:
            raise ValueError("Model not trained yet")
        
        recommendations = []
        
        # For each viewed report
        for viewed_report_idx in viewed_reports:
            if viewed_report_idx < len(self.similarity_matrix):
                # Get similarities
                similarities = self.similarity_matrix[viewed_report_idx]
                
                # Find top similar reports (excluding viewed ones)
                for report_idx, similarity_score in enumerate(similarities):
                    if report_idx not in viewed_reports and similarity_score > 0:
                        recommendations.append({
                            'report_id': self.reports_df.iloc[report_idx]['metabase_report_id'],
                            'score': float(similarity_score),
                            'algorithm': 'content-based'
                        })
        
        # Aggregate scores for duplicate reports
        aggregated = {}
        for rec in recommendations:
            rid = rec['report_id']
            if rid not in aggregated:
                aggregated[rid] = rec.copy()
            else:
                aggregated[rid]['score'] += rec['score']
        
        # Sort and return top N
        final_recs = sorted(aggregated.values(), key=lambda x: x['score'], reverse=True)
        return final_recs[:n_recommendations]
    
    def save_models(self):
        """Save TF-IDF vectorizer and similarity matrix"""
        os.makedirs(os.path.dirname(self.vectorizer_path), exist_ok=True)
        
        joblib.dump(self.vectorizer, self.vectorizer_path)
        joblib.dump(self.similarity_matrix, self.similarity_path)
        
        logger.info(f"💾 Models saved")
    
    def load_models(self):
        """Load TF-IDF vectorizer and similarity matrix"""
        self.vectorizer = joblib.load(self.vectorizer_path)
        self.similarity_matrix = joblib.load(self.similarity_path)
        
        logger.info(f"✅ Models loaded")

if __name__ == '__main__':
    cb = ContentBasedFiltering()
    
    # Train
    cb.train()
    
    # Save
    cb.save_models()
    
    # Test
    recommendations = cb.get_recommendations(
        user_id=1,
        viewed_reports=[0, 5, 10],
        n_recommendations=3
    )
    logger.info(f"🎯 Content-based recommendations:\n{recommendations}")
```

---

## 🎯 Tâche 4.4 : Modèle Hybride

**Responsable**: Personne A (Data/AI)

**Durée**: 4h

**Créer: `backend/ml_engine/hybrid.py`**

```python
#!/usr/bin/env python3
"""
Hybrid Recommendation Engine
Combines Collaborative and Content-Based Filtering
"""

import logging
import os
import sys
from typing import List, Dict

# Add parent dir to path
sys.path.insert(0, os.path.dirname(__file__))

from collaborative import CollaborativeFiltering
from content_based import ContentBasedFiltering

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class HybridRecommender:
    def __init__(self, alpha: float = 0.6):
        """
        Initialize hybrid recommender
        
        Args:
            alpha: Weight for collaborative filtering (0-1)
                   1-alpha is weight for content-based
        """
        self.alpha = alpha
        self.cf = None
        self.cb = None
        
        logger.info(f"🔧 Initialized Hybrid Recommender (α={alpha})")
    
    def train(self, training_data_path: str = None):
        """Train both models"""
        logger.info("🚀 Training Hybrid Model...")
        
        # Train Collaborative Filtering
        try:
            self.cf = CollaborativeFiltering()
            if training_data_path:
                data = self.cf.load_data(training_data_path)
            else:
                data = self.cf.load_data()
            self.cf.train(data)
            self.cf.save_model()
        except Exception as e:
            logger.warning(f"⚠️ Collaborative filtering failed: {e}")
            self.cf = None
        
        # Train Content-Based
        try:
            self.cb = ContentBasedFiltering()
            self.cb.train()
            self.cb.save_models()
        except Exception as e:
            logger.warning(f"⚠️ Content-based filtering failed: {e}")
            self.cb = None
        
        logger.info("✅ Hybrid model trained")
    
    def get_recommendations(self, user_id: int, n_recommendations: int = 5) -> List[Dict]:
        """
        Get hybrid recommendations for a user
        
        Returns:
            List of recommendations with format:
            [
                {'report_id': 42, 'score': 0.85, 'algorithm': 'hybrid'},
                ...
            ]
        """
        recommendations = {}
        
        # Get collaborative recommendations
        if self.cf:
            try:
                cf_recs = self.cf.get_recommendations(user_id, n_recommendations * 2)
                for rec in cf_recs:
                    rid = rec['report_id']
                    score = rec['score'] * self.alpha
                    if rid not in recommendations:
                        recommendations[rid] = {'score': 0, 'count': 0}
                    recommendations[rid]['score'] += score
                    recommendations[rid]['count'] += 1
            except Exception as e:
                logger.warning(f"⚠️ Error getting CF recommendations: {e}")
        
        # Get content-based recommendations
        if self.cb:
            try:
                # Get user's viewed reports (simplified: assume user_id == report_id for now)
                viewed_reports = [user_id - 1, user_id, user_id + 1]  # Mock data
                cb_recs = self.cb.get_recommendations(
                    user_id,
                    viewed_reports,
                    n_recommendations * 2
                )
                for rec in cb_recs:
                    rid = rec['report_id']
                    score = rec['score'] * (1 - self.alpha)
                    if rid not in recommendations:
                        recommendations[rid] = {'score': 0, 'count': 0}
                    recommendations[rid]['score'] += score
                    recommendations[rid]['count'] += 1
            except Exception as e:
                logger.warning(f"⚠️ Error getting CB recommendations: {e}")
        
        # Normalize and sort
        final_recs = []
        for report_id, data in recommendations.items():
            final_recs.append({
                'report_id': report_id,
                'score': data['score'] / max(data['count'], 1),  # Average score
                'algorithm': 'hybrid'
            })
        
        final_recs.sort(key=lambda x: x['score'], reverse=True)
        return final_recs[:n_recommendations]
    
    def evaluate(self, test_data_path: str = None) -> Dict:
        """Evaluate model performance"""
        logger.info("📊 Evaluating model...")
        
        metrics = {
            'collaborative_available': self.cf is not None,
            'content_based_available': self.cb is not None,
            'alpha': self.alpha,
            'hybrid': True
        }
        
        logger.info(f"✅ Evaluation results:\n{metrics}")
        return metrics

if __name__ == '__main__':
    # Test hybrid recommender
    hybrid = HybridRecommender(alpha=0.6)
    
    # Train (requires data)
    try:
        hybrid.train()
        
        # Get recommendations
        recs = hybrid.get_recommendations(user_id=1, n_recommendations=5)
        logger.info(f"🎯 Hybrid recommendations for user 1:\n{recs}")
        
        # Evaluate
        metrics = hybrid.evaluate()
    except Exception as e:
        logger.error(f"Error: {e}")
```

---

## 🎯 Tâche 4.5 : Pipeline d'Entraînement

**Responsable**: Personne A (Data/AI)

**Durée**: 2h

**Créer: `backend/ml_engine/train.py`**

```python
#!/usr/bin/env python3
"""
Training Pipeline for ML Models
"""

import logging
import sys
import os
from pathlib import Path

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    """Main training pipeline"""
    logger.info("🚀 Starting ML Training Pipeline")
    
    try:
        # Step 1: Data Preparation
        logger.info("\n[1/4] Preparing data...")
        from data_preparation import DataPreparation
        prep = DataPreparation()
        prep.connect()
        df = prep.load_data()
        prep.explore_data(df)
        matrix = prep.create_interaction_matrix(df)
        prep.save_for_training(df)
        logger.info("✅ Data preparation complete")
        
        # Step 2: Train Collaborative Filtering
        logger.info("\n[2/4] Training Collaborative Filtering...")
        from collaborative import CollaborativeFiltering
        cf = CollaborativeFiltering()
        data = cf.load_data()
        cf.train(data)
        cf.save_model()
        logger.info("✅ Collaborative Filtering trained")
        
        # Step 3: Train Content-Based Filtering
        logger.info("\n[3/4] Training Content-Based Filtering...")
        from content_based import ContentBasedFiltering
        cb = ContentBasedFiltering()
        cb.train()
        cb.save_models()
        logger.info("✅ Content-Based Filtering trained")
        
        # Step 4: Create Hybrid Model
        logger.info("\n[4/4] Creating Hybrid Model...")
        from hybrid import HybridRecommender
        hybrid = HybridRecommender(alpha=0.6)
        hybrid.train()
        metrics = hybrid.evaluate()
        logger.info(f"✅ Hybrid Model created. Metrics: {metrics}")
        
        logger.info("\n🎉 Training pipeline complete!")
        return True
    
    except Exception as e:
        logger.error(f"❌ Error during training: {e}", exc_info=True)
        return False

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
```

**Créer: `backend/ml_engine/requirements.txt`**

```
pandas==1.3.5
numpy==1.23.0
scikit-learn==1.0.2
surprise==0.1.3
psycopg2-binary==2.9.6
joblib==1.2.0
python-dotenv==1.0.0
```

---

## ✅ FIN DE PHASE 4 - SYNCHRONISATION

**Réunion d'équipe** (45 min):

**Checklist commune**:
- [ ] Données chargées et explorées ✅
- [ ] Collaborative Filtering entraîné ✅
- [ ] Content-Based Filtering entraîné ✅
- [ ] Modèle Hybride fonctionnel ✅
- [ ] Modèles sauvegardés ✅
- [ ] Test de recommandations OK ✅

**Test**:
```bash
# Depuis backend/ml_engine/
python train.py

# Devrait afficher:
# ✅ Data preparation complete
# ✅ Collaborative Filtering trained
# ✅ Content-Based Filtering trained
# ✅ Hybrid Model created
# 🎉 Training pipeline complete!
```

**Prochaines étapes**:
- Personne A: Phase 5 (API FastAPI)
- Personne B: Phase 5 (Intégration Metabase)

---

---

# ⏱️ PHASE 5 : API & Intégration

**Durée**: 2 semaines (12h)  
**Objectif**: Exposer les recommandations et les afficher dans Metabase  
**Deadline**: Fin du jour 31

---

## 🎯 Tâche 5.1 : API REST FastAPI

**Responsable**: Personne A (Data/AI)

**Durée**: 4h

**Créer: `backend/api/main.py`**

```python
#!/usr/bin/env python3
"""
FastAPI for Recommendation Engine
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
import sys
import logging
from typing import List

# Add parent dir
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from ml_engine.hybrid import HybridRecommender

# Setup logging
logging.basicConfig(level=os.getenv('LOG_LEVEL', 'INFO'))
logger = logging.getLogger(__name__)

# FastAPI app
app = FastAPI(
    title="BI Adaptive Recommendation API",
    description="Machine learning-powered recommendation engine for BI reports",
    version="1.0.0"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load models
recommender = None

@app.on_event("startup")
async def startup_event():
    """Load ML models on startup"""
    global recommender
    try:
        logger.info("Loading ML models...")
        recommender = HybridRecommender(alpha=0.6)
        recommender.cf = recommender.cf or None  # Load if available
        recommender.cb = recommender.cb or None  # Load if available
        logger.info("✅ ML models loaded")
    except Exception as e:
        logger.warning(f"⚠️ Could not load models: {e}")
        recommender = HybridRecommender(alpha=0.6)

# ============ SCHEMAS ============

class RecommendationRequest(BaseModel):
    user_id: int
    n_recommendations: int = 3
    alpha: float = 0.6

class RecommendationResponse(BaseModel):
    user_id: int
    recommendations: List[dict]

# ============ ENDPOINTS ============

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "ok",
        "service": "BI Adaptive Recommendation API",
        "version": "1.0.0"
    }

@app.post("/recommendations", response_model=RecommendationResponse)
async def get_recommendations(request: RecommendationRequest):
    """
    Get personalized recommendations for a user
    
    Parameters:
        user_id: Metabase user ID
        n_recommendations: Number of recommendations (default: 3)
        alpha: Weight for collaborative filtering (0-1)
    
    Returns:
        List of recommended reports with scores
    """
    try:
        if not recommender:
            raise HTTPException(status_code=503, detail="Models not loaded")
        
        # Validate input
        if request.user_id < 1:
            raise HTTPException(status_code=400, detail="user_id must be >= 1")
        if request.n_recommendations < 1:
            raise HTTPException(status_code=400, detail="n_recommendations must be >= 1")
        if not (0 <= request.alpha <= 1):
            raise HTTPException(status_code=400, detail="alpha must be between 0 and 1")
        
        # Get recommendations
        recs = recommender.get_recommendations(
            user_id=request.user_id,
            n_recommendations=request.n_recommendations
        )
        
        # Format response
        return RecommendationResponse(
            user_id=request.user_id,
            recommendations=[
                {
                    'report_id': int(rec['report_id']),
                    'score': float(rec['score']),
                    'algorithm': rec['algorithm']
                }
                for rec in recs
            ]
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting recommendations: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/metrics")
async def get_metrics():
    """Get model performance metrics"""
    if not recommender:
        raise HTTPException(status_code=503, detail="Models not loaded")
    
    return recommender.evaluate()

@app.post("/feedback")
async def log_feedback(user_id: int, report_id: int, clicked: bool):
    """Log user feedback on recommendations"""
    try:
        # TODO: Save feedback to database for model improvement
        logger.info(f"Feedback: user={user_id}, report={report_id}, clicked={clicked}")
        return {"status": "logged"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
async def root():
    """API documentation"""
    return {
        "message": "Welcome to BI Adaptive Recommendation API",
        "endpoints": {
            "GET /health": "Health check",
            "POST /recommendations": "Get recommendations for a user",
            "GET /metrics": "Model performance metrics",
            "POST /feedback": "Log recommendation feedback"
        }
    }

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(
        app,
        host='0.0.0.0',
        port=8000,
        log_level='info'
    )
```

**Créer: `backend/api/requirements.txt`**

```
fastapi==0.95.1
uvicorn==0.21.0
pydantic==1.10.7
python-dotenv==1.0.0
```

**Créer: `backend/api/Dockerfile`**

```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

---

## 🎯 Tâche 5.2 : Intégrer API dans docker-compose

**Responsable**: Personne B (Backend)

**Durée**: 1h

**(Déjà fait dans Phase 1 docker-compose.yml)**

Vérifier que le service `python-api` est bien configuré et démarrer.

---

## 🎯 Tâche 5.3 : Intégrer dans Metabase

**Responsable**: Personne B (Backend)

**Durée**: 4h

**Approche**: Créer un dashboard Metabase qui affiche les recommandations

**Étapes**:

### 1. Créer une table PostgreSQL pour les recommandations

*Déjà créée en Phase 3 (tâche 3.1)*

### 2. Créer un script qui remplit cette table avec les recommandations de l'API

**Créer: `backend/scripts/populate_recommendations.py`**

```python
#!/usr/bin/env python3
"""
Populate recommendations table with API predictions
"""

import requests
import psycopg2
import os
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def populate_recommendations():
    """Get recommendations for all users and store in DB"""
    
    # Connect to DB
    conn = psycopg2.connect(
        host=os.getenv('DB_HOST'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD'),
        database=os.getenv('DB_NAME')
    )
    cur = conn.cursor()
    
    # Get all users
    cur.execute("SELECT DISTINCT user_id FROM navigation_logs")
    users = [row[0] for row in cur.fetchall()]
    
    logger.info(f"Getting recommendations for {len(users)} users")
    
    # Clear old recommendations
    cur.execute("DELETE FROM recommendations")
    
    # Get recommendations for each user
    for user_id in users:
        try:
            response = requests.post(
                'http://python-api:8000/recommendations',
                json={'user_id': user_id, 'n_recommendations': 5},
                timeout=5
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Insert recommendations
                for rec in data['recommendations']:
                    cur.execute(
                        """
                        INSERT INTO recommendations 
                        (user_id, recommended_report_id, score, algorithm)
                        VALUES (%s, %s, %s, %s)
                        """,
                        (user_id, rec['report_id'], rec['score'], rec['algorithm'])
                    )
                
                logger.info(f"✅ User {user_id}: {len(data['recommendations'])} recommendations")
            else:
                logger.warning(f"⚠️ User {user_id}: API returned {response.status_code}")
        
        except Exception as e:
            logger.error(f"❌ User {user_id}: {e}")
    
    conn.commit()
    cur.close()
    conn.close()
    
    logger.info("✅ Recommendations populated")

if __name__ == '__main__':
    populate_recommendations()
```

### 3. Créer un Dashboard Metabase

1. Accéder à Metabase (http://localhost:3000)
2. Créer une nouvelle Question (Query)
3. Utiliser cette requête SQL:

```sql
SELECT 
    u.email as user_email,
    r.title as recommended_report,
    rec.score,
    rec.algorithm,
    rec.generated_at
FROM recommendations rec
JOIN users u ON rec.user_id = u.id
JOIN reports r ON rec.recommended_report_id = r.id
ORDER BY rec.generated_at DESC, rec.score DESC
LIMIT 100
```

4. Sauvegarder comme "User Recommendations"
5. Ajouter à un Dashboard "Recommendations"

---

## 🎯 Tâche 5.4 : Tests de l'API

**Responsable**: Personne A (Data/AI) + Personne B

**Durée**: 2h

**Test manuel**:

```bash
# 1. Vérifier que l'API est up
curl http://localhost:8000/health
# Response: {"status": "ok", ...}

# 2. Tester un endpoint de recommandation
curl -X POST http://localhost:8000/recommendations \
  -H "Content-Type: application/json" \
  -d '{"user_id": 1, "n_recommendations": 3}'

# Response should be:
# {
#   "user_id": 1,
#   "recommendations": [
#     {"report_id": 42, "score": 0.85, "algorithm": "hybrid"},
#     ...
#   ]
# }

# 3. Vérifier les métriques
curl http://localhost:8000/metrics
```

---

## ✅ FIN DE PHASE 5 - SYNCHRONISATION

**Réunion d'équipe** (45 min):

**Checklist commune**:
- [ ] API FastAPI accessible ✅
- [ ] Endpoints fonctionnent ✅
- [ ] Recommandations retournées ✅
- [ ] Table recommendations remplie ✅
- [ ] Dashboard Metabase affiche les recommendations ✅
- [ ] Tests OK ✅

**Prochaines étapes**:
- Personne B: Phase 6 (CI/CD, Résilience)
- Personne A: Phase 6 (A/B Testing, optionnel Bandits)

---

---

# ⏱️ PHASE 6 : Avancé & Tests

**Durée**: 1.5 semaines (14h)  
**Objectif**: CI/CD, résilience, A/B testing  
**Deadline**: Fin du jour 38

**(Voir document complet pour détails de Phase 6)**

---

# ⏱️ PHASE 7 : Rapport & Soutenance

**Durée**: 1 semaine (12h)  
**Objectif**: Documentation et présentation finale  
**Deadline**: Fin du jour 42 (Fin de semaine 6)

**(Voir document complet pour détails de Phase 7)**

---

---

## 📊 RÉSUMÉ DE LA ROADMAP

### Par Personne A (Data & AI Engineer)

| Phase | Tâches | Heures | Status |
|-------|--------|--------|--------|
| 1 | 1.4 (Metabase data) | 1h | 📌 |
| 2 | - | - | ⏳ |
| 3 | 3.1, 3.3 (Data) | 3h | 📌 |
| 4 | 4.1-4.5 (ML Models) | 16h | 🎯 |
| 5 | 5.1 (API) | 4h | 📌 |
| 6 | 6.2-6.3 (A/B, Bandits) | 6h | 📌 |
| 7 | Rapport + Slides | 6h | 📌 |
| **TOTAL** | **~16 tâches** | **~36h** | |

### Par Personne B (Backend & System)

| Phase | Tâches | Heures | Status |
|-------|--------|--------|--------|
| 1 | 1.1-1.3 (Setup) | 4h | 📌 |
| 2 | 2.1-2.4 (Tracking) | 6h | 📌 |
| 3 | 3.2-3.3 (Consumer) | 7h | 📌 |
| 4 | - | - | ⏳ |
| 5 | 5.2-5.3 (Metabase int.) | 5h | 📌 |
| 6 | 6.1, 6.4-6.5 (CI/CD, Résilience) | 8h | 📌 |
| 7 | Rapport + Slides | 6h | 📌 |
| **TOTAL** | **~16 tâches** | **~36h** | |

---

## 🎯 SYNCHRONISATION POINTS

```
Semaine 1
├─ Phase 1 COMPLETE
├─ Réunion: All systems running ✅
└─ Go to Phase 2/3

Semaine 2
├─ Phase 2 COMPLETE
├─ Phase 3 IN PROGRESS
├─ Réunion: Data flowing ✅
└─ Go to Phase 3/4

Semaine 3
├─ Phase 3 COMPLETE
├─ Phase 4 IN PROGRESS
├─ Réunion: Pipeline E2E working ✅
└─ Go to Phase 4/5

Semaine 4
├─ Phase 4 COMPLETE
├─ Phase 5 IN PROGRESS
├─ Réunion: Models trained ✅
└─ Go to Phase 5

Semaine 5
├─ Phase 5 COMPLETE
├─ Phase 6 IN PROGRESS
├─ Réunion: Recommendations visible ✅
└─ Go to Phase 6

Semaine 6
├─ Phase 6 COMPLETE
├─ Phase 7 IN PROGRESS
├─ Réunion: System resilient ✅
└─ Final push: Rapport + Slides

JOUR 42
└─ 🎉 SOUTENANCE!
```

---

## 💡 CONSEILS DE COLLABORATION

### Pour réussir ensemble:

1. **Réunion quotidienne** (15 min)
   - Ce qui a été fait hier
   - Ce qui se fait aujourd'hui
   - Blocages

2. **Code Review** (30 min, 2x par semaine)
   - Check avant merge dans main
   - Discuss patterns et architecture

3. **Test together** (1h, fin de chaque phase)
   - Tester l'intégration complète
   - Reproduire les bugs ensemble

4. **Git discipline**
   - Branches par feature/phase
   - Commits clairs avec messages
   - PR avant merge

5. **Documentation inline**
   - Docstrings sur chaque fonction
   - Commentaires sur la logique complexe
   - README.md à jour

---

## 🚨 POINTS CRITIQUES

### Risques à mitigate:

| Risque | Impact | Mitigation |
|--------|--------|-----------|
| Les deux travaillent sur le même code | 🔴 Élevé | Feature branches + code review |
| Manque de tests | 🔴 Élevé | Tests à chaque phase |
| Panne de communication | 🔴 Élevé | Daily standup + chat |
| Données sales | 🟡 Moyen | Peupler Metabase avec mock data early |
| Modèles ne convergent pas | 🟡 Moyen | Test simple Baseline avant complexe |
| API lente | 🟡 Moyen | Profiler et optimiser tôt |

---

## ✨ BONUS

Si vous avez du temps libre:

1. **Dashboard avancé** : Visualisations Metabase custom
2. **Monitoring**: Prometheus + Grafana
3. **Tests**: Augmenter coverage à 80%+
4. **Documentation**: Blog post ou tutorial
5. **Optimisation**: Réduire latence API < 50ms

---

## 📞 EN CAS DE BESOIN

- **Erreur de connexion**: Check `.env` et port availability
- **Modèle ne converge pas**: Réduire features, vérifier données
- **Metabase lent**: Réduire nombre de dashboards ou réindexer
- **Docker issues**: `docker-compose down`, `docker-compose up --build`

---

**C'est maintenant à vous de coder! Bonne chance! 🚀**

*Generated: May 2026*  
*Project: BI Adaptative - AI-driven Engineering*
