# Project Progress Status

## Objective

Build an adaptive BI recommendation system for Metabase.

The "brain" of the project is responsible for:

- Collecting user/report interactions
- Cleaning and enriching the data
- Training recommendation models
- Serving recommendations through an API
- Storing batch recommendations for demo and future product use
- Monitoring the pipeline

## Completed Phases

### Phase 1: Deep Understanding

Completed.

We clarified the real problem: Metabase shows BI reports, but it does not
personalize what each user should open next. The recommendation engine uses
behavioral logs and report metadata to suggest relevant dashboards/cards.

### Phase 2: Audit And Test Existing Code

Completed.

The existing Docker stack and data flow were tested:

- Metabase
- PostgreSQL
- RabbitMQ
- Publisher
- Consumer
- Backend API

### Phase 3: Problem Identification

Completed.

Key issues found:

- Metabase logs did not provide reliable consultation duration.
- The original schema missed event enrichment fields.
- Report metadata was too weak for content-based recommendations.
- The consumer could fail when PostgreSQL closed a stale connection.

### Phase 4: Brainstorming And Solutions

Completed.

Solutions implemented:

- Simulated duration with `duration_source`.
- Enriched navigation events with source id, event type, model fields, and raw payload.
- Added report business categories and descriptions.
- Chose temporal train/test split.
- Defined recommendation metrics: Precision@K, Recall@K, HitRate@K, NDCG@K, Coverage@K.

### Phase 5: ML And Data Brain

Completed.

Implemented:

- Data preparation and feature engineering
- User-based collaborative filtering baseline
- Surprise SVD and KNN models
- Content-based TF-IDF recommender
- Hybrid recommender
- Offline evaluation
- FastAPI serving
- Batch recommendation storage

Selected serving model:

- `hybrid_knn_content`
- Collaborative component: Surprise KNN
- Content component: TF-IDF
- Weighting: 0.6 collaborative / 0.4 content

Best top-5 result:

- Precision@5: 0.140
- NDCG@5: 0.132
- Catalog coverage@5: 0.875

### Phase 6: Tests And Integration

Completed.

Added:

- Unit tests for data preparation and ML models
- Integration checks for PostgreSQL, API, batch serving, and stored recommendations
- Synthetic E2E test through RabbitMQ, consumer, PostgreSQL, API, and recommendation batch
- Lightweight stress test

Important bug fixed:

- The consumer now reconnects to PostgreSQL if the DB connection was closed.
- Failed messages are safely requeued instead of killing the worker thread.

### Phase 7: Local Deployment And Demo

Completed.

Added:

- `backend/demo_local.py` demo runner
- `/monitoring/summary` API endpoint
- PostgreSQL monitoring views
- Local demo guide

Latest demo validation:

- Published 50 synthetic events
- Persisted 50 events
- Generated 500 recommendations
- Served top-5 recommendations for a sample user
- Monitoring showed pipeline totals and top reports

### Phase 8: Hardening And Cleanup

Completed for the current milestone.

Done:

- Removed obsolete Docker Compose `version` attribute.
- Removed unused API import.
- Added documentation for tests, demo, progress, and model optimization.
- Hardened batch insertion count reporting.
- Revalidated integration after cleanup.

## Current Project Position

The project is now demo-ready locally.

Working flow:

```text
Metabase-like activity
    -> RabbitMQ
    -> Consumer
    -> PostgreSQL navigation_logs
    -> ML feature engineering
    -> Hybrid recommender
    -> FastAPI
    -> Stored batch recommendations
    -> Monitoring summary / Metabase views
```

## Main Remaining Future Improvements

- Replace simulated duration with real client-side dwell-time tracking.
- Build real Metabase monitoring dashboards from the SQL views.
- Add recommendation click tracking from the UI.
- Add model persistence to disk or object storage.
- Add CI/CD test execution.
- Add authentication and stricter API security before production deployment.
