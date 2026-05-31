#!/usr/bin/env python3
"""
Integration checks for Phase 6.

Validates the already-running local stack:
- PostgreSQL contains pipeline data.
- API health is reachable.
- Batch generation stores recommendations.
- Stored recommendations can be read back through the API.
"""

import os
import sys

import psycopg2
import requests


API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")
DB_CONFIG = {
    "host": os.getenv("DB_HOST", "postgres"),
    "port": int(os.getenv("DB_PORT", 5432)),
    "user": os.getenv("DB_USER", "admin"),
    "password": os.getenv("DB_PASSWORD", "admin123"),
    "dbname": os.getenv("DB_NAME", "bi_recommendation"),
}


def fail(message):
    print(f"[FAIL] {message}")
    sys.exit(1)


def assert_true(condition, message):
    if not condition:
        fail(message)


def get_json(path, method="GET"):
    url = f"{API_BASE_URL}{path}"
    response = requests.request(method, url, timeout=120)
    if response.status_code >= 400:
        fail(f"{method} {path} returned {response.status_code}: {response.text}")
    return response.json()


def db_counts():
    with psycopg2.connect(**DB_CONFIG) as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT
                    (SELECT COUNT(*) FROM users),
                    (SELECT COUNT(*) FROM reports),
                    (SELECT COUNT(*) FROM navigation_logs),
                    (SELECT COUNT(*) FROM navigation_logs WHERE duration > 0)
                """
            )
            users, reports, logs, logs_with_duration = cur.fetchone()
    return {
        "users": users,
        "reports": reports,
        "navigation_logs": logs,
        "logs_with_duration": logs_with_duration,
    }


def main():
    counts = db_counts()
    assert_true(counts["users"] >= 100, "Expected at least 100 users")
    assert_true(counts["reports"] >= 40, "Expected at least 40 reports")
    assert_true(counts["navigation_logs"] >= 9000, "Expected pipeline navigation logs")
    assert_true(
        counts["logs_with_duration"] > 0,
        "Expected duration-enriched navigation logs",
    )

    health = get_json("/health")
    assert_true(health["status"] == "healthy", "API health should be healthy")

    batch = get_json("/batch/recommendations/generate?n=5", method="POST")
    assert_true(batch["users"] >= 100, "Batch should cover known users")
    assert_true(
        batch["recommendations_inserted"] >= batch["users"] * 5,
        "Batch should store at least top-5 recommendations per user",
    )

    stored = get_json("/stored-recommendations/1?n=5")
    assert_true(stored["count"] == 5, "Stored endpoint should return top-5")
    assert_true(stored["batch_id"] == batch["batch_id"], "Stored recs should use latest batch")

    print("[PASS] Integration checks passed")
    print(
        {
            "counts": counts,
            "batch_id": batch["batch_id"],
            "stored_count": stored["count"],
        }
    )


if __name__ == "__main__":
    main()
