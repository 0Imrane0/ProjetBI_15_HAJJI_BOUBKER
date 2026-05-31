# Local Deployment And Demo Guide

## Goal

This guide shows the complete local demo path:

1. Start the Docker stack.
2. Verify services.
3. Simulate Metabase-like traffic.
4. Generate batch recommendations.
5. Inspect monitoring metrics.

## Services

Expected local URLs:

- Metabase: http://localhost:3000
- Backend API: http://localhost:8000
- RabbitMQ Management: http://localhost:15672
- PostgreSQL: localhost:5432

## Start Stack

```bash
docker-compose up -d
```

Check services:

```bash
docker-compose ps
```

Expected services:

- `bi_postgres`
- `bi_rabbitmq`
- `bi_metabase`
- `bi_backend`
- `bi_publisher`
- `bi_consumer`

## Run The Demo Scenario

Inside the backend container:

```bash
docker exec bi_backend python demo_local.py --events 50 --top-n 5
```

What it does:

- Publishes synthetic navigation events to RabbitMQ.
- Waits until the consumer stores them in PostgreSQL.
- Triggers batch recommendation generation.
- Prints top-5 recommendations for a sample user.
- Prints pipeline monitoring totals.

## Useful API Calls

Health:

```bash
curl http://localhost:8000/health
```

Train model:

```bash
curl -X POST http://localhost:8000/train
```

Generate stored recommendations:

```bash
curl -X POST "http://localhost:8000/batch/recommendations/generate?n=5"
```

Read stored recommendations:

```bash
curl "http://localhost:8000/stored-recommendations/1?n=5"
```

Monitoring:

```bash
curl http://localhost:8000/monitoring/summary
```

## Monitoring Views

The PostgreSQL database includes these demo views:

- `v_pipeline_monitoring_summary`
- `v_top_viewed_reports`
- `v_latest_batch_recommendations`

Example:

```bash
docker exec bi_postgres psql -U admin -d bi_recommendation -c "SELECT * FROM v_pipeline_monitoring_summary;"
```

These views can also be used from Metabase to build simple monitoring cards:

- Total users, reports, navigation logs, recommendations
- Latest event timestamp
- Latest batch timestamp
- Top viewed reports
- Latest recommendations by user

## Validation

Run the Phase 6 test suite:

```bash
docker exec bi_backend python tests/run_phase6_tests.py
```

Expected result:

```text
[PASS] Phase 6 test suite passed
```
