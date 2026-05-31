# Phase 6 Test Suite

Run from inside the backend container:

```bash
python tests/run_phase6_tests.py
```

The suite checks:

- Unit tests for data preparation and ML recommenders
- Integration checks for PostgreSQL, API health, batch generation, and stored recommendations
- Synthetic E2E check through RabbitMQ, consumer, PostgreSQL, API, and recommendations
- Lightweight stress check against the stored recommendation read path

The E2E test publishes one synthetic navigation event to RabbitMQ. It uses a
unique `source_event_id`, so repeated runs should not duplicate the same event.
