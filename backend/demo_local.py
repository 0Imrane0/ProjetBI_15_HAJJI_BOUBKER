#!/usr/bin/env python3
"""
Local demo runner.

Run inside the backend container:
    python demo_local.py --events 50 --top-n 5

The script injects synthetic Metabase-like navigation events into RabbitMQ,
waits for the consumer, triggers batch recommendations, and prints a compact
demo summary.
"""

import argparse
import json
import os
import random
import sys
import time
from datetime import datetime, timezone

import pika
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
RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "rabbitmq")
RABBITMQ_PORT = int(os.getenv("RABBITMQ_PORT", "5672"))
RABBITMQ_USER = os.getenv("RABBITMQ_USER", "guest")
RABBITMQ_PASS = os.getenv("RABBITMQ_PASS", "guest")


def load_entities():
    with psycopg2.connect(**DB_CONFIG) as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT id, metabase_user_id FROM users ORDER BY id")
            users = cur.fetchall()
            cur.execute("SELECT id, metabase_report_id FROM reports ORDER BY id")
            reports = cur.fetchall()
            cur.execute("SELECT COALESCE(MAX(source_event_id), 0) + 1 FROM navigation_logs")
            next_source_event_id = int(cur.fetchone()[0])

    if not users or not reports:
        raise RuntimeError("Demo requires existing users and reports")

    return users, reports, next_source_event_id


def publish_events(events):
    credentials = pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PASS)
    params = pika.ConnectionParameters(
        host=RABBITMQ_HOST,
        port=RABBITMQ_PORT,
        credentials=credentials,
    )
    connection = pika.BlockingConnection(params)
    channel = connection.channel()
    channel.queue_declare(queue="navigation_logs", durable=True)

    for event in events:
        channel.basic_publish(
            exchange="",
            routing_key="navigation_logs",
            body=json.dumps(event),
            properties=pika.BasicProperties(delivery_mode=2),
        )

    connection.close()


def build_events(users, reports, first_source_event_id, count):
    events = []
    for offset in range(count):
        _, metabase_user_id = random.choice(users)
        _, metabase_report_id = random.choice(reports)
        action = random.choices(["view", "selection"], weights=[0.82, 0.18], k=1)[0]
        duration = random.randint(20, 480) if action == "view" else random.randint(90, 840)

        events.append(
            {
                "source_event_id": first_source_event_id + offset,
                "metabase_user_id": metabase_user_id,
                "metabase_report_id": metabase_report_id,
                "action": action,
                "event_type": f"demo_{action}",
                "duration": duration,
                "duration_source": "synthetic_demo",
                "metabase_model": "card",
                "metabase_model_id": metabase_report_id,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
        )
    return events


def wait_until_persisted(first_source_event_id, count, timeout_seconds=60):
    expected_ids = (first_source_event_id, first_source_event_id + count - 1)
    deadline = time.time() + timeout_seconds
    while time.time() < deadline:
        with psycopg2.connect(**DB_CONFIG) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT COUNT(*)
                    FROM navigation_logs
                    WHERE source_event_id BETWEEN %s AND %s
                    """,
                    expected_ids,
                )
                persisted = cur.fetchone()[0]
        if persisted >= count:
            return persisted
        time.sleep(1)
    return persisted


def api_request(method, path, timeout=120):
    response = requests.request(method, f"{API_BASE_URL}{path}", timeout=timeout)
    response.raise_for_status()
    return response.json()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--events", type=int, default=50)
    parser.add_argument("--top-n", type=int, default=5)
    args = parser.parse_args()

    random.seed(42)
    users, reports, first_source_event_id = load_entities()
    events = build_events(users, reports, first_source_event_id, args.events)

    publish_events(events)
    persisted = wait_until_persisted(first_source_event_id, args.events)
    if persisted < args.events:
        print(
            f"[FAIL] Only {persisted}/{args.events} demo events were persisted",
            file=sys.stderr,
        )
        return 1

    batch = api_request("POST", f"/batch/recommendations/generate?n={args.top_n}")
    sample_user_id = users[0][0]
    stored = api_request("GET", f"/stored-recommendations/{sample_user_id}?n={args.top_n}")
    monitoring = api_request("GET", "/monitoring/summary")

    print("[PASS] Local demo pipeline completed")
    print(
        json.dumps(
            {
                "events_published": args.events,
                "events_persisted": persisted,
                "batch_id": batch["batch_id"],
                "recommendations_inserted": batch["recommendations_inserted"],
                "sample_user_id": sample_user_id,
                "sample_recommendations": [
                    {
                        "rank": item["rank"],
                        "title": item["title"],
                        "score": round(item["score"], 4),
                    }
                    for item in stored["recommendations"]
                ],
                "monitoring_totals": monitoring["totals"],
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
