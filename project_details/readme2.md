# BI Adaptive — README

Adaptive BI recommendation system that tracks Metabase user navigation and recommends relevant dashboards/reports using ML.

---

## Architecture

```
Metabase (PostgreSQL) → Publisher → RabbitMQ → Consumer → Your Tables → ML Engine → FastAPI
```

### Services

| Container | Role | Port |
|---|---|---|
| `bi_postgres` | PostgreSQL — stores Metabase internals + your tables | 5432 |
| `bi_rabbitmq` | Message queue between publisher and consumer | 5672 / 15672 |
| `bi_metabase` | BI front-end, source of navigation data | 3000 |
| `bi_publisher` | Polls Metabase tables → pushes to RabbitMQ | — |
| `bi_consumer` | Reads RabbitMQ → writes to your tables | — |
| `bi_backend` | FastAPI recommendation API | 8000 |

---

## Your Tables

| Table | Description |
|---|---|
| `users` | Synced from Metabase `core_user` |
| `reports` | Synced from Metabase `report_card` (40 reports) |
| `navigation_logs` | Every user-report interaction (view, click, selection) |
| `recommendations` | ML-generated recommendations (populated by ML engine) |
| `publisher_state` | Cursor tracking last processed id per stream |

---

## Streaming Pipeline

### Publisher — 3 parallel streams

| Source (Metabase table) | RabbitMQ Queue | Trigger |
|---|---|---|
| `recent_views` | `navigation_logs` | New view/click event |
| `core_user` | `users_sync` | New user created |
| `report_card` | `reports_sync` | New report/card created |

### Consumer — 3 parallel queues

| Queue | Action |
|---|---|
| `navigation_logs` | Upsert user + report if unknown, insert into `navigation_logs` |
| `users_sync` | Upsert into `users` |
| `reports_sync` | Upsert into `reports` |

---

## Prerequisites

- Docker Desktop installed and running
- Git
- Python 3.9+ with pip (for data generation only)
- Ports free: 5432, 5672, 15672, 3000, 8000

---

## First-Time Setup

### 1. Clone and configure
```bash
git clone <repo_url>
cd projet_BI
```

### 2. Start all services
```bash
docker compose up -d
```

### 3. Create your tables (first time only)
```bash
docker exec -i bi_postgres psql -U admin -d bi_recommendation < db/init.sql
```

### 4. Verify tables were created
```bash
docker exec -it bi_postgres psql -U admin -d bi_recommendation -c "SELECT table_name FROM information_schema.tables WHERE table_schema = 'public' AND table_name IN ('users','reports','navigation_logs','recommendations','publisher_state');"
```
Expected output: 5 rows.

---

## Generate Fake Training Data

Since `recent_views` only captures real user activity, we provide a script that generates **100 fake users across 6 behavioral clusters** with realistic navigation patterns over the last 30 days.

### Clusters

| Cluster | Profile | Focus |
|---|---|---|
| Sales Manager | Revenue and orders | Revenue, Checkout funnel, Orders |
| Product Analyst | Products and categories | Product breakdown, Ratings, Category orders |
| Marketing Analyst | Customer behavior | Customer satisfaction, User flow, Orders by source |
| Finance Executive | KPIs and subscriptions | Revenue per quarter, Subscriptions, Discounts |
| Operations Manager | Quantities and trends | Quantity sold, Product trends, Total orders |
| Data Analyst | Raw data and deep dives | Tables, People, Survey responses |

Each user generates **50–150 views**, 70% within their preferred reports, 30% random noise. Timestamps are spread across working hours (8am–7pm, Mon–Fri).

### Run the generator

```bash
# Install dependency (once)
pip install psycopg2-binary

# Run the script
python generate_data.py
```

The script inserts directly into Metabase's `core_user` and `recent_views` tables in PostgreSQL.

### Sync generated data into your tables

```bash
# 1. Reset publisher cursors to reprocess everything
docker exec -it bi_postgres psql -U admin -d bi_recommendation -c "UPDATE publisher_state SET last_id = 0;"

# 2. Purge RabbitMQ queues
#    http://localhost:15672 → Queues → purge navigation_logs, users_sync, reports_sync

# 3. Restart the pipeline
docker compose restart publisher consumer
```

### Verify
```bash
docker exec -it bi_postgres psql -U admin -d bi_recommendation -c "SELECT COUNT(*) FROM users;"
docker exec -it bi_postgres psql -U admin -d bi_recommendation -c "SELECT COUNT(*) FROM navigation_logs;"
```
Expected: ~100 users, ~5000–7500 navigation logs.

---

## Daily Usage (After First Setup)

```bash
# Start everything
docker compose up -d

# Stop everything
docker compose down

# View live logs
docker logs bi_publisher -f
docker logs bi_consumer -f
```

---

## Verify Data is Flowing

```bash
# Check navigation logs
docker exec -it bi_postgres psql -U admin -d bi_recommendation -c "SELECT COUNT(*) FROM navigation_logs;"

# Check users
docker exec -it bi_postgres psql -U admin -d bi_recommendation -c "SELECT COUNT(*) FROM users;"

# Check reports
docker exec -it bi_postgres psql -U admin -d bi_recommendation -c "SELECT COUNT(*) FROM reports;"

# Check top viewed reports
docker exec -it bi_postgres psql -U admin -d bi_recommendation -c "SELECT * FROM v_top_reports LIMIT 10;"
```

---

## Troubleshooting

### Tables don't exist
```bash
docker exec -i bi_postgres psql -U admin -d bi_recommendation < db/init.sql
```

### Publisher not sending new events (cursor stuck)
```bash
docker exec -it bi_postgres psql -U admin -d bi_recommendation -c "UPDATE publisher_state SET last_id = 0;"
docker compose restart publisher
```

### Full reset (wipe all your data and reprocess)
```bash
# 1. Truncate your tables
docker exec -it bi_postgres psql -U admin -d bi_recommendation -c "TRUNCATE navigation_logs, users, reports RESTART IDENTITY CASCADE;"

# 2. Reset cursors
docker exec -it bi_postgres psql -U admin -d bi_recommendation -c "UPDATE publisher_state SET last_id = 0;"

# 3. Purge RabbitMQ queues
#    http://localhost:15672 → Queues → purge each queue

# 4. Restart pipeline
docker compose restart publisher consumer
```

### Rebuild after code changes
```bash
docker compose down publisher consumer
docker compose up --build publisher consumer -d
```

---

## Project Structure

```
projet_BI/
├── docker-compose.yml
├── .gitignore
├── generate_data.py          # Fake training data generator (100 users, 6 clusters)
├── db/
│   └── init.sql              # Your table schemas
└── backend/
    ├── rabbitmq/
    │   ├── Dockerfile
    │   ├── requirements.txt
    │   ├── publisher.py      # Metabase → RabbitMQ (3 streams)
    │   └── consumer.py       # RabbitMQ → PostgreSQL (3 queues)
    ├── api/                  # FastAPI (Week 5)
    └── ml_engine/            # ML models (Week 3-4)
```

---

## Useful URLs

| Service | URL | Credentials |
|---|---|---|
| Metabase | http://localhost:3000 | admin@bi.local / metabase123 |
| RabbitMQ UI | http://localhost:15672 | guest / guest |
| FastAPI docs | http://localhost:8000/docs | — |

---

## Current Status

- [x] Week 1 — Infrastructure & Docker setup
- [x] Week 2 — Streaming pipeline (publisher + consumer)
- [x] Week 2 — Fake training data generator (100 users, 6 clusters)
- [ ] Week 3 — Data pipeline & ML training data
- [ ] Week 4 — ML models (collaborative filtering, hybrid)
- [ ] Week 5 — FastAPI recommendation endpoint
- [ ] Week 6 — CI/CD, A/B testing, report