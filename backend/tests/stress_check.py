#!/usr/bin/env python3
"""
Lightweight stress check for stored recommendations.

This is intentionally small enough for a laptop demo. It verifies that the
read path stays stable under concurrent API calls.
"""

import os
import statistics
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

import psycopg2
import requests


API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")
REQUESTS = int(os.getenv("STRESS_REQUESTS", "100"))
WORKERS = int(os.getenv("STRESS_WORKERS", "8"))
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


def load_user_ids(limit=20):
    with psycopg2.connect(**DB_CONFIG) as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT id FROM users ORDER BY id LIMIT %s", (limit,))
            return [row[0] for row in cur.fetchall()]


def timed_request(user_id):
    start = time.perf_counter()
    response = requests.get(
        f"{API_BASE_URL}/stored-recommendations/{user_id}?n=5",
        timeout=20,
    )
    latency = time.perf_counter() - start
    return response.status_code, latency, response.json()


def percentile(values, pct):
    if not values:
        return 0.0
    ordered = sorted(values)
    index = min(len(ordered) - 1, int(round((pct / 100) * (len(ordered) - 1))))
    return ordered[index]


def main():
    user_ids = load_user_ids()
    if not user_ids:
        fail("No users available for stress check")

    results = []
    with ThreadPoolExecutor(max_workers=WORKERS) as executor:
        futures = [
            executor.submit(timed_request, user_ids[index % len(user_ids)])
            for index in range(REQUESTS)
        ]
        for future in as_completed(futures):
            results.append(future.result())

    statuses = [status for status, _, _ in results]
    latencies = [latency for _, latency, _ in results]
    counts = [payload.get("count", 0) for _, _, payload in results]

    if any(status != 200 for status in statuses):
        fail(f"Non-200 responses detected: {statuses}")
    if any(count < 1 for count in counts):
        fail("Some stored recommendation responses were empty")

    avg_latency = statistics.mean(latencies)
    p95_latency = percentile(latencies, 95)

    if p95_latency > 5.0:
        fail(f"P95 latency too high for local demo: {p95_latency:.3f}s")

    print("[PASS] Stress check passed")
    print(
        {
            "requests": REQUESTS,
            "workers": WORKERS,
            "avg_latency_sec": round(avg_latency, 4),
            "p95_latency_sec": round(p95_latency, 4),
        }
    )


if __name__ == "__main__":
    main()
