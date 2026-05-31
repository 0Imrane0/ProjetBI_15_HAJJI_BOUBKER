# Phase 6 Test Report

## Scope

Phase 6 validates the recommendation system after the ML and API work:

- Unit tests for data preparation and ML models
- Integration checks for PostgreSQL, API, batch generation, and stored recommendations
- Synthetic E2E check through RabbitMQ, consumer, PostgreSQL, API, and recommendations
- Lightweight stress check on the stored recommendation read path

## Commands

Run from inside the backend container:

```bash
python tests/run_phase6_tests.py
```

Or from the project root:

```bash
docker exec bi_backend python tests/run_phase6_tests.py
```

## Results

Final run status: PASS

Unit tests:

- 6 tests passed
- Covered temporal split, interaction feature generation, collaborative filtering,
  content-based filtering, hybrid recommendations, and offline metric bounds.

Integration checks:

- PostgreSQL users: 100
- PostgreSQL reports: 40
- Navigation logs after final run: 9,913 before the last E2E event
- Logs with duration: 9,913
- Batch generation: PASS
- Stored recommendations endpoint: PASS

Synthetic E2E:

- Published one synthetic navigation event to RabbitMQ.
- Consumer persisted it into `navigation_logs`.
- Batch recommendations regenerated successfully.
- Stored recommendations returned top-5 for the test user.

Stress check:

- Requests: 100
- Workers: 8
- Average latency: 0.0601 seconds
- P95 latency: 0.0814 seconds

## Bug Found And Fixed

The first E2E run failed because the consumer kept a stale PostgreSQL connection.
When PostgreSQL closed that connection, the `navigation_logs` consumer thread
crashed and left one RabbitMQ message unacknowledged.

Fix implemented in `backend/rabbitmq/consumer.py`:

- Detect closed DB connections before processing a message.
- Reconnect automatically.
- Roll back safely only when the connection is still open.
- Requeue failed messages without killing the worker thread.
- Add `basic_qos(prefetch_count=1)` to limit unacknowledged messages per worker.

## Lesson

The ML model can pass offline metrics while the real pipeline still fails.
Phase 6 proved the full system path, and it found a reliability issue that only
appears when RabbitMQ, the consumer, PostgreSQL, and the API run together.
